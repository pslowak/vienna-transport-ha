from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Vehicle:
    name: str
    type: str
    towards: str
    cooling: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "towards": self.towards,
            "cooling": self.cooling,
        }


@dataclass(frozen=True)
class Departure:
    time_planned: datetime
    time_real: datetime
    vehicle: Vehicle

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_planned": self.time_planned.isoformat(),
            "time_real": self.time_real.isoformat(),
            "vehicle": self.vehicle.to_dict(),
        }


@dataclass(frozen=True)
class Line:
    name: str
    departures: list[Departure]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "departures": [departure.to_dict() for departure in self.departures],
        }


@dataclass(frozen=True)
class StopProperties:
    id: int
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}


@dataclass(frozen=True)
class Stop:
    props: StopProperties
    lines: list[Line]

    def to_dict(self) -> dict[str, Any]:
        return {
            "props": self.props.to_dict(),
            "lines": [line.to_dict() for line in self.lines],
        }


@dataclass(frozen=True)
class TransportData:
    stops: dict[int, Stop]
