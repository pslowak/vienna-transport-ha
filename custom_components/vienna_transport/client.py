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
_MAX_CONCURRENT_REQUESTS = 3


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

        Stops are fetched in batches with bounded concurrency: One raw
        response is returned per batch.

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

        sem = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)
        tasks: list[asyncio.Task[dict[str, Any]]] = []
        try:
            async with asyncio.TaskGroup() as task_group:
                for chunk in chunks:
                    tasks.append(task_group.create_task(self._fetch_batch(sem, chunk)))
        except BaseExceptionGroup as error_group:
            raise self._map_error(error_group.exceptions[0]) from error_group

        return [task.result() for task in tasks]

    async def _fetch_batch(
        self, sem: asyncio.Semaphore, chunk: list[str]
    ) -> dict[str, Any]:
        async with sem:
            return await self._fetch_raw(
                [("stopId", stop_id) for stop_id in chunk], chunk
            )

    @staticmethod
    def _map_error(error: BaseException) -> ClientError:
        if isinstance(error, ClientError):
            return error
        if isinstance(error, (aiohttp.ContentTypeError, ValueError)):
            return ClientError(f"Invalid JSON response: {error}")
        if isinstance(error, TimeoutError):
            return ClientError(f"Timeout error: {error}")
        if isinstance(error, aiohttp.ClientError):
            return ClientError(f"HTTP client error: {error}")
        return ClientError(f"Unexpected batch error: {error}")

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
