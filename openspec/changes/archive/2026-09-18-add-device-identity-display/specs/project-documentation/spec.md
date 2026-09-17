## MODIFIED Requirements

### Requirement: Documentation covers every implemented feature

The project documentation under the docs directory SHALL describe every feature the implementation provides. Coverage SHALL be mechanically verifiable: each feature is assigned one anchor term, and the documentation SHALL contain at least one occurrence of every anchor term.

An anchor term SHALL be an identifier taken from the source code (a function name, constant name, state field, or endpoint path) whenever a suitable one exists, because such a term appears in the documentation only where that feature is being described. Where no suitable identifier exists, the feature's name SHALL be used as the anchor.

When a change adds a feature, it SHALL add that feature to the coverage table in the same change. A feature that ships without an anchor term is indistinguishable from a feature that was never built, and the mechanical check cannot report what it was never told to look for.

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
| Layered connection diagnostics endpoint       | `/api/diagnostics`         |
| Four ordered stages with per-stage next action | `_DIAG_STAGE_META`        |
| Three-state stage outcome                     | `_DIAG_NOT_RUN`            |
| Diagnostics reusing the shared connection     | `_diag_probe_connection`   |
| Tunnel and developer service judged separately | `_acquire_rsd`            |
| Server address reported for phone access      | `_default_route_address`   |
| Narrow-viewport bottom sheet                  | `--status-bar-h`           |
| Minimum touch target size                     | 44 CSS 像素                 |
| Home screen install manifest                  | `manifest.webmanifest`     |
| Icon generation without added dependencies    | `make_icons.py`            |
| Connected device identity query               | `/api/device`              |
| Device identity in the status bar             | `renderDeviceStatus`       |
| Model names for every listed device           | `_device_models`           |
| Identity poll kept out of the access log      | `_mute_poll_access_log`    |
| Route length and duration preview             | `updateRoutePreview`       |
| Remaining time while a walk runs              | `remainingMeters`          |
