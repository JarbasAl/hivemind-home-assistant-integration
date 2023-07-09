"""HiveMind notification platform."""
import logging
import os
from typing import Any

from hivemind_bus_client.client import HiveMessageBusClient
from hivemind_bus_client.identity import NodeIdentity
from hivemind_bus_client.message import HiveMessageType, HiveMessage
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    BaseNotificationService,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from json_database import JsonStorage
from ovos_bus_client import Message

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities,
):
    """Setup from a config entry created in the integrations UI."""
    async_add_entities([HiveMindNotificationService(**config_entry)], True)


class HiveMindNotificationService(BaseNotificationService):
    """The HiveMind Notification Service."""

    def __init__(self, key: str, password: str, host: str, port: int = 5678,
                 self_signed: bool = False, **kwargs) -> None:
        """Initialize the service."""
        self.key = key
        self.password = password
        self.port = port
        self.host = host
        self.self_signed = self_signed
        self.bus = HiveMessageBusClient(key=self.key,
                                        password=self.password,
                                        port=self.port,
                                        host=self.host,
                                        useragent="HomeAssistantV0.0.1",
                                        self_signed=self.self_signed)
        # NOTE: we explicitly pass a identity file to work around HA being root
        #  FileNotFoundError: [Errno 2] No such file or directory: '/root/.config/hivemind/unnamed-node.asc'
        identity_file = JsonStorage(f"{os.path.dirname(__file__)}/_identity.json")
        self.bus.connect(identity=NodeIdentity(identity_file))
        # self.bus.on_mycroft("recognizer_loop:output_start", self.handle_tts_start)
        # self.bus.on_mycroft("recognizer_loop:output_end", self.handle_tts_end)

    def handle_tts_start(self, message):
        _LOGGER.info("TTS started on OVOS device")

    def handle_tts_end(self, message):
        _LOGGER.info("TTS ended on OVOS device")

    def send_message(
            self, message: str = "", **kwargs: Any
    ) -> None:
        """Send a message to HiveMind to speak on instance."""
        targets = kwargs.get(ATTR_TARGET)

        data = kwargs.get(ATTR_DATA) or {}  # lang can be specified here
        data["utterance"] = message

        payload = HiveMessage(HiveMessageType.BUS, Message("speak", data))
        try:
            _LOGGER.log(level=3, msg=kwargs)
            self.bus.emit(payload)
        except:
            _LOGGER.log(level=1, msg="Error from HiveMind messagebus", exc_info=True)


def get_service(
        hass: HomeAssistant,
        config: ConfigType,
        discovery_info: DiscoveryInfoType | None = None,
) -> HiveMindNotificationService:
    """Get the HiveMind notification service."""
    return HiveMindNotificationService(**config)
