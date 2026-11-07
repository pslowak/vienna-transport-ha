# Wiener Linien Realtime API

Reference for the Wiener Linien realtime API.

| Source                 | Version | Date       |
| ---------------------- | ------- | ---------- |
| Official Documentation | 1.6     | 2026-10-19 |

## Overview

The API provides real-time departures for Vienna's public transport stops for the next 70 minutes, including vehicle details and possible disruptions.

| Property             | Value                                                                                            |
|----------------------|--------------------------------------------------------------------------------------------------|
| Base URL             | `https://www.wienerlinien.at/ogd_realtime/`                                                      |
| HTTP method          | `GET`                                                                                            |
| Response MIME Type   | `application/json`                                                                               |

## Request

```http request
GET /monitor?stopId=...
```

| Parameter             | Type    | Req | Description                                                             |
|-----------------------|---------|-----|-------------------------------------------------------------------------|
| `stopId`              | integer | Yes | Stop ID. Repeatable.                                                    |
| `diva`                | integer | No  | Returns all stops with this DIVA number.                                |
| `aArea`               | integer | No  | `1` = also return all stops sharing a DIVA number with the given stops. |
| `activateTrafficInfo` | string  | No  | Disruption types to include. Repeatable. See below.                     |
| `languageId`          | string  | No  | Also return disruption texts in another language: `de` or `en`.         |

### Disruption Types

| `activateTrafficInfo` | Meaning                              |
|-----------------------|--------------------------------------|
| `stoerungkurz`        | Line-specific text shown on displays |
| `stoerunglang`        | Disruptions from the control centre  |
| `aufzugsinfo`         | Elevator outages                     |
| `fahrtreppeninfo`     | Escalator outages                    |
| `information`         | General information about a stop     |

## Message

| Field                 | Type     | Req | Description                     |
| --------------------- | -------- | --- | ------------------------------- |
| `message.value`       | string   | Yes | Description, `OK` on success.   |
| `message.messageCode` | integer  | Yes | `1` on success, else see below. |
| `message.serverTime`  | datetime | Yes | Time of the response.           |

### Message Codes

| Code  | Meaning                 |
| ----- | ----------------------- |
| `311` | Database not available  |
| `312` | Stop does not exist     |
| `316` | Request limit reached   |
| `320` | Invalid query parameter |
| `321` | Missing query parameter |
| `322` | No data in the database |

## Monitor

```
data
`-- monitors[]
    |-- locationStop
    |   |-- geometry
    |   `-- properties
    |-- lines[]
    |   `-- departures
    |       `-- departure[]
    |           |-- departureTime
    |           `-- vehicle
    |-- attributes
    `-- refTrafficInfoNames[]
message
```

The same stop ID can appear in several monitors, for example one per line.

### Monitor

The departures at a stop, grouped by line.

`monitors[]`

| Field                 | Type     | Req | Description                                     |
|-----------------------|----------|-----|-------------------------------------------------|
| `locationStop`        | object   | Yes | Information about the queried stop.             |
| `lines`               | object[] | No  | Lines at the stop.                              |
| `attributes`          | object   | Yes | Currently not populated.                        |
| `refTrafficInfoNames` | string[] | No  | Names of the disruptions linked to the monitor. |

### Location Stop

The stop's properties and location.

`monitors[].locationStop`

| Field                       | Type             | Req | Description                     |
|-----------------------------|------------------|-----|---------------------------------|
| `type`                      | string           | Yes | GeoJSON type, `Feature`.        |
| `geometry.type`             | string           | Yes | Always `Point`.                 |
| `geometry.coordinates`      | [double, double] | Yes | Longitude, latitude (WGS84).    |
| `properties.name`           | string           | Yes | DIVA number of the stop.        |
| `properties.title`          | string           | Yes | Stop name.                      |
| `properties.municipality`   | string           | Yes | City name.                      |
| `properties.municipalityId` | string           | Yes | City ID.                        |
| `properties.type`           | string           | Yes | Always `stop`.                  |
| `properties.coordName`      | string           | Yes | Always `WGS84`.                 |
| `properties.gate`           | string           | No  | Track or platform.              |
| `properties.attributes.rbl` | string           | Yes | Stop ID, as passed in `stopId`. |

