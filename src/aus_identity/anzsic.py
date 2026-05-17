"""ANZSIC 2006 industry-code crosswalks for cross-source AU data joins.

ANZSIC (Australian and New Zealand Standard Industrial Classification) is the
canonical industry taxonomy used by ABS, ATO, APRA, ASIC, WGEA. Each level
has a fixed-digit code:

- Division: 1 letter (A–S)   → 19 broad industries
- Subdivision: 2 digits        → 86 sub-industries
- Group: 3 digits              → 214 groups
- Class: 4 digits              → 1,006 classes

This v0.3 ships the Division-level table (19 rows) and a thin Group-level
helper. Full Class-level enumeration is deferred to v0.4 to keep the wheel
under 20 KB (the package's zero-dep promise).

Customer use case: when wgea returns `anzsic_group: 'Accommodation'` (name)
and ato returns `industry_fine: '440 Accommodation'` (code + name), the join
needs a code→name canonicalizer. Use `anzsic_division(letter)`,
`anzsic_division_name(letter)`, or `anzsic_division_for_code(group_or_class)`.

Source: ABS Catalogue 1292.0 (ANZSIC 2006 Rev 2.0). Codes are stable —
ANZSIC has not been revised since 2006.
"""
from __future__ import annotations

from typing import Final


# The 19 Division-level industries (ANZSIC 2006).
ANZSIC_DIVISIONS: Final[dict[str, str]] = {
    "A": "Agriculture, Forestry and Fishing",
    "B": "Mining",
    "C": "Manufacturing",
    "D": "Electricity, Gas, Water and Waste Services",
    "E": "Construction",
    "F": "Wholesale Trade",
    "G": "Retail Trade",
    "H": "Accommodation and Food Services",
    "I": "Transport, Postal and Warehousing",
    "J": "Information Media and Telecommunications",
    "K": "Financial and Insurance Services",
    "L": "Rental, Hiring and Real Estate Services",
    "M": "Professional, Scientific and Technical Services",
    "N": "Administrative and Support Services",
    "O": "Public Administration and Safety",
    "P": "Education and Training",
    "Q": "Health Care and Social Assistance",
    "R": "Arts and Recreation Services",
    "S": "Other Services",
}

# Subdivision (2-digit) → Division (letter) mapping. ANZSIC numbering is
# blocked by division: 01-05 = A, 06-10 = B, 11-25 = C, etc.
_SUBDIV_TO_DIVISION: Final[dict[str, str]] = {
    # A — Agriculture, Forestry and Fishing
    "01": "A", "02": "A", "03": "A", "04": "A", "05": "A",
    # B — Mining
    "06": "B", "07": "B", "08": "B", "09": "B", "10": "B",
    # C — Manufacturing
    **{f"{n:02d}": "C" for n in range(11, 26)},
    # D — Electricity, Gas, Water and Waste Services
    "26": "D", "27": "D", "28": "D", "29": "D",
    # E — Construction
    "30": "E", "31": "E", "32": "E",
    # F — Wholesale Trade
    "33": "F", "34": "F", "35": "F", "36": "F", "37": "F", "38": "F",
    # G — Retail Trade
    "39": "G", "40": "G", "41": "G", "42": "G", "43": "G",
    # H — Accommodation and Food Services
    "44": "H", "45": "H",
    # I — Transport, Postal and Warehousing
    "46": "I", "47": "I", "48": "I", "49": "I", "50": "I", "51": "I", "52": "I", "53": "I",
    # J — Information Media and Telecommunications
    "54": "J", "55": "J", "56": "J", "57": "J", "58": "J", "59": "J", "60": "J",
    # K — Financial and Insurance Services
    "62": "K", "63": "K", "64": "K",
    # L — Rental, Hiring and Real Estate Services
    "66": "L", "67": "L",
    # M — Professional, Scientific and Technical Services
    "69": "M", "70": "M", "71": "M", "72": "M",
    # N — Administrative and Support Services
    # NOTE: Subdivision 72 spans BOTH M (72.10/72.20 — Computer System Design)
    # and N (72.50 — Other services). The portfolio-canonical mapping is
    # M (above) because customers usually mean Computer System Design when
    # they reference ANZSIC 72. The N-side codes (73) are mapped here.
    "73": "N",
    # O — Public Administration and Safety
    "75": "O", "76": "O", "77": "O",
    # P — Education and Training
    "80": "P", "81": "P", "82": "P",
    # Q — Health Care and Social Assistance
    "84": "Q", "85": "Q", "86": "Q", "87": "Q",
    # R — Arts and Recreation Services
    "89": "R", "90": "R", "91": "R", "92": "R",
    # S — Other Services
    "94": "S", "95": "S", "96": "S",
}


