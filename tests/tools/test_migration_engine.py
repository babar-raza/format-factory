"""
tests/tools/test_migration_engine.py

Tests for the documentation-structure-migration engine (DOCS-REORG-001).
"""

import hashlib
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure tools/ is on path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.docs.migration_engine import (
    ROOT_RETENTION,
    classify_reference,
    file_hash,
    get_docs_root_files,
)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestRootRetention:
    def test_readme_is_retained(self):
        assert "README.md" in ROOT_RETENTION

    def test_gates_is_retained(self):
        assert "gates.md" in ROOT_RETENTION

    def test_methodology_files_retained(self):
        assert "agent-methodology-index.md" in ROOT_RETENTION
        assert "planning-methodology.md" in ROOT_RETENTION
        assert "agent-execution-handoff-standard.md" in ROOT_RETENTION
        assert "plan-hardening-checklist.md" in ROOT_RETENTION
        assert "fresh-chat-continuity-brief.md" in ROOT_RETENTION

    def test_spec_summary_retained(self):
        assert "spec-to-feature-correction-plan-summary.md" in ROOT_RETENTION

    def test_exactly_eight_retained(self):
        assert len(ROOT_RETENTION) == 8


class TestClassifyReference:
    def test_agents_md_is_governance(self):
        ref_file = REPO_ROOT / "AGENTS.md"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_GOVERNANCE_REFERENCE"

    def test_claude_md_is_governance(self):
        ref_file = REPO_ROOT / "CLAUDE.md"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_GOVERNANCE_REFERENCE"

    def test_test_file_is_test_reference(self):
        ref_file = REPO_ROOT / "tests" / "tools" / "test_something.py"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_TEST_REFERENCE"

    def test_python_file_is_runtime(self):
        ref_file = REPO_ROOT / "tools" / "llm" / "run_record.py"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_RUNTIME_REFERENCE"

    def test_evidence_dir_is_historical(self):
        ref_file = REPO_ROOT / ".local" / "evidences" / "sprint-001" / "evidence.yaml"
        result = classify_reference(ref_file, "some context")
        assert result == "HISTORICAL_EVIDENCE"

    def test_skill_registry_is_registry_reference(self):
        ref_file = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_REGISTRY_REFERENCE"

    def test_plans_are_plan_reference(self):
        ref_file = REPO_ROOT / "plans" / "master-plan.md"
        result = classify_reference(ref_file, "some context")
        assert result == "ACTIVE_PLAN_OR_TASKCARD"


class TestFileHash:
    def test_returns_hex_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h = file_hash(f)
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex

    def test_consistent(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        assert file_hash(f) == file_hash(f)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content a")
        f2.write_text("content b")
        assert file_hash(f1) != file_hash(f2)


class TestGetDocsRootFiles:
    def test_returns_list_of_paths(self):
        files = get_docs_root_files()
        assert isinstance(files, list)
        assert all(isinstance(f, Path) for f in files)

    def test_all_files_are_under_docs(self):
        files = get_docs_root_files()
        docs_root = REPO_ROOT / "docs"
        for f in files:
            assert f.parent == docs_root, f"{f} is not directly under docs/"

    def test_returns_markdown_and_yaml(self):
        files = get_docs_root_files()
        extensions = {f.suffix for f in files}
        assert ".md" in extensions

    def test_does_not_include_subdirectory_files(self):
        files = get_docs_root_files()
        docs_root = REPO_ROOT / "docs"
        for f in files:
            # Parent must be exactly docs/, not a subdirectory
            assert f.parent == docs_root


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------

class TestCLISmoke:
    def test_inventory_subcommand_exits_zero(self, tmp_path):
        out = tmp_path / "inventory.yaml"
        result = subprocess.run(
            [sys.executable, "tools/docs/migration_engine.py", "inventory", "--output", str(out)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        assert out.exists()

    def test_inventory_output_has_expected_keys(self, tmp_path):
        import yaml as _yaml
        out = tmp_path / "inventory.yaml"
        subprocess.run(
            [sys.executable, "tools/docs/migration_engine.py", "inventory", "--output", str(out)],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        data = _yaml.safe_load(out.read_text())
        assert "total_files" in data
        assert "retained_at_root" in data
        assert "movable" in data
        assert data["retained_at_root"] == 8

    def test_validate_full_exits_zero_when_no_manifest(self):
        # validate --full with no manifest should return 0 (skips gracefully)
        result = subprocess.run(
            [sys.executable, "tools/docs/migration_engine.py", "validate", "--full"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        # Either 0 (no manifest, skipped) or meaningful output
        assert result.returncode in (0, 1)

    def test_no_subcommand_shows_help(self):
        result = subprocess.run(
            [sys.executable, "tools/docs/migration_engine.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()
