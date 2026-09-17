## MODIFIED Requirements

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
