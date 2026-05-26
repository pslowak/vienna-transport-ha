import logging

import aiohttp
from homeassistant.helpers.update_coordinator import UpdateFailed

_LOGGER = logging.getLogger(__name__)

_API_BASE_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

_HTTP_OK = 200
_HTTP_FORBIDDEN = 403


class ViennaTransportClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def fetch(self, stop_ids: list[str]) -> dict:
        """Fetches departure data for one or more stops."""

        if not stop_ids:
            raise ValueError("stop_ids cannot be empty")

        params = [("stopId", stop_id) for stop_id in stop_ids]

        _LOGGER.debug("Fetching data for stops %s", stop_ids)

        try:
            async with self._session.get(
                _API_BASE_URL, params=params, timeout=_REQUEST_TIMEOUT
            ) as response:
                if response.status == _HTTP_OK or response.status == _HTTP_FORBIDDEN:
                    return await response.json()
                else:
                    raise UpdateFailed(
                        f"Unexpected HTTP status code: {response.status}"
                    )
        except aiohttp.ClientConnectionError as e:
            raise UpdateFailed(f"Connection error: {e}") from e
        except TimeoutError as e:
            raise UpdateFailed(f"Timeout error: {e}") from e
