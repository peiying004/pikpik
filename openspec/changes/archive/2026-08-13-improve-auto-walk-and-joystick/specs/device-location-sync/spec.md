## ADDED Requirements

### Requirement: Device location writes are mutually exclusive

The system SHALL serialise device location writes and connection recovery so that at most one coroutine at a time is able to establish, replace, or tear down the shared device connection objects. A stale-connection recovery triggered by one write SHALL NOT be interleaved with another write's recovery.

#### Scenario: Concurrent writes do not corrupt the shared connection

- **WHEN** several location writes are dispatched while an earlier write is still in flight
- **THEN** only one of them holds the connection at a time
- **AND** no write tears down a connection that another write has just established

#### Scenario: Connection recovery during a long walk

- **WHEN** the device connection goes stale during a running walk
- **THEN** exactly one recovery sequence runs
- **AND** the walk continues writing to the device after recovery succeeds

### Requirement: Overlapping walk writes are dropped rather than queued

While a walk is running, the system SHALL skip the current tick's device write when the previous write has not yet completed. The system SHALL NOT accumulate an unbounded backlog of pending device writes. A dropped write SHALL NOT be recorded as a failure and SHALL NOT be reported as an error.

#### Scenario: Slow device write causes the next tick to be skipped

- **WHEN** a walk tick is due and the previous device write has not completed
- **THEN** the current tick's device write is skipped
- **AND** no pending write is queued for later delivery
- **AND** no failure is recorded

#### Scenario: Later position supersedes a dropped one

- **WHEN** a walk tick's write is dropped
- **THEN** the next successful write carries the walker's newer position
- **AND** the device is not sent the dropped older position

### Requirement: Device write failures are surfaced, not swallowed

The system SHALL retrieve and record the outcome of every device write dispatched from the walk path, including writes that raise an exception. The system SHALL NOT leave a write's exception unretrieved.

The walk status SHALL report whether the most recent device write succeeded, and SHALL report the most recent failure message when the most recent write failed. The frontend SHALL display a device-write failure indication together with that message while a walk is running.

#### Scenario: Failing write is recorded and reported

- **WHEN** a device write raised from the walk path fails
- **THEN** the failure is recorded on the server
- **AND** the walk status reports the most recent device write as unsuccessful
- **AND** the walk status carries the failure message

#### Scenario: Interface stops claiming success once writes fail

- **WHEN** every device write fails while a walk is running
- **THEN** the interface indicates that device writes are failing
- **AND** the interface does not present the device as being written to successfully

#### Scenario: Successful write clears the failure indication

- **WHEN** a device write succeeds after earlier writes failed
- **THEN** the walk status reports the most recent device write as successful
- **AND** the interface stops indicating a device-write failure

### Requirement: Device write failures do not abort the walk

A failed device write, including a failed connection recovery, SHALL NOT terminate the walk. The walker SHALL continue advancing its position and SHALL continue attempting device writes on subsequent ticks.

#### Scenario: Walk survives a temporary device disconnection

- **WHEN** the device becomes unreachable during a running walk
- **THEN** the walk remains active
- **AND** the walker continues advancing its position
- **AND** device writes are attempted again on subsequent ticks

#### Scenario: Walk resumes writing after the device returns

- **WHEN** the device becomes reachable again after being unreachable during a running walk
- **THEN** device writes succeed again
- **AND** the device location catches up to the walker's current position
