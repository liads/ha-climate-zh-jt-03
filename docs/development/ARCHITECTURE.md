# Architecture

This document describes the current implementation of **Climate for IR Devices using ZH/JT-03 Remote**.

## Scope

The integration exposes one Home Assistant `climate` entity per config entry. It does not poll an external API and does
not maintain a data coordinator. Commands are encoded locally and sent through Home Assistant's `infrared` integration.

## Runtime Structure

```text
custom_components/climate_ir_zhjt03/
|-- __init__.py
|-- compat.py
|-- config_flow.py
|-- config_flow_handler/
|   |-- __init__.py
|   `-- config_flow.py
|-- const.py
|-- diagnostics.py
|-- manifest.json
|-- protocol.py
|-- climate/
|   |-- __init__.py
|   `-- zh_jt_03.py
`-- translations/
    `-- en.json
```

## Components

### Integration Setup

`__init__.py` declares config-entry-only setup and forwards entries to the climate platform.

The integration currently loads only `Platform.CLIMATE`.

### Config Flow

`config_flow.py` exports the handler from `config_flow_handler/config_flow.py`.

The user step:

- requires at least one Home Assistant `infrared` emitter entity,
- asks for a friendly name,
- asks for the infrared transmitter entity,
- optionally accepts temperature, humidity, and power feedback sensors,
- prevents configuring the same transmitter more than once.

Unique IDs are based on the selected transmitter's entity-registry unique ID when available. If the transmitter has no
registry entry, the entity ID is used as the fallback.

### Climate Entity

`climate/zh_jt_03.py` implements `ClimateZHJT03`.

Responsibilities:

- expose Home Assistant climate capabilities,
- restore the previous state after restart,
- track transmitter availability,
- listen to optional feedback sensors,
- validate climate values before commands are sent,
- build a `ZhJt03Command` and send it through `homeassistant.components.infrared.async_send_command`.

The entity is assumed-state because the IR protocol is one-way.

### Protocol Encoder

`protocol.py` contains the ZH/JT-03 frame encoder.

It maps Home Assistant climate values to protocol values, builds the 48-bit payload, applies the per-byte inverted frame
layout, and returns raw timings for the infrared integration.

Supported protocol values:

| Home Assistant value                      | Protocol area      |
| ----------------------------------------- | ------------------ |
| `auto`, `cool`, `dry`, `fan_only`, `heat` | HVAC mode          |
| `off`, non-off modes                      | Power bit          |
| `auto`, `low`, `medium`, `high`           | Fan                |
| `off`, `fast`, `slow`                     | Swing              |
| 16-32 C                                   | Target temperature |

### Compatibility Layer

`compat.py` imports the infrared command base class from either `infrared_protocols` or
`infrared_protocols.commands`. This keeps the integration compatible with package layout differences across
`infrared-protocols` versions.

### Diagnostics

`diagnostics.py` returns config-entry diagnostics and redacts the friendly name and configured entity IDs. These values
can reveal local room names or setup details.

## Data Flow

```text
Config flow
    |
    v
Config entry data
    |
    v
ClimateZHJT03 entity
    |
    +--> optional sensor listeners update current readings / assumed power
    |
    v
ZhJt03Command
    |
    v
infrared.async_send_command(...)
    |
    v
Configured IR transmitter entity
```

## State Model

- The entity starts unavailable until the transmitter entity is present and available.
- State is restored with `RestoreEntity`.
- `last_on_operation` tracks the last non-off HVAC mode.
- Off-state changes to temperature, fan mode, and swing mode are stored locally.
- Sending a non-off command sends mode, temperature, fan, and swing in the same encoded frame.

## Testing

Tests live in `tests/` and cover:

- config-flow schema and unique ID behavior,
- climate entity state coercion, restoration, sensor handling, and command application,
- protocol encoding and boundary validation.

Run tests through the project script:

```bash
script/test
```

## Agent Instruction Layout

The repository keeps agent instructions separate from user/developer documentation:

| File                                     | Purpose                                    |
| ---------------------------------------- | ------------------------------------------ |
| `AGENTS.md`                              | Primary instructions for AI coding agents. |
| `.github/copilot-instructions.md`        | Compact GitHub Copilot entry point.        |
| `CLAUDE.md` and `GEMINI.md`              | Pointers for other agent tools.            |
| `.github/instructions/*.instructions.md` | Path-specific style guidance.              |
| `.github/prompts/*.prompt.md`            | Optional prompt templates for maintainers. |

Some path-specific instruction files describe broader Home Assistant blueprint patterns, including coordinators and API
clients. Those patterns are optional here; the runtime architecture documented in this file is authoritative.

## Development Scripts

Use repository scripts rather than direct `pytest`, `hass`, or `pip` commands.

| Script              | Purpose                                                            |
| ------------------- | ------------------------------------------------------------------ |
| `script/develop`    | Start a local Home Assistant instance.                             |
| `script/markdown`   | Format and lint Markdown.                                          |
| `script/lint`       | Format and lint supported file types.                              |
| `script/type-check` | Run Pyright.                                                       |
| `script/test`       | Run tests.                                                         |
| `script/check`      | Run full validation.                                               |
| `script/hassfest`   | Validate integration metadata against Home Assistant expectations. |

## Extension Points

### Add Another IR Protocol

Keep protocol-specific encoding separate from the entity. Add a protocol module and choose the encoder from config data
only after the config flow and translations are updated.

### Add More Feedback

Prefer listening to existing Home Assistant entities when possible. If a new platform is needed, add it deliberately and
update `PLATFORMS`, docs, translations, and tests together.

### Add Services

There are currently no custom services. If a service is added, define it in `services.yaml`, register it from
`async_setup()`, and document the action in the user docs.

### Add an API or Coordinator

The current integration does not need a coordinator. Add one only if the integration starts polling a device or service
for shared data used by multiple entities.
