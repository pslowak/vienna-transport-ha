import logging
from typing import Any

import voluptuous
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from custom_components.vienna_transport_ha import DOMAIN
from custom_components.vienna_transport_ha.client import ViennaTransportClient
from custom_components.vienna_transport_ha.model import TransportData
from custom_components.vienna_transport_ha.parser import ViennaTransportParser

_LOGGER = logging.getLogger(__name__)

KEY_STOP_IDS = "stop_ids"

STEP_USER_SCHEMA = voluptuous.Schema(
    {voluptuous.Required(KEY_STOP_IDS): TextSelector(TextSelectorConfig(multiple=True))}
)


class ViennaTransportConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors = {}

        if user_input is not None:
            stop_ids = self._validate_stop_ids(user_input[KEY_STOP_IDS])

            if not stop_ids:
                errors[KEY_STOP_IDS] = "invalid_stop_ids"
            else:
                data = await self._test_connection(stop_ids)

                if data is None:
                    errors[KEY_STOP_IDS] = "unknown"
                else:
                    return self.async_create_entry(
                        title=self._build_title(data),
                        data={KEY_STOP_IDS: stop_ids},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def _test_connection(self, stop_ids: list[str]) -> TransportData | None:
        session = async_get_clientsession(self.hass)
        client = ViennaTransportClient(session=session)
        parser = ViennaTransportParser()

        try:
            raw = await client.fetch(stop_ids)
            return parser.parse(raw)
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error while connecting to Vienna Transport API: %s", err
            )
            return None

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
            f"{stop.props.name} (id {stop.props.id})" for stop in data.stops.values()
        ]
        return "stops " + ", ".join(labels)
