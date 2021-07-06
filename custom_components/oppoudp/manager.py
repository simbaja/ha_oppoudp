"""Connection manager Oppo UDP-20x integration."""

import asyncio
import async_timeout
import logging
from typing import Optional

from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send

from oppoudpsdk import OppoClient, OppoDevice
from oppoudpsdk import EVENT_DEVICE_STATE_UPDATED, EVENT_CONNECTED, EVENT_DISCONNECTED

from .const import *
from .exceptions import *

_LOGGER = logging.getLogger(__name__)

class OppoUdpManager:
    """Manages a connection with an Oppo device including retries when the connection is dropped"""
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self._hass = hass
        self._config_entry = config_entry
        self._host_name = config_entry[CONF_HOST]
        self._port_number = config_entry[CONF_PORT]
        self._mac_address = config_entry[CONF_MAC]

        self._reset_initialization()

    def _reset_initialization(self):
        self._client = None
        self._retry_count = 0

    @property
    def online(self) -> bool:
        """ 
        Indicates whether the services is online.  If it's retried several times, it's assumed
        that it's offline for some reason
        """
        return self.connected or self._retry_count <= RETRY_OFFLINE_COUNT

    @property
    def connected(self) -> bool:
        """
        Indicates whether the coordinator is connected
        """
        return self._client and self._client.connected

    @property
    def client(self) -> OppoClient:
        return self._client

    @property
    def device(self) -> OppoDevice:
        if self._client:
            return self._client.device
        return None

    @property
    def hass(self) -> HomeAssistant:
        return self._hass

    async def async_start_client(self):
        """Start a new OppoClient in the HASS event loop."""
        try:
            _LOGGER.debug('Creating and starting client')
            await self._get_client()
            await asyncio.ensure_future(self.client.async_run_client(), loop=self._hass.loop)
            _LOGGER.debug('Client running')
        except:
            _LOGGER.debug('Could not start the client')
            self.client = None
            raise

    @callback
    def reconnect(self, log=False) -> None:
        """Prepare to reconnect oppo_udp session."""
        if log:
            _LOGGER.info("Will try to reconnect to oppo_udp device")
        self.hass.loop.create_task(self.async_reconnect())

    async def async_reconnect(self) -> None:
        """Try to reconnect oppo_udp session."""
        self._retry_count += 1
        _LOGGER.info(f"attempting to reconnect to oppo_udp service (attempt {self._retry_count})")
        
        try:
            with async_timeout.timeout(ASYNC_TIMEOUT):
                await self.async_start_client()
        except Exception as err:
            _LOGGER.warn(f"could not reconnect: {err}, will retry in {self._get_retry_delay()} seconds")
            self.hass.loop.call_later(self._get_retry_delay(), self.reconnect)
            #_LOGGER.debug("forcing a state refresh while disconnected")
            #try:
            #    await self._refresh_ha_state()
            #except Exception as err:
            #    _LOGGER.debug(f"error refreshing state: {err}")

    async def disconnect(self) -> None:
        """Disconnect from the device"""
        _LOGGER.debug("Disconnecting from device")
        try:
            if self._client:
                self._client.clear_event_handlers()
                await self._client.disconnect()
                self._client = None
        except:
            _LOGGER.exception("An error occurred while disconnecting")

    async def on_device_state_updated(self, device: OppoDevice):        
        pass

    async def on_disconnect(self, _):
        """Handle disconnection."""
        _LOGGER.debug(f"Disconnected. Attempting to reconnect in {MIN_RETRY_DELAY} seconds")
        self.hass.loop.call_later(MIN_RETRY_DELAY, self.reconnect, True)
        self._dispatch_send(SIGNAL_DISCONNECTED)

    async def on_connect(self, _):
        """Set state upon connection."""
        self._retry_count = 0
        self._dispatch_send(SIGNAL_CONNECTED, self.device)

    def _create_oppo_client(self, event_loop: Optional[asyncio.AbstractEventLoop]) -> OppoClient:
        """
        Create a new OppoClient object with some helpful callbacks.

        :param event_loop: Event loop
        :return: OppoClient
        """
        client = OppoClient(self._host_name, self._port_number, self._mac_address, event_loop=event_loop)
        client.add_event_handler(EVENT_DEVICE_STATE_UPDATED, self.on_device_state_updated)
        client.add_event_handler(EVENT_DISCONNECTED, self.on_disconnect)
        client.add_event_handler(EVENT_CONNECTED, self.on_connect)

        #send a signal to all associated entities that we have a new client
        self._dispatch_send(SIGNAL_CLIENT_CREATED, client)
        return client    

    async def _get_client(self) -> OppoClient:
        """Get a new Oppo UDP client."""
        if self._client:
            try:
                self._client.clear_event_handlers()
                await self._client.disconnect()
            except Exception as err:
                _LOGGER.warn(f'exception while disconnecting client {err}')
            finally:
                self._reset_initialization()
        
        loop = self._hass.loop
        self._client = self._create_oppo_client(event_loop=loop)
        return self._client

    def _dispatch_send(self, signal, *args):
        """Dispatch a signal to all entities managed by this manager."""
        async_dispatcher_send(
            self.hass, f"{signal}_{self.config_entry.entry_id}", *args
        )

    def _get_retry_delay(self) -> int:
        delay = MIN_RETRY_DELAY * 2 ** (self._retry_count - 1)
        return min(delay, MAX_RETRY_DELAY)
