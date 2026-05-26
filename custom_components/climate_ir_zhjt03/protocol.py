"""ZH/JT-03 infrared protocol encoder."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from homeassistant.components.climate.const import FAN_AUTO, FAN_HIGH, FAN_LOW, FAN_MEDIUM, HVACMode

from .compat import InfraredCommand
from .const import MAX_TEMPERATURE, MIN_TEMPERATURE, SWING_FAST, SWING_OFF, SWING_SLOW

DEFAULT_MODULATION = 38000

TICK_US = 620
BIT_MARK = TICK_US
ONE_SPACE = -TICK_US
ZERO_SPACE = -(TICK_US * 3)
HEADER_MARK = TICK_US * 11
HEADER_SPACE = -(TICK_US * 11)
PAYLOAD_BITS = 48
END_FRAME = 0xD5

BIT_POWER = 25
BIT_SWING = 26
BIT_FAN = 29
BIT_TEMPERATURE = 32
BIT_MODE = 37
BIT_END_FRAME = 40


class ZhJt03Mode(IntEnum):
    """ZH/JT-03 HVAC mode values."""

    AUTO = 0x00
    COOL = 0x01
    DRY = 0x02
    FAN_ONLY = 0x03
    HEAT = 0x04


class ZhJt03Fan(IntEnum):
    """ZH/JT-03 fan values."""

    AUTO = 0x00
    HIGH = 0x01
    MEDIUM = 0x02
    LOW = 0x03


class ZhJt03Swing(IntEnum):
    """ZH/JT-03 swing values."""

    FAST = 0x00
    SLOW = 0x01
    OFF = 0x12


class ZhJt03Power(IntEnum):
    """ZH/JT-03 power values."""

    OFF = 0x00
    ON = 0x01


HVAC_MODE_TO_PROTOCOL: dict[HVACMode, ZhJt03Mode] = {
    HVACMode.AUTO: ZhJt03Mode.AUTO,
    HVACMode.COOL: ZhJt03Mode.COOL,
    HVACMode.DRY: ZhJt03Mode.DRY,
    HVACMode.FAN_ONLY: ZhJt03Mode.FAN_ONLY,
    HVACMode.HEAT: ZhJt03Mode.HEAT,
}

FAN_MODE_TO_PROTOCOL: dict[str, ZhJt03Fan] = {
    FAN_AUTO: ZhJt03Fan.AUTO,
    FAN_LOW: ZhJt03Fan.LOW,
    FAN_MEDIUM: ZhJt03Fan.MEDIUM,
    FAN_HIGH: ZhJt03Fan.HIGH,
}

SWING_MODE_TO_PROTOCOL: dict[str, ZhJt03Swing] = {
    SWING_OFF: ZhJt03Swing.OFF,
    SWING_FAST: ZhJt03Swing.FAST,
    SWING_SLOW: ZhJt03Swing.SLOW,
}


@dataclass(frozen=True, slots=True)
class ZhJt03State:
    """State encoded into a ZH/JT-03 command."""

    hvac_mode: HVACMode
    target_temperature: int
    fan_mode: str | None = None
    swing_mode: str | None = None


class ZhJt03Command(InfraredCommand):
    """ZH/JT-03 infrared command."""

    def __init__(
        self,
        state: ZhJt03State,
        *,
        modulation: int = DEFAULT_MODULATION,
        repeat_count: int = 0,
    ) -> None:
        """Initialize the ZH/JT-03 command."""
        super().__init__(modulation=modulation, repeat_count=repeat_count)
        self.state = state

    def get_raw_timings(self) -> list[int]:
        """Return raw timings for the ZH/JT-03 command."""
        return _build_frame(_build_payload(self.state))


def _build_payload(state: ZhJt03State) -> int:
    """Build the 48-bit ZH/JT-03 payload before per-byte inversion."""
    _validate_target_temperature(state.target_temperature)

    payload = 0
    payload = _set_field(payload, END_FRAME, BIT_END_FRAME, 8)
    payload = _set_field(
        payload,
        state.target_temperature - MIN_TEMPERATURE,
        BIT_TEMPERATURE,
        4,
    )

    if state.fan_mode is not None:
        payload = _set_field(
            payload,
            int(FAN_MODE_TO_PROTOCOL[state.fan_mode]),
            BIT_FAN,
            2,
        )

    if state.swing_mode is not None:
        payload = _set_field(
            payload,
            int(SWING_MODE_TO_PROTOCOL[state.swing_mode]),
            BIT_SWING,
            2,
        )

    if state.hvac_mode == HVACMode.OFF:
        return _set_field(payload, int(ZhJt03Power.OFF), BIT_POWER, 1)

    payload = _set_field(payload, int(ZhJt03Power.ON), BIT_POWER, 1)
    return _set_field(
        payload,
        int(HVAC_MODE_TO_PROTOCOL[state.hvac_mode]),
        BIT_MODE,
        3,
    )


def _build_frame(payload: int) -> list[int]:
    """Build raw timings for the payload."""
    timings = [HEADER_MARK, HEADER_SPACE]

    for bit_offset in range(0, PAYLOAD_BITS, 8):
        chunk = (payload >> bit_offset) & 0xFF
        _append_byte(timings, chunk)
        _append_byte(timings, ~chunk & 0xFF)

    timings.extend([BIT_MARK, HEADER_SPACE, BIT_MARK])
    return timings


def _append_byte(timings: list[int], value: int) -> None:
    """Append one LSB-first byte to raw timings."""
    for bit_index in range(8):
        timings.append(BIT_MARK)
        timings.append(ONE_SPACE if value & (1 << bit_index) else ZERO_SPACE)


def _set_field(payload: int, value: int, bit_offset: int, width: int) -> int:
    """Set a bit field in a payload."""
    mask = (1 << width) - 1
    return payload | ((value & mask) << bit_offset)


def _validate_target_temperature(target_temperature: int) -> None:
    """Validate the target temperature can be encoded safely."""
    if MIN_TEMPERATURE <= target_temperature <= MAX_TEMPERATURE:
        return

    raise ValueError(
        f"ZH/JT-03 target temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE} C",
    )
