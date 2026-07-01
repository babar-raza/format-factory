"""Tests for capability-subjects.yaml — identity, grouped targets, aliases, duplicates (TC-CAP-015)."""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SUBJECTS_FILE = REPO_ROOT / "reports" / "capability-layer" / "capability-subjects.yaml"


@pytest.fixture(scope="module")
def subjects_data():
    if not SUBJECTS_FILE.exists():
        pytest.skip("capability-subjects.yaml not found")
    return yaml.safe_load(SUBJECTS_FILE.read_text(encoding="utf-8"))


def test_subjects_file_exists():
    assert SUBJECTS_FILE.exists()


def test_subjects_has_required_counters(subjects_data):
    counters = subjects_data.get("required_counters", {})
    assert counters.get("UNRESOLVED_PRODUCT_FORMAT_IDENTITIES") == 0
    assert counters.get("DUPLICATE_CAPABILITY_SUBJECTS") == 0


def test_no_duplicate_subject_ids(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    ids = [s.get("subject_id") for s in subjects]
    assert len(ids) == len(set(ids)), f"Duplicate subject_ids: {[i for i in ids if ids.count(i) > 1]}"


def test_netpbm_aggregation_rules(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    netpbm_dotnet = next((s for s in subjects if s.get("subject_id") == "netpbm:dotnet"), None)
    assert netpbm_dotnet is not None, "netpbm:dotnet subject must exist"
    agg = netpbm_dotnet.get("aggregate_children", [])
    assert set(agg) >= {"pbm", "pgm", "ppm"}, f"netpbm:dotnet must aggregate pbm+pgm+ppm, got: {agg}"


def test_excluded_formats_not_present_as_active(subjects_data):
    """Excluded formats (ora, pam, xpm, zpaq) must not appear as active subjects."""
    subjects = subjects_data.get("capability_subjects", [])
    active_ids = {s.get("subject_id") for s in subjects if s.get("active", True)}
    for fmt in ("ora", "pam", "xpm", "zpaq"):
        found = [sid for sid in active_ids if fmt in sid.lower()]
        assert found == [], f"Excluded format {fmt} found in active subjects: {found}"


def test_all_subjects_have_subject_id(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    missing = [i for i, s in enumerate(subjects) if not s.get("subject_id")]
    assert missing == [], f"Subjects at indices {missing} missing subject_id"


def test_all_subjects_have_format_id(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    missing = [s.get("subject_id") for s in subjects if not s.get("format_id")]
    assert missing == [], f"Subjects without format_id: {missing}"


def test_all_subjects_have_language(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    missing = [s.get("subject_id") for s in subjects if not s.get("language")]
    assert missing == [], f"Subjects without language: {missing}"


def test_all_subjects_have_track(subjects_data):
    subjects = subjects_data.get("capability_subjects", [])
    missing = [s.get("subject_id") for s in subjects if not s.get("track")]
    assert missing == [], f"Subjects without track: {missing}"
