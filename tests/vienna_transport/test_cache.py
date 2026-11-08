from datetime import timedelta

from freezegun import freeze_time

from custom_components.vienna_transport.cache import ExpiringCache
from custom_components.vienna_transport.model import Stop, StopProperties


def _stop(stop_id: int) -> Stop:
    return Stop(props=StopProperties(id=stop_id, name=f"Stop {stop_id}"), lines=[])


def test_get_returns_none_when_empty() -> None:
    cache = ExpiringCache()

    assert cache.get(1) is None


def test_set_stores_stop() -> None:
    cache = ExpiringCache()
    stop = _stop(1)

    cache.set(stop)

    assert cache.get(1) is stop


def test_get_returns_none_for_unknown_stop() -> None:
    cache = ExpiringCache()

    cache.set(_stop(1))

    assert cache.get(2) is None


def test_get_respects_ttl() -> None:
    cache = ExpiringCache(ttl=timedelta(minutes=3))
    stop = _stop(1)

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(stop)

        frozen.tick(timedelta(minutes=2))
        assert cache.get(1) is stop

        frozen.tick(timedelta(minutes=2))
        assert cache.get(1) is None


def test_set_replaces_previous_stop() -> None:
    cache = ExpiringCache()
    old = _stop(1)
    new = _stop(1)

    cache.set(old)
    cache.set(new)

    assert cache.get(1) is new


def test_resets_ttl_on_new_set() -> None:
    cache = ExpiringCache(ttl=timedelta(minutes=3))

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(_stop(1))

        frozen.tick(timedelta(minutes=2))

        other = _stop(1)
        cache.set(other)

        frozen.tick(timedelta(minutes=2))
        assert cache.get(1) is other

        frozen.tick(timedelta(minutes=2))
        assert cache.get(1) is None


def test_stops_expire_independently() -> None:
    cache = ExpiringCache(ttl=timedelta(minutes=3))
    newer = _stop(2)

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(_stop(1))

        frozen.tick(timedelta(minutes=2))
        cache.set(newer)

        frozen.tick(timedelta(minutes=2))
        assert cache.get(1) is None
        assert cache.get(2) is newer


def test_set_keeps_expired_stops_before_eviction_interval() -> None:
    cache = ExpiringCache(
        ttl=timedelta(minutes=3), eviction_interval=timedelta(minutes=10)
    )

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(_stop(1))

        frozen.tick(timedelta(minutes=4))
        cache.set(_stop(2))

        assert set(cache._entries) == {1, 2}


def test_set_evicts_expired_stops_after_eviction_interval() -> None:
    cache = ExpiringCache(
        ttl=timedelta(minutes=3), eviction_interval=timedelta(minutes=10)
    )
    newer = _stop(2)

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(_stop(1))

        frozen.tick(timedelta(minutes=8))
        cache.set(newer)

        frozen.tick(timedelta(minutes=2))
        cache.set(_stop(3))

        assert set(cache._entries) == {2, 3}
        assert cache.get(2) is newer


def test_set_restarts_eviction_interval_after_eviction() -> None:
    cache = ExpiringCache(
        ttl=timedelta(minutes=3), eviction_interval=timedelta(minutes=10)
    )

    with freeze_time("2026-01-01 12:00:00+00:00") as frozen:
        cache.set(_stop(1))

        frozen.tick(timedelta(minutes=10))
        cache.set(_stop(2))

        frozen.tick(timedelta(minutes=9))
        cache.set(_stop(3))

        assert set(cache._entries) == {2, 3}
