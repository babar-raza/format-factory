"""test_oracle_hardening.py — Tests for oracle hardening (MCP-W5-001 / shiny-percolating-sky)

TC-OIS-003: Honest D1 depth — SYNTHETIC_PROPERTIES excluded from D1 eligibility
TC-OIS-004: Generic invalid case executor + dispatch
TC-OIS-005: G2 fallback removed
TC-OIS-006: Source hash fields in oracle summary
TC-OIS-008: Coverage gap reporting
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.oracle.execute_oracle import (
    SYNTHETIC_PROPERTIES,
    _compare_model_properties,
    _check_case_coverage,
    _compute_source_hash,
    _compute_package_hash,
    DEPTH_D0,
    DEPTH_D1,
)


# ---------------------------------------------------------------------------
# TC-OIS-003: SYNTHETIC_PROPERTIES and honest D1 depth
# ---------------------------------------------------------------------------

def test_synthetic_properties_frozenset():
    """SYNTHETIC_PROPERTIES must contain 'loaded' and 'result_type'."""
    assert "loaded" in SYNTHETIC_PROPERTIES
    assert "result_type" in SYNTHETIC_PROPERTIES


def test_only_loaded_property_gives_d0():
    """A case with only 'loaded: true' must earn D0, not D1."""
    props = [{"property": "loaded", "value": True}]
    _, _, depth, _ = _compare_model_properties({}, props)
    assert depth == DEPTH_D0, "loaded-only case must not earn D1"


def test_only_result_type_gives_d0():
    """A case with only 'result_type' must earn D0."""
    props = [{"property": "result_type", "value": "dict"}]
    _, _, depth, _ = _compare_model_properties({}, props)
    assert depth == DEPTH_D0, "result_type-only case must not earn D1"


def test_real_property_earns_d1():
    """A case with a non-synthetic property (data_source=parsed) must earn D1."""
    props = [{"property": "row_count", "value": 3, "data_source": "parsed"}]
    _, _, depth, _ = _compare_model_properties({"row_count": 3}, props)
    assert depth == DEPTH_D1


def test_mixed_synthetic_and_real_earns_d1():
    """loaded + real property: should earn D1 (real property elevates)."""
    props = [
        {"property": "loaded", "value": True},
        {"property": "vectors", "value": 2, "data_source": "parsed"},
    ]
    _, _, depth, _ = _compare_model_properties({"vectors": 2}, props)
    assert depth == DEPTH_D1


def test_empty_expected_props_gives_d0():
    """No expected_model_properties → D0."""
    _, _, depth, _ = _compare_model_properties({}, [])
    assert depth == DEPTH_D0


def test_real_property_mismatch_detected():
    """Real property deviation must be captured even with synthetic props present."""
    props = [
        {"property": "loaded", "value": True},
        {"property": "row_count", "value": 5, "data_source": "parsed"},
    ]
    _, deviations, depth, _ = _compare_model_properties({"row_count": 3}, props)
    assert depth == DEPTH_D1
    assert len(deviations) == 1
    assert deviations[0]["property"] == "row_count"
    assert deviations[0]["expected"] == 5
    assert deviations[0]["observed"] == 3


def test_unsupported_data_source_gives_d0():
    """Properties with data_source='unsupported' must not earn D1 (TC-FGSQ-007 preserved)."""
    props = [{"property": "some_feature", "value": "x", "data_source": "unsupported"}]
    _, _, depth, _ = _compare_model_properties({"some_feature": "x"}, props)
    assert depth == DEPTH_D0


# ---------------------------------------------------------------------------
# TC-OIS-004: Generic invalid case executor coverage gaps
# ---------------------------------------------------------------------------

def test_check_case_coverage_no_gaps_for_csv():
    """CSV with invalid_cases and no roundtrip_cases: no gap expected."""
    pkg = {"invalid_cases": [{"case_id": "csv-invalid-001"}]}
    gaps = _check_case_coverage(pkg, "csv")
    assert gaps == []


def test_check_case_coverage_no_gaps_for_fods():
    """FODS with invalid_cases: no gap expected (has dedicated executor)."""
    pkg = {"invalid_cases": [{"case_id": "fods-invalid-001"}]}
    gaps = _check_case_coverage(pkg, "fods")
    assert gaps == []


def test_check_case_coverage_no_executor_config_reports_gap():
    """Format with invalid_cases but no executor_config: COVERAGE_GAP reported."""
    pkg = {
        "invalid_cases": [{"case_id": "gnumeric-invalid-001", "sample_ref": None}],
    }
    gaps = _check_case_coverage(pkg, "gnumeric")
    assert any("executor_config" in g for g in gaps)


def test_check_case_coverage_no_sample_reports_gap():
    """Invalid case with no sample_ref and no input_inline: NOT_APPLICABLE gap."""
    pkg = {
        "invalid_cases": [{"case_id": "dif-invalid-001", "sample_ref": None}],
        "executor_config": {"module": "dif.dif_parser", "callable": "parse_dif"},
    }
    gaps = _check_case_coverage(pkg, "dif")
    assert any("NOT_APPLICABLE" in g for g in gaps)


def test_check_case_coverage_no_gaps_when_no_invalid_cases():
    """Format with no invalid_cases: no coverage gap."""
    pkg = {}
    gaps = _check_case_coverage(pkg, "abw")
    assert gaps == []


# ---------------------------------------------------------------------------
# TC-OIS-005: G2 fallback removed
# ---------------------------------------------------------------------------

def test_g2_no_fallback_field_in_gate_executor():
    """gate_executor.py must not contain 'using_fallback' variable."""
    gate_path = REPO_ROOT / "tools" / "supervisor" / "gate_executor.py"
    content = gate_path.read_text(encoding="utf-8")
    assert "using_fallback" not in content, "G2 test-suite fallback must be removed"


def test_g2_no_fallback_logic_in_check_g2():
    """check_g2() must not contain the test-suite fallback path."""
    gate_path = REPO_ROOT / "tools" / "supervisor" / "gate_executor.py"
    content = gate_path.read_text(encoding="utf-8")
    # Extract just the check_g2 function body
    import re
    match = re.search(r"def check_g2\(.*?\ndef check_", content, re.DOTALL)
    if match:
        g2_body = match.group()
    else:
        g2_body = content  # fallback: check full file
    assert "using_fallback" not in g2_body, "G2 using_fallback must be removed from check_g2"
    assert "fallback: {test_count}" not in g2_body, "G2 test-count fallback message must be removed"


# ---------------------------------------------------------------------------
# TC-OIS-006: Source hash fields in oracle summary
# ---------------------------------------------------------------------------

def test_compute_source_hash_returns_sha256():
    """_compute_source_hash must return a sha256: prefixed string for known format."""
    h = _compute_source_hash("csv")
    assert h.startswith("sha256:") or h == "sha256:absent"


def test_compute_package_hash_returns_sha256():
    """_compute_package_hash must return sha256: prefixed string or absent."""
    h = _compute_package_hash("csv")
    assert h.startswith("sha256:") or h == "sha256:absent"


def test_oracle_summary_has_source_hash():
    """oracle-run-summary.json for csv must have product_source_hash after a run."""
    import json
    summary_path = REPO_ROOT / "oracle" / "formats" / "csv" / "reports" / "oracle-run-summary.json"
    if not summary_path.exists():
        pytest.skip("oracle summary not found — run oracle first")
    s = json.loads(summary_path.read_text())
    assert "product_source_hash" in s, "product_source_hash must be in oracle summary"
    assert "oracle_package_hash" in s, "oracle_package_hash must be in oracle summary"
    assert s["product_source_hash"].startswith("sha256:")


# ---------------------------------------------------------------------------
# TC-OIS-002: Oracle package upgrades for dif/fodt/sylk
# ---------------------------------------------------------------------------

def test_dif_oracle_package_has_real_properties():
    """DIF oracle package must have non-synthetic expected_model_properties."""
    import yaml
    pkg_path = REPO_ROOT / "oracle" / "formats" / "dif" / "oracle-package.yaml"
    pkg = yaml.safe_load(pkg_path.read_text())
    for case in pkg.get("valid_cases", []):
        props = case.get("expected_model_properties", [])
        non_synthetic = [p for p in props if p.get("property") not in SYNTHETIC_PROPERTIES]
        assert len(non_synthetic) >= 1, f"Case {case['case_id']} must have non-synthetic properties"


def test_fodt_oracle_package_has_real_properties():
    """FODT oracle package must have non-synthetic expected_model_properties.

    SCHEMA_VALID cases (D2 depth schema-only validation) are excluded — they
    produce a validity verdict, not model properties.
    """
    import yaml
    pkg_path = REPO_ROOT / "oracle" / "formats" / "fodt" / "oracle-package.yaml"
    pkg = yaml.safe_load(pkg_path.read_text())
    for case in pkg.get("valid_cases", []):
        # Skip schema-only cases that produce SCHEMA_VALID, not model properties
        if case.get("expected_parse_result") == "SCHEMA_VALID":
            continue
        props = case.get("expected_model_properties", [])
        non_synthetic = [p for p in props if p.get("property") not in SYNTHETIC_PROPERTIES]
        assert len(non_synthetic) >= 1, f"Case {case['case_id']} must have non-synthetic properties"


def test_sylk_oracle_package_has_real_properties():
    """SYLK oracle package must have non-synthetic expected_model_properties."""
    import yaml
    pkg_path = REPO_ROOT / "oracle" / "formats" / "sylk" / "oracle-package.yaml"
    pkg = yaml.safe_load(pkg_path.read_text())
    for case in pkg.get("valid_cases", []):
        props = case.get("expected_model_properties", [])
        non_synthetic = [p for p in props if p.get("property") not in SYNTHETIC_PROPERTIES]
        assert len(non_synthetic) >= 1, f"Case {case['case_id']} must have non-synthetic properties"


def test_sylk_executor_uses_parse_sylk():
    """execute_sylk_valid_case must use parse_sylk, not SylkDocument constructor."""
    oracle_path = REPO_ROOT / "tools" / "oracle" / "execute_oracle.py"
    content = oracle_path.read_text(encoding="utf-8")
    # Look for the execute_sylk_valid_case function definition
    assert '"parse_sylk"' in content, "SYLK executor must use parse_sylk (not SylkDocument)"
    # Verify the old wrong callable is gone from the sylk wrapper
    # (SylkDocument may appear elsewhere but not in execute_sylk_valid_case)
    import re
    match = re.search(r'def execute_sylk_valid_case.*?return execute_generic_load_case\(.*?\)',
                      content, re.DOTALL)
    assert match, "execute_sylk_valid_case must call execute_generic_load_case"
    assert "parse_sylk" in match.group(), "SYLK callable must be parse_sylk"
