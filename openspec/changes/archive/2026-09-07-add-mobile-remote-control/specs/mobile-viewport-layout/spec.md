## ADDED Requirements

### Requirement: A narrow viewport is defined by a width breakpoint

The system SHALL treat a viewport whose width is at most 768 CSS pixels as a narrow viewport, and a viewport wider than that as a wide viewport. The narrow-viewport rules in this capability SHALL apply only to narrow viewports.

The breakpoint SHALL depend on viewport width alone. Viewport height SHALL NOT select between the two layouts, because a short-but-wide viewport is already covered by the control panel's existing requirement to fit the viewport and scroll internally.

#### Scenario: Layout switches at the breakpoint

- **WHEN** the viewport width is 375 CSS pixels
- **THEN** the narrow-viewport layout is in effect

#### Scenario: Wide viewport keeps the existing layout

- **WHEN** the viewport width is 1280 CSS pixels
- **THEN** the narrow-viewport layout is not in effect
- **AND** the control panel appears on the left side of the map

##### Example: layout selection by viewport width

| Viewport width | Layout in effect |
| -------------- | ---------------- |
| 375 CSS pixels | narrow |
| 430 CSS pixels | narrow |
| 768 CSS pixels | narrow |
| 769 CSS pixels | wide |
| 1280 CSS pixels | wide |

---

### Requirement: Control panel becomes a bottom sheet in a narrow viewport

In a narrow viewport, the control panel SHALL be positioned against the bottom of the viewport and SHALL span its full width, rather than appearing as a fixed-width overlay on the left side.

When expanded in a narrow viewport, the panel's height SHALL NOT exceed half the viewport height, and the panel SHALL scroll internally when its contents exceed that height rather than overflowing the viewport or hiding any section.

The panel SHALL retain all five labelled sections and their contents in a narrow viewport. No section SHALL be removed or moved out of the panel by the narrow-viewport layout.

#### Scenario: Panel spans the bottom of a narrow viewport

- **WHEN** the viewport width is 375 CSS pixels
- **THEN** the control panel is positioned against the bottom of the viewport
- **AND** the panel spans the full viewport width

#### Scenario: Expanded panel is bounded to half the viewport height

- **WHEN** the viewport width is 375 CSS pixels and the viewport height is 812 CSS pixels
- **AND** the panel is expanded
- **THEN** the panel height does not exceed 406 CSS pixels
- **AND** the panel scrolls internally
- **AND** the controls in the lowest section can be scrolled to and operated

#### Scenario: All five sections remain present in a narrow viewport

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the panel is expanded
- **THEN** the position, speed, multi-waypoint sequential walk, single-destination road walk, and connection diagnostics sections are all present in the panel

---

### Requirement: Control panel is collapsed by default in a narrow viewport

In a narrow viewport, the control panel SHALL be collapsed when the page loads, with its header row visible so that it can be expanded.

While collapsed in a narrow viewport, the panel's contents SHALL remain present in the document so that scripted access to them continues to succeed.

Collapse state SHALL NOT persist across page loads.

#### Scenario: Panel loads collapsed in a narrow viewport

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the user loads the simulator page
- **THEN** the control panel is collapsed
- **AND** the panel header row is visible

#### Scenario: Collapsed narrow panel keeps its elements accessible to scripts

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the panel is collapsed
- **AND** a multi-waypoint walk is started and runs
- **THEN** the walk proceeds normally
- **AND** the walk progress display holds the current coordinate index
- **AND** no error caused by a missing element occurs

---

### Requirement: Panel and joystick do not overlap in a narrow viewport

In a narrow viewport, the joystick SHALL be reduced in size and positioned above the control panel so that the bounding boxes of the joystick and the panel do not intersect, whether the panel is collapsed or expanded.

The joystick SHALL remain fully within the viewport in a narrow viewport, and SHALL NOT be clipped by the viewport edges or by the panel.

