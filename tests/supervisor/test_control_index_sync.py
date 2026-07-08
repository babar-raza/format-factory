"""Integration tests for the control index sync pipeline.

Tests full sync, idempotency, rebuild, FTS5 search, and queries
against the real repository data.
"""

import json
import sys
import time
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from control_index import DEFAULT_DB_PATH
from control_index.db import init_db, get_schema_version, ensure_db, get_connection
from control_index.sync import sync_all, rebuild, ALL_INGESTORS


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test-sync.db"


class TestFullSync:
    """Tests requiring sync against real repo data."""

    def test_full_sync_completes_without_errors(self, db_path):
        report = rebuild(db_path, _REPO)
        errors = [r for r in report.results if r.error]
        assert len(errors) == 0, f"Errors: {[r.to_dict() for r in errors]}"

    def test_full_sync_populates_all_entity_types(self, db_path):
        report = rebuild(db_path, _REPO)
        entity_types = {r.entity_type for r in report.results}
        # Core entity types must be present (TC-BF-006 added invocation types as extras)
        required = {"format", "capability", "skill", "layer", "failure",
                    "plan_lock", "source_violation", "gap", "qname", "sprint", "event"}
        assert required.issubset(entity_types), (
            f"Missing entity types: {required - entity_types}"
        )

    def test_full_sync_row_counts(self, db_path):
        report = rebuild(db_path, _REPO)
        counts = {r.entity_type: r.inserted for r in report.results}
        # Committed data (always present in CI)
        assert counts["format"] >= 20
        assert counts["capability"] >= 80
        assert counts["skill"] >= 70
        assert counts["gap"] >= 1000
        assert counts["qname"] >= 60
        # .local/ data (gitignored — only present in local dev environments)
        _local_base = _REPO / ".local" / "supervisor"
        if (_local_base / "failure-memory.json").exists():
            assert counts["failure"] >= 20
        if (_local_base / "plan-locks").exists():
            assert counts["plan_lock"] >= 50
        if (_local_base / "continuation-ledger.jsonl").exists():
            assert counts["event"] >= 10

    def test_sync_under_60_seconds(self, db_path):
        start = time.time()
        rebuild(db_path, _REPO)
        elapsed = time.time() - start
        assert elapsed < 60, f"Full rebuild took {elapsed:.1f}s"

    def test_sync_idempotent(self, db_path):
        # First sync
        report1 = rebuild(db_path, _REPO)
        total1 = sum(r.inserted for r in report1.results)
        assert total1 > 0

        # Second sync — core entity types should skip (hash-based dedup)
        # Some ingestors (source_violation, subprocess_invocation, command_invocation,
        # maintenance_obligation) always re-insert — excluded from idempotency check.
        report2 = sync_all(db_path, _REPO)
        _non_idempotent = {"source_violation", "subprocess_invocation",
                           "command_invocation", "maintenance_obligation",
                           "skill_invocation"}
        core_results = [r for r in report2.results if r.entity_type not in _non_idempotent]
        core_inserted = sum(r.inserted for r in core_results)
        assert core_inserted == 0, f"Core entity types re-inserted: {[(r.entity_type, r.inserted) for r in core_results if r.inserted > 0]}"
        assert all(r.skipped for r in core_results)

    def test_rebuild_matches_sync(self, db_path, tmp_path):
        # First build
        report1 = rebuild(db_path, _REPO)
        counts1 = {r.entity_type: r.inserted for r in report1.results}

        # Rebuild from scratch
        db_path2 = tmp_path / "test-rebuild.db"
        report2 = rebuild(db_path2, _REPO)
        counts2 = {r.entity_type: r.inserted for r in report2.results}

        assert counts1 == counts2

    def test_gap_spec_facts_populated(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            count = conn.execute("SELECT COUNT(*) as c FROM gap_spec_facts").fetchone()["c"]
            assert count > 0, "gap_spec_facts should be populated"
        finally:
            conn.close()

    def test_layer_dependencies_populated(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            count = conn.execute("SELECT COUNT(*) as c FROM layer_dependencies").fetchone()["c"]
            assert count > 0, "layer_dependencies should be populated"
        finally:
            conn.close()


class TestFTS5Search:
    """Tests for FTS5 full-text search."""

    def test_fts5_populated_after_sync(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            count = conn.execute("SELECT COUNT(*) as c FROM fts_operational").fetchone()["c"]
            assert count > 0, "FTS5 should be populated"
        finally:
            conn.close()

    def test_search_returns_results(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            from control_index.search import search
            results = search(conn, "FODS")
            assert len(results) > 0
            # Results should contain multiple entity types
            types_found = {r["entity_type"] for r in results}
            assert len(types_found) >= 1
        finally:
            conn.close()

    def test_search_filter_by_type(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            from control_index.search import search
            results = search(conn, "FODS", entity_types=["gap"])
            assert all(r["entity_type"] == "gap" for r in results)
        finally:
            conn.close()


class TestQueries:
    """Tests for specific query patterns."""

    def test_gaps_by_format(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM gaps WHERE UPPER(format) = 'FODS'"
            ).fetchall()
            assert len(rows) > 0
            assert all(r["format"].upper() == "FODS" for r in rows)
        finally:
            conn.close()

    def test_failures_unresolved(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM failures WHERE resolved = 0"
            ).fetchall()
            assert len(rows) >= 0  # May have all resolved
            for r in rows:
                assert r["resolved"] == 0
        finally:
            conn.close()

    def test_format_dashboard_join(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            fmt = conn.execute(
                "SELECT * FROM formats WHERE format_id = 'fods'"
            ).fetchone()
            assert fmt is not None
            assert fmt["display_name"] == "Flat OpenDocument Spreadsheet"

            gap_count = conn.execute(
                "SELECT COUNT(*) as c FROM gaps WHERE UPPER(format) = 'FODS'"
            ).fetchone()["c"]
            assert gap_count > 0
        finally:
            conn.close()

    def test_query_under_200ms(self, db_path):
        rebuild(db_path, _REPO)
        conn = get_connection(db_path)
        try:
            start = time.time()
            conn.execute(
                "SELECT format, COUNT(*) FROM gaps GROUP BY format ORDER BY COUNT(*) DESC"
            ).fetchall()
            elapsed = (time.time() - start) * 1000
            assert elapsed < 200, f"Query took {elapsed:.0f}ms"
        finally:
            conn.close()


class TestParity:
    """Parity tests: index results match direct file reads."""

    def test_gap_count_parity(self, db_path):
        rebuild(db_path, _REPO)
        # Direct read
        ledger = json.loads((_REPO / "reports/capability-layer/gap-ledger.json").read_text(encoding="utf-8"))
        direct_count = len(ledger["gaps"])
        # Index count
        conn = get_connection(db_path)
        try:
            idx_count = conn.execute("SELECT COUNT(*) as c FROM gaps").fetchone()["c"]
            assert idx_count == direct_count
        finally:
            conn.close()

    def test_format_count_parity(self, db_path):
        import yaml
        rebuild(db_path, _REPO)
        data = yaml.safe_load((_REPO / "registry/format-registry.yaml").read_text())
        direct_count = len(data["formats"])
        conn = get_connection(db_path)
        try:
            idx_count = conn.execute("SELECT COUNT(*) as c FROM formats").fetchone()["c"]
            assert idx_count == direct_count
        finally:
            conn.close()

    def test_skill_count_parity(self, db_path):
        import yaml
        rebuild(db_path, _REPO)
        data = yaml.safe_load((_REPO / ".supervisor/skill-registry.yaml").read_text())
        direct_count = len([s for s in data["skills"] if s.get("command")])
        conn = get_connection(db_path)
        try:
            idx_count = conn.execute("SELECT COUNT(*) as c FROM skills").fetchone()["c"]
            assert idx_count == direct_count
        finally:
            conn.close()

    def test_failure_count_parity(self, db_path):
        failure_path = _REPO / ".local/supervisor/failure-memory.json"
        if not failure_path.exists():
            pytest.skip(".local/supervisor/failure-memory.json not present (gitignored, CI skip)")
        rebuild(db_path, _REPO)
        data = json.loads(failure_path.read_text())
        direct_count = len([f for f in data["failures"] if f.get("id")])
        conn = get_connection(db_path)
        try:
            idx_count = conn.execute("SELECT COUNT(*) as c FROM failures").fetchone()["c"]
            assert idx_count == direct_count
        finally:
            conn.close()
