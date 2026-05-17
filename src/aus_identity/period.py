"""Period-grain normalisation for cross-source AU data joins.

Each AU agency publishes at a different cadence:
- ABS LF: monthly (YYYY-MM)
- ABS CPI / WPI / ANA_AGG: quarterly (YYYY-Q1)
- ABS ERP_Q: quarterly (YYYY-Q1)
- ABS Census: 5-yearly (YYYY)
- RBA F-tables: daily (YYYY-MM-DD)
- AEMO dispatch: 5-min interval (YYYY-MM-DDTHH:MM:SS+10:00)
- ATO: annual fiscal year (YYYY-YY)
- AIHW: annual fiscal year (YYYY-YY)
- WGEA: annual reporting year (YYYY-YY)

When customers cross-source-join (e.g. WPI × CPI for real wages, or F1.1 cash
rate × ABS CPI for monetary policy timing), they need to normalise periods
to a common grain. This module is the canonical reducer.

Two coordinate systems:
- INPUT: the strings each sister MCP returns or accepts
- INTERNAL: a 4-tuple (year, quarter|None, month|None, day|None) for arithmetic

Use `to_quarter('2025-03')` → `'2025-Q1'`, `to_quarter('2025-Q1')` → `'2025-Q1'`
(pass-through), `to_quarter('2025-03-15')` → `'2025-Q1'`. Same shape for
`to_month`, `to_year`. The inverse functions snap to the START of the period
for use as `start_period` arguments.
"""
from __future__ import annotations

import re
from typing import Final

# Period regexes — order matters: most specific first.
_RE_QUARTER: Final = re.compile(r"^(\d{4})-Q([1-4])$")
_RE_HALF: Final = re.compile(r"^(\d{4})-S([12])$")
_RE_DATE: Final = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:T.*)?$")
_RE_MONTH: Final = re.compile(r"^(\d{4})-(\d{2})$")
_RE_YEAR: Final = re.compile(r"^(\d{4})$")
_RE_FISCAL: Final = re.compile(r"^(\d{4})-(\d{2,4})$")  # 2024-25 or 2024-2025


def _parse(period: str) -> tuple[int, int | None, int | None, int | None]:
    """Parse a period string into (year, quarter, month, day).

    Returns the tuple with unset components as None. Recognises:
    - YYYY → (year, None, None, None)
    - YYYY-Q1..Q4 → (year, q, None, None)
    - YYYY-S1..S2 → maps to (year, q*2-1, None, None) for half-year
    - YYYY-MM → (year, ((m-1)//3)+1, m, None)
    - YYYY-MM-DD → (year, ((m-1)//3)+1, m, d)
    - YYYY-YY (fiscal) → (year, None, None, None) — treated as the calendar
      year that the fiscal year STARTS in

    Raises ValueError if the input matches no recognised shape.
    """
    if not isinstance(period, str):
        raise ValueError(
            f"period must be a string, got {type(period).__name__}. "
            "Valid shapes: 'YYYY', 'YYYY-Q1', 'YYYY-S1', 'YYYY-MM', 'YYYY-MM-DD', 'YYYY-YY'."
        )
    s = period.strip()
    if (m := _RE_DATE.match(s)):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= mo <= 12) or not (1 <= d <= 31):
            raise ValueError(f"Invalid date components in {period!r}.")
        return (y, ((mo - 1) // 3) + 1, mo, d)
    if (m := _RE_QUARTER.match(s)):
        return (int(m.group(1)), int(m.group(2)), None, None)
    if (m := _RE_HALF.match(s)):
        h = int(m.group(2))
        return (int(m.group(1)), 2 * h - 1, None, None)  # S1 → Q1, S2 → Q3
    if (m := _RE_MONTH.match(s)):
        y, mo = int(m.group(1)), int(m.group(2))
        if not (1 <= mo <= 12):
            raise ValueError(f"Invalid month in {period!r}.")
        return (y, ((mo - 1) // 3) + 1, mo, None)
    if (m := _RE_FISCAL.match(s)):
        # 2024-25 or 2024-2025 — fiscal year starting in given calendar year
        return (int(m.group(1)), None, None, None)
    if (m := _RE_YEAR.match(s)):
        return (int(m.group(1)), None, None, None)
    raise ValueError(
        f"Unrecognised period shape {period!r}. "
        "Valid shapes: 'YYYY', 'YYYY-Q1', 'YYYY-S1', 'YYYY-MM', 'YYYY-MM-DD', 'YYYY-YY'."
    )


def to_year(period: str) -> str:
    """Coarsen any period to the year. '2025-Q3' → '2025', '2025-05-15' → '2025'."""
    y, _, _, _ = _parse(period)
    return f"{y:04d}"


def to_quarter(period: str) -> str:
    """Coarsen any period to YYYY-QN. '2025-05' → '2025-Q2', '2025' → '2025-Q1'.

    When the input is just YYYY, returns Q1 of that year (start-of-period bias).
    """
    y, q, _, _ = _parse(period)
    return f"{y:04d}-Q{q or 1}"


def to_month(period: str) -> str:
    """Coarsen any period to YYYY-MM. '2025-Q2' → '2025-04' (start of quarter)."""
    y, q, mo, _ = _parse(period)
    if mo is None:
        # Snap to start of quarter, or start of year
        mo = ((q or 1) - 1) * 3 + 1
    return f"{y:04d}-{mo:02d}"


def to_date(period: str) -> str:
    """Coarsen any period to YYYY-MM-DD. '2025-Q2' → '2025-04-01', '2025' → '2025-01-01'.

    Snaps to the FIRST day of the period — appropriate for `start_period`
    arguments where you want everything from that point onwards. Use
    `to_date_end(period)` for the corresponding last-day-of-period.
    """
    y, q, mo, d = _parse(period)
    if mo is None:
        mo = ((q or 1) - 1) * 3 + 1
    if d is None:
        d = 1
    return f"{y:04d}-{mo:02d}-{d:02d}"


def to_date_end(period: str) -> str:
    """Snap to the LAST day of the period. '2025-Q1' → '2025-03-31'.

    Useful for `end_period` arguments where you want everything THROUGH the
    end of the given period. Month-end days respect leap years for Feb.
    """
    y, q, mo, d = _parse(period)
    if d is not None:
        # Already a day — return as-is.
        return f"{y:04d}-{mo:02d}-{d:02d}"
    if mo is None:
        # Quarter or year — pick the last month of the unit.
        if q is not None:
            mo = q * 3
        else:
            mo = 12
    # Month-end day depends on month + leap year for Feb.
    if mo in (1, 3, 5, 7, 8, 10, 12):
        d = 31
    elif mo in (4, 6, 9, 11):
        d = 30
    else:  # February
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        d = 29 if leap else 28
    return f"{y:04d}-{mo:02d}-{d:02d}"


def normalize_period(period: str, target_grain: str) -> str:
    """Normalise a period to the requested grain.

    target_grain ∈ {'year', 'quarter', 'month', 'date'}.
    """
    fn = {
        "year": to_year,
        "quarter": to_quarter,
        "month": to_month,
        "date": to_date,
    }.get(target_grain)
    if fn is None:
        raise ValueError(
            f"Unknown target_grain {target_grain!r}. "
            "Valid: 'year', 'quarter', 'month', 'date'."
        )
    return fn(period)
