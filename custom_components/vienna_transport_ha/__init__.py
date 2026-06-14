"""
Vienna Transport HA integration.
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from custom_components.vienna_transport_ha.client import ViennaTransportClient
from custom_components.vienna_transport_ha.const import DOMAIN
from custom_components.vienna_transport_ha.coordinator import ViennaTransportCoordinator
from custom_components.vienna_transport_ha.parser import ViennaTransportParser

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp_client.async_get_clientsession(hass)

    pt_client = ViennaTransportClient(session=session)
    pt_parser = ViennaTransportParser()

    c = ViennaTransportCoordinator(
        hass=hass, client=pt_client, parser=pt_parser, stop_ids=entry.data["stop_ids"]
    )

    await c.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = c
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
