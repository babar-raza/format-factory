"""Sprint 269 deepening – FODS / FODT / ODT / TSV composite analytics."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100,
    fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50,
    parse_fods_strict,
)
from src.python.fodt import (
    fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37,
    fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43,
)
from src.python.odt import (
    odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37,
    odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43,
)
from src.python.tsv import (
    tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31,
    tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37,
)

_SAMPLES = _REPO / "samples" / "by-format"
_FODS = _SAMPLES / "fods" / "minimal-spreadsheet.fods"
_FODT = _SAMPLES / "fodt" / "minimal-document.fodt"
_ODT = _SAMPLES / "odt" / "valid" / "minimal-document.odt"
_TSV = _SAMPLES / "tsv" / "minimal-2x2.tsv"


@pytest.fixture
def fods_wb():
    return parse_fods_strict(str(_FODS))


class TestFodsF1:
    def test_returns_int(self, fods_wb):
        assert isinstance(fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100(fods_wb), int)
    def test_positive(self, fods_wb):
        assert fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100(fods_wb) > 0
    def test_deterministic(self, fods_wb):
        assert fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100(fods_wb) == fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100(fods_wb)
    def test_expected(self, fods_wb):
        assert fods_sc_times_700_plus_tc_sq_times_3_plus_sc_tc_times_100(fods_wb) == 803


class TestFodsF2:
    def test_returns_int(self, fods_wb):
        assert isinstance(fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50(fods_wb), int)
    def test_positive(self, fods_wb):
        assert fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50(fods_wb) > 0
    def test_deterministic(self, fods_wb):
        assert fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50(fods_wb) == fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50(fods_wb)
    def test_expected(self, fods_wb):
        assert fods_tc_times_600_plus_sc_sq_times_200_plus_sc_tc_times_50(fods_wb) == 850


class TestFodtF3:
    def test_returns_int(self):
        assert isinstance(fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37(str(_FODT)), int)
    def test_positive(self):
        assert fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37(str(_FODT)) > 0
    def test_deterministic(self):
        assert fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37(str(_FODT)) == fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37(str(_FODT))
    def test_expected(self):
        assert fodt_pc_times_400_plus_wc_cc_times_3_plus_fsz_mod_37(str(_FODT)) == 509


class TestFodtF4:
    def test_returns_int(self):
        assert isinstance(fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43(str(_FODT)), int)
    def test_positive(self):
        assert fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43(str(_FODT)) > 0
    def test_deterministic(self):
        assert fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43(str(_FODT)) == fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43(str(_FODT))
    def test_expected(self):
        assert fodt_cc_times_200_plus_pc_wc_times_100_plus_fsz_mod_43(str(_FODT)) == 2841


class TestOdtF5:
    def test_returns_int(self):
        assert isinstance(odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37(str(_ODT)), int)
    def test_positive(self):
        assert odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37(str(_ODT)) > 0
    def test_deterministic(self):
        assert odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37(str(_ODT)) == odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37(str(_ODT))
    def test_expected(self):
        assert odt_pc_times_500_plus_wc_cc_times_2_plus_fsz_mod_37(str(_ODT)) == 580


class TestOdtF6:
    def test_returns_int(self):
        assert isinstance(odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43(str(_ODT)), int)
    def test_positive(self):
        assert odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43(str(_ODT)) > 0
    def test_deterministic(self):
        assert odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43(str(_ODT)) == odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43(str(_ODT))
    def test_expected(self):
        assert odt_cc_times_300_plus_pc_wc_times_100_plus_fsz_mod_43(str(_ODT)) == 4108


class TestTsvF7:
    def test_returns_int(self):
        assert isinstance(tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31(str(_TSV)), int)
    def test_positive(self):
        assert tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31(str(_TSV)) > 0
    def test_deterministic(self):
        assert tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31(str(_TSV)) == tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31(str(_TSV))
    def test_expected(self):
        assert tsv_rc_cc_times_400_plus_uvc_sq_times_30_plus_fsz_mod_31(str(_TSV)) == 2108


class TestTsvF8:
    def test_returns_int(self):
        assert isinstance(tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37(str(_TSV)), int)
    def test_positive(self):
        assert tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37(str(_TSV)) > 0
    def test_deterministic(self):
        assert tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37(str(_TSV)) == tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37(str(_TSV))
    def test_expected(self):
        assert tsv_uvc_times_300_plus_rc_cc_times_200_plus_fsz_mod_37(str(_TSV)) == 2028
