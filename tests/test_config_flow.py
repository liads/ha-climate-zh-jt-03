"""Tests for the ZH/JT-03 config flow."""

from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace

import pytest

from .common import (
    ConfigEntries,
    EntityRegistry,
    SensorDeviceClass,
    clear_integration_modules,
    install_homeassistant_stubs,
)


@pytest.fixture
def config_flow(monkeypatch):
    """Import the config flow module with Home Assistant stubs."""
    install_homeassistant_stubs(monkeypatch)
    clear_integration_modules(monkeypatch)
    return importlib.import_module(
        "custom_components.climate_ir_zhjt03.config_flow_handler.config_flow",
    )


def _flow(config_flow, unique_id: str | None = None, entries: list[SimpleNamespace] | None = None):
    """Create a config flow with a fake entity registry."""
    flow = config_flow.ClimateZHJT03ConfigFlowHandler()
    flow.hass = SimpleNamespace(
        config_entries=ConfigEntries(entries),
        entity_registry=EntityRegistry(unique_id, "remote"),
    )
    return flow


def _config_entry(config_flow, **overrides):
    """Create a fake config entry."""
    data = {
        config_flow.CONF_NAME: "Bedroom AC",
        config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
        config_flow.CONF_TEMPERATURE_SENSOR: "sensor.old_temperature",
        config_flow.CONF_HUMIDITY_SENSOR: "sensor.old_humidity",
    }
    data.update(overrides.pop("data", {}))
    return SimpleNamespace(
        data=data,
        entry_id=overrides.pop("entry_id", "entry-1"),
        title=overrides.pop("title", "Bedroom AC"),
        unique_id=overrides.pop("unique_id", "zh_jt_03_remote_abc123"),
        **overrides,
    )


def _marker(schema, field_name: str):
    """Return a field marker from a tiny voluptuous schema."""
    for marker in schema.schema:
        if marker.schema == field_name:
            return marker
    raise AssertionError(f"{field_name} was not found in schema")


def _schema_value(schema, field_name: str):
    """Return a selector value from a tiny voluptuous schema."""
    for marker, value in schema.schema.items():
        if marker.schema == field_name:
            return value
    raise AssertionError(f"{field_name} was not found in schema")


def test_step_user_aborts_without_emitters(config_flow, monkeypatch) -> None:
    """The flow aborts when no infrared emitters exist."""
    monkeypatch.setattr(config_flow.infrared, "async_get_emitters", lambda hass: [])

    result = asyncio.run(_flow(config_flow).async_step_user())

    assert result == {"type": "abort", "reason": "no_emitters"}


def test_step_user_filters_optional_sensor_selectors(config_flow, monkeypatch) -> None:
    """The form limits optional sensor selectors by device class."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )

    result = asyncio.run(_flow(config_flow).async_step_user())
    schema = result["data_schema"]

    emitter = _schema_value(schema, config_flow.CONF_INFRARED_ENTITY_ID)
    temperature = _schema_value(schema, config_flow.CONF_TEMPERATURE_SENSOR)
    humidity = _schema_value(schema, config_flow.CONF_HUMIDITY_SENSOR)

    assert emitter.config == {
        "domain": "infrared",
        "include_entities": ["infrared.remote"],
    }
    assert temperature.config["filter"] == {
        "domain": "sensor",
        "device_class": SensorDeviceClass.TEMPERATURE,
    }
    assert humidity.config["filter"] == {
        "domain": "sensor",
        "device_class": SensorDeviceClass.HUMIDITY,
    }


def test_step_user_creates_entry_with_emitter_unique_id(
    config_flow,
    monkeypatch,
) -> None:
    """The flow stores selected entities and derives a stable unique ID."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )

    flow = _flow(config_flow, unique_id="abc123")
    result = asyncio.run(
        flow.async_step_user(
            {
                config_flow.CONF_NAME: " Bedroom AC ",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
                config_flow.CONF_TEMPERATURE_SENSOR: "sensor.bedroom_temperature",
                config_flow.CONF_HUMIDITY_SENSOR: "",
            },
        ),
    )

    assert flow.unique_id == "zh_jt_03_remote_abc123"
    assert flow.duplicate_check_called is True
    assert result["type"] == "create_entry"
    assert result["title"] == "Bedroom AC"
    assert result["data"] == {
        config_flow.CONF_NAME: "Bedroom AC",
        config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
        config_flow.CONF_TEMPERATURE_SENSOR: "sensor.bedroom_temperature",
    }


