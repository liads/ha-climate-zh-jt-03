"""Number platform for climate_ir_zhjt03."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.climate_ir_zhjt03.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.number import NumberEntityDescription

from .target_humidity import ENTITY_DESCRIPTIONS as HUMIDITY_DESCRIPTIONS, ClimateZHJT03HumidityNumber

if TYPE_CHECKING:
    from custom_components.climate_ir_zhjt03.data import ClimateZHJT03ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (*HUMIDITY_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClimateZHJT03ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        ClimateZHJT03HumidityNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in HUMIDITY_DESCRIPTIONS
    )