def anzsic_division(letter: str) -> str:
    """Return the human-readable name for an ANZSIC division letter.

    Examples:
        >>> anzsic_division("A")
        'Agriculture, Forestry and Fishing'
        >>> anzsic_division("g")  # case-insensitive
        'Retail Trade'

    Raises ValueError if the letter is not A-S.
    """
    if not isinstance(letter, str):
        raise ValueError(
            f"letter must be a string, got {type(letter).__name__}. "
            f"Valid: {', '.join(sorted(ANZSIC_DIVISIONS))}."
        )
    key = letter.strip().upper()
    if key not in ANZSIC_DIVISIONS:
        raise ValueError(
            f"{letter!r} is not an ANZSIC division. "
            f"Valid letters: {', '.join(sorted(ANZSIC_DIVISIONS))}."
        )
    return ANZSIC_DIVISIONS[key]


def anzsic_division_name(letter: str) -> str:
    """Alias for `anzsic_division` (matches the `state_full_name` naming pattern)."""
    return anzsic_division(letter)


def anzsic_division_for_code(code: str) -> str:
    """Return the Division letter for a Subdivision/Group/Class code.

    Accepts 2-, 3-, or 4-digit codes — only the first 2 digits matter for
    division lookup, since ANZSIC subdivision numbering is contiguous within
    divisions.

    Examples:
        >>> anzsic_division_for_code('011')  # ATO industry_fine "011 Nursery..."
        'A'
        >>> anzsic_division_for_code('0111')  # WGEA anzsic_class
        'A'
        >>> anzsic_division_for_code('44')   # H — Accommodation
        'H'

    Raises ValueError if the input cannot be parsed.
    """
    if not isinstance(code, str):
        raise ValueError(
            f"code must be a string, got {type(code).__name__}. "
            "Pass 2-, 3-, or 4-digit ANZSIC code (e.g. '01', '011', '0111')."
        )
    s = code.strip()
    if not s.isdigit() or len(s) not in (2, 3, 4):
        raise ValueError(
            f"{code!r} is not a valid ANZSIC code. "
            "Pass a 2-, 3-, or 4-digit numeric string (e.g. '01', '011', '0111')."
        )
    subdiv = s[:2]
    division = _SUBDIV_TO_DIVISION.get(subdiv)
    if division is None:
        raise ValueError(
            f"Subdivision {subdiv!r} (from code {code!r}) is not a known "
            "ANZSIC 2006 subdivision. Valid range: 01-96 with gaps. "
            "See ABS Catalogue 1292.0."
        )
    return division


def normalize_anzsic_division(value: str) -> str:
    """Resolve any input (letter, full name, or numeric code) to the Division letter.

    Examples:
        >>> normalize_anzsic_division('A')
        'A'
        >>> normalize_anzsic_division('Agriculture, Forestry and Fishing')
        'A'
        >>> normalize_anzsic_division('011')
        'A'
        >>> normalize_anzsic_division('retail trade')
        'G'

    Raises ValueError on bad input.
    """
    if not isinstance(value, str):
        raise ValueError(f"value must be a string, got {type(value).__name__}.")
    v = value.strip()
    # Single letter
    if len(v) == 1 and v.upper() in ANZSIC_DIVISIONS:
        return v.upper()
    # Numeric code
    if v.isdigit() and len(v) in (2, 3, 4):
        return anzsic_division_for_code(v)
    # Full name (case-insensitive)
    v_upper = v.upper()
    for letter, name in ANZSIC_DIVISIONS.items():
        if name.upper() == v_upper:
            return letter
    raise ValueError(
        f"Cannot resolve {value!r} to an ANZSIC division. "
        f"Pass a letter (A-S), full division name, or 2-/3-/4-digit code."
    )
