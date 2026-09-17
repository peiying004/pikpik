## MODIFIED Requirements

### Requirement: Joystick container remains visually distinct

The joystick container SHALL retain a translucent background so that it stays visually distinguishable from the map beneath it, at every viewport width. It SHALL retain its existing CSS class name at every viewport width.

In a wide viewport, the joystick container SHALL retain its existing size and position.

In a narrow viewport, the joystick's size and position are governed by `mobile-viewport-layout`, which reduces its size and places it above the control panel. The translucent background and the CSS class name SHALL be unaffected by that relocation.

#### Scenario: Joystick stays distinguishable from the map

- **WHEN** the user views the simulator page over map tiles of any brightness
- **THEN** the joystick container is distinguishable from the map beneath it

#### Scenario: Joystick keeps its size and position in a wide viewport

- **WHEN** the user views the simulator page in a wide viewport
- **THEN** the joystick occupies the same position and size as before this change

#### Scenario: Relocation in a narrow viewport preserves the background and class name

- **WHEN** the user views the simulator page in a narrow viewport
- **THEN** the joystick container retains a translucent background
- **AND** the joystick container keeps the same CSS class name it has in a wide viewport
