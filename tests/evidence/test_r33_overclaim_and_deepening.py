"""
Evidence validators for R33 overclaim review and format deepening.

Validates:
1. All DRIFT taskcards have R33 review outcomes
2. Overclaimed formats have r33_review_outcome in matrix
3. ODS CSV exporter exists and is importable
4. QOI encoder exists and is importable
5. QOI round-trip works
6. ZST test expansion achieved (>= 45 tests)
7. Matrix deepening annotations are consistent
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

try:
    import yaml
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# 1. DRIFT taskcard completeness
# ---------------------------------------------------------------------------

class TestDriftTaskcardCompleteness:

    DRIFT_TASKCARDS = [
        "DRIFT-FODP-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-FODG-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-GNUMERIC-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-ABW-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-XCF-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-PPM-GATE-OVERCLAIM-REVIEW.md",
        "DRIFT-PGM-PBM-ASCII-SCOPE-REVIEW.md",
    ]

    def test_all_drift_taskcards_exist(self):
        for name in self.DRIFT_TASKCARDS:
            path = REPO_ROOT / "taskcards" / name
            assert path.exists(), f"DRIFT taskcard missing: {name}"

    def test_all_drift_taskcards_have_r33_review(self):
        for name in self.DRIFT_TASKCARDS:
            path = REPO_ROOT / "taskcards" / name
            content = path.read_text(encoding="utf-8")
            assert "R33 Expert Review Outcome" in content, (
                f"{name} missing R33 review outcome section"
            )

    def test_high_overclaim_taskcards_have_correction_verdict(self):
        """FODP/FODG/Gnumeric/ABW must have GATE_CORRECTION_REQUIRED."""
        correction_required = [
            "DRIFT-FODP-GATE-OVERCLAIM-REVIEW.md",
            "DRIFT-FODG-GATE-OVERCLAIM-REVIEW.md",
            "DRIFT-GNUMERIC-GATE-OVERCLAIM-REVIEW.md",
            "DRIFT-ABW-GATE-OVERCLAIM-REVIEW.md",
        ]
        for name in correction_required:
            path = REPO_ROOT / "taskcards" / name
            content = path.read_text(encoding="utf-8")
            assert "GATE_CORRECTION_REQUIRED" in content, (
                f"{name} should have GATE_CORRECTION_REQUIRED verdict"
            )


# ---------------------------------------------------------------------------
# 2. Matrix overclaim annotations
# ---------------------------------------------------------------------------

@pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
class TestMatrixOverclaimAnnotations:

    @pytest.fixture(scope="class")
    def matrix(self):
        path = REPO_ROOT / "registry" / "format-completion-matrix.yaml"
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _find_format(self, matrix, fmt_id):
        for entry in matrix["formats"]:
            if entry["format_id"] == fmt_id:
                return entry
        return None

    def test_fodp_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "fodp")
        assert entry is not None
        assert "r33_review_outcome" in entry
        assert "GATE_CORRECTION_REQUIRED" in entry["r33_review_outcome"]

    def test_fodg_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "fodg")
        assert entry is not None
        assert "r33_review_outcome" in entry

    def test_gnumeric_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "gnumeric")
        assert entry is not None
        assert "r33_review_outcome" in entry

    def test_abw_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "abw")
        assert entry is not None
        assert "r33_review_outcome" in entry

    def test_xcf_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "xcf")
        assert entry is not None
        assert "r33_review_outcome" in entry

    def test_ppm_has_r33_review(self, matrix):
        entry = self._find_format(matrix, "ppm")
        assert entry is not None
        assert "r33_review_outcome" in entry


# ---------------------------------------------------------------------------
# 3. ODS CSV exporter
# ---------------------------------------------------------------------------

class TestOdsCsvExporterExists:

    def test_exporter_module_importable(self):
        from ods.ods_csv_exporter import export_ods_to_csv
        assert callable(export_ods_to_csv)

    def test_exporter_file_exists(self):
        path = REPO_ROOT / "src" / "python" / "ods" / "ods_csv_exporter.py"
        assert path.exists()

    def test_exporter_capabilities(self):
        from ods.ods_csv_exporter import get_csv_export_capabilities
        caps = get_csv_export_capabilities()
        assert caps["export_target"] == "csv"
        assert "single_sheet_export" in caps["features"]


# ---------------------------------------------------------------------------
# 4. QOI encoder
# ---------------------------------------------------------------------------

class TestQoiEncoderExists:

    def test_encoder_module_importable(self):
        from qoi.qoi_encoder import encode_qoi
        assert callable(encode_qoi)

    def test_encoder_file_exists(self):
        path = REPO_ROOT / "src" / "python" / "qoi" / "qoi_encoder.py"
        assert path.exists()

    def test_encoder_capabilities(self):
        from qoi.qoi_encoder import get_encoder_capabilities
        caps = get_encoder_capabilities()
        assert caps["operation"] == "encode"
        assert len(caps["chunk_types"]) == 6

    def test_qoi_roundtrip(self):
        from qoi.qoi_parser import QoiImage, parse_qoi_strict
        from qoi.qoi_encoder import encode_qoi
        import tempfile

        pixels = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
        img = QoiImage(width=2, height=2, channels=4, colorspace=0, pixels=pixels)
        data = encode_qoi(img)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels


# ---------------------------------------------------------------------------
# 5. Matrix deepening consistency
# ---------------------------------------------------------------------------

@pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
class TestMatrixDeepeningConsistency:

    @pytest.fixture(scope="class")
    def matrix(self):
        path = REPO_ROOT / "registry" / "format-completion-matrix.yaml"
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _find_format(self, matrix, fmt_id):
        for entry in matrix["formats"]:
            if entry["format_id"] == fmt_id:
                return entry
        return None

    def test_ods_has_export_support(self, matrix):
        entry = self._find_format(matrix, "ods")
        assert entry["export_support"] is True

    def test_ods_maturity_upgraded(self, matrix):
        entry = self._find_format(matrix, "ods")
        assert entry["actual_maturity_class"] == "roundtrip_capable_library"

    def test_qoi_has_write_support(self, matrix):
        entry = self._find_format(matrix, "qoi")
        assert entry["write_support"] is True

    def test_qoi_has_roundtrip_support(self, matrix):
        entry = self._find_format(matrix, "qoi")
        assert entry["roundtrip_support"] is True

    def test_qoi_maturity_upgraded(self, matrix):
        entry = self._find_format(matrix, "qoi")
        assert entry["actual_maturity_class"] == "roundtrip_capable_library"

    def test_zst_tests_expanded(self, matrix):
        entry = self._find_format(matrix, "zst")
        assert entry["tests_python_count"] >= 45

    def test_deepened_formats_have_r33_annotation(self, matrix):
        for fmt_id in ["ods", "qoi", "zst"]:
            entry = self._find_format(matrix, fmt_id)
            assert "r33_deepening" in entry, f"{fmt_id} missing r33_deepening annotation"
