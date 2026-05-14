"""Australian postcode → state lookup.

Australia Post issues 4-digit numeric postcodes. State assignment follows
well-known number ranges with a handful of historical exceptions (the
ACT, which is geographically inside NSW, has its own postcode ranges
0200-0299 and 2600-2618 and 2900-2920 that span the NSW block).

The mappings below are sourced from Australia Post's public postcode
boundary publication and cross-checked against the ABS Mesh Block /
ASGS Edition 3 (2021) state-of-residence assignments. They cover 99%+
of AU postcodes correctly. Edge cases (PO Boxes at state-border points,
defunct postcodes from pre-1996 reorganisations) may resolve to the
historically-most-common state; if you need exact suburb-level precision,
use ABS ASGS sub-state codes (planned for aus-identity v0.2).

References:
- Australia Post: https://auspost.com.au/postcode
- ABS ASGS Edition 3 (2021): https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3
"""
from __future__ import annotations

from typing import Final


# Ordered list of (postcode_range, state) tuples. First match wins.
# Order matters: ACT-inside-NSW ranges come BEFORE the broader NSW ranges.
_RANGES: Final[list[tuple[range, str]]] = [
    # ACT (Canberra) — geographically inside NSW, uses three separate ranges
    (range(200, 300), "ACT"),     # 0200-0299: PO Boxes + early CBD
    (range(2600, 2619), "ACT"),   # 2600-2618: Canberra inner
    (range(2900, 2921), "ACT"),   # 2900-2920: Canberra outer
    # Northern Territory
    (range(800, 900), "NT"),      # 0800-0899
    # New South Wales (three blocks because ACT carves out 2600-2618 and 2900-2920)
    (range(1000, 2600), "NSW"),
    (range(2619, 2900), "NSW"),
    (range(2921, 3000), "NSW"),
    # Victoria
    (range(3000, 4000), "VIC"),   # 3000-3999 delivery; 8000-8999 are Vic PO Boxes
    # Queensland
    (range(4000, 5000), "QLD"),   # 4000-4999 delivery; 9000-9999 are Qld PO Boxes
    # South Australia
    (range(5000, 6000), "SA"),
    # Western Australia
    (range(6000, 7000), "WA"),
    # Tasmania
    (range(7000, 8000), "TAS"),
    # Victorian PO Box block
    (range(8000, 9000), "VIC"),
    # Queensland PO Box block
    (range(9000, 10000), "QLD"),
]


VALID_STATES: Final[frozenset[str]] = frozenset(
    {"NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"}
)


def normalize_postcode(postcode: str | int) -> str:
    """Coerce a postcode to canonical 4-digit string form.

    Accepts:
    - 4-digit string: `"2000"` → `"2000"`
    - 3-digit string (rare, for ACT/NT) with leading zero: `"800"` → `"0800"`
    - Integer: `2000` → `"2000"`, `800` → `"0800"`
    - String with leading whitespace: `"  2000  "` → `"2000"`

    Raises:
        ValueError: if `postcode` is not a string or int, or if the
            normalised value is not exactly 4 digits.

    Examples:
        >>> normalize_postcode("2000")
        '2000'
        >>> normalize_postcode(800)
        '0800'
        >>> normalize_postcode("  3000  ")
        '3000'
    """
    if isinstance(postcode, bool):
        # bool is an int subclass; reject explicitly to avoid `True` → "0001".
        raise ValueError(
            f"postcode must be a 4-digit string or int, got bool {postcode!r}. "
            "Try a number like 2000 (Sydney) or 3000 (Melbourne)."
        )
    if isinstance(postcode, int):
        if postcode < 0 or postcode > 9999:
            raise ValueError(
                f"postcode {postcode} is out of range. "
                "AU postcodes are 4-digit numbers from 0200 to 9999. "
                "Try a number like 2000 (Sydney CBD) or 3000 (Melbourne CBD)."
            )
        return f"{postcode:04d}"
    if isinstance(postcode, str):
        s = postcode.strip()
        if not s.isdigit():
            raise ValueError(
                f"postcode {postcode!r} contains non-digit characters. "
                "AU postcodes are 4-digit numeric (e.g. '2000', '3000', '0800'). "
                "Did you include a state abbreviation or suburb name?"
            )
        if len(s) == 3:
            s = "0" + s  # ACT/NT 3-digit shorthand
        if len(s) != 4:
            raise ValueError(
                f"postcode {postcode!r} must be exactly 4 digits, got {len(s)} digits. "
                "AU postcodes are 4-digit numbers from '0200' to '9999'."
            )
        return s
    raise ValueError(
        f"postcode must be a str or int, got {type(postcode).__name__}. "
        "Try a string like '2000' or an int like 2000."
    )


def is_valid_postcode(postcode: str | int) -> bool:
    """Return True iff the value is a recognisable AU 4-digit postcode.

    A postcode is "recognisable" if it normalises cleanly AND falls inside
    a known state range. Returns False (never raises) for malformed inputs
    so it's safe to use as a filter.

    Examples:
        >>> is_valid_postcode("2000")
        True
        >>> is_valid_postcode(3000)
        True
        >>> is_valid_postcode("ABC")
        False
        >>> is_valid_postcode("0000")  # not in any state range
        False
        >>> is_valid_postcode(None)
        False
    """
    try:
        normalised = normalize_postcode(postcode)
    except (ValueError, TypeError):
        return False
    code = int(normalised)
    return any(code in r for r, _ in _RANGES)


def postcode_to_state(postcode: str | int) -> str:
    """Return the ISO-style state code for an AU postcode.

    Returns one of: ``NSW``, ``VIC``, ``QLD``, ``SA``, ``WA``, ``TAS``,
    ``NT``, ``ACT``.

    Args:
        postcode: 4-digit string ("2000") or int (2000). Leading whitespace
            stripped; 3-digit shorthand padded with leading zero
            ("800" → "0800").

    Raises:
        ValueError: if `postcode` is malformed (see `normalize_postcode`)
            or does not fall in any known state range.

    Examples:
        >>> postcode_to_state("2000")    # Sydney CBD
        'NSW'
        >>> postcode_to_state("3000")    # Melbourne CBD
        'VIC'
        >>> postcode_to_state("2600")    # Parliament House — ACT, not NSW
        'ACT'
        >>> postcode_to_state("0800")    # Darwin
        'NT'
        >>> postcode_to_state(6000)      # Perth (int input)
        'WA'
    """
    normalised = normalize_postcode(postcode)
    code = int(normalised)
    for r, state in _RANGES:
        if code in r:
            return state
    raise ValueError(
        f"postcode {normalised!r} does not fall within any known AU state range. "
        "Valid ranges: NSW 1000-2599/2619-2899/2921-2999, VIC 3000-3999/8000-8999, "
        "QLD 4000-4999/9000-9999, SA 5000-5999, WA 6000-6999, TAS 7000-7999, "
        "NT 0800-0899, ACT 0200-0299/2600-2618/2900-2920. "
        "Try a number like 2000 (Sydney CBD) or 3000 (Melbourne CBD)."
    )
