# Climate for IR Devices using ZH/JT-03 Remote

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

Home Assistant custom integration that exposes an air conditioner controlled by a ZH/JT-03 infrared remote as a
`climate` entity. It sends raw IR commands through Home Assistant's `infrared` integration and keeps an assumed state
inside Home Assistant.

## Features

- UI setup through Home Assistant's config flow.
- One climate entity per configured infrared transmitter.
- Command encoding for ZH/JT-03-compatible AC units.
- HVAC modes: off, auto, cool, heat, fan only, and dry.
- Target temperature range: 16-32 C in whole-degree steps.
- Fan modes: auto, low, medium, and high.
- Swing modes: off, fast, and slow.
- Optional temperature and humidity sensors for current readings.
- Optional binary power sensor to reconcile the assumed HVAC state.
- State restoration after Home Assistant restarts.
- Redacted diagnostics for config-entry troubleshooting.

## Requirements

- Home Assistant 2026.4.0 or newer.
- HACS 2.0.5 or newer for the recommended installation path.
- A configured Home Assistant `infrared` transmitter entity.
- An AC unit that responds to the ZH/JT-03 IR protocol.

This integration is `assumed_state`: most IR remotes do not receive feedback from the AC. Home Assistant assumes the
last command succeeded unless you provide optional feedback sensors.

## Known Compatibility

Brand names are not a guarantee. To check support, compare your original remote with `ZH/JT-03` /
`ZHJT03` replacement remotes or test whether your AC responds to this protocol.

**Reported or better-sourced compatibility:** Family, Pilot, Chigo, Ecox, ACSON, Goodweather. Sources include
[Dealema][dealema-zhjt03-family], [Smartclima][smartclima-chigo-zhjt03], [Ozremote][ozremote-chigo-zhjt03],
[Ecoxline][ecoxline-zhjt03], [Remote Control World][remote-control-world-acson-zhjt03], and
[IRremoteESP8266][irremote-supported-protocols] / [issue #697][irremote-goodweather-issue].

**Possible unverified compatibility from marketplace listings:** Mando, GE, Beko, Lennox, Soprano, Prime, Dantex,
Elekta, Teslas, SVAN. These claims come from marketplace remote listings, including
[Amazon.com][amazon-zhjt03-marketplace] and [AliExpress][aliexpress-zhjt03-marketplace], and may vary by AC model or
region.

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add `https://github.com/liads/ha-climate-zh-jt-03` as an **Integration** repository.
5. Download **Climate for IR Devices using ZH/JT-03 Remote**.
6. Restart Home Assistant.

You can also open the repository directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=liads&repository=ha-climate-zh-jt-03&category=integration)

### Manual

1. Download the latest release from the [releases page][releases].
2. Copy `custom_components/climate_ir_zhjt03/` into your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

## Setup

Before adding this integration, configure the infrared transmitter you want to use. The setup form only appears when at
least one Home Assistant `infrared` emitter entity is available.

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Climate for IR Devices using ZH/JT-03 Remote**.
4. Enter a name for the climate entity.
5. Select the infrared transmitter entity.
6. Optionally select:
   - a temperature sensor for current room temperature,
   - a humidity sensor for current room humidity,
   - a binary power sensor that is `on` when the AC is powered.
7. Submit the form.

You can also start the config flow from My Home Assistant:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=climate_ir_zhjt03)

## Created Entity

The integration creates a single climate entity for each config entry. The default entity name is based on the name you
enter during setup.

Supported controls:

| Control            | Values                                           |
| ------------------ | ------------------------------------------------ |
| HVAC mode          | `off`, `auto`, `cool`, `heat`, `fan_only`, `dry` |
| Target temperature | 16-32 C                                          |
| Fan mode           | `auto`, `low`, `medium`, `high`                  |
| Swing mode         | `off`, `fast`, `slow`                            |

When the climate entity is off, changing target temperature, fan mode, or swing mode updates Home Assistant's stored
state. The next turn-on command sends the complete state to the infrared transmitter.

## Optional Feedback Sensors

The integration can listen to existing Home Assistant entities:

- **Temperature sensor:** updates the climate entity's current temperature. Non-Celsius units are converted to Celsius
  when Home Assistant supports the unit.
