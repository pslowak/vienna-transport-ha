from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component import common

from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.config_flow import (
    ViennaTransportConfigFlow,
    _StopCheckError,
)
from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.exceptions import ClientError, ParserError
from custom_components.vienna_transport.model import Stop, StopProperties, TransportData
from custom_components.vienna_transport.setup.model import StopListEntry

_LOAD = "custom_components.vienna_transport.config_flow.StopListLoader.load"
_ENTRIES = [
    StopListEntry(stop_id=4113, name="Schwedenplatz", line="U1", towards="Leopoldau"),
    StopListEntry(stop_id=4116, name="Schwedenplatz", line="U1", towards="Oberlaa"),
    StopListEntry(stop_id=4119, name="Stephansplatz", line="U1", towards="Oberlaa"),
    StopListEntry(stop_id=5650, name="Schwedenplatz", line="1", towards="Prater"),
]


def test_validate_stop_ids_returns_cleaned_list() -> None:
    valid, invalid = ViennaTransportConfigFlow._validate_stop_ids(["2683", " 1337 "])
    assert valid == ["2683", "1337"]
    assert invalid == []


def test_validate_stop_ids_returns_empty_on_blank_input() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids([""]) == ([], [])
    assert ViennaTransportConfigFlow._validate_stop_ids(["  "]) == ([], [])
    assert ViennaTransportConfigFlow._validate_stop_ids([]) == ([], [])


def test_validate_stop_ids_splits_valid_and_invalid() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids(["abc"]) == ([], ["abc"])
    assert ViennaTransportConfigFlow._validate_stop_ids(["2683", "abc"]) == (
        ["2683"],
        ["abc"],
    )


def test_validate_stop_ids_accepts_multiple_valid_ids() -> None:
    valid, invalid = ViennaTransportConfigFlow._validate_stop_ids(
        ["2683", "1337", "5566"]
    )
    assert valid == ["2683", "1337", "5566"]
    assert invalid == []


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


