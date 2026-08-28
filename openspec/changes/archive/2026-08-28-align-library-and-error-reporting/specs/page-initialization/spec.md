## MODIFIED Requirements

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

## ADDED Requirements

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
