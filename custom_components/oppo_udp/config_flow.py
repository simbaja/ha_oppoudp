""" ConfigFlow for the Oppo UDP-20x Integration """
import logging
import ipaddress
import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from oppoudpsdk import OppoClient

from .const import DEFAULT_PORT, DOMAIN
from .exceptions import HaAlreadyConfigured, HaCannotConnect, HaInvalidHost

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    })

def host_valid(host: str) -> bool:
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version in (4, 6):
            return True
    except ValueError:
        pass
    if len(host) > 253:
        return False
    allowed = re.compile(r"(?!-)[A-Z\d\-\_]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in host.split("."))    

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oppo UDP-20x."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                if not host_valid(user_input[CONF_HOST]):
                    raise HaInvalidHost
                
                host: str = user_input[CONF_HOST]
                port: int = user_input[CONF_PORT]

                if self.host_already_configured(host):
                    raise HaAlreadyConfigured
                
                await self.test_connection(host, port)

                return self.async_create_entry(title=host, data=user_input)
            except HaCannotConnect:
                errors[CONF_HOST] = "cannot_connect"
            except HaAlreadyConfigured:
                errors[CONF_HOST] = "already_configured"
            except HaInvalidHost:
                errors[CONF_HOST] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    def host_already_configured(self, host: str) -> bool:
        """See if we already have a dunehd entry matching user input configured."""
        existing_hosts = {
            entry.data[CONF_HOST] for entry in self._async_current_entries()
        }
        return host in existing_hosts        

    async def test_connection(self, host: str, port: int):
        """Validate the user input allows us to connect."""

        #connect to the client
        try:            
            client = OppoClient(host, port)
            result = await client.test_connection()
            if not result:
                raise HaCannotConnect
        except:
            raise HaCannotConnect