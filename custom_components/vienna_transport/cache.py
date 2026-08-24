"""Cache for transport data with TTL expiry."""

from datetime import UTC, datetime, timedelta

from custom_components.vienna_transport.model import TransportData


class ExpiringCache:
    """Expiring cache for transport data.

    Stores ``TransportData`` with timestamp and returns ``None`` after TTL expires.
    """

    def __init__(self, ttl: timedelta = timedelta(minutes=3)) -> None:
        """Initialize cache.

        Args:
            ttl: Time to live for cached data.

        """
        self._ttl = ttl
        self._timestamp: datetime | None = None
        self._data: TransportData | None = None

    def set(self, data: TransportData) -> None:
        """Store transport data in cache.

        Args:
            data: Transport data to cache.

        """
        self._timestamp = datetime.now(UTC)
        self._data = data

    def get(self) -> TransportData | None:
        """Retrieve cached data if not expired.

        Returns:
            Cached transport data or ``None`` if empty or expired.

        """
        if self._timestamp is None:
            return None
        if self._data is None:
            return None

        age = datetime.now(UTC) - self._timestamp
        if age > self._ttl:
            return None

        return self._data
