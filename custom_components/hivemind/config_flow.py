"""Config flow for HiveMind integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .notify import HiveMindNotificationService

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("key"): str,
        vol.Required("pswd"): str,
        vol.Required("hm_host"): str,
        vol.Optional("hm_port", default=5678): int,
        vol.Optional("self_signed", default=False): bool,
        vol.Optional("hm_name", default="HiveMind Listener"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        hm = HiveMindNotificationService(
            data["key"],
            data["pswd"],
            data["hm_host"],
            data["hm_port"],
            data["self_signed"]
        )
        if not hm.connect():
            raise InvalidAuth
        hm.bus.close()
    except Exception as exc:  # pylint: disable=broad-except
        raise CannotConnect() from exc

    # Return info that you want to store in the config entry.
    return data


class HiveMindConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HiveMind"""

    VERSION = 1

    async def async_step_user(self, info):
        errors: dict[str, str] = {}
        if info is not None:
            try:
                info = await validate_input(self.hass, info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["hm_name"],
                                               data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
