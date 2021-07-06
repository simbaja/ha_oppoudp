import asyncio
import logging
from typing import Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from oppoudpsdk.device import OppoDevice

from .const import DOMAIN
from .manager import OppoUdpManager

_LOGGER = logging.getLogger(__name__)

class OppoUdpEntity(Entity):
    """
    Base class for Oppo entities
    """
    def __init__(self, name: str, identifier: str, manager: OppoUdpManager):
        self._name = name
        self._identifier = identifier
        self._hass = manager.hass
        self._manager = manager

    @property
    def hass(self) -> HomeAssistant:
        return self._hass

    @property
    def device(self) -> OppoDevice:
        return self._manager.device

    @property
    def available(self) -> bool:
        return self._manager.online

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._identifier

    @property
    def should_poll(self):
        """No polling needed for Oppo"""
        return False

    @property
    def device_info(self) -> Dict:
        """Device info dictionary."""
        attrs = {
            "identifiers": {(DOMAIN, self._identifier)},
            "name": self.name,
            "manufacturer": "Oppo",
            "model": "UDP-20x",
            "sw_version": self._manager.device.firmware_version
        }
        if self._manager.device:
            attrs["sw_version"] = self._manager.device.firmware_version

        return attrs