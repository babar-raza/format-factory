"""Tests for validator shadow registry system (TC-TEST-001-01).

8 focused tests covering shadow registry round-trip, routing, isolation,
and promotion lifecycle.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO_ROOT / "tools"))

import governance_validator_runner as gvr
sys.path.insert(0, str(_REPO_ROOT / "tools" / "canary"))
import validator_promotion


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_registry(tmp_path):
    """Create a temp shadow registry YAML with empty entries list."""
    reg = tmp_path / "validator-shadow-registry.yaml"
    reg.write_text("validator_shadow_entries: []\n", encoding="utf-8")
    return reg


@pytest.fixture
def tmp_registry_with_entry(tmp_path):
    """Create a temp shadow registry YAML with one validator entry."""
    reg = tmp_path / "validator-shadow-registry.yaml"
    content = yaml.dump({
        "validator_shadow_entries": [
            {
                "validator_id": "validate_something",
                "mode": "shadow",
                "format_scope": ["*"],
                "shadow_promotion_threshold": 10,
                "notes": "test entry",
            }
        ]
    })
    reg.write_text(content, encoding="utf-8")
    return reg


# ---------------------------------------------------------------------------
# Test 1: empty registry file loads as empty dict
# ---------------------------------------------------------------------------

def test_shadow_registry_loads_empty(tmp_registry, monkeypatch):
    """Empty registry file → _load_shadow_registry returns {}."""
    monkeypatch.setattr(gvr, "SHADOW_REGISTRY_PATH", tmp_registry)
    result = gvr._load_shadow_registry()
    assert result == {}


# ---------------------------------------------------------------------------
# Test 2: missing registry file is handled fail-safe
# ---------------------------------------------------------------------------

def test_shadow_registry_missing_file(tmp_path, monkeypatch):
    """Non-existent registry path → _load_shadow_registry returns {} (fail-safe)."""
    missing = tmp_path / "does-not-exist.yaml"
    monkeypatch.setattr(gvr, "SHADOW_REGISTRY_PATH", missing)
    result = gvr._load_shadow_registry()
    assert result == {}


# ---------------------------------------------------------------------------
# Test 3: registry with one entry loads correctly
# ---------------------------------------------------------------------------

def test_shadow_registry_loads_entry(tmp_registry_with_entry, monkeypatch):
    """Registry with one entry → dict has one key with correct validator_id."""
    monkeypatch.setattr(gvr, "SHADOW_REGISTRY_PATH", tmp_registry_with_entry)
    result = gvr._load_shadow_registry()
    assert len(result) == 1
    assert "validate_something" in result
    assert result["validate_something"]["mode"] == "shadow"


# ---------------------------------------------------------------------------
# Test 4: shadow routing neutralizes blocks_sprint on FAIL result
# ---------------------------------------------------------------------------

def test_shadow_routing_neutralizes_blocks_sprint(tmp_path, monkeypatch):
    """Production _apply_shadow_routing: FAIL for registered validator has blocks_sprint neutralized."""
    monkeypatch.setattr(gvr, "SHADOW_LOG_PATH", tmp_path / "shadow-log.jsonl")

    result = {
        "validator": "validate_something",
        "validator_id": "validate_something",
        "result": "FAIL",
        "blocks_sprint": True,
        "items": [],
    }
    results = [result]
    shadow_registry = {
        "validate_something": {"validator_id": "validate_something", "mode": "shadow"}
    }

    suppressions = gvr._apply_shadow_routing(results, shadow_registry)

    assert result["blocks_sprint"] is False
    assert len(suppressions) == 1
    assert suppressions[0]["would_have_blocked"] is True
    assert suppressions[0]["validator_id"] == "validate_something"


# ---------------------------------------------------------------------------
# Test 5: PASS result with registry entry is preserved untouched
# ---------------------------------------------------------------------------

def test_shadow_routing_preserves_pass_result(tmp_path, monkeypatch):
    """Production _apply_shadow_routing: PASS results are never suppressed."""
    monkeypatch.setattr(gvr, "SHADOW_LOG_PATH", tmp_path / "shadow-log.jsonl")

    result = {
        "validator": "validate_something",
        "validator_id": "validate_something",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
    }
    results = [result]
    shadow_registry = {
        "validate_something": {"validator_id": "validate_something", "mode": "shadow"}
    }

    suppressions = gvr._apply_shadow_routing(results, shadow_registry)

    assert result["result"] == "PASS"
    assert result["blocks_sprint"] is False
    assert suppressions == []


# ---------------------------------------------------------------------------
# Test 6: validator NOT in registry still blocks on FAIL
# ---------------------------------------------------------------------------

def test_shadow_routing_non_shadow_validator_still_blocks(tmp_path, monkeypatch):
    """Production _apply_shadow_routing: non-shadow validator FAIL still has blocks_sprint=True."""
    monkeypatch.setattr(gvr, "SHADOW_LOG_PATH", tmp_path / "shadow-log.jsonl")

    result = {
        "validator": "validate_other",
        "validator_id": "validate_other",
        "result": "FAIL",
        "blocks_sprint": True,
        "items": [],
    }
    results = [result]
    shadow_registry = {
        "validate_something_else": {"validator_id": "validate_something_else", "mode": "shadow"}
    }

    suppressions = gvr._apply_shadow_routing(results, shadow_registry)

    assert result["blocks_sprint"] is True
    assert suppressions == []


# ---------------------------------------------------------------------------
# Test 7: shadow log is written with correct fields
# ---------------------------------------------------------------------------

def test_shadow_log_written(tmp_path, monkeypatch):
    """When shadow suppression fires, _write_shadow_log_entry is called with correct fields."""
    log_path = tmp_path / "validator-shadow-log.jsonl"
    monkeypatch.setattr(gvr, "SHADOW_LOG_PATH", log_path)

    entry = {
        "validator_id": "validate_test",
        "result": "FAIL",
        "would_have_blocked": True,
        "finding_count": 2,
        "mode": "shadow",
    }
    gvr._write_shadow_log_entry(entry)

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["validator_id"] == "validate_test"
    assert parsed["would_have_blocked"] is True
    assert parsed["finding_count"] == 2
    assert parsed["mode"] == "shadow"
    assert "ts" in parsed


# ---------------------------------------------------------------------------
# Test 8: promote command changes mode in YAML
# ---------------------------------------------------------------------------

def test_promote_command_changes_mode(tmp_path, monkeypatch):
    """validator_promotion.py promote changes mode to 'blocking' in registry file."""
    reg = tmp_path / "validator-shadow-registry.yaml"
    content = yaml.dump({
        "validator_shadow_entries": [
            {
                "validator_id": "validate_something",
                "mode": "shadow",
                "format_scope": ["*"],
                "shadow_promotion_threshold": 5,
            }
        ]
    })
    reg.write_text(content, encoding="utf-8")

    monkeypatch.setattr(validator_promotion, "REGISTRY_PATH", reg)

    args = MagicMock()
    args.validator = "validate_something"
    ret = validator_promotion.cmd_promote(args)

    assert ret == 0
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    entry = next(e for e in data["validator_shadow_entries"] if e["validator_id"] == "validate_something")
    assert entry["mode"] == "blocking"
    assert "promoted_at" in entry
