"""Climate entity for AC units using the ZH/JT-03 IR remote."""

from __future__ import annotations

import logging
from math import isfinite
from typing import Any

from custom_components.climate_ir_zhjt03.const import (
    CONF_HUMIDITY_SENSOR,
    CONF_INFRARED_ENTITY_ID,
    CONF_POWER_SENSOR,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_FAN_MODE,
    DEFAULT_HVAC_MODE,
    DEFAULT_TEMPERATURE,
    DOMAIN,
    MANUFACTURER,
    MAX_TEMPERATURE,
    MIN_TEMPERATURE,
    MODEL,
    SUPPORTED_FAN_MODES,
    SUPPORTED_HVAC_MODES,
    SUPPORTED_SWING_MODES,
    SWING_OFF,
)
from custom_components.climate_ir_zhjt03.protocol import ZhJt03Command, ZhJt03State
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ATTR_HVAC_MODE, ClimateEntityFeature, HVACMode
from homeassistant.components.infrared import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    PRECISION_WHOLE,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import Event, EventStateChangedData, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from homeassistant.util.unit_conversion import TemperatureConverter

_LOGGER = logging.getLogger(__name__)

LAST_ON_OPERATION = "last_on_operation"


def _coerce_target_temperature(temperature: Any) -> int | None:
    """Coerce and validate a ZH/JT-03 target temperature."""
    try:
        target_temperature = round(float(temperature))
    except TypeError, ValueError, OverflowError:
        _LOGGER.warning("Ignoring non-numeric ZH/JT-03 temperature: %s", temperature)
        return None

    if MIN_TEMPERATURE <= target_temperature <= MAX_TEMPERATURE:
        return target_temperature

    _LOGGER.warning("Temperature %s is outside the ZH/JT-03 range", temperature)
    return None


def _coerce_hvac_mode(hvac_mode: Any, *, warn: bool = True) -> HVACMode | None:
    """Coerce and validate a ZH/JT-03 HVAC mode."""
    if hvac_mode is None:
        return None

    try:
        coerced_hvac_mode = HVACMode(hvac_mode)
    except TypeError, ValueError:
        if warn:
            _LOGGER.warning("Unsupported ZH/JT-03 HVAC mode: %s", hvac_mode)
        return None

    if coerced_hvac_mode in SUPPORTED_HVAC_MODES:
        return coerced_hvac_mode

    if warn:
        _LOGGER.warning("Unsupported ZH/JT-03 HVAC mode: %s", hvac_mode)
    return None


