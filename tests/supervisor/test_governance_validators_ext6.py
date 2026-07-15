"""Tests for V224 validate_backfill_completeness (TC-GOV-V224-001)."""

import json

from tools.supervisor.governance_validators_ext6 import validate_backfill_completeness


class TestV224BackfillCompleteness:
    def test_pass_no_migration_dir(self, tmp_path):
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "PASS"
        assert r["validator"] == "validate_backfill_completeness"

    def test_pass_empty_migration_dir(self, tmp_path):
        (tmp_path / "reports" / "qname-migration").mkdir(parents=True)
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "PASS"

    def test_pass_all_actions_none(self, tmp_path):
        mig_dir = tmp_path / "reports" / "qname-migration"
        mig_dir.mkdir(parents=True)
        (mig_dir / "fods-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "NONE"}, {"action_required": "NONE"}]
        }))
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "PASS"

    def test_warn_missing_backfill_plan(self, tmp_path):
        mig_dir = tmp_path / "reports" / "qname-migration"
        mig_dir.mkdir(parents=True)
        (mig_dir / "fods-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "MOVE_FILE"}, {"action_required": "NONE"}]
        }))
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "WARN"
        assert r["blocks_sprint"] is False
        assert len(r["violations"]) == 1
        assert "fods" in r["violations"][0]

    def test_pass_backfill_plan_exists(self, tmp_path):
        mig_dir = tmp_path / "reports" / "qname-migration"
        mig_dir.mkdir(parents=True)
        (mig_dir / "fods-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "MOVE_FILE"}]
        }))
        (mig_dir / "fods-backfill-plan.yaml").write_text("steps:\n  - move file\n")
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "PASS"

    def test_warn_empty_backfill_plan(self, tmp_path):
        mig_dir = tmp_path / "reports" / "qname-migration"
        mig_dir.mkdir(parents=True)
        (mig_dir / "csv-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "MISSING_CLASS"}]
        }))
        (mig_dir / "csv-backfill-plan.yaml").write_text("")
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "WARN"
        assert "csv" in r["violations"][0]

    def test_multiple_formats_mixed(self, tmp_path):
        mig_dir = tmp_path / "reports" / "qname-migration"
        mig_dir.mkdir(parents=True)
        (mig_dir / "fods-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "MOVE_FILE"}]
        }))
        (mig_dir / "fods-backfill-plan.yaml").write_text("steps:\n  - move\n")
        (mig_dir / "csv-migration-map.json").write_text(json.dumps({
            "entries": [{"action_required": "MISSING_CLASS"}]
        }))
        # csv has no backfill plan
        r = validate_backfill_completeness({}, tmp_path)
        assert r["result"] == "WARN"
        assert len(r["violations"]) == 1
        assert "csv" in r["violations"][0]
