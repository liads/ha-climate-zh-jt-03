# Contributing

Thanks for helping improve **Climate for IR Devices using ZH/JT-03 Remote**.

## How to Contribute

Use GitHub issues and pull requests for bugs, fixes, and feature proposals.

1. Fork the repository and create a branch from `main`.
2. Run `script/setup/bootstrap` to install dependencies and pre-commit hooks.
3. Make a focused change.
4. Update documentation when behavior changes.
5. Make sure your code passes all checks (using `script/check` for linting and type checking).
6. Test your contribution.
7. Open a pull request.

## Development Environment

Use the repository scripts rather than direct `hass`, `pip`, or `pytest` commands.

```bash
script/setup/bootstrap
script/develop
script/markdown
script/lint
script/type-check
script/test
script/check
script/hassfest
```

For docs-only changes, `script/markdown` is usually enough.

## Code Style

- Python: 4 spaces, double quotes, full type hints, 120 character line target.
- YAML: 2 spaces and modern Home Assistant syntax.
- JSON: 2 spaces, no comments, no trailing commas.
- Markdown: format and lint with `script/markdown`.

## Project Architecture

The current integration creates a single assumed-state `climate` entity backed by Home Assistant's `infrared`
integration.

Key files:

- `custom_components/climate_ir_zhjt03/climate/zh_jt_03.py`
- `custom_components/climate_ir_zhjt03/protocol.py`
- `custom_components/climate_ir_zhjt03/config_flow_handler/config_flow.py`
- `custom_components/climate_ir_zhjt03/diagnostics.py`

There is no API client, data coordinator, or custom service action layer today. Add those only when a feature genuinely
needs them.

## Bug Reports

Useful bug reports include:

- Home Assistant version.
- Integration version.
- Infrared transmitter integration and entity ID.
- AC model, if known.
- Steps to reproduce.
- Expected behavior and actual behavior.
- Relevant log lines from `config/home-assistant.log`.

Great bug reports also include a short summary, exact steps to reproduce, what you expected, what actually happened, and
anything you already tried. If an automation, script, or dashboard card is involved, include the smallest YAML snippet
that reproduces the issue.

## Pull Request Checks

Before opening a pull request, run the narrowest relevant checks:

| Change type          | Command                                 |
| -------------------- | --------------------------------------- |
| Markdown only        | `script/markdown`                       |
| Python only          | `script/python` and `script/type-check` |
| Tests relevant       | `script/test`                           |
| Integration metadata | `script/hassfest`                       |
| Broad changes        | `script/check`                          |

`script/hassfest` validates `manifest.json`, translations, integration structure, and Home Assistant metadata locally.
Use it after changing manifest fields, config flow, translations, diagnostics, or platform structure.

Fix-mode scripts print the errors they cannot fix. After running `script/lint`, only manually edit issues that remain in
the output. `script/type-check` has no auto-fix mode.

## Code Quality Expectations

This is a custom integration, but contributions should still follow Home Assistant Core-style quality where reasonable:

- typed Python,
- async-safe Home Assistant patterns,
- stable config-entry and entity identity,
- redacted diagnostics,
- no YAML setup for the integration,
- no direct hardware assumptions outside the infrared transmitter abstraction.

For this integration specifically, keep protocol behavior in `protocol.py`, climate behavior in
`climate/zh_jt_03.py`, and config-flow behavior in `config_flow_handler/config_flow.py`.

## GitHub Copilot Support

This project includes prompt files under `.github/prompts/` for common maintenance tasks. They are optional aids and may
describe broader blueprint patterns than this integration currently uses.

Useful prompts include:

- **Add Config Option**
- **Add Entity Platform**
- **Add Entity to Device**
- **Create ADR**
- **Create Implementation Plan**
- **Review Integration**
- **Update Translations**

Review generated code carefully and keep it aligned with the current architecture.

## Breaking Changes

Call out changes that affect:

- entity IDs or unique IDs,
- config-entry data,
- supported climate modes or state attributes,
- service signatures if services are added later,
- minimum Home Assistant or HACS versions.

## AI Agent Support

Agent instructions are in [AGENTS.md](AGENTS.md). GitHub Copilot also reads
[.github/copilot-instructions.md](.github/copilot-instructions.md).

Prompt files under `.github/prompts/` are development aids. Review generated code carefully, especially for accidental
coordinator/API scaffolding that does not match the current architecture.

## License

By contributing, you agree that your contribution is licensed under the MIT License.
