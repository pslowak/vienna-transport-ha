import logging
from pathlib import Path

import pytest

from custom_components.vienna_transport.stop_list import StopListEntry
from custom_components.vienna_transport.stop_list_loader import StopListLoader

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_load_returns_entries_in_file_order() -> None:
    loader = StopListLoader(path=FIXTURES_DIR / "stops.csv")

    assert loader.load() == [
        StopListEntry(
            stop_id=4118, name="Schwedenplatz", line="U1", towards="Leopoldau"
        ),
        StopListEntry(stop_id=4113, name="Schwedenplatz", line="U1", towards="Oberlaa"),
        StopListEntry(
            stop_id=5650, name="Schwedenplatz", line="1", towards="Prater Hauptallee"
        ),
        StopListEntry(
            stop_id=5650,
            name="Schwedenplatz",
            line="2",
            towards="Friedrich-Engels-Platz",
        ),
    ]


def test_load_keeps_non_ascii_names(tmp_path: Path) -> None:
    path = tmp_path / "stops.csv"
    path.write_text(
        "stop_id;name;line;towards\n433;1. Haidequerstraße Mitte;72A;Gasometer U\n",
        encoding="utf-8",
    )

    entries = StopListLoader(path=path).load()

    assert entries[0].name == "1. Haidequerstraße Mitte"


def test_load_returns_empty_list_for_header_only(tmp_path: Path) -> None:
    path = tmp_path / "stops.csv"
    path.write_text("stop_id;name;line;towards\n", encoding="utf-8")

    assert StopListLoader(path=path).load() == []


def test_load_raises_when_file_missing(tmp_path: Path) -> None:
    loader = StopListLoader(path=tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_logs_warning_when_file_missing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path = tmp_path / "missing.csv"
    loader = StopListLoader(path=path)

    with caplog.at_level(logging.WARNING), pytest.raises(FileNotFoundError):
        loader.load()

    assert f"Stop list not found at {path}" in caplog.text
