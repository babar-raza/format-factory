"""Tests for tools/supervisor/plan_importer.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/ is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.supervisor.plan_importer import (
    ImportResult,
    ValidationResult,
    RegistrationResult,
    import_plan,
    validate_plan,
    register_plan,
    _sha256,
    _extract_taskcard_ids,
    _extract_mission_id,
    _extract_plan_id,
)


SAMPLE_PLAN = """\
# Test Plan

## plan_id: TEST-PLAN-001
## Mission ID: MISSION-TEST-001
## plan_type: machinery_hardening

| TC-ID | Status |
|-------|--------|
| TC-TEST-001 | OPEN |
| TC-TEST-002 | CLOSED |
"""

SAMPLE_PLAN_NO_MISSION = """\
# Test Plan No Mission

## plan_id: TEST-PLAN-002
## plan_type: test

| TC-ID | Status |
|-------|--------|
| TC-NM-001 | OPEN |
"""


# ── Unit tests for helpers ────────────────────────────────────────────────────

def test_extract_taskcard_ids_from_table():
    ids = _extract_taskcard_ids(SAMPLE_PLAN)
    assert 'TC-TEST-001' in ids
    assert 'TC-TEST-002' in ids
    assert len(ids) == 2


def test_extract_mission_id():
    mid = _extract_mission_id(SAMPLE_PLAN)
    assert mid == 'MISSION-TEST-001'


def test_extract_plan_id():
    pid = _extract_plan_id(SAMPLE_PLAN)
    assert pid == 'TEST-PLAN-001'


def test_extract_taskcard_ids_heading_format():
    text = "### TC-HEAD-001 | Title | OPEN\n\nsome body\n\n### TC-HEAD-002 | Other | CLOSED\n"
    ids = _extract_taskcard_ids(text)
    assert 'TC-HEAD-001' in ids
    assert 'TC-HEAD-002' in ids


# ── import_plan tests ─────────────────────────────────────────────────────────

def test_import_plan_source_not_found():
    result = import_plan('/nonexistent/path/plan.md')
    assert result.success is False
    assert result.status == 'ERROR'
    assert 'not found' in result.message.lower() or 'Source not found' in result.message


def _patch_pi(pi, tmp_path):
    """Return (orig_reg, orig_plans, orig_root) after patching module globals."""
    registry_dir = tmp_path / '.local' / 'supervisor'
    registry_dir.mkdir(parents=True, exist_ok=True)
    plans_dir = tmp_path / 'plans' / '.claude'
    plans_dir.mkdir(parents=True, exist_ok=True)

    orig = (pi.REGISTRY_PATH, pi.PLANS_DIR, pi.REPO_ROOT)
    pi.REGISTRY_PATH = registry_dir / 'plan-registry.json'
    pi.PLANS_DIR = plans_dir
    pi.REPO_ROOT = tmp_path
    return orig


def _restore_pi(pi, orig):
    pi.REGISTRY_PATH, pi.PLANS_DIR, pi.REPO_ROOT = orig


def test_import_plan_idempotency(tmp_path):
    """Second import of identical file must return ALREADY_REGISTERED, not overwrite."""
    import tools.supervisor.plan_importer as pi
    orig = _patch_pi(pi, tmp_path)
    try:
        src = tmp_path / 'test-plan.md'
        src.write_text(SAMPLE_PLAN, encoding='utf-8')

        r1 = import_plan(src)
        assert r1.success is True
        assert r1.status == 'IMPORTED'
        assert r1.taskcard_count == 2

        r2 = import_plan(src)
        assert r2.success is True
        assert r2.status == 'ALREADY_REGISTERED'
    finally:
        _restore_pi(pi, orig)


def test_import_plan_mission_conflict(tmp_path):
    """Second plan with same mission_id and different content must be rejected."""
    import tools.supervisor.plan_importer as pi
    orig = _patch_pi(pi, tmp_path)
    try:
        src_a = tmp_path / 'plan-a.md'
        src_a.write_text(SAMPLE_PLAN, encoding='utf-8')
        r1 = import_plan(src_a)
        assert r1.success is True

        # Different content, same mission_id
        src_b = tmp_path / 'plan-b.md'
        src_b.write_text(SAMPLE_PLAN + '\n## Extra content to change hash\n', encoding='utf-8')
        r2 = import_plan(src_b)
        assert r2.success is False
        assert r2.status == 'SKIPPED_CONFLICT'
        assert 'MISSION-TEST-001' in r2.message or 'already ACTIVE' in r2.message
    finally:
        _restore_pi(pi, orig)


def test_import_plan_force_overrides_conflict(tmp_path):
    """--force must override mission conflict."""
    import tools.supervisor.plan_importer as pi
    orig = _patch_pi(pi, tmp_path)
    try:
        src_a = tmp_path / 'plan-a.md'
        src_a.write_text(SAMPLE_PLAN, encoding='utf-8')
        import_plan(src_a)

        src_b = tmp_path / 'plan-b.md'
        src_b.write_text(SAMPLE_PLAN + '\n## Extra\n', encoding='utf-8')
        r2 = import_plan(src_b, force=True)
        assert r2.success is True
    finally:
        _restore_pi(pi, orig)


# ── validate_plan tests ───────────────────────────────────────────────────────

def test_validate_plan_missing_file():
    result = validate_plan('/nonexistent/plan.md')
    assert result.valid is False
    assert any('not found' in e.lower() or 'File not found' in e for e in result.errors)


def test_validate_plan_valid(tmp_path):
    p = tmp_path / 'plan.md'
    p.write_text(SAMPLE_PLAN, encoding='utf-8')
    result = validate_plan(p)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validate_plan_warns_missing_mission(tmp_path):
    p = tmp_path / 'plan.md'
    p.write_text(SAMPLE_PLAN_NO_MISSION, encoding='utf-8')
    result = validate_plan(p)
    assert result.valid is True  # warnings don't fail validation
    assert any('mission_id' in w for w in result.warnings)


def test_validate_plan_warns_no_taskcards(tmp_path):
    p = tmp_path / 'empty-plan.md'
    p.write_text('# Empty Plan\n## plan_id: EMPTY-001\n## Mission ID: EMPTY-MISSION\n', encoding='utf-8')
    result = validate_plan(p)
    assert any('TC-' in w or 'taskcard' in w.lower() for w in result.warnings)


# ── register_plan tests ───────────────────────────────────────────────────────

def test_register_plan_missing_file():
    result = register_plan('/nonexistent/plan.md')
    assert result.success is False
    assert 'not found' in result.message.lower() or 'Plan not found' in result.message


def test_register_plan_success(tmp_path):
    import tools.supervisor.plan_importer as pi
    orig = _patch_pi(pi, tmp_path)
    try:
        p = tmp_path / 'plan.md'
        p.write_text(SAMPLE_PLAN, encoding='utf-8')

        result = register_plan(p)
        assert result.success is True
        assert 'TEST-PLAN-001' in result.message or 'MISSION-TEST-001' in result.message

        reg = json.loads(pi.REGISTRY_PATH.read_text())
        assert len(reg['plans']) == 1
        plan_rec = next(iter(reg['plans'].values()))
        assert plan_rec['taskcard_count'] == 2
    finally:
        _restore_pi(pi, orig)
