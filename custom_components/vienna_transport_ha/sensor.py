from dataclasses import asdict

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.vienna_transport_ha import DOMAIN, ViennaTransportCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        ViennaTransportSensor(coordinator=coordinator, stop_id=int(stop_id))
        for stop_id in coordinator.stop_ids
    )


class ViennaTransportSensor(
    CoordinatorEntity[ViennaTransportCoordinator], SensorEntity
):
    """
    A sensor entity representing departures for one stop.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: ViennaTransportCoordinator, stop_id: int) -> None:
        super().__init__(coordinator)
        self._stop_id = stop_id
        self._attr_unique_id = f"{DOMAIN}_{stop_id}"
        self._attr_name = self._resolve_name(coordinator, stop_id)

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.stops.get(self._stop_id) is not None
        )

    @property
    def native_value(self) -> str:
        return "ok"

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {}

        stop = self.coordinator.data.stops.get(self._stop_id)
        if stop is None:
            return {}

        return asdict(stop)

    @staticmethod
    def _resolve_name(coordinator: ViennaTransportCoordinator, stop_id: int) -> str:
        if coordinator.data is not None:
            stop = coordinator.data.stops.get(stop_id)
            if stop is not None:
                return f"Vienna Transport {stop.props.name} (id {stop_id})"

        return f"Vienna Transport {stop_id}"
