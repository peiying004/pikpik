## MODIFIED Requirements

### Requirement: Multi-waypoint sequential walk

The system SHALL accept an ordered list of two or more coordinates and walk to each coordinate in the order given. The device location SHALL be set to the first coordinate exactly, before any interpolated position is produced. The walker SHALL then advance along a straight line toward the next coordinate at the configured speed, and upon reaching a coordinate SHALL continue immediately toward the following coordinate without pausing. The walk SHALL end automatically after the final coordinate is reached.

When a walk ends by reaching its final coordinate, the system SHALL ensure the device has been sent that final coordinate exactly, dispatching an additional write when the final coordinate has not already been delivered.

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

#### Scenario: First coordinate reaches the device before any interpolation

- **WHEN** a walk starts
- **THEN** the first coordinate the device receives is the route's first coordinate exactly
- **AND** no interpolated position is sent to the device before it

##### Example: the device is not advanced before its first write

- **GIVEN** the route starts at 25.033964,121.564468
- **AND** the configured speed advances 1 metre per tick
- **WHEN** the walk starts
- **THEN** the device receives 25.033964,121.564468
- **AND** the device does not receive a position 1 metre along the first segment as its first write

#### Scenario: Final coordinate reaches the device even when a write was in flight

- **WHEN** a walk reaches its final coordinate while an earlier device write has not completed
- **THEN** the final coordinate is still dispatched to the device
- **AND** the device is not left at a position short of the final coordinate

#### Scenario: Coordinates are reached exactly

- **WHEN** a walk is given a coordinate that lies away from any road
- **THEN** the walker passes through that exact coordinate
- **AND** the coordinate is not displaced toward a nearby road

#### Scenario: Straight-line path crosses impassable terrain

- **WHEN** the straight line between two consecutive coordinates crosses a building, a body of water, or restricted ground
- **THEN** the walker follows that straight line regardless

---

### Requirement: Walk route rendering and progress reporting

While a multi-waypoint walk is configured or running, the system SHALL draw a numbered marker for each coordinate in input order and a polyline connecting the coordinates in that order, and SHALL fit the map view to enclose all coordinates. While the walk runs, the system SHALL display the index of the most recently reached coordinate together with the total coordinate count.

When a walk ends by reaching its final coordinate, the displayed progress SHALL read the final coordinate's index together with the total coordinate count, and SHALL remain visible after the numbered markers and the polyline are removed.

#### Scenario: Progress advances as coordinates are reached

- **WHEN** a walk over three coordinates is running
- **THEN** the displayed progress reads coordinate 1 of 3 at the start
- **AND** it reads coordinate 2 of 3 once the second coordinate is reached
- **AND** it reads coordinate 3 of 3 once the third coordinate is reached

#### Scenario: Final index stays visible after the walk completes

- **WHEN** a walk over three coordinates reaches its third coordinate and ends on its own
- **THEN** the displayed progress reads coordinate 3 of 3
- **AND** that reading remains visible after the numbered markers and the polyline are removed

#### Scenario: Route is drawn before movement begins

- **WHEN** the user starts a multi-waypoint walk
- **THEN** numbered markers appear at each coordinate in input order
- **AND** a polyline connects the coordinates in that order
- **AND** the map view encloses all coordinates

---

### Requirement: Stopping a multi-waypoint walk

The system SHALL allow the user to stop a running multi-waypoint walk. On stopping, the system SHALL halt movement, report the walk as inactive, and remove the numbered coordinate markers and the connecting polyline from the map.

When the walk is stopped at the user's request rather than by reaching its final coordinate, the system SHALL NOT dispatch the route's final coordinate to the device, and SHALL clear the displayed progress together with the markers and the polyline.

#### Scenario: User stops a running walk

- **WHEN** the user presses the stop button while a multi-waypoint walk runs
- **THEN** movement halts
- **AND** the walk reports itself inactive
- **AND** the numbered markers and the connecting polyline are removed from the map

#### Scenario: Stopping does not jump the device to the final coordinate

- **WHEN** the user presses the stop button partway along a route
- **THEN** the route's final coordinate is not dispatched to the device
- **AND** the displayed progress is cleared

## ADDED Requirements

### Requirement: Walk start validates route coordinates and speed

The walk start request SHALL be validated before any walker is started. The system SHALL convert every coordinate in the route to a number, and SHALL require each latitude to lie between -90 and 90 and each longitude to lie between -180 and 180. The system SHALL convert the speed to a number and SHALL require it to be greater than zero.

When any of these conditions fails, the system SHALL reject the request with a 4xx status code and a response carrying an explanation, SHALL NOT start a walker, and SHALL NOT alter the walk status. The walker SHALL receive the converted numeric route rather than the raw request input.

#### Scenario: Non-numeric coordinate is rejected before a walker starts

- **WHEN** a walk start request carries a route whose coordinate is not a number
- **THEN** the request is rejected with a 4xx status code
- **AND** no walker is started
- **AND** the walk status reports the walk as inactive

#### Scenario: Rejection does not produce the start-then-stop symptom

- **WHEN** a walk start request is rejected for an invalid route or speed
- **THEN** the failure is reported in the response to that request
- **AND** the interface does not show a walk that starts and immediately stops

##### Example: rejection cases

| Route                                              | Speed | Result                        | Notes                    |
| -------------------------------------------------- | ----- | ----------------------------- | ------------------------ |
| `[[25.033964, 121.564468], [25.041, 121.565]]`     | 18    | walk starts                   | normal case              |
| `[["25.033964", "121.564468"], [25.041, 121.565]]` | 18    | walk starts                   | numeric strings convert  |
| `[[25.033964, 121.564468], ["abc", 121.565]]`      | 18    | rejected with 4xx             | coordinate not a number  |
| `[[91.0, 121.564468], [25.041, 121.565]]`          | 18    | rejected with 4xx             | latitude above 90        |
| `[[25.033964, 181.0], [25.041, 121.565]]`          | 18    | rejected with 4xx             | longitude above 180      |
| `[[25.033964, 121.564468], [25.041, 121.565]]`     | "x"   | rejected with 4xx             | speed not a number       |
| `[[25.033964, 121.564468], [25.041, 121.565]]`     | 0     | rejected with 4xx             | speed not greater than 0 |
| `[[25.033964, 121.564468], [25.041, 121.565]]`     | -5    | rejected with 4xx             | speed not greater than 0 |
