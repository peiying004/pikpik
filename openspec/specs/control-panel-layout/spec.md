# control-panel-layout Specification

## Purpose

Placement and organisation of the map-overlay controls: a single panel on the left
that gathers every control except the joystick.

Covers the panel's four labelled sections and their contents, the joystick's
deliberate exclusion from the panel, collapsing and expanding, fitting the viewport
by scrolling internally rather than overflowing, and the invariant that gathering the
controls changes none of their behaviour.

This capability governs where controls live and how the panel behaves as a container.
The behaviour of the individual controls belongs to `auto-walk`,
`joystick-control`, and `device-location-sync`. One cross-capability guarantee is
recorded here because it would otherwise be lost: a device-write failure must stay
visible through the status bar while the panel is collapsed.

## Requirements

### Requirement: Controls are gathered into a single left-side panel

The system SHALL present a single control panel on the left side of the map, containing every map-overlay control except the joystick. The right side of the map SHALL NOT contain any speed control block.

The panel SHALL organise its contents into four labelled sections in this order: position, speed, multi-waypoint sequential walk, and single-destination road walk.

- The position section SHALL contain the set-GPS-location control and the centre-on-marker control.
- The speed section SHALL contain the automatic walk speed slider and the joystick speed slider, each with its label and its value display.
- The multi-waypoint sequential walk section SHALL contain the coordinate list input, the start-walk control, the coordinate error message, the walk progress display, and the device-write warning.
- The single-destination road walk section SHALL contain the walk-along-roads control and the stop-walk control.

#### Scenario: Panel presents four labelled sections in order

- **WHEN** the user loads the simulator page
- **THEN** a single control panel appears on the left side
- **AND** it shows labelled sections in the order position, speed, multi-waypoint sequential walk, single-destination road walk

#### Scenario: No controls remain on the right side except the joystick

- **WHEN** the user loads the simulator page
- **THEN** no speed control block appears on the right side of the map
- **AND** the joystick remains the only control on the right side

---
### Requirement: Joystick stays outside the panel

The joystick SHALL remain in the lower-right corner outside the control panel, retaining the size, position, and CSS class name it had before the controls were gathered into the panel.

#### Scenario: Joystick position and identity are unchanged

- **WHEN** the user loads the simulator page
- **THEN** the joystick appears in the lower-right corner
- **AND** its container keeps the same CSS class name, width, height, and distance from the viewport edges as before this change

---
### Requirement: Panel can be collapsed and expanded

The panel SHALL provide a control that collapses and expands it. While collapsed, the panel's header SHALL remain visible so the panel can be expanded again, and the panel's contents SHALL remain present in the document so that scripted access to them continues to succeed.

Collapse state SHALL NOT persist across page loads: the panel SHALL be expanded when the page loads.

#### Scenario: Collapsing hides the contents but keeps the header

- **WHEN** the user activates the collapse control
- **THEN** the panel contents are hidden from view
- **AND** the panel header remains visible

#### Scenario: Expanding restores the contents

- **WHEN** the panel is collapsed
- **AND** the user activates the expand control
- **THEN** the panel contents are shown again in full

#### Scenario: Collapsed panel keeps its elements accessible to scripts

- **WHEN** the panel is collapsed
- **AND** a multi-waypoint walk is started and runs
- **THEN** the walk proceeds normally
- **AND** the walk progress display holds the current coordinate index
- **AND** no error caused by a missing element occurs

#### Scenario: Panel is expanded after a page load

- **WHEN** the user collapses the panel and then reloads the page
- **THEN** the panel is expanded

---
### Requirement: Device-write failure stays visible while the panel is collapsed

While a walk is running and the panel is collapsed, a device-write failure SHALL remain visible to the user outside the panel through the status bar, which SHALL indicate the failure rather than continuing to present the device as being written to successfully.

#### Scenario: Failure is visible with the panel collapsed

- **WHEN** a walk is running
- **AND** the panel is collapsed
- **AND** device writes are failing
- **THEN** the status bar indicates that device writes are failing

---
### Requirement: Panel fits the viewport and scrolls internally

The panel's height SHALL NOT exceed the viewport height available between the top bar and the status bar. When the panel's contents exceed that height, the panel SHALL scroll internally rather than overflow the viewport, clip its contents, or hide any section.

The panel SHALL NOT overlap the status bar or the joystick at any viewport height.

#### Scenario: Short viewport scrolls inside the panel

- **WHEN** the viewport height is reduced to about 600 pixels
- **THEN** the panel does not extend beyond the viewport
- **AND** the panel scrolls internally
- **AND** the controls in the lowest section can be scrolled to and operated

#### Scenario: Panel does not overlap other overlays

- **WHEN** the user loads the simulator page at any viewport height
- **THEN** the panel does not overlap the status bar
- **AND** the panel does not overlap the joystick

---
### Requirement: Gathering the controls preserves their behaviour

Relocating the controls into the panel SHALL NOT change the behaviour, parameters, or request payload of any control. Every element that the page script accesses by identifier SHALL continue to resolve after the reorganisation, and the initialization that populates the speed labels and the coordinate readout SHALL continue to run before any third-party library is initialized.

#### Scenario: Every scripted element identifier still resolves

- **WHEN** the set of element identifiers declared in the page markup is compared against the set of identifiers the page script accesses
- **THEN** every identifier the script accesses is declared in the markup

#### Scenario: Controls behave as before

- **WHEN** the user operates the set-GPS-location control, the centre-on-marker control, the two speed sliders, the coordinate list input with the start-walk control, the stop-walk control, and the walk-along-roads control
- **THEN** each behaves as it did before the controls were gathered into the panel

#### Scenario: Coordinate parsing is unaffected

- **WHEN** the coordinate list input receives the inputs covered by the auto-walk coordinate parsing cases
- **THEN** the acceptance and rejection results are unchanged by the reorganisation

#### Scenario: Initialization order is preserved

- **WHEN** the page script runs
- **THEN** the speed labels and the coordinate readout are populated before any third-party library is initialized
