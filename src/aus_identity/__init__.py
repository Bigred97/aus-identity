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

from .postcode import (
    is_valid_postcode,
    normalize_postcode,
    postcode_to_state,
)
from .state import (
    STATE_NAMES,
    normalize_state,
    state_full_name,
)

try:
    __version__ = _version("aus-identity")
except PackageNotFoundError:  # editable install before metadata is generated
    __version__ = "0.0.0+unknown"

__all__ = [
    "STATE_NAMES",
    "__version__",
    "is_valid_postcode",
    "normalize_postcode",
    "normalize_state",
    "postcode_to_state",
    "state_full_name",
]
