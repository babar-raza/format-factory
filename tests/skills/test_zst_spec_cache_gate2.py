"""
ZST Gate 2 — Spec Cache Validation Tests
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001

Validates:
1. spec-index.yaml validity for rfc8878 and rfc9659
2. SHA-256 checksums match cached files
3. manifest.yaml exists
4. RFC 8878 -> updated_by RFC 9659 relationship is recorded
5. No generated requirements or src mutations
6. No unrelated specs cached under zst/
"""
import hashlib
import yaml
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
SPEC_CACHE_ROOT = REPO_ROOT / ".local" / "spec-cache" / "zst"

RFC8878_SHA256 = "sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4"
RFC9659_SHA256 = "sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2"


# ── Cache existence ────────────────────────────────────────────────────────────

def test_spec_cache_zst_root_exists():
    assert SPEC_CACHE_ROOT.exists(), (
        ".local/spec-cache/zst/ must exist after R14 Gate 2 retrieval"
    )


def test_rfc8878_file_exists():
    assert (SPEC_CACHE_ROOT / "rfc8878" / "rfc8878.txt").exists()


def test_rfc9659_file_exists():
    assert (SPEC_CACHE_ROOT / "rfc9659" / "rfc9659.txt").exists()


def test_manifest_yaml_exists():
    assert (SPEC_CACHE_ROOT / "manifest.yaml").exists()


def test_update_relationship_yaml_exists():
    assert (SPEC_CACHE_ROOT / "provenance" / "update-relationship.yaml").exists()


# ── SHA-256 integrity ──────────────────────────────────────────────────────────

def test_rfc8878_sha256_matches():
    path = SPEC_CACHE_ROOT / "rfc8878" / "rfc8878.txt"
    actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == RFC8878_SHA256, f"RFC 8878 hash mismatch: {actual}"


def test_rfc9659_sha256_matches():
    path = SPEC_CACHE_ROOT / "rfc9659" / "rfc9659.txt"
    actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == RFC9659_SHA256, f"RFC 9659 hash mismatch: {actual}"


def test_rfc8878_spec_index_sha256_matches_file():
    index_path = SPEC_CACHE_ROOT / "rfc8878" / "spec-index.yaml"
    with open(index_path) as f:
        index = yaml.safe_load(f)
    recorded = index.get("sha256") or index.get("content_hash")
    assert recorded == RFC8878_SHA256, f"spec-index sha256 mismatch: {recorded}"


def test_rfc9659_spec_index_sha256_matches_file():
    index_path = SPEC_CACHE_ROOT / "rfc9659" / "spec-index.yaml"
    with open(index_path) as f:
        index = yaml.safe_load(f)
    recorded = index.get("sha256") or index.get("content_hash")
    assert recorded == RFC9659_SHA256, f"spec-index sha256 mismatch: {recorded}"


# ── spec-index.yaml content ────────────────────────────────────────────────────

def test_rfc8878_spec_index_format_id_is_zst():
    with open(SPEC_CACHE_ROOT / "rfc8878" / "spec-index.yaml") as f:
        index = yaml.safe_load(f)
    assert index.get("format_id") == "zst"


def test_rfc9659_spec_index_format_id_is_zst():
    with open(SPEC_CACHE_ROOT / "rfc9659" / "spec-index.yaml") as f:
        index = yaml.safe_load(f)
    assert index.get("format_id") == "zst"


def test_rfc8878_spec_index_local_only():
    with open(SPEC_CACHE_ROOT / "rfc8878" / "spec-index.yaml") as f:
        index = yaml.safe_load(f)
    assert index.get("local_only") is True


def test_rfc8878_not_stale():
    with open(SPEC_CACHE_ROOT / "rfc8878" / "spec-index.yaml") as f:
        index = yaml.safe_load(f)
    assert index.get("stale") is False


# ── Update relationship ────────────────────────────────────────────────────────

def test_update_relationship_rfc8878_updated_by_rfc9659():
    with open(SPEC_CACHE_ROOT / "provenance" / "update-relationship.yaml") as f:
        rel = yaml.safe_load(f)
    # Support both flat (rfc8878_updated_by) and nested (update_relationship.update.rfc) structures
    ur = rel.get("update_relationship", rel)
    flat_key = str(ur.get("rfc8878_updated_by", ""))
    nested_rfc = str(ur.get("update", {}).get("rfc", ""))
    nested_updates = str(ur.get("update", {}).get("updates", ""))
    combined = (flat_key + nested_rfc + nested_updates).upper()
    assert "9659" in combined, (
        f"RFC 8878 updated-by RFC 9659 relationship not found. combined={combined!r}"
    )


def test_update_relationship_rfc9659_scope_http_only():
    with open(SPEC_CACHE_ROOT / "provenance" / "update-relationship.yaml") as f:
        rel = yaml.safe_load(f)
    ur = rel.get("update_relationship", rel)
    # Support flat (rfc9659_scope) or nested (update.scope / update.description)
    flat_scope = str(ur.get("rfc9659_scope", "")).lower()
    nested_scope = str(ur.get("update", {}).get("scope", "")).lower()
    nested_desc = str(ur.get("update", {}).get("description", "")).lower()
    combined = flat_scope + nested_scope + nested_desc
    assert "http" in combined, "RFC 9659 update scope must note HTTP context"


def test_manifest_both_rfcs_present():
    with open(SPEC_CACHE_ROOT / "manifest.yaml") as f:
        manifest = yaml.safe_load(f)
    entries = manifest.get("spec_cache_manifest", manifest).get("entries", [])
    versions = {e.get("version") for e in entries}
    assert "rfc8878" in versions, "manifest must include rfc8878"
    assert "rfc9659" in versions, "manifest must include rfc9659"


# ── No forbidden artifacts ─────────────────────────────────────────────────────

def test_no_generated_requirements_zst():
    path = REPO_ROOT / "generated-requirements" / "zst"
    assert not path.exists(), "generated-requirements/zst must not exist"


def test_no_src_net_zst():
    path = REPO_ROOT / "src" / "net" / "zst"
    assert not path.exists(), "src/net/zst must not exist"


def test_src_python_zst_exists():
    """src/python/zst/ must exist — R20 authorized python_foss implementation."""
    path = REPO_ROOT / "src" / "python" / "zst"
    assert path.exists(), "src/python/zst must exist — authorized in R20"


def test_no_unrelated_specs_in_zst_cache():
    """Only rfc8878/ and rfc9659/ subdirectories should exist under spec-cache/zst/."""
    allowed = {"rfc8878", "rfc9659", "provenance", "manifest.yaml"}
    for item in SPEC_CACHE_ROOT.iterdir():
        assert item.name in allowed, (
            f"Unexpected item in spec-cache/zst/: {item.name}"
        )
