import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.lovelace import LovelaceData
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from custom_components.vienna_transport.frontend import CARD_URL, async_register_card

MANIFEST_PATH = (
    Path(__file__).parents[2]
    / "custom_components"
    / "vienna_transport"
    / "manifest.json"
)


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


def make_resources(
    hass: HomeAssistant, items: list[dict[str, Any]], *, loaded: bool = True
) -> MagicMock:
    hass.http = MagicMock()
    hass.http.async_register_static_paths = AsyncMock()

    resources = MagicMock(spec=ResourceStorageCollection)
    resources.loaded = loaded
    resources.async_load = AsyncMock()
    resources.async_items.return_value = items
    resources.async_create_item = AsyncMock()
    resources.async_update_item = AsyncMock()

    lovelace = MagicMock(spec=LovelaceData)
    lovelace.resources = resources
    lovelace.resource_mode = "storage"
    hass.data["lovelace"] = lovelace
    return resources


@pytest.fixture
def card_file() -> Iterator[None]:
    with patch.object(Path, "is_file", return_value=True):
        yield


@pytest.fixture
def version() -> Iterator[MagicMock]:
    integration = MagicMock(version="1.3.0")
    with patch(
        "custom_components.vienna_transport.frontend.async_get_integration",
        AsyncMock(return_value=integration),
    ):
        yield integration


@pytest.mark.usefixtures("card_file", "version")
async def test_creates_resource_when_missing(hass: HomeAssistant) -> None:
    resources = make_resources(hass, [], loaded=False)

    await async_register_card(hass)

    resources.async_load.assert_awaited_once()
    assert resources.loaded is True
    resources.async_create_item.assert_awaited_once_with(
        {"res_type": "module", "url": f"{CARD_URL}?v=1.3.0"}
    )
    resources.async_update_item.assert_not_called()


@pytest.mark.usefixtures("card_file", "version")
async def test_skips_when_resource_of_same_version_exists(
    hass: HomeAssistant,
) -> None:
    resources = make_resources(hass, [{"id": "abc", "url": f"{CARD_URL}?v=1.3.0"}])

    await async_register_card(hass)

    resources.async_create_item.assert_not_called()
    resources.async_update_item.assert_not_called()


@pytest.mark.usefixtures("card_file", "version")
@pytest.mark.parametrize(
    "old_url",
    [CARD_URL, f"{CARD_URL}?v=1.2.0"],
    ids=["unversioned", "older_version"],
)
async def test_updates_resource_of_other_version_in_place(
    hass: HomeAssistant, old_url: str
) -> None:
    resources = make_resources(hass, [{"id": "abc", "url": old_url}])

    await async_register_card(hass)

    resources.async_update_item.assert_awaited_once_with(
        "abc", {"res_type": "module", "url": f"{CARD_URL}?v=1.3.0"}
    )
    resources.async_create_item.assert_not_called()


@pytest.mark.usefixtures("card_file", "version")
async def test_ignores_resources_of_other_cards(hass: HomeAssistant) -> None:
    resources = make_resources(
        hass, [{"id": "abc", "url": f"{CARD_URL}-other.js?v=1.0.0"}]
    )

    await async_register_card(hass)

    resources.async_update_item.assert_not_called()
    resources.async_create_item.assert_awaited_once_with(
        {"res_type": "module", "url": f"{CARD_URL}?v=1.3.0"}
    )


@pytest.mark.usefixtures("card_file")
async def test_uses_unversioned_url_without_version(
    hass: HomeAssistant, version: MagicMock
) -> None:
    version.version = None
    resources = make_resources(hass, [])

    await async_register_card(hass)

    resources.async_create_item.assert_awaited_once_with(
        {"res_type": "module", "url": CARD_URL}
    )


@pytest.mark.usefixtures("card_file", "enable_custom_integrations")
async def test_versions_url_with_manifest_version(hass: HomeAssistant) -> None:
    manifest_version = json.loads(MANIFEST_PATH.read_text())["version"]
    resources = make_resources(hass, [])

    await async_register_card(hass)

    resources.async_create_item.assert_awaited_once_with(
        {"res_type": "module", "url": f"{CARD_URL}?v={manifest_version}"}
    )
