# home-screen-install Specification

## Purpose

Installing the control interface onto the iOS home screen so that it launches as a
standalone app rather than as a browser tab.

Covers the web app manifest and its standalone display declaration, the start URL resolving
to the control interface, the PNG icons for the home screen and for the manifest, generating
those icons without adding a dependency, and the standalone launch presenting the same
interface as a browser visit.

iOS does not read the manifest's display field, so the standalone launch and the status bar
style are declared through apple-prefixed meta tags, and the home screen icon must be PNG
rather than SVG. The icons are produced by a repository script using only the standard
library, because adding an image-processing dependency for two flat-colour icons is out of
proportion.

## Requirements

### Requirement: A web app manifest is served

The system SHALL serve a web app manifest as valid JSON from a stable path under the static assets, and the page SHALL reference it from the document head.

The manifest SHALL declare the application name, a short name, a standalone display mode, a start URL, a background colour, a theme colour, and an icon list.

#### Scenario: Manifest is retrievable and valid

- **WHEN** the manifest path is requested from the server
- **THEN** the response is retrieved successfully
- **AND** the body parses as JSON
- **AND** the parsed object declares a name, a short name, a display mode, a start URL, a background colour, a theme colour, and an icon list

#### Scenario: Page references the manifest

- **WHEN** the simulator page is served
- **THEN** the document head contains a manifest reference resolving to the served manifest path


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
### Requirement: The manifest declares standalone display

The manifest SHALL declare a standalone display mode so that a launch from the home screen presents the page without browser navigation controls.

The manifest's start URL SHALL resolve to the simulator page itself, so that a home screen launch opens the control interface rather than a subordinate path.

#### Scenario: Standalone display is declared

- **WHEN** the served manifest is parsed
- **THEN** its display mode is standalone

#### Scenario: Start URL opens the control interface

- **WHEN** the served manifest is parsed
- **AND** its start URL is requested from the server
- **THEN** the simulator page is returned


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
### Requirement: An iOS home screen icon is provided

The system SHALL provide a 180 by 180 pixel PNG icon for the iOS home screen, and the page SHALL reference it from the document head using the iOS home screen icon relation.

The system SHALL provide a 512 by 512 pixel PNG icon and the manifest icon list SHALL reference it.

Both icons SHALL be PNG. SVG SHALL NOT be used for the iOS home screen icon, because iOS does not accept it for that purpose.

#### Scenario: iOS icon is retrievable and referenced

- **WHEN** the simulator page is served
- **THEN** the document head contains an iOS home screen icon reference
- **AND** the referenced path returns a PNG image when requested from the server

#### Scenario: Manifest icon is retrievable

- **WHEN** the served manifest is parsed
- **THEN** each path in its icon list returns a PNG image when requested from the server

##### Example: required icon assets

| Icon purpose | Pixel dimensions | Format | Referenced from |
| ------------ | ---------------- | ------ | --------------- |
| iOS home screen | 180 by 180 | PNG | document head |
| manifest icon | 512 by 512 | PNG | manifest icon list |


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
### Requirement: Icons are generated without adding dependencies

The icon files SHALL be produced by a repository script that uses only the Python standard library. The system SHALL NOT add an image-processing dependency to produce them.

The script SHALL be re-runnable and SHALL overwrite the icon files it produces, so that regenerating the icons does not require deleting them first.

#### Scenario: Generation script uses only the standard library

- **WHEN** the icon generation script is inspected for its imports
- **THEN** every imported module belongs to the Python standard library

#### Scenario: Generation script produces both icons

- **WHEN** the icon generation script is run in a checkout where the icon files are absent
- **THEN** the 180 pixel icon and the 512 pixel icon are both created
- **AND** each created file is a PNG of its declared pixel dimensions

#### Scenario: Re-running the script overwrites existing icons

- **WHEN** the icon files already exist
- **AND** the icon generation script is run
- **THEN** the script completes successfully
- **AND** both icon files are present with their declared pixel dimensions


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
### Requirement: Standalone launch presents the full control interface

When launched from the iOS home screen in standalone mode, the page SHALL present the same control interface as a browser visit, including the map, the control panel, the joystick, the status bar, and the diagnostics control.

The document head SHALL declare the iOS standalone web app capability and a status bar style, so that the standalone launch does not reserve space for browser navigation controls.

#### Scenario: Standalone launch shows every interface element

- **WHEN** the page is launched from the iOS home screen in standalone mode
- **THEN** the map, the control panel, the joystick, the status bar, and the diagnostics control are all present

#### Scenario: Standalone capability is declared

- **WHEN** the simulator page is served
- **THEN** the document head declares the iOS standalone web app capability
- **AND** the document head declares a status bar style

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