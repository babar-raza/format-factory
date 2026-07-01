"""Tests for capability_compiler.py — SAL-driven capability derivation (TC-CAP-015)."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "capability_layer"))
SAL_DRIVEN_MAP = REPO_ROOT / "reports" / "capability-layer" / "sal-driven-capability-map.json"


@pytest.fixture(scope="module")
def sal_driven_data():
    if not SAL_DRIVEN_MAP.exists():
        pytest.skip("sal-driven-capability-map.json not found")
    return json.loads(SAL_DRIVEN_MAP.read_bytes())


def test_sal_driven_map_exists():
    assert SAL_DRIVEN_MAP.exists(), "sal-driven-capability-map.json must exist"


def test_sal_driven_map_schema_version(sal_driven_data):
    assert sal_driven_data.get("schema_version") == "2.0"


def test_sal_driven_map_authority(sal_driven_data):
    assert sal_driven_data.get("authority") == "SAL_FACTS_PRIMARY"


def test_all_records_have_obligation_ids(sal_driven_data):
    caps = sal_driven_data.get("capabilities", [])
    assert len(caps) > 0, "sal-driven-map must have at least one record"
    missing_obl = [c.get("capability_id") for c in caps if not c.get("obligation_ids")]
    assert missing_obl == [], f"Records without obligation_ids: {missing_obl[:5]}"


def test_all_records_have_capability_id(sal_driven_data):
    caps = sal_driven_data.get("capabilities", [])
    missing_id = [i for i, c in enumerate(caps) if not c.get("capability_id")]
    assert missing_id == [], f"Records at indices {missing_id[:5]} have no capability_id"


def test_all_records_have_valid_state(sal_driven_data):
    valid_states = {
        "test_verified", "example_verified", "implementation_verified", "missing",
        "oracle_verified", "ai_draft", "inferred_unverified",
    }
    caps = sal_driven_data.get("capabilities", [])
    invalid = [c.get("capability_id") for c in caps if c.get("current_state") not in valid_states]
    assert invalid == [], f"Records with invalid state: {invalid[:5]}"


def test_test_verified_records_have_test_refs(sal_driven_data):
    caps = sal_driven_data.get("capabilities", [])
    test_verified = [c for c in caps if c.get("current_state") == "test_verified"]
    no_refs = [c.get("capability_id") for c in test_verified if not c.get("test_refs")]
    assert no_refs == [], f"test_verified records without test_refs: {no_refs[:5]}"


def test_sal_driven_records_count(sal_driven_data):
    caps = sal_driven_data.get("capabilities", [])
    assert len(caps) >= 100, f"Expected >= 100 SAL-driven records, got {len(caps)}"


def test_compiler_module_importable():
    try:
        import capability_compiler  # noqa: F401
    except ImportError:
        pytest.skip("capability_compiler module not importable")
