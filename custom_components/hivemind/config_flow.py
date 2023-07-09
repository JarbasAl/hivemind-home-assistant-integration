"""Config flow for HiveMind integration."""
from __future__ import annotations

import logging
from typing import Any

from hivemind_bus_client.client import HiveMessageBusClient
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, HM_SCHEMA

_LOGGER = logging.getLogger(__name__)



class HiveMindConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HiveMind"""

    VERSION = 1

    async def async_step_user(self, info):
        errors: dict[str, str] = {}
        if info is not None:
            return self.async_create_entry(title="HiveMind Node",
                                           data=info)

        return self.async_show_form(
            step_id="user", data_schema=HM_SCHEMA
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
