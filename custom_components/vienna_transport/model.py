from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Vehicle:
    name: str
    type: str
    towards: str
    cooling: bool


@dataclass(frozen=True)
class Departure:
    time_planned: datetime
    time_real: datetime
    vehicle: Vehicle


@dataclass(frozen=True)
class Line:
    name: str
    departures: list[Departure]


@dataclass(frozen=True)
class StopProperties:
    id: int
    name: str


@dataclass(frozen=True)
class Stop:
    props: StopProperties
    lines: list[Line]


@dataclass(frozen=True)
class TransportData:
    stops: dict[int, Stop]
