"""Build a stop list from Wiener Linien open government data.

The stop list is a CSV table with one row per stop, line and direction
(stop_id;name;line;towards). It is built from three open data tables:

- stops (Haltepunkte): ID and name of each stop
- lines (Linien): name and realtime availability of each line
- routes (Fahrwegverlaeufe): the stops of each route of each line

Usage:
    uv run scripts/build_stop_list.py [--source DIR] [--output FILE]
"""

import argparse
import csv
import io
import logging
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import requests

_LOGGER = logging.getLogger(__name__)

_OGD_BASE_URL = "https://www.wienerlinien.at/ogd_realtime/doku/ogd/"
_STOPS_TABLE = "wienerlinien-ogd-haltepunkte.csv"
_LINES_TABLE = "wienerlinien-ogd-linien.csv"
_ROUTES_TABLE = "wienerlinien-ogd-fahrwegverlaeufe.csv"

_ENCODING = "utf-8-sig"
_REQUEST_TIMEOUT = 30
_DELIMITER = ";"

_DEFAULT_OUTPUT = Path("stops.csv")
_STOP_LIST_HEADER = ("stop_id", "name", "line", "towards")


@dataclass(frozen=True)
class SourceStop:
    """A stop from the stops table.

    Attributes:
        stop_id: Stop ID (RBL number).
        name: Stop name.

    """

    stop_id: int
    name: str


@dataclass(frozen=True)
class SourceLine:
    """A line from the lines table.

    Attributes:
        line_id: Line ID.
        name: Line name, e.g. "U1" or "13A".
        has_realtime: Whether the realtime API reports departures of the line.

    """

    line_id: int
    name: str
    has_realtime: bool


@dataclass(frozen=True)
class RoutePoint:
    """A stop on a route pattern from the routes table.

    A pattern is one path a line can run: an ordered list of stops from a
    start to an end. Besides the regular route, a line has patterns for
    short runs, depot runs and turning maneuvers. Bus 13A in direction 1,
    for example (data of November 2026):

    - pattern 1: Alser Straße -> Hauptbahnhof, 18 stops (regular route)
    - pattern 3: Alser Straße -> Belvederegasse (short run)

    Pattern IDs are unique within a line only, and each pattern belongs to
    exactly one direction.

    Attributes:
        line_id: Line ID.
        pattern_id: ID of the pattern within its line.
        direction: Direction of the pattern, missing on some rows.
        position: Position of the stop on the pattern. Numbers may be
            skipped, so only their order matters.
        stop_id: Stop ID.

    """

    line_id: int
    pattern_id: int
    direction: int | None
    position: int
    stop_id: int


@dataclass(frozen=True)
class Route:
    """The stops a line serves in one direction.

    Attributes:
        line_id: Line ID.
        direction: Direction of the route.
        stop_ids: Stop IDs in the order the line serves them.

    """

    line_id: int
    direction: int
    stop_ids: tuple[int, ...]


@dataclass(frozen=True)
class StopLine:
    """A line departing from a stop in one direction, a row of the stop list.

    Attributes:
        stop_id: Stop ID (RBL number) used to request departures.
        name: Stop name.
        line: Line name.
        towards: Last stop of the line in this direction.

    """

    stop_id: int
    name: str
    line: str
    towards: str


def load_table(name: str, source: Path | None) -> str:
    """Load a table from a local directory, or download it if there is none.

    Args:
        name: File name of the table.
        source: Directory with previously downloaded tables, or None.

    Returns:
        Content of the table.

    """
    if source is None:
        return download_table(name)
    return read_table(name, source)


def download_table(name: str) -> str:
    """Download a table from the Wiener Linien open data server.

    Args:
        name: File name of the table.

    Returns:
        Content of the table.

    Raises:
        requests.RequestException: If the download fails.
        UnicodeDecodeError: If the downloaded table is not valid UTF-8.

    """
    url = _OGD_BASE_URL + name
    _LOGGER.info("Downloading %s", url)
    response = requests.get(url, timeout=_REQUEST_TIMEOUT)
    response.raise_for_status()
    # Decode explicitly: the server declares the tables as text/html without a
    # charset, so response.text would decode them as ISO-8859-1.
    return response.content.decode(_ENCODING)


def read_table(name: str, directory: Path) -> str:
    """Read a previously downloaded table.

    Args:
        name: File name of the table.
        directory: Directory containing the table.

    Returns:
        Content of the table.

    """
    return (directory / name).read_text(encoding=_ENCODING)


def parse_stops(content: str) -> list[SourceStop]:
    """Parse the stops table.

    Args:
        content: Content of the table.

    Returns:
        Stops in table order.

    """
    return [
        SourceStop(
            stop_id=int(row["StopID"]),
            name=row["StopText"].strip(),
        )
        for row in _read_rows(content)
    ]


def parse_lines(content: str) -> list[SourceLine]:
    """Parse the lines table.

    Args:
        content: Content of the table.

    Returns:
        Lines in table order.

    """
    return [
        SourceLine(
            line_id=int(row["LineID"]),
            name=row["LineText"],
            has_realtime=row["Realtime"] == "1",
        )
        for row in _read_rows(content)
    ]


def parse_route_points(content: str) -> list[RoutePoint]:
    """Parse the routes table.

    Args:
        content: Content of the table.

    Returns:
        Route points in table order.

    """
    return [
        RoutePoint(
            line_id=int(row["LineID"]),
            pattern_id=int(row["PatternID"]),
            # Rows lacking the column get None, empty columns an empty string.
            direction=int(row["Direction"]) if row["Direction"] else None,
            position=int(row["StopSeqCount"]),
            stop_id=int(row["StopID"]),
        )
        for row in _read_rows(content)
    ]


