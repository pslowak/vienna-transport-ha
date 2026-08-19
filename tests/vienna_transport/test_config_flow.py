from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component import common

from custom_components.vienna_transport.config_flow import ViennaTransportConfigFlow
from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.model import Stop, StopProperties, TransportData


def test_validate_stop_ids_returns_cleaned_list() -> None:
    result = ViennaTransportConfigFlow._validate_stop_ids(["2683", " 1337 "])
    assert result == ["2683", "1337"]


def test_validate_stop_ids_returns_empty_on_blank_input() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids([""]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids(["  "]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids([]) == []


def test_validate_stop_ids_returns_empty_on_non_numeric() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids(["abc"]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids(["2683", "abc"]) == []


def test_validate_stop_ids_accepts_multiple_valid_ids() -> None:
    result = ViennaTransportConfigFlow._validate_stop_ids(["2683", "1337", "5566"])
    assert result == ["2683", "1337", "5566"]


def test_build_title_uses_singular_stop() -> None:
    data = TransportData(
        stops={2683: Stop(props=StopProperties(id=2683, name="Volkertplatz"), lines=[])}
    )
    assert (
        ViennaTransportConfigFlow._build_title(data) == "Stop: Volkertplatz (ID: 2683)"
    )


def test_build_title_uses_plural_stops() -> None:
    data = TransportData(
        stops={
            2683: Stop(props=StopProperties(id=2683, name="Volkertplatz"), lines=[]),
            1337: Stop(props=StopProperties(id=1337, name="Schottentor"), lines=[]),
        }
    )
    assert (
        ViennaTransportConfigFlow._build_title(data)
        == "Stops: Volkertplatz (ID: 2683), Schottentor (ID: 1337)"
    )


def make_flow(hass: HomeAssistant) -> ViennaTransportConfigFlow:
    flow = ViennaTransportConfigFlow()
    flow.hass = hass
    flow.context = {}
    return flow


async def test_step_user_rejects_stop_already_configured(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    result = await flow.async_step_user(user_input={"stop_ids": ["2683", "1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "stop_ids_already_configured"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None and placeholders["stop_ids"] == "2683"


async def test_step_user_allows_new_stop(hass: HomeAssistant) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow, "_test_connection", new=AsyncMock(return_value=TransportData(stops={}))
    ) as test_connection:
        result = await flow.async_step_user(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["stop_ids"] == ["1337"]
    test_connection.assert_awaited_once()
