import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aiohttp import ClientSession
from aiointercept import CallbackResult, aiointercept

from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.exceptions import ClientError

_API_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"


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
    with pytest.raises(ValueError, match="stop_ids cannot be empty"):
        await client.fetch([])


async def test_fetch_returns_json_on_200(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1", payload=payload)
        result = await client.fetch(["1"])

    assert result == [payload]


async def test_fetch_raises_on_403(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(
            f"{_API_URL}?stopId=1",
            status=403,
            payload={"message": {"messageCode": 316}},
        )

        with pytest.raises(ClientError, match="Unexpected HTTP status code: 403"):
            await client.fetch(["1"])


async def test_fetch_raises_client_error_on_non_200(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1", status=500)

        with pytest.raises(ClientError, match="Unexpected HTTP status code: 500"):
            await client.fetch(["1"])


async def test_fetch_sends_multiple_stop_ids(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1&stopId=2", payload=payload)
        result = await client.fetch(["1", "2"])

    assert result == [payload]


async def test_fetch_raises_update_failed_on_connection_error(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1", exception=True)

        with pytest.raises(ClientError, match="HTTP client error"):
            await client.fetch(["1"])


async def test_fetch_raises_update_failed_on_timeout(
    client: ViennaTransportClient,
    socket_enabled: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import custom_components.vienna_transport.client as client_mod

    monkeypatch.setattr(
        client_mod, "_REQUEST_TIMEOUT", aiohttp.ClientTimeout(total=0.1)
    )

    async def _slow_handler(
        url: str,
        **kwargs: Any,
    ) -> CallbackResult:
        await asyncio.sleep(0.2)
        return CallbackResult(status=200)

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1", callback=_slow_handler)

        with pytest.raises(ClientError, match="Timeout error"):
            await client.fetch(["1"])


async def test_fetch_raises_client_error_on_invalid_json() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    with (
        patch.object(
            client,
            "_fetch_raw",
            new=AsyncMock(
                side_effect=json.JSONDecodeError("Expecting value", "doc", 0)
            ),
        ),
        pytest.raises(ClientError, match="Invalid JSON response"),
    ):
        await client.fetch(["1"])


async def test_fetch_raises_client_error_on_content_type_error() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    with (
        patch.object(
            client,
            "_fetch_raw",
            new=AsyncMock(
                side_effect=aiohttp.ContentTypeError(
                    MagicMock(), history=(), message="not json"
                )
            ),
        ),
        pytest.raises(ClientError, match="Invalid JSON response"),
    ):
        await client.fetch(["1"])


async def test_fetch_raises_client_error_on_generic_client_error() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    with (
        patch.object(
            client, "_fetch_raw", new=AsyncMock(side_effect=aiohttp.ClientError("boom"))
        ),
        pytest.raises(ClientError, match="HTTP client error"),
    ):
        await client.fetch(["1"])


async def test_fetch_single_batch_when_within_limit(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}
    stop_ids = ["1", "2", "3", "4", "5"]
    query = "&".join(f"stopId={s}" for s in stop_ids)

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?{query}", payload=payload)
        result = await client.fetch(stop_ids)

    assert result == [payload]


async def test_fetch_returns_one_response_per_batch(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload_1 = {
        "message": {"messageCode": 1},
        "data": {"monitors": [{"id": 1}]},
    }
    payload_2 = {
        "message": {"messageCode": 1},
        "data": {"monitors": [{"id": 2}]},
    }

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(
            f"{_API_URL}?stopId=1&stopId=2&stopId=3&stopId=4&stopId=5",
            payload=payload_1,
        )
        mock.get(f"{_API_URL}?stopId=6", payload=payload_2)
        result = await client.fetch(["1", "2", "3", "4", "5", "6"])

    assert result == [payload_1, payload_2]


async def test_fetch_dedupes_stop_ids(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(f"{_API_URL}?stopId=1&stopId=2", payload=payload)
        result = await client.fetch(["1", "2", "1", "2"])

    assert result == [payload]


async def test_fetch_fail_fast_on_batch_error(
    client: ViennaTransportClient,
    socket_enabled: None,
) -> None:
    payload = {"message": {"messageCode": 1}, "data": {"monitors": []}}

    async with aiointercept(mock_external_urls=True) as mock:
        mock.get(
            f"{_API_URL}?stopId=1&stopId=2&stopId=3&stopId=4&stopId=5",
            payload=payload,
        )
        mock.get(f"{_API_URL}?stopId=6", status=500)

        with pytest.raises(ClientError, match="Unexpected HTTP status code: 500"):
            await client.fetch(["1", "2", "3", "4", "5", "6"])


async def test_fetch_maps_unexpected_batch_error_to_client_error() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    with (
        patch.object(
            client, "_fetch_raw", new=AsyncMock(side_effect=RuntimeError("boom"))
        ),
        pytest.raises(ClientError, match="Unexpected batch error"),
    ):
        await client.fetch(["1"])


async def test_fetch_bounds_concurrent_requests() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    state: dict[str, int] = {"current": 0, "max": 0}

    async def _tracking_fetch(
        params: list[tuple[str, str]], stop_ids: list[str]
    ) -> dict[str, Any]:
        state["current"] += 1
        state["max"] = max(state["max"], state["current"])
        try:
            await asyncio.sleep(0.05)
        finally:
            state["current"] -= 1
        return {"message": {"messageCode": 1}, "data": {"monitors": []}}

    with patch.object(client, "_fetch_raw", new=AsyncMock(side_effect=_tracking_fetch)):
        result = await client.fetch([str(i) for i in range(16)])

    assert len(result) == 4
    assert 1 < state["max"] <= 3


async def test_fetch_cancels_siblings_on_batch_error() -> None:
    client = ViennaTransportClient(MagicMock(spec=aiohttp.ClientSession))
    cancelled: list[bool] = []

    async def _flaky_fetch(
        params: list[tuple[str, str]], stop_ids: list[str]
    ) -> dict[str, Any]:
        if "6" in stop_ids:
            raise ClientError("Unexpected HTTP status code: 500")
        try:
            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            cancelled.append(True)
            raise
        return {"message": {"messageCode": 1}, "data": {"monitors": []}}

    with (
        patch.object(client, "_fetch_raw", new=AsyncMock(side_effect=_flaky_fetch)),
        pytest.raises(ClientError, match="Unexpected HTTP status code: 500"),
    ):
        await client.fetch(["1", "2", "3", "4", "5", "6"])

    assert cancelled == [True]
