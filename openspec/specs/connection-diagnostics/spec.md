# connection-diagnostics Specification

## Purpose

Probing the device connection chain and reporting where it breaks: which stage failed,
what that means, and what the user does next.

Covers the four ordered probe stages and the halt that follows a failure, the three-state
stage outcome that keeps "not run" distinct from "failed", the per-stage detail and next
action, the device records reported as tunneld gives them, the server address a phone uses
to reach the control interface, and the guarantee that probing changes no device state.

This capability exists because the connection chain has several independent preconditions
— a running tunnel daemon, a paired and discovered device, a reachable tunnel, an available
developer service — and collapsing their failures into one message leaves the user unable to
tell which one to act on. Probing reuses the shared device connection rather than opening a
parallel one, so diagnosing a problem cannot create a second one.

## Requirements

### Requirement: Diagnostics probes the connection chain in four ordered stages

The system SHALL provide a read-only diagnostics endpoint that probes the device connection chain in four ordered stages: tunneld reachability, device discovery, tunnel connection, and developer service availability.

Each stage SHALL report its own outcome independently of the other stages. When a stage fails, the system SHALL NOT run the stages that follow it, because their preconditions no longer hold.

The tunneld reachability stage SHALL query the tunneld HTTP endpoint using the address constant published by the device communication library, and SHALL NOT call any private function of that library.

#### Scenario: All four stages run when the chain is healthy

- **WHEN** tunneld is running, a device is discovered, its tunnel connects, and the developer service opens
- **THEN** the diagnostics response contains four stages in the order tunneld reachability, device discovery, tunnel connection, developer service availability
- **AND** every stage reports success

#### Scenario: A failing stage halts the stages that follow it

- **WHEN** tunneld is not running
- **THEN** the tunneld reachability stage reports failure
- **AND** the device discovery, tunnel connection, and developer service stages each report that they were not run


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Stage outcomes are three-state rather than boolean

Each stage outcome SHALL distinguish three states: succeeded, failed, and not run. A stage that was skipped because an earlier stage failed SHALL report the not-run state and SHALL NOT report failure.

A boolean outcome SHALL NOT be used, because "not run" and "failed" call for different user action and collapsing them reproduces the ambiguity this capability exists to remove.

#### Scenario: Skipped stages are distinguishable from failed stages

- **WHEN** the device discovery stage fails
- **THEN** the device discovery stage reports the failed state
- **AND** the tunnel connection stage reports the not-run state
- **AND** the developer service stage reports the not-run state

##### Example: stage states for each failure point

| Failure point | tunneld | discovery | tunnel | developer service |
| ------------- | ------- | --------- | ------ | ----------------- |
| tunneld not running | failed | not run | not run | not run |
| no device found | succeeded | failed | not run | not run |
| tunnel connect times out | succeeded | succeeded | failed | not run |
| developer service will not open | succeeded | succeeded | succeeded | failed |
| chain healthy | succeeded | succeeded | succeeded | succeeded |


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Every stage outcome carries a detail and a next action

Each stage outcome SHALL carry a stage identifier, a display name, the three-state outcome, a detail text, and a next-action text.

A failed stage SHALL carry a next-action text naming what the user does to resolve it. The next-action texts SHALL be distinct across the four stages, because each failure calls for different user action.

#### Scenario: Each failure names a distinct next action

- **WHEN** the diagnostics endpoint reports a failed stage
- **THEN** that stage carries a non-empty next-action text
- **AND** the next-action text for a tunneld reachability failure differs from the next-action text for a device discovery failure

#### Scenario: Device discovery failure names the environment preconditions

- **WHEN** tunneld is reachable but reports no devices
- **THEN** the device discovery stage reports failure
- **AND** its next-action text names connecting a cable, device pairing, Wi-Fi sync, and developer mode as the conditions to check


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Diagnostics leaves device state unchanged

Running diagnostics SHALL NOT write coordinates to the device, SHALL NOT clear the simulated location, and SHALL NOT close the shared device connection.

Running diagnostics SHALL NOT alter walk state: it SHALL NOT start, stop, or advance a walk, and SHALL NOT change the reported walk progress or the recorded device-write outcome.

#### Scenario: A running walk is unaffected by diagnostics

