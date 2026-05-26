"""
Custom types for climate_ir_zhjt03.

This module defines the runtime data structure attached to each config entry.
Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator

The ClimateZHJT03ConfigEntry type alias is used throughout the integration
for type-safe access to the config entry's runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ClimateZHJT03ApiClient
    from .coordinator import ClimateZHJT03DataUpdateCoordinator


type ClimateZHJT03ConfigEntry = ConfigEntry[ClimateZHJT03Data]


@dataclass
class ClimateZHJT03Data:
    """Runtime data for climate_ir_zhjt03 config entries.

    Stored as entry.runtime_data after successful setup.
    Provides typed access to the API client and coordinator instances.
    """

    client: ClimateZHJT03ApiClient
    coordinator: ClimateZHJT03DataUpdateCoordinator
    integration: Integration
