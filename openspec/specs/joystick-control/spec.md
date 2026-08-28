# joystick-control Specification

## Purpose

The on-screen joystick that drives continuous manual movement: that it exists at all,
that it owns its gestures, that it stays responsive, and that it remains visible.

Covers creating the joystick at page load from a library reference that resolves,
degrading to a visible message when that library is unavailable, taking exclusive
ownership of pointer, touch, and scroll gestures that begin inside the joystick
container, responsive movement that stops when the joystick is released, and the
container's visual distinctness from the map beneath it.

The joystick container is an overlay sibling of the map rather than a child of it, so
gesture ownership has to be asserted explicitly or the map claims the drag. The
joystick's position is deliberately outside the control panel — see
`control-panel-layout`.

## Requirements

### Requirement: Joystick control is created at page load

The system SHALL reference the joystick library at a URL that resolves successfully, and SHALL create the joystick control during page initialization so that the joystick is present and operable once the page has loaded.

When the joystick library is unavailable, the system SHALL display a visible message stating that the joystick is unavailable, and SHALL allow the remaining page initialization to complete. A joystick library failure SHALL NOT prevent the speed labels, the coordinate readout, the search key binding, or the multi-waypoint walk controls from working.

#### Scenario: Joystick exists and responds after page load

- **WHEN** the user loads the simulator page
- **THEN** the joystick is present in its container
- **AND** the joystick responds to being dragged
- **AND** the browser console reports no error relating to the joystick library

#### Scenario: Joystick library URL resolves

- **WHEN** a request is issued for the joystick library URL referenced by the page
- **THEN** the request succeeds rather than returning a not-found response
- **AND** loading it defines the joystick library's global object in the browser

#### Scenario: Joystick library unavailable degrades to a visible message

- **WHEN** the joystick library fails to load
- **THEN** a visible message states that the joystick is unavailable
- **AND** the automatic walk speed label shows its value
- **AND** the coordinate readout shows values
- **AND** pressing Enter in the search box performs a search
- **AND** the multi-waypoint walk controls remain operable

---
### Requirement: Joystick owns its gesture

The joystick control SHALL take exclusive ownership of pointer, touch, and scroll gestures that begin inside its container. The map beneath the joystick SHALL NOT pan, zoom, or scroll in response to a gesture that begins inside the joystick container. The joystick container SHALL declare that it does not participate in the browser's default touch gestures.

#### Scenario: Dragging the joystick does not pan the map

- **WHEN** the user presses inside the joystick container and drags
- **THEN** the joystick stick follows the pointer
- **AND** the map does not pan in response to that gesture

#### Scenario: Touch drag on the joystick does not scroll or zoom

- **WHEN** the user touches inside the joystick container and drags on a touch device
- **THEN** the joystick stick follows the touch point
- **AND** the map does not pan or zoom in response to that gesture
- **AND** the page does not scroll in response to that gesture

#### Scenario: Joystick input moves the marker continuously

- **WHEN** the user holds the joystick deflected in one direction
- **THEN** the marker moves continuously in that direction for as long as the joystick is held

---
### Requirement: Joystick movement is responsive and stops on release

While the joystick drives movement, the system SHALL follow the marker with the map without starting overlapping map animations, and the joystick container SHALL NOT apply a backdrop blur effect. Marker movement SHALL stop within one update interval after the user releases the joystick.

#### Scenario: Sustained dragging stays responsive

- **WHEN** the user drags the joystick continuously for ten seconds
- **THEN** the marker moves without perceptible stalling
- **AND** the map keeps following the marker

#### Scenario: Marker stops on release

- **WHEN** the user releases the joystick
- **THEN** marker movement stops within one update interval
- **AND** the marker does not continue drifting afterward

---
### Requirement: Joystick container remains visually distinct

The joystick container SHALL retain a translucent background so that it stays visually distinguishable from the map beneath it, and SHALL retain its existing size, position, and CSS class name.

#### Scenario: Joystick stays distinguishable from the map

- **WHEN** the user views the simulator page over map tiles of any brightness
- **THEN** the joystick container is distinguishable from the map beneath it
- **AND** the joystick occupies the same position and size as before this change
