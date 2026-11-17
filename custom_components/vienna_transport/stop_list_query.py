"""Queries on the stop list for picking a stop by line."""

import re
from collections import Counter

from custom_components.vienna_transport.stop_list import StopListEntry

_DIGITS = re.compile(r"(\d+)")


class StopListQuery:
    """Answers the questions of picking a stop by line, direction and stop."""

    def __init__(self, entries: list[StopListEntry]) -> None:
        """Initialize query.

        Args:
            entries: Stop list entries to query.

        """
        self._entries = entries

    def lines(self) -> list[str]:
        """Get all lines of the stop list.

        Returns:
            Unique line names in natural order, e.g. "2" before "10A".

        """
        return sorted({entry.line for entry in self._entries}, key=_natural_key)

    def directions(self, line: str) -> list[str]:
        """Get the directions of a line.

        Args:
            line: Line name.

        Returns:
            Unique last stops of the line, sorted by name. Empty for unknown
            lines.

        """
        return sorted({entry.towards for entry in self._entries if entry.line == line})

    def stops(self, line: str, towards: str) -> dict[int, str]:
        """Get the stops of a line in one direction.

        A route can pass two stops of the same name, e.g. at a loop. Their
        labels get the stop ID appended to tell them apart.

        Args:
            line: Line name.
            towards: Last stop of the line in this direction.

        Returns:
            Mapping of stop ID to label, sorted by stop name and stop ID.
            Empty for unknown lines or directions.

        """
        names = {
            entry.stop_id: entry.name
            for entry in self._entries
            if entry.line == line and entry.towards == towards
        }
        counts = Counter(names.values())
        return {
            stop_id: name if counts[name] == 1 else f"{name} ({stop_id})"
            for stop_id, name in sorted(
                names.items(), key=lambda item: (item[1], item[0])
            )
        }


def _natural_key(text: str) -> list[int | str]:
    return [int(part) if part.isdigit() else part for part in _DIGITS.split(text)]
