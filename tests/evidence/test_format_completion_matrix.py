"""
Tests for format-completion-matrix.yaml integrity.

Created: R32 (2026-05-19)
Lane: I — Evidence Quality Validators

These tests ensure the format completion matrix is consistent with the actual
filesystem and that every active format has a matrix entry.
"""
import os

import pytest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MATRIX_PATH = os.path.join(REPO_ROOT, "registry", "format-completion-matrix.yaml")
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry", "format-registry.yaml")
SRC_PYTHON = os.path.join(REPO_ROOT, "src", "python")
SRC_NET = os.path.join(REPO_ROOT, "src", "net")
ACQ_PACKS = os.path.join(REPO_ROOT, "acquisition-packs")

VALID_MATURITY_CLASSES = {
    "acquisition_only",
    "probe_only",
    "read_only_prototype",
    "read_only_library_foundation",
    "read_write_library_foundation",
    "export_capable_library",
    "roundtrip_capable_library",
    "commercial_candidate",
    "production_track_real",
    "blocked",
    "stale_or_contaminated",
}


@pytest.fixture(scope="module")
def matrix():
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


@pytest.fixture(scope="module")
def registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


@pytest.fixture(scope="module")
def matrix_formats(matrix):
    return {entry["format_id"]: entry for entry in matrix["formats"]}


@pytest.fixture(scope="module")
def registry_formats(registry):
    return {entry["format_id"]: entry for entry in registry["formats"]}


class TestMatrixExists:
    def test_matrix_file_exists(self):
        assert os.path.exists(MATRIX_PATH), "format-completion-matrix.yaml must exist"

    def test_matrix_is_valid_yaml(self, matrix):
        assert "formats" in matrix
        assert isinstance(matrix["formats"], list)
        assert len(matrix["formats"]) > 0


class TestMatrixCompleteness:
    def test_every_registry_format_has_matrix_entry(self, matrix_formats, registry_formats):
        """Every format in the registry must have a completion matrix entry."""
        missing = set(registry_formats.keys()) - set(matrix_formats.keys())
        assert missing == set(), f"Formats in registry but missing from matrix: {missing}"

    def test_every_src_python_format_has_matrix_entry(self, matrix_formats):
        """Every directory in src/python/ (except __pycache__) must be in matrix."""
        if not os.path.isdir(SRC_PYTHON):
            pytest.skip("src/python not found")
        src_formats = {
            d for d in os.listdir(SRC_PYTHON)
            if os.path.isdir(os.path.join(SRC_PYTHON, d))
            and not d.startswith("_")
            and not d.startswith(".")
            and not d.endswith(".egg-info")
        }
        missing = src_formats - set(matrix_formats.keys())
        assert missing == set(), f"Formats in src/python/ but missing from matrix: {missing}"


class TestMatrixFieldIntegrity:
    def test_all_entries_have_format_id(self, matrix):
        for entry in matrix["formats"]:
            assert "format_id" in entry, f"Entry missing format_id: {entry}"

    def test_all_entries_have_maturity_class(self, matrix):
        for entry in matrix["formats"]:
            cls = entry.get("actual_maturity_class")
            assert cls in VALID_MATURITY_CLASSES, (
                f"{entry['format_id']}: invalid maturity class '{cls}'"
            )

    def test_all_entries_have_claimed_gate(self, matrix):
        for entry in matrix["formats"]:
            assert "claimed_gate" in entry, f"{entry['format_id']}: missing claimed_gate"

    def test_all_entries_have_evidence_backed_gate(self, matrix):
        for entry in matrix["formats"]:
            assert "evidence_backed_gate" in entry, (
                f"{entry['format_id']}: missing evidence_backed_gate"
            )

    def test_all_entries_have_recommended_action(self, matrix):
        for entry in matrix["formats"]:
            assert "recommended_action" in entry, (
                f"{entry['format_id']}: missing recommended_action"
            )


class TestMatrixConsistency:
    def test_src_python_exists_matches_filesystem(self, matrix_formats):
        """If matrix says src_python_exists: true, the directory must exist."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("src_python_exists"):
                path = os.path.join(SRC_PYTHON, fmt_id)
                assert os.path.isdir(path), (
                    f"{fmt_id}: matrix says src_python_exists but {path} not found"
                )

    def test_src_net_exists_matches_filesystem(self, matrix_formats):
        """If matrix says src_net_exists: true, the directory must exist."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("src_net_exists"):
                path = os.path.join(SRC_NET, fmt_id)
                assert os.path.isdir(path), (
                    f"{fmt_id}: matrix says src_net_exists but {path} not found"
                )

    def test_acquisition_pack_exists_matches_filesystem(self, matrix_formats):
        """If matrix says acquisition_pack_exists: true, the directory must exist."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("acquisition_pack_exists"):
                path = os.path.join(ACQ_PACKS, fmt_id)
                assert os.path.isdir(path), (
                    f"{fmt_id}: matrix says acquisition_pack_exists but {path} not found"
                )


class TestOverclaimDetection:
    def test_probe_only_cannot_claim_g10(self, matrix_formats):
        """Formats classified as probe_only should not have evidence_backed_gate at G10+."""
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "probe_only":
                ebg = entry.get("evidence_backed_gate", "")
                assert "G10" not in ebg and "G11" not in ebg, (
                    f"{fmt_id}: probe_only but evidence_backed_gate={ebg}"
                )

    def test_no_commercial_ready_without_g11_approval(self, matrix_formats):
        """commercial_readiness must not claim 'true' without G11 approval."""
        for fmt_id, entry in matrix_formats.items():
            cr = str(entry.get("commercial_readiness", ""))
            if "commercial_product_ready: true" in cr.lower():
                # This would be a violation
                pytest.fail(
                    f"{fmt_id}: claims commercial_product_ready true — "
                    "requires G11-G human approval"
                )

    def test_overclaim_risk_recorded(self, matrix_formats):
        """Every entry must have an overclaim_risk field."""
        for fmt_id, entry in matrix_formats.items():
            assert "overclaim_risk" in entry, (
                f"{fmt_id}: missing overclaim_risk field"
            )
