"""Idempotency test: sal_master_runner.py --from-cache-only produces identical output on consecutive runs.

TC-MACH-REWORK-002 evidence: two consecutive calls with the same args must yield
identical spec_facts_total and identical fact ID sets. This ensures governance-cycle
safety — random ordering or ID changes across runs would invalidate fact references
stored in declarations.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

_SPEC_CACHE = _REPO / ".local" / "spec-cache"
pytestmark = pytest.mark.skipif(
    not _SPEC_CACHE.is_dir(),
    reason="SAL spec-cache not present in this environment",
)


def _run_for_format(fmt: str) -> tuple[int, set[str]]:
    from sal_master_runner import run_sal_pipeline
    result = run_sal_pipeline([fmt], from_cache_only=True)
    facts = []
    for r in result["results"]:
        if r["format_id"] == fmt:
            facts = r.get("spec_facts", [])
            break
    ids = {f.get("qname") or f.get("claim_id") or f.get("source_id", "") for f in facts}
    return len(facts), ids


def test_fods_idempotent_fact_count():
    """Two FODS runs must produce the same fact count."""
    count1, _ = _run_for_format("fods")
    count2, _ = _run_for_format("fods")
    assert count1 == count2, f"FODS fact count changed between runs: {count1} != {count2}"


def test_fods_idempotent_fact_ids():
    """Two FODS runs must produce the same set of fact IDs."""
    _, ids1 = _run_for_format("fods")
    _, ids2 = _run_for_format("fods")
    assert ids1 == ids2, f"FODS fact ID sets differ: {ids1 ^ ids2}"


def test_zst_idempotent_fact_count():
    """Two ZST runs must produce the same fact count."""
    count1, _ = _run_for_format("zst")
    count2, _ = _run_for_format("zst")
    assert count1 == count2, f"ZST fact count changed between runs: {count1} != {count2}"


def test_zst_idempotent_fact_ids():
    """Two ZST runs must produce the same set of fact IDs."""
    _, ids1 = _run_for_format("zst")
    _, ids2 = _run_for_format("zst")
    assert ids1 == ids2, f"ZST fact ID sets differ: {ids1 ^ ids2}"


def test_all_formats_idempotent_total():
    """Two full --all runs must produce the same total spec_facts_total."""
    from sal_master_runner import run_sal_pipeline
    r1 = run_sal_pipeline(None, from_cache_only=True)
    r2 = run_sal_pipeline(None, from_cache_only=True)
    total1 = r1.get("spec_facts_total", 0)
    total2 = r2.get("spec_facts_total", 0)
    assert total1 == total2, f"Total fact count changed between runs: {total1} != {total2}"
    assert total1 >= 14000, f"Expected >= 14000 total facts, got {total1}"
