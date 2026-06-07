from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.vienna_transport_ha import ViennaTransportCoordinator
from custom_components.vienna_transport_ha.model import Stop, TransportData


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.fetch = AsyncMock()
    return client


@pytest.fixture
def mock_parser() -> MagicMock:
    return MagicMock()


@pytest.fixture
def transport_data() -> TransportData:
    return TransportData(stops={2683: MagicMock(spec=Stop)}, return_code=1)


@pytest.fixture
def coordinator(hass, mock_client, mock_parser) -> ViennaTransportCoordinator:
    return ViennaTransportCoordinator(
        hass=hass, client=mock_client, parser=mock_parser, stop_ids=["2683"]
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
