<h1 align="center">Vienna Public Transport</h1>

<p align="center"><em>Real-time departures for Vienna's public transport, right on your Home Assistant dashboard.</em></p>

[![GitHub Release](https://img.shields.io/github/v/release/pslowak/vienna-transport-ha)](https://github.com/pslowak/vienna-transport-ha/releases/latest)
[![Marketplace](https://img.shields.io/badge/Marketplace-Custom-orange.svg)](https://www.home-assistant.io/integrations/marketplace/)
[![codecov](https://codecov.io/gh/pslowak/vienna-transport-ha/branch/main/graph/badge.svg)](https://codecov.io/gh/pslowak/vienna-transport-ha)
[![backend tests](https://github.com/pslowak/vienna-transport-ha/actions/workflows/be-test.yml/badge.svg)](https://github.com/pslowak/vienna-transport-ha/actions/workflows/be-test.yml)

A custom integration and Lovelace card for [Home Assistant](https://www.home-assistant.io/) that displays real-time public transport departures in Vienna, Austria (Wiener Linien).

 <p align="center">
  <img src="docs/images/phone-departures.png" alt="Mobile View Departures" width="250">
  &nbsp;&nbsp;
  <img src="docs/images/phone-config.png" alt="Mobile View Configuration" width="250">
  &nbsp;&nbsp;
  <img src="docs/images/phone-setup.png" alt="Mobile View Setup" width="250">
</p>

## Features

- **Live departures** from Wiener Linien
- **Delay indicator** - know exactly which departure is running late and by how much
- **Cooling indicator** - know exactly which vehicles are air-conditioned
- **Elevator disruptions** - know which elevators at your stop are out of service
- **Guided setup** - find your stop by line and direction (no lookup of IDs needed)
- **Auto-registered Lovelace card** - no manual resource setup
- **One sensor per stop** - multiple stops per config entry

## Installation

### Marketplace (recommended)

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=pslowak&repository=vienna-transport-ha&category=integration)

Or add it manually:

1. Go to **Settings → Marketplace** and select **Add from link**.
2. Enter `https://github.com/pslowak/vienna-transport-ha` and select **Add**. If you haven't connected GitHub yet, Home Assistant asks you to sign in first.
3. Open *Vienna Public Transport* and select **Install**.

On Home Assistant 2026.10, use HACS instead: go to **HACS → Custom repositories**, add the repository URL (category: **Integration**), download it and restart Home Assistant.

### Manual

1. Download `vienna-transport.zip` from the [latest release](https://github.com/pslowak/vienna-transport-ha/releases/latest) and unpack it.
2. Copy `custom_components/vienna_transport/` into your `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for *Vienna Public Transport* and select it.
3. Choose how to find the stop you want to monitor:
   - **Find stop by line**: pick a line, its direction and the stop. Adds one stop.
   - **Enter stop ID**: enter one or more **RBL stop IDs**. You can find stop IDs via the [RBL search](https://till.mabe.at/rbl/).
4. A sensor entity (e.g. `sensor.vienna_transport_departures_for_stop_2683`) is created for each stop ID.
5. If the card does not appear in the Lovelace card picker, **clear your browser cache**.

A stop ID stands for a platform, so its sensor shows all lines departing there. Use the card's `lines` option to show only some of them.

## Lovelace Card

Add the card to your dashboard:

```yaml
type: 'custom:transport-card'
entity: sensor.vienna_transport_departures_for_stop_2683
max_departures: 3
```

### Options

| Option               | Type    | Required | Default | Description                          |
|:---------------------|:--------|:---------|:--------|:-------------------------------------|
| `type`               | string  | required | -       | Must be `custom:transport-card`      |
| `entity`             | string  | required | -       | Sensor entity ID                     |
| `lines`              | array   | optional | all     | List of lines to show                |
| `max_departures`     | number  | optional | all     | Maximum number of departures to show |
| `show_traffic_infos` | boolean | optional | `true`  | Show elevator notices                |

## Development

### Backend (Python)

```bash
uv sync --extra dev                   # Install dependencies
uv run pytest                         # Run tests
uv run ruff check                     # Linting
uv run mypy                           # Type checking
uv run scripts/build_stop_list.py     # Build the stop list
```

The stop list is built from Wiener Linien open data into `custom_components/vienna_transport/data/stops.csv`. 
It is not committed, but built as part of each release.

### Frontend (Lovelace card)

```bash
npm install                   # Install dependencies
npm run dev                   # Development server
npm run build                 # Build the card
npm run build:release         # Build the card for release
npm run test                  # Run tests
```

## Data Source

Departures and the stop list are based on open data from Wiener Linien, published by the City of Vienna under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Data source: City of Vienna – [data.wien.gv.at](https://data.wien.gv.at)
