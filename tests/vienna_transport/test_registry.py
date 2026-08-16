from custom_components.vienna_transport.registry import StopRegistry


def test_stop_ids_empty_when_nothing_registered() -> None:
    registry = StopRegistry()
    assert registry.stop_ids == []
    assert registry.is_empty is True


def test_stop_ids_union_across_entries() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683", "1337"])
    registry.register("entry-2", ["5566"])
    assert set(registry.stop_ids) == {"2683", "1337", "5566"}


def test_stop_ids_deduplicates_across_entries() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683"])
    registry.register("entry-2", ["2683", "1337"])
    assert set(registry.stop_ids) == {"2683", "1337"}


def test_stop_ids_for_returns_only_own_entry() -> None:
    key = "entry-1"
    registry = StopRegistry()
    registry.register(key, ["2683"])
    registry.register("entry-2", ["1337"])
    assert registry.stop_ids_for(key) == ["2683"]
    assert registry.stop_ids_for("unknown") == []


def test_unregister_removes_entry_stops() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683"])
    registry.register("entry-2", ["1337"])
    registry.unregister("entry-1")
    assert registry.stop_ids == ["1337"]
    assert registry.is_empty is False


def test_unregister_last_entry_empties_registry() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683"])
    registry.unregister("entry-1")
    assert registry.stop_ids == []
    assert registry.is_empty is True


def test_register_overwrites_existing_entry() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683"])
    registry.register("entry-1", ["1337"])
    assert registry.stop_ids == ["1337"]


def test_register_deduplicates_within_entry() -> None:
    registry = StopRegistry()
    registry.register("entry-1", ["2683", "2683"])
    registry.register("entry-2", ["2683", "1337"])
    assert set(registry.stop_ids) == {"2683", "1337"}
