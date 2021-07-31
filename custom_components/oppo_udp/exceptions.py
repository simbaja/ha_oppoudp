""" Home Assistant derived exceptions"""

from homeassistant import exceptions as ha_exc

class HaCannotConnect(ha_exc.HomeAssistantError):
    """Error to indicate we cannot connect."""

class HaInvalidHost(ha_exc.HomeAssistantError):
    """Error to indicate we don't have a valid host."""    

class HaAlreadyConfigured(ha_exc.HomeAssistantError):
    """Error to indicate that the host is already configured"""