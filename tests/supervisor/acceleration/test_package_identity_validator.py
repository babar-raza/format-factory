"""Tests for validate_package_identity.py — Package Identity Validator."""

import json
import zipfile
from pathlib import Path

import pytest
import yaml

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from validate_package_identity import (
    validate_package_identity,
    validate_package_identity_from_declaration,
    _extract_sprint_from_text,
    _extract_stream_from_sprint,
)


# --- Unit tests for helpers ---

def test_extract_sprint_from_text_colon():
    text = "Sprint ID: FORMAT-FACTORY-ACCELERATION-R105-FOO-001\nOther stuff"
    assert _extract_sprint_from_text(text) == "FORMAT-FACTORY-ACCELERATION-R105-FOO-001"


def test_extract_sprint_from_text_run():
    text = "Run: acceleration-r105\nSprint: XYZ"
    assert _extract_sprint_from_text(text) == "acceleration-r105"


def test_extract_stream_from_sprint_acceleration():
    assert _extract_stream_from_sprint("FORMAT-FACTORY-ACCELERATION-R105-FOO") == "acceleration"


def test_extract_stream_from_sprint_mainstream():
    assert _extract_stream_from_sprint("FORMAT-FACTORY-MAINSTREAM-R106-BAR") == "mainstream"


def test_extract_stream_from_sprint_skills():
    assert _extract_stream_from_sprint("FORMAT-FACTORY-SKILLS-R103-BAZ") == "skills"


def test_extract_stream_from_sprint_supervisor():
    assert _extract_stream_from_sprint("FORMAT-FACTORY-SUPERVISOR-R103-QUX") == "supervisor"


def test_extract_stream_from_old_sprint():
    assert _extract_stream_from_sprint("FORMAT-FACTORY-R93-MEGA-TRAIN") == "mainstream"


# --- Integration tests with ZIPs ---

@pytest.fixture
def accel_zip(tmp_path):
    """Create a ZIP that correctly identifies as acceleration."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Declaration matches
        decl = {"run_id": "acceleration-r105", "sprint_id": "FORMAT-FACTORY-ACCELERATION-R105-FOO-001"}
        zf.writestr("evidence/evidence-declaration.yaml", yaml.dump(decl))

        # Supervisor files match acceleration
        zf.writestr("supervisor/latest-cycle-summary.md",
                     "Run: acceleration-r105\nSprint: FORMAT-FACTORY-ACCELERATION-R105-FOO-001\n")
        zf.writestr("supervisor/evidence-review.md",
                     "Sprint ID: FORMAT-FACTORY-ACCELERATION-R105-FOO-001\nVerdict: ACCEPTED\n")
        zf.writestr("supervisor/contradictions.md",
                     "Sprint ID: FORMAT-FACTORY-ACCELERATION-R105-FOO-001\nOverall: CLEAN\n")

        # Context pack matches
        cp = {"latest_sprint": {"sprint_id": "FORMAT-FACTORY-ACCELERATION-R105-FOO-001"}}
        zf.writestr("state/context-pack.yaml", yaml.dump(cp))

        # Gaps match
        gaps = {"sprint_id": "FORMAT-FACTORY-ACCELERATION-R105-FOO-001"}
        zf.writestr("state/selected-product-gaps.json", json.dumps(gaps))
    return zip_path


@pytest.fixture
def contaminated_zip(tmp_path):
    """Create a ZIP where global state points to mainstream, not acceleration."""
    zip_path = tmp_path / "contaminated.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        decl = {"run_id": "acceleration-r104", "sprint_id": "FORMAT-FACTORY-ACCELERATION-R104-FOO-001"}
        zf.writestr("evidence/evidence-declaration.yaml", yaml.dump(decl))

        # WRONG: points to mainstream
        zf.writestr("supervisor/latest-cycle-summary.md",
                     "Run: mainstream-r106\nSprint: FORMAT-FACTORY-MAINSTREAM-R106-BAR-001\n")
        zf.writestr("supervisor/evidence-review.md",
                     "Sprint ID: FORMAT-FACTORY-MAINSTREAM-R106-BAR-001\n")
        zf.writestr("supervisor/contradictions.md",
                     "Sprint ID: FORMAT-FACTORY-MAINSTREAM-R106-BAR-001\n")

        # WRONG: context pack points to skills
        cp = {"latest_sprint": {"sprint_id": "FORMAT-FACTORY-SKILLS-R103-QUX-001"}}
        zf.writestr("state/context-pack.yaml", yaml.dump(cp))

        # STALE: gaps from old sprint
        gaps = {"sprint_id": "R98-OLD"}
        zf.writestr("state/selected-product-gaps.json", json.dumps(gaps))
    return zip_path


def test_clean_package_passes(accel_zip):
    result = validate_package_identity(
        accel_zip,
        expected_run_id="acceleration-r105",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R105-FOO-001",
        expected_stream="acceleration",
    )
    assert result["valid"] is True
    assert result["violations"] == 0
    assert result["matches"] > 0


def test_contaminated_package_fails(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    assert result["valid"] is False
    assert result["violations"] >= 3  # cycle summary, evidence-review, contradictions


def test_wrong_stream_latest_cycle_detected(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    cycle_checks = [c for c in result["checks"]
                    if c["file"] == "supervisor/latest-cycle-summary.md"]
    assert len(cycle_checks) == 1
    assert cycle_checks[0]["status"] == "WRONG_STREAM"
    assert cycle_checks[0]["detected_stream"] == "mainstream"


def test_wrong_stream_evidence_review_detected(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    review_checks = [c for c in result["checks"]
                     if c["file"] == "supervisor/evidence-review.md"]
    assert len(review_checks) == 1
    assert review_checks[0]["status"] == "WRONG_STREAM"


def test_wrong_stream_contradictions_detected(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    contra_checks = [c for c in result["checks"]
                     if c["file"] == "supervisor/contradictions.md"]
    assert len(contra_checks) == 1
    assert contra_checks[0]["status"] == "WRONG_STREAM"


def test_stale_gaps_detected(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    gap_checks = [c for c in result["checks"]
                  if c["file"] == "state/selected-product-gaps.json"]
    assert len(gap_checks) == 1
    assert gap_checks[0]["status"] == "STALE"


def test_wrong_stream_context_pack_detected(contaminated_zip):
    result = validate_package_identity(
        contaminated_zip,
        expected_run_id="acceleration-r104",
        expected_sprint_id="FORMAT-FACTORY-ACCELERATION-R104-FOO-001",
        expected_stream="acceleration",
    )
    cp_checks = [c for c in result["checks"]
                 if c["file"] == "state/context-pack.yaml"]
    assert len(cp_checks) == 1
    assert cp_checks[0]["status"] == "WRONG_STREAM"
    assert cp_checks[0]["detected_stream"] == "skills"


def test_validate_from_declaration(accel_zip):
    decl = {
        "run_id": "acceleration-r105",
        "sprint_id": "FORMAT-FACTORY-ACCELERATION-R105-FOO-001",
    }
    result = validate_package_identity_from_declaration(accel_zip, decl)
    assert result["valid"] is True


def test_missing_zip():
    result = validate_package_identity(
        Path("/nonexistent.zip"),
        "foo", "bar", "acceleration",
    )
    assert result["valid"] is False
    assert "error" in result
