"""The Oppo UDP-20x Integration"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .manager import OppoUdpManager

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True
    
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the component."""

    manager = OppoUdpManager(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager

    async def on_hass_stop(event):
        """Stop updates when hass stops"""
        await manager.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)
    )

    async def setup_platforms():
        """Set up platforms and initiate connection."""
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_setup(entry, platform)
                for platform in PLATFORMS
            ]
        )
        await manager.async_start_client()

    hass.async_create_task(setup_platforms())

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    manager: OppoUdpManager = hass.data[DOMAIN][entry.entry_id] 
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        await manager.disconnect()
    
    return unload_ok

async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
