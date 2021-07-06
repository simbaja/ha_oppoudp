"""Remote control support for Oppo UDP-20x players."""

import asyncio
import logging

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)
from homeassistant.const import CONF_NAME
from oppoudpsdk import PowerStatus
from oppoudpsdk.codes import OppoRemoteCode

from .entity import OppoUdpEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Load Oppo UDP remote based on a config entry."""
    name = config_entry.data[CONF_NAME]
    manager = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([OppoUdpRemote(name, config_entry.entry_id, manager)])

class OppoUdpRemote(OppoUdpEntity, RemoteEntity):
    """Device that sends commands to an Oppo UDP."""

    @property
    def is_on(self):
        """Return true if device is on."""
        return self.device.power_status == PowerStatus.ON

    @property
    def should_poll(self):
        """No polling needed for Oppo UDP."""
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.device.async_send_command(OppoRemoteCode.PON)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.device.async_send_command(OppoRemoteCode.POF)

    async def async_send_command(self, command, **kwargs):
        """Send a command to one device."""
        num_repeats = kwargs[ATTR_NUM_REPEATS]
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)

        if not self.is_on:
            _LOGGER.error("Unable to send commands, not connected to %s", self._name)
            return

        for _ in range(num_repeats):
            for single_command in command:
                await self.device.async_send_command(single_command)
                await asyncio.sleep(delay)