- **WHEN** a walk is running
- **AND** the diagnostics endpoint is called twice in succession
- **THEN** the walk remains active
- **AND** the reported walk progress continues to advance
- **AND** the recorded device-write outcome is not replaced by a diagnostics result

#### Scenario: Simulated location survives diagnostics

- **WHEN** a simulated location has been written to the device
- **AND** the diagnostics endpoint is called
- **THEN** the simulated location on the device is unchanged


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Diagnostics reuses the existing device connection

When the shared location service is already established, the tunnel connection stage and the developer service stage SHALL report success without opening a further connection, because an established connection is itself evidence that both the tunnel and the developer service are available.

When the shared location service is not established, these stages SHALL use the existing connection-establishment path under the same device lock that serialises location writes, and SHALL retain the resulting connection rather than closing it.

Diagnostics SHALL NOT open a connection that runs in parallel with the shared connection.

#### Scenario: An established connection short-circuits the connecting stages

- **WHEN** the shared location service is already established
- **AND** the diagnostics endpoint is called
- **THEN** the tunnel connection stage reports success
- **AND** the developer service stage reports success
- **AND** no additional device connection is opened

#### Scenario: Diagnostics retains a connection it establishes

- **WHEN** no shared location service is established
- **AND** the diagnostics endpoint is called and the developer service stage succeeds
- **THEN** the shared location service is established after the call returns
- **AND** a subsequent location write succeeds without establishing a new connection


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Diagnostics reports the device records it found

The diagnostics response SHALL carry a device list. Each entry SHALL carry the device UDID, the interface address, the tunnel address, and the tunnel port, reported as returned by tunneld.

Each entry SHALL additionally carry a readable model name and an operating system version whenever the system knows them for that UDID, together with a flag stating whether that entry is the **tunnel record** the shared connection is currently using.

The flag SHALL be decided from the unique device identifier and the interface name together, not from the identifier alone. One phone attached by cable and reachable on the same network produces two tunnel records sharing one identifier, and only one of them carries the connection; deciding from the identifier alone marks both, and one of those marks is false. When the recorded interface name matches no listed entry, no entry SHALL be marked, because an absent mark merely withholds a hint whereas a wrong mark tells the user they are operating a tunnel they are not.

The model name SHALL still be decided from the unique device identifier alone, so that every tunnel record of a known phone shows what phone it is. These three fields are derived rather than reported by tunneld, whose response carries no model information at all. An entry whose model is unknown SHALL omit these fields rather than carry an empty or guessed value, because a wrong model name is worse than a bare UDID: the user would act on it.

The system SHALL NOT perform any additional device handshake in order to learn a model. It SHALL use only the information the existing connection path already obtains, because the device list is a display aid and must not become an operation that contends for the lock serialising location writes.

When no device is found, the device list SHALL be an empty list rather than absent.

The system SHALL NOT assert whether a tunnel runs over USB or over Wi-Fi, because the tunneld response carries no connection-type field and inferring it from the address form is unreliable.

#### Scenario: Discovered devices are reported with their tunnel records

- **WHEN** tunneld reports one device
- **THEN** the diagnostics device list contains one entry
- **AND** that entry carries a UDID, an interface address, a tunnel address, and a tunnel port

#### Scenario: No devices yields an empty list

- **WHEN** tunneld is reachable and reports no devices
- **THEN** the diagnostics device list is present and empty

#### Scenario: Known models are reported for every listed device

- **WHEN** tunneld lists two devices and the system knows the model of both
- **THEN** both entries carry a readable model name and an operating system version
- **AND** exactly the entry matching the shared connection is flagged as in use

#### Scenario: One phone on two transports marks only the tunnel in use

- **WHEN** tunneld lists two entries sharing one unique device identifier with different interface names
- **AND** the shared connection was established through one of them
- **THEN** both entries carry the model name
- **AND** only the entry whose interface name matches the connection is flagged as in use

#### Scenario: A recorded interface that no longer appears marks nothing

- **WHEN** the interface name recorded for the shared connection matches no listed entry
- **THEN** no entry is flagged as in use

#### Scenario: An unknown model is omitted rather than guessed

- **WHEN** tunneld lists a device the system has never handshaken with
- **THEN** that entry carries no model name and no operating system version
- **AND** it still carries its UDID, interface address, tunnel address, and tunnel port

#### Scenario: Learning a model costs no extra handshake

