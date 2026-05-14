# Changelog

## 0.1.0 (2026-05-15)

Initial release. The cross-source identity layer for the Australian public-data MCP stack and anyone else building software that touches multiple AU government data sources.

### Added

- **`postcode_to_state(postcode)`** — map a 4-digit AU postcode to its state/territory code (`NSW`, `VIC`, `QLD`, `SA`, `WA`, `TAS`, `NT`, `ACT`). Handles the ACT-inside-NSW exceptions (`0200-0299`, `2600-2618`, `2900-2920`) correctly. Accepts string or int input.
- **`normalize_postcode(postcode)`** — coerce a string or int into canonical 4-digit form. Pads 3-digit shorthand (`"800"` → `"0800"`); strips whitespace; rejects bools to avoid `True` → `"0001"`.
- **`is_valid_postcode(postcode)`** — boolean check, never raises. Safe for use as a filter on user input.
- **`normalize_state(state)`** — coerce short codes (`"NSW"`), lowercase variants (`"nsw"`), full names (`"New South Wales"`), ISO 3166-2 (`"AU-NSW"`), aliases (`"Tassie"`), and underscore-separated LLM payloads (`"New_South_Wales"`) to the canonical short code.
- **`state_full_name(state)`** — return the official long-form name for a state code.
- **`STATE_NAMES`** — public mapping of canonical short codes to full names (8 jurisdictions).

### Test coverage

- 64 unit tests covering normalisation edge cases, ACT/NSW boundary, alias resolution, type validation, and round-trip stability between short codes and full names.

### Out of scope for v0.1

Planned for v0.2:

- ASGS 2021 crosswalk: postcode ↔ SA1/SA2/SA3/SA4 ↔ GCCSA ↔ state
- ABN ↔ ACN ↔ company-name fuzzy matching
- ANZSIC industry codes
- ANZSCO occupation codes

These require larger reference datasets (~3,000-17,000 rows). They will likely ship as separate sub-modules (`aus_identity.asgs`, `aus_identity.abn`, etc.) so the core install stays lean.
