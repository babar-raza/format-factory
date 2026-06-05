"""
R101 — Replay Tests for Review Packages
Verifies that review packages from 4 streams can be loaded and
the stream can be correctly detected from their sprint_id.

Packages tested:
  - supervisor-r100
  - acceleration-r101
  - mainstream-r103
  - skills-r100
"""
import json
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_supervisor_packet import detect_stream_from_sprint_id

REVIEW_BASE = REPO_ROOT / ".local" / "supervisor" / "reviews"

PACKAGES = {
    "supervisor-r100": "supervisor",
    "acceleration-r101": "acceleration",
    "mainstream-r103": "mainstream",
    "skills-r100": "skills",
}


def _get_package_path(run_id: str) -> Path:
    return REVIEW_BASE / run_id / "declaration-review-package.zip"


def _load_declaration_from_zip(zip_path: Path) -> dict:
    """Extract evidence-declaration.yaml from a review package ZIP."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        decl_names = [n for n in names if n.endswith("evidence-declaration.yaml")]
        if not decl_names:
            return {}
        with zf.open(decl_names[0]) as f:
            return yaml.safe_load(f.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Package existence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_review_package_exists(run_id):
    path = _get_package_path(run_id)
    assert path.exists(), f"Review package not found: {path}"


# ---------------------------------------------------------------------------
# Stream detection from package sprint_id
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id,expected_stream", list(PACKAGES.items()))
def test_stream_detected_from_package(run_id, expected_stream):
    path = _get_package_path(run_id)
    if not path.exists():
        pytest.skip(f"Package not found: {path}")
    decl = _load_declaration_from_zip(path)
    if not decl:
        pytest.skip(f"No declaration in {path}")
    sprint_id = decl.get("sprint_id", "")
    detected = detect_stream_from_sprint_id(sprint_id)
    assert detected == expected_stream, \
        f"Sprint {sprint_id} detected as {detected}, expected {expected_stream}"


# ---------------------------------------------------------------------------
# Package contents self-containment
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_package_contains_declaration(run_id):
    path = _get_package_path(run_id)
    if not path.exists():
        pytest.skip(f"Package not found: {path}")
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        has_decl = any("evidence-declaration.yaml" in n for n in names)
        assert has_decl, f"Package {run_id} missing evidence-declaration.yaml"


@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_package_contains_grades(run_id):
    path = _get_package_path(run_id)
    if not path.exists():
        pytest.skip(f"Package not found: {path}")
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        has_grades = any("item-grades" in n for n in names)
        assert has_grades, f"Package {run_id} missing item-grades"


@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_package_contains_manifest(run_id):
    path = _get_package_path(run_id)
    if not path.exists():
        pytest.skip(f"Package not found: {path}")
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        has_manifest = any("supervisor-cycle-manifest" in n or "cycle-manifest" in n for n in names)
        # Manifest is expected but not all packages may have it
        if not has_manifest:
            pytest.skip(f"Package {run_id} has no cycle manifest (older format)")


# ---------------------------------------------------------------------------
# Replay: grades from package match expectations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_replay_grades_from_package(run_id):
    """Load grades from package and verify all are valid grade enums."""
    path = _get_package_path(run_id)
    if not path.exists():
        pytest.skip(f"Package not found: {path}")
    valid_grades = {
        "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED",
        "ACCEPTED_WITH_WARNINGS", "REWORK_REQUIRED", "REJECTED",
        "BLOCKED_EXTERNAL_GATE", "NOT_ATTEMPTED", "NOT_IN_SCOPE",
        "OVERCLAIMED", "INSUFFICIENT_EVIDENCE", "DEFERRED_WITH_REASON",
    }
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        grade_files = [n for n in names if "item-grades" in n and n.endswith((".json", ".yaml"))]
        if not grade_files:
            pytest.skip(f"No grade file in {run_id}")
        for gf in grade_files:
            with zf.open(gf) as f:
                content = f.read().decode("utf-8")
                if gf.endswith(".json"):
                    data = json.loads(content)
                else:
                    data = yaml.safe_load(content)
                if isinstance(data, list):
                    grades_list = data
                elif isinstance(data, dict) and "grades" in data:
                    grades_list = data["grades"]
                else:
                    continue
                for g in grades_list:
                    if isinstance(g, dict) and "supervisor_grade" in g:
                        assert g["supervisor_grade"] in valid_grades, \
                            f"Invalid grade {g['supervisor_grade']} in {run_id}/{gf}"
