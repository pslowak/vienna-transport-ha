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
| Response MIME type   | `application/json`                                                                               |
| Timestamp Format     | ISO 8601 with milliseconds and an offset without a colon (e.g. `2026-11-06T11:02:25.000+0100`)   |

## Request

```http request
GET /monitor?stopId=…
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
