# Changelog

## 0.3.1 (2026-05-17)

### Fixed — `normalize_period('2024-25', ...)` raised "Invalid month"

The `_RE_MONTH` regex (`^(\d{4})-(\d{2})$`) ran before `_RE_FISCAL`
(`^(\d{4})-(\d{2,4})$`); both match `'2024-25'`. The MONTH branch
rejected month=25 as invalid and raised before fiscal could match.

WGEA labels every reporting year `YYYY-YY` (`'2024-25'`, `'2023-24'`,
etc.), so any caller normalising a WGEA period hit this. Now the
MONTH branch only consumes values 1-12; everything else falls through
to FISCAL.

```python
normalize_period('2024-25', 'year')      # '2024'  (was ValueError)
normalize_period('2024-25', 'quarter')   # '2024-Q1' — FY-start quarter
normalize_period('2024-12', 'year')      # '2024'  (still works)
normalize_period('2024-2025', 'year')    # '2024'  (4-digit FY suffix)
```

4 regression tests in `tests/test_period.py`. 139 tests still pass.

## 0.3.0 (2026-05-17)

### Added — period normalisation + ANZSIC industry crosswalks

Two new modules unblock the remaining cross-source workflow gaps that v0.2.0 couldn't close:

**Period normalisation** (`aus_identity.period`):
- `to_quarter('2025-05')` → `'2025-Q2'` · `to_quarter('2025-Q1')` → `'2025-Q1'` (pass-through)
- `to_month('2025-Q2')` → `'2025-04'` · `to_year('2025-Q3')` → `'2025'`
- `to_date('2025-Q1')` → `'2025-01-01'` (start-of-period) · `to_date_end('2025-Q1')` → `'2025-03-31'` (end-of-period, leap-year-aware)
- `normalize_period(period, target_grain)` — single-entry helper

Closes the cross-source workflow pain where customers pass `'2025-Q1'` to rba/aemo (which only accept daily granularity) or `'2025-MM-DD'` to abs (which only accepts up to month). Composers can now snap inputs to each sister's native grain without per-customer translation logic.

**ANZSIC industry crosswalks** (`aus_identity.anzsic`):
- `ANZSIC_DIVISIONS` — 19-row dict: A→Agriculture, B→Mining, ... S→Other Services
- `anzsic_division('A')` → `'Agriculture, Forestry and Fishing'`
- `anzsic_division_for_code('011')` → `'A'` (handles 2/3/4-digit codes — Subdivision, Group, Class)
- `normalize_anzsic_division(value)` — accepts letter, full name, or numeric code, returns canonical letter

Closes the industry-employment cross-source workflow. ato encodes industries as `'011 Nursery and Floriculture Production'`, wgea as `'Accommodation'` (name) + `'0803'` (4-digit class), abs LF has no industry dim at all. The new helpers let composers bridge these without each sister rolling its own ANZSIC table.

**Wheel size stays under 20 KB** (zero-dep promise preserved). Full Class-level (1006-row) lookup deferred to v0.4 — Division and Group resolution cover ~95% of cross-source customer queries.

## 0.2.0 (2026-05-17)

### Added — NEM (National Electricity Market) region crosswalks

Two new helpers that bridge state-level data (ABS / ATO / APRA / etc.) with NEM-region energy data (aemo-mcp):

- `state_to_nem_region(state)` — `'NSW'` → `'NSW1'`, `'Tasmania'` → `'TAS1'`. Raises with helpful hint when the state is not a NEM member (ACT/NT/WA — ACT shares the NSW1 grid; NT and WA have separate grids).
- `nem_region_to_state(region)` — `'NSW1'` → `'NSW'` (round-trip inverse).
- `NEM_REGIONS` constant — `{'NSW': 'NSW1', 'VIC': 'VIC1', ...}` for direct lookup.

Unblocks the climate × electricity workflow (au-weather Sydney → state='NSW' → state_to_nem_region → 'NSW1' → aemo-mcp dispatch_region) end-to-end without consumer code maintaining its own mapping. Mirrors the existing `STATE_NAMES` / `normalize_state` / `state_full_name` pattern. Back-compat preserved (additive only).

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
