"""Support for Oppo UDP-20x media player."""
from datetime import timedelta
import logging

from homeassistant.components.media_player import DEVICE_CLASS_TV, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_VIDEO,
    REPEAT_MODE_ALL,
    REPEAT_MODE_OFF,
    REPEAT_MODE_ONE,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_REPEAT_SET,
    SUPPORT_SEEK,
    SUPPORT_SHUFFLE_SET,
    SUPPORT_STOP,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_SELECT_SOURCE,
)
from homeassistant.const import (
    CONF_HOST,
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_STANDBY,
)
from homeassistant.core import callback
import homeassistant.util.dt as dt_util

from oppoudpsdk import EVENT_DEVICE_STATE_UPDATED
from oppoudpsdk import OppoClient, OppoDevice, OppoPlaybackStatus, OppoRemoteCode
from oppoudpsdk import SetInputSource, SetRepeatMode, SetSearchMode
from oppoudpsdk import DiscType, PlayStatus, RepeatMode
from oppoudpsdk.response.enums import PowerStatus

from .entity import OppoUdpEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

SUPPORT_OPPO_UDP = (
    SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
    | SUPPORT_PAUSE
    | SUPPORT_PLAY
    | SUPPORT_SEEK
    | SUPPORT_STOP
    | SUPPORT_NEXT_TRACK
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_VOLUME_MUTE
    | SUPPORT_VOLUME_SET
    | SUPPORT_VOLUME_STEP
    | SUPPORT_REPEAT_SET
    | SUPPORT_SHUFFLE_SET
    | SUPPORT_SELECT_SOURCE
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Load Oppo UDP media player based on a config entry."""
    host = config_entry.data[CONF_HOST]
    manager = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([OppoUdpMediaPlayer(host, config_entry.entry_id, manager)])

class OppoUdpMediaPlayer(OppoUdpEntity, MediaPlayerEntity):
    """Representation of an Oppo UDP media player."""

    def __init__(self, host, identifier, manager, **kwargs):
        """Initialize the Oppo UDP media player."""
        super().__init__(host, identifier, manager, **kwargs)

    @callback
    def async_client_created(self, client: OppoClient):
        """Handle when a new client is created (due to reconnections)."""
        client.add_event_handler(EVENT_DEVICE_STATE_UPDATED, self._on_device_state_updated)

    async def _on_device_state_updated(self, device: OppoDevice):
        """Handle a device state update event"""        
        self.schedule_update_ha_state()

    @property
    def state(self):
        """Return the state of the device."""
        if not self.available:
            return None
        if self.device is None:
            return None
        if self.device.power_status == PowerStatus.DISCONNECTED:
            return None
        if self.device.power_status == PowerStatus.OFF:
            return STATE_OFF
        if self.playback_status:
            state = self.playback_status
            if state == PlayStatus.OFF:
                return STATE_OFF        
            if state in (PlayStatus.SETUP, PlayStatus.HOME_MENU, PlayStatus.MEDIA_CENTER):
                return STATE_IDLE
            if state == PlayStatus.PLAY:
                return STATE_PLAYING
            if state in (PlayStatus.PAUSE, PlayStatus.SLOW_FORWARD, PlayStatus.SLOW_REVERSE, PlayStatus.FAST_FORWARD, PlayStatus.FAST_REVERSE):
                return STATE_PAUSED
            return STATE_STANDBY
        return None

    @property
    def device_class(self):
        return DEVICE_CLASS_TV

    @property
    def playback_info(self) -> OppoPlaybackStatus:
        """The current playback info"""
        if not self.device:
            return None
        return self.device.playback_attributes
    
    @property
    def playback_status(self) -> PlayStatus:
        """The current playback status"""
        if not self.device:
            return None        
        return self.device.playback_status

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        if self.device:
            return float(self.device.volume) / 100.0
        return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        if self.device:
            return self.device.is_muted
        return None        

    @property
    def media_content_type(self):
        """Content type of current playing media."""

        if self.device:
                #Assuming that UDP is only being used to play discs
                #TODO: determine how to handle media center stuff
            return {
                DiscType.BLURAY: MEDIA_TYPE_VIDEO,
                DiscType.UHD_BLURAY: MEDIA_TYPE_VIDEO,
                DiscType.DVD_VIDEO: MEDIA_TYPE_VIDEO,
                DiscType.VCD2: MEDIA_TYPE_VIDEO,
                DiscType.SVCD: MEDIA_TYPE_VIDEO,
                DiscType.DVD_AUDIO: MEDIA_TYPE_MUSIC,
                DiscType.SACD: MEDIA_TYPE_MUSIC,
                DiscType.CDDA: MEDIA_TYPE_MUSIC,
            }.get(self.device.disc_type, None)
        return None

    @property
    def media_duration(self):            
        """Duration of current playing media in seconds."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_duration.total_seconds()
        if self.media_content_type == MEDIA_TYPE_VIDEO:
            return self.playback_info.total_duration.total_seconds()
        return None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_elapsed_time.total_seconds()
        if self.media_content_type == MEDIA_TYPE_VIDEO:
            return self.playback_info.total_elapsed_time.total_seconds()
        return None

    @property
    def media_position_updated_at(self):
        """Last valid time of media position."""
        if self.state in (STATE_PLAYING, STATE_PAUSED):
            return dt_util.utcnow()
        return None

    @property
    def media_title(self):
        """Title of current playing media."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_name
        if self.device:
            return {
                DiscType.BLURAY: "Blu-ray Disc",
                DiscType.UHD_BLURAY: "UHD Blu-ray Disc",
                DiscType.DVD_VIDEO: "DVD",
                DiscType.VCD2: "Video CD",
                DiscType.SVCD: "Super Video CD",
                DiscType.NONE: "No Disc"
            }.get(self.device.disc_type, None)
        return None

    @property
    def media_artist(self):
        """Artist of current playing media, music track only."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_performer
        return None

    @property
    def media_album_name(self):
        """Album name of current playing media, music track only."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_album        
        return None

    @property
    def media_album_artist(self):
        """Album artist of current playing media, music track only."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track_performer        
        return None

    @property
    def media_track(self):
        """Track number of current playing media, music track only."""
        if self.media_content_type == MEDIA_TYPE_MUSIC:
            return self.playback_info.track        
        return None

    @property
    def source(self):
        """Name of the current input source."""
        if self.device and self.device.input_source:
            return self.device.input_source.name.replace("_"," ").title()
        return None

    @property
    def source_list(self):
        """List of available input sources."""
        return [e.name.replace("_"," ").title() for e in SetInputSource]

    @property
    def sound_mode(self):
        """Name of the current sound mode."""
        if self.playback_info:
            return self.playback_info.audio_type
        return None

    @property
    def repeat(self):
        """Return current repeat mode."""
        if self.playback_info:
            return {
                RepeatMode.REPEAT_ALL: REPEAT_MODE_ALL,
                RepeatMode.REPEAT_TITLE: REPEAT_MODE_ONE,
                RepeatMode.REPEAT_CHAPTER: REPEAT_MODE_ONE,
                RepeatMode.REPEAT_ONE: REPEAT_MODE_ONE,
                RepeatMode.SHUFFLE: REPEAT_MODE_OFF,
                RepeatMode.RANDOM: REPEAT_MODE_OFF,
                RepeatMode.OFF: REPEAT_MODE_OFF
            }.get(self.playback_info.repeat_mode, REPEAT_MODE_OFF)
        return None

    @property
    def shuffle(self):
        """Boolean if shuffle is enabled."""
        if self.playback_info:
            return self.playback_info.repeat_mode in [RepeatMode.SHUFFLE, RepeatMode.RANDOM]
        return None

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_OPPO_UDP

    async def async_turn_on(self):
        """Turn the media player on."""
        await self.device.async_send_command(OppoRemoteCode.PON)

    async def async_turn_off(self):
        """Turn the media player off."""
        await self.device.async_send_command(OppoRemoteCode.POF)

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        await self.device.async_send_command(OppoRemoteCode.MUT)      

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        await self.device.async_set_volume(int(volume * 100.0))

    async def async_select_source(self, source):
        """Select input source."""
        await self.device.async_set_input_source(SetInputSource[source])

    async def async_media_play(self):
        """Play media."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.PLA)

    async def async_media_stop(self):
        """Stop the media player."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.STP)

    async def async_media_pause(self):
        """Pause the media player."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.PAU)

    async def async_media_next_track(self):
        """Send next track command."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.NXT)

    async def async_media_previous_track(self):
        """Send previous track command."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.PRE)

    async def async_media_seek(self, position):
        """Send seek command."""
        if self.device:
            seek_type = SetSearchMode.CHAPTER if self.media_content_type == MEDIA_TYPE_MUSIC else SetSearchMode.TITLE
            seek_position = timedelta(seconds=position)
            await self.device.async_set_position(seek_type, seek_position)

    async def async_volume_up(self):
        """Turn volume up for media player."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.VDN)

    async def async_volume_down(self):
        """Turn volume down for media player."""
        if self.device:
            await self.device.async_send_command(OppoRemoteCode.VDN)

    async def async_set_repeat(self, repeat):
        """Set repeat mode."""
        one_mode = SetRepeatMode.TRACK
        if self.device:
            if self.media_content_type == MEDIA_TYPE_VIDEO:
                one_mode = SetRepeatMode.CHAPTER
            
            if repeat == REPEAT_MODE_ONE:
                await self.device.async_set_repeat_mode(one_mode)
            elif repeat == REPEAT_MODE_ALL:
                await self.device.async_set_repeat_mode(SetRepeatMode.ALL)
            else:
                await self.device.async_set_repeat_mode(SetRepeatMode.OFF)

    async def async_set_shuffle(self, shuffle):
        """Enable/disable shuffle mode."""
        if self.device:
            if self.media_content_type == MEDIA_TYPE_MUSIC:
                if shuffle:
                    await self.device.async_set_repeat_mode(SetRepeatMode.RANDOM)
                else:
                    await self.device.async_set_repeat_mode(SetRepeatMode.OFF)
