"""Parser for Wiener Linien API responses."""

import logging
from datetime import datetime
from typing import Any

from custom_components.vienna_transport.exceptions import ParserError
from custom_components.vienna_transport.model import (
    Departure,
    Line,
    Stop,
    StopProperties,
    TrafficInfo,
    TrafficInfoCategory,
    TransportData,
    Vehicle,
)

_LOGGER = logging.getLogger(__name__)

_MSG_CODE_OK = 1
_MSG_CODE_RATE_LIMIT = 316
_MSG_CODE_DB_UNAVAILABLE = 311
_MSG_CODE_STOP_NOT_FOUND = 312
_MSG_CODE_INVALID_PARAM = 320
_MSG_CODE_MISSING_PARAM = 321
_MSG_CODE_NO_DATA = 322
_MSG_CODE_UNKNOWN = -1


class ViennaTransportParser:
    """Parser for transforming raw API data into transport models."""

    def parse(self, raw_batches: list[dict[str, Any]]) -> TransportData:
        """Parse batched raw API responses into transport data.

        Args:
            raw_batches: Raw JSON responses from Wiener Linien monitor API,
                one per batch.

        Returns:
            Merged transport data across all batches.

        Raises:
            ParserError: If raw_batches is empty or any batch fails.

        """
        if not raw_batches:
            raise ParserError("No API responses to parse")

        _LOGGER.debug("Parsing %d batch(es)", len(raw_batches))
        stops: dict[int, Stop] = {}
        for index, raw in enumerate(raw_batches, start=1):
            _LOGGER.debug("Parsing batch %d/%d", index, len(raw_batches))
            stops.update(self._parse_one(raw).stops)

        _LOGGER.debug(
            "Parsed %d stop(s) from %d batch(es)", len(stops), len(raw_batches)
        )
        return TransportData(stops=stops)

    @staticmethod
    def _parse_one(raw: dict[str, Any]) -> TransportData:
        try:
            msg_code = raw["message"].get("messageCode", _MSG_CODE_UNKNOWN)

            if msg_code == _MSG_CODE_OK:
                data = raw.get("data", {})
                raw_monitors = data.get("monitors", [])

                stops = [
                    ViennaTransportParser._parse_stop(stop) for stop in raw_monitors
                ]

                raw_traffic_info_by_name = {
                    item["name"]: item for item in data.get("trafficInfos", []) or []
                }
                for stop, monitor in zip(stops, raw_monitors, strict=True):
                    refs = monitor.get("refTrafficInfoNames", []) or []
                    ViennaTransportParser._attach_traffic_infos(
                        stop, refs, raw_traffic_info_by_name
                    )

                return TransportData(stops={stop.props.id: stop for stop in stops})

            if msg_code == _MSG_CODE_RATE_LIMIT:
                _LOGGER.warning("API rate limit reached (message code %s)", msg_code)
                raise ParserError(f"API rate limit reached (message code {msg_code})")

            if msg_code == _MSG_CODE_DB_UNAVAILABLE:
                _LOGGER.warning("API unavailable (message code %s)", msg_code)
                raise ParserError(f"API unavailable (message code {msg_code})")

            if msg_code == _MSG_CODE_STOP_NOT_FOUND:
                _LOGGER.warning("Stop not found (message code %s)", msg_code)
                raise ParserError(f"Stop not found (message code {msg_code})")

            if msg_code == _MSG_CODE_INVALID_PARAM:
                _LOGGER.warning("Invalid query parameter (message code %s)", msg_code)
                raise ParserError(f"Invalid query parameter (message code {msg_code})")

            if msg_code == _MSG_CODE_MISSING_PARAM:
                _LOGGER.warning("Missing query parameter (message code %s)", msg_code)
                raise ParserError(f"Missing query parameter (message code {msg_code})")

            if msg_code == _MSG_CODE_NO_DATA:
                _LOGGER.warning("No data in API (message code %s)", msg_code)
                raise ParserError(f"No data in API (message code {msg_code})")

            _LOGGER.warning("Unexpected message code %s", msg_code)
            raise ParserError(f"Unexpected message code {msg_code}")
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            _LOGGER.warning("Unexpected API response %s", e)
            _LOGGER.debug("API response raw: %s", raw)
            raise ParserError(f"unexpected API response: {e}") from e

    @staticmethod
    def _parse_stop(raw: dict[str, Any]) -> Stop:
        props = ViennaTransportParser._parse_stop_properties(
            raw["locationStop"]["properties"]
        )
        lines = [
            ViennaTransportParser._parse_line(line) for line in raw.get("lines", [])
        ]
        return Stop(props=props, lines=lines, traffic_infos=[])

    @staticmethod
    def _attach_traffic_infos(
        stop: Stop, refs: list[str], info_by_name: dict[str, dict[str, Any]]
    ) -> None:
        for ref in dict.fromkeys(refs):
            info_raw = info_by_name.get(ref)
            if info_raw is not None:
                info = ViennaTransportParser._parse_traffic_info(info_raw)
                target_lines = [
                    line
                    for line in stop.lines
                    if line.name in info_raw.get("relatedLines", [])
                ]

                if not target_lines:
                    stop.traffic_infos.append(info)
                else:
                    for line in target_lines:
                        line.traffic_infos.append(info)

    @staticmethod
    def _parse_traffic_info(raw: dict[str, Any]) -> TrafficInfo:
        description = raw["description"]
        reason = (raw.get("attributes", {}) or {}).get("reason", "")
        if reason:
            description = f"{description} - {reason}"
        return TrafficInfo(
            description=description, category=TrafficInfoCategory.ELEVATOR
        )

    @staticmethod
    def _parse_stop_properties(raw: dict[str, Any]) -> StopProperties:
        return StopProperties(id=int(raw["attributes"]["rbl"]), name=raw["title"])

    @staticmethod
    def _parse_line(raw: dict[str, Any]) -> Line:
        name = raw["name"]
        departures = [
            ViennaTransportParser._parse_departure(dep)
            for dep in raw.get("departures", {}).get("departure", [])
        ]
        return Line(name=name, departures=departures, traffic_infos=[])

    @staticmethod
    def _parse_departure(raw: dict[str, Any]) -> Departure:
        times = raw["departureTime"]
        planned_raw = times.get("timePlanned")
        real_raw = times.get("timeReal")

        time_planned = (
            datetime.fromisoformat(planned_raw) if planned_raw is not None else None
        )
        time_real = datetime.fromisoformat(real_raw) if real_raw is not None else None
        time_planned = time_planned or time_real
        time_real = time_real or time_planned
        if time_planned is None or time_real is None:
            raise ParserError("Both timePlanned and timeReal are missing")

        vehicle = ViennaTransportParser._parse_vehicle(raw["vehicle"])
        return Departure(
            time_planned=time_planned, time_real=time_real, vehicle=vehicle
        )

    @staticmethod
    def _parse_vehicle(raw: dict[str, Any]) -> Vehicle:
        name = raw["name"]
        vehicle_type = raw["type"]
        towards = raw["towards"]
        cooling = raw.get("cooling", False)
        return Vehicle(name=name, type=vehicle_type, towards=towards, cooling=cooling)
