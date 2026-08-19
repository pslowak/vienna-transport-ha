from __future__ import annotations


class StopRegistry:
    """Tracks the stop IDs owned by each config entry.

    The union across all registered entries is what the shared coordinator
    fetches in a single API request.
    """

    def __init__(self) -> None:
        self._stops_by_entry: dict[str, set[str]] = {}

    @property
    def stop_ids(self) -> list[str]:
        union: set[str] = set()
        for stop_ids in self._stops_by_entry.values():
            union.update(stop_ids)
        return list(union)

    @property
    def is_empty(self) -> bool:
        return not self._stops_by_entry

    def register(self, entry_id: str, stop_ids: list[str]) -> None:
        self._stops_by_entry[entry_id] = set(stop_ids)

    def unregister(self, entry_id: str) -> None:
        self._stops_by_entry.pop(entry_id, None)

    def stop_ids_for(self, entry_id: str) -> list[str]:
        return list(self._stops_by_entry.get(entry_id, set()))
