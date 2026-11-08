"""Validator for Wiener Linien API responses.

The schema follows docs/wl-api.md, but only covers the fields the parser reads.
A field is required only if both the API reference and the parser require it.
"""

import logging
from typing import Any, Self

import pydantic
from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    StrictBool,
    StrictInt,
    model_validator,
)

from custom_components.vienna_transport.exceptions import ValidationError

_LOGGER = logging.getLogger(__name__)

_MSG_CODE_OK = 1
_MSG_CODE_UNKNOWN = -1


class _Message(BaseModel):
    message_code: StrictInt = Field(default=_MSG_CODE_UNKNOWN, alias="messageCode")


class _StopAttributes(BaseModel):
    # Documented as a string but sent as an integer: lax int accepts both.
    rbl: int


class _StopProperties(BaseModel):
    title: str
    attributes: _StopAttributes


class _LocationStop(BaseModel):
    properties: _StopProperties


class _Vehicle(BaseModel):
    name: str
    type: str
    towards: str
    cooling: StrictBool = False


class _DepartureTime(BaseModel):
    # timePlanned is documented as required, but the parser falls back to
    # timeReal, so either one is enough.
    time_planned: AwareDatetime | None = Field(default=None, alias="timePlanned")
    time_real: AwareDatetime | None = Field(default=None, alias="timeReal")

    @model_validator(mode="after")
    def _require_one_time(self) -> Self:
        if self.time_planned is None and self.time_real is None:
            raise ValueError("Both timePlanned and timeReal are missing")
        return self


class _Departure(BaseModel):
    departure_time: _DepartureTime = Field(alias="departureTime")
    vehicle: _Vehicle | None = None


class _Departures(BaseModel):
    departure: list[_Departure] = Field(default_factory=list)


class _Line(BaseModel):
    name: str
    departures: _Departures = Field(default_factory=_Departures)


class _Monitor(BaseModel):
    location_stop: _LocationStop = Field(alias="locationStop")
    lines: list[_Line] = Field(default_factory=list)
    ref_traffic_info_names: list[str] | None = Field(
        default=None, alias="refTrafficInfoNames"
    )


class _TrafficInfoAttributes(BaseModel):
    reason: str | None = None


class _TrafficInfo(BaseModel):
    name: str
    description: str
    attributes: _TrafficInfoAttributes | None = None
    related_lines: list[str] = Field(default_factory=list, alias="relatedLines")


class _MonitorData(BaseModel):
    monitors: list[_Monitor] = Field(default_factory=list)
    traffic_infos: list[_TrafficInfo] | None = Field(default=None, alias="trafficInfos")


class _Response(BaseModel):
    message: _Message


class _OkResponse(_Response):
    data: _MonitorData = Field(default_factory=_MonitorData)


class ViennaTransportValidator:
    """Validator for checking raw API data before it is parsed."""

    def validate(self, raw_batches: list[dict[str, Any]]) -> None:
        """Validate batched raw API responses.

        Only successful responses are checked in full: Responses with any other
        message code carry no data and are left for the parser to report.

        Args:
            raw_batches: Raw JSON responses from Wiener Linien monitor API,
                one per batch.

        Raises:
            ValidationError: If any batch does not match the expected structure.

        """
        _LOGGER.debug("Validating %d batch(es)", len(raw_batches))
        for raw in raw_batches:
            self._validate_one(raw)

    @staticmethod
    def _validate_one(raw: dict[str, Any]) -> None:
        try:
            response = _Response.model_validate(raw)
            if response.message.message_code == _MSG_CODE_OK:
                _OkResponse.model_validate(raw)
        except pydantic.ValidationError as e:
            error = ViennaTransportValidator._to_validation_error(e)
            _LOGGER.warning("%s", error)
            _LOGGER.debug("API response raw: %s", raw)
            raise error from e

    @staticmethod
    def _to_validation_error(error: pydantic.ValidationError) -> ValidationError:
        first = error.errors(include_url=False, include_input=False)[0]
        path = ".".join(str(part) for part in first["loc"]) or "response"
        return ValidationError(f"unexpected API response: {path}: {first['msg']}")
