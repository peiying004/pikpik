## MODIFIED Requirements

### Requirement: Controls are gathered into a single left-side panel

In a wide viewport, the system SHALL present a single control panel on the left side of the map, containing every map-overlay control except the joystick. The right side of the map SHALL NOT contain any speed control block.

In a narrow viewport, the panel's position and dimensions are governed by `mobile-viewport-layout` instead. The requirement that the controls live in one panel, and that the right side carries no speed control block, SHALL hold at every viewport width.

The panel SHALL organise its contents into five labelled sections in this order: position, speed, multi-waypoint sequential walk, single-destination road walk, and connection diagnostics. This ordering SHALL hold at every viewport width.

- The position section SHALL contain the set-GPS-location control and the centre-on-marker control.
- The speed section SHALL contain the automatic walk speed slider and the joystick speed slider, each with its label and its value display.
- The multi-waypoint sequential walk section SHALL contain the coordinate list input, the start-walk control, the coordinate error message, the walk progress display, and the device-write warning.
- The single-destination road walk section SHALL contain the walk-along-roads control and the stop-walk control.
- The connection diagnostics section SHALL contain the diagnostics control and the diagnostics result area. Diagnostics is its own section rather than an addition to an existing one, because it belongs to none of the other four subjects.

#### Scenario: Panel presents five labelled sections in order

- **WHEN** the user loads the simulator page
- **THEN** a single control panel appears
- **AND** it shows labelled sections in the order position, speed, multi-waypoint sequential walk, single-destination road walk, connection diagnostics

#### Scenario: Panel appears on the left side in a wide viewport

- **WHEN** the user loads the simulator page in a wide viewport
- **THEN** the control panel appears on the left side of the map

#### Scenario: No controls remain on the right side except the joystick

- **WHEN** the user loads the simulator page in a wide viewport
- **THEN** no speed control block appears on the right side of the map
- **AND** the joystick remains the only control on the right side

#### Scenario: Section contents are unchanged in a narrow viewport

- **WHEN** the user loads the simulator page in a narrow viewport
- **THEN** the five labelled sections are present in the same order
- **AND** each section contains the same controls it contains in a wide viewport

---

### Requirement: Joystick stays outside the panel

The joystick SHALL remain outside the control panel at every viewport width, and SHALL retain the CSS class name it had before the controls were gathered into the panel.

In a wide viewport, the joystick SHALL remain in the lower-right corner, retaining the size, position, and distance from the viewport edges it had before the controls were gathered into the panel.

In a narrow viewport, the joystick's size and position are governed by `mobile-viewport-layout` instead, which reduces its size and places it above the panel so that the two do not overlap. The requirement that the joystick stays outside the panel SHALL still hold.

#### Scenario: Joystick position and identity are unchanged in a wide viewport

- **WHEN** the user loads the simulator page in a wide viewport
- **THEN** the joystick appears in the lower-right corner
- **AND** its container keeps the same CSS class name, width, height, and distance from the viewport edges as before this change

#### Scenario: Joystick keeps its class name in a narrow viewport

- **WHEN** the user loads the simulator page in a narrow viewport
- **THEN** the joystick container keeps the same CSS class name it has in a wide viewport
- **AND** the joystick is not a descendant of the control panel
