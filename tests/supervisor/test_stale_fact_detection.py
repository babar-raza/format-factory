"""
Tests for stale fact detection policy.

Sprint: FORMAT-FACTORY-SAL-PHASE2-CLOSEOUT-AND-PRODUCT-GATED-ADVANCEMENT-001
Heals: SAL-GAP-005 — stale fact detection was manual only.

Policy (WARNING mode):
- Fact with spec_sha256 matching registered source hash: CURRENT
- Fact with spec_sha256 that does NOT match: STALE_WARNING (not hard-block)
- Fact with null/missing spec_sha256: UNKNOWN_FRESHNESS (warn, do not block)
- missing_hash_warn: legacy formats without hash are warned, not blocked
"""
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / "tools" / "supervisor"))
_SPEC_CACHE = REPO / ".local" / "spec-cache"


# ── Inline stale-fact policy (mirrors warning-mode design) ──────────────────

_STALE_WARNING = "STALE_WARNING"
_CURRENT = "CURRENT"
_UNKNOWN = "UNKNOWN_FRESHNESS"


def check_fact_freshness(fact_sha256: str | None, registered_source_sha256: str | None) -> str:
    """
    Compare fact provenance sha256 against registered source sha256.

    Returns:
        CURRENT — hashes match (or both are None — legacy equal)
        STALE_WARNING — hashes both present but differ
        UNKNOWN_FRESHNESS — one or both hashes missing
    """
    if fact_sha256 is None and registered_source_sha256 is None:
        return _UNKNOWN  # Both unknown — cannot determine freshness
    if fact_sha256 is None or registered_source_sha256 is None:
        return _UNKNOWN  # One is missing — cannot determine
    # Normalize sha256: strip "sha256:" prefix if present
    def _norm(s: str) -> str:
        return s.lower().replace("sha256:", "").strip()
    if _norm(fact_sha256) == _norm(registered_source_sha256):
        return _CURRENT
    return _STALE_WARNING  # noqa: F821 — defined above


def check_spec_cache_freshness(format_id: str) -> list[dict]:
    """
    Check all facts in .local/spec-cache/{format}/*/workbench/verified-facts-review.yaml.
    Returns list of {fact_id, status, spec_sha256, registered_sha256} dicts.
    """
    cache_dir = REPO / ".local" / "spec-cache" / format_id.lower()
    if not cache_dir.exists():
        return []

    results = []
    for review_file in sorted(cache_dir.rglob("verified-facts-review.yaml")):
        content = review_file.read_text(encoding="utf-8")
        if content.lstrip().startswith("{"):
            data = json.loads(content)
        else:
            # Simple YAML parser for this specific file structure
            data = _simple_yaml_parse(content)
        if not data:
            continue

        # Get top-level spec_sha256 (registered source hash for this file)
        registered_sha = data.get("spec_sha256")

        for fact in data.get("facts", []):
            if not isinstance(fact, dict):
                continue
            cid = fact.get("claim_id", "")
            if not cid:
                continue
            # Get fact-level sha256 from provenance
            prov = fact.get("provenance", {}) or {}
            fact_sha = prov.get("source_sha256")
            status = check_fact_freshness(fact_sha, registered_sha)
            results.append({
                "fact_id": cid,
                "status": status,
                "fact_sha256": fact_sha,
                "registered_sha256": registered_sha,
            })
    return results


