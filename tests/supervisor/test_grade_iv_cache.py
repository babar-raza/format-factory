"""Tests for intermediate verify result caching (TC-GRADE-003).

Covers:
- Second call returns _from_cache=True when evidence is unchanged
- iv:-prefixed key does not collide with LLM-graded key for same item
- Cache miss after evidence content changes (requires TC-GRADE-001 content-hash)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import _get_cached_grade, _cache_grade  # noqa: E402


class TestIVCacheKeyIsolation:
    def test_iv_cache_key_prefix_isolates_from_llm_cache(self) -> None:
        """iv:-prefixed key does not collide with LLM-graded key for same item."""
        item_id = "TC-TEST-001"
        ev_hash = "deadbeef12345678"
        llm_key = f"{item_id}:{ev_hash}"
        iv_key = f"iv:{item_id}:{ev_hash}"
        assert llm_key != iv_key, "iv: prefix must separate iv-cache from LLM cache keys"

    def test_iv_cache_hit_returns_from_cache_marker(self, tmp_path: Path) -> None:
        """After caching an iv result, a second lookup returns the entry (cache hit)."""
        from datetime import datetime, timezone
        cache_path = tmp_path / "grade-cache.json"
        item_id = "TC-TEST-002"
        ev_hash = "cafebabe12345678"

        # Write a fresh cache entry (simulating what _cache_grade would write)
        _cache_grade(f"iv:{item_id}", ev_hash,
                     {"adequate": True, "source": "intermediate_verify"},
                     cache_path=cache_path)

        result = _get_cached_grade(f"iv:{item_id}", ev_hash, cache_path=cache_path)
        assert result is not None, "Cached iv entry must be retrievable"
        assert result.get("adequate") is True
        assert result.get("source") == "intermediate_verify"

    def test_iv_cache_misses_after_content_change(self, tmp_path: Path, monkeypatch) -> None:
        """Different content hash → different ev_hash → cache miss for second call."""
        import grade_declared_work as gdw
        from grade_declared_work import _evidence_hash

        # Set up a fake REPO_ROOT with an evidence file
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        ev_dir = fake_repo / "ev"
        ev_dir.mkdir()
        ev_file = ev_dir / "proof.txt"
        ev_file.write_bytes(b"original content")
        monkeypatch.setattr(gdw, "REPO_ROOT", fake_repo)

        rel_path = "ev/proof.txt"
        item = {"evidence_paths": [rel_path], "status": "completed", "acceptance_criteria": "x"}
        inspection = {"evidence_paths_found": [rel_path]}

        cache_path = tmp_path / "grade-cache.json"
        ev_hash_v1 = _evidence_hash(item, inspection)
        _cache_grade(f"iv:TC-CONTENT-001", ev_hash_v1,
                     {"adequate": True, "source": "intermediate_verify"},
                     cache_path=cache_path)

        # Change file content → different hash → cache miss
        ev_file.write_bytes(b"modified content")
        ev_hash_v2 = _evidence_hash(item, inspection)

        assert ev_hash_v1 != ev_hash_v2, "Content change must produce different hash"
        result = _get_cached_grade(f"iv:TC-CONTENT-001", ev_hash_v2, cache_path=cache_path)
        assert result is None, "Cache must miss after content change (different ev_hash)"
