"""Exceptions for Vienna Transport integration."""


class ClientError(Exception):
    """Raised by ViennaTransportClient on API errors."""


class ValidationError(Exception):
    """Raised by ViennaTransportValidator on invalid API responses."""


class ParserError(Exception):
    """Raised by ViennaTransportParser on parse errors."""
