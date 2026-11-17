from custom_components.vienna_transport.stop_list import StopListEntry
from custom_components.vienna_transport.stop_list_query import StopListQuery


def _entry(stop_id: int, name: str, line: str, towards: str) -> StopListEntry:
    return StopListEntry(stop_id=stop_id, name=name, line=line, towards=towards)


def test_lines_returns_unique_lines() -> None:
    query = StopListQuery(
        [
            _entry(4118, "Schwedenplatz", "U1", "Leopoldau"),
            _entry(4113, "Schwedenplatz", "U1", "Oberlaa"),
        ]
    )

    assert query.lines() == ["U1"]


def test_lines_sorts_naturally() -> None:
    query = StopListQuery(
        [
            _entry(1, "A", "U1", "X"),
            _entry(2, "A", "10A", "X"),
            _entry(3, "A", "2", "X"),
            _entry(4, "A", "N6", "X"),
            _entry(5, "A", "13A", "X"),
            _entry(6, "A", "D", "X"),
        ]
    )

    assert query.lines() == ["2", "10A", "13A", "D", "N6", "U1"]


def test_lines_returns_empty_list_without_entries() -> None:
    assert StopListQuery([]).lines() == []


def test_directions_returns_directions_of_line() -> None:
    query = StopListQuery(
        [
            _entry(4118, "Schwedenplatz", "U1", "Oberlaa"),
            _entry(4113, "Schwedenplatz", "U1", "Leopoldau"),
            _entry(4119, "Stephansplatz", "U1", "Oberlaa"),
            _entry(5650, "Schwedenplatz", "1", "Prater Hauptallee"),
        ]
    )

    assert query.directions("U1") == ["Leopoldau", "Oberlaa"]


def test_directions_returns_empty_list_for_unknown_line() -> None:
    query = StopListQuery([_entry(4118, "Schwedenplatz", "U1", "Leopoldau")])

    assert query.directions("U5") == []


def test_stops_returns_stops_of_line_direction_sorted_by_name() -> None:
    query = StopListQuery(
        [
            _entry(4119, "Stephansplatz", "U1", "Oberlaa"),
            _entry(4113, "Schwedenplatz", "U1", "Oberlaa"),
            _entry(4118, "Schwedenplatz", "U1", "Leopoldau"),
            _entry(5650, "Schwedenplatz", "1", "Oberlaa"),
        ]
    )

    stops = query.stops("U1", "Oberlaa")

    assert list(stops.items()) == [(4113, "Schwedenplatz"), (4119, "Stephansplatz")]


def test_stops_appends_stop_id_to_duplicate_names() -> None:
    query = StopListQuery(
        [
            _entry(2939, "Alaudagasse U", "67A", "Inzersdorf, Slamastraße"),
            _entry(2932, "Alaudagasse U", "67A", "Inzersdorf, Slamastraße"),
            _entry(2940, "Ada-Christen-Gasse", "67A", "Inzersdorf, Slamastraße"),
        ]
    )

    stops = query.stops("67A", "Inzersdorf, Slamastraße")

    assert list(stops.items()) == [
        (2940, "Ada-Christen-Gasse"),
        (2932, "Alaudagasse U (2932)"),
        (2939, "Alaudagasse U (2939)"),
    ]


def test_stops_keeps_names_unique_in_other_directions() -> None:
    query = StopListQuery(
        [
            _entry(4118, "Schwedenplatz", "U1", "Leopoldau"),
            _entry(4113, "Schwedenplatz", "U1", "Oberlaa"),
        ]
    )

    assert query.stops("U1", "Leopoldau") == {4118: "Schwedenplatz"}


def test_stops_returns_empty_dict_for_unknown_direction() -> None:
    query = StopListQuery([_entry(4118, "Schwedenplatz", "U1", "Leopoldau")])

    assert query.stops("U1", "Oberlaa") == {}