async def test_step_manual_rejects_stop_already_configured(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    result = await flow.async_step_manual(user_input={"stop_ids": ["2683", "1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "stop_ids_already_configured"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["stop_ids"] == "2683"


async def test_step_manual_allows_new_stop(hass: HomeAssistant) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(
            return_value=TransportData(
                stops={
                    1337: Stop(
                        props=StopProperties(id=1337, name="Schottentor"), lines=[]
                    )
                }
            )
        ),
    ) as test_connection:
        result = await flow.async_step_manual(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["stop_ids"] == ["1337"]
    test_connection.assert_awaited_once()


async def test_step_manual_shows_cannot_connect_on_client_error(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(side_effect=ClientError("Timeout error: request timed out")),
    ):
        result = await flow.async_step_manual(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "cannot_connect"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["detail"] == "Timeout error: request timed out"


async def test_step_manual_shows_unexpected_response_on_parser_error(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(
            side_effect=ParserError("API rate limit reached (message code 316)")
        ),
    ):
        result = await flow.async_step_manual(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "unexpected_response"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["detail"] == "API rate limit reached (message code 316)"


async def test_step_manual_shows_unexpected_response_on_validation_error(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)
    malformed = {"message": {"messageCode": 1}, "data": None}

    with patch.object(
        ViennaTransportClient, "fetch", new=AsyncMock(return_value=[malformed])
    ):
        result = await flow.async_step_manual(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "unexpected_response"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["detail"].startswith("unexpected API response: data: ")


async def test_step_manual_shows_unknown_on_unexpected_error(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ) as test_connection:
        result = await flow.async_step_manual(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "unknown"}
    test_connection.assert_awaited_once()


async def test_step_manual_shows_stop_not_found_on_empty_response(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(return_value=TransportData(stops={})),
    ):
        result = await flow.async_step_manual(user_input={"stop_ids": ["9999"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "stop_not_found"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["stop_ids"] == "9999"


async def test_step_manual_shows_stop_not_found_on_partial_response(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["1337"]},
    ).add_to_hass(hass)

    flow = make_flow(hass)

    with patch.object(
        flow,
        "_test_connection",
        new=AsyncMock(
            return_value=TransportData(
                stops={
                    2683: Stop(
                        props=StopProperties(id=2683, name="Volkertplatz"), lines=[]
                    )
                }
            )
        ),
    ):
        result = await flow.async_step_manual(user_input={"stop_ids": ["2683", "9999"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "stop_not_found"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["stop_ids"] == "9999"
    assert "rbl_url" in placeholders


async def test_step_manual_shows_empty_stop_ids_on_blank_input(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)

    result = await flow.async_step_manual(user_input={"stop_ids": ["  "]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "empty_stop_ids"}


async def test_step_manual_shows_invalid_stop_id_with_placeholder(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)

    result = await flow.async_step_manual(user_input={"stop_ids": ["a stop"]})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "invalid_stop_id"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["stop_ids"] == '"a stop"'


async def test_step_manual_shows_all_invalid_stop_ids_with_placeholder(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)

    result = await flow.async_step_manual(
        user_input={"stop_ids": ["2683", "abc", "def"]}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"stop_ids": "invalid_stop_ids"}
    placeholders = result.get("description_placeholders")
    assert placeholders is not None
    assert placeholders["stop_ids"] == '"abc", "def"'


async def test_check_stops_returns_data_for_new_stop(hass: HomeAssistant) -> None:
    flow = make_flow(hass)
    data = TransportData(
        stops={1337: Stop(props=StopProperties(id=1337, name="Schottentor"), lines=[])}
    )

    with patch.object(flow, "_test_connection", new=AsyncMock(return_value=data)):
        result = await flow._async_check_stops(["1337"])

    assert result is data


async def test_check_stops_raises_for_configured_stop(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["2683"]},
    ).add_to_hass(hass)
    flow = make_flow(hass)

    with pytest.raises(_StopCheckError) as exc_info:
        await flow._async_check_stops(["2683"])

    assert exc_info.value.key == "stop_ids_already_configured"
    assert exc_info.value.placeholders == {"stop_ids": "2683"}


async def test_step_user_shows_menu_with_stop_list(hass: HomeAssistant) -> None:
    flow = make_flow(hass)

    with patch(_LOAD, return_value=_ENTRIES):
        result = await flow.async_step_user()

    assert result["type"] == FlowResultType.MENU
    assert result["step_id"] == "user"
    assert result["menu_options"] == ["pick_line", "manual"]


async def test_step_user_shows_manual_form_without_stop_list(
    hass: HomeAssistant,
) -> None:
    flow = make_flow(hass)

    with patch(_LOAD, side_effect=FileNotFoundError):
        result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "manual"
    assert result["errors"] == {}


async def test_step_user_shows_manual_form_for_empty_stop_list(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    flow = make_flow(hass)

    with patch(_LOAD, return_value=[]):
        result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "manual"
    assert "Stop list is empty" in caplog.text


async def test_step_user_passes_input_to_manual_step(hass: HomeAssistant) -> None:
    flow = make_flow(hass)
    data = TransportData(
        stops={1337: Stop(props=StopProperties(id=1337, name="Schottentor"), lines=[])}
    )

    with patch.object(flow, "_test_connection", new=AsyncMock(return_value=data)):
        result = await flow.async_step_user(user_input={"stop_ids": ["1337"]})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["stop_ids"] == ["1337"]


async def _picked_flow(hass: HomeAssistant) -> ViennaTransportConfigFlow:
    flow = make_flow(hass)
    with patch(_LOAD, return_value=_ENTRIES):
        await flow.async_step_user()
    await flow.async_step_pick_line(user_input={"line": "U1"})
    await flow.async_step_pick_direction(user_input={"towards": "Oberlaa"})
    return flow


def _options(result: Any, key: str) -> Any:
    return result["data_schema"].schema[key].config["options"]


async def test_step_pick_line_offers_lines(hass: HomeAssistant) -> None:
    flow = make_flow(hass)
    with patch(_LOAD, return_value=_ENTRIES):
        await flow.async_step_user()

    result = await flow.async_step_pick_line()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "pick_line"
    assert _options(result, "line") == ["1", "U1"]


async def test_step_pick_line_shows_directions_of_line(hass: HomeAssistant) -> None:
    flow = make_flow(hass)
    with patch(_LOAD, return_value=_ENTRIES):
        await flow.async_step_user()

    result = await flow.async_step_pick_line(user_input={"line": "U1"})

    assert result["step_id"] == "pick_direction"
    assert _options(result, "towards") == ["Leopoldau", "Oberlaa"]
    placeholders = result.get("description_placeholders")
    assert placeholders == {"line": "U1"}


async def test_step_pick_direction_shows_stops_of_direction(
    hass: HomeAssistant,
) -> None:
    flow = await _picked_flow(hass)

    result = await flow.async_step_pick_stop()

    assert result["step_id"] == "pick_stop"
    assert _options(result, "stop") == [
        {"value": "4116", "label": "Schwedenplatz"},
        {"value": "4119", "label": "Stephansplatz"},
    ]
    placeholders = result.get("description_placeholders")
    assert placeholders == {"line": "U1", "towards": "Oberlaa"}


async def test_step_pick_stop_creates_entry(hass: HomeAssistant) -> None:
    flow = await _picked_flow(hass)
    data = TransportData(
        stops={
            4116: Stop(props=StopProperties(id=4116, name="Schwedenplatz"), lines=[])
        }
    )

    with patch.object(flow, "_test_connection", new=AsyncMock(return_value=data)):
        result = await flow.async_step_pick_stop(user_input={"stop": "4116"})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stop: Schwedenplatz (ID: 4116)"
    assert result["data"] == {"stop_ids": ["4116"]}


async def test_step_pick_stop_shows_error_on_pick_stop_form(
    hass: HomeAssistant,
) -> None:
    common.MockConfigEntry(
        domain=DOMAIN,
        data={"stop_ids": ["4116"]},
    ).add_to_hass(hass)
    flow = await _picked_flow(hass)

    result = await flow.async_step_pick_stop(user_input={"stop": "4116"})

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "pick_stop"
    assert result["errors"] == {"stop": "stop_ids_already_configured"}
    placeholders = result.get("description_placeholders")
    assert placeholders == {"line": "U1", "towards": "Oberlaa", "stop_ids": "4116"}
