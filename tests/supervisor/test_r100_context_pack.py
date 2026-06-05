"""
R100 — Context Pack Builder Unit Tests
Tests build_context_pack() structure and generate_md() output.
"""
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from build_context_pack import build_context_pack, generate_md


# ---------------------------------------------------------------------------
# build_context_pack — runs against the real repo
# ---------------------------------------------------------------------------

def test_build_context_pack_returns_dict():
    """build_context_pack() returns a dict with expected top-level keys."""
    pack = build_context_pack(REPO_ROOT)
    assert isinstance(pack, dict)
    for key in ("schema_version", "generated_at", "git", "supervisor_mode"):
        assert key in pack, f"Missing key: {key}"


def test_build_context_pack_has_poc_matrix():
    pack = build_context_pack(REPO_ROOT)
    assert "poc_matrix" in pack, "Context pack should have poc_matrix key"


def test_build_context_pack_has_skill_registry():
    pack = build_context_pack(REPO_ROOT)
    assert "skill_registry" in pack, "Context pack should have skill_registry key"


# ---------------------------------------------------------------------------
# generate_md
# ---------------------------------------------------------------------------

def test_generate_md_returns_string():
    pack = build_context_pack(REPO_ROOT)
    md = generate_md(pack)
    assert isinstance(md, str)
    assert len(md) > 50
    assert "Context Pack" in md or "context" in md.lower()


def test_generate_md_contains_git_info():
    pack = build_context_pack(REPO_ROOT)
    md = generate_md(pack)
    # Should mention git or HEAD
    assert "git" in md.lower() or "HEAD" in md or "head" in md.lower()


def test_context_pack_yaml_roundtrip():
    """Context pack can be serialized to YAML and loaded back."""
    pack = build_context_pack(REPO_ROOT)
    yaml_str = yaml.dump(pack, default_flow_style=False, sort_keys=False)
    loaded = yaml.safe_load(yaml_str)
    assert loaded["git"] == pack["git"]
