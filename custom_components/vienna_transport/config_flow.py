"""Config flow for Vienna Transport integration."""

import logging
from typing import Any

import voluptuous
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.exceptions import ClientError, ParserError
from custom_components.vienna_transport.model import TransportData
from custom_components.vienna_transport.parser import ViennaTransportParser

_LOGGER = logging.getLogger(__name__)

_KEY_STOP_IDS = "stop_ids"
_RBL_SEARCH_URL = "https://till.mabe.at/rbl/"
_STEP_USER_SCHEMA = voluptuous.Schema(
    {
        voluptuous.Required(_KEY_STOP_IDS): TextSelector(
            TextSelectorConfig(multiple=True)
        )
    }
)


class ViennaTransportConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Vienna Transport.

    Handles user input for stop IDs, validation, duplicate check, and connection test.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial user step.

        Args:
            user_input: User input with stop IDs or None for initial form.

        Returns:
            Config flow result with form or created entry.

        """
        if user_input is None:
            return self._show_error_form()

        stop_ids = self._validate_stop_ids(user_input[_KEY_STOP_IDS])
        if not stop_ids:
            return self._show_error_form(errors={_KEY_STOP_IDS: "invalid_stop_ids"})

        duplicates = set(stop_ids) & self._already_configured_stop_ids()
        if duplicates:
            return self._show_error_form(
                errors={_KEY_STOP_IDS: "stop_ids_already_configured"},
                placeholders={"stop_ids": ", ".join(duplicates)},
            )

        try:
            data = await self._test_connection(stop_ids)
        except ClientError as err:
            _LOGGER.warning("Wiener Linien API unreachable during setup: %s", err)
            return self._show_error_form(
                errors={_KEY_STOP_IDS: "cannot_connect"},
                placeholders={"detail": str(err)},
            )
        except ParserError as err:
            _LOGGER.warning(
                "Unexpected Wiener Linien API response during setup: %s", err
            )
            return self._show_error_form(
                errors={_KEY_STOP_IDS: "unexpected_response"},
                placeholders={"detail": str(err)},
            )
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error while connecting to Vienna Transport API: %s", err
            )
            return self._show_error_form(errors={_KEY_STOP_IDS: "unknown"})

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
            step_id="user",
            data_schema=_STEP_USER_SCHEMA,
            errors=errors or {},
            description_placeholders={
                "rbl_url": _RBL_SEARCH_URL,
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
        parser = ViennaTransportParser()
        raw = await client.fetch(stop_ids)
        return parser.parse(raw)

    @staticmethod
    def _validate_stop_ids(raw: list[str]) -> list[str]:
        cleaned = [s.strip() for s in raw if s.strip()]

        if not cleaned:
            return []

        if not all(s.isdigit() for s in cleaned):
            return []

        return cleaned

    @staticmethod
    def _build_title(data: TransportData) -> str:
        labels = [
            f"{stop.props.name} (ID: {stop.props.id})" for stop in data.stops.values()
        ]
        prefix = "Stop: " if len(data.stops) == 1 else "Stops: "
        return prefix + ", ".join(labels)
