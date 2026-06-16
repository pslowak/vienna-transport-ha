from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from custom_components.vienna_transport.coordinator import ViennaTransportCoordinator
from custom_components.vienna_transport.model import (
    Departure,
    Line,
    Stop,
    StopProperties,
    TransportData,
    Vehicle,
)
from custom_components.vienna_transport.sensor import ViennaTransportSensor


def make_stop(rbl: int = 2683, name: str = "Volkertplatz") -> Stop:
    tz = timezone(timedelta(hours=2))

    return Stop(
        props=StopProperties(id=rbl, name=name),
        lines=[
            Line(
                name="5B",
                departures=[
                    Departure(
                        time_planned=datetime(2026, 6, 2, 13, 14, 30, tzinfo=tz),
                        time_real=datetime(2026, 6, 2, 13, 15, 45, tzinfo=tz),
                        vehicle=Vehicle(
                            name="5B",
                            type="ptBusCity",
                            towards="Bhf. Heiligenstadt S U",
                        ),
                    )
                ],
            )
        ],
    )


def make_coordinator(hass, data: TransportData | None) -> ViennaTransportCoordinator:
    coordinator = ViennaTransportCoordinator(
        hass=hass,
        stop_ids=["2683"],
        client=MagicMock(),
        parser=MagicMock(),
    )
    coordinator.data = data
    return coordinator


def make_sensor(
    hass, data: TransportData | None, stop_id: int = 2683
) -> ViennaTransportSensor:
    coordinator = make_coordinator(hass, data)
    return ViennaTransportSensor(coordinator=coordinator, stop_id=stop_id)


def test_unique_id(hass) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.unique_id == "vienna_transport_2683"


def test_available_false_when_data_is_none(hass) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.available is False


def test_available_false_when_stop_not_in_data(hass) -> None:
    data = TransportData(stops={9999: make_stop(9999)}, return_code=1)
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.available is False


def test_available_true_when_stop_in_data(hass) -> None:
    data = TransportData(stops={2683: make_stop(2683)}, return_code=1)
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.available is True


def test_native_value_is_ok(hass) -> None:
    data = TransportData(stops={2683: make_stop()}, return_code=1)
    sensor = make_sensor(hass, data=data)
    assert sensor.native_value == "ok"


def test_extra_state_attributes_empty_when_data_is_none(hass) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.extra_state_attributes == {}


def test_extra_state_attributes_empty_when_stop_not_found(hass) -> None:
    data = TransportData(stops={9999: make_stop(9999)}, return_code=1)
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.extra_state_attributes == {}


def test_sensor_only_returns_its_own_stop(hass) -> None:
    data = TransportData(
        stops={
            1337: make_stop(1337, "Schottentor"),
            2683: make_stop(2683, "Volkertplatz"),
        },
        return_code=1,
    )
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.extra_state_attributes["props"]["name"] == "Volkertplatz"
