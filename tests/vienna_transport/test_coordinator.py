from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.coordinator import ViennaTransportCoordinator
from custom_components.vienna_transport.exceptions import ClientError, ParserError
from custom_components.vienna_transport.model import Stop, TransportData


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.fetch = AsyncMock()
    return client


@pytest.fixture
def mock_parser() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_cache() -> MagicMock:
    return MagicMock(spec=ExpiringCache)


@pytest.fixture
def transport_data() -> TransportData:
    return TransportData(stops={2683: MagicMock(spec=Stop)})


@pytest.fixture
def coordinator(
    hass, mock_client, mock_parser, mock_cache
) -> ViennaTransportCoordinator:
    return ViennaTransportCoordinator(
        hass=hass,
        client=mock_client,
        parser=mock_parser,
        cache=mock_cache,
        stop_ids=["2683"],
    )


async def test_update_data_returns_transport_data(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_parser: MagicMock,
    transport_data: TransportData,
) -> None:
    mock_client.fetch.return_value = {"message": {"messageCode": 1}}
    mock_parser.parse.return_value = transport_data

    result = await coordinator._async_update_data()

    assert result is transport_data


async def test_update_data_calls_client_with_stop_ids(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_parser: MagicMock,
    transport_data: TransportData,
) -> None:
    mock_client.fetch.return_value = {}
    mock_parser.parse.return_value = transport_data

    await coordinator._async_update_data()

    mock_client.fetch.assert_called_once_with(["2683"])


async def test_update_data_passes_raw_response_to_parser(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_parser: MagicMock,
    transport_data: TransportData,
) -> None:
    raw = {"message": {"messageCode": 1}, "data": {"monitors": []}}
    mock_client.fetch.return_value = raw
    mock_parser.parse.return_value = transport_data

    await coordinator._async_update_data()

    mock_parser.parse.assert_called_once_with(raw)


async def test_update_data_caches_result(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_parser: MagicMock,
    mock_cache: MagicMock,
    transport_data: TransportData,
) -> None:
    mock_client.fetch.return_value = {}
    mock_parser.parse.return_value = transport_data

    await coordinator._async_update_data()

    mock_cache.set.assert_called_once_with(transport_data)


async def test_update_data_returns_cached_on_client_error(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_cache: MagicMock,
    transport_data: TransportData,
) -> None:
    mock_client.fetch.side_effect = ClientError("API error")
    mock_cache.get.return_value = transport_data

    result = await coordinator._async_update_data()

    assert result is transport_data


async def test_update_data_returns_cached_on_parser_error(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_parser: MagicMock,
    mock_cache: MagicMock,
    transport_data: TransportData,
) -> None:
    mock_client.fetch.return_value = {}
    mock_parser.parse.side_effect = ParserError("Parse error")
    mock_cache.get.return_value = transport_data

    result = await coordinator._async_update_data()

    assert result is transport_data


async def test_update_data_raises_update_failed_on_error_without_cache(
    coordinator: ViennaTransportCoordinator,
    mock_client: MagicMock,
    mock_cache: MagicMock,
) -> None:
    mock_client.fetch.side_effect = ClientError("API error")
    mock_cache.get.return_value = None

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
