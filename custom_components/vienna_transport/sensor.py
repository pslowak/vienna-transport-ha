"""Sensor platform for Vienna Transport stops."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.vienna_transport.const import DOMAIN
from custom_components.vienna_transport.coordinator import (
    PlatformData,
    ViennaTransportCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vienna Transport sensors for config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry containing platform data.
        async_add_entities: Callback to add entities.

    """
    data: PlatformData = entry.runtime_data

    async_add_entities(
        ViennaTransportSensor(coordinator=data.coordinator, stop_id=int(stop_id))
        for stop_id in data.stop_ids
    )


class ViennaTransportSensor(
    CoordinatorEntity[ViennaTransportCoordinator], SensorEntity
):
    """Sensor entity representing departures for one stop."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ViennaTransportCoordinator, stop_id: int) -> None:
        """Initialize sensor.

        Args:
            coordinator: Data coordinator.
            stop_id: Stop ID for this sensor.

        """
        super().__init__(coordinator)
        self._stop_id = stop_id
        self._attr_unique_id = f"{DOMAIN}_{stop_id}"
        self._attr_name = self._resolve_name(coordinator, stop_id)

    @property
    def available(self) -> bool:
        """Check if sensor is available.

        Returns:
            True if coordinator data contains this stop.

        """
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.stops.get(self._stop_id) is not None
        )

    @property
    def native_value(self) -> str:
        """Return sensor value.

        Returns:
            Always ``ok``; actual data in attributes.

        """
        return "ok"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes with stop data.

        Returns:
            Dictionary with stop departure data or empty if unavailable.

        """
        if self.coordinator.data is None:
            return {}

        stop = self.coordinator.data.stops.get(self._stop_id)
        if stop is None:
            return {}

        return stop.to_dict()

    @staticmethod
    def _resolve_name(coordinator: ViennaTransportCoordinator, stop_id: int) -> str:
        if coordinator.data is not None:
            stop = coordinator.data.stops.get(stop_id)
            if stop is not None:
                return f"Vienna Transport {stop.props.name} (id {stop_id})"

        return f"Vienna Transport {stop_id}"
