"""Schema of Wiener Linien API responses.

The schema follows docs/wl-api.md, but only covers the fields the parser reads.
A field is required only if both the API reference and the parser require it.
"""

from enum import IntEnum
from typing import Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    StrictBool,
    StrictInt,
    model_validator,
)


class MessageCode(IntEnum):
    """Message codes of the API response."""

    OK = 1
    DB_UNAVAILABLE = 311
    STOP_NOT_FOUND = 312
    RATE_LIMIT = 316
    INVALID_PARAM = 320
    MISSING_PARAM = 321
    NO_DATA = 322
    UNKNOWN = -1


class Message(BaseModel):
    """Status of the response (`message`)."""

    message_code: StrictInt = Field(default=MessageCode.UNKNOWN, alias="messageCode")


class StopAttributes(BaseModel):
    """Attributes of a stop (`locationStop.properties.attributes`)."""

    # Documented as a string but sent as an integer: lax int accepts both.
    rbl: int


class StopProperties(BaseModel):
    """Properties of a stop (`locationStop.properties`)."""

    title: str
    attributes: StopAttributes


class LocationStop(BaseModel):
    """Stop of a monitor (`locationStop`)."""

    properties: StopProperties


class Vehicle(BaseModel):
    """Vehicle of a departure (`vehicle`)."""

    name: str
    type: str
    towards: str
    cooling: StrictBool = False


class DepartureTime(BaseModel):
    """Planned and real time of a departure (`departureTime`)."""

    # timePlanned is documented as required, but the parser falls back to
    # timeReal, so either one is enough.
    time_planned: AwareDatetime | None = Field(default=None, alias="timePlanned")
    time_real: AwareDatetime | None = Field(default=None, alias="timeReal")

    @model_validator(mode="after")
    def _require_one_time(self) -> Self:
        if self.time_planned is None and self.time_real is None:
            raise ValueError("Both timePlanned and timeReal are missing")
        return self


class Departure(BaseModel):
    """Departure of a line (`departures.departure[]`)."""

    departure_time: DepartureTime = Field(alias="departureTime")
    vehicle: Vehicle | None = None


class Departures(BaseModel):
    """Departures of a line (`departures`)."""

    departure: list[Departure] = Field(default_factory=list)


class Line(BaseModel):
    """Line serving a stop (`lines[]`)."""

    name: str
    towards: str
    type: str
    departures: Departures = Field(default_factory=Departures)


class Monitor(BaseModel):
    """Departures at one stop (`data.monitors[]`)."""

    location_stop: LocationStop = Field(alias="locationStop")
    lines: list[Line] = Field(default_factory=list)
    ref_traffic_info_names: list[str] | None = Field(
        default=None, alias="refTrafficInfoNames"
    )


class TrafficInfoAttributes(BaseModel):
    """Attributes of a traffic info (`attributes`)."""

    reason: str | None = None


class TrafficInfo(BaseModel):
    """Traffic info, e.g. an elevator outage (`data.trafficInfos[]`)."""

    name: str
    description: str
    attributes: TrafficInfoAttributes | None = None
    related_lines: list[str] = Field(default_factory=list, alias="relatedLines")


class MonitorData(BaseModel):
    """Payload of a successful response (`data`)."""

    monitors: list[Monitor] = Field(default_factory=list)
    traffic_infos: list[TrafficInfo] | None = Field(default=None, alias="trafficInfos")


class Response(BaseModel):
    """Response of any message code."""

    message: Message


class OkResponse(Response):
    """Response with message code OK, including its data."""

    data: MonitorData = Field(default_factory=MonitorData)
