# device-location-sync Specification

## Purpose

Writing simulated coordinates to the connected device: serialising access to the
shared connection, bounding the write rate, and making failures observable.

Covers mutual exclusion across location writes and connection recovery, dropping
rather than queueing writes that overlap a slower in-flight write, retrieving and
reporting write outcomes instead of discarding them, and keeping a walk running when
writes fail.

The shared connection objects are module-level state that several concurrent
coroutines can reach, so every path that establishes, replaces, or tears down a
connection is serialised. Failures are surfaced rather than silent because the
reported walk position is pure interpolation: without explicit reporting, a frozen
device is indistinguishable from a healthy one.

## Requirements

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

---
### Requirement: Overlapping walk writes are dropped rather than queued

While a walk is running, the system SHALL skip the current tick's device write when the previous write has not yet completed. The system SHALL NOT accumulate an unbounded backlog of pending device writes. A dropped write SHALL NOT be recorded as a failure and SHALL NOT be reported as an error.

The write that delivers a route's first coordinate and the write that delivers a route's final coordinate SHALL be exempt from this rule and SHALL be dispatched even when an earlier write has not completed. No other write SHALL be exempt. The final-coordinate write SHALL be dispatched only when the walk ends by reaching that coordinate, and SHALL NOT be dispatched when the user stops the walk.

#### Scenario: Slow device write causes the next tick to be skipped

- **WHEN** a walk tick is due and the previous device write has not completed
- **THEN** the current tick's device write is skipped
- **AND** no pending write is queued for later delivery
- **AND** no failure is recorded

#### Scenario: Later position supersedes a dropped one

- **WHEN** a walk tick's write is dropped
- **THEN** the next successful write carries the walker's newer position
- **AND** the device is not sent the dropped older position

#### Scenario: Endpoint writes are not subject to dropping

- **WHEN** a route's first or final coordinate is due to be written and an earlier write has not completed
- **THEN** that write is dispatched rather than skipped
- **AND** the ticks between the two endpoints keep the dropping behaviour unchanged

##### Example: which writes can be dropped

| Write                                   | Dropped when an earlier write is in flight |
| --------------------------------------- | ------------------------------------------ |
| route's first coordinate                | no                                         |
| an interpolated position mid-route      | yes                                        |
| a coordinate reached mid-route          | yes                                        |
| route's final coordinate, walk completed | no                                        |
| route's final coordinate, user stopped  | not dispatched at all                      |

---
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

---
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

---
### Requirement: Write outcomes from a superseded walk are discarded

Each walk SHALL be identified by a generation that changes when a new walk starts. A device write dispatched from the walk path SHALL carry the generation that was current when it was dispatched.

When a write completes, the system SHALL apply its outcome to the walk status only when the carried generation matches the current generation. The system SHALL discard the outcome of a write whose generation no longer matches, without recording a failure, without carrying a failure message, and without altering the walk status. The generation SHALL NOT appear in the walk status response.

#### Scenario: A previous walk's write does not alter the new walk's status

- **WHEN** a write dispatched by one walk completes after a new walk has started
- **THEN** the new walk's reported device write outcome is unchanged by it
- **AND** the new walk continues to report no result yet until one of its own writes completes

#### Scenario: A previous walk's failure does not appear on the new walk

- **WHEN** a write dispatched by one walk fails after a new walk has started
- **THEN** the failure is not recorded on the new walk
- **AND** the new walk's failure message stays empty

#### Scenario: The current walk's own outcomes still apply

- **WHEN** a write dispatched by the current walk completes
- **THEN** its outcome is applied to the walk status as succeeded or failed
