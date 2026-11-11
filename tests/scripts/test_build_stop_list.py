from pathlib import Path

import pytest
import requests
import responses
from responses import matchers

from scripts.build_stop_list import (
    Route,
    RoutePoint,
    SourceLine,
    SourceStop,
    StopLine,
    build_stop_lines,
    download_table,
    find_main_routes,
    load_table,
    main,
    parse_lines,
    parse_route_points,
    parse_stops,
    read_table,
    write_stop_list,
)

URL = "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-linien.csv"
BYTE_ORDER_MARK = "\ufeff"


def stop(stop_id: int, name: str) -> SourceStop:
    return SourceStop(stop_id=stop_id, name=name)


def line(line_id: int, name: str, *, has_realtime: bool = True) -> SourceLine:
    return SourceLine(line_id=line_id, name=name, has_realtime=has_realtime)


def route(line_id: int, *stop_ids: int) -> Route:
    return Route(line_id=line_id, direction=1, stop_ids=stop_ids)


def route_points(
    line_id: int, pattern_id: int, direction: int | None, *stop_ids: int
) -> list[RoutePoint]:
    return [
        RoutePoint(
            line_id=line_id,
            pattern_id=pattern_id,
            direction=direction,
            position=position,
            stop_id=stop_id,
        )
        for position, stop_id in enumerate(stop_ids)
    ]


@pytest.fixture
def stops() -> list[SourceStop]:
    return [
        stop(1, "Start"),
        stop(2, "Middle"),
        stop(3, "End"),
    ]


@responses.activate
def test_download_table_requests_table_from_open_data_server() -> None:
    responses.get(
        URL,
        body=b"LineID;LineText\n301;U1\n",
        match=[matchers.request_kwargs_matcher({"timeout": 30})],
    )

    assert download_table("wienerlinien-ogd-linien.csv") == "LineID;LineText\n301;U1\n"


@responses.activate
def test_download_table_decodes_utf8_despite_missing_charset() -> None:
    # The server declares the tables as text/html without a charset.
    responses.get(
        URL, body="StopText\nPerspektivstraße\n".encode(), content_type="text/html"
    )

    assert (
        download_table("wienerlinien-ogd-linien.csv") == "StopText\nPerspektivstraße\n"
    )


@responses.activate
def test_download_table_drops_byte_order_mark() -> None:
    responses.get(URL, body=f"{BYTE_ORDER_MARK}StopID\n".encode())

    assert download_table("wienerlinien-ogd-linien.csv") == "StopID\n"


@responses.activate
def test_download_table_raises_on_http_error() -> None:
    responses.get(URL, status=404)

    with pytest.raises(requests.HTTPError):
        download_table("wienerlinien-ogd-linien.csv")


