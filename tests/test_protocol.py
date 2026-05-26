"""Tests for the ZH/JT-03 protocol encoder."""

from __future__ import annotations

import importlib

import pytest

from .common import clear_integration_modules, install_homeassistant_stubs


@pytest.fixture
def protocol(monkeypatch):
    """Import the protocol module with Home Assistant stubs."""
    install_homeassistant_stubs(monkeypatch)
    clear_integration_modules(monkeypatch)
    return importlib.import_module("custom_components.climate_ir_zhjt03.protocol")


def _append_legacy_byte(timings: list[int], value: int) -> None:
    """Append one LSB-first legacy SmartIR byte."""
    for bit_index in range(8):
        timings.append(620)
        timings.append(-620 if value & (1 << bit_index) else -1860)


def _legacy_timings(
    *,
    hvac_mode: str,
    target_temperature: int,
    fan_mode: str,
    swing_mode: str,
) -> list[int]:
    """Generate timings using the legacy SmartIR bit layout and timing rules."""
    modes = {
        "auto": 0x00,
        "cool": 0x01,
        "dry": 0x02,
        "fan_only": 0x03,
        "heat": 0x04,
    }
    fans = {
        "auto": 0x00,
        "high": 0x01,
        "medium": 0x02,
        "low": 0x03,
    }
    swings = {
        "fast": 0x00,
        "slow": 0x01,
        "off": 0x12,
    }

    payload = 0
    payload |= 0xD5 << 40
    payload |= ((target_temperature - 16) & 0x0F) << 32
    payload |= (fans[fan_mode] & 0b11) << 29
    payload |= (swings[swing_mode] & 0b11) << 26
    if hvac_mode != "off":
        payload |= 1 << 25
        payload |= (modes[hvac_mode] & 0b111) << 37

    timings = [6820, -6820]
    for bit_offset in range(0, 48, 8):
        chunk = (payload >> bit_offset) & 0xFF
        _append_legacy_byte(timings, chunk)
        _append_legacy_byte(timings, ~chunk & 0xFF)
    timings.extend([620, -6820, 620])
    return timings


@pytest.mark.parametrize(
    "hvac_mode",
    ["off", "auto", "cool", "heat", "fan_only", "dry"],
)
@pytest.mark.parametrize("fan_mode", ["auto", "low", "medium", "high"])
@pytest.mark.parametrize("swing_mode", ["off", "fast", "slow"])
def test_protocol_matches_legacy_smartir(
    protocol,
    hvac_mode: str,
    fan_mode: str,
    swing_mode: str,
) -> None:
    """ZhJt03Command matches the legacy SmartIR encoder."""
    state = protocol.ZhJt03State(
        hvac_mode=hvac_mode,
        target_temperature=24,
        fan_mode=fan_mode,
        swing_mode=swing_mode,
    )

    command = protocol.ZhJt03Command(state)

    assert command.modulation == 38000
    assert command.get_raw_timings() == _legacy_timings(
        hvac_mode=hvac_mode,
        target_temperature=24,
        fan_mode=fan_mode,
        swing_mode=swing_mode,
    )


@pytest.mark.parametrize("temperature", [16, 32])
def test_temperature_boundaries(protocol, temperature: int) -> None:
    """Minimum and maximum target temperatures are encoded correctly."""
    state = protocol.ZhJt03State(
        hvac_mode="cool",
        target_temperature=temperature,
        fan_mode="auto",
        swing_mode="off",
    )

    assert protocol.ZhJt03Command(state).get_raw_timings() == _legacy_timings(
        hvac_mode="cool",
        target_temperature=temperature,
        fan_mode="auto",
        swing_mode="off",
    )


@pytest.mark.parametrize("temperature", [15, 33])
def test_temperature_outside_supported_range_is_rejected(
    protocol,
    temperature: int,
) -> None:
    """Out-of-range target temperatures cannot leak into reserved payload bits."""
    state = protocol.ZhJt03State(
        hvac_mode="cool",
        target_temperature=temperature,
        fan_mode="auto",
        swing_mode="off",
    )

    with pytest.raises(ValueError, match="target temperature"):
        protocol.ZhJt03Command(state).get_raw_timings()


def test_power_bit_changes_payload(protocol) -> None:
    """Off and on commands differ in the encoded power field."""
    off_state = protocol.ZhJt03State(
        hvac_mode="off",
        target_temperature=24,
        fan_mode="auto",
        swing_mode="off",
    )
    cool_state = protocol.ZhJt03State(
        hvac_mode="cool",
        target_temperature=24,
        fan_mode="auto",
        swing_mode="off",
    )

    assert protocol.ZhJt03Command(off_state).get_raw_timings() != (protocol.ZhJt03Command(cool_state).get_raw_timings())
