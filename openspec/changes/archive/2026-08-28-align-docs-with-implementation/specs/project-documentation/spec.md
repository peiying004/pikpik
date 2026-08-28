## ADDED Requirements

### Requirement: Documentation covers every implemented feature

The project documentation under the docs directory SHALL describe every feature the implementation provides. Coverage SHALL be mechanically verifiable: each feature is assigned one anchor term, and the documentation SHALL contain at least one occurrence of every anchor term.

An anchor term SHALL be an identifier taken from the source code (a function name, constant name, state field, or endpoint path) whenever a suitable one exists, because such a term appears in the documentation only where that feature is being described. Where no suitable identifier exists, the feature's name SHALL be used as the anchor.

#### Scenario: Every anchor term is present

- **WHEN** the documentation is searched for each anchor term in the coverage table
- **THEN** every anchor term occurs at least once

#### Scenario: A missing anchor names the uncovered feature

- **WHEN** an anchor term occurs zero times
- **THEN** that feature is treated as not covered
- **AND** the anchor term identifies which feature is missing without further investigation

##### Example: feature coverage table

| Feature                                       | Anchor term                |
| --------------------------------------------- | -------------------------- |
| Persistent device connection and reconnection | `_connect`                 |
| Async event loop bridge                       | `_run_async`               |
| Device write mutual exclusion                 | `_device_lock`             |
| Device write timeout bound                    | `_DEVICE_WRITE_TIMEOUT`    |
| Single-point location endpoint                | `/api/location`            |
| Stop and clear the simulated location          | `/api/stop`                |
| Walk interpolation worker                     | `_walk_worker`             |
| Haversine distance calculation                | `_haversine`               |
| Route first-coordinate write                  | 起點寫入                    |
| Route final-coordinate write                  | 終點補寫                    |
| Overlapping write dropping                    | `_walk_write_inflight`     |
| Write completion callback                     | `_on_walk_write_done`      |
| Three-state device write outcome              | `device_ok`                |
| Walk generation identification                | 代次                        |
| Route and speed validation                    | `_parse_walk_request`      |
| Walk endpoints                                | `/api/walk/status`         |
| Default walk speed                            | 18 km/h                    |
| Destination marker set by map click           | 綠色目的地                  |
| Map library failure guard                     | `showMapUnavailable`       |
| Disabling map-dependent controls              | 停用相依控制項              |
| Joystick library failure guard                | `showJoystickUnavailable`  |
| Continuous joystick movement                  | `moveByJoystick`           |
| Gesture propagation blocking                  | 手勢傳播                    |
| Search result rendering and escaping          | `makeResultItem`           |
| Location send throttling                      | `_flushLocation`           |
| Unified control panel and collapsing          | 控制面板                    |
| Multi-waypoint sequential walk                | 多座標依序移動              |
| Coordinate list parsing                       | `parseCoordInput`          |
| Walk polling and teardown split               | `startWalkPolling`         |
| Document-only initialization ordering         | 只依賴 DOM 的初始化         |

---

### Requirement: Documentation states nothing that contradicts the implementation

The documentation SHALL NOT contain statements that the implementation contradicts. Statements known to have been wrong SHALL be prevented from reappearing by a set of terms that SHALL NOT occur anywhere in the documentation.

#### Scenario: Forbidden terms are absent

- **WHEN** the documentation is searched for each term in the forbidden table
- **THEN** every one of them occurs zero times

##### Example: forbidden term table

| Forbidden term | Why it is wrong                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------ |
| `timezonefinder` | Removed from the dependency list; naming it sends readers to install a package nothing uses      |
| 射後不理        | Walk writes carry a completion callback that retrieves the outcome, which is the opposite of fire-and-forget |
| 逾時 15 秒      | The timeout is defined by a named constant; restating the literal duration makes the text lie when the constant changes |

---

### Requirement: Documentation embeds only stable code excerpts

The documentation SHALL NOT embed a code excerpt longer than fifteen lines. An embedded excerpt SHALL be limited to code that expresses a concept which does not change as features evolve.

Behaviour that changes as features evolve SHALL be described by naming the responsible function and stating what it is responsible for, rather than by reproducing its body.

#### Scenario: No long excerpt remains

- **WHEN** the documentation is inspected for embedded code blocks
- **THEN** no block exceeds fifteen lines

#### Scenario: Volatile behaviour is named rather than reproduced

- **WHEN** the documentation describes the walk worker, the device location write, the map or joystick initialization, the search result rendering, or the walk polling
- **THEN** it names the responsible functions and states their responsibilities
- **AND** it does not reproduce their bodies

---

### Requirement: Architecture documentation shows both walk paths

The architecture documentation SHALL contain a data-flow diagram for the multi-waypoint sequential walk that is separate from the single-destination road walk diagram. The multi-waypoint diagram SHALL NOT include an external routing service as a participant, because that path takes coordinates directly from user input and never contacts one.

The layered architecture SHALL list the control panel and the multi-waypoint sequential walk in the presentation layer. The key design decisions table SHALL record the six decisions established by the three most recent changes.

#### Scenario: The multi-waypoint path has its own diagram

- **WHEN** the architecture documentation is read
- **THEN** a data-flow diagram for the multi-waypoint sequential walk is present
- **AND** it lists no external routing service among its participants

#### Scenario: Recent design decisions are recorded

- **WHEN** the key design decisions table is read
- **THEN** it records dropping overlapping writes rather than queueing them
- **AND** it records the route endpoints being named exceptions to that dropping rule
- **AND** it records the write completion callback identifying its walk by generation
- **AND** it records the three-state device write outcome
- **AND** it records third-party library failure having to be visible on the page
- **AND** it records walk input validation preceding the start of the worker
