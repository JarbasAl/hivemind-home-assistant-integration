"""HiveMind notification platform."""
from __future__ import annotations

import logging
from typing import Any

from hivemind_bus_client.client import HiveMessageBusClient
from hivemind_bus_client.message import HiveMessageType, HiveMessage
from homeassistant.components.notify import BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from hivemind_bus_client import Message
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_service(
        hass: HomeAssistant,
        config: ConfigType,
        discovery_info: DiscoveryInfoType | None = None,
) -> HiveMindNotificationService:
    """Get the HiveMind notification service."""
    return HiveMindNotificationService(**hass.data[DOMAIN])


class HiveMindNotificationService(BaseNotificationService):
    """The HiveMind Notification Service."""

    def __init__(self, key: str, pswd: str, hm_host: str, hm_port: int = 5678, self_signed: bool = False, **kwargs) -> None:
        """Initialize the service."""
        self.key = key
        self.pswd = pswd
        self.hm_port = hm_port
        self.hm_host = hm_host
        self.self_signed = self_signed
        self.bus = None

    def connect(self):
        try:
            self.bus = HiveMessageBusClient(key=self.key,
                                            password=self.pswd,
                                            port=self.hm_port,
                                            host=self.hm_host,
                                            useragent="HomeAssistantV0.0.1",
                                            self_signed=self.self_signed)
            self.bus.connect()
            return True
        except:
            _LOGGER.error("Failed to connect to HiveMind")
            return False

    def _reconnect(self):
        if self.bus:
            try:
                self.bus.close()
            except:
                pass
            self.bus = None
        self._connect()

    def send_message(
            self, message: str = "", lang: str = "en-us", **kwargs: Any
    ) -> None:
        """Send a message to HiveMind to speak on instance."""
        try:
            _LOGGER.log(level=3, msg=kwargs)
            if self.bus is None:
                self._connect()
            payload = HiveMessage(HiveMessageType.BUS,
                                  payload=Message("speak",
                                                  {"utterance": message, "lang": lang}))
            self.bus.emit(payload)
            return
        except ConnectionRefusedError:
            _LOGGER.log(
                level=1, msg="Could not reach this instance of HiveMind", exc_info=True
            )

        except ValueError:
            _LOGGER.log(level=1, msg="Error from HiveMind messagebus", exc_info=True)

        # didn't return -> connection is lost
        self._reconnect()
