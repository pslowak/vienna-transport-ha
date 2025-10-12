# Vienna Public Transport Card

A custom Lovelace card for [Home Assistant](https://www.home-assistant.io/) that displays real-time public transport 
departures in Vienna, Austria.

## Installation

### Option 1 - Manual

1. Download the latest release from the Release Page.
2. Copy `transport-card.js` into your Home Assistant `www` directory.
3. Add the resource to your Home Assistant configuration, see
[Registering Resources](https://developers.home-assistant.io/docs/frontend/custom-ui/registering-resources/)

## Setup

1. Make sure you have the [RESTful Integration](https://www.home-assistant.io/integrations/rest/) enabled.
2. Add a  REST sensor for each stop in your `configuration.yaml`:

```yaml
sensor:
  - platform: rest
    name: "Station Volkertmarkt"
    resource: "https://www.wienerlinien.at/ogd_realtime/monitor?diva=60201876"
    scan_interval: 30
    value_template: "{{ value_json.data.monitors[0].locationStop.properties.title }}"
    json_attributes_path: "$.data"
    json_attributes:
      - "monitors"
```

3. You can find the `diva` code for each stop using the [Stop Search Tool](https://till.mabe.at/rbl/).
4. Add the card to your dashboard:

```yaml
type: 'custom:transport-card'
entity: sensor.station_volkertmarkt
lines:
  - "5B" 
```

## Development

Install dependencies:
```bash
npm install
```

Build the card:
```bash
npm run build 
```

Run a development server:
```bash
npm run dev
```
