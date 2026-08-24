"""Data models for Vienna Transport integration."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Vehicle:
    """Vehicle information.

    Attributes:
        name: Vehicle name.
        type: Vehicle type.
        towards: Destination.
        cooling: Whether vehicle has cooling.

    """

    name: str
    type: str
    towards: str
    cooling: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.

        """
        return {
            "name": self.name,
            "type": self.type,
            "towards": self.towards,
            "cooling": self.cooling,
        }


@dataclass(frozen=True)
class Departure:
    """Departure with planned and real times.

    Attributes:
        time_planned: Scheduled departure time.
        time_real: Real departure time.
        vehicle: Vehicle for departure.

    """

    time_planned: datetime
    time_real: datetime
    vehicle: Vehicle

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.

        """
        return {
            "time_planned": self.time_planned.isoformat(),
            "time_real": self.time_real.isoformat(),
            "vehicle": self.vehicle.to_dict(),
        }


@dataclass(frozen=True)
class Line:
    """Transit line with departures.

    Attributes:
        name: Line name.
        departures: List of departures.

    """

    name: str
    departures: list[Departure]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.

        """
        return {
            "name": self.name,
            "departures": [departure.to_dict() for departure in self.departures],
        }


@dataclass(frozen=True)
class StopProperties:
    """Stop properties.

    Attributes:
        id: Stop ID.
        name: Stop name.

    """

    id: int
    name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.

        """
        return {"id": self.id, "name": self.name}


@dataclass(frozen=True)
class Stop:
    """Stop with properties and lines.

    Attributes:
        props: Stop properties.
        lines: Lines serving stop.

    """

    props: StopProperties
    lines: list[Line]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.

        """
        return {
            "props": self.props.to_dict(),
            "lines": [line.to_dict() for line in self.lines],
        }


@dataclass(frozen=True)
class TransportData:
    """Aggregated transport data.

    Attributes:
        stops: Mapping of stop ID to stop data.

    """

    stops: dict[int, Stop]