#### Scenario: No overlap with the panel collapsed

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the panel is collapsed
- **THEN** the bounding box of the joystick does not intersect the bounding box of the panel
- **AND** the joystick is fully within the viewport

#### Scenario: No overlap with the panel expanded

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the panel is expanded
- **THEN** the bounding box of the joystick does not intersect the bounding box of the panel
- **AND** the joystick is fully within the viewport

---

### Requirement: Map stays visible and operable in a narrow viewport

In a narrow viewport, the map SHALL remain visible and operable above the collapsed panel, so that a destination can be placed by interacting with the map without first collapsing or dismissing any control.

When the panel is expanded in a narrow viewport, the control panel SHALL NOT extend above the vertical midpoint of the viewport, and the map SHALL remain unobscured by the panel everywhere above that midpoint. The requirement is stated as a bound on the panel rather than as "the map fills the upper half", because the top bar occupies the top of the viewport at every width and is outside this capability's scope.

#### Scenario: Map is operable with the panel collapsed

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the panel is collapsed
- **THEN** the map is visible above the panel
- **AND** a map interaction that places a destination succeeds without collapsing or dismissing any control

#### Scenario: Expanded panel stays below the viewport midpoint

- **WHEN** the viewport width is 375 CSS pixels and the viewport height is 812 CSS pixels
- **AND** the panel is expanded
- **THEN** the top edge of the control panel is at or below 406 CSS pixels from the top of the viewport
- **AND** the map extends below 406 CSS pixels from the top of the viewport

---

### Requirement: Touch targets meet a minimum size in a narrow viewport

In a narrow viewport, every control the user activates by touch SHALL present a touch target of at least 44 CSS pixels in both width and height. This SHALL apply to the buttons in every panel section, the panel collapse control, the diagnostics control, the search control, and the stop control.

A range slider SHALL present a thumb whose touch target is at least 44 CSS pixels in height.

#### Scenario: Panel buttons meet the minimum touch target

- **WHEN** the viewport width is 375 CSS pixels
- **THEN** each button in the panel sections presents a touch target of at least 44 CSS pixels in width and height

#### Scenario: Collapse and diagnostics controls meet the minimum touch target

- **WHEN** the viewport width is 375 CSS pixels
- **THEN** the panel collapse control presents a touch target of at least 44 CSS pixels in width and height
- **AND** the diagnostics control presents a touch target of at least 44 CSS pixels in width and height

#### Scenario: Speed slider thumbs meet the minimum touch target

- **WHEN** the viewport width is 375 CSS pixels
- **THEN** each speed slider presents a thumb touch target of at least 44 CSS pixels in height

---

### Requirement: The narrow-viewport layout preserves control behaviour

Applying the narrow-viewport layout SHALL NOT change the behaviour, parameters, or request payload of any control. Every element that the page script accesses by identifier SHALL continue to resolve, and the initialization that populates the speed labels and the coordinate readout SHALL continue to run before any third-party library is initialized.

The narrow-viewport layout SHALL be expressed through viewport-width-conditional style rules. It SHALL NOT be implemented by serving different markup for narrow and wide viewports, because divergent markup would let the two layouts drift apart in which elements exist.

#### Scenario: Every scripted element identifier still resolves

- **WHEN** the set of element identifiers declared in the page markup is compared against the set of identifiers the page script accesses
- **THEN** every identifier the script accesses is declared in the markup

#### Scenario: Markup is identical across the two layouts

- **WHEN** the page is served
- **THEN** the same markup is served regardless of viewport width
- **AND** the layout differs only through viewport-width-conditional style rules

#### Scenario: Controls behave as before in a narrow viewport

- **WHEN** the viewport width is 375 CSS pixels
- **AND** the user operates the set-GPS-location control, the centre-on-marker control, the two speed sliders, the coordinate list input with the start-walk control, the stop-walk control, and the walk-along-roads control
- **THEN** each behaves as it does in a wide viewport
