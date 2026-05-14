"""Postcode normalisation + state lookup."""
from __future__ import annotations

import pytest

from aus_identity import (
    is_valid_postcode,
    normalize_postcode,
    postcode_to_state,
)


# ─── normalize_postcode ─────────────────────────────────────────────────

@pytest.mark.parametrize("inp,out", [
    ("2000", "2000"),
    ("3000", "3000"),
    ("  2000  ", "2000"),
    ("0800", "0800"),
    ("0200", "0200"),
    (2000, "2000"),
    (200, "0200"),
    (800, "0800"),
    (9999, "9999"),
])
def test_normalize_postcode_accepts_valid(inp: str | int, out: str) -> None:
    assert normalize_postcode(inp) == out


@pytest.mark.parametrize("bad", [None, 1.5, [], {}])
def test_normalize_postcode_rejects_non_str_non_int(bad: object) -> None:
    with pytest.raises(ValueError, match="must be a str or int"):
        normalize_postcode(bad)  # type: ignore[arg-type]


def test_normalize_postcode_rejects_bool() -> None:
    """`True`/`False` are int subclasses; must not silently coerce to '0001'/'0000'."""
    with pytest.raises(ValueError, match="bool"):
        normalize_postcode(True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="bool"):
        normalize_postcode(False)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ["ABCD", "20A0", "20-00", "twenty-thousand"])
def test_normalize_postcode_rejects_non_digit_strings(bad: str) -> None:
    with pytest.raises(ValueError, match="non-digit"):
        normalize_postcode(bad)


@pytest.mark.parametrize("bad", ["1", "12", "12345"])
def test_normalize_postcode_rejects_wrong_length(bad: str) -> None:
    with pytest.raises(ValueError, match="4 digits"):
        normalize_postcode(bad)


def test_normalize_postcode_rejects_empty_string() -> None:
    """Empty string trips the non-digit guard (since `"".isdigit()` is False) —
    that's fine, just lock in the contract that it raises somewhere clear."""
    with pytest.raises(ValueError, match="non-digit"):
        normalize_postcode("")


@pytest.mark.parametrize("bad", [-1, 10000, -2000])
def test_normalize_postcode_rejects_out_of_range_int(bad: int) -> None:
    with pytest.raises(ValueError, match="out of range"):
        normalize_postcode(bad)


# ─── postcode_to_state ──────────────────────────────────────────────────

@pytest.mark.parametrize("postcode,state", [
    # NSW capitals
    ("2000", "NSW"),   # Sydney CBD
    ("2010", "NSW"),   # Surry Hills
    ("2500", "NSW"),   # Wollongong area
    ("2899", "NSW"),
    ("2999", "NSW"),
    # ACT (carved out of NSW)
    ("0200", "ACT"),
    ("0299", "ACT"),
    ("2600", "ACT"),
    ("2618", "ACT"),
    ("2900", "ACT"),
    ("2920", "ACT"),
    # VIC
    ("3000", "VIC"),   # Melbourne CBD
    ("3999", "VIC"),
    ("8000", "VIC"),   # Vic PO Box block
    ("8999", "VIC"),
    # QLD
    ("4000", "QLD"),   # Brisbane CBD
    ("4999", "QLD"),
    ("9000", "QLD"),   # Qld PO Box block
    ("9999", "QLD"),
    # SA
    ("5000", "SA"),    # Adelaide
    ("5999", "SA"),
    # WA
    ("6000", "WA"),    # Perth
    ("6999", "WA"),
    # TAS
    ("7000", "TAS"),   # Hobart
    ("7999", "TAS"),
    # NT
    ("0800", "NT"),    # Darwin
    ("0899", "NT"),
])
def test_postcode_to_state_known_codes(postcode: str, state: str) -> None:
    assert postcode_to_state(postcode) == state


def test_postcode_to_state_int_inputs() -> None:
    """Integer inputs work the same as 4-digit strings."""
    assert postcode_to_state(2000) == "NSW"
    assert postcode_to_state(3000) == "VIC"
    assert postcode_to_state(800) == "NT"   # 3-digit shorthand padded
    assert postcode_to_state(200) == "ACT"  # 3-digit shorthand padded


def test_postcode_to_state_act_inside_nsw_boundary() -> None:
    """The ACT/NSW boundary is well-defined. Verify it doesn't drift."""
    assert postcode_to_state("2599") == "NSW", "2599 is in the NSW 1000-2599 block"
    assert postcode_to_state("2600") == "ACT", "2600 starts the inner-Canberra ACT block"
    assert postcode_to_state("2618") == "ACT", "2618 is the last inner-Canberra ACT code"
    assert postcode_to_state("2619") == "NSW", "2619 resumes the NSW block"
    assert postcode_to_state("2899") == "NSW", "2899 is the last pre-Canberra-outer NSW code"
    assert postcode_to_state("2900") == "ACT", "2900 starts the outer-Canberra ACT block"
    assert postcode_to_state("2920") == "ACT", "2920 is the last outer-Canberra ACT code"
    assert postcode_to_state("2921") == "NSW", "2921 resumes the NSW block"


@pytest.mark.parametrize("bad", ["0000", "0100", "0500"])
def test_postcode_to_state_unrecognised_range(bad: str) -> None:
    """Postcodes outside any known state range raise with a helpful hint."""
    with pytest.raises(ValueError, match="state range"):
        postcode_to_state(bad)


# ─── is_valid_postcode ──────────────────────────────────────────────────

@pytest.mark.parametrize("good", [
    "2000", "3000", "0800", "0200", "2600", "5000", "6000", "7000", "9999",
    2000, 800, 200,
])
def test_is_valid_postcode_true(good: str | int) -> None:
    assert is_valid_postcode(good) is True


@pytest.mark.parametrize("bad", [
    None, "", "abc", "20a0", "1", "12345", -1, 10000, "0000", "0100", 1.5, True, False,
])
def test_is_valid_postcode_false(bad: object) -> None:
    """`is_valid_postcode` never raises — returns False for any malformed input."""
    assert is_valid_postcode(bad) is False  # type: ignore[arg-type]
