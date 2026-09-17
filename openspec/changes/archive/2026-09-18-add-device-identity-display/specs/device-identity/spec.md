## ADDED Requirements

### Requirement: The connected device's identity is retained when the connection is established

The system SHALL record the identity of the device it connects to at the moment the shared connection is established, and SHALL clear that record when the connection is closed. The identity SHALL comprise the device's unique device identifier, its product type, a readable model name derived from that product type, its operating system version, and the interface name of the tunnel record it connected through.

The interface name SHALL be recorded because a unique device identifier does not identify a tunnel: one phone attached by cable and reachable on the same network has two tunnel records sharing one identifier. The interface name is what distinguishes them. It exists only to answer "which tunnel record is in use" and SHALL NOT be reported to callers, who have no use for it.

The identity SHALL be taken from the connection that was actually established, not re-derived by re-reading the tunnel list. Re-reading the list and taking its first entry reproduces the selection rule instead of reading its result: the two agree only by coincidence, and a list whose order changes between reads would report a device the system is not using, with no symptom until a location write lands on the wrong phone.

The readable model name SHALL be derived from the product type using the device table the device library already provides, and SHALL fall back to the product type itself when the table has no entry for it. The system SHALL NOT use the name attribute of the tunnel-derived connection object as the device name, because that attribute carries the network interface name rather than a device name.

#### Scenario: Identity is recorded on connect and cleared on disconnect

- **WHEN** the shared connection to a device is established
- **THEN** the system holds that device's unique device identifier, product type, model name, and operating system version
- **AND** that device's visibility is recorded as listed, because reaching it required reading the tunnel list
- **AND** the interface name of the tunnel record it connected through is recorded
- **WHEN** the shared connection is closed
- **THEN** the system holds no device identity
- **AND** the recorded visibility returns to undetermined

#### Scenario: Model name falls back to the product type

- **WHEN** a device's product type has no entry in the device table
- **THEN** the reported model name is the product type itself
- **AND** it is not empty

##### Example: product type to model name

| Product type | Reported model name | Notes                         |
| ------------ | ------------------- | ----------------------------- |
| `iPhone14,2` | `iPhone 13 Pro`     | present in the device table   |
| `iPhone10,1` | `iPhone 8 (Global)` | present in the device table   |
| `iPhone19,1` | `iPhone19,1`        | absent, falls back to the code |

---

### Requirement: Device identity is reported without touching the device

The system SHALL provide a read-only query that reports the retained device identity together with the last known visibility of that device.

The query SHALL read state already held in memory and nothing else. It SHALL NOT establish, replace, or close any device connection, SHALL NOT write or clear a simulated location, SHALL NOT alter walk state, and SHALL NOT contact the tunnel daemon. Contacting the tunnel daemon on every call would make each poll produce a request — and therefore a log line — in the tunnel daemon's own process, which runs in the same terminal; silencing the poll in this system's log while generating the same volume in another process solves nothing.

Visibility SHALL be recorded when the shared connection is established, where the device is known to be listed because the tunnel list was just read to reach it, and SHALL be refreshed whenever diagnostics runs, which reads the tunnel list for its own purposes. Between those moments the reported visibility MAY be out of date.

The visibility of the device SHALL be three-state: listed, not listed, or undetermined. Undetermined SHALL be reported when the last attempt to read the tunnel list failed, and when no attempt has been made. Reporting an unreachable tunnel daemon as "not listed" blames the phone for the daemon's failure, and the two send the user to different remedies — one to reconnect the phone, the other to restart the daemon.

The query SHALL always respond successfully, expressing an unknown device or unknown visibility through its reported values rather than through a failure status, so that a caller can distinguish a completed query that found nothing from a query that itself broke.

#### Scenario: Query reports identity and visibility

- **WHEN** a device connection is established and the tunnel daemon lists that device
- **AND** the identity query is issued
- **THEN** the retained identity is reported
- **AND** visibility is reported as listed

##### Example: response shape