### Line

A line serving the stop, with its upcoming departures.

`monitors[].lines[]`

| Field                  | Type     | Req | Description                                    |
|------------------------|----------|-----|------------------------------------------------|
| `name`                 | string   | Yes | Line name, for example `13A`.                  |
| `towards`              | string   | Yes | Destination.                                   |
| `direction`            | string   | Yes | `H` (outbound) or `R` (return).                |
| `richtungsId`          | string   | Yes | Unique direction ID.                           |
| `platform`             | string   | No  | Platform, for example `1`.                     |
| `type`                 | string   | Yes | Vehicle type, for example `ptTram`.            |
| `lineId`               | integer  | No  | Unique line ID.                                |
| `barrierFree`          | boolean  | No  | Suitable for passengers with reduced mobility. |
| `realtimeSupported`    | boolean  | No  | Real-time data generally available.            |
| `trafficjam`           | boolean  | No  | Traffic jam on the approach.                   |
| `departures.departure` | object[] | No  | Departures.                                    |

### Departure

A single departure of a line, with its planned and real-time times.

`monitors[].lines[].departures.departure[]`

| Field                       | Type     | Req | Description                                                   |
|-----------------------------|----------|-----|---------------------------------------------------------------|
| `departureTime.timePlanned` | datetime | Yes | Scheduled time.                                               |
| `departureTime.timeReal`    | datetime | No  | Predicted (real-time) time.                                   |
| `departureTime.countdown`   | integer  | Yes | Minutes until departure.                                      |
| `vehicle`                   | object   | No  | Only if it differs from the line; otherwise the line applies. |

### Vehicle

The vehicle of a departure, if it differs from the line.

`monitors[].lines[].departures.departure[].vehicle`

| Field               | Type    | Req | Description                                    |
|---------------------|---------|-----|------------------------------------------------|
| `name`              | string  | Yes | Line name.                                     |
| `towards`           | string  | Yes | Destination.                                   |
| `direction`         | string  | Yes | `H` (outbound) or `R` (return).                |
| `richtungsId`       | string  | Yes | Unique direction ID.                           |
| `type`              | string  | Yes | Vehicle type, for example `ptTram`.            |
| `linienId`          | integer | Yes | Unique line ID.                                |
| `barrierFree`       | boolean | Yes | Suitable for passengers with reduced mobility. |
| `foldingRamp`       | boolean | No  | Has a folding ramp.                            |
| `cooling`           | boolean | No  | Is air-conditioned.                            |
| `onStop`            | boolean | Yes | A metro train is at the stop.                  |
| `realtimeSupported` | boolean | Yes | Real-time data generally available.            |
| `trafficjam`        | boolean | Yes | Traffic jam on the approach.                   |

## Traffic Infos

```
data
|-- trafficInfos[]
|   |-- languages[]
|   |-- attributes
|   `-- relatedLinesDetails[]
|-- trafficInfoCategories[]
`-- trafficInfoCategoryGroups[]
```

Only sent if disruption types are requested via `activateTrafficInfo` and disruptions exist. A monitor references traffic infos by `name`, a traffic info references its category by `id`, and a category references its group by `id`.

### Traffic Info

A disruption or information affecting lines or stops.

`trafficInfos[]`

