"""Select platform for climate_ir_zhjt03."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.climate_ir_zhjt03.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.select import SelectEntityDescription

from .fan_speed import ENTITY_DESCRIPTIONS as FAN_SPEED_DESCRIPTIONS, ClimateZHJT03FanSpeedSelect

if TYPE_CHECKING:
    from custom_components.climate_ir_zhjt03.data import ClimateZHJT03ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (*FAN_SPEED_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClimateZHJT03ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        ClimateZHJT03FanSpeedSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in FAN_SPEED_DESCRIPTIONS
    )