- **WHEN** the diagnostics device list is built
- **THEN** no device handshake is performed beyond those the existing connection path already performs

##### Example: entries by what is known

| Tunneld entry | System knowledge                        | Model fields | In-use flag |
| ------------- | --------------------------------------- | ------------ | ----------- |
| UDID-A        | shared connection is using UDID-A       | present      | true        |
| UDID-B        | handshaken during this connection attempt | present    | false       |
| UDID-C        | never handshaken                        | omitted      | false       |

##### Example: one phone, two tunnel records

| Tunneld entry            | Interface        | Connection used  | Model fields | In-use flag |
| ------------------------ | ---------------- | ---------------- | ------------ | ----------- |
| UDID-A                   | `usbmux-…-USB`   | this one         | present      | true        |
| UDID-A                   | `utun6`          | not this one     | present      | false       |
| UDID-A (recorded `utun9`) | any listed entry | none matches     | present      | false       |


<!-- @trace
source: add-device-identity-display
updated: 2026-09-18
code:
  - app.py
  - templates/index.html
  - docs/主要功能程式碼介紹.md
-->

---
### Requirement: Diagnostics reports a server address reachable from a phone

The diagnostics response SHALL carry the server address that a phone on the same network uses to reach the control interface, comprising the host address for the default route and the listening port.

The reported address SHALL be presented as the default-route address rather than as the only usable address, because the system reports one address and does not enumerate every network interface.

When the address cannot be determined, the address field SHALL be an empty string and the remaining diagnostics output SHALL still be reported.

#### Scenario: Server address accompanies the stage results

- **WHEN** the diagnostics endpoint is called
- **THEN** the response carries a server host address and the listening port

#### Scenario: An undeterminable address does not fail diagnostics

- **WHEN** the server host address cannot be determined
- **THEN** the server host address is reported as an empty string
- **AND** the four stage outcomes are still reported


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Diagnostics endpoint succeeds even when stages fail

The diagnostics endpoint SHALL respond with a success status code whenever it completes, including when every stage fails. A stage failure is normal diagnostics output, not an endpoint error.

The endpoint SHALL NOT respond with a client-error or server-error status code to signal a failed stage, because doing so leaves the front end unable to distinguish "diagnostics ran and found a problem" from "diagnostics itself is broken".

#### Scenario: Total failure still returns a success status

- **WHEN** tunneld is not running
- **AND** the diagnostics endpoint is called
- **THEN** the response status code indicates success
- **AND** the response body reports the tunneld reachability stage as failed


<!-- @trace
source: add-mobile-remote-control
updated: 2026-09-07
code:
  - docs/系統架構設計圖.md
  - static/manifest.webmanifest
  - docs/主要功能程式碼介紹.md
  - static/icons/app-icon-512.png
  - tools/make_icons.py
  - templates/index.html
  - static/icons/app-icon-180.png
  - app.py
  - docs/專案簡介.md
  - static/css/style.css
-->

---
### Requirement: Diagnostics is triggerable from the control interface

The control interface SHALL provide a control that runs diagnostics and presents each stage's display name, outcome, detail, and next action, together with the reported server address and device list.

The control's label SHALL convey that activating it attempts to establish a device connection, because the diagnostics path establishes and retains the shared connection when none exists. A label that names only diagnosis leaves the user unaware that the interface already offers a way to connect on demand, and invites a second control that would duplicate the same path while reporting less.

The diagnostics presentation SHALL distinguish the three stage states from one another visually, so that a not-run stage is not presented as a failure.

#### Scenario: Results are presented per stage

- **WHEN** the user activates the diagnostics control
- **THEN** each of the four stages is presented with its display name and outcome
- **AND** each failed stage presents its next action
- **AND** the reported server address is presented

#### Scenario: Not-run stages are visually distinct from failures

- **WHEN** diagnostics reports one failed stage and three not-run stages
- **THEN** the failed stage is presented differently from the not-run stages

#### Scenario: The control announces that it connects

- **WHEN** the user reads the diagnostics control without activating it
- **THEN** its label indicates that activating it attempts to establish a device connection


<!-- @trace
source: add-device-identity-display
updated: 2026-09-18
code:
  - app.py
  - templates/index.html
  - docs/主要功能程式碼介紹.md
-->

---