"""Tests for V91 root structure validator (TC-ROOT-006, TC-RR-010)."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest
import yaml

# Ensure tools/supervisor is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

from governance_validators_root_struct import (  # noqa: E402
    validate_root_structure,
    _check_source_test_parity,
    _check_readme_content_floor,
    _check_registry_producer_integrity,
)


# ---------- Fixtures ----------

MINIMAL_REGISTRY = textwrap.dedent("""\
    schema_version: "1.0"
    folders:
      - folder_path: "src/"
        retention: RETAIN
        readme_required: true
        readme_convention: README.md
        format_scoped: false
      - folder_path: "docs/"
        retention: RETAIN
        readme_required: true
        readme_convention: README.md
        format_scoped: false
      - folder_path: "registry/"
        retention: RETAIN
        readme_required: false
        format_scoped: false
      - folder_path: ".venv/"
        retention: EXEMPT
        readme_required: false
      - folder_path: "old-stuff/"
        retention: DELETED
""")


@pytest.fixture
def fake_repo(tmp_path: Path):
    """Create a minimal fake repo structure with registry."""
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()
    (reg_dir / "repository-root-folders.yaml").write_text(MINIMAL_REGISTRY, encoding="utf-8")

    _ADEQUATE_README = (
        "# Source\n\n"
        "This folder contains product source code. Created by developers.\n\n"
        "## Purpose\n\nHolds format implementation source files.\n\n"
        "## Agent Navigation\n\n"
        "Producer: developers and spec-parity tools.\n"
        "Run: python .venv/Scripts/pytest tests/ -q to validate.\n"
        "Validation command: python tools/supervisor/governance_validators_root_struct.py\n"
    )

    # Create the registered directories
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "README.md").write_text(_ADEQUATE_README, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "README.md").write_text(_ADEQUATE_README, encoding="utf-8")
    (tmp_path / ".venv").mkdir()

    return tmp_path


# ---------- Tests ----------

def test_pass_on_valid_repo(fake_repo: Path):
    """Validator returns PASS when all registered dirs exist with READMEs."""
    result = validate_root_structure({}, fake_repo)
    assert result["result"] == "PASS"
    assert result["blocks_sprint"] is False
    assert len(result["items"]) == 0


def test_fail_unregistered_directory(fake_repo: Path):
    """FAIL when a directory exists on disk but not in registry."""
    (fake_repo / "mystery-folder").mkdir()
    result = validate_root_structure({}, fake_repo)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    unreg = [i for i in result["items"] if i["check"] == "unregistered_directory"]
    assert len(unreg) == 1
    assert "mystery-folder" in unreg[0]["message"]


def test_warn_missing_readme(fake_repo: Path):
    """WARN when readme_required=true but no README exists."""
    (fake_repo / "docs" / "README.md").unlink()
    result = validate_root_structure({}, fake_repo)
    assert result["result"] == "WARN"
    assert result["blocks_sprint"] is False
    missing = [i for i in result["items"] if i["check"] == "missing_readme"]
    assert len(missing) == 1
    assert "docs" in missing[0]["message"]


def test_fail_resurrected_deleted(fake_repo: Path):
    """FAIL when retention=DELETED but directory exists on disk."""
    (fake_repo / "old-stuff").mkdir()
    result = validate_root_structure({}, fake_repo)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    resurrected = [i for i in result["items"] if i["check"] == "resurrected_deleted"]
    assert len(resurrected) == 1
    assert "old-stuff" in resurrected[0]["message"]


def test_idempotent_second_run(fake_repo: Path):
    """Two consecutive runs produce identical results."""
    result1 = validate_root_structure({}, fake_repo)
    result2 = validate_root_structure({}, fake_repo)
    assert result1 == result2


def test_pass_on_real_repo():
    """Validator has no FAIL items on the actual format-factory repo.
    WARN items are expected from readme_floor_fail and registry_producer_integrity checks.
    The critical invariant is blocks_sprint=False and no FAIL-severity items.
    """
    repo = Path(__file__).resolve().parents[2]
    registry = repo / "registry" / "repository-root-folders.yaml"
    if not registry.exists():
        pytest.skip("Not running from format-factory repo")
    result = validate_root_structure({}, repo)
    fail_items = [i for i in result["items"] if i.get("severity") == "FAIL"]
    assert len(fail_items) == 0, f"Unexpected FAIL items: {fail_items}"
    assert result["blocks_sprint"] is False, f"Validator unexpectedly blocks sprint: {result['items']}"


def test_no_registry_returns_warn(tmp_path: Path):
    """WARN when registry file does not exist."""
    result = validate_root_structure({}, tmp_path)
    assert result["result"] == "WARN"
    assert "not found" in result["summary"]


# ---------- TC-RR-010: New unit tests for TC-RR-004/005/008 ----------

def test_format_coverage_gap_detected(tmp_path: Path):
    """TC-RR-004: FORMAT_COVERAGE_GAP WARN when src/python/csv/ exists but tests/python/csv/ is missing."""
    (tmp_path / "src" / "python" / "csv").mkdir(parents=True)
    findings = _check_source_test_parity(tmp_path)
    assert len(findings) == 1
    assert findings[0]["check"] == "format_coverage_gap"
    assert "csv" in findings[0]["message"]
    assert findings[0]["severity"] == "WARN"


def test_format_coverage_no_gap(tmp_path: Path):
    """TC-RR-004: No FORMAT_COVERAGE_GAP when src/python/csv/ and tests/python/csv/ both exist."""
    (tmp_path / "src" / "python" / "csv").mkdir(parents=True)
    (tmp_path / "tests" / "python" / "csv").mkdir(parents=True)
    findings = _check_source_test_parity(tmp_path)
    assert len(findings) == 0


def test_readme_floor_fails_stub(tmp_path: Path):
    """TC-RR-005: Floor check fails for tiny README stub."""
    stub = tmp_path / "README.md"
    stub.write_text("# hi\n", encoding="utf-8")
    issues = _check_readme_content_floor(stub)
    assert "too_short" in issues


def test_readme_floor_passes_adequate(tmp_path: Path):
    """TC-RR-005: Floor check passes for README with purpose, producer, and command."""
    adequate = tmp_path / "README.md"
    adequate.write_text(
        "# Source\n\n"
        "This folder contains product source. Created by developers and spec-parity tools.\n\n"
        "## Purpose\n\nHolds format implementations.\n\n"
        "## Agent Navigation\n\nProducer: developers.\n"
        "Run: python .venv/Scripts/pytest tests/ -q to validate.\n"
        "Validation command: python tools/supervisor/governance_validators_root_struct.py\n",
        encoding="utf-8",
    )
    issues = _check_readme_content_floor(adequate)
    assert issues == []


def test_readme_floor_not_run_when_missing(fake_repo: Path):
    """TC-RR-005: Floor check not triggered when README is absent (only missing_readme fires)."""
    (fake_repo / "docs" / "README.md").unlink()
    result = validate_root_structure({}, fake_repo)
    floor_items = [i for i in result["items"] if i["check"] == "readme_floor_fail"]
    assert len(floor_items) == 0
    missing_items = [i for i in result["items"] if i["check"] == "missing_readme"]
    assert len(missing_items) == 1


def test_registry_producer_integrity_warns_on_fiction(tmp_path: Path):
    """TC-RR-008: WARN when all producers are non-verifiable strings."""
    entry = {
        "folder_path": "src/",
        "producers": ["developers", "humans"],
    }
    warn = _check_registry_producer_integrity(entry, tmp_path)
    assert warn is not None
    assert "non-verifiable" in warn


def test_registry_producer_integrity_passes_with_tool_path(tmp_path: Path):
    """TC-RR-008: No warning when at least one producer is a resolvable tool path."""
    tool_path = tmp_path / "tools" / "supervisor" / "some_tool.py"
    tool_path.parent.mkdir(parents=True)
    tool_path.write_text("# tool\n", encoding="utf-8")
    entry = {
        "folder_path": "src/",
        "producers": ["tools/supervisor/some_tool.py"],
    }
    warn = _check_registry_producer_integrity(entry, tmp_path)
    assert warn is None
