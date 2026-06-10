"""Tests for ProductSourceExecutor.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-1-001
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from product_source_executor import ProductSourceExecutor, _HARD_FORBIDDEN


def _make_item(**overrides):
    base = {
        "action_id": "q-test-001",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "stream": "product",
        "priority": 1,
        "status": "pending",
        "objective": "Test feature implementation",
        "allowed_paths": ["src/python/"],
        "forbidden_paths": [],
        "human_approval_required": False,
        "evidence_required": True,
        "rollback_strategy": "git checkout src/python/fodg/fodg_codec.py",
        "expected_tests": [],
        "patch_code": "def test_func():\n    return 42\n",
    }
    base.update(overrides)
    return base


class TestPathValidation:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_hard_forbidden_src_net_blocked(self):
        item = _make_item(
            allowed_paths=["src/net/"],
            target_path="src/net/fods/SomeFile.cs",
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "hard-forbidden" in (result.error or "")

    def test_hard_forbidden_registry_blocked(self):
        item = _make_item(
            allowed_paths=["registry/"],
            target_path="registry/format-registry.yaml",
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "hard-forbidden" in (result.error or "")

    def test_hard_forbidden_poc_targets_blocked(self):
        item = _make_item(
            allowed_paths=["product-capability-matrix/"],
            target_path="product-capability-matrix/poc-targets.yaml",
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"

    def test_item_forbidden_paths_honored(self):
        item = _make_item(
            allowed_paths=["src/python/"],
            forbidden_paths=["src/python/ndjson/"],
            target_path="src/python/ndjson/ndjson_codec.py",
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "forbidden by item policy" in (result.error or "")

    def test_path_not_in_allowed_paths_blocked(self):
        item = _make_item(
            allowed_paths=["src/python/fodg/"],
            target_path="src/python/tsv/tsv_parser.py",
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "not in allowed_paths" in (result.error or "")

    def test_valid_path_in_allowed_paths_passes_validation(self):
        """Validation passes (blocked only because file doesn't exist in tmp)."""
        item = _make_item(
            allowed_paths=["src/python/fodg/"],
            target_path="src/python/fodg/fodg_codec.py",
        )
        # Validation itself passes; execution may fail due to file not found
        errors = self.executor._validate_paths(item, "src/python/fodg/fodg_codec.py")
        assert errors is None


class TestMissingFields:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_missing_target_path_blocked(self):
        # No target_path, no expected_files_to_change in the item
        item = _make_item()
        item.pop("target_path", None)
        item.pop("expected_files_to_change", None)
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"

    def test_missing_patch_code_blocked(self):
        item = _make_item(
            target_path="src/python/fodg/fodg_codec.py",
        )
        del item["patch_code"]
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "patch_code" in (result.error or "")


class TestPatchSizeLimit:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_oversized_patch_blocked(self):
        huge_patch = "\n".join(f"# line {i}" for i in range(250))
        item = _make_item(
            target_path="src/python/fodg/fodg_codec.py",
            patch_code=huge_patch,
        )
        result = self.executor.execute(item)
        assert result.status == "BLOCKED"
        assert "too large" in (result.error or "")

    def test_small_patch_not_blocked_by_size(self):
        small_patch = "\n".join(f"# line {i}" for i in range(10))
        # Will fail at file-not-found, not size
        item = _make_item(
            target_path="src/python/fodg/fodg_codec.py",
            allowed_paths=["src/python/fodg/"],
            patch_code=small_patch,
        )
        errors = self.executor._validate_paths(item, "src/python/fodg/fodg_codec.py")
        assert errors is None  # path check passes


class TestApplyFeature:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_appends_to_end_of_file(self, tmp_path):
        source = tmp_path / "test_mod.py"
        source.write_text("def existing():\n    pass\n", encoding="utf-8")
        item = {"insert_before": None}
        self.executor._apply_feature(source, "def new_func():\n    return 1\n", item)
        content = source.read_text(encoding="utf-8")
        assert "def existing" in content
        assert "def new_func" in content

    def test_inserts_before_anchor(self, tmp_path):
        source = tmp_path / "test_mod.py"
        source.write_text(
            "# internal helpers\ndef helper():\n    pass\n", encoding="utf-8"
        )
        item = {"insert_before": "# internal helpers"}
        self.executor._apply_feature(source, "def new_func():\n    return 1\n", item)
        content = source.read_text(encoding="utf-8")
        assert content.index("def new_func") < content.index("# internal helpers")


class TestRollback:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_rollback_restores_original(self, tmp_path):
        source = tmp_path / "mod.py"
        original = "def original():\n    pass\n"
        source.write_text(original, encoding="utf-8")
        source.write_text("def changed():\n    pass\n", encoding="utf-8")
        self.executor._rollback(source, original)
        assert source.read_text(encoding="utf-8") == original


class TestSuccessPath:
    def setup_method(self):
        self.executor = ProductSourceExecutor()

    def test_success_when_tests_pass(self, tmp_path):
        """Integration: apply patch + mock passing tests → SUCCESS."""
        source_file = tmp_path / "fodg_codec.py"
        source_file.write_text("def existing():\n    pass\n", encoding="utf-8")

        item = _make_item(
            target_path=str(source_file.relative_to(tmp_path)),
            allowed_paths=[""],  # Allow everything in tmp context
            patch_code="def new_feature():\n    return 'ok'\n",
            expected_tests=["tests/python/fodg/"],
        )

        executor = ProductSourceExecutor(repo_root=tmp_path)

        with patch.object(executor, "_run_tests", return_value=(True, "1 passed")):
            with patch.object(executor, "_record_evidence"):
                result = executor.execute(item)

        assert result.status == "SUCCESS"
        assert result.test_passed is True

    def test_rollback_when_tests_fail(self, tmp_path):
        """Integration: apply patch + mock failing tests → ROLLED_BACK."""
        source_file = tmp_path / "fodg_codec.py"
        original = "def existing():\n    pass\n"
        source_file.write_text(original, encoding="utf-8")

        item = _make_item(
            target_path=str(source_file.relative_to(tmp_path)),
            allowed_paths=[""],
            patch_code="def new_broken():\n    raise ValueError\n",
            expected_tests=["tests/python/fodg/"],
        )

        executor = ProductSourceExecutor(repo_root=tmp_path)

        with patch.object(executor, "_run_tests", return_value=(False, "1 failed")):
            result = executor.execute(item)

        assert result.status == "ROLLED_BACK"
        assert result.rollback_performed is True
        assert source_file.read_text(encoding="utf-8") == original


class TestLedgerWrite:
    def test_record_evidence_writes_ledger(self, tmp_path):
        executor = ProductSourceExecutor(repo_root=tmp_path)
        ledger_dir = tmp_path / ".local" / "supervisor"
        ledger_dir.mkdir(parents=True)

        item = _make_item(sprint_id="TEST-SPRINT-001")
        executor._record_evidence(item, "src/python/fodg/fodg_codec.py", "1 passed")

        ledger = ledger_dir / "lane-execution-ledger.json"
        assert ledger.exists()
        data = json.loads(ledger.read_text(encoding="utf-8"))
        assert len(data["executions"]) == 1
        entry = data["executions"][0]
        assert entry["action_id"] == "q-test-001"
        assert entry["status"] == "SUCCESS"
        assert entry["action_source"] == "queue_dispatched"
