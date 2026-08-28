## ADDED Requirements

### Requirement: Default automatic walk speed

The system SHALL use 18 km/h as the default automatic walk speed. The backend SHALL apply 18 km/h when a walk start request omits the speed field. The frontend SHALL initialise the automatic walk speed slider to 18 and SHALL derive its displayed speed label and its in-memory speed value from the slider's current value at page load, so that the slider is the single frontend source of the default.

#### Scenario: Page loads with the default speed shown

- **WHEN** the user loads the simulator page
- **THEN** the automatic walk speed slider is positioned at 18
- **AND** the label beneath the slider reads "18 km/h"

#### Scenario: Walk starts without the user touching the slider

- **WHEN** the user starts a walk without adjusting the automatic walk speed slider
- **THEN** the walk proceeds at 18 km/h

#### Scenario: Walk start request omits the speed field

- **WHEN** a walk start request arrives without a speed field
- **THEN** the backend runs the walk at 18 km/h

### Requirement: Multi-waypoint sequential walk

The system SHALL accept an ordered list of two or more coordinates and walk to each coordinate in the order given. The device location SHALL be set to the first coordinate when the walk starts. The walker SHALL then advance along a straight line toward the next coordinate at the configured speed, and upon reaching a coordinate SHALL continue immediately toward the following coordinate without pausing. The walk SHALL end automatically after the final coordinate is reached.

The system SHALL NOT snap the supplied coordinates to a road network, and SHALL NOT alter the supplied coordinates in any way.

#### Scenario: Walk visits every coordinate in input order

- **WHEN** the user enters three coordinates and starts the walk
- **THEN** the device location is set to the first coordinate
- **AND** the walker advances in a straight line to the second coordinate
- **AND** the walker continues to the third coordinate without pausing at the second
- **AND** the walk ends automatically once the third coordinate is reached

##### Example: three coordinates at 18 km/h

- **GIVEN** the coordinate list 25.033964,121.564468 then 25.041000,121.565000 then 25.047924,121.517081
- **AND** the configured speed is 18 km/h, which advances 1 metre per 200 ms tick
- **WHEN** the user starts the walk
- **THEN** the device is first placed at 25.033964,121.564468
- **AND** the walker travels the straight-line segment to 25.041000,121.565000, then the straight-line segment to 25.047924,121.517081
- **AND** no pause occurs at 25.041000,121.565000
- **AND** the walk reports itself inactive after 25.047924,121.517081 is reached

#### Scenario: Coordinates are reached exactly

- **WHEN** a walk is given a coordinate that lies away from any road
- **THEN** the walker passes through that exact coordinate
- **AND** the coordinate is not displaced toward a nearby road

#### Scenario: Straight-line path crosses impassable terrain

- **WHEN** the straight line between two consecutive coordinates crosses a building, a body of water, or restricted ground
- **THEN** the walker follows that straight line regardless

### Requirement: Coordinate list input

The system SHALL provide a multi-line text input that accepts one coordinate per line, written as a latitude and a longitude separated by a comma. The system SHALL ignore blank lines and SHALL trim leading and trailing whitespace on each line.

The system SHALL reject the input and SHALL NOT start a walk when any non-blank line fails to parse as two numbers, when a latitude falls outside -90 through 90, when a longitude falls outside -180 through 180, or when fewer than two valid coordinates remain. A rejection message SHALL identify the offending input line number and the reason.

#### Scenario: Valid input starts the walk

- **WHEN** the user enters two or more valid coordinate lines and presses the start button
- **THEN** the walk starts with those coordinates in the order entered

#### Scenario: Unparseable line is rejected

- **WHEN** the input contains a non-blank line that does not parse as two numbers
- **THEN** no walk starts
- **AND** a message identifies the input line number and states that the line is not a valid coordinate pair

#### Scenario: Fewer than two valid coordinates

- **WHEN** the input yields fewer than two valid coordinates
- **THEN** no walk starts
- **AND** a message states that at least two coordinates are required

##### Example: parsing and validation cases

| Input                                                        | Result                                        | Notes                          |
| ------------------------------------------------------------ | --------------------------------------------- | ------------------------------ |
| `25.033964, 121.564468` / `25.041000, 121.565000`            | walk starts with 2 coordinates                | normal case                    |
| `  25.033964,121.564468  ` / `` / `25.041000,121.565000`     | walk starts with 2 coordinates                | whitespace trimmed, blank line ignored |
| `25.033964, 121.564468` / `25.03, abc` / `25.041, 121.565`   | rejected, message names input line 2          | second value is not a number   |
| `25.033964, 121.564468` / `91.0, 121.565000`                 | rejected, message names input line 2          | latitude above 90              |
| `25.033964, 121.564468` / `25.041000, 181.0`                 | rejected, message names input line 2          | longitude above 180            |
| `25.033964, 121.564468`                                      | rejected, at least two coordinates required   | only one coordinate            |
| `` (empty input)                                             | rejected, at least two coordinates required   | no coordinates                 |

### Requirement: Walk route rendering and progress reporting

While a multi-waypoint walk is configured or running, the system SHALL draw a numbered marker for each coordinate in input order and a polyline connecting the coordinates in that order, and SHALL fit the map view to enclose all coordinates. While the walk runs, the system SHALL display the index of the most recently reached coordinate together with the total coordinate count.

#### Scenario: Progress advances as coordinates are reached

- **WHEN** a walk over three coordinates is running
- **THEN** the displayed progress reads coordinate 1 of 3 at the start
- **AND** it reads coordinate 2 of 3 once the second coordinate is reached
- **AND** it reads coordinate 3 of 3 once the third coordinate is reached

#### Scenario: Route is drawn before movement begins

- **WHEN** the user starts a multi-waypoint walk
- **THEN** numbered markers appear at each coordinate in input order
- **AND** a polyline connects the coordinates in that order
- **AND** the map view encloses all coordinates

### Requirement: Walk state is truthful when the start request responds

The walk start endpoint SHALL set the walk to active, reset the progress index to the first coordinate, record the total coordinate count, and reset the device-write status before it returns its response. A status query issued immediately after that response SHALL report the walk as active.

#### Scenario: Status query immediately after start reports active

- **WHEN** a walk start request returns successfully
- **AND** a walk status query is issued before the walker has advanced
- **THEN** the status reports the walk as active

#### Scenario: Starting a walk does not immediately stop

- **WHEN** the user starts a walk
- **THEN** the walk continues running
- **AND** the interface does not revert to the stopped state without the user requesting a stop

#### Scenario: Consecutive walks do not carry stale progress

- **WHEN** a walk is started after a previous walk has finished
- **THEN** the reported progress index refers to the new walk's first coordinate
- **AND** the reported total coordinate count refers to the new walk's coordinate list

### Requirement: Stopping a multi-waypoint walk

The system SHALL allow the user to stop a running multi-waypoint walk. On stopping, the system SHALL halt movement, report the walk as inactive, and remove the numbered coordinate markers and the connecting polyline from the map.

#### Scenario: User stops a running walk

- **WHEN** the user presses the stop button while a multi-waypoint walk runs
- **THEN** movement halts
- **AND** the walk reports itself inactive
- **AND** the numbered markers and the connecting polyline are removed from the map
