"""Constants for HiveMind integration."""
import voluptuous as vol

DOMAIN = "hivemind"

HM_SCHEMA = vol.Schema(
    {
        vol.Required("key"): str,
        vol.Required("pswd"): str,
        vol.Required("host"): str,
        vol.Optional("port", default=5678): int,
        vol.Optional("self_signed", default=False): bool
    }
)
