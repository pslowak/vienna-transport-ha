from collections.abc import AsyncGenerator
from typing import Any

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.vienna_transport_ha.client import ViennaTransportClient


@pytest.fixture
async def session() -> AsyncGenerator[ClientSession, Any]:
    async with aiohttp.ClientSession() as s:
        yield s


@pytest.fixture
def client(session: aiohttp.ClientSession) -> ViennaTransportClient:
    return ViennaTransportClient(session=session)


async def test_fetch_raises_value_error_on_empty_stop_ids(
    client: ViennaTransportClient,
) -> None:
    with aioresponses() as mock:
        with pytest.raises(ValueError, match="stop_ids cannot be empty"):
            await client.fetch([])

        assert len(mock.requests) == 0


async def test_fetch_returns_json_on_200(
    client: ViennaTransportClient,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    with aioresponses() as mock:
        mock.get(
            "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=1",
            payload=payload,
        )
        result = await client.fetch(["1"])

    assert result == payload


async def test_fetch_sends_multiple_stop_ids(
    client: ViennaTransportClient,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    with aioresponses() as mock:
        mock.get(
            "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=1&stopId=2",
            payload=payload,
        )
        result = await client.fetch(["1", "2"])

    assert result == payload


async def test_fetch_raises_update_failed_on_non_200(
    client: ViennaTransportClient,
) -> None:
    with aioresponses() as mock:
        mock.get(
            "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=1", status=500
        )

        with pytest.raises(UpdateFailed, match="Unexpected HTTP status code: 500"):
            await client.fetch(["1"])


async def test_fetch_raises_update_failed_on_connection_error(
    client: ViennaTransportClient,
) -> None:
    with aioresponses() as mock:
        mock.get(
            "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=1",
            exception=aiohttp.ClientConnectionError("refused"),
        )

        with pytest.raises(UpdateFailed, match="Connection error: refused"):
            await client.fetch(["1"])


async def test_fetch_raises_update_failed_on_timeout(
    client: ViennaTransportClient,
) -> None:
    with aioresponses() as mock:
        mock.get(
            "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=1",
            exception=TimeoutError(),
        )

        with pytest.raises(UpdateFailed, match="Timeout error"):
            await client.fetch(["1"])
