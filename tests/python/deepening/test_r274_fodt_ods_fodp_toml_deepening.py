"""Sprint 22: FODT/ODS/FODP/TOML product deepening — 8 new analytics functions."""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

FODT = str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt")
ODS = str(next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods")))
FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")

TOML_CONTENT = b'[server]\nhost = "localhost"\nport = 8080\nenabled = true\n'


def _toml_file():
    f = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    f.write(TOML_CONTENT)
    f.close()
    return f.name


# --- FODT ---

class TestFodtIsEmpty:
    def test_returns_bool(self):
        from fodt import fodt_is_empty
        assert isinstance(fodt_is_empty(FODT), bool)


class TestFodtHasHeadings:
    def test_returns_bool(self):
        from fodt import fodt_has_headings
        assert isinstance(fodt_has_headings(FODT), bool)


# --- ODS ---

class TestOdsMinNumericValue:
    def test_returns_numeric_or_none(self):
        from ods import ods_min_numeric_value
        result = ods_min_numeric_value(ODS)
        assert result is None or isinstance(result, (int, float))

    def test_lte_max(self):
        from ods import ods_min_numeric_value, ods_max_numeric_value
        mn = ods_min_numeric_value(ODS)
        mx = ods_max_numeric_value(ODS)
        if mn is not None and mx is not None:
            assert mn <= mx


class TestOdsHasNumericCells:
    def test_returns_bool(self):
        from ods import ods_has_numeric_cells
        assert isinstance(ods_has_numeric_cells(ODS), bool)


# --- FODP ---

class TestFodpHasTitles:
    def test_returns_bool(self):
        from fodp import fodp_has_titles
        assert isinstance(fodp_has_titles(FODP), bool)


class TestFodpMinShapesPerSlide:
    def test_returns_int(self):
        from fodp import fodp_min_shapes_per_slide
        assert isinstance(fodp_min_shapes_per_slide(FODP), int)

    def test_non_negative(self):
        from fodp import fodp_min_shapes_per_slide
        assert fodp_min_shapes_per_slide(FODP) >= 0


# --- TOML ---

class TestTomlIsEmpty:
    def test_returns_bool(self):
        from toml import toml_is_empty
        assert isinstance(toml_is_empty(_toml_file()), bool)

    def test_non_empty_sample(self):
        from toml import toml_is_empty
        assert toml_is_empty(_toml_file()) is False


class TestTomlStringDensity:
    def test_returns_float(self):
        from toml import toml_string_density
        assert isinstance(toml_string_density(_toml_file()), float)

    def test_in_range(self):
        from toml import toml_string_density
        assert 0.0 <= toml_string_density(_toml_file()) <= 1.0
