"""State code ↔ full-name crosswalk."""
from __future__ import annotations

import pytest

from aus_identity import STATE_NAMES, normalize_state, state_full_name


# ─── STATE_NAMES dict integrity ─────────────────────────────────────────

def test_state_names_has_eight_jurisdictions() -> None:
    assert len(STATE_NAMES) == 8


def test_state_names_codes_are_uppercase_short() -> None:
    for code in STATE_NAMES:
        assert code == code.upper()
        assert 2 <= len(code) <= 3


def test_state_names_full_names_proper_case() -> None:
    for name in STATE_NAMES.values():
        # Each name should start with an uppercase letter
        assert name[0].isupper()
        # No trailing whitespace
        assert name == name.strip()


# ─── normalize_state ────────────────────────────────────────────────────

@pytest.mark.parametrize("inp,out", [
    # Canonical short codes
    ("NSW", "NSW"),
    ("VIC", "VIC"),
    ("QLD", "QLD"),
    ("SA", "SA"),
    ("WA", "WA"),
    ("TAS", "TAS"),
    ("NT", "NT"),
    ("ACT", "ACT"),
    # Lowercase
    ("nsw", "NSW"),
    ("vic", "VIC"),
    ("act", "ACT"),
    # Mixed case
    ("Nsw", "NSW"),
    ("nSw", "NSW"),
    # Whitespace
    ("  NSW  ", "NSW"),
    ("\tVIC\n", "VIC"),
    # Full names
    ("New South Wales", "NSW"),
    ("Victoria", "VIC"),
    ("Queensland", "QLD"),
    ("South Australia", "SA"),
    ("Western Australia", "WA"),
    ("Tasmania", "TAS"),
    ("Northern Territory", "NT"),
    ("Australian Capital Territory", "ACT"),
    # Full names with underscores (LLM payload pattern)
    ("New_South_Wales", "NSW"),
    ("Western_Australia", "WA"),
    # ISO 3166-2
    ("AU-NSW", "NSW"),
    ("AU-VIC", "VIC"),
    ("AU-TAS", "TAS"),
    # Aliases
    ("Tassie", "TAS"),
    ("TASSIE", "TAS"),
])
def test_normalize_state_accepts_variants(inp: str, out: str) -> None:
    assert normalize_state(inp) == out


@pytest.mark.parametrize("bad", [
    "XYZ",       # not a real state
    "Tas mania", # mid-word space (after replace _ → space this passes a different path)
    "",          # empty
    "  ",        # whitespace only
    "AU",        # no state suffix
    "NewSouthWales",  # missing space
])
def test_normalize_state_rejects_unknown(bad: str) -> None:
    with pytest.raises(ValueError, match="not a recognised AU state"):
        normalize_state(bad)


@pytest.mark.parametrize("bad", [None, 123, 1.5, [], {}])
def test_normalize_state_rejects_non_string(bad: object) -> None:
    with pytest.raises(ValueError, match="must be a string"):
        normalize_state(bad)  # type: ignore[arg-type]


# ─── state_full_name ────────────────────────────────────────────────────

@pytest.mark.parametrize("inp,out", [
    ("NSW", "New South Wales"),
    ("nsw", "New South Wales"),
    ("VIC", "Victoria"),
    ("ACT", "Australian Capital Territory"),
    ("Tassie", "Tasmania"),
    ("AU-WA", "Western Australia"),
    ("Queensland", "Queensland"),       # idempotent for full names
    ("New_South_Wales", "New South Wales"),
])
def test_state_full_name(inp: str, out: str) -> None:
    assert state_full_name(inp) == out


def test_state_full_name_round_trip() -> None:
    """Every canonical short code → full name → back to short code is stable."""
    for code, name in STATE_NAMES.items():
        assert state_full_name(code) == name
        assert normalize_state(name) == code
