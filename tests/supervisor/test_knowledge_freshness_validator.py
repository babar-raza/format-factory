"""Tests for V68: knowledge_freshness_validator.py — WARN/PASS/SKIP scenarios.

TC-P2-001 (hidden-puzzling-rain Phase 2): regression tests for knowledge freshness
validator. Covers: PASS (fresh hashes), WARN (stale hash), SKIP (no registry).

Run with: .venv/Scripts/pytest tests/supervisor/test_knowledge_freshness_validator.py -v
"""
import hashlib
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from knowledge_freshness_validator import validate_knowledge_freshness  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_registry(tmp_path: Path, contracts: list) -> Path:
    registry = {
        "schema_version": "1.0",
        "registry_id": "test-registry",
        "contracts": contracts,
        "gaps_path": "gaps.yaml",
        "growth_events_path": "growth-events.yaml",
    }
    reg_path = tmp_path / ".supervisor" / "knowledge" / "registry.yaml"
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(yaml.dump(registry), encoding="utf-8")
    return tmp_path


def _make_contract(tmp_path: Path, cid: str, status: str, hashes: list) -> Path:
    contract = {
        "knowledge_id": cid,
        "status": status,
        "source_hashes": hashes,
    }
    cpath = tmp_path / ".supervisor" / "knowledge" / "contracts" / f"{cid.lower()}.yaml"
    cpath.parent.mkdir(parents=True, exist_ok=True)
    cpath.write_text(yaml.dump(contract), encoding="utf-8")
    return cpath


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# TC-P2-001 Test 1: PASS — VERIFIED_CURRENT contract with fresh hash
# ---------------------------------------------------------------------------

def test_pass_verified_current_fresh_hash(tmp_path):
    """V68 returns PASS when all VERIFIED_CURRENT source hashes match."""
    # Create a source file
    src = tmp_path / "src" / "python" / "csv" / "__init__.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    content = b"# canonical csv init\n"
    src.write_bytes(content)

    rel_path = "src/python/csv/__init__.py"
    hashes = [{"path": rel_path, "sha256": _sha256(content)}]

    cpath = _make_contract(tmp_path, "KC-PYTHON-001", "VERIFIED_CURRENT", hashes)
    contracts = [{
        "contract_id": "KC-PYTHON-001",
        "status": "VERIFIED_CURRENT",
        "path": str(cpath.relative_to(tmp_path)).replace("\\", "/"),
    }]
    root = _make_registry(tmp_path, contracts)

    result = validate_knowledge_freshness({}, root)

    assert result["result"] == "PASS", f"Expected PASS, got {result}"
    assert result["blocks_sprint"] is False
    assert "PASS" in result["summary"]


# ---------------------------------------------------------------------------
# TC-P2-001 Test 2: WARN — VERIFIED_CURRENT contract with stale hash
# ---------------------------------------------------------------------------

def test_warn_verified_current_stale_hash(tmp_path):
    """V68 returns WARN (non-blocking) when a source hash has diverged."""
    src = tmp_path / "src" / "python" / "csv" / "__init__.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    original_content = b"# original content\n"
    modified_content = b"# modified content -- this causes stale\n"
    src.write_bytes(modified_content)  # Write modified version

    rel_path = "src/python/csv/__init__.py"
    # Store hash of ORIGINAL content — file has MODIFIED content → STALE
    hashes = [{"path": rel_path, "sha256": _sha256(original_content)}]

    cpath = _make_contract(tmp_path, "KC-PYTHON-001", "VERIFIED_CURRENT", hashes)
    contracts = [{
        "contract_id": "KC-PYTHON-001",
        "status": "VERIFIED_CURRENT",
        "path": str(cpath.relative_to(tmp_path)).replace("\\", "/"),
    }]
    root = _make_registry(tmp_path, contracts)

    result = validate_knowledge_freshness({}, root)

    assert result["result"] == "WARN", f"Expected WARN, got {result}"
    assert result["blocks_sprint"] is False, "STALE must never block sprint (non-blocking)"
    assert any("STALE" in item for item in result["items"])
    assert "WARN" in result["summary"]


# ---------------------------------------------------------------------------
# TC-P2-001 Test 3: SKIP — DRAFT contract is silently ignored (PASS returned)
# ---------------------------------------------------------------------------

def test_skip_draft_contract_silent(tmp_path):
    """V68 silently skips DRAFT contracts and returns PASS (no noise)."""
    rel_path = "src/python/csv/__init__.py"
    hashes = [{"path": rel_path, "sha256": "deadbeef" * 8}]  # Invalid hash

    cpath = _make_contract(tmp_path, "KC-PYTHON-002", "DRAFT_PENDING_AUTHORITY", hashes)
    contracts = [{
        "contract_id": "KC-PYTHON-002",
        "status": "DRAFT_PENDING_AUTHORITY",
        "path": str(cpath.relative_to(tmp_path)).replace("\\", "/"),
    }]
    root = _make_registry(tmp_path, contracts)

    result = validate_knowledge_freshness({}, root)

    # DRAFT contracts must be silently skipped — result is PASS with 0 items checked
    assert result["result"] == "PASS", f"DRAFT contract must not trigger WARN/FAIL, got {result}"
    assert result["blocks_sprint"] is False
    # No STALE or MISSING_SOURCE items from the DRAFT contract
    stale_items = [i for i in result["items"] if "STALE" in i or "MISSING" in i]
    assert not stale_items, f"DRAFT contract generated noise: {stale_items}"


# ---------------------------------------------------------------------------
# TC-P2-001 Test 4: SKIP — No registry (graceful degradation)
# ---------------------------------------------------------------------------

def test_skip_no_registry(tmp_path):
    """V68 returns PASS when registry.yaml does not exist (graceful skip)."""
    # No registry created in tmp_path
    result = validate_knowledge_freshness({}, tmp_path)

    assert result["result"] == "PASS", f"Missing registry must not fail, got {result}"
    assert result["blocks_sprint"] is False
    assert "SKIPPED" in result["summary"] or "PASS" in result["summary"]


# ---------------------------------------------------------------------------
# TC-P2-001 Test 5: Integration — real repo registry exits cleanly
# ---------------------------------------------------------------------------

def test_integration_real_registry_passes():
    """V68 on the real repository returns PASS (all hashes fresh)."""
    result = validate_knowledge_freshness({}, _REPO)

    assert result["result"] == "PASS", (
        f"Real registry must be VERIFIED_CURRENT but got WARN: {result['items']}"
    )
    assert result["blocks_sprint"] is False
    assert "PASS" in result["summary"]
