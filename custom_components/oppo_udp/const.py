"""Constants for the Oppo UDP-20x integration."""

from homeassistant.const import Platform

DOMAIN = "oppo_udp"
DEFAULT_PORT = 23

ASYNC_TIMEOUT = 30
MIN_RETRY_DELAY = 15
MAX_RETRY_DELAY = 1800
RETRY_OFFLINE_COUNT = 5

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.REMOTE]

SIGNAL_CONNECTED = "oppo_udp_connected"
SIGNAL_DISCONNECTED = "oppo_udp_disconnected"
SIGNAL_CLIENT_CREATED = "oppo_udp_client_created"