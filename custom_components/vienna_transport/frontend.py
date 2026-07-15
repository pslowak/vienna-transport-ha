import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
from homeassistant.components.lovelace import LovelaceData
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_URL = f"/api/static/{DOMAIN}/transport-card.js"


async def async_register_card(hass: HomeAssistant) -> None:
    _LOGGER.debug("Registering Vienna Transport Card frontend")

    card_path = Path(__file__).parent / "frontend" / "transport-card.js"

    if not card_path.is_file():
        _LOGGER.warning(
            "no transport-card.js found at %s, skipping card registration", card_path
        )
        return

    try:
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    url_path=CARD_URL, path=str(card_path), cache_headers=True
                )
            ]
        )
        _LOGGER.debug("Static path registered: %s -> %s", CARD_URL, card_path)
    except RuntimeError:
        _LOGGER.debug("Static path already registered: %s", CARD_URL)

    lovelace: LovelaceData | None = hass.data.get(LOVELACE_DOMAIN)
    if lovelace is None:
        _LOGGER.debug("Lovelace not available, skipping resource registration")
        return

    resources = lovelace.resources
    if not isinstance(resources, ResourceStorageCollection):
        _LOGGER.debug(
            "Lovelace is in %s mode, skipping automatic resource registration",
            lovelace.resource_mode,
        )
        return

    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True
        _LOGGER.debug("Lovelace resource collection loaded from storage")

    existing = [r for r in resources.async_items() if r.get("url") == CARD_URL]
    if existing:
        _LOGGER.debug("Card resource already registered, skipping")
        return

    await resources.async_create_item({"res_type": "module", "url": CARD_URL})
    _LOGGER.info("Registered Transport Card as Lovelace resource: %s", CARD_URL)
