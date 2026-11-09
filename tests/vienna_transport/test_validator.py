import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import custom_components.vienna_transport as integration
from custom_components.vienna_transport.exceptions import ValidationError
from custom_components.vienna_transport.validator import ViennaTransportValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict[str, Any]:
    result: dict[str, Any] = json.loads((FIXTURES_DIR / filename).read_text())
    return result


def monitor(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = raw["data"]["monitors"][0]
    return result


def line(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = monitor(raw)["lines"][0]
    return result


def departure(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = line(raw)["departures"]["departure"][0]
    return result


def with_traffic_info(raw: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    info = {"name": "ftazS_566", "description": "Elevator out of service"}
    raw["data"]["trafficInfos"] = [{**info, **overrides}]
    return raw


@pytest.fixture
def validator() -> ViennaTransportValidator:
    return ViennaTransportValidator()


@pytest.fixture
def raw() -> dict[str, Any]:
    return load_fixture("single_stop.json")


def test_manifest_declares_pydantic() -> None:
    manifest_path = Path(integration.__file__).parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert any(req.startswith("pydantic") for req in manifest["requirements"])


def test_validate_accepts_fixture(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    validator.validate([raw])


def test_validate_accepts_empty_list(validator: ViennaTransportValidator) -> None:
    validator.validate([])


def test_validate_does_not_modify_response(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    original = copy.deepcopy(raw)
    validator.validate([raw])
    assert raw == original


@pytest.mark.parametrize("code", [-1, 311, 312, 316, 320, 321, 322])
def test_validate_passes_through_non_ok_response(
    validator: ViennaTransportValidator, code: int
) -> None:
    validator.validate([{"message": {"messageCode": code, "value": "Some error"}}])


def test_validate_does_not_check_data_of_non_ok_response(
    validator: ViennaTransportValidator,
) -> None:
    validator.validate([{"message": {"messageCode": 316}, "data": {"monitors": "x"}}])


def test_validate_passes_through_missing_message_code(
    validator: ViennaTransportValidator,
) -> None:
    validator.validate([{"message": {}}])


def test_validate_accepts_ok_response_without_data(
    validator: ViennaTransportValidator,
) -> None:
    validator.validate([{"message": {"messageCode": 1}}])


def test_validate_accepts_unknown_fields(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    departure(raw)["vehicle"]["someNewField"] = "value"
    validator.validate([raw])


def test_validate_accepts_departure_without_vehicle(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    del departure(raw)["vehicle"]
    validator.validate([raw])


def test_validate_accepts_vehicle_without_cooling(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    del departure(raw)["vehicle"]["cooling"]
    validator.validate([raw])


@pytest.mark.parametrize("key", ["timePlanned", "timeReal"])
def test_validate_accepts_one_missing_time(
    validator: ViennaTransportValidator, raw: dict[str, Any], key: str
) -> None:
    del departure(raw)["departureTime"][key]
    validator.validate([raw])


def test_validate_accepts_rbl_as_string(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    monitor(raw)["locationStop"]["properties"]["attributes"]["rbl"] = "2683"
    validator.validate([raw])


def test_validate_accepts_monitors_with_same_rbl(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    raw["data"]["monitors"].append(copy.deepcopy(monitor(raw)))
    validator.validate([raw])


def test_validate_accepts_missing_collections(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    del line(raw)["departures"]
    validator.validate([raw])
    del monitor(raw)["lines"]
    validator.validate([raw])


def test_validate_accepts_tolerated_nulls(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    monitor(raw)["refTrafficInfoNames"] = None
    raw["data"]["trafficInfos"] = None
    validator.validate([raw])


@pytest.mark.parametrize(
    "overrides",
    [
        {"attributes": None},
        {"attributes": {"reason": None}},
        {"attributes": {"reason": "Out of order"}},
        {"relatedLines": ["5B"]},
    ],
)
def test_validate_accepts_traffic_info_variants(
    validator: ViennaTransportValidator,
    raw: dict[str, Any],
    overrides: dict[str, Any],
) -> None:
    validator.validate([with_traffic_info(raw, **overrides)])


def _delete(container: dict[str, Any], key: str) -> None:
    del container[key]


@pytest.mark.parametrize(
    ("mutate", "path"),
    [
        (
            lambda r: _delete(monitor(r), "locationStop"),
            "data.monitors.0.locationStop",
        ),
        (
            lambda r: _delete(monitor(r)["locationStop"]["properties"], "title"),
            "data.monitors.0.locationStop.properties.title",
        ),
        (
            lambda r: _delete(
                monitor(r)["locationStop"]["properties"]["attributes"], "rbl"
            ),
            "data.monitors.0.locationStop.properties.attributes.rbl",
        ),
        (
            lambda r: _delete(line(r), "name"),
            "data.monitors.0.lines.0.name",
        ),
        (
            lambda r: line(r).update(name=5),
            "data.monitors.0.lines.0.name",
        ),
        (
            lambda r: _delete(line(r), "towards"),
            "data.monitors.0.lines.0.towards",
        ),
        (
            lambda r: _delete(line(r), "type"),
            "data.monitors.0.lines.0.type",
        ),
        (
            lambda r: line(r).update(departures=None),
            "data.monitors.0.lines.0.departures",
        ),
        (
            lambda r: _delete(departure(r), "departureTime"),
            "data.monitors.0.lines.0.departures.departure.0.departureTime",
        ),
        (
            lambda r: departure(r).update(departureTime=None),
            "data.monitors.0.lines.0.departures.departure.0.departureTime",
        ),
        (
            lambda r: departure(r).update(departureTime={}),
            "data.monitors.0.lines.0.departures.departure.0.departureTime",
        ),
        (
            lambda r: departure(r)["departureTime"].update(
                timePlanned="2026-06-03T12:04:30"
            ),
            "data.monitors.0.lines.0.departures.departure.0.departureTime.timePlanned",
        ),
        (
            lambda r: departure(r)["vehicle"].update(towards=None),
            "data.monitors.0.lines.0.departures.departure.0.vehicle.towards",
        ),
        (
            lambda r: departure(r)["vehicle"].update(cooling=None),
            "data.monitors.0.lines.0.departures.departure.0.vehicle.cooling",
        ),
        (
            lambda r: departure(r)["vehicle"].update(cooling="true"),
            "data.monitors.0.lines.0.departures.departure.0.vehicle.cooling",
        ),
        (
            lambda r: _delete(departure(r)["vehicle"], "type"),
            "data.monitors.0.lines.0.departures.departure.0.vehicle.type",
        ),
    ],
)
def test_validate_raises_with_field_path(
    validator: ViennaTransportValidator,
    raw: dict[str, Any],
    mutate: Callable[[dict[str, Any]], None],
    path: str,
) -> None:
    mutate(raw)
    with pytest.raises(ValidationError, match="unexpected API response") as exc_info:
        validator.validate([raw])
    assert f": {path}: " in str(exc_info.value)
    assert "\n" not in str(exc_info.value)


def test_validate_raises_on_none_data(validator: ViennaTransportValidator) -> None:
    with pytest.raises(ValidationError, match="unexpected API response: data: "):
        validator.validate([{"message": {"messageCode": 1}, "data": None}])


def test_validate_raises_on_string_message_code(
    validator: ViennaTransportValidator,
) -> None:
    with pytest.raises(
        ValidationError, match="unexpected API response: message.messageCode: "
    ):
        validator.validate([{"message": {"messageCode": "1"}}])


def test_validate_raises_on_malformed_message(
    validator: ViennaTransportValidator,
) -> None:
    with pytest.raises(ValidationError, match="unexpected API response: message: "):
        validator.validate([{"message": "oops"}])


def test_validate_raises_on_missing_message(
    validator: ViennaTransportValidator,
) -> None:
    with pytest.raises(ValidationError, match="unexpected API response: message: "):
        validator.validate([{}])


def test_validate_raises_on_non_dict_batch(
    validator: ViennaTransportValidator,
) -> None:
    not_a_dict: Any = ["not", "a", "dict"]
    with pytest.raises(ValidationError, match="unexpected API response: response: "):
        validator.validate([not_a_dict])


def test_validate_raises_on_any_invalid_batch(
    validator: ViennaTransportValidator, raw: dict[str, Any]
) -> None:
    with pytest.raises(ValidationError):
        validator.validate([raw, {"message": "oops"}])


@pytest.mark.parametrize(
    ("overrides", "path"),
    [
        ({"description": None}, "data.trafficInfos.0.description"),
        ({"relatedLines": None}, "data.trafficInfos.0.relatedLines"),
        ({"attributes": "oops"}, "data.trafficInfos.0.attributes"),
    ],
)
def test_validate_raises_on_malformed_traffic_info(
    validator: ViennaTransportValidator,
    raw: dict[str, Any],
    overrides: dict[str, Any],
    path: str,
) -> None:
    with pytest.raises(ValidationError, match=path):
        validator.validate([with_traffic_info(raw, **overrides)])
