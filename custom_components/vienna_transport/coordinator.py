"""Coordinator for Vienna transport data updates."""

from __future__ import annotations

import logging
from dataclasses import dataclass
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
from custom_components.vienna_transport.registry import StopRegistry

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlatformData:
    """Per-config-entry data handed to the sensor platform."""

    coordinator: ViennaTransportCoordinator
    stop_ids: list[str]


class ViennaTransportCoordinator(DataUpdateCoordinator[TransportData]):
    """Coordinator for fetching and caching transport data.

    Fetches data via API client, parses it, and caches results.
    Falls back to cached data on client or parser errors.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: ViennaTransportClient,
        parser: ViennaTransportParser,
        cache: ExpiringCache,
        registry: StopRegistry,
    ) -> None:
        """Initialize coordinator.

        Args:
            hass: Home Assistant instance.
            client: API client for fetching data.
            parser: Parser for API responses.
            cache: Cache for transport data.
            registry: Registry of stop IDs.

        """
        super().__init__(
            hass,
            _LOGGER,
            name="Vienna Transport Data Coordinator",
            update_interval=timedelta(seconds=60),
        )
        self._client = client
        self._parser = parser
        self._cache = cache
        self._registry = registry

    async def _async_update_data(self) -> TransportData:
        stop_ids = self._registry.stop_ids
        if not stop_ids:
            _LOGGER.debug("No stop IDs registered, skipping data fetching")
            return self._cache.get() or TransportData(stops={})

        try:
            raw = await self._client.fetch(stop_ids)
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
