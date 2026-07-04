import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from custom_components.vienna_transport.exceptions import ParserError
from custom_components.vienna_transport.model import Departure, TransportData, Vehicle
from custom_components.vienna_transport.parser import ViennaTransportParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict[str, Any]:
    result: dict[str, Any] = json.loads((FIXTURES_DIR / filename).read_text())
    return result


@pytest.fixture
def parser() -> ViennaTransportParser:
    return ViennaTransportParser()


def test_parse_returns_transport_data(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    result = parser.parse(raw)
    assert isinstance(result, TransportData)


def test_parse_produces_one_stop(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    result = parser.parse(raw)
    assert len(result.stops) == 1


def test_parse_stop_properties(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    stop = parser.parse(raw).stops[2683]

    assert stop.props.id == 2683
    assert stop.props.name == "Volkertplatz"


def test_parse_stop_has_one_line(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    stop = parser.parse(raw).stops[2683]
    assert len(stop.lines) == 1


def test_parse_line_name(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    line = parser.parse(raw).stops[2683].lines[0]
    assert line.name == "5B"


def test_parse_line_has_three_departures(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    line = parser.parse(raw).stops[2683].lines[0]
    assert len(line.departures) == 3


def test_parse_departure_times(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    departure = parser.parse(raw).stops[2683].lines[0].departures[0]

    tz = timezone(timedelta(hours=2))
    expected_planned = datetime(2026, 6, 3, 12, 4, 30, tzinfo=tz)
    expected_real = datetime(2026, 6, 3, 12, 5, 30, tzinfo=tz)

    assert departure.time_planned == expected_planned
    assert departure.time_real == expected_real


def test_parse_departure_falls_back_to_time_planned_when_time_real_missing(
    parser: ViennaTransportParser,
) -> None:
    raw = load_fixture("single_stop.json")
    departure = parser.parse(raw).stops[2683].lines[0].departures[1]

    assert departure.time_real == departure.time_planned


def test_parse_departure_falls_back_to_time_real_when_time_planned_missing(
    parser: ViennaTransportParser,
) -> None:
    raw = load_fixture("single_stop.json")
    departure = parser.parse(raw).stops[2683].lines[0].departures[2]

    assert departure.time_planned == departure.time_real


def test_parse_departure_raises_on_both_times_missing(
    parser: ViennaTransportParser,
) -> None:
    with pytest.raises(ParserError):
        parser._parse_departure(
            {
                "departureTime": {},
                "vehicle": {
                    "name": "5B",
                    "towards": "Bhf. Heiligenstadt S U",
                    "direction": "H",
                    "platform": "1",
                    "richtungsId": "1",
                    "barrierFree": True,
                    "cooling": True,
                    "realtimeSupported": False,
                    "trafficjam": False,
                    "type": "ptBusCity",
                    "attributes": {},
                    "linienId": 205,
                },
            }
        )


def test_parse_departure_times_are_timezone_aware(
    parser: ViennaTransportParser,
) -> None:
    raw = load_fixture("single_stop.json")
    departure: Departure = parser.parse(raw).stops[2683].lines[0].departures[0]

    assert departure.time_planned.tzinfo is not None
    assert departure.time_real.tzinfo is not None


def test_parse_cooled_vehicle(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    vehicle: Vehicle = parser.parse(raw).stops[2683].lines[0].departures[0].vehicle

    assert vehicle.name == "5B"
    assert vehicle.type == "ptBusCity"
    assert vehicle.towards == "Bhf. Heiligenstadt S U"
    assert vehicle.cooling is True


def test_parse_non_cooled_vehicle(parser: ViennaTransportParser) -> None:
    raw = load_fixture("single_stop.json")
    vehicle: Vehicle = parser.parse(raw).stops[2683].lines[0].departures[1].vehicle

    assert vehicle.name == "5B"
    assert vehicle.type == "ptBusCity"
    assert vehicle.towards == "Bhf. Heiligenstadt S U"
    assert vehicle.cooling is False


def test_parse_rate_limit_error(parser: ViennaTransportParser) -> None:
    raw = {
        "message": {"messageCode": 316, "value": "Rate limit exceeded"},
    }
    with pytest.raises(ParserError, match="rate limit"):
        parser.parse(raw)


def test_parse_unknown_code(parser: ViennaTransportParser) -> None:
    raw = {
        "message": {"messageCode": -1, "value": "Some unknown code"},
    }
    with pytest.raises(ParserError, match="Unexpected message code"):
        parser.parse(raw)


def test_parse_malformed_data(parser: ViennaTransportParser) -> None:
    raw = {
        "message": {"messageCode": 1, "value": "OK"},
        "data": {
            "monitors": [
                {"locationStop": {}}  # missing data
            ]
        },
    }
    with pytest.raises(ParserError, match="unexpected API response"):
        parser.parse(raw)