def test_read_table_reads_table_from_directory(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text(
        "StopText\nPerspektivstraße\n", encoding="utf-8"
    )

    assert read_table("table.csv", tmp_path) == "StopText\nPerspektivstraße\n"


def test_read_table_drops_byte_order_mark(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text(f"{BYTE_ORDER_MARK}StopID\n", encoding="utf-8")

    assert read_table("table.csv", tmp_path) == "StopID\n"


def test_load_table_reads_from_source_directory(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text("StopID\n", encoding="utf-8")

    assert load_table("table.csv", tmp_path) == "StopID\n"


@responses.activate
def test_load_table_downloads_without_source_directory() -> None:
    responses.get(URL, body=b"LineID\n")

    assert load_table("wienerlinien-ogd-linien.csv", None) == "LineID\n"


def test_parse_stops() -> None:
    content = (
        "StopID;DIVA;StopText;Municipality;MunicipalityID;Longitude;Latitude\n"
        "4111;60201320;Stephansplatz;Wien;49000001;16.3716613;48.2080620\n"
        "6145;;Abstellplatz Erdberg;;;0000000000;0000000000\n"
        "2859;60201035; ;Wien;49000001;16.4;48.2\n"
    )

    assert parse_stops(content) == [
        SourceStop(stop_id=4111, name="Stephansplatz"),
        SourceStop(stop_id=6145, name="Abstellplatz Erdberg"),
        SourceStop(stop_id=2859, name=""),
    ]


def test_parse_lines() -> None:
    content = (
        "LineID;LineText;SortingHelp;Realtime;MeansOfTransport\n"
        "301;U1;1;1;ptMetro\n"
        "1001;S1;400;0;ptTrainS\n"
    )

    assert parse_lines(content) == [
        SourceLine(line_id=301, name="U1", has_realtime=True),
        SourceLine(line_id=1001, name="S1", has_realtime=False),
    ]


def test_parse_route_points() -> None:
    content = (
        "LineID;PatternID;StopSeqCount;StopID;Direction\n"
        "301;1;0;4134;1\n"
        "301;2;1;4135;2\n"
    )

    assert parse_route_points(content) == [
        RoutePoint(line_id=301, pattern_id=1, direction=1, position=0, stop_id=4134),
        RoutePoint(line_id=301, pattern_id=2, direction=2, position=1, stop_id=4135),
    ]


def test_parse_route_points_without_direction() -> None:
    content = (
        "LineID;PatternID;StopSeqCount;StopID;Direction\n301;1;0;4134\n301;1;1;4135;\n"
    )

    assert [point.direction for point in parse_route_points(content)] == [None, None]


def test_find_main_routes_picks_lowest_pattern_id() -> None:
    points = [
        *route_points(10, 3, 1, 9, 1, 2, 3, 8),
        *route_points(10, 1, 1, 1, 2, 3),
        *route_points(10, 5, 1, 1, 2),
    ]

    assert find_main_routes(points) == [
        Route(line_id=10, direction=1, stop_ids=(1, 2, 3))
    ]


def test_find_main_routes_per_line_and_direction() -> None:
    points = [
        *route_points(10, 1, 1, 1, 2),
        *route_points(10, 2, 2, 2, 1),
        *route_points(20, 1, 1, 3, 4),
    ]

    assert find_main_routes(points) == [
        Route(line_id=10, direction=1, stop_ids=(1, 2)),
        Route(line_id=10, direction=2, stop_ids=(2, 1)),
        Route(line_id=20, direction=1, stop_ids=(3, 4)),
    ]


def test_find_main_routes_orders_stops_by_position() -> None:
    points = route_points(10, 1, 1, 1, 2, 3)

    assert find_main_routes(points[::-1]) == [
        Route(line_id=10, direction=1, stop_ids=(1, 2, 3))
    ]


def test_find_main_routes_skips_points_without_direction() -> None:
    points = [
        *route_points(10, 1, None, 7, 8),
        *route_points(10, 1, 1, 1, 2),
    ]

    assert find_main_routes(points) == [Route(line_id=10, direction=1, stop_ids=(1, 2))]


def test_find_main_routes_without_points() -> None:
    assert find_main_routes([]) == []


def test_build_stop_lines_labels_stops_with_last_stop(
    stops: list[SourceStop],
) -> None:
    result = build_stop_lines(stops, [line(10, "5A")], [route(10, 1, 2, 3)])

    assert result == [
        StopLine(stop_id=2, name="Middle", line="5A", towards="End"),
        StopLine(stop_id=1, name="Start", line="5A", towards="End"),
    ]


def test_build_stop_lines_leaves_out_lines_without_realtime_data(
    stops: list[SourceStop],
) -> None:
    lines = [line(10, "5A"), line(20, "S1", has_realtime=False)]

    result = build_stop_lines(stops, lines, [route(10, 1, 3), route(20, 2, 3)])

    assert [s.line for s in result] == ["5A"]


def test_build_stop_lines_leaves_out_unknown_lines(stops: list[SourceStop]) -> None:
    assert build_stop_lines(stops, [], [route(10, 1, 3)]) == []


def test_build_stop_lines_leaves_out_stops_named_like_last_stop(
    stops: list[SourceStop],
) -> None:
    stops.append(stop(5, "End"))

    result = build_stop_lines(stops, [line(10, "5A")], [route(10, 1, 5, 3)])

    assert [s.stop_id for s in result] == [1]


def test_build_stop_lines_leaves_out_stops_without_name(
    stops: list[SourceStop],
) -> None:
    stops.append(stop(5, ""))

    result = build_stop_lines(stops, [line(10, "5A")], [route(10, 5, 1, 3)])

    assert [s.stop_id for s in result] == [1]


def test_build_stop_lines_leaves_out_unknown_stops(stops: list[SourceStop]) -> None:
    result = build_stop_lines(stops, [line(10, "5A")], [route(10, 99, 1, 3, 98)])

    assert [(s.stop_id, s.towards) for s in result] == [(1, "End")]


def test_build_stop_lines_leaves_out_routes_without_known_stops(
    stops: list[SourceStop],
) -> None:
    assert build_stop_lines(stops, [line(10, "5A")], [route(10, 98, 99)]) == []


def test_build_stop_lines_lists_stop_once_per_line_and_direction(
    stops: list[SourceStop],
) -> None:
    result = build_stop_lines(stops, [line(10, "5A")], [route(10, 1, 2, 1, 3)])

    assert sorted(s.stop_id for s in result) == [1, 2]


def test_build_stop_lines_sorts_by_name_stop_id_and_line() -> None:
    stops = [stop(3, "Middle"), stop(2, "Middle"), stop(1, "Start"), stop(9, "End")]
    lines = [line(20, "U1"), line(10, "13A")]
    routes = [route(20, 3, 9), route(10, 3, 2, 1, 9)]

    result = build_stop_lines(stops, lines, routes)

    assert [(s.name, s.stop_id, s.line) for s in result] == [
        ("Middle", 2, "13A"),
        ("Middle", 3, "13A"),
        ("Middle", 3, "U1"),
        ("Start", 1, "13A"),
    ]


def test_write_stop_list(tmp_path: Path) -> None:
    path = tmp_path / "stops.csv"
    stop_lines = [
        StopLine(stop_id=4118, name="Stephansplatz", line="U1", towards="Oberlaa"),
        StopLine(stop_id=2903, name="Stephansplatz U", line="3A", towards="Oper, >"),
        StopLine(stop_id=1, name='Say "hi"; bye', line="1", towards="End"),
    ]

    write_stop_list(stop_lines, path)

    assert path.read_text(encoding="utf-8") == (
        "stop_id;name;line;towards\n"
        "4118;Stephansplatz;U1;Oberlaa\n"
        "2903;Stephansplatz U;3A;Oper, >\n"
        '1;"Say ""hi""; bye";1;End\n'
    )


def test_write_stop_list_creates_directory(tmp_path: Path) -> None:
    path = tmp_path / "out" / "stops.csv"

    write_stop_list([], path)

    assert path.read_text(encoding="utf-8") == "stop_id;name;line;towards\n"


def test_main_builds_stop_list_from_source_directory(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "wienerlinien-ogd-haltepunkte.csv").write_text(
        "StopID;DIVA;StopText;Municipality;MunicipalityID;Longitude;Latitude\n"
        "4134;60201095;Oberlaa;Wien;49000001;16.4;48.1\n"
        "4111;60201320;Stephansplatz;Wien;49000001;16.3;48.2\n"
        "4182;60200745;Leopoldau;Wien;49000001;16.4;48.2\n"
    )
    (source / "wienerlinien-ogd-linien.csv").write_text(
        "LineID;LineText;SortingHelp;Realtime;MeansOfTransport\n301;U1;1;1;ptMetro\n"
    )
    (source / "wienerlinien-ogd-fahrwegverlaeufe.csv").write_text(
        "LineID;PatternID;StopSeqCount;StopID;Direction\n"
        "301;1;0;4134;1\n"
        "301;1;1;4111;1\n"
        "301;1;2;4182;1\n"
    )
    output = tmp_path / "stops.csv"

    main(["--source", str(source), "--output", str(output)])

    assert output.read_text() == (
        "stop_id;name;line;towards\n"
        "4134;Oberlaa;U1;Leopoldau\n"
        "4111;Stephansplatz;U1;Leopoldau\n"
    )
