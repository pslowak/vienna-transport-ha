import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.vienna_transport.client import ViennaTransportClient
from custom_components.vienna_transport.model import TransportData
from custom_components.vienna_transport.parser import ViennaTransportParser

_LOGGER = logging.getLogger(__name__)


class ViennaTransportCoordinator(DataUpdateCoordinator[TransportData]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: ViennaTransportClient,
        parser: ViennaTransportParser,
        stop_ids: list[str],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Vienna Transport Data Coordinator",
            update_interval=timedelta(seconds=60),
        )
        self._client = client
        self._parser = parser
        self.stop_ids = stop_ids

    async def _async_update_data(self) -> TransportData:
        raw = await self._client.fetch(self.stop_ids)
        return self._parser.parse(raw)
