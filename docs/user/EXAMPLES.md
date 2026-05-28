# Examples

These examples assume your climate entity is `climate.zh_jt_03_ac`. Replace it with your actual entity ID.

## Dashboard Cards

### Thermostat Card

```yaml
type: thermostat
entity: climate.zh_jt_03_ac
features:
  - type: climate-hvac-modes
    hvac_modes:
      - "off"
      - auto
      - cool
      - heat
      - fan_only
      - dry
```

### Entities Card

```yaml
type: entities
title: Bedroom AC
entities:
  - entity: climate.zh_jt_03_ac
    name: AC
  - entity: sensor.bedroom_temperature
    name: Room temperature
  - entity: sensor.bedroom_humidity
    name: Room humidity
```

## Automations

### Start Cooling When the Room Is Hot

```yaml
automation:
  - alias: "Bedroom AC cool when hot"
    trigger:
      - trigger: numeric_state
        entity_id: sensor.bedroom_temperature
        above: 27
        for:
          minutes: 10
    condition:
      - condition: state
        entity_id: binary_sensor.bedroom_window
        state: "off"
    action:
      - action: climate.set_temperature
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          hvac_mode: cool
          temperature: 24
      - action: climate.set_fan_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          fan_mode: auto
```

### Turn Off When a Window Opens

```yaml
automation:
  - alias: "Bedroom AC off when window opens"
    trigger:
      - trigger: state
        entity_id: binary_sensor.bedroom_window
        to: "on"
        for:
          minutes: 2
    action:
      - action: climate.turn_off
        target:
          entity_id: climate.zh_jt_03_ac
```

### Dry Mode During High Humidity

```yaml
automation:
  - alias: "Bedroom AC dry mode on high humidity"
    trigger:
      - trigger: numeric_state
        entity_id: sensor.bedroom_humidity
        above: 65
        for:
          minutes: 15
    action:
      - action: climate.set_hvac_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          hvac_mode: dry
```

### Restore Comfort Mode in the Evening

```yaml
automation:
  - alias: "Bedroom AC evening comfort"
    trigger:
      - trigger: time
        at: "21:30:00"
    action:
      - action: climate.set_temperature
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          hvac_mode: cool
          temperature: 25
      - action: climate.set_fan_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          fan_mode: low
      - action: climate.set_swing_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          swing_mode: slow
```

## Script

### Send a Known Good Cooling Command

```yaml
script:
  zh_jt_03_cool_24:
    alias: "ZH/JT-03 cool 24"
    sequence:
      - action: climate.set_temperature
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          hvac_mode: cool
          temperature: 24
      - action: climate.set_fan_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          fan_mode: auto
      - action: climate.set_swing_mode
        target:
          entity_id: climate.zh_jt_03_ac
        data:
          swing_mode: "off"
```

## Related Documentation

- [Configuration Reference](./CONFIGURATION.md)
- [Getting Started](./GETTING_STARTED.md)
- [GitHub Issues](https://github.com/liads/ha-climate-zh-jt-03/issues)
