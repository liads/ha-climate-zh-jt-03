"""Config flow for Climate for IR Devices using ZH/JT-03 Remote."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from custom_components.climate_ir_zhjt03.const import (
    CONF_HUMIDITY_SENSOR,
    CONF_INFRARED_ENTITY_ID,
    CONF_POWER_SENSOR,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_NAME,
    DOMAIN,
)
from homeassistant.components import infrared
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig, TextSelector

OPTIONAL_ENTITY_CONFIG_KEYS = (
    CONF_TEMPERATURE_SENSOR,
    CONF_HUMIDITY_SENSOR,
    CONF_POWER_SENSOR,
)


class ClimateZHJT03ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Climate for IR Devices using ZH/JT-03 Remote."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        emitter_entity_ids = infrared.async_get_emitters(self.hass)
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        errors: dict[str, str] = {}

        if user_input is not None:
            data = _data_from_user_input(user_input)
            if not data[CONF_NAME]:
                errors[CONF_NAME] = "name_required"
            else:
                emitter_entity_id = data[CONF_INFRARED_ENTITY_ID]
                if _emitter_entity_in_use(self.hass, emitter_entity_id):
                    return self.async_abort(reason="already_configured")

                await self.async_set_unique_id(
                    _unique_id_for_emitter(self.hass, emitter_entity_id),
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=data[CONF_NAME],
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(emitter_entity_ids),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing config entry."""
        entry = self._get_reconfigure_entry()
        emitter_entity_ids = _emitter_entity_ids_for_reconfigure(
            self.hass,
            entry.data[CONF_INFRARED_ENTITY_ID],
        )
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        errors: dict[str, str] = {}

        if user_input is not None:
            data = _data_from_user_input(user_input)
            if not data[CONF_NAME]:
                errors[CONF_NAME] = "name_required"
            elif _emitter_entity_in_use(
                self.hass,
                data[CONF_INFRARED_ENTITY_ID],
                current_entry_id=entry.entry_id,
            ):
                errors[CONF_INFRARED_ENTITY_ID] = "emitter_already_configured"
            else:
                if entry.unique_id is not None:
                    await self.async_set_unique_id(entry.unique_id)
                    self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    entry,
                    title=data[CONF_NAME],
                    data=data,
                    reload_even_if_entry_is_unchanged=False,
                )

        schema = self.add_suggested_values_to_schema(
            _config_schema(emitter_entity_ids),
            user_input or entry.data,
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )


def _config_schema(emitter_entity_ids: list[str]) -> vol.Schema:
    """Return the config flow schema."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(),
            vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                EntitySelectorConfig(
                    domain=infrared.DOMAIN,
                    include_entities=emitter_entity_ids,
                ),
            ),
            vol.Optional(CONF_TEMPERATURE_SENSOR): EntitySelector(
                EntitySelectorConfig(
                    filter={
                        "domain": "sensor",
                        "device_class": SensorDeviceClass.TEMPERATURE,
                    },
                ),
            ),
            vol.Optional(CONF_HUMIDITY_SENSOR): EntitySelector(
                EntitySelectorConfig(
                    filter={
                        "domain": "sensor",
                        "device_class": SensorDeviceClass.HUMIDITY,
                    },
                ),
            ),
            vol.Optional(CONF_POWER_SENSOR): EntitySelector(
                EntitySelectorConfig(domain="binary_sensor"),
            ),
        },
    )


def _data_from_user_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Normalize user input into config entry data."""
    data: dict[str, str] = {
        CONF_NAME: str(user_input[CONF_NAME]).strip(),
        CONF_INFRARED_ENTITY_ID: str(user_input[CONF_INFRARED_ENTITY_ID]),
    }
    data.update(
        {key: str(value) for key in OPTIONAL_ENTITY_CONFIG_KEYS if (value := user_input.get(key))},
    )
    return data


def _emitter_entity_ids_for_reconfigure(hass: Any, current_emitter_entity_id: str) -> list[str]:
    """Return selectable emitter entity IDs for reconfiguration."""
    emitter_entity_ids = infrared.async_get_emitters(hass)
    if current_emitter_entity_id in emitter_entity_ids:
        return emitter_entity_ids

    return [*emitter_entity_ids, current_emitter_entity_id]


def _emitter_entity_in_use(
    hass: Any,
    emitter_entity_id: str,
    *,
    current_entry_id: str | None = None,
) -> bool:
    """Return whether another config entry already uses an infrared emitter."""
    config_entries = getattr(hass, "config_entries", None)
    if config_entries is None:
        return False

    return any(
        (current_entry_id is None or entry.entry_id != current_entry_id)
        and entry.data.get(CONF_INFRARED_ENTITY_ID) == emitter_entity_id
        for entry in config_entries.async_entries(DOMAIN)
    )


def _unique_id_for_emitter(hass: Any, emitter_entity_id: str) -> str:
    """Return a stable unique ID for an emitter-backed ZH/JT-03 climate entity."""
    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(emitter_entity_id)
    if entry is not None and entry.unique_id is not None:
        return f"zh_jt_03_{entry.platform}_{entry.unique_id}"

    return f"zh_jt_03_{emitter_entity_id}"


__all__ = ["ClimateZHJT03ConfigFlowHandler"]
