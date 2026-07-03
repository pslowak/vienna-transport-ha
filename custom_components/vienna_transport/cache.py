from datetime import UTC, datetime, timedelta

from custom_components.vienna_transport.model import TransportData


class ExpiringCache:
    def __init__(self, ttl: timedelta = timedelta(minutes=3)) -> None:
        self._ttl = ttl
        self._timestamp: datetime | None = None
        self._data: TransportData | None = None

    def set(self, data: TransportData) -> None:
        self._timestamp = datetime.now(UTC)
        self._data = data

    def get(self) -> TransportData | None:
        if self._timestamp is None:
            return None
        if self._data is None:
            return None

        age = datetime.now(UTC) - self._timestamp
        if age > self._ttl:
            return None

        return self._data
