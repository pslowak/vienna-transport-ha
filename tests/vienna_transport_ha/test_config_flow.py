from custom_components.vienna_transport_ha.config_flow import ViennaTransportConfigFlow


def test_validate_stop_ids_returns_cleaned_list() -> None:
    result = ViennaTransportConfigFlow._validate_stop_ids(["2683", " 1337 "])
    assert result == ["2683", "1337"]


def test_validate_stop_ids_returns_empty_on_blank_input() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids([""]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids(["  "]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids([]) == []


def test_validate_stop_ids_returns_empty_on_non_numeric() -> None:
    assert ViennaTransportConfigFlow._validate_stop_ids(["abc"]) == []
    assert ViennaTransportConfigFlow._validate_stop_ids(["2683", "abc"]) == []


def test_validate_stop_ids_accepts_multiple_valid_ids() -> None:
    result = ViennaTransportConfigFlow._validate_stop_ids(["2683", "1337", "5566"])
    assert result == ["2683", "1337", "5566"]