- **GIVEN** the shared connection was established to a device whose unique device identifier is `00008110-000A4D2E0A88801E`, product type `iPhone14,2`, operating system version `17.5`
- **AND** the tunnel daemon still lists that unique device identifier
- **WHEN** the identity query is issued
- **THEN** the response carries an `identity` object with `udid` `00008110-000A4D2E0A88801E`, `product_type` `iPhone14,2`, `model` `iPhone 13 Pro`, `os_version` `17.5`
- **AND** the response carries `visible` set to `true`

#### Scenario: Device no longer listed is distinguished from an unreachable daemon

- **WHEN** diagnostics has run and found that the tunnel daemon no longer lists the connected device
- **THEN** visibility is reported as not listed
- **WHEN** diagnostics has run and the tunnel daemon could not be reached
- **THEN** visibility is reported as undetermined
- **AND** the two conditions are distinguishable from one another

#### Scenario: The query itself contacts nothing

- **WHEN** the identity query is called repeatedly
- **THEN** no request is made to the tunnel daemon
- **AND** the reported visibility is whatever was last recorded

##### Example: visibility by condition

| Retained identity | Tunnel daemon state                    | `identity` | `visible` | Status code |
| ----------------- | -------------------------------------- | ---------- | --------- | ----------- |
| present           | lists the identity's unique device id  | object     | `true`    | 2xx         |
| present           | reachable, does not list that id       | object     | `false`   | 2xx         |
| present           | cannot be reached                      | object     | `null`    | 2xx         |
| absent            | any                                    | `null`     | `null`    | 2xx         |

#### Scenario: Query leaves device state unchanged

- **WHEN** the identity query is issued repeatedly
- **THEN** no device connection is established, replaced, or closed
- **AND** no simulated location is written or cleared
- **AND** walk state is unchanged

#### Scenario: No connection has been established

- **WHEN** no shared connection has been established
- **AND** the identity query is issued
- **THEN** no identity is reported
- **AND** visibility is reported as undetermined

---

### Requirement: The status bar reports which device is connected

The control interface SHALL present the connected device's model name and operating system version in the status bar, and SHALL refresh that presentation periodically so that it reflects the device's current state rather than the result of the user's last action.

The status bar SHALL distinguish four conditions from one another: no device identity is held, the device is held and still listed, the device is held but no longer listed, and the device is held but its visibility cannot be determined.

The status bar's device identity and its device state SHALL be maintained separately and rendered together, so that a device write failure during a walk is presented alongside the device's name rather than replacing it. Every writer of the status bar SHALL go through the single rendering path; writers that set the text directly would overwrite one another, and that fault appears only under specific timing.

The periodic refresh SHALL depend only on the document and the fetch capability, so that it continues to run when a third-party library fails to load.

#### Scenario: Status bar names the connected device

- **WHEN** a device connection is established and the device is still listed
- **THEN** the status bar presents that device's model name and operating system version
- **AND** it indicates that the device is connected

#### Scenario: Status bar stops naming a device that went away

- **WHEN** the connected device stops being listed by the tunnel daemon
- **AND** diagnostics is then run
- **THEN** the status bar indicates that the device is offline
- **AND** it does not continue to present the device as connected

#### Scenario: A device that goes away while idle is corrected by the next device write

- **WHEN** the connected device is physically detached while the user is doing nothing
- **THEN** the status bar continues to name it until diagnostics runs or a device write is attempted
- **AND** the first failing device write presents the failure alongside the device name

#### Scenario: Losing the connection clears the name without any tunnel query

- **WHEN** the shared connection is closed, whether by stopping the simulation or otherwise
- **THEN** the status bar returns to reporting no device within one refresh interval
- **AND** no tunnel daemon request is made to determine this

#### Scenario: Unreachable daemon is not presented as an offline device

- **WHEN** the tunnel daemon cannot be queried
- **THEN** the status bar indicates that the device's state cannot be determined
- **AND** it does not indicate that the device is offline

#### Scenario: Device name and write failure are presented together

- **WHEN** a walk is running and a device write fails
- **AND** a device identity is held
- **THEN** the status bar presents both the device's model name and the write failure
- **AND** neither replaces the other

##### Example: status bar text by condition

