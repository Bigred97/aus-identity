"""aus-identity — cross-source join keys for Australian public data.

The foundation layer for tools that need to talk to multiple AU datasets at
once (ABS demographics + ATO income + APRA banking + au-weather climate +
ASIC company register + RBA monetary stats). Each agency uses its own
identifier conventions; this package provides the crosswalks.

v0.1.0 scope:
- Postcode (4-digit) ↔ state (NSW/VIC/QLD/SA/WA/TAS/NT/ACT) — covers ~99% of AU postcodes
- State code ↔ state full name (with fuzzy normalisation)
- Postcode validation

v0.2 (future):
- ASGS 2021 crosswalk: postcode ↔ SA1/SA2/SA3/SA4 ↔ GCCSA
- ABN ↔ ACN ↔ company-name fuzzy
- ANZSIC industry codes
- ANZSCO occupation codes

Used by the AU public-data MCP stack
(https://github.com/Bigred97?tab=repositories&q=mcp) and by anyone else
building software that touches multiple AU government data sources.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .anzsic import (
    ANZSIC_DIVISIONS,
    anzsic_division,
    anzsic_division_for_code,
    anzsic_division_name,
    normalize_anzsic_division,
)
from .period import (
    normalize_period,
    to_date,
    to_date_end,
    to_month,
    to_quarter,
    to_year,
)
from .postcode import (
    is_valid_postcode,
    normalize_postcode,
    postcode_to_state,
)
from .state import (
    NEM_REGIONS,
    STATE_NAMES,
    nem_region_to_state,
    normalize_state,
    state_full_name,
    state_to_nem_region,
)

try:
    __version__ = _version("aus-identity")
except PackageNotFoundError:  # editable install before metadata is generated
    __version__ = "0.0.0+unknown"

__all__ = [
    "ANZSIC_DIVISIONS",
    "NEM_REGIONS",
    "STATE_NAMES",
    "__version__",
    "anzsic_division",
    "anzsic_division_for_code",
    "anzsic_division_name",
    "is_valid_postcode",
    "nem_region_to_state",
    "normalize_anzsic_division",
    "normalize_period",
    "normalize_postcode",
    "normalize_state",
    "postcode_to_state",
    "state_full_name",
    "state_to_nem_region",
    "to_date",
    "to_date_end",
    "to_month",
    "to_quarter",
    "to_year",
]
