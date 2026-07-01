"""
tests/python/test_gate4_governance.py

Gate 4 governance tests.
Verifies that the format registry satisfies Gate 4 coverage invariants.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"

NOT_APPLICABLE = {"odf-shared"}
BLOCKED_FORMATS = {"zpaq", "ora"}
VALID_EVIDENCE_TYPES = {
    "STANDALONE_PROTOTYPE",
    "EVIDENCE_WRAPPER",
    "SOURCE_TRACK_EQUIVALENT",
    "BLOCKED_BEFORE_GATE4",
    "NOT_APPLICABLE",
}


def _load_registry():
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_registry_file_exists():
    assert REGISTRY_PATH.exists(), "format-registry.yaml must exist"


def test_every_format_has_gate4_disposition():
    """Every tracked format (except NOT_APPLICABLE set) must have a gate_4 block."""
    data = _load_registry()
    missing = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid in NOT_APPLICABLE:
            continue
        g4 = fmt.get("gates", {}).get("gate_4")
        if g4 is None:
            missing.append(fid)
    assert missing == [], f"Formats missing gate_4 block: {missing}"


def test_every_gate4_block_has_evidence_type():
    """Every gate_4 block that exists must have evidence_type field."""
    data = _load_registry()
    missing_et = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid in NOT_APPLICABLE:
            continue
        g4 = fmt.get("gates", {}).get("gate_4")
        if g4 and not g4.get("evidence_type"):
            missing_et.append(fid)
    assert missing_et == [], f"Formats with gate_4 but missing evidence_type: {missing_et}"


def test_evidence_types_are_valid():
    """All evidence_type values must be from the known set."""
    data = _load_registry()
    invalid = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4", {})
        et = g4.get("evidence_type") if g4 else None
        if et and et not in VALID_EVIDENCE_TYPES:
            invalid.append((fid, et))
    assert invalid == [], f"Invalid evidence_types: {invalid}"


def test_blocked_formats_not_passed():
    """zpaq and ora must NOT have gate_4.status = passed."""
    data = _load_registry()
    false_passes = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid not in BLOCKED_FORMATS:
            continue
        g4 = fmt.get("gates", {}).get("gate_4", {})
        if g4 and g4.get("status") == "passed":
            false_passes.append(fid)
    assert false_passes == [], f"Blocked formats incorrectly marked passed: {false_passes}"


def test_no_path_only_claims():
    """No gate_4 block with status=passed may have only prototype_path and no tests."""
    data = _load_registry()
    path_only = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid in NOT_APPLICABLE:
            continue
        g4 = fmt.get("gates", {}).get("gate_4", {})
        if not g4:
            continue
        if g4.get("status") == "passed" and not g4.get("tests"):
            path_only.append(fid)
    assert path_only == [], f"Formats with passed gate_4 but no tests[]: {path_only}"


def test_passed_formats_have_corpus():
    """All formats with gate_4.status=passed must have corpus[]."""
    data = _load_registry()
    no_corpus = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid in NOT_APPLICABLE:
            continue
        g4 = fmt.get("gates", {}).get("gate_4", {})
        if not g4:
            continue
        et = g4.get("evidence_type", "")
        if g4.get("status") == "passed" and et not in ("BLOCKED_BEFORE_GATE4", "NOT_APPLICABLE"):
            if not g4.get("corpus"):
                no_corpus.append(fid)
    assert no_corpus == [], f"Passed formats missing corpus[]: {no_corpus}"


def test_unclassified_supported_formats_is_zero():
    """UNCLASSIFIED_SUPPORTED_FORMATS counter must be 0."""
    data = _load_registry()
    unclassified = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        if fid in NOT_APPLICABLE:
            continue
        g4 = fmt.get("gates", {}).get("gate_4")
        if g4 is None:
            unclassified.append(fid)
    assert len(unclassified) == 0, f"Unclassified formats: {unclassified}"


def test_standalone_prototype_has_prototype_path():
    """All STANDALONE_PROTOTYPE formats must have prototype_path set."""
    data = _load_registry()
    missing_pp = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4", {})
        if g4 and g4.get("evidence_type") == "STANDALONE_PROTOTYPE":
            if not g4.get("prototype_path"):
                missing_pp.append(fid)
    assert missing_pp == [], f"STANDALONE_PROTOTYPE missing prototype_path: {missing_pp}"


def test_evidence_wrapper_has_delegated_source():
    """All EVIDENCE_WRAPPER formats must have delegated_source_path set."""
    data = _load_registry()
    missing_dsp = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4", {})
        if g4 and g4.get("evidence_type") == "EVIDENCE_WRAPPER":
            if not g4.get("delegated_source_path"):
                missing_dsp.append(fid)
    assert missing_dsp == [], f"EVIDENCE_WRAPPER missing delegated_source_path: {missing_dsp}"


def test_validator_passes_all_formats():
    """The Gate 4 validator must pass for all 25 tracked formats (0 FAIL)."""
    from tools.gates.validate_gate4_evidence import validate_gate4, NOT_APPLICABLE_FORMATS
    data = _load_registry()
    all_errors = []
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        errors = validate_gate4(fid, fmt)
        all_errors.extend(errors)
    assert all_errors == [], f"Validator failures:\n" + "\n".join(all_errors)


def test_registry_consistent_after_update_and_patch():
    """TC-G4-HRD-001: Validator accepts current registry state (proves update+patch atomicity).

    Running validate_gate4_evidence on the live registry proves that the registry
    is in a consistent, fully-patched state. Any partial run (e.g., update without
    patch) would leave formats without evidence_type, which the validator catches.
    """
    from tools.gates.validate_gate4_evidence import validate_gate4
    data = _load_registry()
    for fmt in data["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4")
        if g4 is None:
            continue
        # Every gate_4 block must have evidence_type — proves patch script ran
        assert g4.get("evidence_type"), (
            f"{fid}: gate_4 missing evidence_type — patch script may not have run"
        )
        errors = validate_gate4(fid, fmt)
        assert errors == [], f"{fid}: validator errors after update+patch: {errors}"
