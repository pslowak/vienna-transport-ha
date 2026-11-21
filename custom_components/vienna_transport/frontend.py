"""Frontend registration for Vienna Transport card."""

import logging
from pathlib import Path

from homeassistant.components.http.server import StaticPathConfig
from homeassistant.components.lovelace import LovelaceData
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_URL = f"/api/static/{DOMAIN}/transport-card.js"
LOVELACE_DOMAIN = "lovelace"


async def async_register_card(hass: HomeAssistant) -> None:
    """Register transport card frontend and Lovelace resource.

    Args:
        hass: Home Assistant instance.

    """
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

    await _async_register_resource(resources, await _async_card_url(hass))


async def _async_card_url(hass: HomeAssistant) -> str:
    # The card is served with long-lived cache headers. A version in the
    # resource URL makes browsers fetch the new card after an update instead
    # of keeping the cached one.
    integration = await async_get_integration(hass, DOMAIN)
    if integration.version is None:
        return CARD_URL
    return f"{CARD_URL}?v={integration.version}"


async def _async_register_resource(
    resources: ResourceStorageCollection, url: str
) -> None:
    existing = [r for r in resources.async_items() if _is_card_url(r.get("url"))]

    if any(r.get("url") == url for r in existing):
        _LOGGER.debug("Card resource already registered, skipping")
        return

    if existing:
        # Update the resource of an older version in place: a second resource
        # would load the card twice and fail to define its element again.
        await resources.async_update_item(
            existing[0]["id"], {"res_type": "module", "url": url}
        )
        _LOGGER.info("Updated Transport Card Lovelace resource: %s", url)
        return

    await resources.async_create_item({"res_type": "module", "url": url})
    _LOGGER.info("Registered Transport Card as Lovelace resource: %s", url)


def _is_card_url(url: object) -> bool:
    return isinstance(url, str) and (url == CARD_URL or url.startswith(f"{CARD_URL}?"))
