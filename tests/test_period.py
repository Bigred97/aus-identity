

# ----- Fiscal-year (YYYY-YY) regression -----
#
# Before 0.3.1 the YYYY-MM regex matched '2024-25' first and raised "Invalid
# month" instead of falling through to _RE_FISCAL. WGEA uses YYYY-YY for
# every reporting year ('2024-25', '2023-24', etc.) so this blocked any
# customer using normalize_period on the wgea-mcp output.


def test_fiscal_yyyy_yy_normalizes_to_year():
    from aus_identity.period import normalize_period

    assert normalize_period("2024-25", "year") == "2024"
    assert normalize_period("2023-24", "year") == "2023"
    assert normalize_period("2024-2025", "year") == "2024"


def test_fiscal_yyyy_yy_normalizes_to_quarter_uses_fy_start():
    from aus_identity.period import normalize_period

    # FY starts in given calendar year — quarter coarsens to Q1 of that year.
    assert normalize_period("2024-25", "quarter") == "2024-Q1"


def test_yyyy_mm_still_works_for_valid_months():
    from aus_identity.period import normalize_period

    # Sanity: the fix didn't break legitimate YYYY-MM parsing.
    assert normalize_period("2024-12", "year") == "2024"
    assert normalize_period("2024-01", "quarter") == "2024-Q1"
    assert normalize_period("2024-06", "quarter") == "2024-Q2"


def test_invalid_period_shape_raises():
    from aus_identity.period import normalize_period
    import pytest as _pytest

    # A totally bogus shape with no numeric structure should still raise.
    with _pytest.raises(ValueError):
        normalize_period("not-a-period", "year")
