"""
Vienna Transport HA integration.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.coordinator import ViennaTransportCoordinator
from custom_components.vienna_transport.frontend import async_register_card
from custom_components.vienna_transport.parser import ViennaTransportParser

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    stop_ids = entry.data["stop_ids"]
    _LOGGER.info("Setting up Vienna Transport integration for stops %s", stop_ids)

    session = aiohttp_client.async_get_clientsession(hass)

    pt_client = ViennaTransportClient(session=session)
    pt_parser = ViennaTransportParser()
    pt_cache = ExpiringCache()

    c = ViennaTransportCoordinator(
        hass=hass, client=pt_client, parser=pt_parser, cache=pt_cache, stop_ids=stop_ids
    )

    await c.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = c
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await async_register_card(hass)

    _LOGGER.debug("Vienna Transport integration setup complete for stops %s", stop_ids)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Unloading Vienna Transport integration for entry %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug(
            "Vienna Transport integration unloaded for entry %s", entry.entry_id
        )

    return unload_ok
