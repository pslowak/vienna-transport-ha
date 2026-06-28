class ClientError(Exception):
    """Raised by ViennaTransportClient on API errors."""


class ParserError(Exception):
    """Raised by ViennaTransportParser on parse errors."""
