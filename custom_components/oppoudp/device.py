import asyncio
import logging
from typing import Optional

from homeassistant.core import HomeAssistant
from oppoudpsdk import OppoClient, OppoDevice
from oppoudpsdk import EVENT_DEVICE_STATE_UPDATED

from .const import PLATFORMS

_LOGGER = logging.getLogger(__name__)

class OppoHaDevice:
    def __init__(self, hass: HomeAssistant, host_name: str, port_number: int, mac_address: Optional[str]) -> None:
        self._hass = hass
        self._client = OppoClient(host_name, port_number, mac_address)
        self._device = self._client._device

        self._client.add_event_handler(EVENT_DEVICE_STATE_UPDATED, self.on_device_state_updated)

    async def on_device_state_updated(self, device: OppoDevice):        
        pass

    def shutdown(self, event) -> None:
        """Close the connection on shutdown.
        Used as an argument to EventBus.async_listen_once.
        """
        _LOGGER.info("oppo_udp shutting down")
        if self._client:
            self._client.clear_event_handlers()
            self._client.disconnect()
