## MODIFIED Requirements

### Requirement: Diagnostics reports a server address reachable from a phone

The diagnostics response SHALL carry the server address that a phone on the same network uses to reach the control interface, comprising the host address for the default route and the listening port.

The reported address SHALL be presented as the default-route address rather than as the only usable address, because the system reports one address and does not enumerate every network interface.

When the reported address falls inside the subnet that iOS reserves for Personal Hotspot, the response SHALL additionally carry a caveat and a next action for that address. A Mac holding an address in that subnet is a client of a phone's hotspot, and the phone hosting the hotspot does not route to its own clients, so the address cannot be opened on that phone — which is the very phone the instruction is addressed to. Without the caveat the diagnostics hands the user an instruction that cannot succeed, while every probe stage that fails already carries a next action.

The caveat SHALL state the subnet as a fact rather than assert the network topology, because a router could use the same private range; a statement about the subnet stays true under that misdetection, whereas a statement about the user's topology would not. For the same reason the system SHALL decide this from the address alone and SHALL NOT read the default gateway.

The address itself SHALL still be reported when the caveat applies, because a third device on the same hotspot can reach it. The caveat and the next action are additional fields, not a replacement.

When the address falls outside that subnet, or cannot be determined, these two fields SHALL be absent rather than empty.

When the address cannot be determined, the address field SHALL be an empty string and the remaining diagnostics output SHALL still be reported.

#### Scenario: Server address accompanies the stage results

- **WHEN** the diagnostics endpoint is called
- **THEN** the response carries a server host address and the listening port

#### Scenario: An undeterminable address does not fail diagnostics

- **WHEN** the server host address cannot be determined
- **THEN** the server host address is reported as an empty string
- **AND** the four stage outcomes are still reported
- **AND** no hotspot caveat accompanies it

#### Scenario: A hotspot address carries a caveat and a next action

- **WHEN** the reported address falls inside the subnet iOS reserves for Personal Hotspot
- **THEN** the response carries a caveat for that address and a next action
- **AND** the address itself is still reported
- **AND** the caveat states which subnet the address belongs to rather than asserting that a hotspot is in use

#### Scenario: An ordinary address is unaffected

- **WHEN** the reported address falls outside that subnet
- **THEN** no caveat and no next action accompany the address
- **AND** the rest of the diagnostics output is unchanged

##### Example: which addresses carry the caveat

| Reported address | Caveat  | Notes                                   |
| ---------------- | ------- | --------------------------------------- |
| `172.20.10.7`    | present | inside the reserved subnet              |
| `172.20.10.0`    | present | lower boundary of the reserved subnet   |
| `172.20.10.15`   | present | upper boundary of the reserved subnet   |
| `172.20.10.16`   | absent  | just outside the reserved subnet        |
| `172.20.11.1`    | absent  | different subnet                        |
| `192.168.1.5`    | absent  | ordinary home network                   |
| `` (empty)       | absent  | address could not be determined         |
