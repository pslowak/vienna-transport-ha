"""Client for Wiener Linien realtime monitor API."""

import asyncio
import logging
from typing import Any

import aiohttp

from custom_components.vienna_transport.exceptions import ClientError

_LOGGER = logging.getLogger(__name__)

_API_BASE_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

_HTTP_OK = 200
_MAX_STOPS_PER_REQUEST = 5


class ViennaTransportClient:
    """Client for fetching departure data from Wiener Linien API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize client.

        Args:
            session: HTTP client session for API requests.

        """
        self._session = session

    async def fetch(self, stop_ids: list[str]) -> list[dict[str, Any]]:
        """Fetch departure data for one or more stops.

        Stops are fetched in batches: One raw response is returned per batch.

        Args:
            stop_ids: List of stop IDs to fetch.

        Returns:
            List of raw JSON responses from API.

        Raises:
            ClientError: If any batch request fails or returns non-200 status.
            ValueError: If stop_ids is empty.

        """
        if not stop_ids:
            raise ValueError("stop_ids cannot be empty")

        chunks = self._chunk_stop_ids(stop_ids)

        _LOGGER.debug(
            "Fetching data for stops %s in %d batch(es)", stop_ids, len(chunks)
        )
        for index, chunk in enumerate(chunks, start=1):
            _LOGGER.debug(
                "Fetching batch %d/%d for stops %s", index, len(chunks), chunk
            )

        try:
            responses = await asyncio.gather(
                *(
                    self._fetch_raw([("stopId", stop_id) for stop_id in chunk], chunk)
                    for chunk in chunks
                )
            )
        except (aiohttp.ContentTypeError, ValueError) as e:
            raise ClientError(f"Invalid JSON response: {e}") from e
        except TimeoutError as e:
            raise ClientError(f"Timeout error: {e}") from e
        except aiohttp.ClientError as e:
            raise ClientError(f"HTTP client error: {e}") from e

        return list(responses)

    @staticmethod
    def _chunk_stop_ids(
        stop_ids: list[str], size: int = _MAX_STOPS_PER_REQUEST
    ) -> list[list[str]]:
        unique = sorted(set(stop_ids))
        return [unique[i : i + size] for i in range(0, len(unique), size)]

    async def _fetch_raw(
        self, params: list[tuple[str, str]], stop_ids: list[str]
    ) -> dict[str, Any]:
        async with self._session.get(
            _API_BASE_URL, params=params, timeout=_REQUEST_TIMEOUT
        ) as response:
            _LOGGER.debug("Received HTTP %s for stops %s", response.status, stop_ids)
            if response.status != _HTTP_OK:
                raise ClientError(f"Unexpected HTTP status code: {response.status}")
            data: dict[str, Any] = await response.json()
            return data
