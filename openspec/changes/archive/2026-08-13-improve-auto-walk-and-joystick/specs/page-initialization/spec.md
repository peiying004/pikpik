## ADDED Requirements

### Requirement: DOM-only initialization precedes library-dependent initialization

Initialization that depends only on the document — populating the coordinate readout and the speed labels from their controls — SHALL run before any third-party library is initialized. A third-party library failure SHALL NOT leave these values unpopulated.

#### Scenario: Readouts are populated on a fresh page load

- **WHEN** the user loads the simulator page and performs no interaction
- **THEN** the coordinate readout shows numeric latitude and longitude rather than a placeholder
- **AND** the automatic walk speed label shows a speed value

##### Example: fresh load with the default slider position

- **GIVEN** the automatic walk speed slider's markup sets its value to 18
- **AND** the marker's initial coordinates are 25.033964, 121.564468
- **WHEN** the page finishes loading and the user has clicked nothing, dragged nothing, and started no walk
- **THEN** the automatic walk speed label reads "18 km/h"
- **AND** the coordinate readout reads 25.033964 and 121.564468

#### Scenario: A failing library does not blank the readouts

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the user loads the simulator page
- **THEN** the coordinate readout still shows numeric values
- **AND** the automatic walk speed label still shows a speed value

### Requirement: Library-independent event bindings survive a library failure

Event bindings that do not depend on a third-party library — performing a search when Enter is pressed in the search box, and dismissing the search result list when the user clicks outside it — SHALL remain functional when a third-party library fails to load.

#### Scenario: Enter key search works after a library failure

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the user types a query in the search box and presses Enter
- **THEN** the search is performed

#### Scenario: Search results dismiss on outside click after a library failure

- **WHEN** a third-party library referenced by the page fails to load
- **AND** the search result list is open
- **AND** the user clicks outside the search box and the result list
- **THEN** the result list closes

### Requirement: Third-party library load failure is surfaced

When a third-party library that the page depends on fails to load, the system SHALL surface that failure to the user through visible page content naming the affected control. The system SHALL NOT fail silently, leaving the user to infer the cause from unrelated symptoms.

#### Scenario: Failure is named rather than silent

- **WHEN** a third-party library that a control depends on fails to load
- **THEN** visible page content states that the affected control is unavailable
- **AND** the user is not left with only unrelated symptoms such as a blank value or an unresponsive key
