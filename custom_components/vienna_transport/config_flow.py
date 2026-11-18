"""Config flow for Vienna Transport integration."""

import logging
from typing import Any

import probatio
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.exceptions import (
    ClientError,
    ParserError,
    ValidationError,
)
from custom_components.vienna_transport.model import TransportData
from custom_components.vienna_transport.parser import ViennaTransportParser
from custom_components.vienna_transport.stop_list_loader import StopListLoader
from custom_components.vienna_transport.stop_list_query import StopListQuery
from custom_components.vienna_transport.validator import ViennaTransportValidator

_LOGGER = logging.getLogger(__name__)

_KEY_STOP_IDS = "stop_ids"
_KEY_LINE = "line"
_KEY_TOWARDS = "towards"
_KEY_STOP = "stop"
_RBL_SEARCH_URL = "https://till.mabe.at/rbl/"
_STEP_MANUAL_SCHEMA = probatio.Schema(
    {probatio.Required(_KEY_STOP_IDS): TextSelector(TextSelectorConfig(multiple=True))}
)


class _StopCheckError(Exception):
    """Raised when stops can't be added, with the error to show on the form."""

    def __init__(self, key: str, placeholders: dict[str, str] | None = None) -> None:
        """Initialize error.

        Args:
            key: Translation key of the error.
            placeholders: Values for the placeholders of the error message.

        """
        super().__init__(key)
        self.key = key
        self.placeholders = placeholders or {}


class ViennaTransportConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Vienna Transport.

    Lets the user pick a stop by line, direction and stop from the stop list,
    or enter stop IDs manually. Handles validation, duplicate check, and
    connection test.
    """

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        super().__init__()
        self._query = StopListQuery([])
        self._line = ""
        self._towards = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial user step.

        Offers to pick a stop from the stop list or to enter stop IDs. Without
        a stop list, goes straight to stop ID entry.

        Args:
            user_input: User input with stop IDs or None for initial form.

        Returns:
            Config flow result with menu, or of the manual step.

        """
        if user_input is not None:
            return await self.async_step_manual(user_input)

        try:
            entries = await self.hass.async_add_executor_job(StopListLoader().load)
        except FileNotFoundError:
            return await self.async_step_manual()
        if not entries:
            _LOGGER.warning("Stop list is empty, offering stop ID entry only")
            return await self.async_step_manual()

        self._query = StopListQuery(entries)
        return self.async_show_menu(
            step_id="user", menu_options=["pick_line", "manual"]
        )

    async def async_step_pick_line(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle picking the line of a stop.

        Args:
            user_input: User input with line or None for initial form.

        Returns:
            Config flow result with form or of the direction step.

        """
        if user_input is not None:
            self._line = user_input[_KEY_LINE]
            return await self.async_step_pick_direction()

        return self.async_show_form(
            step_id="pick_line",
            data_schema=probatio.Schema(
                {
                    probatio.Required(_KEY_LINE): SelectSelector(
                        SelectSelectorConfig(
                            options=self._query.lines(),
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_pick_direction(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle picking the direction of the line.

        Args:
            user_input: User input with direction or None for initial form.

        Returns:
            Config flow result with form or of the stop step.

        """
        if user_input is not None:
            self._towards = user_input[_KEY_TOWARDS]
            return await self.async_step_pick_stop()

        return self.async_show_form(
            step_id="pick_direction",
            data_schema=probatio.Schema(
                {
                    probatio.Required(_KEY_TOWARDS): SelectSelector(
                        SelectSelectorConfig(
                            options=self._query.directions(self._line),
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            description_placeholders={"line": self._line},
        )

    async def async_step_pick_stop(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle picking the stop of the line in the direction.

        Args:
            user_input: User input with stop ID or None for initial form.

        Returns:
            Config flow result with form or created entry.

        """
        if user_input is None:
            return self._show_pick_stop_form()

        stop_ids = [user_input[_KEY_STOP]]
        try:
            data = await self._async_check_stops(stop_ids)
        except _StopCheckError as err:
            return self._show_pick_stop_form(
                errors={_KEY_STOP: err.key}, placeholders=err.placeholders
            )
        return self._create_entry(stop_ids, data)

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual stop ID entry.

        Args:
            user_input: User input with stop IDs or None for initial form.

        Returns:
            Config flow result with form or created entry.

        """
        if user_input is None:
            return self._show_error_form()

        stop_ids, invalid_stop_ids = self._validate_stop_ids(user_input[_KEY_STOP_IDS])
        if not stop_ids and not invalid_stop_ids:
            return self._show_error_form(errors={_KEY_STOP_IDS: "empty_stop_ids"})
        if invalid_stop_ids:
            key = (
                "invalid_stop_id" if len(invalid_stop_ids) == 1 else "invalid_stop_ids"
            )
            return self._show_error_form(
                errors={_KEY_STOP_IDS: key},
                placeholders={
                    "stop_ids": ", ".join(f'"{s}"' for s in invalid_stop_ids)
                },
            )

        try:
            data = await self._async_check_stops(stop_ids)
        except _StopCheckError as err:
            return self._show_error_form(
                errors={_KEY_STOP_IDS: err.key}, placeholders=err.placeholders
            )
        return self._create_entry(stop_ids, data)

    async def _async_check_stops(self, stop_ids: list[str]) -> TransportData:
        duplicates = set(stop_ids) & self._already_configured_stop_ids()
        if duplicates:
            raise _StopCheckError(
                "stop_ids_already_configured", {"stop_ids": ", ".join(duplicates)}
            )

        try:
            data = await self._test_connection(stop_ids)
        except ClientError as err:
            _LOGGER.warning("Wiener Linien API unreachable during setup: %s", err)
            raise _StopCheckError("cannot_connect", {"detail": str(err)}) from err
        except (ValidationError, ParserError) as err:
            _LOGGER.warning(
                "Unexpected Wiener Linien API response during setup: %s", err
            )
            raise _StopCheckError("unexpected_response", {"detail": str(err)}) from err
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error while connecting to Vienna Transport API: %s", err
            )
            raise _StopCheckError("unknown") from err

        requested = {int(s) for s in stop_ids}
        present = set(data.stops.keys())
        missing = requested - present
        if missing:
            _LOGGER.warning("Stop IDs not found in API response: %s", missing)
            raise _StopCheckError(
                "stop_not_found",
                {"stop_ids": ", ".join(str(m) for m in sorted(missing))},
            )

        return data

    def _create_entry(
        self, stop_ids: list[str], data: TransportData
    ) -> ConfigFlowResult:
        return self.async_create_entry(
            title=self._build_title(data),
            data={_KEY_STOP_IDS: stop_ids},
        )

    def _show_error_form(
        self,
        *,
        errors: dict[str, str] | None = None,
        placeholders: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        return self.async_show_form(
            step_id="manual",
            data_schema=_STEP_MANUAL_SCHEMA,
            errors=errors or {},
            description_placeholders={
                "rbl_url": _RBL_SEARCH_URL,
                **(placeholders or {}),
            },
        )

    def _show_pick_stop_form(
        self,
        *,
        errors: dict[str, str] | None = None,
        placeholders: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        stops = self._query.stops(self._line, self._towards)
        return self.async_show_form(
            step_id="pick_stop",
            data_schema=probatio.Schema(
                {
                    probatio.Required(_KEY_STOP): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(stop_id), label=label)
                                for stop_id, label in stops.items()
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
            errors=errors or {},
            description_placeholders={
                "line": self._line,
                "towards": self._towards,
                **(placeholders or {}),
            },
        )

    def _already_configured_stop_ids(self) -> set[str]:
        return {
            stop_id
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            for stop_id in entry.data.get("stop_ids", [])
        }

    async def _test_connection(self, stop_ids: list[str]) -> TransportData:
        session = async_get_clientsession(self.hass)
        client = ViennaTransportClient(session=session)
        validator = ViennaTransportValidator()
        parser = ViennaTransportParser()
        raw_batches = await client.fetch(stop_ids)
        validator.validate(raw_batches)
        return parser.parse(raw_batches)

    @staticmethod
    def _validate_stop_ids(raw: list[str]) -> tuple[list[str], list[str]]:
        cleaned = [s.strip() for s in raw if s.strip()]
        valid = [s for s in cleaned if s.isascii() and s.isdigit()]
        invalid = [s for s in cleaned if not (s.isascii() and s.isdigit())]
        return valid, invalid

    @staticmethod
    def _build_title(data: TransportData) -> str:
        labels = [
            f"{stop.props.name} (ID: {stop.props.id})" for stop in data.stops.values()
        ]
        prefix = "Stop: " if len(data.stops) == 1 else "Stops: "
        return prefix + ", ".join(labels)