- **Humidity sensor:** updates the climate entity's current humidity.
- **Power sensor:** if it turns `off`, the climate entity is marked off. If it turns `on` while the entity is off, the
  last non-off HVAC mode is restored.

These sensors are optional. They do not change how commands are sent; they only improve the displayed state.

## Troubleshooting

### No infrared transmitter found

The config flow aborts when Home Assistant has no `infrared` emitter entities. Set up the device or integration that
provides your IR transmitter first, then add this integration again.

### Climate entity is unavailable

The climate entity is available only while the configured infrared transmitter entity exists and is not unavailable.
Check the transmitter integration and Home Assistant logs.

### The AC does not respond

1. Confirm the transmitter can reach the AC.
2. Check that the AC model uses the ZH/JT-03 protocol.
3. Try a simple command such as setting cool mode to 24 C.
4. Enable debug logging and inspect `config/home-assistant.log`.

Debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.climate_ir_zhjt03: debug
```

## Documentation

- [Getting Started](docs/user/GETTING_STARTED.md)
- [Configuration Reference](docs/user/CONFIGURATION.md)
- [Examples](docs/user/EXAMPLES.md)
- [Architecture](docs/development/ARCHITECTURE.md)
- [Design Decisions](docs/development/DECISIONS.md)
- [Development Customization](docs/development/CUSTOMIZATION.md)
- [Release Management](docs/development/RELEASE.md)
- [Dependencies](DEPENDENCIES.md)

## Development

Use the project scripts; they manage the local environment for this repository.

```bash
script/develop        # Start Home Assistant at http://localhost:8123
script/markdown       # Format and lint Markdown
script/lint           # Format and lint supported file types
script/type-check     # Run Pyright
script/test           # Run tests
script/check          # Full validation
script/hassfest       # Home Assistant integration validation
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution details.

## AI-Assisted Development

This repository includes AI-agent instruction files and prompt templates. They are development aids, not runtime
requirements. If generated changes behave unexpectedly, please open an issue with logs and reproduction steps.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

**Made by [@liads][user_profile]**

[commits-shield]: https://img.shields.io/github/commit-activity/y/liads/ha-climate-zh-jt-03.svg?style=for-the-badge
[commits]: https://github.com/liads/ha-climate-zh-jt-03/commits/main
[aliexpress-zhjt03-marketplace]: https://www.aliexpress.com/item/1005004236929351.html
[amazon-zhjt03-marketplace]: https://www.amazon.com/Control-EVERWELL-CLIMATIC-Blomberg-Conditioner/dp/B0BF942YZX
[dealema-zhjt03-family]: https://dealema.co.il/product/%D7%A9%D7%9C%D7%98-%D7%A8%D7%97%D7%95%D7%A7-%D7%90%D7%95%D7%A0%D7%99%D7%91%D7%A8%D7%A1%D7%9C%D7%99-%D7%9C%D7%9E%D7%96%D7%92%D7%A0%D7%99%D7%9D-zh-jt-03-family/
[ecoxline-zhjt03]: https://ecoxline.com/en/ecox-split-air-conditioner-parts/remote-control-for-split-ecox-zhjt-03/205.html
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[irremote-goodweather-issue]: https://github.com/crankyoldgit/IRremoteESP8266/issues/697
[irremote-supported-protocols]: https://github.com/crankyoldgit/IRremoteESP8266/blob/master/SupportedProtocols.md
[license-shield]: https://img.shields.io/github/license/liads/ha-climate-zh-jt-03.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40liads-blue.svg?style=for-the-badge
[ozremote-chigo-zhjt03]: https://www.ozremote.com/products/zh-jt-03-remote-control-replacement-for-chigo-air-conditioner
[releases-shield]: https://img.shields.io/github/release/liads/ha-climate-zh-jt-03.svg?style=for-the-badge
[releases]: https://github.com/liads/ha-climate-zh-jt-03/releases
[remote-control-world-acson-zhjt03]: https://www.remote-control-world.eu/air-conditioning-c-261/acson-zhjt-03-replacement-remote-control-p-85177
[smartclima-chigo-zhjt03]: https://www.smartclima.com/chigo-air-conditioner-remote-controller-zh-jt-01-zh-jt-03.htm
[user_profile]: https://github.com/liads
