"""Tests for backfill dry-run tool (TC-GFB-024-03, FF-MR-2026-001).

Requirements: REQ-BF-001, REQ-BF-002 — dry_run_migration.py must be read-only.

Tests:
1. dry_run produces no src/ changes (zero mutation contract)
2. dry_run output is deterministic (run twice → identical content)
3. Continuation idempotency: check_continuation.py output is stable
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "backfill"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestDryRunNoSrcChanges:
    """dry_run_migration.py must make zero changes to src/."""

    def test_dry_run_produces_no_src_changes(self, tmp_path: Path) -> None:
        """After running dry_run, src/ content must be unchanged.

        This test reads all .py files under src/python/ before and after the dry run
        and asserts identical content (by collecting file sizes as a fast proxy).
        """
        src_python = REPO_ROOT / "src" / "python"
        if not src_python.is_dir():
            pytest.skip("src/python/ not available in this repo layout")

        # Capture pre-run fingerprint (file sizes as fast proxy for content)
        def fingerprint(root: Path) -> dict[str, int]:
            return {
                str(p.relative_to(root)): p.stat().st_size
                for p in sorted(root.rglob("*.py"))
                if "build" not in p.parts and "__pycache__" not in p.parts
            }

        pre = fingerprint(src_python)

        from dry_run_migration import run_dry_run
        result = run_dry_run("fods", target_profile="MINIMAL", out_path=tmp_path / "out.json")

        post = fingerprint(src_python)

        assert result["src_mutations"] == 0, (
            f"dry_run must report src_mutations=0, got: {result['src_mutations']}"
        )
        assert pre == post, (
            f"src/python/ changed after dry run — new/deleted/modified files:\n"
            + "\n".join(
                f"  {k}: {pre.get(k, 'missing')} -> {post.get(k, 'missing')}"
                for k in sorted(set(pre.keys()) | set(post.keys()))
                if pre.get(k) != post.get(k)
            )
        )

    def test_dry_run_contract_field_present(self, tmp_path: Path) -> None:
        """dry_run result must include contract_ref and schema_ref fields."""
        from dry_run_migration import run_dry_run
        result = run_dry_run("csv", target_profile="MINIMAL", out_path=tmp_path / "out.json")
        assert "contract_ref" in result, "result must have contract_ref"
        assert "schema_ref" in result, "result must have schema_ref"
        assert result["dry_run"] is True, "result must have dry_run=True"


class TestDryRunDeterminism:
    """dry_run_migration.py output must be deterministic."""

    def test_dry_run_output_is_deterministic(self, tmp_path: Path) -> None:
        """Running dry_run twice for the same format must produce identical JSON output."""
        from dry_run_migration import run_dry_run

        out1 = tmp_path / "run1.json"
        out2 = tmp_path / "run2.json"

        result1 = run_dry_run("csv", target_profile="MINIMAL", out_path=out1)
        result2 = run_dry_run("csv", target_profile="MINIMAL", out_path=out2)

        # Compare proposed migrations (excluding timestamp)
        migrations1 = result1["proposed_migrations"]
        migrations2 = result2["proposed_migrations"]

        assert len(migrations1) == len(migrations2), (
            f"dry_run count must be stable: {len(migrations1)} vs {len(migrations2)}"
        )

        # Source files and symbols must be identical
        keys1 = [(m["source_file"], m["old_symbol"]) for m in migrations1]
        keys2 = [(m["source_file"], m["old_symbol"]) for m in migrations2]
        assert keys1 == keys2, (
            f"dry_run migrations are not deterministic:\n  run1: {keys1}\n  run2: {keys2}"
        )

    def test_dry_run_schema_fields_stable(self, tmp_path: Path) -> None:
        """dry_run result fields must match migration-map.schema.yaml required fields."""
        from dry_run_migration import run_dry_run

        result = run_dry_run("csv", target_profile="MINIMAL", out_path=tmp_path / "out.json")

        # Top-level result fields
        required_top = {"dry_run", "src_mutations", "format_id", "proposed_migrations",
                        "proposed_migration_count", "contract_ref", "schema_ref"}
        missing_top = required_top - set(result.keys())
        assert not missing_top, f"Result is missing fields: {missing_top}"

        # Each migration entry must have schema-required fields
        schema_required = {
            "format_id", "source_file", "old_symbol", "new_symbol",
            "symbol_type", "reason", "behavior_preservation_class",
        }
        for entry in result["proposed_migrations"]:
            missing_entry = schema_required - set(entry.keys())
            assert not missing_entry, (
                f"Migration entry missing required schema fields: {missing_entry}\nEntry: {entry}"
            )


class TestContinuationIdempotency:
    """check_continuation.py output must be stable when state is unchanged."""

    def test_continuation_check_is_idempotent(self, tmp_path: Path) -> None:
        """Running check_continuation twice with unchanged state must return identical verdicts."""
        import json
        import yaml

        sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

        # Set up minimal continuation environment
        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True)
        signal = {
            "autonomous_continue": True,
            "continuation_state": "YES",
            "iteration": 1,
            "max_iterations": 12,
            "rework_items": [],
            "stop_reason": None,
            "session_id": None,
            "hard_stops_detected": [],
        }
        (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))
        (tmp_path / "reports").mkdir()
        (tmp_path / "reports" / "supervisor").mkdir()
        (tmp_path / "reports" / "supervisor" / "approval-gates.md").write_text(
            "AUTONOMOUS_CONTINUE: YES\n"
        )
        (tmp_path / ".local" / "supervisor" / "next-work-items.json").write_text(
            json.dumps({"work_items": [{"id": "W1", "format": "csv"}]})
        )

        from check_continuation import check

        # Run twice without changing state
        result1 = check(tmp_path)
        result2 = check(tmp_path)

        assert result1["verdict"] == result2["verdict"], (
            f"check_continuation verdict is not idempotent: {result1['verdict']} vs {result2['verdict']}"
        )

        # Reason must also be stable
        reason1 = result1.get("reason", "")
        reason2 = result2.get("reason", "")
        assert reason1 == reason2, (
            f"check_continuation reason is not idempotent: {reason1!r} vs {reason2!r}"
        )
