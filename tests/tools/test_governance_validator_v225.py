"""
Tests for V225 (validate_sal_store_reconciliation) in governance_validators_ext7.py.

Proves each drift class is actually detected:
  - code binding mismatch / missing symbol
  - alias missing or mismatched
  - architecture count drift
  - store fact absent from combined DB
  - completeness shortfall: FAIL when untracked, WARN when an OPEN B2 gap covers it
  - clean fixture passes
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"

if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

spec = importlib.util.spec_from_file_location(
    "governance_validators_ext7", _SUPERVISOR / "governance_validators_ext7.py"
)
ext7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ext7)

validate = ext7.validate_sal_store_reconciliation


def _base_fixture(tmp_path: Path) -> Path:
    """A minimal repo with one clean, fully reconciled format ('demo')."""
    (tmp_path / "shared" / "sal-facts").mkdir(parents=True)
    (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
    (tmp_path / "registry").mkdir()
    (tmp_path / ".local" / "spec-cache").mkdir(parents=True)
    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "demo_parser.py").write_text(
        "DEMO_MAGIC = 0xAB\nDEMO_END = bytes([0, 1])\n", encoding="utf-8"
    )

    facts = [
        {
            "fact_id": "SAL-DEMO-00001",
            "qname": "FACT-DEMO-001",
            "claim": "demo magic byte",
            "code_bindings": [
                {"file": "src/demo_parser.py", "symbol": "DEMO_MAGIC", "expected": "0xAB"},
                {"file": "src/demo_parser.py", "symbol": "DEMO_END", "expected": "0001"},
            ],
        },
    ]
    (tmp_path / "shared" / "sal-facts" / "demo.yaml").write_text(
        yaml.safe_dump({"format_id": "demo", "facts": facts}, sort_keys=False),
        encoding="utf-8",
    )
    (tmp_path / "shared" / "sal-fact-id-aliases.json").write_text(
        json.dumps({"aliases": {"FACT-DEMO-001": "SAL-DEMO-00001"}}), encoding="utf-8"
    )
    (tmp_path / ".local" / "spec-cache" / "sal-facts-latest.json").write_text(
        json.dumps({"results": [{"format_id": "demo", "spec_facts": [
            {"fact_id": "SAL-DEMO-00001", "qname": "FACT-DEMO-001", "claim": "demo magic byte"},
        ]}]}),
        encoding="utf-8",
    )
    (tmp_path / "registry" / "python-qname-architecture.json").write_text(
        json.dumps({"formats": {"demo": {"state": "ACCEPTED_VERIFIED", "sal_facts_count": 1}}}),
        encoding="utf-8",
    )
    (tmp_path / "shared" / "qname-registry" / "demo.yaml").write_text(
        yaml.safe_dump([{"qname": "demo:magic", "spec_fact_ref": "SAL-DEMO-00001"}]),
        encoding="utf-8",
    )
    return tmp_path


def _edit_store(root: Path, mutate) -> None:
    store_path = root / "shared" / "sal-facts" / "demo.yaml"
    store = yaml.safe_load(store_path.read_text(encoding="utf-8"))
    mutate(store)
    store_path.write_text(yaml.safe_dump(store, sort_keys=False), encoding="utf-8")


def test_clean_fixture_passes(tmp_path):
    result = validate({}, _base_fixture(tmp_path))
    assert result["result"] == "PASS", result["violations"]


def test_int_binding_mismatch_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _edit_store(root, lambda s: s["facts"][0]["code_bindings"].__setitem__(
        0, {"file": "src/demo_parser.py", "symbol": "DEMO_MAGIC", "expected": "0xFF"}))
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("binding mismatch" in v for v in result["violations"])


def test_str_binding_match_and_mismatch(tmp_path):
    root = _base_fixture(tmp_path)
    (root / "src" / "demo_parser.py").write_text(
        'DEMO_MAGIC = 0xAB\nDEMO_END = bytes([0, 1])\nDEMO_TAG = "P1"\n', encoding="utf-8")
    _edit_store(root, lambda s: s["facts"][0]["code_bindings"].append(
        {"file": "src/demo_parser.py", "symbol": "DEMO_TAG", "expected": "P1"}))
    assert validate({}, root)["result"] == "PASS"
    _edit_store(root, lambda s: s["facts"][0]["code_bindings"].__setitem__(
        -1, {"file": "src/demo_parser.py", "symbol": "DEMO_TAG", "expected": "P9"}))
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("binding mismatch" in v for v in result["violations"])


def test_bytes_binding_mismatch_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _edit_store(root, lambda s: s["facts"][0]["code_bindings"].__setitem__(
        1, {"file": "src/demo_parser.py", "symbol": "DEMO_END", "expected": "0002"}))
    result = validate({}, root)
    assert result["result"] == "FAIL"


def test_missing_symbol_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _edit_store(root, lambda s: s["facts"][0]["code_bindings"].__setitem__(
        0, {"file": "src/demo_parser.py", "symbol": "NO_SUCH", "expected": "0x01"}))
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("not found" in v for v in result["violations"])


def test_missing_alias_fails(tmp_path):
    root = _base_fixture(tmp_path)
    (root / "shared" / "sal-fact-id-aliases.json").write_text(
        json.dumps({"aliases": {}}), encoding="utf-8")
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("alias missing" in v for v in result["violations"])


def test_arch_count_drift_fails(tmp_path):
    root = _base_fixture(tmp_path)
    (root / "registry" / "python-qname-architecture.json").write_text(
        json.dumps({"formats": {"demo": {"state": "ACCEPTED_VERIFIED", "sal_facts_count": 99}}}),
        encoding="utf-8")
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("sal_facts_count=99" in v for v in result["violations"])


def test_fact_absent_from_combined_db_fails(tmp_path):
    root = _base_fixture(tmp_path)
    (root / ".local" / "spec-cache" / "sal-facts-latest.json").write_text(
        json.dumps({"results": [{"format_id": "demo", "spec_facts": []}]}), encoding="utf-8")
    result = validate({}, root)
    assert result["result"] == "FAIL"
    assert any("absent from combined DB" in v for v in result["violations"])


def test_missing_combined_db_is_tolerated(tmp_path):
    """Fresh checkout: no .local cache. Committed-layer checks still run."""
    root = _base_fixture(tmp_path)
    (root / ".local" / "spec-cache" / "sal-facts-latest.json").unlink()
    result = validate({}, root)
    assert result["result"] == "PASS", result["violations"]


def _add_spec_unit_register(root: Path, tracked: bool):
    reg_dir = root / "reports" / "spec-to-code-forensic-audit"
    reg_dir.mkdir(parents=True)
    (reg_dir / "raw-spec-unit-register.yaml").write_text(
        yaml.safe_dump({"per_format": [{"format_id": "demo", "raw_spec_units": 10}]}),
        encoding="utf-8")
    gaps = []
    if tracked:
        gaps = [{"gap_id": "GAP-TEST-1", "status": "OPEN",
                 "pipeline_boundary": "B2_spec_unit_to_sal_fact", "scope": ["demo"]}]
    (reg_dir / "forensic-gap-register.yaml").write_text(
        yaml.safe_dump({"gaps": gaps}), encoding="utf-8")


def test_untracked_completeness_shortfall_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _add_spec_unit_register(root, tracked=False)
    result = validate({}, root)  # 1 fact / 10 units = 0.1
    assert result["result"] == "FAIL"
    assert any("UNTRACKED" in v for v in result["violations"])


def test_tracked_completeness_shortfall_warns(tmp_path):
    root = _base_fixture(tmp_path)
    _add_spec_unit_register(root, tracked=True)
    result = validate({}, root)
    assert result["result"] == "WARN"
    assert any("tracked by OPEN B2 gap" in v for v in result["violations"])
