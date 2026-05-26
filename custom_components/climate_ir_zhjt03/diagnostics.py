"""Diagnostics support for Climate for IR Devices using ZH/JT-03 Remote."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import CONF_HUMIDITY_SENSOR, CONF_INFRARED_ENTITY_ID, CONF_POWER_SENSOR, CONF_TEMPERATURE_SENSOR

TO_REDACT = {
    "title",
    CONF_NAME,
    CONF_INFRARED_ENTITY_ID,
    CONF_TEMPERATURE_SENSOR,
    CONF_HUMIDITY_SENSOR,
    CONF_POWER_SENSOR,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return {
        "entry": async_redact_data(
            {
                "entry_id": entry.entry_id,
                "title": entry.title,
                "unique_id": entry.unique_id,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            TO_REDACT,
        ),
    }
