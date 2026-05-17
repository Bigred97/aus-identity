"""Australian state / territory code ↔ full name crosswalks.

Eight official jurisdictions: 6 states + 2 territories. The ABS, ATO,
APRA, AIHW, and other AU agencies use a mix of:
- ISO 3166-2 codes (AU-NSW, AU-VIC, ...) — rare outside official documents
- Short codes (NSW, VIC, ...) — most common in CSV / JSON exports
- Full names ("New South Wales", "Victoria", ...) — common in published reports
- Mixed case ("nsw", "New_South_Wales", "Nsw") — common from LLM inputs

`normalize_state` accepts any of these and returns the canonical 2-3 letter
short code. `state_full_name` does the reverse.
"""
from __future__ import annotations

from typing import Final


STATE_NAMES: Final[dict[str, str]] = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA": "South Australia",
    "WA": "Western Australia",
    "TAS": "Tasmania",
    "NT": "Northern Territory",
    "ACT": "Australian Capital Territory",
}


# Reverse map (full-name-upper → short code) for fast normalisation lookups.
_NAME_TO_CODE: Final[dict[str, str]] = {
    name.upper(): code for code, name in STATE_NAMES.items()
}

# Common alternative spellings / abbreviations.
_ALIASES: Final[dict[str, str]] = {
    # ISO 3166-2 codes
    "AU-NSW": "NSW",
    "AU-VIC": "VIC",
    "AU-QLD": "QLD",
    "AU-SA": "SA",
    "AU-WA": "WA",
    "AU-TAS": "TAS",
    "AU-NT": "NT",
    "AU-ACT": "ACT",
    # Common alternates / typos
    "NEW SOUTH WALES": "NSW",
    "TASSIE": "TAS",
    "NORTHERN TERRITORY OF AUSTRALIA": "NT",
    "AUSTRALIAN CAPITAL TERRITORY": "ACT",
    "QUEENSLAND": "QLD",
    "VICTORIA": "VIC",
    "WESTERN AUSTRALIA": "WA",
    "SOUTH AUSTRALIA": "SA",
    "TASMANIA": "TAS",
}


def normalize_state(state: str) -> str:
    """Normalise a state reference to the canonical 2-3 letter short code.

    Accepts short codes, ISO 3166-2 codes, full names, common aliases,
    and casual variants ("nsw", "New_South_Wales", "AU-VIC", "Tassie").

    Raises:
        ValueError: if the input cannot be matched to any AU state/territory.

    Examples:
        >>> normalize_state("NSW")
        'NSW'
        >>> normalize_state("nsw")
        'NSW'
        >>> normalize_state("New South Wales")
        'NSW'
        >>> normalize_state("New_South_Wales")
        'NSW'
        >>> normalize_state("AU-VIC")
        'VIC'
        >>> normalize_state("Tassie")
        'TAS'
    """
    if not isinstance(state, str):
        raise ValueError(
            f"state must be a string, got {type(state).__name__}. "
            f"Try one of: {', '.join(sorted(STATE_NAMES.keys()))}."
        )
    s = state.strip().upper().replace("_", " ").replace("-", "-")
    if s in STATE_NAMES:
        return s
    if s in _NAME_TO_CODE:
        return _NAME_TO_CODE[s]
    if s in _ALIASES:
        return _ALIASES[s]
    raise ValueError(
        f"state {state!r} is not a recognised AU state or territory. "
        f"Valid short codes: {', '.join(sorted(STATE_NAMES.keys()))}. "
        f"Full names also accepted (e.g. 'New South Wales', 'Tasmania'). "
        "Did you mean one of these? Use the search-by-prefix approach: "
        f"'N' matches NSW/NT, 'S' matches SA, 'T' matches TAS, 'A' matches ACT, 'V' matches VIC."
    )


NEM_REGIONS: Final[dict[str, str]] = {
    "NSW": "NSW1",
    "VIC": "VIC1",
    "QLD": "QLD1",
    "SA": "SA1",
    "TAS": "TAS1",
    # ACT shares the NSW1 grid; NT and WA have separate grids (not NEM members).
}

# Reverse map (NEM region code → state short code) for fast normalisation.
_NEM_TO_STATE: Final[dict[str, str]] = {region: state for state, region in NEM_REGIONS.items()}


def state_to_nem_region(state: str) -> str:
    """Translate an AU state code to its NEM (National Electricity Market) region.

    AEMO's NEM uses region codes like 'NSW1', 'VIC1', etc. — distinct from
    the state short codes used by ABS, ATO, APRA, AIHW, ASIC. Use this helper
    to bridge state-level data (e.g. ABS LF unemployment by state) with NEM
    energy data (e.g. aemo-mcp dispatch_price by region).

    Args:
        state: Anything `normalize_state` accepts.

    Raises:
        ValueError: if the input cannot be matched OR the state is not a NEM
            member (ACT shares NSW1 — pass 'NSW' explicitly. NT and WA are
            on separate grids and have no AEMO NEM coverage).

    Examples:
        >>> state_to_nem_region("NSW")
        'NSW1'
        >>> state_to_nem_region("vic")
        'VIC1'
        >>> state_to_nem_region("Tasmania")
        'TAS1'
    """
    code = normalize_state(state)
    if code not in NEM_REGIONS:
        raise ValueError(
            f"{code!r} is not a NEM member. NEM regions cover NSW, VIC, QLD, SA, TAS "
            f"(map: {NEM_REGIONS}). ACT shares the NSW1 grid — pass 'NSW' to get NSW1. "
            "NT and WA have separate grids with no AEMO NEM coverage."
        )
    return NEM_REGIONS[code]


def nem_region_to_state(region: str) -> str:
    """Translate a NEM region code (e.g. 'NSW1') back to a state short code.

    Args:
        region: NEM region code — 'NSW1', 'VIC1', 'QLD1', 'SA1', 'TAS1'.
            Case-insensitive.

    Raises:
        ValueError: if the input is not a known NEM region.

    Examples:
        >>> nem_region_to_state("NSW1")
        'NSW'
        >>> nem_region_to_state("vic1")
        'VIC'
    """
    if not isinstance(region, str):
        raise ValueError(
            f"region must be a string, got {type(region).__name__}. "
            f"Try one of: {', '.join(sorted(NEM_REGIONS.values()))}."
        )
    r = region.strip().upper()
    if r not in _NEM_TO_STATE:
        raise ValueError(
            f"{region!r} is not a known NEM region. "
            f"Valid NEM regions: {', '.join(sorted(NEM_REGIONS.values()))}."
        )
    return _NEM_TO_STATE[r]


def state_full_name(state: str) -> str:
    """Return the official full name for a state/territory code.

    Args:
        state: Anything `normalize_state` accepts.

    Raises:
        ValueError: if the input cannot be matched.

    Examples:
        >>> state_full_name("NSW")
        'New South Wales'
        >>> state_full_name("nsw")
        'New South Wales'
        >>> state_full_name("AU-VIC")
        'Victoria'
        >>> state_full_name("Tassie")
        'Tasmania'
    """
    code = normalize_state(state)
    return STATE_NAMES[code]
