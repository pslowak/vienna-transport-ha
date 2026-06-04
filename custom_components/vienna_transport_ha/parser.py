import logging
from datetime import datetime

from custom_components.vienna_transport_ha.model import (
    Departure,
    Line,
    Stop,
    StopProperties,
    TransportData,
    Vehicle,
)

_LOGGER = logging.getLogger(__name__)

_MSG_CODE_OK = 1
_MSG_CODE_RATE_LIMIT = 316


class ViennaTransportParser:
    def parse(self, raw: dict) -> TransportData:
        try:
            msg = raw["message"]
            msg_code = msg.get("messageCode", -1)

            if msg_code == _MSG_CODE_OK:
                raw_monitors = raw.get("data", {}).get("monitors", [])
                parsed = [self._parse_stop(stop) for stop in raw_monitors]
                stops = {stop.props.id: stop for stop in parsed}
                return TransportData(stops=stops, return_code=msg_code)

            if msg_code == _MSG_CODE_RATE_LIMIT:
                return TransportData(stops={}, return_code=_MSG_CODE_RATE_LIMIT)

            _LOGGER.warning("Unexpected message code %s", msg_code)
            return TransportData(stops={}, return_code=msg_code)
        except (KeyError, TypeError, ValueError) as e:
            _LOGGER.error(f"unexpected API response {e}")
            return TransportData(stops={}, return_code=-1)

    @staticmethod
    def _parse_stop(raw: dict) -> Stop:
        props = ViennaTransportParser._parse_properties(
            raw["locationStop"]["properties"]
        )
        lines = [
            ViennaTransportParser._parse_line(line) for line in raw.get("lines", [])
        ]
        return Stop(props=props, lines=lines)

    @staticmethod
    def _parse_properties(raw: dict) -> StopProperties:
        return StopProperties(id=int(raw["attributes"]["rbl"]), name=raw["title"])

    @staticmethod
    def _parse_line(raw: dict) -> Line:
        name = raw["name"]
        departures = [
            ViennaTransportParser._parse_departure(dep)
            for dep in raw.get("departures", {}).get("departure", [])
        ]
        return Line(name=name, departures=departures)

    @staticmethod
    def _parse_departure(raw: dict) -> Departure:
        times = raw["departureTime"]
        time_planned = datetime.fromisoformat(times["timePlanned"])
        time_real = datetime.fromisoformat(times["timeReal"])
        vehicle = ViennaTransportParser._parse_vehicle(raw["vehicle"])
        return Departure(
            time_planned=time_planned, time_real=time_real, vehicle=vehicle
        )

    @staticmethod
    def _parse_vehicle(raw: dict) -> Vehicle:
        return Vehicle(name=raw["name"], type=raw["type"], towards=raw["towards"])
