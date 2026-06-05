"""Tests for review package self-containment — R104 Wave 1."""

import json
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from build_declaration_review_package import build_package


def _make_declaration(tmp_path, evidence_root_name="reports/accel-test"):
    """Create a minimal declaration + evidence tree for testing."""
    evidence_dir = tmp_path / evidence_root_name
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "preflight.md").write_text("# Preflight\nOK")
    (evidence_dir / "raw-test-log.txt").write_text("10 passed")
    samples = evidence_dir / "sample-outputs"
    samples.mkdir()
    (samples / "gaps.json").write_text('{"gaps": []}')
    prompts = evidence_dir / "generated-stream-prompts"
    prompts.mkdir()
    (prompts / "next-accel-prompt.md").write_text("# Acceleration")
    (evidence_dir / "evidence-manifest.yaml").write_text("sprint_id: test")

    decl = {
        "run_id": "test-r104",
        "sprint_id": "TEST-R104",
        "evidence_root": evidence_root_name,
        "evidence_artifacts": [
            {"path": f"{evidence_root_name}/preflight.md", "type": "report"},
            {"path": f"{evidence_root_name}/raw-test-log.txt", "type": "raw_log"},
        ],
        "planned_work_items": [
            {
                "item_id": "W1",
                "evidence_paths": [
                    f"{evidence_root_name}/sample-outputs/gaps.json",
                    f"{evidence_root_name}/generated-stream-prompts/next-accel-prompt.md",
                ],
            },
        ],
        "reports_created": [f"{evidence_root_name}/preflight.md"],
    }
    decl_dir = tmp_path / ".local" / "evidences" / "test-r104"
    decl_dir.mkdir(parents=True)
    decl_path = decl_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl, default_flow_style=False), encoding="utf-8")

    # Create supervisor dirs the builder expects
    (tmp_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)
    (tmp_path / "product-capability-matrix").mkdir(parents=True, exist_ok=True)

    return decl_path


def test_package_includes_evidence_root_files(tmp_path):
    """Evidence root directory contents are packaged recursively."""
    decl_path = _make_declaration(tmp_path)
    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)
    zip_path = Path(result["zip_path"])

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        # Should contain sprint-evidence/ entries
        sprint_evidence = [n for n in names if n.startswith("sprint-evidence/")]
        assert len(sprint_evidence) >= 5, f"Expected 5+ sprint-evidence entries, got {len(sprint_evidence)}: {sprint_evidence}"


def test_package_includes_sample_outputs(tmp_path):
    """Sample outputs from subdirectories are included."""
    decl_path = _make_declaration(tmp_path)
    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)

    with zipfile.ZipFile(Path(result["zip_path"])) as zf:
        names = zf.namelist()
        gaps = [n for n in names if "gaps.json" in n]
        assert len(gaps) >= 1, f"gaps.json not found in ZIP: {names}"


def test_package_includes_generated_prompts(tmp_path):
    """Generated stream prompts are included."""
    decl_path = _make_declaration(tmp_path)
    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)

    with zipfile.ZipFile(Path(result["zip_path"])) as zf:
        names = zf.namelist()
        prompts = [n for n in names if "next-accel-prompt" in n]
        assert len(prompts) >= 1, f"next-accel-prompt not found in ZIP: {names}"


def test_package_includes_raw_log(tmp_path):
    """Raw test log is included."""
    decl_path = _make_declaration(tmp_path)
    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)

    with zipfile.ZipFile(Path(result["zip_path"])) as zf:
        names = zf.namelist()
        logs = [n for n in names if "raw-test-log" in n]
        assert len(logs) >= 1, f"raw-test-log not found in ZIP: {names}"


def test_package_includes_evidence_manifest(tmp_path):
    """Evidence manifest is included."""
    decl_path = _make_declaration(tmp_path)
    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)

    with zipfile.ZipFile(Path(result["zip_path"])) as zf:
        names = zf.namelist()
        manifests = [n for n in names if "evidence-manifest" in n]
        assert len(manifests) >= 1, f"evidence-manifest not found in ZIP: {names}"


def test_package_no_evidence_root_still_works(tmp_path):
    """Package builds without error when evidence_root is missing."""
    decl = {
        "run_id": "test-empty",
        "sprint_id": "TEST-EMPTY",
        "evidence_artifacts": [],
        "planned_work_items": [],
    }
    decl_dir = tmp_path / ".local" / "evidences" / "test-empty"
    decl_dir.mkdir(parents=True)
    decl_path = decl_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl, default_flow_style=False), encoding="utf-8")
    (tmp_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)
    (tmp_path / "product-capability-matrix").mkdir(parents=True, exist_ok=True)

    out_dir = tmp_path / "out"
    result = build_package(decl_path, tmp_path, out_dir)
    assert result["exit_code"] in (0, 2)  # builds, possibly with missing
