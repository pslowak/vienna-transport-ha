"""Cache for stops with TTL expiry."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from custom_components.vienna_transport.model import Stop

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Entry:
    timestamp: datetime
    stop: Stop


class ExpiringCache:
    """Expiring cache for stops.

    Stores each ``Stop`` with its own timestamp and returns ``None`` after TTL
    expires. Expired entries are evicted periodically on write, so memory
    stays bounded without callers having to trigger cleanup.
    """

    def __init__(
        self,
        ttl: timedelta = timedelta(minutes=3),
        eviction_interval: timedelta = timedelta(minutes=10),
    ) -> None:
        """Initialize cache.

        Args:
            ttl: Time to live for each cached stop.
            eviction_interval: Minimum time between evictions of expired stops.

        """
        self._ttl = ttl
        self._eviction_interval = eviction_interval
        self._entries: dict[int, _Entry] = {}
        self._last_eviction: datetime | None = None

    def set(self, stop: Stop) -> None:
        """Store stop in cache and evict expired entries if due.

        Args:
            stop: Stop to cache, keyed by its ID.

        """
        now = datetime.now(UTC)

        # An entry is only replaced when its stop is written again. Stops that
        # are no longer fetched, e.g. after their config entry was removed, or
        # that keep failing are never written again, so their expired entries
        # would stay in the cache forever and bloat memory. Expired entries
        # therefore have to be evicted.
        #
        # The obvious place to evict is on every read or write. However, each
        # eviction scans all entries, which turns constant-time `get` and `set`
        # into linear-time operations, and a poll that writes all stops into a
        # quadratic-time one.
        #
        # As a compromise, expired entries are evicted on write, but at most
        # once per eviction interval. This keeps `get` and `set` constant-time
        # apart from the occasional scan, while still bounding the lifetime of
        # an expired entry to TTL plus eviction interval. Since `get` checks
        # the TTL itself, expired entries are never returned while they wait
        # for eviction.
        if self._is_eviction_due(now):
            self._evict_expired(now)
        self._entries[stop.props.id] = _Entry(timestamp=now, stop=stop)

    def get(self, stop_id: int) -> Stop | None:
        """Retrieve cached stop if not expired.

        Args:
            stop_id: ID of the stop to retrieve.

        Returns:
            Cached stop or ``None`` if missing or expired.

        """
        entry = self._entries.get(stop_id)
        if entry is None or self._is_expired(entry, datetime.now(UTC)):
            return None
        return entry.stop

    def _is_eviction_due(self, now: datetime) -> bool:
        return (
            self._last_eviction is None
            or now - self._last_eviction >= self._eviction_interval
        )

    def _evict_expired(self, now: datetime) -> None:
        expired = [
            stop_id
            for stop_id, entry in self._entries.items()
            if self._is_expired(entry, now)
        ]
        for stop_id in expired:
            del self._entries[stop_id]
        self._last_eviction = now
        if expired:
            _LOGGER.debug("Evicted %d expired stop(s): %s", len(expired), expired)

    def _is_expired(self, entry: _Entry, now: datetime) -> bool:
        return now - entry.timestamp > self._ttl
