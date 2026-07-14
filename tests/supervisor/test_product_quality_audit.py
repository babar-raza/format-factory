"""Tests for tools/supervisor/product_quality_audit.py — TC-SPW-005.

One test per check (6 checks) + integration test.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

from product_quality_audit import ProductQualityAudit, CheckResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_cs(directory: Path, filename: str, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    f = directory / filename
    f.write_text(content, encoding="utf-8")
    return f


def _make_audit(tmp_path: Path) -> ProductQualityAudit:
    return ProductQualityAudit(repo_root=tmp_path)


# ---------------------------------------------------------------------------
# Check 1: check_aggregate_loc
# ---------------------------------------------------------------------------

def test_check_aggregate_loc_warns_for_large_class(tmp_path, monkeypatch):
    """check_aggregate_loc: class with 10 partial files at high LOC → WARN (if above cap)."""
    src_dir = tmp_path / "src" / "net" / "fods"
    src_dir.mkdir(parents=True)
    # Write 2 partial files so collect_partial_class_aggregates finds them
    content = "public partial class BigClass { int x; }\n" * 200
    _write_cs(src_dir, "BigClass.cs", content)
    _write_cs(src_dir, "BigClassOps.cs", content)

    # Patch baseline: BigClass has lower cap than total LOC
    import json
    baseline = {
        "known_violations": {},
        "partial_class_aggregates": {
            "BigClass": {"aggregate_cap": 100, "trajectory": "decrease_required_on_touch"}
        }
    }
    baseline_path = tmp_path / "registry" / "source-structure-baseline.json"
    baseline_path.parent.mkdir(parents=True)
    baseline_path.write_text(json.dumps(baseline))

    import governance_validators_dotnet as gvd
    monkeypatch.setattr(gvd, "_BASELINE_PATH", baseline_path)
    monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

    audit = _make_audit(tmp_path)
    result = audit._check_aggregate_loc("fods", src_dir)
    assert result.verdict in ("WARN", "FAIL")
    assert result.count >= 1


# ---------------------------------------------------------------------------
# Check 2: check_writer_surface
# ---------------------------------------------------------------------------

def test_check_writer_surface_fails_for_small_writer(tmp_path, monkeypatch):
    """check_writer_surface: Writer file at 57 LOC for Gate-1 format → FAIL."""
    src_dir = tmp_path / "src" / "net" / "fods"
    # Write a small FodsWriter.cs (57 lines)
    _write_cs(src_dir, "FodsWriter.cs", "// writer\n" * 57)

    # Patch gate-1 check to return True for "fods"
    audit = _make_audit(tmp_path)
    import unittest.mock as mock
    with mock.patch.object(audit, "_is_gate1", return_value=True):
        result = audit._check_writer_surface("fods", src_dir)
    assert result.verdict == "FAIL"
    assert result.count < 100


def test_check_writer_surface_passes_for_adequate_writer(tmp_path, monkeypatch):
    """check_writer_surface: Writer file at 200 LOC for Gate-1 format → PASS."""
    src_dir = tmp_path / "src" / "net" / "fods"
    _write_cs(src_dir, "FodsWriter.cs", "// code\n" * 200)

    audit = _make_audit(tmp_path)
    import unittest.mock as mock
    with mock.patch.object(audit, "_is_gate1", return_value=True):
        result = audit._check_writer_surface("fods", src_dir)
    assert result.verdict == "PASS"
    assert result.count >= 100


# ---------------------------------------------------------------------------
# Check 3: check_roundtrip_coverage
# ---------------------------------------------------------------------------

def test_check_roundtrip_coverage_fails_when_no_test(tmp_path):
    """check_roundtrip_coverage: No round-trip test in tests/net/fods/ → FAIL."""
    (tmp_path / "tests" / "net" / "fods").mkdir(parents=True)
    # Only a load-only test
    _write_cs(tmp_path / "tests" / "net" / "fods", "LoadTest.cs", "doc = FodsDocument.Load(path);\n")

    audit = _make_audit(tmp_path)
    result = audit._check_roundtrip_coverage("fods")
    assert result.verdict == "FAIL"


def test_check_roundtrip_coverage_passes_when_test_exists(tmp_path):
    """check_roundtrip_coverage: Round-trip test present → PASS."""
    test_dir = tmp_path / "tests" / "net" / "fods"
    _write_cs(test_dir, "RoundtripTest.cs", "var doc = FodsDocument.Load(path);\ndoc.Save(outpath);\n")

    audit = _make_audit(tmp_path)
    result = audit._check_roundtrip_coverage("fods")
    assert result.verdict == "PASS"


# ---------------------------------------------------------------------------
# Check 4: check_dictionary_state
# ---------------------------------------------------------------------------

def test_check_dictionary_state_counts_dict_fields(tmp_path):
    """check_dictionary_state: file with 3 Dictionary<> occurrences → WARN with count 3."""
    src_dir = tmp_path / "src" / "net" / "fods"
    _write_cs(src_dir, "FodsDoc.cs", (
        "private Dictionary<string, int> _a = new();\n"
        "private Dictionary<string, string> _b = new();\n"
        "private Dictionary<int, object> _c = new();\n"
    ))

    audit = _make_audit(tmp_path)
    result = audit._check_dictionary_state("fods", src_dir)
    assert result.verdict == "WARN"
    assert result.count >= 3


def test_check_dictionary_state_passes_when_no_dicts(tmp_path):
    """check_dictionary_state: No Dictionary fields → PASS."""
    src_dir = tmp_path / "src" / "net" / "fods"
    _write_cs(src_dir, "FodsDoc.cs", "private int _x; private string _y;\n")

    audit = _make_audit(tmp_path)
    result = audit._check_dictionary_state("fods", src_dir)
    assert result.verdict == "PASS"


# ---------------------------------------------------------------------------
# Check 5: check_api_documentation
# ---------------------------------------------------------------------------

def test_check_api_documentation_counts_undocumented(tmp_path):
    """check_api_documentation: 2 undocumented public methods → WARN with count ≥ 2."""
    src_dir = tmp_path / "src" / "net" / "fods"
    _write_cs(src_dir, "FodsDoc.cs", (
        "public void MethodA() {}\n"
        "public string GetValue(string key) { return key; }\n"
    ))

    audit = _make_audit(tmp_path)
    result = audit._check_api_documentation("fods", src_dir)
    assert result.verdict == "WARN"
    assert result.count >= 2


# ---------------------------------------------------------------------------
# Check 6: check_partial_class_count
# ---------------------------------------------------------------------------

def test_check_partial_class_count_warns_for_too_many_partials(tmp_path, monkeypatch):
    """check_partial_class_count: class with 10 partial files → WARN."""
    src_dir = tmp_path / "src" / "net" / "fods"
    for i in range(10):
        _write_cs(src_dir, f"FodsDoc{i}.cs", f"public partial class FodsDoc {{ int x{i}; }}\n")

    import governance_validators_dotnet as gvd
    monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

    audit = _make_audit(tmp_path)
    result = audit._check_partial_class_count("fods", src_dir)
    assert result.verdict == "WARN"
    assert result.count >= 1


def test_check_partial_class_count_passes_for_few_partials(tmp_path, monkeypatch):
    """check_partial_class_count: class with 2 partial files → PASS (not over limit)."""
    src_dir = tmp_path / "src" / "net" / "fods"
    _write_cs(src_dir, "FodsDoc.cs", "public partial class FodsDoc { int x; }\n")
    _write_cs(src_dir, "FodsDocOps.cs", "public partial class FodsDoc { void F() {} }\n")

    import governance_validators_dotnet as gvd
    monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

    audit = _make_audit(tmp_path)
    result = audit._check_partial_class_count("fods", src_dir)
    assert result.verdict == "PASS"


# ---------------------------------------------------------------------------
# Integration: Run all 6 checks against real repo FODS .NET
# ---------------------------------------------------------------------------

def test_integration_real_fods_produces_6_checks():
    """Integration: Running all 6 checks against actual src/net/fods/ → 6 results, ≥3 non-PASS."""
    audit = ProductQualityAudit()
    result = audit.run("fods", "dotnet", "test-integration")
    assert len(result.checks) == 6, f"Expected 6 checks, got {len(result.checks)}"
    non_pass = sum(1 for c in result.checks if c.verdict not in ("PASS", "SKIP"))
    assert non_pass >= 3, f"Expected ≥3 WARN/FAIL, got {non_pass}: {[(c.check_name, c.verdict) for c in result.checks]}"
    # Validate to_dict works
    d = result.to_dict()
    assert "checks" in d and "warn_count" in d


def test_non_dotnet_language_returns_skip():
    """Audit for non-dotnet language → SKIP immediately."""
    audit = ProductQualityAudit()
    result = audit.run("fods", "python", "test-skip")
    assert all(c.verdict == "SKIP" for c in result.checks)
