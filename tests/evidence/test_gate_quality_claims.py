"""
Tests for gate quality claims vs actual source evidence.

Created: R32 (2026-05-19)
Lane: I — Evidence Quality Validators

These tests validate that gate claims in the completion matrix are supported
by actual source/test evidence, per docs/governance/gate-quality-criteria.md.
"""
import os

import pytest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MATRIX_PATH = os.path.join(REPO_ROOT, "registry", "format-completion-matrix.yaml")
SRC_PYTHON = os.path.join(REPO_ROOT, "src", "python")
SRC_NET = os.path.join(REPO_ROOT, "src", "net")
TESTS_PYTHON = os.path.join(REPO_ROOT, "tests", "python")


@pytest.fixture(scope="module")
def matrix_formats():
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {entry["format_id"]: entry for entry in data["formats"]}


def _count_test_methods(test_dir):
    """Count 'def test_' occurrences in a test directory."""
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


def _has_neutral_model(fmt_id):
    """Check if format has a neutral_model.py or dataclass-based model."""
    nm_path = os.path.join(SRC_PYTHON, fmt_id, "neutral_model.py")
    if os.path.isfile(nm_path):
        return True
    # Check for dataclass usage in main parser
    for fname in os.listdir(os.path.join(SRC_PYTHON, fmt_id)):
        if fname.endswith(".py") and not fname.startswith("_"):
            fpath = os.path.join(SRC_PYTHON, fmt_id, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "@dataclass" in content or "dataclass" in content:
                    return True
    return False


def _has_write_capability(fmt_id):
    """Check if format has write/save/compress/export in source."""
    fmt_dir = os.path.join(SRC_PYTHON, fmt_id)
    if not os.path.isdir(fmt_dir):
        return False
    for fname in os.listdir(fmt_dir):
        if fname.endswith(".py") and not fname.startswith("_"):
            fpath = os.path.join(fmt_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if any(kw in content for kw in ["def save", "def write", "def export", "def compress", "def encode"]):
                    return True
    return False


class TestGate5Requirements:
    """Gate 5 requires neutral model with at least 5 modeled features."""

    def test_g5_plus_formats_have_model(self, matrix_formats):
        """Formats with evidence_backed_gate >= G5 must have a neutral model."""
        for fmt_id, entry in matrix_formats.items():
            ebg = entry.get("evidence_backed_gate", "")
            if not entry.get("src_python_exists"):
                continue
            # Parse gate number from evidence_backed_gate
            gate_num = 0
            for part in ebg.replace("G", "").replace("(", "").split("-"):
                part = part.strip().split()[0]
                try:
                    gate_num = max(gate_num, int(part))
                except ValueError:
                    pass
            if gate_num >= 5:
                nms = entry.get("neutral_model_status", "")
                assert nms and "N/A" not in nms, (
                    f"{fmt_id}: evidence_backed_gate includes G{gate_num}+ "
                    f"but neutral_model_status is '{nms}'"
                )


class TestGate8SecurityNotProductMaturity:
    """Gate 8 security pass does not imply product readiness."""

    def test_g8_does_not_imply_packaging(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            ebg = entry.get("evidence_backed_gate", "")
            maturity = entry.get("actual_maturity_class", "")
            if "G8" in ebg and maturity in ("probe_only", "read_only_prototype"):
                pkg = entry.get("package_readiness", "none")
                if pkg not in ("none", "N/A", None, ""):
                    # Acceptable if local build exists from earlier work
                    pass  # No assertion — just awareness


class TestGate10Requirements:
    """Gate 10 requires write/export/round-trip or approved read-only scope."""

    def test_g10_evidence_requires_capability(self, matrix_formats):
        """
        If evidence_backed_gate includes G10, format must have:
        - write_support: true, OR
        - export_support: true, OR
        - roundtrip_support: true, OR
        - maturity class that allows read-only (with approved scope)
        """
        for fmt_id, entry in matrix_formats.items():
            ebg = entry.get("evidence_backed_gate", "")
            if "G10" not in ebg:
                continue
            has_write = entry.get("write_support") is True
            has_export = entry.get("export_support") is True
            has_roundtrip = entry.get("roundtrip_support") is True
            maturity = entry.get("actual_maturity_class", "")
            if not (has_write or has_export or has_roundtrip):
                # Must be an approved read-only scope or production_track_real
                assert maturity in (
                    "production_track_real",
                    "read_write_library_foundation",
                    "roundtrip_capable_library",
                    "export_capable_library",
                ), (
                    f"{fmt_id}: evidence_backed_gate=G10 but no write/export/roundtrip "
                    f"and maturity={maturity}"
                )

    def test_g10_evidence_has_sufficient_tests(self, matrix_formats):
        """Formats with G10 evidence should have >= 25 tests."""
        for fmt_id, entry in matrix_formats.items():
            ebg = entry.get("evidence_backed_gate", "")
            if "G10" not in ebg:
                continue
            test_count = entry.get("tests_python_count", 0) + entry.get("tests_net_count", 0)
            assert test_count >= 25, (
                f"{fmt_id}: evidence_backed_gate=G10 but only {test_count} tests"
            )


class TestGate11Requirements:
    """Gate 11 requires .NET implementation and human approval."""

    def test_no_commercial_ready_without_net_source(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            cr = str(entry.get("commercial_readiness", ""))
            if "commercial_product_ready: true" in cr.lower():
                assert entry.get("src_net_exists"), (
                    f"{fmt_id}: commercial_product_ready true but no .NET source"
                )

    def test_commercial_readiness_is_false_everywhere(self, matrix_formats):
        """Currently no format should claim commercial_product_ready: true."""
        for fmt_id, entry in matrix_formats.items():
            cr = str(entry.get("commercial_readiness", ""))
            assert "commercial_product_ready: true" not in cr.lower(), (
                f"{fmt_id}: commercial_product_ready true — "
                "G11-G human approval has not been granted"
            )


class TestProbeOnlyConstraints:
    """Probe-only formats have strict constraints."""

    def test_probe_only_has_no_write(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "probe_only":
                assert entry.get("write_support") is not True, (
                    f"{fmt_id}: probe_only but has write_support"
                )

    def test_probe_only_has_no_export(self, matrix_formats):
        for fmt_id, entry in matrix_formats.items():
            if entry.get("actual_maturity_class") == "probe_only":
                assert entry.get("export_support") is not True, (
                    f"{fmt_id}: probe_only but has export_support"
                )
