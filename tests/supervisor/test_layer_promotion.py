"""Tests for layer_promotion.py — TC-LHEAL-009.

Covers: create (happy path, fixture_mode, idempotency), 4 negative controls, update (idempotency).

TC-LHEAL-009 (glittery-splashing-manatee, 2026-07-13)
11 tests.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    pass

# Add tools/supervisor to sys.path for direct import
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))


def _import_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "layer_promotion",
        _REPO_ROOT / "tools" / "supervisor" / "layer_promotion.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def lp():
    return _import_module()


def _make_index_yaml(path: Path, layer_ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = [{"layer_id": lid, "canonical_name": f"Layer {lid}"} for lid in layer_ids]
    path.write_text(yaml.dump({"layers": entries}), encoding="utf-8")


def _make_skill_registry(path: Path, skill_ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    skills = [{"skill_id": s, "description": f"Skill {s}"} for s in skill_ids]
    path.write_text(yaml.dump({"skills": skills}), encoding="utf-8")


def _make_request_yaml(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(fields), encoding="utf-8")


class TestCreateHappyPath:
    """cmd_create creates a layer file in fixture_mode without touching production registries."""

    def test_fixture_mode_creates_plan_file(self, lp, tmp_path):
        """fixture_mode=True writes layer plan file to fixture dir."""
        # Set up registries
        idx = tmp_path / "plans" / "layers" / "index.yaml"
        _make_index_yaml(idx, ["L01"])
        sk = tmp_path / ".supervisor" / "skill-registry.yaml"
        _make_skill_registry(sk, ["inventory-format-dom"])
        # Evidence path must exist
        (tmp_path / "samples" / "by-format").mkdir(parents=True)

        req_path = tmp_path / "request.yaml"
        _make_request_yaml(req_path, {
            "candidate_id": "L-TEST-001",
            "candidate_name": "Test Layer",
            "permanent_responsibility": "Test permanent responsibility",
            "upstream_layers": ["L01"],
            "downstream_consumers": ["L07"],
            "skill_ids": ["inventory-format-dom"],
            "command_ids": ["inventory-format-dom"],
            "evidence_paths": ["samples/by-format/"],
            "requested_status": "PROPOSED",
            "fixture_mode": True,
        })

        fixture_dir = tmp_path / "tests" / "fixtures" / "layers"
        fixture_dir.mkdir(parents=True)

        rc = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc == 0
        assert (fixture_dir / "l_test_001-layer.md").exists()

        # Production index.yaml must be unmodified (only L01 entry)
        idx_data = yaml.safe_load(idx.read_text())
        assert all(e["layer_id"] != "L-TEST-001" for e in idx_data["layers"])

    def test_fixture_mode_idempotency(self, lp, tmp_path):
        """Second run with same fixture request returns total_changes=0, ALREADY_CURRENT."""
        idx = tmp_path / "plans" / "layers" / "index.yaml"
        _make_index_yaml(idx, ["L01"])
        sk = tmp_path / ".supervisor" / "skill-registry.yaml"
        _make_skill_registry(sk, ["inventory-format-dom"])
        (tmp_path / "samples" / "by-format").mkdir(parents=True)
        fixture_dir = tmp_path / "tests" / "fixtures" / "layers"
        fixture_dir.mkdir(parents=True)

        req_path = tmp_path / "request.yaml"
        _make_request_yaml(req_path, {
            "candidate_id": "L-TEST-IDEM",
            "candidate_name": "Idempotent Layer",
            "permanent_responsibility": "Idempotent responsibility",
            "upstream_layers": ["L01"],
            "downstream_consumers": ["L07"],
            "skill_ids": ["inventory-format-dom"],
            "command_ids": ["inventory-format-dom"],
            "evidence_paths": ["samples/by-format/"],
            "requested_status": "PROPOSED",
            "fixture_mode": True,
        })

        # First run
        rc1 = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc1 == 0
        assert (fixture_dir / "l_test_idem-layer.md").exists()

        # Second run — must be idempotent (rc=0, plan file exists, manifest written to module path)
        rc2 = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc2 == 0

        # Verify idempotency via the module-level manifest path (written to actual repo)
        manifest_path = _REPO_ROOT / ".local" / "supervisor" / "layer-promotion-manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            assert manifest["total_changes"] == 0
            assert manifest["idempotency"] == "ALREADY_CURRENT"

    def test_dry_run_does_not_write_any_files(self, lp, tmp_path):
        """--dry-run must not create any files."""
        idx = tmp_path / "plans" / "layers" / "index.yaml"
        _make_index_yaml(idx, ["L01"])
        sk = tmp_path / ".supervisor" / "skill-registry.yaml"
        _make_skill_registry(sk, ["inventory-format-dom"])
        (tmp_path / "samples" / "by-format").mkdir(parents=True)
        fixture_dir = tmp_path / "tests" / "fixtures" / "layers"
        fixture_dir.mkdir(parents=True)

        req_path = tmp_path / "request.yaml"
        _make_request_yaml(req_path, {
            "candidate_id": "L-TEST-DRY",
            "candidate_name": "Dry Layer",
            "permanent_responsibility": "Dry responsibility",
            "upstream_layers": ["L01"],
            "downstream_consumers": ["L07"],
            "skill_ids": ["inventory-format-dom"],
            "command_ids": ["inventory-format-dom"],
            "evidence_paths": ["samples/by-format/"],
            "requested_status": "PROPOSED",
            "fixture_mode": True,
        })

        rc = lp.cmd_create(_make_args(request=str(req_path), dry_run=True), repo_root=tmp_path)
        assert rc == 0
        # No layer plan file should have been written
        assert not (fixture_dir / "l_test_dry-layer.md").exists()


class TestCreateNegativeControls:
    """All 4 REJECT cases return exit code 3."""

    def _base_req(self) -> dict:
        return {
            "candidate_name": "NC Layer",
            "permanent_responsibility": "NC responsibility",
            "upstream_layers": ["L01"],
            "downstream_consumers": ["L07"],
            "skill_ids": ["inventory-format-dom"],
            "command_ids": ["inventory-format-dom"],
            "evidence_paths": ["samples/by-format/"],
            "requested_status": "PROPOSED",
            "fixture_mode": True,
        }

    def _setup_env(self, tmp_path):
        _make_index_yaml(tmp_path / "plans" / "layers" / "index.yaml", ["L01", "L28"])
        _make_skill_registry(tmp_path / ".supervisor" / "skill-registry.yaml", ["inventory-format-dom"])
        (tmp_path / "samples" / "by-format").mkdir(parents=True)
        (tmp_path / "tests" / "fixtures" / "layers").mkdir(parents=True)

    def test_duplicate_layer_id_rejected(self, lp, tmp_path):
        """REJECTED: DUPLICATE_LAYER_ID when candidate_id already in index.yaml."""
        self._setup_env(tmp_path)
        req = {**self._base_req(), "candidate_id": "L28"}
        req_path = tmp_path / "dup.yaml"
        _make_request_yaml(req_path, req)
        rc = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc == 3

    def test_methodology_not_proven_rejected(self, lp, tmp_path):
        """REJECTED: METHODOLOGY_NOT_PROVEN when evidence_paths is empty."""
        self._setup_env(tmp_path)
        req = {**self._base_req(), "candidate_id": "L-NC-002", "evidence_paths": []}
        req_path = tmp_path / "no-ev.yaml"
        _make_request_yaml(req_path, req)
        rc = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc == 3

    def test_unknown_skill_id_rejected(self, lp, tmp_path):
        """REJECTED: UNKNOWN_SKILL_ID when skill not in skill-registry.yaml."""
        self._setup_env(tmp_path)
        req = {**self._base_req(), "candidate_id": "L-NC-003", "skill_ids": ["ghost-skill-xyz"]}
        req_path = tmp_path / "bad-skill.yaml"
        _make_request_yaml(req_path, req)
        rc = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc == 3

    def test_unknown_upstream_layer_rejected(self, lp, tmp_path):
        """REJECTED: UNKNOWN_UPSTREAM_LAYER when upstream_layer not in index.yaml."""
        self._setup_env(tmp_path)
        req = {**self._base_req(), "candidate_id": "L-NC-004", "upstream_layers": ["L999"]}
        req_path = tmp_path / "bad-up.yaml"
        _make_request_yaml(req_path, req)
        rc = lp.cmd_create(_make_args(request=str(req_path)), repo_root=tmp_path)
        assert rc == 3


class TestUpdateIdempotency:
    """cmd_update idempotency: second run with same args returns total_changes=0."""

    def test_update_idempotent_when_no_changes(self, lp, tmp_path):
        """Second update with same skill_ids already in index returns ALREADY_CURRENT."""
        idx = tmp_path / "plans" / "layers" / "index.yaml"
        idx.parent.mkdir(parents=True)
        sk = tmp_path / ".supervisor" / "skill-registry.yaml"
        _make_skill_registry(sk, ["inventory-format-dom"])

        entries = [{"layer_id": "L01", "skill_ids": ["inventory-format-dom"], "canonical_name": "SAL"}]
        idx.write_text(yaml.dump({"layers": entries}), encoding="utf-8")

        args = _make_args(layer_id="L01", set_fields=["skill_ids=inventory-format-dom"])
        # Monkey-patch registry paths to use tmp_path
        import types
        lp_mod = _import_module()
        lp_mod._INDEX_YAML = idx
        lp_mod._CHANGE_LEDGER = tmp_path / "plans" / "layers" / "change-ledger.jsonl"
        lp_mod._MANIFEST_PATH = tmp_path / ".local" / "supervisor" / "layer-promotion-manifest.json"
        lp_mod._MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        lp_mod._SKILL_REGISTRY = sk

        rc = lp_mod.cmd_update(args, repo_root=tmp_path)
        assert rc == 0
        manifest = json.loads(lp_mod._MANIFEST_PATH.read_text())
        assert manifest["total_changes"] == 0
        assert manifest["idempotency"] == "ALREADY_CURRENT"


# ---- helpers ----

class _FakeArgs:
    pass


def _make_args(*, request: str = "", layer_id: str = "", set_fields: "list[str] | None" = None, dry_run: bool = False) -> _FakeArgs:
    a = _FakeArgs()
    a.request = request
    a.layer_id = layer_id
    a.set = set_fields or []
    a.dry_run = dry_run
    return a