def test_step_user_falls_back_to_emitter_entity_id(config_flow, monkeypatch) -> None:
    """The flow falls back to the emitter entity ID when registry data is missing."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )

    flow = _flow(config_flow)
    asyncio.run(
        flow.async_step_user(
            {
                config_flow.CONF_NAME: "Bedroom AC",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
            },
        ),
    )

    assert flow.unique_id == "zh_jt_03_infrared.remote"


def test_step_user_rejects_empty_name(config_flow, monkeypatch) -> None:
    """The flow redisplays the form when the name is empty."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )

    result = asyncio.run(
        _flow(config_flow).async_step_user(
            {
                config_flow.CONF_NAME: " ",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
            },
        ),
    )

    assert result["type"] == "form"
    assert result["errors"] == {config_flow.CONF_NAME: "name_required"}


def test_step_user_aborts_when_emitter_is_already_used(config_flow, monkeypatch) -> None:
    """The flow rejects an infrared emitter that is already assigned to an entry."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )
    existing_entry = _config_entry(config_flow)

    result = asyncio.run(
        _flow(config_flow, entries=[existing_entry]).async_step_user(
            {
                config_flow.CONF_NAME: "Kitchen AC",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote",
            },
        ),
    )

    assert result == {"type": "abort", "reason": "already_configured"}


def test_step_reconfigure_includes_current_unavailable_emitter(config_flow, monkeypatch) -> None:
    """The reconfigure form keeps the current emitter selectable if it is unavailable."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote"],
    )
    entry = _config_entry(
        config_flow,
        data={config_flow.CONF_INFRARED_ENTITY_ID: "infrared.missing"},
    )
    flow = _flow(config_flow, entries=[entry])
    flow.reconfigure_entry = entry

    result = asyncio.run(flow.async_step_reconfigure())
    schema = result["data_schema"]
    emitter = _schema_value(schema, config_flow.CONF_INFRARED_ENTITY_ID)

    assert result["type"] == "form"
    assert emitter.config == {
        "domain": "infrared",
        "include_entities": ["infrared.remote", "infrared.missing"],
    }
    assert _marker(schema, config_flow.CONF_NAME).default == "Bedroom AC"
    assert _marker(schema, config_flow.CONF_INFRARED_ENTITY_ID).default == "infrared.missing"


def test_step_reconfigure_updates_existing_entry(config_flow, monkeypatch) -> None:
    """The reconfigure flow updates and reloads the existing entry."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote", "infrared.remote_2"],
    )
    entry = _config_entry(config_flow)
    flow = _flow(config_flow, entries=[entry])
    flow.reconfigure_entry = entry

    result = asyncio.run(
        flow.async_step_reconfigure(
            {
                config_flow.CONF_NAME: " Living Room AC ",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote_2",
                config_flow.CONF_TEMPERATURE_SENSOR: "",
                config_flow.CONF_HUMIDITY_SENSOR: "",
                config_flow.CONF_POWER_SENSOR: "binary_sensor.living_room_ac_power",
            },
        ),
    )

    assert flow.unique_id == "zh_jt_03_remote_abc123"
    assert flow.unique_id_mismatch_check_called is True
    assert flow.updated_entry is entry
    assert result == {"type": "abort", "reason": "reconfigure_successful"}
    assert entry.title == "Living Room AC"
    assert entry.data == {
        config_flow.CONF_NAME: "Living Room AC",
        config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote_2",
        config_flow.CONF_POWER_SENSOR: "binary_sensor.living_room_ac_power",
    }
    assert flow.hass.config_entries.reloads == ["entry-1"]


def test_step_reconfigure_rejects_emitter_used_by_another_entry(config_flow, monkeypatch) -> None:
    """The reconfigure flow rejects an emitter that belongs to another entry."""
    monkeypatch.setattr(
        config_flow.infrared,
        "async_get_emitters",
        lambda hass: ["infrared.remote", "infrared.remote_2"],
    )
    entry = _config_entry(config_flow, entry_id="entry-1")
    other_entry = _config_entry(
        config_flow,
        entry_id="entry-2",
        data={config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote_2"},
    )
    flow = _flow(config_flow, entries=[entry, other_entry])
    flow.reconfigure_entry = entry

    result = asyncio.run(
        flow.async_step_reconfigure(
            {
                config_flow.CONF_NAME: "Bedroom AC",
                config_flow.CONF_INFRARED_ENTITY_ID: "infrared.remote_2",
            },
        ),
    )

    assert result["type"] == "form"
    assert result["errors"] == {
        config_flow.CONF_INFRARED_ENTITY_ID: "emitter_already_configured",
    }
    assert flow.hass.config_entries.reloads == []
