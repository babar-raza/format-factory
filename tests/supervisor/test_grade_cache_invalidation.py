"""Tests for grade cache content-hash invalidation and TTL behavior (TC-GRADE-001).

Covers:
- TTL: entries older than 7 days are treated as cache misses
- TTL: fresh entries are returned normally
- Content-hash: same evidence paths but changed file content → different hash
- Content-hash: unchanged file content → same hash (idempotent)
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import _evidence_hash, _get_cached_grade  # noqa: E402


# ---------------------------------------------------------------------------
# TTL tests
# ---------------------------------------------------------------------------


class TestGradeCacheTTL:
    def _write_cache(self, tmp_path: Path, item_id: str, ev_hash: str, cached_at: str) -> Path:
        cache_file = tmp_path / "grade-cache.json"
        cache_file.write_text(
            json.dumps({
                f"{item_id}:{ev_hash}": {"adequate": True, "_cached_at": cached_at},
            }),
            encoding="utf-8",
        )
        return cache_file

    def test_cache_ttl_returns_none_for_expired_entry(self, tmp_path: Path) -> None:
        """Cache entry with _cached_at 8 days ago → _get_cached_grade returns None."""
        old_ts = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        cache_path = self._write_cache(tmp_path, "test_item", "abc123", old_ts)
        result = _get_cached_grade("test_item", "abc123", cache_path=cache_path)
        assert result is None, "8-day-old entry should be treated as a cache miss (TTL expired)"

    def test_cache_ttl_returns_result_for_fresh_entry(self, tmp_path: Path) -> None:
        """Cache entry with _cached_at today → _get_cached_grade returns the result."""
        fresh_ts = datetime.now(timezone.utc).isoformat()
        cache_path = self._write_cache(tmp_path, "test_item", "abc123", fresh_ts)
        result = _get_cached_grade("test_item", "abc123", cache_path=cache_path)
        assert result is not None, "Fresh entry should be returned"
        assert result["adequate"] is True


# ---------------------------------------------------------------------------
# Content-hash tests
# ---------------------------------------------------------------------------


class TestEvidenceHashContentSensitivity:
    def _item_and_inspection(self, evidence_rel_path: str) -> tuple[dict, dict]:
        item = {
            "evidence_paths": [evidence_rel_path],
            "status": "completed",
            "acceptance_criteria": "test",
        }
        inspection = {"evidence_paths_found": [evidence_rel_path]}
        return item, inspection

    def test_evidence_hash_changes_when_file_content_changes(self, tmp_path: Path, monkeypatch) -> None:
        """Same path, different content → different hash (content-sensitive invalidation)."""
        import grade_declared_work as gdw
        # Create a temp evidence file relative to a fake REPO_ROOT
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        evidence_dir = fake_repo / "evidence"
        evidence_dir.mkdir()
        evidence_file = evidence_dir / "proof.txt"
        evidence_file.write_bytes(b"content version A")

        rel_path = "evidence/proof.txt"
        # Patch REPO_ROOT inside grade_declared_work
        monkeypatch.setattr(gdw, "REPO_ROOT", fake_repo)

        item, inspection = self._item_and_inspection(rel_path)
        hash_a = _evidence_hash(item, inspection)

        evidence_file.write_bytes(b"content version B")
        hash_b = _evidence_hash(item, inspection)

        assert hash_a != hash_b, "Hash must change when file content changes"

    def test_evidence_hash_stable_for_unchanged_content(self, tmp_path: Path, monkeypatch) -> None:
        """Same path, same content → same hash on repeated calls (idempotent)."""
        import grade_declared_work as gdw
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        evidence_dir = fake_repo / "evidence"
        evidence_dir.mkdir()
        evidence_file = evidence_dir / "proof.txt"
        evidence_file.write_bytes(b"stable content")

        rel_path = "evidence/proof.txt"
        monkeypatch.setattr(gdw, "REPO_ROOT", fake_repo)

        item, inspection = self._item_and_inspection(rel_path)
        hash_1 = _evidence_hash(item, inspection)
        hash_2 = _evidence_hash(item, inspection)

        assert hash_1 == hash_2, "Hash must be stable for unchanged content"