| Field                      | Type      | Req | Description                                                            |
|----------------------------|-----------|-----|------------------------------------------------------------------------|
| `name`                     | string    | Yes | Unique name, referenced by `refTrafficInfoNames`.                      |
| `parentName`               | string    | Yes | Name of the original message; equal to `name` if this is the original. |
| `refTrafficInfoCategoryId` | integer   | Yes | ID of the category.                                                    |
| `priority`                 | string    | No  | Priority.                                                              |
| `owner`                    | string    | No  | Data provider.                                                         |
| `title`                    | string    | Yes | Title.                                                                 |
| `description`              | string    | Yes | Description as plain text.                                             |
| `descriptionHTML`          | string    | Yes | Description as HTML.                                                   |
| `elevatorId`               | string    | No  | Elevator ID, only for elevator outages.                                |
| `languages`                | object[]  | No  | Texts in other languages.                                              |
| `time.start`               | datetime  | No  | Start of the disruption.                                               |
| `time.end`                 | datetime  | No  | End of the disruption.                                                 |
| `time.resume`              | datetime  | No  | Service resumes during the disruption.                                 |
| `time.created`             | datetime  | No  | Creation of the message.                                               |
| `time.lastupdate`          | datetime  | No  | Last change of the message.                                            |
| `location`                 | string    | No  | Address, if available.                                                 |
| `status`                   | string    | Yes | `active` or `resolved`.                                                |
| `pictures`                 | object[]  | No  | Links to pictures.                                                     |
| `infoChannels`             | object[]  | No  | Available output channels.                                             |
| `attributes`               | object    | No  | Additional information about a traffic info.                           |
| `relatedLines`             | string[]  | No  | Names of the affected lines.                                           |
| `relatedLinesDetails`      | object[]  | No  | Details of the affected lines.                                         |
| `relatedStops`             | integer[] | No  | IDs of the affected stops.                                             |

### Language

The texts of a traffic info in another language, keyed by language ID.

`trafficInfos[].languages[].<languageId>`

| Field              | Type   | Req | Description                |
|--------------------|--------|-----|----------------------------|
| `title`            | string | Yes | Title.                     |
| `descriptionPlain` | string | Yes | Description as plain text. |
| `descriptionHtml`  | string | Yes | Description as HTML.       |

### Attributes

Additional information about a traffic info.

`trafficInfos[].attributes`

| Field          | Type      | Req | Description                                     |
|----------------|-----------|-----|-------------------------------------------------|
| `reason`       | string    | No  | Reason of the outage.                           |
| `relatedLines` | string[]  | No  | Names of the affected lines.                    |
| `station`      | string    | No  | Affected stop.                                  |
| `location`     | string    | No  | Location of the elevator.                       |
| `towards`      | string    | No  | Direction of the line, if only one is affected. |
| `relatedStops` | integer[] | No  | IDs of the affected stops.                      |
| `status`       | string    | No  | Status, for example out of service.             |

### Related Line

An affected line with its details.

`trafficInfos[].relatedLinesDetails[]`

| Field          | Type      | Req | Description                             |
|----------------|-----------|-----|-----------------------------------------|
| `lineId`       | integer   | Yes | Unique line ID.                         |
| `lineName`     | string    | Yes | Line name, for example `13A`.           |
| `vehicleType`  | string    | Yes | Vehicle type, for example `ptTram`.     |
| `relatedStops` | integer[] | No  | IDs of the stops affected on this line. |

### Category

The category of a traffic info.

`trafficInfoCategories[]`

| Field                           | Type    | Req | Description                                                             |
|---------------------------------|---------|-----|-------------------------------------------------------------------------|
| `id`                            | integer | Yes | Unique category ID.                                                     |
| `refTrafficInfoCategoryGroupId` | integer | Yes | ID of the group.                                                        |
| `name`                          | string  | Yes | Disruption type, see [Disruption Types](#disruption-types).             |
| `trafficInfoNameList`           | string  | Yes | Comma-separated names of the linked traffic infos, e.g. `v41_2, v41_1`. |
| `title`                         | string  | Yes | Title.                                                                  |

### Category Group

The group of a category.

`trafficInfoCategoryGroups[]`

| Field  | Type    | Req | Description      |
|--------|---------|-----|------------------|
| `id`   | integer | Yes | Unique group ID. |
| `name` | string  | Yes | Always `pt`.     |
