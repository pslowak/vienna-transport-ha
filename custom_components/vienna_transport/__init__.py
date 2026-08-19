"""
Vienna Transport HA integration.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.frontend import async_register_card
from custom_components.vienna_transport.hub import ViennaTransportHub, build_hub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    stop_ids = entry.data["stop_ids"]
    _LOGGER.info("Setting up Vienna Transport integration for stops %s", stop_ids)

    vt_hub = hass.data.get(DOMAIN)
    if vt_hub is None:
        vt_hub = build_hub(hass)
        hass.data[DOMAIN] = vt_hub

        await async_register_card(hass)
        await vt_hub.async_register_first_entry(entry)
    else:
        await vt_hub.async_register_entry(entry)

    entry.runtime_data = vt_hub.platform_data(entry.entry_id)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Vienna Transport integration setup complete for stops %s", stop_ids)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Unloading Vienna Transport integration for entry %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        vt_hub: ViennaTransportHub = hass.data[DOMAIN]
        if await vt_hub.async_unregister_entry(entry):
            hass.data.pop(DOMAIN, None)
            _LOGGER.debug("Vienna Transport hub torn down")

        _LOGGER.debug(
            "Vienna Transport integration unloaded for entry %s", entry.entry_id
        )

    return unload_ok
