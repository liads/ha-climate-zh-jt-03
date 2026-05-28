# Configuration Reference

This page describes the configuration options and runtime behavior of **Climate for IR Devices using ZH/JT-03 Remote**.

## Setup Fields

Configuration is done through Home Assistant's UI config flow. YAML setup is not supported.

| Field                | Required | Stored key           | Description                                                    |
| -------------------- | -------- | -------------------- | -------------------------------------------------------------- |
| Name                 | Yes      | `name`               | Friendly name used for the config entry and device.            |
| Infrared transmitter | Yes      | `infrared_entity_id` | Home Assistant `infrared` entity that sends raw commands.      |
| Temperature sensor   | No       | `temperature_sensor` | Existing temperature sensor used for `current_temperature`.    |
| Humidity sensor      | No       | `humidity_sensor`    | Existing humidity sensor used for `current_humidity`.          |
| Power sensor         | No       | `power_sensor`       | Existing binary sensor used to reconcile assumed on/off state. |

Each infrared transmitter can be configured only once. The unique ID is derived from the transmitter's entity-registry
unique ID when available, otherwise from its entity ID.

## Climate Capabilities

The integration creates one climate entity per config entry.

| Capability         | Values                                           |
| ------------------ | ------------------------------------------------ |
| HVAC modes         | `off`, `auto`, `cool`, `heat`, `fan_only`, `dry` |
| Target temperature | 16-32 C                                          |
| Temperature step   | 1 C                                              |
| Fan modes          | `auto`, `low`, `medium`, `high`                  |
| Swing modes        | `off`, `fast`, `slow`                            |

The climate entity supports Home Assistant's turn on, turn off, target temperature, fan mode, and swing mode features.

## Assumed State Behavior

IR control is one-way, so the entity is marked as assumed-state.

- Sending a command updates Home Assistant's state immediately.
- The integration restores the previous climate state after Home Assistant restarts.
- The entity remembers the last non-off HVAC mode and uses it for turn-on.
- If the entity is off, changing target temperature, fan mode, or swing mode stores the value without sending a command.
- The next non-off HVAC command sends the full mode, temperature, fan, and swing state.

## Availability

The climate entity is available when the configured infrared transmitter entity exists and is not `unavailable`.

If the transmitter becomes unavailable, the climate entity becomes unavailable too. It returns to available when the
transmitter returns.

## Optional Sensor Handling

### Temperature Sensor

The integration reads the selected sensor state as a number. Celsius values are used directly. Other temperature units
are converted to Celsius when Home Assistant supports the unit.

Unknown, unavailable, non-numeric, and non-finite values are ignored.

### Humidity Sensor

The integration reads the selected sensor state as a number and exposes it as current humidity.

Unknown, unavailable, non-numeric, and non-finite values are ignored.

### Power Sensor

The optional power sensor is expected to be a binary sensor:

- `off`: the climate entity is set to HVAC off.
- `on`: if the climate entity is currently off, the last non-off HVAC mode is restored.

The power sensor does not send commands. It only adjusts Home Assistant's assumed state.

## Diagnostics

Diagnostics are available from **Settings** > **Devices & Services** > this integration > three-dot menu > **Download
diagnostics**.

The diagnostics payload includes the config entry ID, unique ID, options, and redacted config-entry data. Entity IDs and
the friendly name are redacted because they can reveal room names or local setup details.

## Debug Logging

Add this to `configuration.yaml`, then restart Home Assistant:

```yaml
logger:
  default: info
  logs:
    custom_components.climate_ir_zhjt03: debug
```

Useful log events include invalid restored values, ignored sensor states, unsupported units, transmitter availability
changes, and unsupported climate values.

## Troubleshooting

### Setup Form Does Not Open

The integration requires at least one `infrared` emitter entity. Set up your IR transmitter integration first.

### Entity Is Unavailable

Check the configured infrared transmitter. The climate entity follows the transmitter's availability.

### AC Does Not Respond

1. Verify the transmitter can physically reach the AC.
2. Confirm the AC uses the ZH/JT-03 protocol.
3. Try `cool`, `24 C`, fan `auto`, swing `off`.
4. Check Home Assistant logs for errors from the transmitter integration.

### Current Temperature or Humidity Is Missing

Confirm the optional sensor entity still exists and has a numeric state. For temperature, check that the unit is a Home
Assistant-supported temperature unit.

## Related Documentation

- [Getting Started](./GETTING_STARTED.md)
- [Examples](./EXAMPLES.md)
- [GitHub Issues](https://github.com/liads/ha-climate-zh-jt-03/issues)
