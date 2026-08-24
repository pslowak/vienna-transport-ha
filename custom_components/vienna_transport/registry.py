"""Registry for stop IDs owned by config entries."""

from __future__ import annotations


class StopRegistry:
    """Tracks the stop IDs owned by each config entry."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._stops_by_entry: dict[str, set[str]] = {}

    @property
    def stop_ids(self) -> list[str]:
        """Union of stop IDs across all entries.

        Returns:
            List of unique stop IDs.

        """
        union: set[str] = set()
        for stop_ids in self._stops_by_entry.values():
            union.update(stop_ids)
        return list(union)

    @property
    def is_empty(self) -> bool:
        """Check if registry is empty.

        Returns:
            True if no entries registered.

        """
        return not self._stops_by_entry

    def register(self, entry_id: str, stop_ids: list[str]) -> None:
        """Register stop IDs for a config entry.

        Args:
            entry_id: Config entry ID.
            stop_ids: List of stop IDs to register.

        """
        self._stops_by_entry[entry_id] = set(stop_ids)

    def unregister(self, entry_id: str) -> None:
        """Unregister a config entry.

        Args:
            entry_id: Config entry ID to remove.

        """
        self._stops_by_entry.pop(entry_id, None)

    def stop_ids_for(self, entry_id: str) -> list[str]:
        """Get stop IDs for a specific entry.

        Args:
            entry_id: Config entry ID.

        Returns:
            List of stop IDs for entry, empty if not found.

        """
        return list(self._stops_by_entry.get(entry_id, set()))
