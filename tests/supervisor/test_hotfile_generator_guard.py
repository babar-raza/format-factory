"""test_hotfile_generator_guard.py — SFC-GAP-B (2026-07-17).

Unit tests for the hot-governance-files output manifest and its GENERATOR_PATTERNS
wiring in gate.py. The real multi-thread contention proof lives in
tests/supervisor/pilots/run_coordination_pilot.py (pilot 16) — these tests cover
configuration correctness (manifest shape, pattern matching, drift detection),
not concurrency (already covered by the real-thread pilot).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from coordination.generator_guard import guarded_generation, load_manifest  # noqa: E402
from coordination.hooks.gate import GENERATOR_PATTERNS  # noqa: E402
from coordination import db as cdb  # noqa: E402

MANIFEST_PATH = _REPO / "tools" / "governance" / "hot-governance-files" / "output-manifest.yaml"

_HOT_FILES = [
    "docs/governance/skill-only-policy.yaml",
    ".supervisor/skill-registry.yaml",
    ".claude/commands/command-registry.yaml",
    ".supervisor/capability-routing-registry.yaml",
    "registry/found-issue-register.yaml",
    "registry/governance/validator-id-authority.yaml",
    "oracle/registry/format-oracle-registry.yaml",
    ".supervisor/skill-first-policy.md",
]


def test_manifest_exists_and_loads():
    assert MANIFEST_PATH.exists()
    manifest = load_manifest(MANIFEST_PATH)
    assert manifest["generator_id"] == "hot-governance-files"
    assert manifest["mode"] == "exclusive"


def test_manifest_covers_all_known_hot_files():
    manifest = load_manifest(MANIFEST_PATH)
    outputs = {o.replace("\\", "/") for o in manifest["outputs"]}
    for f in _HOT_FILES:
        assert f in outputs, f"{f} missing from hot-governance-files manifest"


@pytest.mark.parametrize("script_path", [
    "tools/supervisor/sync_skill_command_registry.py",
    "tools/supervisor/patch_registry_missing_fields.py",
    "tools/supervisor/build_capability_routes.py",
])
def test_generator_patterns_recognizes_hot_file_writers(script_path):
    matched = [gid for gid, pat in GENERATOR_PATTERNS if pat.search(script_path)]
    assert "hot-governance-files" in matched, (
        f"{script_path} should be recognized as a hot-governance-files writer"
    )


def test_generator_patterns_does_not_match_unrelated_script():
    matched = [gid for gid, pat in GENERATOR_PATTERNS
              if pat.search("tools/oracle/execute_oracle.py")]
    assert "hot-governance-files" not in matched


def test_guarded_generation_proceeds_when_uncontended(tmp_path):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / "out").mkdir(parents=True)
    (repo / ".git").mkdir()
    cdb.ensure_db(root)
    manifest = repo / "manifest.yaml"
    manifest.write_text(
        "generator_id: hot-governance-files\nmode: exclusive\noutputs:\n"
        "  - out/registry.yaml\n", encoding="utf-8")
    target = repo / "out" / "registry.yaml"

    with guarded_generation("hot-governance-files", manifest, root=root,
                            start=repo) as g:
        target.write_text("content\n", encoding="utf-8")
        g.record_written(target)

    assert target.read_text(encoding="utf-8") == "content\n"
    assert g.drift == []


def test_guarded_generation_flags_out_of_manifest_drift(tmp_path):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / "out").mkdir(parents=True)
    (repo / ".git").mkdir()
    cdb.ensure_db(root)
    manifest = repo / "manifest.yaml"
    manifest.write_text(
        "generator_id: hot-governance-files\nmode: exclusive\noutputs:\n"
        "  - out/registry.yaml\n", encoding="utf-8")

    with guarded_generation("hot-governance-files", manifest, root=root,
                            start=repo) as g:
        declared = repo / "out" / "registry.yaml"
        declared.write_text("ok\n", encoding="utf-8")
        g.record_written(declared)
        rogue = repo / "out" / "rogue.yaml"
        rogue.write_text("undeclared\n", encoding="utf-8")
        g.record_written(rogue)

    assert g.drift == ["out/rogue.yaml"]
