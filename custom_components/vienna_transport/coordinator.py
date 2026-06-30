import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.exceptions import ClientError, ParserError
from custom_components.vienna_transport.model import TransportData
from custom_components.vienna_transport.parser import ViennaTransportParser

_LOGGER = logging.getLogger(__name__)


class ViennaTransportCoordinator(DataUpdateCoordinator[TransportData]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: ViennaTransportClient,
        parser: ViennaTransportParser,
        cache: ExpiringCache,
        stop_ids: list[str],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Vienna Transport Data Coordinator",
            update_interval=timedelta(seconds=60),
        )
        self._client = client
        self._parser = parser
        self._cache = cache
        self.stop_ids = stop_ids

    async def _async_update_data(self) -> TransportData:
        try:
            raw = await self._client.fetch(self.stop_ids)
            parsed = self._parser.parse(raw)
            self._cache.set(parsed)
            _LOGGER.debug("Cache updated")
            return parsed
        except (ClientError, ParserError) as e:
            cached = self._cache.get()
            if cached is not None:
                _LOGGER.info(
                    "Cache hit: Using transport data due to %s: %s",
                    type(e).__name__,
                    e,
                    exc_info=True,
                )
                return cached
            _LOGGER.debug("Cache miss")
            raise UpdateFailed(str(e)) from e
