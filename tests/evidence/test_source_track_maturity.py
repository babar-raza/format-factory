"""
Tests for source track maturity policy compliance.

Created: R32 (2026-05-19)
Lane: I — Evidence Quality Validators

Validates that formats in src/python/ meet source-track-maturity-policy.md
requirements, and that maturity classifications are consistent.
"""
import os

import pytest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MATRIX_PATH = os.path.join(REPO_ROOT, "registry", "format-completion-matrix.yaml")
SRC_PYTHON = os.path.join(REPO_ROOT, "src", "python")
TESTS_PYTHON = os.path.join(REPO_ROOT, "tests", "python")
TASKCARDS = os.path.join(REPO_ROOT, "taskcards")


@pytest.fixture(scope="module")
def matrix_formats():
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {entry["format_id"]: entry for entry in data["formats"]}


def _count_test_methods(fmt_id):
    test_dir = os.path.join(TESTS_PYTHON, fmt_id)
    count = 0
    if not os.path.isdir(test_dir):
        return 0
    for root, _dirs, files in os.walk(test_dir):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "def test_" in line:
                            count += 1
    return count


class TestSourceTrackPresence:
    """Formats in src/python/ must have matrix entries."""

    def test_all_src_python_formats_classified(self, matrix_formats):
        if not os.path.isdir(SRC_PYTHON):
            pytest.skip("src/python not found")
        for d in os.listdir(SRC_PYTHON):
            if (os.path.isdir(os.path.join(SRC_PYTHON, d))
                    and not d.startswith("_")
                    and not d.startswith(".")
                    and not d.endswith(".egg-info")):
                assert d in matrix_formats, (
                    f"src/python/{d}/ exists but has no matrix entry"
                )


class TestMaturityClassConsistency:

    def test_production_track_has_tests(self, matrix_formats):
        """production_track_real must have >= 25 tests."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "production_track_real":
                total = entry.get("tests_python_count", 0) + entry.get("tests_net_count", 0)
                assert total >= 25, (
                    f"{fmt_id}: production_track_real but only {total} tests"
                )

    def test_library_foundation_has_model(self, matrix_formats):
        """read_only_library_foundation must have a neutral model."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") in (
                "read_only_library_foundation",
                "read_write_library_foundation",
            ):
                nms = entry.get("neutral_model_status", "")
                assert nms and "N/A" not in nms and "plain dict" not in nms, (
                    f"{fmt_id}: library_foundation but neutral_model_status='{nms}'"
                )

    def test_read_write_has_write(self, matrix_formats):
        """read_write_library_foundation must have write_support."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "read_write_library_foundation":
                assert entry.get("write_support") is True, (
                    f"{fmt_id}: read_write_library_foundation but no write_support"
                )

    def test_roundtrip_has_roundtrip(self, matrix_formats):
        """roundtrip_capable_library must have roundtrip_support."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "roundtrip_capable_library":
                assert entry.get("roundtrip_support") is True, (
                    f"{fmt_id}: roundtrip_capable_library but no roundtrip_support"
                )

    def test_acquisition_only_has_no_source(self, matrix_formats):
        """acquisition_only must not have src_python or src_net."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "acquisition_only":
                assert not entry.get("src_python_exists"), (
                    f"{fmt_id}: acquisition_only but src_python_exists=true"
                )
                assert not entry.get("src_net_exists"), (
                    f"{fmt_id}: acquisition_only but src_net_exists=true"
                )


class TestProbeInSrcPython:
    """Probe-only formats in src/python/ must have drift taskcards."""

    def test_probe_only_in_src_python_has_drift_taskcard(self, matrix_formats):
        """If a format is probe_only but lives in src/python/, a DRIFT-* taskcard should exist."""
        for fmt_id, entry in matrix_formats.items():
            if (
                entry.get("actual_maturity_class") == "probe_only"
                and entry.get("src_python_exists")
            ):
                # Check for DRIFT-* taskcard
                expected_patterns = [
                    f"DRIFT-{fmt_id.upper()}",
                    f"DRIFT-{fmt_id.upper().replace('-', '_')}",
                ]
                found = False
                if os.path.isdir(TASKCARDS):
                    for tc in os.listdir(TASKCARDS):
                        for pattern in expected_patterns:
                            if pattern in tc.upper():
                                found = True
                                break
                assert found, (
                    f"{fmt_id}: probe_only in src/python/ but no DRIFT-* taskcard found"
                )


class TestOverclaimRiskHighHasTaskcard:
    """High overclaim risk must have a DRIFT-* taskcard."""

    def test_high_overclaim_has_taskcard(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            if entry.get("overclaim_risk") == "high":
                found = False
                if os.path.isdir(TASKCARDS):
                    for tc in os.listdir(TASKCARDS):
                        if fmt_id.upper().replace("-", "_") in tc.upper() and "DRIFT" in tc.upper():
                            found = True
                            break
                assert found, (
                    f"{fmt_id}: overclaim_risk=high but no DRIFT-* taskcard found"
                )


class TestTestCountsAccurate:
    """Matrix test counts should approximately match filesystem."""

    def test_python_test_counts_reasonable(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            if not entry.get("src_python_exists"):
                continue
            claimed = entry.get("tests_python_count", 0)
            actual = _count_test_methods(fmt_id)
            if actual == 0 and claimed == 0:
                continue
            # Allow 20% tolerance for counting method differences
            assert actual >= claimed * 0.8, (
                f"{fmt_id}: matrix claims {claimed} tests but found {actual}"
            )
