# Design Decisions

This file records architecture decisions that affect maintainability or user-visible behavior.

## Decision Log

### Use Home Assistant's Infrared Integration

**Date:** 2026-05-27

**Context:** The integration needs to send IR commands but should not own transmitter hardware support.

**Decision:** Depend on Home Assistant's `infrared` integration and send commands with `async_send_command`.

**Rationale:**

- Keeps transmitter discovery, device support, and transport details in the infrared integration.
- Allows this integration to focus on ZH/JT-03 climate behavior and protocol encoding.
- Avoids adding device-specific transmitter dependencies.

**Consequences:**

- Setup requires an existing `infrared` emitter entity.
- Climate availability follows the selected transmitter entity.
- Troubleshooting sometimes requires checking the transmitter integration logs too.

### Model the AC as an Assumed-State Climate Entity

**Date:** 2026-05-27

**Context:** Typical IR AC remotes send one-way commands and do not receive state from the AC.

**Decision:** Expose a Home Assistant `climate` entity with `_attr_assumed_state = True`.

**Rationale:**

- Matches the physical limitations of IR control.
- Gives users the expected climate card and service APIs.
- Avoids pretending the integration can verify command delivery.

**Consequences:**

- Home Assistant state updates immediately after a command is sent.
- Users may need optional feedback sensors to improve displayed state.
- Automations should be written with the assumption that IR commands can be missed.

### Configure One Climate Entity per IR Transmitter

**Date:** 2026-05-27

**Context:** A configured entry binds one ZH/JT-03 AC abstraction to one transmitter entity.

**Decision:** Derive the config-entry unique ID from the selected transmitter and reject duplicates.

**Rationale:**

- Prevents accidental duplicate climate entities sending conflicting commands through the same transmitter.
- Keeps setup simple and predictable.
- Preserves stable entity IDs when the transmitter has a stable registry unique ID.

**Consequences:**

- A single transmitter can only be configured once for this integration.
- Users need separate transmitter entities for separate AC units.

### Keep Protocol Encoding Local

**Date:** 2026-05-27

**Context:** The ZH/JT-03 command format is small and deterministic.

**Decision:** Encode frames in `protocol.py` instead of depending on a remote API or large third-party climate library.

**Rationale:**

- The behavior is easy to test with fixed timings.
- There is no network I/O and no polling lifecycle.
- The integration remains small and transparent.

**Consequences:**

- Protocol changes require code changes and tests.
- Support for additional remotes should be added as separate protocol code, not mixed into the current encoder.

### Use Optional Existing Sensors for Feedback

**Date:** 2026-05-27

**Context:** Some Home Assistant installations already have room sensors or power monitoring.

**Decision:** Let users select optional temperature, humidity, and power entities during setup.

**Rationale:**

- Improves climate card state without forcing extra entities or dependencies.
- Keeps the IR control path independent from sensor availability.
- Lets users choose the most accurate sensors for their room.

**Consequences:**

- Feedback sensors are not required for command sending.
- Bad sensor values are ignored rather than making the climate entity unavailable.
- Changing selected sensors currently requires removing and re-adding the integration unless a future reconfigure flow is
  added.

### Do Not Use a DataUpdateCoordinator

**Date:** 2026-05-27

**Context:** The integration sends commands and listens to selected entity state changes. It does not poll shared remote
data.

**Decision:** Do not add a `DataUpdateCoordinator` until there is a real polling or shared-data need.

**Rationale:**

- Avoids unnecessary lifecycle complexity.
- The climate entity can subscribe directly to the few Home Assistant entities it needs.
- The infrared command path is command-driven, not poll-driven.

**Consequences:**

- Future polling features must introduce a coordinator deliberately.
- Agent instructions and docs should not assume coordinator/API packages exist in this repository.

## Future Considerations

- Add a reconfigure flow for changing optional sensors without deleting the entry.
- Add more protocols only if they can be isolated cleanly.
- Consider repairs if common setup mistakes become detectable.
- Document known compatible AC models as users report validated hardware.
