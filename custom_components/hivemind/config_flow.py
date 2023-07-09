"""Config flow for HiveMind integration."""
from __future__ import annotations

import logging
from typing import Any

from hivemind_bus_client.client import HiveMessageBusClient
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, HM_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def _validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from HM_SCHEMA with values provided by the user.
    """
    try:
        hm = HiveMessageBusClient(
            key=data["key"],
            password=data["pswd"],
            host=data["host"],
            port=data["port"],
            self_signed=data["self_signed"]
        )
        hm.connect()
        hm.close()
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
                info = await _validate_input(info)
                return self.async_create_entry(title="HiveMind Node",
                                               data=info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=HM_SCHEMA
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
