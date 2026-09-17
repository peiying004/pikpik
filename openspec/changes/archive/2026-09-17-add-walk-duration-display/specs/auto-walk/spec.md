## ADDED Requirements

### Requirement: Route length and duration preview before a multi-waypoint walk starts

The system SHALL display the total length of a multi-waypoint route together with the time that route takes at the currently selected automatic walk speed, before the walk is started. The total length SHALL be the sum of the great-circle distances between consecutive coordinates, and the duration SHALL be that length divided by the speed. The speed used SHALL be the automatic walk speed control's current value.

The preview SHALL be recomputed when the coordinate input changes and when the automatic walk speed changes. The preview SHALL be cleared whenever the coordinate input does not yield at least two valid coordinates, and SHALL NOT retain the length or duration of a previously valid input.

The route length SHALL be shown alongside the duration, so that a mistyped coordinate that displaces the route by an order of magnitude is visible without starting the walk.

#### Scenario: Preview appears for a valid coordinate list

- **WHEN** the user enters two or more valid coordinates without starting the walk
- **THEN** the total route length is displayed
- **AND** the time that route takes at the current automatic walk speed is displayed

##### Example: three coordinates at 18 km/h

- **GIVEN** the coordinate list 25.033964,121.564468 then 25.041000,121.565000 then 25.047924,121.517081
- **AND** the two segments measure 784 metres and 4888 metres, totalling 5673 metres
- **AND** the automatic walk speed control reads 18
- **WHEN** the coordinates are entered and the walk is not started
- **THEN** the display reads "全長 5.7 公里 · 約 18 分 55 秒"

#### Scenario: Preview follows the automatic walk speed control

- **WHEN** the user changes the automatic walk speed without changing the coordinate input
- **THEN** the displayed duration is recomputed at the new speed
- **AND** the displayed route length is unchanged

##### Example: the same route at 36 km/h

- **GIVEN** the route totalling 5673 metres is entered and the walk is not started
- **WHEN** the automatic walk speed control is moved from 18 to 36
- **THEN** the display reads "全長 5.7 公里 · 約 9 分 27 秒"

#### Scenario: Preview clears when the input stops being valid

- **WHEN** a valid coordinate list is previewed
- **AND** the user then edits the input so that it no longer yields at least two valid coordinates
- **THEN** the preview is cleared
- **AND** neither the length nor the duration of the previously valid input remains displayed

##### Example: the third line becomes unparseable

- **GIVEN** the coordinate list 25.033964,121.564468 then 25.041000,121.565000 then 25.047924,121.517081 is previewed as "全長 5.7 公里 · 約 18 分 55 秒"
- **WHEN** the third line is edited to `25.047924, abc`
- **THEN** the display is empty
- **AND** it does not remain at "全長 5.7 公里 · 約 18 分 55 秒"

---

### Requirement: Remaining time while a walk runs

While a walk runs, the system SHALL display the time remaining until the route is completed. The remaining time SHALL be the remaining distance divided by the speed the running walk was started with, and SHALL be recomputed on every walk status update.

The remaining distance SHALL be the distance from the walk's currently reported position to the first coordinate it has not yet reached, plus the length of every route segment after that coordinate.

The speed used SHALL be the speed reported by the walk status rather than the automatic walk speed control's current value, because the speed of a running walk is fixed at the moment the walk starts and the control no longer governs it. Moving the automatic walk speed control while a walk runs SHALL NOT change the displayed remaining time for that walk.

The remaining time SHALL be displayed for a single-destination road walk as well as for a multi-waypoint walk. For a multi-waypoint walk it SHALL be displayed together with the reached-coordinate index and the total coordinate count; for a single-destination road walk it SHALL be displayed on its own, as that path reports no coordinate index.

When a multi-waypoint walk ends by reaching its final coordinate, the retained progress reading SHALL NOT include a remaining time.

#### Scenario: Remaining time accompanies the progress index during a multi-waypoint walk

- **WHEN** a multi-waypoint walk is running
- **THEN** the display shows the reached-coordinate index, the total coordinate count, and the remaining time
- **AND** the remaining time decreases as the walk advances

##### Example: partway along the second segment at 18 km/h

- **GIVEN** the route 25.033964,121.564468 then 25.041000,121.565000 then 25.047924,121.517081, whose segments measure 784 metres and 4888 metres
- **AND** the walk is running at 18 km/h, which advances 5 metres per second
- **AND** the walk has reached the second coordinate and advanced a further 1000 metres along the second segment, leaving 3888 metres
- **WHEN** the walk status is read
- **THEN** the display reads "第 2 點／共 3 點 · 剩餘 12 分 58 秒"

#### Scenario: Remaining time is shown for a single-destination road walk

- **WHEN** a single-destination road walk is running
- **THEN** the remaining time is displayed
- **AND** no coordinate index or coordinate count accompanies it

##### Example: 3888 metres remaining at 18 km/h

- **GIVEN** a single-destination road walk is running at 18 km/h
- **AND** 3888 metres of the returned road route remain ahead of the reported position
- **WHEN** the walk status is read
- **THEN** the display reads "剩餘 12 分 58 秒"
- **AND** the display contains no "第 N 點／共 M 點" reading

#### Scenario: Moving the speed control during a walk does not change the remaining time

- **WHEN** a walk is running
- **AND** the user moves the automatic walk speed control
- **THEN** the displayed remaining time for the running walk is unchanged
- **AND** it continues to be computed from the speed the walk was started with

##### Example: the control is moved from 18 to 36 mid-walk

- **GIVEN** a walk was started at 18 km/h and has 3888 metres remaining, displaying "剩餘 12 分 58 秒"
- **WHEN** the automatic walk speed control is moved from 18 to 36
- **THEN** the display continues from "剩餘 12 分 58 秒"
- **AND** it does not jump to "剩餘 6 分 29 秒", which is what 36 km/h over the same remaining distance would give

#### Scenario: Completed walk retains the index without a remaining time

- **WHEN** a multi-waypoint walk over three coordinates ends by reaching its third coordinate
- **THEN** the retained reading is "第 3 點／共 3 點"
- **AND** it carries no remaining time

---

### Requirement: Distance and duration display formats

The system SHALL format a displayed distance in metres when it is below 1000 metres and in kilometres to one decimal place when it is 1000 metres or above.

The system SHALL round a displayed duration to whole seconds and then format it by magnitude: seconds alone below one minute; minutes and seconds below one hour, with the seconds omitted when they round to zero; hours and minutes at one hour and above, with the seconds discarded. Seconds are discarded at the hour magnitude because stating them claims a precision the walk does not have.

#### Scenario: Distances and durations are formatted by magnitude

- **WHEN** a distance or a duration is displayed
- **THEN** it is formatted according to its magnitude

##### Example: formatting cases

| Value           | Displayed as | Notes                                  |
| --------------- | ------------ | -------------------------------------- |
| 784 metres      | `784 公尺`   | below 1000 metres, whole metres        |
| 5673 metres     | `5.7 公里`   | 1000 metres or above, one decimal      |
| 1000 metres     | `1.0 公里`   | boundary, formatted as kilometres      |
| 45 seconds      | `45 秒`      | below one minute                       |
| 778 seconds     | `12 分 58 秒` | below one hour                          |
| 1080 seconds    | `18 分`      | seconds round to zero, so omitted      |
| 3903 seconds    | `1 小時 5 分` | one hour or above, seconds discarded    |
