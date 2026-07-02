"""
test_jsonschema_engine.py — TC-VS-003 + TC-VS-004

Verifies that:
  TC-VS-003: The jsonschema engine enforces constraints that the structural fallback
             does not (additionalProperties, ID patterns, integer ranges, minLength, enums).
  TC-VS-004: Negative controls confirm the structural fallback IS permissive where the
             jsonschema engine IS strict — proving TC-VS-003 tests detect real gaps.

All jsonschema-engine tests are skipped when jsonschema is not installed (CI without venv).
"""
import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "playbook"))

from validate_playbook import (  # noqa: E402
    ENGINE_JSONSCHEMA,
    ENGINE_STRUCTURAL,
    JSONSCHEMA_AVAILABLE,
    validate,
)

_SCHEMA = str(_REPO / "schemas" / "playbook" / "acquisition-playbook.schema.json")
_ODF_FLAT = str(_REPO / "acquisition-packs" / "_families" / "odf-flat" / "playbook.yaml")
_FIXTURE_VALID = _REPO / "tests" / "playbook" / "fixtures" / "valid-acquisition-playbook.yaml"

_SKIP_NO_JSONSCHEMA = pytest.mark.skipif(
    not JSONSCHEMA_AVAILABLE,
    reason="jsonschema not installed — run with .venv/Scripts/pytest",
)


def _load_fixture() -> dict:
    """Return a deep copy of the valid fixture playbook dict."""
    return copy.deepcopy(yaml.safe_load(_FIXTURE_VALID.read_text(encoding="utf-8")))


def _write_playbook(tmp_path: Path, data: dict) -> str:
    """Write a playbook dict to a temp YAML file, return its path string."""
    p = tmp_path / "test_playbook.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# TC-VS-003: jsonschema engine enforces schema constraints
# ---------------------------------------------------------------------------


@_SKIP_NO_JSONSCHEMA
def test_odf_flat_passes_jsonschema_engine():
    """Pilot 4 upgrade — odf-flat passes full JSON Schema validation (not just structural)."""
    passed, errors, info = validate(_SCHEMA, _ODF_FLAT, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert passed, f"Expected PASS, got errors: {errors}"
    assert info.get("json_schema_engine") == ENGINE_JSONSCHEMA, (
        f"Expected engine=jsonschema, got {info.get('json_schema_engine')}"
    )


@_SKIP_NO_JSONSCHEMA
def test_playbook_id_pattern_rejected_by_jsonschema(tmp_path):
    """playbook_id 'INVALID_UPPER' violates pattern ^[a-z0-9][a-z0-9-]*[a-z0-9]$ — jsonschema rejects it."""
    data = _load_fixture()
    data["playbook_id"] = "INVALID_UPPER"
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert not passed, "Expected FAIL for invalid playbook_id pattern under jsonschema engine"
    assert errors, "Expected at least one error message"


@_SKIP_NO_JSONSCHEMA
def test_unknown_top_level_field_rejected_by_jsonschema(tmp_path):
    """Extra field 'unknown_field' violates additionalProperties: false — jsonschema rejects it."""
    data = _load_fixture()
    data["unknown_field"] = True
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert not passed, "Expected FAIL for unknown top-level field under jsonschema engine"


@_SKIP_NO_JSONSCHEMA
def test_gate_number_out_of_range_rejected_by_jsonschema(tmp_path):
    """gate_number 0 violates minimum: 1 — jsonschema rejects it."""
    data = _load_fixture()
    data["gates"][0]["gate_number"] = 0
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert not passed, "Expected FAIL for gate_number=0 (below minimum: 1) under jsonschema engine"


@_SKIP_NO_JSONSCHEMA
def test_operation_title_too_short_rejected_by_jsonschema(tmp_path):
    """operation title 'X' (1 char) violates minLength: 5 — jsonschema rejects it."""
    data = _load_fixture()
    if not data.get("operations"):
        pytest.skip("No operations in fixture to mutate")
    data["operations"][0]["title"] = "X"
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert not passed, "Expected FAIL for operation title too short under jsonschema engine"


@_SKIP_NO_JSONSCHEMA
def test_invalid_artifact_type_rejected_by_jsonschema(tmp_path):
    """artifact_type 'not_a_real_type' violates enum — jsonschema rejects it."""
    data = _load_fixture()
    if not data.get("operations"):
        pytest.skip("No operations in fixture to mutate")
    op = data["operations"][0]
    if not op.get("evidence_requirements"):
        pytest.skip("No evidence_requirements in fixture operation to mutate")
    op["evidence_requirements"][0]["artifact_type"] = "not_a_real_type"
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_JSONSCHEMA)
    assert not passed, "Expected FAIL for invalid artifact_type enum under jsonschema engine"


# ---------------------------------------------------------------------------
# TC-VS-004: Negative controls — structural fallback is permissive
# ---------------------------------------------------------------------------


def test_extra_field_passes_structural(tmp_path):
    """Structural fallback does NOT enforce additionalProperties: false — extra fields pass silently."""
    data = _load_fixture()
    data["unknown_field"] = True
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_STRUCTURAL)
    assert passed, (
        f"Expected structural fallback to PASS with extra field (no additionalProperties check); "
        f"got errors: {errors}"
    )
    assert info.get("json_schema_engine") == ENGINE_STRUCTURAL


def test_invalid_id_passes_structural(tmp_path):
    """Structural fallback does NOT enforce playbook_id pattern — uppercase IDs pass silently."""
    data = _load_fixture()
    data["playbook_id"] = "INVALID_UPPER"
    path = _write_playbook(tmp_path, data)
    passed, errors, info = validate(_SCHEMA, path, kind="acquisition-playbook", engine=ENGINE_STRUCTURAL)
    assert passed, (
        f"Expected structural fallback to PASS with invalid playbook_id pattern; "
        f"got errors: {errors}"
    )
    assert info.get("json_schema_engine") == ENGINE_STRUCTURAL
