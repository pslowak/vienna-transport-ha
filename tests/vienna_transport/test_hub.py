from typing import cast
from unittest.mock import MagicMock, create_autospec

import pytest
from homeassistant.core import HomeAssistant

from custom_components.vienna_transport.coordinator import ViennaTransportCoordinator
from custom_components.vienna_transport.hub import ViennaTransportHub, build_hub
from custom_components.vienna_transport.registry import StopRegistry


def make_entry(entry_id: str, stop_ids: list[str]) -> MagicMock:
    entry = MagicMock()
    entry.entry_id = entry_id
    entry.data = {"stop_ids": stop_ids}
    return entry


def make_coordinator() -> MagicMock:
    return cast(MagicMock, create_autospec(ViennaTransportCoordinator, instance=True))


@pytest.fixture
def entry() -> MagicMock:
    return make_entry("entry-1", ["2683"])


@pytest.fixture
def coordinator() -> MagicMock:
    return make_coordinator()


@pytest.fixture
def hub(coordinator: MagicMock) -> ViennaTransportHub:
    return ViennaTransportHub(StopRegistry(), coordinator)


async def test_register_entry_registers_stops_and_refreshes(
    hub: ViennaTransportHub, entry: MagicMock, coordinator: MagicMock
) -> None:
    await hub.async_register_entry(entry)
    assert hub.platform_data("entry-1").stop_ids == ["2683"]
    coordinator.async_request_refresh.assert_awaited_once()


async def test_unregister_last_entry_shuts_down(
    hub: ViennaTransportHub, entry: MagicMock, coordinator: MagicMock
) -> None:
    await hub.async_register_entry(entry)
    result = await hub.async_unregister_entry(entry)
    assert result is True
    assert hub.platform_data("entry-1").stop_ids == []
    coordinator.async_shutdown.assert_awaited_once()
    assert coordinator.async_request_refresh.await_count == 1


async def test_unregister_non_last_entry_refreshes(
    hub: ViennaTransportHub, coordinator: MagicMock
) -> None:
    await hub.async_register_entry(make_entry("entry-1", ["2683"]))
    await hub.async_register_entry(make_entry("entry-2", ["1337"]))
    assert coordinator.async_request_refresh.await_count == 2

    result = await hub.async_unregister_entry(make_entry("entry-1", ["2683"]))

    assert result is False
    assert hub.platform_data("entry-2").stop_ids == ["1337"]
    coordinator.async_shutdown.assert_not_awaited()
    assert coordinator.async_request_refresh.await_count == 3


async def test_platform_data_stop_ids_returns_copy(hub: ViennaTransportHub) -> None:
    await hub.async_register_entry(make_entry("entry-1", ["2683"]))
    result = hub.platform_data("entry-1").stop_ids
    result.append("1337")
    assert hub.platform_data("entry-1").stop_ids == ["2683"]


async def test_register_first_entry_registers_and_first_refreshes(
    hub: ViennaTransportHub, entry: MagicMock, coordinator: MagicMock
) -> None:
    await hub.async_register_first_entry(entry)
    assert hub.platform_data("entry-1").stop_ids == ["2683"]
    coordinator.async_config_entry_first_refresh.assert_awaited_once()


async def test_build_hub_wires_graph(hass: HomeAssistant) -> None:
    hub = build_hub(hass)
    assert hub.platform_data("unknown").stop_ids == []