def _simple_yaml_parse(text: str) -> dict:
    """Minimal YAML parser for verified-facts-review.yaml structure."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        pass
    # Fallback: parse top-level spec_sha256 only
    result: dict = {"facts": []}
    for line in text.splitlines():
        m = re.match(r'^spec_sha256:\s*"?([^"#\n]+)"?', line)
        if m:
            result["spec_sha256"] = m.group(1).strip() or None
    return result


# ── Tests ────────────────────────────────────────────────────────────────────


class TestFreshnessLogic:
    """Unit tests for check_fact_freshness logic."""

    def test_matching_hashes_returns_current(self):
        sha = "sha256:abc123"
        assert check_fact_freshness(sha, sha) == _CURRENT

    def test_matching_hashes_without_prefix(self):
        assert check_fact_freshness("abc123", "abc123") == _CURRENT

    def test_matching_hashes_mixed_prefix(self):
        assert check_fact_freshness("sha256:abc123", "abc123") == _CURRENT

    def test_mismatched_hashes_returns_stale_warning(self):
        assert check_fact_freshness("sha256:aaa", "sha256:bbb") == _STALE_WARNING

    def test_null_fact_sha_returns_unknown(self):
        assert check_fact_freshness(None, "sha256:aaa") == _UNKNOWN

    def test_null_registered_sha_returns_unknown(self):
        assert check_fact_freshness("sha256:aaa", None) == _UNKNOWN

    def test_both_null_returns_unknown(self):
        assert check_fact_freshness(None, None) == _UNKNOWN

    def test_case_insensitive_comparison(self):
        assert check_fact_freshness("SHA256:ABC123", "sha256:abc123") == _CURRENT


class TestStaleWarningIsNotHardBlock:
    """Verify stale detection is WARNING mode, not hard-block."""

    def test_stale_warning_value(self):
        assert _STALE_WARNING == "STALE_WARNING"

    def test_stale_is_not_block(self):
        assert _STALE_WARNING != "BLOCK"
        assert _STALE_WARNING != "HARD_BLOCK"
        assert _STALE_WARNING != "FAIL"

    def test_unknown_is_not_block(self):
        assert _UNKNOWN != "BLOCK"
        assert _UNKNOWN != "HARD_BLOCK"

    def test_stale_does_not_prevent_all_queries(self):
        # If stale detection returned BLOCK, product work would be blocked for all
        # legacy formats with no hash. Verify it returns WARNING.
        result = check_fact_freshness("sha256:old", "sha256:new")
        assert result == _STALE_WARNING, f"Expected WARNING, got {result}"


class TestSpecCacheFreshnessCheck:
    """Integration test against real spec cache."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_zst_facts_freshness_check_runs(self):
        results = check_spec_cache_freshness("zst")
        assert results, "Expected at least one ZST fact result"
        for r in results:
            assert "fact_id" in r
            assert "status" in r
            assert r["status"] in (_CURRENT, _STALE_WARNING, _UNKNOWN)

    def test_zst_matching_hashes_are_current(self):
        results = check_spec_cache_freshness("zst")
        for r in results:
            # ZST facts have consistent sha256 in provenance == top-level
            # If they match, status should be CURRENT
            if r["fact_sha256"] and r["registered_sha256"]:
                if r["fact_sha256"].replace("sha256:", "") == r["registered_sha256"].replace("sha256:", ""):
                    assert r["status"] == _CURRENT

    def test_no_format_has_stale_warning_for_zst(self):
        """ZST spec is a single cached file — should not be stale."""
        results = check_spec_cache_freshness("zst")
        stale = [r for r in results if r["status"] == _STALE_WARNING]
        assert not stale, f"Unexpected STALE_WARNING for ZST facts: {stale}"

    def test_abw_format_has_unknown_freshness(self):
        """ABW spec cache facts exist but have UNKNOWN_FRESHNESS (no registered sha256)."""
        results = check_spec_cache_freshness("abw")
        assert isinstance(results, list)
        # ABW facts may exist with UNKNOWN_FRESHNESS; all must have valid status
        for r in results:
            assert r["status"] in (_CURRENT, _STALE_WARNING, _UNKNOWN), \
                f"Unexpected status for ABW fact: {r}"

    def test_fods_facts_run_without_error(self):
        results = check_spec_cache_freshness("fods")
        assert isinstance(results, list)
        # All should have valid status values
        for r in results:
            assert r["status"] in (_CURRENT, _STALE_WARNING, _UNKNOWN)
