# page-initialization Specification

## Purpose

Front-end startup ordering and the containment of third-party library failures.

Covers running document-only initialization — populating the coordinate readout and
the speed labels from their controls — before any third-party library is initialized,
keeping library-independent event bindings functional when a library fails to load,
and surfacing a library load failure instead of failing silently.

A thrown error in a top-level statement stops every top-level statement after it, so
initialization order determines what survives a library failure. This capability
exists because a single unreachable library reference once disabled the speed labels,
the coordinate readout, and the search key binding at the same time, with no visible
indication of the cause.

## Requirements

### Requirement: DOM-only initialization precedes library-dependent initialization

Initialization that depends only on the document — populating the coordinate readout and the speed labels from their controls — SHALL run before any third-party library is initialized. A third-party library failure SHALL NOT leave these values unpopulated.

#### Scenario: Readouts are populated on a fresh page load

- **WHEN** the user loads the simulator page and performs no interaction
- **THEN** the coordinate readout shows numeric latitude and longitude rather than a placeholder
- **AND** the automatic walk speed label shows a speed value

##### Example: fresh load with the default slider position

- **GIVEN** the automatic walk speed slider's markup sets its value to 18
- **AND** the marker's initial coordinates are 25.033964, 121.564468
- **WHEN** the page finishes loading and the user has clicked nothing, dragged nothing, and started no walk
- **THEN** the automatic walk speed label reads "18 km/h"
- **AND** the coordinate readout reads 25.033964 and 121.564468

#### Scenario: A failing library does not blank the readouts

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the user loads the simulator page
- **THEN** the coordinate readout still shows numeric values
- **AND** the automatic walk speed label still shows a speed value

---
### Requirement: Library-independent event bindings survive a library failure

Event bindings that do not depend on a third-party library — performing a search when Enter is pressed in the search box, and dismissing the search result list when the user clicks outside it — SHALL remain functional when a third-party library fails to load.

#### Scenario: Enter key search works after a library failure

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the user types a query in the search box and presses Enter
- **THEN** the search is performed

#### Scenario: Search results dismiss on outside click after a library failure

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the search result list is open
- **AND** the user clicks outside the search box and the result list
- **THEN** the result list closes

---
### Requirement: Third-party library load failure is surfaced

When a third-party library that the page depends on fails to load, the system SHALL surface that failure to the user through visible page content naming the affected control. The system SHALL NOT fail silently, leaving the user to infer the cause from unrelated symptoms.

Each third-party library's availability SHALL be determined independently of every other third-party library. One library's failure SHALL NOT prevent another library's failure from being detected, and SHALL NOT prevent the other library's unavailability message from appearing.

#### Scenario: Failure is named rather than silent

- **WHEN** a third-party library that a control depends on fails to load
- **THEN** visible page content states that the affected control is unavailable
- **AND** the user is not left with only unrelated symptoms such as a blank value or an unresponsive key

#### Scenario: Map library failure does not suppress the joystick unavailability message

- **WHEN** the map library fails to load
- **AND** the joystick library also fails to load
- **THEN** visible page content states that the map is unavailable
- **AND** visible page content states that the joystick is unavailable

#### Scenario: Map library failure alone still reports the joystick as unavailable

- **WHEN** the map library fails to load
- **AND** the joystick library loads successfully
- **THEN** visible page content states that the map is unavailable
- **AND** visible page content states that the joystick is unavailable, because joystick movement operates on the map and the marker

##### Example: the four library availability combinations

| Map library | Joystick library | Map area                | Joystick container        |
| ----------- | ---------------- | ----------------------- | ------------------------- |
| loads       | loads            | interactive map         | working joystick          |
| loads       | fails            | interactive map         | "joystick unavailable"    |
| fails       | loads            | "map unavailable"       | "joystick unavailable"    |
| fails       | fails            | "map unavailable"       | "joystick unavailable"    |

---
### Requirement: Map library failure disables map-dependent controls and preserves document-only features

When the map library fails to load, the system SHALL display visible page content in the map area stating that the map, the marker, and movement are unavailable. The system SHALL skip every initialization step that depends on the map library instead of raising an uncaught error.

The system SHALL disable the controls whose behaviour operates on the map or the marker: set GPS location, centre on marker, start walk, stop walk, and walk along roads. A disabled control SHALL NOT issue a request and SHALL NOT raise a runtime error.

The coordinate readout, the speed labels, the Enter key search, and the outside-click dismissal of the search result list SHALL remain functional. Selecting a search result SHALL update the coordinate readout and SHALL skip the marker and map view updates.

#### Scenario: Map area names what is unavailable

- **WHEN** the map library fails to load
- **AND** the user loads the simulator page
- **THEN** the map area shows content stating that the map, the marker, and movement are unavailable
- **AND** no uncaught error is raised during page load

#### Scenario: Map-dependent controls are disabled rather than broken

- **WHEN** the map library fails to load
- **THEN** the set GPS location, centre on marker, start walk, stop walk, and walk along roads controls are disabled
- **AND** activating any of them issues no request and raises no runtime error

#### Scenario: Search still works without the map library

- **WHEN** the map library fails to load
- **AND** the user types a query in the search box and presses Enter
- **THEN** the search is performed and its results are listed
- **AND** selecting a result updates the coordinate readout
- **AND** selecting a result raises no runtime error

##### Example: selecting a search result without the map library

- **GIVEN** the map library failed to load
- **AND** the coordinate readout reads 25.033964 and 121.564468
- **WHEN** the user searches and selects a result whose coordinates are 25.047924, 121.517081
- **THEN** the coordinate readout reads 25.047924 and 121.517081
- **AND** no marker is moved and no map view is changed

---
### Requirement: Initialization entry points are callable before their definitions

The DOM-only initialization block runs at the top of the script, ahead of every
function definition it calls. Those functions SHALL therefore be declared in a form
that is reachable from a call site appearing earlier in the same script.

A function declaration (`function name() { ... }`) satisfies this. A function bound to
a `const`, `let`, or class field does not: the binding is not initialized until control
reaches it, so a call from the initialization block raises a reference error instead of
running. Because that error is thrown from a top-level statement, it also stops every
top-level statement after it — which is precisely the failure mode the DOM-only
initialization ordering exists to prevent.

Converting these declarations to `const` arrow functions is therefore not a neutral
modernization. It SHALL NOT be done without first moving the initialization block below
every definition it depends on, which would reintroduce that failure mode.

#### Scenario: The initialization block runs before the definitions it calls

- **WHEN** the page script is evaluated
- **THEN** the coordinate readout and both speed labels are populated
- **AND** the functions that populate them are defined later in the same script

##### Example: the three initialization call sites and their definitions

| Call | Definition | Separation |
| ---- | ---------- | ---------- |
| `updateDisplay()`    | `function updateDisplay()`    | ~220 lines later |
| `updateWalkSpeed()`  | `function updateWalkSpeed()`  | ~344 lines later |
| `updateSpeed()`      | `function updateSpeed()`      | ~205 lines later |

#### Scenario: A non-hoisted declaration form breaks every downstream initialization

- **GIVEN** one of these functions is redeclared as a `const` arrow function
- **WHEN** the page loads
- **THEN** the initialization block raises a reference error
- **AND** the coordinate readout and speed labels stay at their placeholders
- **AND** the search key binding and the outside-click dismissal are never bound,
  because their registration follows the failing statement