| Identity held | Visibility    | Walk write state | Status bar text                    | Indicator |
| ------------- | ------------- | ---------------- | ---------------------------------- | --------- |
| none          | undetermined  | —                | `未連接裝置`                        | off       |
| `iPhone 13 Pro`, iOS 17.5 | listed | ok    | `iPhone 13 Pro · iOS 17.5 已連接`   | on        |
| `iPhone 13 Pro`, iOS 17.5 | not listed | — | `iPhone 13 Pro 已離線`              | off       |
| `iPhone 13 Pro`, iOS 17.5 | undetermined | — | `iPhone 13 Pro · 無法確認狀態`      | off       |
| `iPhone 13 Pro`, iOS 17.5 | listed | write failed | `iPhone 13 Pro 裝置寫入失敗`        | off       |
| `iPhone19,1`, iOS 18.2    | listed | ok     | `iPhone19,1 · iOS 18.2 已連接`      | on        |

#### Scenario: A failed query does not break the refresh

- **WHEN** the identity query fails or returns a response missing required fields
- **THEN** the status bar keeps its existing text
- **AND** the periodic refresh continues

---

### Requirement: Model information is recorded for every device seen during a connection attempt

When the system obtains the list of tunnel-derived devices in order to establish a connection, it SHALL record, for every device in that list, the mapping from unique device identifier to product type, readable model name, and operating system version — not only for the device it goes on to use.

The recording SHALL NOT cause any additional handshake. The connection path already handshakes every entry in that list and discards all but the one it selects; the requirement is to retain what has already been obtained, not to obtain more.

The recorded mapping is a display aid and MAY be out of date, because it is refreshed only when a connection attempt occurs. A device that has never been handshaken SHALL have no entry, and consumers SHALL omit model information for it rather than substitute a guess.

#### Scenario: Every listed device is recorded, not just the selected one

- **WHEN** the tunnel-derived device list contains two devices and a connection is established to the first
- **THEN** model information is recorded for both devices
- **AND** no handshake beyond those the list retrieval already performed is made

#### Scenario: A never-seen device has no recorded model

- **WHEN** a unique device identifier has never appeared in a retrieved device list
- **THEN** no model information is recorded for it

---

### Requirement: The identity poll does not drown the server log

The system SHALL suppress the access-log line for a request to the device identity query when that request is answered with a 2xx status, and SHALL NOT suppress it for any other status.

A poll running every few seconds produces well over a thousand access-log lines per hour. The server log also carries walk progress and device-write failures, which are the primary evidence of whether the device is still alive; a successful health check has no diagnostic value and must not crowd them out.

Suppressing the endpoint's failures as well would make this feature's own malfunction silent: an endpoint called every few seconds that begins answering 5xx is visible in the log and nowhere else.

The suppression SHALL be decided from the request line and status carried by the log record rather than from the formatted log message, because the formatted message is wrapped in terminal styling for non-2xx responses and its layout is not a stable contract.

No other path's logging SHALL be affected, and output that does not pass through the access log — walk progress and device-write reporting — SHALL be untouched.

The poll SHALL NOT generate equivalent noise in any other process. The tunnel daemon runs as a separate process whose output shares the operator's terminal and whose logging this system cannot filter; a poll that contacted it every few seconds would move the noise rather than remove it. This is why the identity query reads only memory.

#### Scenario: Successful polls leave no access-log lines

- **WHEN** the device identity query is called repeatedly and every call is answered with a 2xx status
- **THEN** no access-log line mentions that query

#### Scenario: A failing poll is still logged

- **WHEN** the device identity query is answered with a status that is not 2xx
- **THEN** an access-log line for that request is written

#### Scenario: Other endpoints keep their access-log lines

- **WHEN** the diagnostics query and the location endpoint are called
- **THEN** access-log lines for both are written

#### Scenario: Polling produces no log lines in the tunnel daemon

- **WHEN** the device identity query is called repeatedly while a device is connected
- **THEN** the tunnel daemon receives no requests as a result
- **AND** its own log gains no lines

##### Example: which lines survive

| Request                       | Status | Access-log line |
| ----------------------------- | ------ | --------------- |
| device identity query         | 200    | suppressed      |
| device identity query         | 500    | written         |
| device identity query         | 404    | written         |
| diagnostics query             | 200    | written         |
| location endpoint             | 200    | written         |
