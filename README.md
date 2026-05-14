# aus-identity

[![PyPI](https://img.shields.io/pypi/v/aus-identity.svg)](https://pypi.org/project/aus-identity/)
[![Python](https://img.shields.io/pypi/pyversions/aus-identity.svg)](https://pypi.org/project/aus-identity/)
[![License](https://img.shields.io/pypi/l/aus-identity.svg)](https://github.com/Bigred97/aus-identity/blob/main/LICENSE)
[![Tests](https://github.com/Bigred97/aus-identity/actions/workflows/test.yml/badge.svg)](https://github.com/Bigred97/aus-identity/actions/workflows/test.yml)

Cross-source join keys for Australian public data. The foundation layer for tools that need to talk to multiple AU government data sources at once (ABS demographics + ATO income + APRA banking + au-weather climate + ASIC company register + RBA monetary stats), or for any application that has to map between Australia's postcode and state/territory conventions.

## What it does today (v0.1.0)

- **Postcode → state**: `postcode_to_state("2000")` → `"NSW"`. Handles the three ACT-inside-NSW carve-outs (`0200-0299`, `2600-2618`, `2900-2920`) correctly.
- **Postcode normalisation**: accept `"2000"`, `2000`, `" 2000 "`, `"0800"`, `800` — all return canonical 4-digit string form.
- **Postcode validation**: `is_valid_postcode(x)` returns a boolean and never raises — safe for filtering arbitrary input.
- **State code normalisation**: `normalize_state("nsw")` / `normalize_state("New South Wales")` / `normalize_state("AU-VIC")` / `normalize_state("Tassie")` → canonical short code.
- **Full state name**: `state_full_name("NSW")` → `"New South Wales"`.

## Install

```bash
pip install aus-identity
# or
uv add aus-identity
```

Zero runtime dependencies. Pure Python. Wheel is < 20 KB.

## Quick examples

```python
from aus_identity import (
    postcode_to_state,
    normalize_postcode,
    is_valid_postcode,
    normalize_state,
    state_full_name,
)

# Postcode → state
postcode_to_state("2000")      # "NSW" (Sydney CBD)
postcode_to_state("3000")      # "VIC" (Melbourne CBD)
postcode_to_state("2600")      # "ACT" (Parliament House — not NSW)
postcode_to_state("0800")      # "NT"  (Darwin)
postcode_to_state(6000)        # "WA"  (int input also accepted)

# Normalisation
normalize_postcode("  2000  ")  # "2000"
normalize_postcode(800)         # "0800" (3-digit shorthand padded)

# Validation (never raises)
is_valid_postcode("2000")       # True
is_valid_postcode("ABCD")       # False
is_valid_postcode(None)         # False

# State normalisation
normalize_state("nsw")                  # "NSW"
normalize_state("New South Wales")      # "NSW"
normalize_state("AU-VIC")               # "VIC"
normalize_state("Tassie")               # "TAS"
normalize_state("New_South_Wales")      # "NSW" (LLM payload form)

# Full names
state_full_name("NSW")          # "New South Wales"
state_full_name("act")          # "Australian Capital Territory"
```

## Why this exists

The AU public-data MCP stack ([abs-mcp](https://pypi.org/project/abs-mcp/), [rba-mcp](https://pypi.org/project/rba-mcp/), [ato-mcp](https://pypi.org/project/ato-mcp/), [apra-mcp](https://pypi.org/project/apra-mcp/), [aihw-mcp](https://pypi.org/project/aihw-mcp/), [asic-mcp](https://pypi.org/project/asic-mcp/), [aemo-mcp](https://pypi.org/project/aemo-mcp/), [au-weather-mcp](https://pypi.org/project/au-weather-mcp/), [wgea-mcp](https://pypi.org/project/wgea-mcp/)) lets an LLM agent talk to any single Australian government data source. But each agency uses its own identifier conventions:

- ABS uses ASGS region codes (`1GSYD` for Greater Sydney, `101011001` for an SA1)
- ATO uses 4-digit postcodes
- APRA uses ABNs
- ASIC uses licence numbers
- AEMO uses NEM region codes (`NSW1`, `QLD1`)
- au-weather uses location keys and lat/long
- RBA uses F-table IDs and series codes
- WGEA uses ABNs + reporting-year labels

To use any two of these together — "what's the median household income vs unemployment rate in postcode 2000?" — something has to translate between identifier systems. **aus-identity is that something.** v0.1 starts with the most-used crosswalk (postcode ↔ state); v0.2+ will extend to ASGS / ABN / ANZSIC / ANZSCO.

## Used by

- [abs-mcp](https://pypi.org/project/abs-mcp/) — Australian Bureau of Statistics
- [rba-mcp](https://pypi.org/project/rba-mcp/) — Reserve Bank of Australia
- [ato-mcp](https://pypi.org/project/ato-mcp/) — Australian Taxation Office
- [apra-mcp](https://pypi.org/project/apra-mcp/) — Australian Prudential Regulation Authority
- [aihw-mcp](https://pypi.org/project/aihw-mcp/) — Australian Institute of Health and Welfare
- [asic-mcp](https://pypi.org/project/asic-mcp/) — Australian Securities and Investments Commission
- [aemo-mcp](https://pypi.org/project/aemo-mcp/) — Australian Energy Market Operator
- [au-weather-mcp](https://pypi.org/project/au-weather-mcp/) — Open-Meteo (Bureau of Meteorology aggregator)
- [wgea-mcp](https://pypi.org/project/wgea-mcp/) — Workplace Gender Equality Agency

## Source of truth

Postcode → state mappings are sourced from Australia Post's public postcode boundary publication and cross-checked against ABS ASGS Edition 3 (2021) state-of-residence assignments. The three ACT-inside-NSW ranges and the Vic/Qld PO Box blocks are handled explicitly. Coverage is 99%+ of currently-active AU postcodes.

For exact suburb-level precision (e.g. which side of an ACT/NSW boundary a specific delivery address falls), use ABS ASGS sub-state codes — planned for v0.2 of this package.

## Roadmap

- **v0.1.0** (this release) — postcode + state crosswalks
- **v0.2** — ASGS 2021 sub-state crosswalk (SA1 ↔ SA2 ↔ SA3 ↔ SA4 ↔ GCCSA ↔ state)
- **v0.3** — ABN ↔ ACN ↔ ACNC charity-ID crosswalk
- **v0.4** — ANZSIC industry codes + ANZSCO occupation codes

## License

MIT.
