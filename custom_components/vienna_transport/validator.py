"""Validator for Wiener Linien API responses."""

import logging
from typing import Any

import pydantic

from custom_components.vienna_transport.exceptions import ValidationError
from custom_components.vienna_transport.schema import (
    MessageCode,
    OkResponse,
    Response,
)

_LOGGER = logging.getLogger(__name__)


class ViennaTransportValidator:
    """Validator for checking raw API data before it is parsed."""

    def validate(self, raw_batches: list[dict[str, Any]]) -> list[Response]:
        """Validate batched raw API responses.

        Only successful responses are checked in full: Responses with any other
        message code carry no data and are left for the parser to report.

        Args:
            raw_batches: Raw JSON responses from Wiener Linien monitor API,
                one per batch.

        Returns:
            One validated response per batch, in the same order: an OkResponse
            for a successful batch, a Response with only its message otherwise.

        Raises:
            ValidationError: If any batch does not match the expected structure.

        """
        _LOGGER.debug("Validating %d batch(es)", len(raw_batches))
        return [self._validate_one(raw) for raw in raw_batches]

    @staticmethod
    def _validate_one(raw: dict[str, Any]) -> Response:
        try:
            response = Response.model_validate(raw)
            if response.message.message_code == MessageCode.OK:
                return OkResponse.model_validate(raw)
            return response
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