def _read_rows(content: str) -> csv.DictReader[str]:
    return csv.DictReader(io.StringIO(content), delimiter=_DELIMITER)


def find_main_routes(points: list[RoutePoint]) -> list[Route]:
    """Find the main route of each line direction.

    Besides its regular route, a line direction has patterns for short runs,
    depot runs, diversions and through runs onto other lines. The data doesn't
    mark the regular route, so it is assumed to be the pattern with the lowest
    pattern ID (note that this is an assumption).

    The pattern with the most stops is not a better choice: it differs from
    the lowest pattern ID in about a third of the line directions, and is
    then mostly a diversion, depot run or through run. Those add stops to the
    regular route, so the line would be listed at stops it doesn't normally
    serve.

    Args:
        points: Route points of all lines.

    Returns:
        One route per line direction.

    """
    return [
        _main_route(line_id, direction, direction_points)
        for (line_id, direction), direction_points in _group_by_direction(
            points
        ).items()
    ]


def _group_by_direction(
    points: list[RoutePoint],
) -> dict[tuple[int, int], list[RoutePoint]]:
    # Points without a direction are skipped. Lines without any direction
    # are lost.
    groups: dict[tuple[int, int], list[RoutePoint]] = defaultdict(list)
    for point in points:
        if point.direction is not None:
            groups[(point.line_id, point.direction)].append(point)
    return groups


def _main_route(line_id: int, direction: int, points: list[RoutePoint]) -> Route:
    main_pattern_id = min(point.pattern_id for point in points)
    main_points = [point for point in points if point.pattern_id == main_pattern_id]
    main_points.sort(key=lambda point: point.position)
    return Route(
        line_id=line_id,
        direction=direction,
        stop_ids=tuple(point.stop_id for point in main_points),
    )


def build_stop_lines(
    stops: list[SourceStop], lines: list[SourceLine], routes: list[Route]
) -> list[StopLine]:
    """Build the stop list entries of the given routes.

    Each stop of a route becomes an entry, with the last stop of the route as
    its direction. Left out are:

    - lines without realtime data, as no departures are reported for them
    - the last stop and stops named like it, as the line only arrives there
    - stops without a name or missing from the stops table

    Args:
        stops: Stops of all lines.
        lines: All lines.
        routes: Routes to convert, usually the main route of each direction.

    Returns:
        Entries sorted by stop name, stop ID, line and direction.

    """
    stops_by_id = {stop.stop_id: stop for stop in stops}
    lines_by_id = {line.line_id: line for line in lines if line.has_realtime}
    stop_lines = {
        stop_line
        for route in routes
        if route.line_id in lines_by_id
        for stop_line in _route_stop_lines(
            route, lines_by_id[route.line_id], stops_by_id
        )
    }
    return sorted(stop_lines, key=lambda s: (s.name, s.stop_id, s.line, s.towards))


def _route_stop_lines(
    route: Route, line: SourceLine, stops_by_id: dict[int, SourceStop]
) -> Iterator[StopLine]:
    known_stops = [stops_by_id[i] for i in route.stop_ids if i in stops_by_id]
    if not known_stops:
        return
    *departure_stops, last_stop = known_stops
    for stop in departure_stops:
        if _is_listed(stop, last_stop):
            yield StopLine(
                stop_id=stop.stop_id,
                name=stop.name,
                line=line.name,
                towards=last_stop.name,
            )


def _is_listed(stop: SourceStop, last_stop: SourceStop) -> bool:
    # Stops named like the last stop are typically its arrival platform just
    # before a turning loop.
    return bool(stop.name) and stop.name != last_stop.name


def write_stop_list(stop_lines: list[StopLine], path: Path) -> None:
    """Write the stop list as a semicolon separated CSV file.

    Args:
        stop_lines: Stop lines in the order to write them.
        path: Path of the CSV file.

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=_DELIMITER, lineterminator="\n")
        writer.writerow(_STOP_LIST_HEADER)
        writer.writerows((s.stop_id, s.name, s.line, s.towards) for s in stop_lines)


def main(argv: list[str] | None = None) -> None:
    """Build the stop list from downloaded or local open data tables.

    Args:
        argv: Command line arguments, those of the process by default.

    """
    args = _parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    stops = parse_stops(load_table(_STOPS_TABLE, args.source))
    lines = parse_lines(load_table(_LINES_TABLE, args.source))
    route_points = parse_route_points(load_table(_ROUTES_TABLE, args.source))
    stop_lines = build_stop_lines(stops, lines, find_main_routes(route_points))

    write_stop_list(stop_lines, args.output)
    _LOGGER.info(
        "Wrote %d entries for %d stops to %s",
        len(stop_lines),
        len({stop_line.stop_id for stop_line in stop_lines}),
        args.output,
    )


@dataclass(frozen=True)
class _Arguments:
    """Command line arguments.

    Attributes:
        source: Directory with previously downloaded tables, or None to
            download them.
        output: Path of the stop list to write.

    """

    source: Path | None
    output: Path


def _parse_args(argv: list[str] | None) -> _Arguments:
    parser = argparse.ArgumentParser(
        description="Build a stop list from Wiener Linien open data.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="directory with previously downloaded tables (downloads if omitted)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"path of the stop list to write (default: {_DEFAULT_OUTPUT})",
    )
    namespace = parser.parse_args(argv)
    return _Arguments(source=namespace.source, output=namespace.output)


if __name__ == "__main__":
    main()
