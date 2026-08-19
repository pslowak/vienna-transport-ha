from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.coordinator import (
    PlatformData,
    ViennaTransportCoordinator,
)
from custom_components.vienna_transport.parser import ViennaTransportParser
from custom_components.vienna_transport.registry import StopRegistry

_LOGGER = logging.getLogger(__name__)


class ViennaTransportHub:
    def __init__(
        self,
        registry: StopRegistry,
        coordinator: ViennaTransportCoordinator,
    ) -> None:
        self._registry = registry
        self._coordinator = coordinator

    def platform_data(self, entry_id: str) -> PlatformData:
        """Return the per-config-entry data handed to the sensor platform."""
        return PlatformData(
            coordinator=self._coordinator,
            stop_ids=self._stop_ids_for_entry(entry_id),
        )

    async def async_register_first_entry(self, entry: ConfigEntry) -> None:
        self._registry.register(entry.entry_id, list(entry.data["stop_ids"]))
        await self._coordinator.async_config_entry_first_refresh()

    async def async_register_entry(self, entry: ConfigEntry) -> None:
        self._registry.register(entry.entry_id, list(entry.data["stop_ids"]))
        await self._coordinator.async_request_refresh()

    async def async_unregister_entry(self, entry: ConfigEntry) -> bool:
        """Remove an entry's stops.

        Returns ``True`` if this was the last registered entry and the hub
        should be torn down by the caller.
        """
        self._registry.unregister(entry.entry_id)
        if self._registry.is_empty:
            await self._coordinator.async_shutdown()
            return True
        await self._coordinator.async_request_refresh()
        return False

    def _stop_ids_for_entry(self, entry_id: str) -> list[str]:
        return self._registry.stop_ids_for(entry_id)


def build_hub(hass: HomeAssistant) -> ViennaTransportHub:
    client = ViennaTransportClient(session=aiohttp_client.async_get_clientsession(hass))
    parser = ViennaTransportParser()
    cache = ExpiringCache()
    registry = StopRegistry()
    coordinator = ViennaTransportCoordinator(
        hass=hass,
        client=client,
        parser=parser,
        cache=cache,
        registry=registry,
    )
    return ViennaTransportHub(registry=registry, coordinator=coordinator)
