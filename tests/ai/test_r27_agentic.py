"""Lane I tests — Qwen2 low-risk agentic controls.

Tests for scoped runner, path allowlist, forbidden operations,
model validation, timeout, and output discard on violation.
"""


from tools.ai.agentic.scoped_runner import (
    AgenticTaskContract,
    FORBIDDEN_OPERATIONS,
    ScopedRunner,
)


class TestContractValidation:
    def test_valid_contract(self):
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/ai/"],
            operation_allowlist=["read_file", "list_dir"],
        )
        assert contract.validate() == []

    def test_forbidden_operation_in_allowlist(self):
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/ai/"],
            operation_allowlist=["commit"],
        )
        errors = contract.validate()
        assert any("forbidden" in e for e in errors)

    def test_missing_path_allowlist(self):
        contract = AgenticTaskContract(
            task_id="t1",
            operation_allowlist=["read_file"],
        )
        errors = contract.validate()
        assert any("path_allowlist" in e for e in errors)


class TestModelValidation:
    def test_qwen_model_accepted(self):
        runner = ScopedRunner()
        assert runner.validate_model("qwen3-next") is True

    def test_non_qwen_rejected(self):
        runner = ScopedRunner()
        assert runner.validate_model("gpt-oss") is False

    def test_non_qwen_model_discards_output(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/"],
            operation_allowlist=["read_file"],
        )
        result = runner.run(contract, model_id="gpt-oss")
        assert result.status == "model_rejected"
        assert result.discarded is True
        assert len(result.violations) > 0


class TestScopeViolation:
    def test_forbidden_path_discards(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/ai/"],
            operation_allowlist=["read_file"],
        )

        def bad_task(c, root):
            return {"files_accessed": ["src/python/fods/codec.py"], "result": {}}

        result = runner.run(contract, model_id="qwen3-next", task_fn=bad_task)
        assert result.status == "scope_violation"
        assert result.discarded is True

    def test_allowed_path_succeeds(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/ai/"],
            operation_allowlist=["read_file"],
        )

        def good_task(c, root):
            return {"files_accessed": ["tools/ai/schemas/models.py"], "result": {"files": 1}}

        result = runner.run(contract, model_id="qwen3-next", task_fn=good_task)
        assert result.status == "success"
        assert result.discarded is False


class TestFixtureMode:
    def test_fixture_mode_without_task_fn(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="t1",
            path_allowlist=["tools/"],
            operation_allowlist=["read_file"],
        )
        result = runner.run(contract, model_id="qwen3-next")
        assert result.status == "fixture_mode"
        assert result.output["mode"] == "fixture"


class TestForbiddenOperations:
    def test_all_dangerous_ops_in_set(self):
        for op in ["commit", "push", "delete_file", "write_src", "gate_evidence_generation"]:
            assert op in FORBIDDEN_OPERATIONS
