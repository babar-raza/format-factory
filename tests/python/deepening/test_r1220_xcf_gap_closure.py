"""Gap closure: GAP-XCF-FOSS-XCF_FSZ_MOD_-001 — missing test coverage."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
SAMPLE = SAMPLES / "1x1-red-rgb.xcf"


def test_xcf_fsz_mod_43_returns_int():
    from xcf.xcf_analytics import xcf_fsz_mod_43_times_300_plus_it_times_900_plus_w_sq_h_sq_times_50
    result = xcf_fsz_mod_43_times_300_plus_it_times_900_plus_w_sq_h_sq_times_50(str(SAMPLE))
    assert isinstance(result, int)


def test_xcf_fsz_mod_43_nonnegative():
    from xcf.xcf_analytics import xcf_fsz_mod_43_times_300_plus_it_times_900_plus_w_sq_h_sq_times_50
    result = xcf_fsz_mod_43_times_300_plus_it_times_900_plus_w_sq_h_sq_times_50(str(SAMPLE))
    assert result >= 0
