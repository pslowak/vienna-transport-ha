from datetime import timedelta
from unittest.mock import MagicMock

from freezegun import freeze_time

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.model import Stop, TransportData


def test_get_returns_none_when_empty() -> None:
    cache = ExpiringCache()

    assert cache.get() is None


def test_set_stores_data() -> None:
    cache = ExpiringCache()
    data = TransportData(stops={1: MagicMock(spec=Stop)})

    cache.set(data)

    assert cache.get() is data


def test_get_respects_ttl() -> None:
    cache = ExpiringCache(ttl=timedelta(minutes=3))
    data = TransportData(stops={1: MagicMock(spec=Stop)})

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(data)

        frozen.tick(timedelta(minutes=2))
        assert cache.get() is data

        frozen.tick(timedelta(minutes=2))
        assert cache.get() is None


def test_set_replaces_previous_data() -> None:
    cache = ExpiringCache()
    old = TransportData(stops={})
    new = TransportData(stops={1: MagicMock(spec=Stop)})

    cache.set(old)
    cache.set(new)

    assert cache.get() is new
    assert cache.get() is not old


def test_resets_ttl_on_new_set() -> None:
    cache = ExpiringCache(ttl=timedelta(minutes=3))
    data = TransportData(stops={1: MagicMock(spec=Stop)})

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(data)

        frozen.tick(timedelta(minutes=2))

        other = TransportData(stops={})
        cache.set(other)

        frozen.tick(timedelta(minutes=2))
        assert cache.get() is other

        frozen.tick(timedelta(minutes=2))
        assert cache.get() is None
