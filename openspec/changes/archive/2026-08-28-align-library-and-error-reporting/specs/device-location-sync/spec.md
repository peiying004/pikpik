## MODIFIED Requirements

### Requirement: Device write failures are surfaced, not swallowed

The system SHALL retrieve and record the outcome of every device write dispatched from the walk path, including writes that raise an exception. The system SHALL NOT leave a write's exception unretrieved.

The walk status SHALL report the most recent device write outcome as exactly one of three states: no result yet, succeeded, or failed. A walk SHALL begin in the no-result-yet state, and SHALL leave that state only when a dispatched write has completed. The walk status SHALL carry the most recent failure message while the state is failed, and SHALL carry an empty failure message in the other two states.

The frontend SHALL present the device as successfully written to only while the walk status reports the succeeded state. While the walk status reports no result yet, the frontend SHALL indicate that it is waiting for the device and SHALL NOT present the device as connected. While the walk status reports the failed state, the frontend SHALL display a device-write failure indication together with the failure message.

#### Scenario: Walk start reports no result yet

- **WHEN** a walk start request returns successfully
- **AND** a walk status query is issued before any dispatched device write has completed
- **THEN** the walk status reports the device write outcome as no result yet
- **AND** the walk status carries an empty failure message
- **AND** the interface indicates that it is waiting for the device
- **AND** the interface does not present the device as connected

#### Scenario: Failing write is recorded and reported

- **WHEN** a device write raised from the walk path fails
- **THEN** the failure is recorded on the server
- **AND** the walk status reports the device write outcome as failed
- **AND** the walk status carries the failure message

#### Scenario: Interface stops claiming success once writes fail

- **WHEN** every device write fails while a walk is running
- **THEN** the interface indicates that device writes are failing
- **AND** the interface does not present the device as being written to successfully

#### Scenario: Successful write clears the failure indication

- **WHEN** a device write succeeds after earlier writes failed
- **THEN** the walk status reports the device write outcome as succeeded
- **AND** the interface stops indicating a device-write failure

#### Scenario: A new walk returns to no result yet

- **WHEN** a walk is started after a previous walk ended with a failed device write
- **THEN** the walk status reports the device write outcome as no result yet
- **AND** the walk status carries an empty failure message
- **AND** the interface does not carry the previous walk's failure message

##### Example: device write state across one walk

| Point in the walk                              | Reported outcome | Failure message | Interface                |
| ---------------------------------------------- | ---------------- | --------------- | ------------------------ |
| start request has returned, no write completed | no result yet    | empty           | waiting for the device   |
| first write completed successfully             | succeeded        | empty           | device connected         |
| a later write raised "No device found"         | failed           | No device found | device write failed, with the message |
| a write succeeded again                        | succeeded        | empty           | device connected         |
| a new walk is started                          | no result yet    | empty           | waiting for the device   |
