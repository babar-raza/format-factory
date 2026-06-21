"""Sprint 268 deepening – NDJSON / Gnumeric / ODS / SYLK composite analytics."""
import sys, pathlib, tempfile, os, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31,
    ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37,
)
from src.python.gnumeric import (
    gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200,
    gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37,
)
from src.python.ods import (
    ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31,
    ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41,
)
from src.python.sylk import (
    sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29,
    sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37,
)

_SAMPLES = _REPO / "samples" / "by-format"
_GNUMERIC = _SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric"
_ODS = _SAMPLES / "ods" / "valid" / "single-cell.ods"
_SYLK = _SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"


@pytest.fixture
def ndjson_path(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text('{"a":1,"b":2}\n{"a":3,"b":4}\n')
    return str(p)


# --- NDJSON f1 ---
class TestNdjsonF1:
    def test_returns_int(self, ndjson_path):
        assert isinstance(ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31(ndjson_path), int)

    def test_positive(self, ndjson_path):
        assert ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31(ndjson_path) > 0

    def test_deterministic(self, ndjson_path):
        a = ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31(ndjson_path)
        b = ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31(ndjson_path)
        assert a == b

    def test_expected(self, ndjson_path):
        assert ndjson_rc_times_uk_times_400_plus_tvc_times_200_plus_file_size_mod_31(ndjson_path) == 2430


# --- NDJSON f2 ---
class TestNdjsonF2:
    def test_returns_int(self, ndjson_path):
        assert isinstance(ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37(ndjson_path), int)

    def test_positive(self, ndjson_path):
        assert ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37(ndjson_path) > 0

    def test_deterministic(self, ndjson_path):
        a = ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37(ndjson_path)
        b = ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37(ndjson_path)
        assert a == b

    def test_expected(self, ndjson_path):
        assert ndjson_tvc_times_rc_times_100_plus_uk_times_500_plus_file_size_mod_37(ndjson_path) == 1830


# --- Gnumeric f3 ---
class TestGnumericF3:
    def test_returns_int(self):
        assert isinstance(gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200(str(_GNUMERIC)), int)

    def test_positive(self):
        assert gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200(str(_GNUMERIC)) > 0

    def test_deterministic(self):
        a = gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200(str(_GNUMERIC))
        b = gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200(str(_GNUMERIC))
        assert a == b

    def test_expected(self):
        assert gnumeric_sc_times_cc_times_300_plus_file_size_mod_29_times_100_plus_sc_times_200(str(_GNUMERIC)) == 2200


# --- Gnumeric f4 ---
class TestGnumericF4:
    def test_returns_int(self):
        assert isinstance(gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37(str(_GNUMERIC)), int)

    def test_positive(self):
        assert gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37(str(_GNUMERIC)) > 0

    def test_deterministic(self):
        a = gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37(str(_GNUMERIC))
        b = gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37(str(_GNUMERIC))
        assert a == b

    def test_expected(self):
        assert gnumeric_cc_squared_times_50_plus_sc_times_600_plus_file_size_mod_37(str(_GNUMERIC)) == 661


# --- ODS f5 ---
class TestOdsF5:
    def test_returns_int(self):
        assert isinstance(ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31(str(_ODS)), int)

    def test_positive(self):
        assert ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31(str(_ODS)) > 0

    def test_deterministic(self):
        a = ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31(str(_ODS))
        b = ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31(str(_ODS))
        assert a == b

    def test_expected(self):
        assert ods_sc_times_rc_times_400_plus_cc_times_300_plus_file_size_mod_31(str(_ODS)) == 723


# --- ODS f6 ---
class TestOdsF6:
    def test_returns_int(self):
        assert isinstance(ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41(str(_ODS)), int)

    def test_positive(self):
        assert ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41(str(_ODS)) > 0

    def test_deterministic(self):
        a = ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41(str(_ODS))
        b = ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41(str(_ODS))
        assert a == b

    def test_expected(self):
        assert ods_rc_times_cc_times_200_plus_sc_times_500_plus_file_size_mod_41(str(_ODS)) == 723


# --- SYLK f7 ---
class TestSylkF7:
    def test_returns_int(self):
        assert isinstance(sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29(str(_SYLK)), int)

    def test_positive(self):
        assert sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29(str(_SYLK)) > 0

    def test_deterministic(self):
        a = sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29(str(_SYLK))
        b = sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29(str(_SYLK))
        assert a == b

    def test_expected(self):
        assert sylk_rc_times_cc_times_300_plus_uvc_times_200_plus_file_size_mod_29(str(_SYLK)) == 2017


# --- SYLK f8 ---
class TestSylkF8:
    def test_returns_int(self):
        assert isinstance(sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37(str(_SYLK)), int)

    def test_positive(self):
        assert sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37(str(_SYLK)) > 0

    def test_deterministic(self):
        a = sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37(str(_SYLK))
        b = sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37(str(_SYLK))
        assert a == b

    def test_expected(self):
        assert sylk_uvc_times_rc_times_100_plus_cc_times_400_plus_file_size_mod_37(str(_SYLK)) == 1601
