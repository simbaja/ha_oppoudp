"""Constants for the Oppo UDP-20x integration."""

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN

DOMAIN = "oppo_udp"
DEFAULT_PORT = 23

PLATFORMS = [MEDIA_PLAYER_DOMAIN, REMOTE_DOMAIN]