# control-panel-layout Specification

## Purpose

Placement and organisation of the map-overlay controls: one panel that gathers every
control except the joystick, placed on the left of the map in a wide viewport.

Covers the panel's five labelled sections and their contents, the joystick's
deliberate exclusion from the panel, collapsing and expanding, fitting the viewport
by scrolling internally rather than overflowing, and the invariant that gathering the
controls changes none of their behaviour.

Below the viewport-width breakpoint the panel's position and dimensions are governed by
`mobile-viewport-layout`; what stays true at every width is that the controls live in one
panel, that the panel carries five labelled sections in a fixed order, and that the joystick
is not one of them.

This capability governs where controls live and how the panel behaves as a container.
The behaviour of the individual controls belongs to `auto-walk`,
`joystick-control`, and `device-location-sync`. One cross-capability guarantee is
recorded here because it would otherwise be lost: a device-write failure must stay
visible through the status bar while the panel is collapsed.

## Requirements

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


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

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


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

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