class ClimateZHJT03(ClimateEntity, RestoreEntity):
    """ZH/JT-03 climate entity controlled through an infrared emitter."""

    _attr_assumed_state = True
    _attr_has_entity_name = True
    _attr_name = None
    _attr_hvac_modes = SUPPORTED_HVAC_MODES
    _attr_fan_modes = SUPPORTED_FAN_MODES
    _attr_swing_modes = SUPPORTED_SWING_MODES
    _attr_min_temp = MIN_TEMPERATURE
    _attr_max_temp = MAX_TEMPERATURE
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_supported_features = (
        ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the ZH/JT-03 climate entity."""
        data = entry.data
        name = data[CONF_NAME]
        config_unique_id = entry.unique_id or entry.entry_id

        self._attr_unique_id = f"{config_unique_id}_climate"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_unique_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=name,
        )
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature = DEFAULT_TEMPERATURE
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_fan_mode = DEFAULT_FAN_MODE
        self._attr_swing_mode = SWING_OFF
        self._attr_available = False

        self._infrared_emitter_entity_id: str = data[CONF_INFRARED_ENTITY_ID]
        self._temperature_sensor_entity_id: str | None = data.get(CONF_TEMPERATURE_SENSOR)
        self._humidity_sensor_entity_id: str | None = data.get(CONF_HUMIDITY_SENSOR)
        self._power_sensor_entity_id: str | None = data.get(CONF_POWER_SENSOR)
        self._last_on_operation: HVACMode = DEFAULT_HVAC_MODE
        self._last_sent_hvac_mode: HVACMode = HVACMode.OFF

    async def async_added_to_hass(self) -> None:
        """Subscribe to entity changes and restore the previous climate state."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is not None:
            self._restore_climate_state(last_state.state, last_state.attributes)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._infrared_emitter_entity_id],
                self._async_infrared_emitter_changed,
            ),
        )
        self._update_infrared_availability(
            self.hass.states.get(self._infrared_emitter_entity_id),
        )

        if self._temperature_sensor_entity_id is not None:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._temperature_sensor_entity_id],
                    self._async_temperature_sensor_changed,
                ),
            )
            self._update_temperature_from_state(
                self.hass.states.get(self._temperature_sensor_entity_id),
            )

        if self._humidity_sensor_entity_id is not None:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._humidity_sensor_entity_id],
                    self._async_humidity_sensor_changed,
                ),
            )
            self._update_humidity_from_state(
                self.hass.states.get(self._humidity_sensor_entity_id),
            )

        if self._power_sensor_entity_id is not None:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._power_sensor_entity_id],
                    self._async_power_sensor_changed,
                ),
            )
            self._update_power_from_state(
                self.hass.states.get(self._power_sensor_entity_id),
            )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return integration-specific state attributes."""
        return {LAST_ON_OPERATION: self._last_on_operation}

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)

        if temperature is None and hvac_mode is None:
            return

        next_temperature = self._target_temperature
        if temperature is not None and (next_temperature := _coerce_target_temperature(temperature)) is None:
            return

        next_hvac_mode = self._hvac_mode
        if hvac_mode is not None:
            if (next_hvac_mode := _coerce_hvac_mode(hvac_mode)) is None:
                return

        if next_hvac_mode == HVACMode.OFF and hvac_mode is None:
            self._attr_target_temperature = next_temperature
            self.async_write_ha_state()
            return

        await self._async_apply_state(
            hvac_mode=next_hvac_mode,
            target_temperature=next_temperature,
            fan_mode=self._fan_mode,
            swing_mode=self._swing_mode,
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        if (next_hvac_mode := _coerce_hvac_mode(hvac_mode)) is None:
            return

        await self._async_apply_state(
            hvac_mode=next_hvac_mode,
            target_temperature=self._target_temperature,
            fan_mode=self._fan_mode,
            swing_mode=self._swing_mode,
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the fan mode."""
        if fan_mode not in SUPPORTED_FAN_MODES:
            _LOGGER.warning("Unsupported ZH/JT-03 fan mode: %s", fan_mode)
            return

        if self._hvac_mode == HVACMode.OFF:
            self._attr_fan_mode = fan_mode
            self.async_write_ha_state()
            return

        await self._async_apply_state(
            hvac_mode=self._hvac_mode,
            target_temperature=self._target_temperature,
            fan_mode=fan_mode,
            swing_mode=self._swing_mode,
        )

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set the swing mode."""
        if swing_mode not in SUPPORTED_SWING_MODES:
            _LOGGER.warning("Unsupported ZH/JT-03 swing mode: %s", swing_mode)
            return

        if self._hvac_mode == HVACMode.OFF:
            self._attr_swing_mode = swing_mode
            self.async_write_ha_state()
            return

        await self._async_apply_state(
            hvac_mode=self._hvac_mode,
            target_temperature=self._target_temperature,
            fan_mode=self._fan_mode,
            swing_mode=swing_mode,
        )

    async def async_turn_on(self) -> None:
        """Turn on the AC using the last non-off mode."""
        await self.async_set_hvac_mode(self._last_on_operation)

    async def async_turn_off(self) -> None:
        """Turn off the AC."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def _async_apply_state(
        self,
        *,
        hvac_mode: HVACMode,
        target_temperature: int,
        fan_mode: str,
        swing_mode: str,
    ) -> None:
        """Send an IR command and update the assumed climate state."""
        if hvac_mode not in SUPPORTED_HVAC_MODES:
            _LOGGER.warning("Unsupported ZH/JT-03 HVAC mode: %s", hvac_mode)
            return

        if fan_mode not in SUPPORTED_FAN_MODES:
            _LOGGER.warning("Unsupported ZH/JT-03 fan mode: %s", fan_mode)
            return

        if swing_mode not in SUPPORTED_SWING_MODES:
            _LOGGER.warning("Unsupported ZH/JT-03 swing mode: %s", swing_mode)
            return

        validated_temperature = _coerce_target_temperature(target_temperature)
        if validated_temperature is None:
            return
        target_temperature = validated_temperature

        command = ZhJt03Command(
            ZhJt03State(
                hvac_mode=hvac_mode,
                target_temperature=target_temperature,
                fan_mode=fan_mode,
                swing_mode=swing_mode,
            ),
        )
        await self._async_send_ir_command(command)

        self._attr_hvac_mode = hvac_mode
        self._attr_target_temperature = target_temperature
        self._attr_fan_mode = fan_mode
        self._attr_swing_mode = swing_mode
        self._last_sent_hvac_mode = hvac_mode
        if hvac_mode != HVACMode.OFF:
            self._last_on_operation = hvac_mode
        self.async_write_ha_state()

    @property
    def _hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode with the entity default applied."""
        return self._attr_hvac_mode or HVACMode.OFF

    @property
    def _target_temperature(self) -> int:
        """Return the current target temperature with the entity default applied."""
        if (target_temperature := _coerce_target_temperature(self._attr_target_temperature)) is not None:
            return target_temperature

        return DEFAULT_TEMPERATURE

    @property
    def _fan_mode(self) -> str:
        """Return the current fan mode with the entity default applied."""
        return self._attr_fan_mode or DEFAULT_FAN_MODE

    @property
    def _swing_mode(self) -> str:
        """Return the current swing mode with the entity default applied."""
        return self._attr_swing_mode or SWING_OFF

    def _restore_climate_state(
        self,
        state: StateType,
        attributes: dict[str, Any],
    ) -> None:
        """Restore previous climate state attributes."""
        if (restored_hvac_mode := _coerce_hvac_mode(state, warn=False)) is not None:
            self._attr_hvac_mode = restored_hvac_mode
            self._last_sent_hvac_mode = restored_hvac_mode

        if (temperature := attributes.get(ATTR_TEMPERATURE)) is not None and (
            restored_temperature := _coerce_target_temperature(temperature)
        ) is not None:
            self._attr_target_temperature = restored_temperature

        if (fan_mode := attributes.get("fan_mode")) in SUPPORTED_FAN_MODES:
            self._attr_fan_mode = fan_mode

        if (swing_mode := attributes.get("swing_mode")) in SUPPORTED_SWING_MODES:
            self._attr_swing_mode = swing_mode

        last_on_operation = attributes.get(LAST_ON_OPERATION)
        if (
            restored_last_on_operation := _coerce_hvac_mode(last_on_operation, warn=False)
        ) is not None and restored_last_on_operation != HVACMode.OFF:
            self._last_on_operation = restored_last_on_operation
        elif self._hvac_mode != HVACMode.OFF:
            self._last_on_operation = self._hvac_mode

    async def _async_send_ir_command(self, command: ZhJt03Command) -> None:
        """Send an IR command through the configured infrared emitter."""
        await async_send_command(
            self.hass,
            self._infrared_emitter_entity_id,
            command,
            context=self._context,
        )

    @callback
    def _async_infrared_emitter_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle infrared emitter availability changes."""
        self._update_infrared_availability(event.data["new_state"])

    @callback
    def _async_temperature_sensor_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle temperature sensor changes."""
        self._update_temperature_from_state(event.data["new_state"])
        self.async_write_ha_state()

    @callback
    def _async_humidity_sensor_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle humidity sensor changes."""
        self._update_humidity_from_state(event.data["new_state"])
        self.async_write_ha_state()

    @callback
    def _async_power_sensor_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle power sensor changes."""
        self._update_power_from_state(event.data["new_state"])
        self.async_write_ha_state()

    @callback
    def _update_infrared_availability(self, state: State | None) -> None:
        """Update availability from the configured infrared emitter state."""
        available = state is not None and state.state != STATE_UNAVAILABLE
        if available == self.available:
            return

        _LOGGER.info(
            "Infrared entity %s used by %s is %s",
            self._infrared_emitter_entity_id,
            self.entity_id,
            "available" if available else "unavailable",
        )
        self._attr_available = available
        self.async_write_ha_state()

    @callback
    def _update_temperature_from_state(self, state: State | None) -> None:
        """Update the current temperature from a sensor state."""
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            temperature = float(state.state)
        except TypeError, ValueError:
            _LOGGER.warning("Ignoring non-numeric temperature from %s", state.entity_id)
            return

        if not isfinite(temperature):
            _LOGGER.warning("Ignoring non-finite temperature from %s", state.entity_id)
            return

        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        if unit not in (None, UnitOfTemperature.CELSIUS):
            try:
                temperature = TemperatureConverter.convert(
                    temperature,
                    unit,
                    UnitOfTemperature.CELSIUS,
                )
            except HomeAssistantError:
                _LOGGER.warning(
                    "Ignoring temperature from %s with unsupported unit %s",
                    state.entity_id,
                    unit,
                )
                return

        self._attr_current_temperature = temperature

    @callback
    def _update_humidity_from_state(self, state: State | None) -> None:
        """Update the current humidity from a sensor state."""
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            humidity = float(state.state)
        except TypeError, ValueError:
            _LOGGER.warning("Ignoring non-numeric humidity from %s", state.entity_id)
            return

        if not isfinite(humidity):
            _LOGGER.warning("Ignoring non-finite humidity from %s", state.entity_id)
            return

        self._attr_current_humidity = humidity

    @callback
    def _update_power_from_state(self, state: State | None) -> None:
        """Update assumed HVAC mode from the optional power sensor."""
        if state is None:
            return

        if state.state == STATE_OFF:
            self._attr_hvac_mode = HVACMode.OFF
            self._last_sent_hvac_mode = HVACMode.OFF
        elif state.state == STATE_ON and self._hvac_mode == HVACMode.OFF:
            self._attr_hvac_mode = self._last_on_operation
            self._last_sent_hvac_mode = self._hvac_mode
