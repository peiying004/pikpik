## MODIFIED Requirements

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

## ADDED Requirements

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
