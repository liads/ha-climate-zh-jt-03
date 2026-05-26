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
            name = user_input[CONF_NAME].strip()
            if not name:
                errors[CONF_NAME] = "name_required"
            else:
                emitter_entity_id = user_input[CONF_INFRARED_ENTITY_ID]
                await self.async_set_unique_id(
                    _unique_id_for_emitter(self.hass, emitter_entity_id),
                )
                self._abort_if_unique_id_configured()

                data = {
                    CONF_NAME: name,
                    CONF_INFRARED_ENTITY_ID: emitter_entity_id,
                }
                data.update(
                    {key: value for key, value in user_input.items() if key not in data and value},
                )

                return self.async_create_entry(
                    title=name,
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(emitter_entity_ids),
            errors=errors,
        )


def _user_schema(emitter_entity_ids: list[str]) -> vol.Schema:
    """Return the user step schema."""
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


def _unique_id_for_emitter(hass: Any, emitter_entity_id: str) -> str:
    """Return a stable unique ID for an emitter-backed ZH/JT-03 climate entity."""
    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(emitter_entity_id)
    if entry is not None and entry.unique_id is not None:
        return f"zh_jt_03_{entry.platform}_{entry.unique_id}"

    return f"zh_jt_03_{emitter_entity_id}"


__all__ = ["ClimateZHJT03ConfigFlowHandler"]
