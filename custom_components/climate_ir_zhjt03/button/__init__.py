"""Button platform for climate_ir_zhjt03."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.climate_ir_zhjt03.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.button import ButtonEntityDescription

from .reset_filter import ENTITY_DESCRIPTIONS as RESET_DESCRIPTIONS, ClimateZHJT03Button

if TYPE_CHECKING:
    from custom_components.climate_ir_zhjt03.data import ClimateZHJT03ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (*RESET_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClimateZHJT03ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        ClimateZHJT03Button(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )
