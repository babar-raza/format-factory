"""Tests for V91 root structure validator (TC-ROOT-006)."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest
import yaml

# Ensure tools/supervisor is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

from governance_validators_root_struct import validate_root_structure  # noqa: E402


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

    # Create the registered directories
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "README.md").write_text("# Source\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
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


def test_warn_resurrected_deleted(fake_repo: Path):
    """WARN when retention=DELETED but directory exists on disk."""
    (fake_repo / "old-stuff").mkdir()
    result = validate_root_structure({}, fake_repo)
    assert result["result"] == "WARN"
    assert result["blocks_sprint"] is False
    resurrected = [i for i in result["items"] if i["check"] == "resurrected_deleted"]
    assert len(resurrected) == 1
    assert "old-stuff" in resurrected[0]["message"]


def test_idempotent_second_run(fake_repo: Path):
    """Two consecutive runs produce identical results."""
    result1 = validate_root_structure({}, fake_repo)
    result2 = validate_root_structure({}, fake_repo)
    assert result1 == result2


def test_pass_on_real_repo():
    """Validator returns PASS on the actual format-factory repo."""
    repo = Path(__file__).resolve().parents[2]
    registry = repo / "registry" / "repository-root-folders.yaml"
    if not registry.exists():
        pytest.skip("Not running from format-factory repo")
    result = validate_root_structure({}, repo)
    # Allow WARN-severity items (e.g. resurrected_deleted for state/ dir) — only fail on ERROR
    errors = [i for i in result["items"] if i.get("severity") == "ERROR"]
    assert len(errors) == 0, f"Unexpected ERROR items: {errors}"
    assert result["result"] in ("PASS", "WARN"), f"Unexpected result: {result['result']}, items: {result['items']}"


def test_no_registry_returns_warn(tmp_path: Path):
    """WARN when registry file does not exist."""
    result = validate_root_structure({}, tmp_path)
    assert result["result"] == "WARN"
    assert "not found" in result["summary"]
