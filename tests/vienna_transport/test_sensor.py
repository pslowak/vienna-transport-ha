from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from custom_components.vienna_transport.coordinator import (
    PlatformData,
    ViennaTransportCoordinator,
)
from custom_components.vienna_transport.model import (
    Departure,
    Line,
    Stop,
    StopProperties,
    TransportData,
    Vehicle,
)
from custom_components.vienna_transport.registry import StopRegistry
from custom_components.vienna_transport.sensor import (
    ViennaTransportSensor,
    async_setup_entry,
)


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
                            cooling=True,
                        ),
                    )
                ],
            )
        ],
    )


def make_coordinator(
    hass: HomeAssistant, data: TransportData | None
) -> ViennaTransportCoordinator:
    coordinator = ViennaTransportCoordinator(
        hass=hass,
        client=MagicMock(),
        parser=MagicMock(),
        cache=MagicMock(),
        registry=StopRegistry(),
    )
    if data is not None:
        coordinator.data = data
    return coordinator


def make_sensor(
    hass: HomeAssistant, data: TransportData | None, stop_id: int = 2683
) -> ViennaTransportSensor:
    coordinator = make_coordinator(hass, data)
    return ViennaTransportSensor(coordinator=coordinator, stop_id=stop_id)


def test_unique_id(hass: HomeAssistant) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.unique_id == "vienna_transport_2683"


def test_available_false_when_data_is_none(hass: HomeAssistant) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.available is False


def test_available_false_when_stop_not_in_data(hass: HomeAssistant) -> None:
    data = TransportData(stops={9999: make_stop(9999)})
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.available is False


def test_available_true_when_stop_in_data(hass: HomeAssistant) -> None:
    data = TransportData(stops={2683: make_stop(2683)})
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.available is True


def test_native_value_is_ok(hass: HomeAssistant) -> None:
    data = TransportData(stops={2683: make_stop()})
    sensor = make_sensor(hass, data=data)
    assert sensor.native_value == "ok"


def test_extra_state_attributes_empty_when_data_is_none(hass: HomeAssistant) -> None:
    sensor = make_sensor(hass, data=None)
    assert sensor.extra_state_attributes == {}


def test_extra_state_attributes_empty_when_stop_not_found(hass: HomeAssistant) -> None:
    data = TransportData(stops={9999: make_stop(9999)})
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.extra_state_attributes == {}


def test_sensor_only_returns_its_own_stop(hass: HomeAssistant) -> None:
    data = TransportData(
        stops={
            1337: make_stop(1337, "Schottentor"),
            2683: make_stop(2683, "Volkertplatz"),
        },
    )
    sensor = make_sensor(hass, data=data, stop_id=2683)
    assert sensor.extra_state_attributes["props"]["name"] == "Volkertplatz"


async def test_async_setup_entry_creates_one_sensor_per_stop_id(
    hass: HomeAssistant,
) -> None:
    coordinator = make_coordinator(hass, data=None)
    entry = MagicMock()
    entry.runtime_data = PlatformData(
        coordinator=coordinator, stop_ids=["2683", "1337"]
    )
    added: list[ViennaTransportSensor] = []

    def async_add_entities(
        new_entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        added.extend(cast(Iterable[ViennaTransportSensor], new_entities))

    await async_setup_entry(hass, entry, async_add_entities)
    assert len(added) == 2
    assert {sensor._stop_id for sensor in added} == {2683, 1337}
    assert all(sensor.coordinator is coordinator for sensor in added)
