"""Constants for Climate for IR Devices using ZH/JT-03 Remote."""

from homeassistant.components.climate.const import FAN_AUTO, FAN_HIGH, FAN_LOW, FAN_MEDIUM, HVACMode
from homeassistant.const import Platform

DOMAIN = "climate_ir_zhjt03"
TITLE = "Climate for IR Devices using ZH/JT-03 Remote"

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_POWER_SENSOR = "power_sensor"

DEFAULT_NAME = "ZH/JT-03 AC"
DEFAULT_TEMPERATURE = 24
DEFAULT_FAN_MODE = FAN_AUTO
DEFAULT_HVAC_MODE = HVACMode.AUTO

MANUFACTURER = "Chigo"
MODEL = "ZH/JT-03"

MIN_TEMPERATURE = 16
MAX_TEMPERATURE = 32

SWING_OFF = "off"
SWING_FAST = "fast"
SWING_SLOW = "slow"

SUPPORTED_HVAC_MODES: list[HVACMode] = [
    HVACMode.OFF,
    HVACMode.AUTO,
    HVACMode.COOL,
    HVACMode.HEAT,
    HVACMode.FAN_ONLY,
    HVACMode.DRY,
]
SUPPORTED_FAN_MODES: list[str] = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
SUPPORTED_SWING_MODES: list[str] = [SWING_OFF, SWING_FAST, SWING_SLOW]

PLATFORMS: list[Platform] = [Platform.CLIMATE]
