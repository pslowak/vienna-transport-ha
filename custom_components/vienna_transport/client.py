"""Client for Wiener Linien realtime monitor API."""

import logging
from typing import Any

import aiohttp

from custom_components.vienna_transport.exceptions import ClientError

_LOGGER = logging.getLogger(__name__)

_API_BASE_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

_HTTP_OK = 200


class ViennaTransportClient:
    """Client for fetching departure data from Wiener Linien API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize client.

        Args:
            session: HTTP client session for API requests.

        """
        self._session = session

    async def fetch(self, stop_ids: list[str]) -> dict[str, Any]:
        """Fetch departure data for one or more stops.

        Args:
            stop_ids: List of stop IDs to fetch.

        Returns:
            JSON response from API as dictionary.

        Raises:
            ClientError: If request fails or returns non-200 status.
            ValueError: If stop_ids is empty.

        """
        if not stop_ids:
            raise ValueError("stop_ids cannot be empty")

        params = [("stopId", stop_id) for stop_id in stop_ids]

        _LOGGER.debug("Fetching data for stops %s", stop_ids)

        try:
            async with self._session.get(
                _API_BASE_URL, params=params, timeout=_REQUEST_TIMEOUT
            ) as response:
                _LOGGER.debug(
                    "Received HTTP %s for stops %s", response.status, stop_ids
                )
                if response.status == _HTTP_OK:
                    data: dict[str, Any] = await response.json()
                    return data
                raise ClientError(f"Unexpected HTTP status code: {response.status}")
        except aiohttp.ClientConnectionError as e:
            raise ClientError(f"Connection error: {e}") from e
        except TimeoutError as e:
            raise ClientError(f"Timeout error: {e}") from e
