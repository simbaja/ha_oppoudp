"""The Oppo UDP-20x Integration"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .device import OppoHaDevice

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True
    
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the component."""
    hass.data.setdefault(DOMAIN, {})

    device = OppoHaDevice(hass, entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_MAC])
    hass.data[DOMAIN][entry.entry_id] = device
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, device.shutdown)

    # Initialize the platforms
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    device: OppoHaDevice = hass.data[DOMAIN][entry.entry_id] 
    unload_ok = all(
        await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, component)
                    for component in PLATFORMS
                ]
            )
        )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
