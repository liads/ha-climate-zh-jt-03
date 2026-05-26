"""Climate platform for Climate for IR Devices using ZH/JT-03 Remote."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .zh_jt_03 import ClimateZHJT03

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a ZH/JT-03 climate entity from a config entry."""
    async_add_entities([ClimateZHJT03(entry)])
