# Getting Started

This guide walks through installing and setting up **Climate for IR Devices using ZH/JT-03 Remote** in Home Assistant.

## Prerequisites

- Home Assistant 2026.4.0 or newer.
- HACS 2.0.5 or newer, unless you install manually.
- A Home Assistant `infrared` transmitter entity.
- An AC unit that responds to the ZH/JT-03 IR protocol.

The integration does not communicate with the AC directly. It builds ZH/JT-03 IR commands and sends them through the
infrared transmitter entity you select during setup.

## Install

### HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL: `https://github.com/liads/ha-climate-zh-jt-03`.
5. Select **Integration** as the category.
6. Download **Climate for IR Devices using ZH/JT-03 Remote**.
7. Restart Home Assistant.

### Manual

1. Download the latest release from the [releases page](https://github.com/liads/ha-climate-zh-jt-03/releases).
2. Copy `custom_components/climate_ir_zhjt03/` into your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

## Add the Integration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Climate for IR Devices using ZH/JT-03 Remote**.
4. Fill in the setup form:

| Field                | Required | Description                                                   |
| -------------------- | -------- | ------------------------------------------------------------- |
| Name                 | Yes      | Friendly name for the AC. The default is `ZH/JT-03 AC`.       |
| Infrared transmitter | Yes      | The Home Assistant `infrared` entity that sends commands.     |
| Temperature sensor   | No       | Existing temperature sensor used as current room temperature. |
| Humidity sensor      | No       | Existing humidity sensor used as current room humidity.       |
| Power sensor         | No       | Existing binary sensor that is `on` when the AC is powered.   |

The config flow aborts with **No infrared transmitter entities found** if no supported transmitter exists yet. Configure
your IR transmitter first, then retry.

## Verify Basic Control

After setup, Home Assistant creates one climate entity.

1. Open the climate entity.
2. Set HVAC mode to **Cool**.
3. Set the target temperature to **24 C**.
4. Choose a fan mode, such as **Auto**.
5. Confirm the transmitter sends a command and the AC responds.

The entity is assumed-state. Home Assistant updates its displayed state after sending the command, but the AC normally
does not report back whether the command was received.

## Optional Feedback Sensors

Feedback sensors can make the displayed state more useful:

- Use a room temperature sensor so the climate card shows current temperature.
- Use a humidity sensor so the climate card shows current humidity.
- Use a power sensor when another device can detect whether the AC is actually on.

If you skip these fields, the integration still works; only the corresponding current readings are absent.

## Next Steps

- See [Configuration Reference](./CONFIGURATION.md) for supported modes and behavior.
- See [Examples](./EXAMPLES.md) for dashboard and automation snippets.
- Report issues at [GitHub Issues](https://github.com/liads/ha-climate-zh-jt-03/issues).
