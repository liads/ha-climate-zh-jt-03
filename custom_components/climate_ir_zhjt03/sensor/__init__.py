"""Sensor platform for climate_ir_zhjt03."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.climate_ir_zhjt03.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.sensor import SensorEntityDescription

from .air_quality import ENTITY_DESCRIPTIONS as AIR_QUALITY_DESCRIPTIONS, ClimateZHJT03AirQualitySensor
from .diagnostic import ENTITY_DESCRIPTIONS as DIAGNOSTIC_DESCRIPTIONS, ClimateZHJT03DiagnosticSensor

if TYPE_CHECKING:
    from custom_components.climate_ir_zhjt03.data import ClimateZHJT03ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    *AIR_QUALITY_DESCRIPTIONS,
    *DIAGNOSTIC_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClimateZHJT03ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Add air quality sensors
    async_add_entities(
        ClimateZHJT03AirQualitySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in AIR_QUALITY_DESCRIPTIONS
    )
    # Add diagnostic sensors
    async_add_entities(
        ClimateZHJT03DiagnosticSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in DIAGNOSTIC_DESCRIPTIONS
    )
