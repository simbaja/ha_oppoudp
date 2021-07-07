"""Constants for the Oppo UDP-20x integration."""

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN

DOMAIN = "oppo_udp"
DEFAULT_PORT = 23

ASYNC_TIMEOUT = 30
MIN_RETRY_DELAY = 15
MAX_RETRY_DELAY = 1800
RETRY_OFFLINE_COUNT = 5

PLATFORMS = [MEDIA_PLAYER_DOMAIN, REMOTE_DOMAIN]

SIGNAL_CONNECTED = "oppo_udp_connected"
SIGNAL_DISCONNECTED = "oppo_udp_disconnected"
SIGNAL_CLIENT_CREATED = "oppo_udp_client_created"