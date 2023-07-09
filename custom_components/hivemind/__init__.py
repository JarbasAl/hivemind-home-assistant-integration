"""Send notifications to OpenVoiceOS via HiveMind"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    # Forward the setup to the notify platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "notify")
    )
    return True
