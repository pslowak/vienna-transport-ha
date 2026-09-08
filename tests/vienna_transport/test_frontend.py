from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.lovelace import LovelaceData
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from custom_components.vienna_transport.frontend import CARD_URL, async_register_card


async def test_registers_static_path(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()
        hass.data.clear()

        await async_register_card(hass)

        assert hass.http.async_register_static_paths.await_count == 1
        config = hass.http.async_register_static_paths.call_args.args[0][0]
        assert config.url_path == CARD_URL
        assert config.cache_headers is True
        assert config.path.endswith("transport-card.js")


async def test_handles_duplicate_static_path(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock(
            side_effect=RuntimeError("already registered")
        )
        hass.data.clear()

        await async_register_card(hass)

        hass.http.async_register_static_paths.assert_awaited_once()


async def test_skips_resource_when_lovelace_none(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()
        hass.data.clear()

        await async_register_card(hass)

        hass.http.async_register_static_paths.assert_awaited_once()


async def test_skips_resource_in_yaml_mode(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()

        yaml_resources = MagicMock()
        lovelace = MagicMock(spec=LovelaceData)
        lovelace.resources = yaml_resources
        lovelace.resource_mode = "yaml"
        hass.data.clear()
        hass.data["lovelace"] = lovelace

        await async_register_card(hass)

        # yaml_resources is not a ResourceStorageCollection, so no create
        assert not isinstance(yaml_resources, ResourceStorageCollection)


async def test_skips_when_resource_already_exists(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()

        resources = MagicMock(spec=ResourceStorageCollection)
        resources.loaded = True
        resources.async_items.return_value = [{"url": CARD_URL}]
        resources.async_create_item = AsyncMock()

        lovelace = MagicMock(spec=LovelaceData)
        lovelace.resources = resources
        lovelace.resource_mode = "storage"
        hass.data.clear()
        hass.data["lovelace"] = lovelace

        await async_register_card(hass)

        resources.async_create_item.assert_not_called()


async def test_creates_resource_when_missing(hass: HomeAssistant) -> None:
    with patch.object(Path, "is_file", return_value=True):
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()

        resources = MagicMock(spec=ResourceStorageCollection)
        resources.loaded = False
        resources.async_load = AsyncMock()
        resources.async_items.return_value = []
        resources.async_create_item = AsyncMock()

        lovelace = MagicMock(spec=LovelaceData)
        lovelace.resources = resources
        lovelace.resource_mode = "storage"
        hass.data.clear()
        hass.data["lovelace"] = lovelace

        await async_register_card(hass)

        resources.async_load.assert_awaited_once()
        assert resources.loaded is True
        resources.async_create_item.assert_awaited_once_with(
            {"res_type": "module", "url": CARD_URL}
        )
