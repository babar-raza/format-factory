"""Lane ledger .jsonl support tests (GEC-TC-002).

Verifies that detect_missing_lane_ledger recognizes .jsonl files
(previously only .json and .yaml were searched, causing false violations
when state-ledger.jsonl was the only ledger artifact).
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestLaneLedgerJsonlSupport:
    """Lane ledger detector now finds .jsonl files."""

    def test_lane_execution_ledger_jsonl_found(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "lane-execution-ledger.jsonl").write_text('{"lane":"A"}\n')
        result = detect_missing_lane_ledger(tmp_path)
        assert not result["is_violation"], (
            f"lane-execution-ledger.jsonl should satisfy ledger requirement, got {result}"
        )

    def test_state_ledger_jsonl_found(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "state-ledger.jsonl").write_text('{"taskcard_id":"GEC-TC-001"}\n')
        result = detect_missing_lane_ledger(tmp_path)
        assert not result["is_violation"], (
            f"state-ledger.jsonl should satisfy ledger requirement, got {result}"
        )

    def test_lane_ledger_jsonl_found(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "ledger.jsonl").write_text('{"entry":1}\n')
        result = detect_missing_lane_ledger(tmp_path)
        assert not result["is_violation"], (
            f"ledger.jsonl should satisfy ledger requirement, got {result}"
        )

    def test_legacy_json_ledger_still_found(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "lane-execution-ledger.json").write_text('{}')
        result = detect_missing_lane_ledger(tmp_path)
        assert not result["is_violation"], (
            f"Legacy .json ledger should still be found, got {result}"
        )

    def test_missing_ledger_is_violation(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"], (
            f"Missing ledger must be a violation, got {result}"
        )

    def test_non_ledger_file_does_not_satisfy(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "evidence-declaration.yaml").write_text("run_id: test\n")
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"], (
            f"evidence-declaration.yaml should not satisfy lane-ledger check, got {result}"
        )

    def test_lane_jsonl_satisfies_search(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "lane-execution-ledger.jsonl").write_text('{"lane":"B"}\n')
        result = detect_missing_lane_ledger(tmp_path)
        assert len(result["ledgers_found"]) >= 1, (
            f"Expected at least one ledger found, got {result}"
        )

    def test_reports_dir_jsonl_found_via_declaration(self, tmp_path):
        """Ledger in reports/<run_id>/ recognized when provided via declaration."""
        from anti_skip_checker import detect_missing_lane_ledger
        run_dir = tmp_path / "reports" / "test-run-gec"
        run_dir.mkdir(parents=True)
        (run_dir / "state-ledger.jsonl").write_text('{"taskcard_id":"GEC-TC-001"}\n')
        declaration = {"run_id": "test-run-gec"}
        empty_evidence = tmp_path / "empty-evidence"
        empty_evidence.mkdir()
        result = detect_missing_lane_ledger(
            empty_evidence, declaration=declaration, repo_root=tmp_path
        )
        assert not result["is_violation"], (
            f"state-ledger.jsonl in reports/<run_id>/ should satisfy lane-ledger check, got {result}"
        )


class TestPromptQualityUnsafeWording:
    """Prompt quality validator now blocks unsafe commit/push wording (GEC-TC-005)."""

    def test_safe_governance_prompt_passes(self):
        from validate_prompt_quality import validate_prompt_quality
        prompt = (
            "## Sprint\nGovernance enforcement sprint.\n"
            "## Lane A\nRun governance validators.\n"
            "## Lane B\nFix anti-skip.\n"
            "## Evidence\nWrite evidence-declaration and run autonomous-cycle.\n"
            "Do not commit or push. External gate requires explicit human authorization."
        )
        result = validate_prompt_quality(prompt, "supervisor")
        no_unsafe = next((c for c in result["checks"] if c["check"] == "no_unsafe_commit_push_wording"), None)
        assert no_unsafe is not None, "no_unsafe_commit_push_wording check missing"
        assert no_unsafe["pass"], f"Safe prompt should pass, got {no_unsafe}"

    def test_unsafe_commit_push_fails(self):
        from validate_prompt_quality import validate_prompt_quality
        prompt = (
            "## Sprint\nProduct sprint.\n"
            "## Lane A\nDo work.\n"
            "## Evidence\nAuthorized git commit + push (requires user authorization)\n"
            "evidence-declaration.yaml\nautonomous-cycle\n"
        )
        result = validate_prompt_quality(prompt, "mainstream")
        no_unsafe = next((c for c in result["checks"] if c["check"] == "no_unsafe_commit_push_wording"), None)
        assert no_unsafe is not None, "no_unsafe_commit_push_wording check missing"
        assert not no_unsafe["pass"], f"Unsafe prompt should fail, got {no_unsafe}"
        assert "authorized git commit + push" in no_unsafe["unsafe_patterns_found"]

    def test_check_8_exists_in_validator(self):
        from validate_prompt_quality import validate_prompt_quality
        prompt = (
            "## Sprint\nTest.\n## Lane A\nWork.\n## Evidence\nevidence-declaration.yaml\n"
        )
        result = validate_prompt_quality(prompt, "supervisor")
        check_names = [c["check"] for c in result["checks"]]
        assert "no_unsafe_commit_push_wording" in check_names, (
            f"Check 8 must be present, got {check_names}"
        )

    def test_total_checks_increased_to_8(self):
        from validate_prompt_quality import validate_prompt_quality
        prompt = (
            "## Sprint\nTest.\n## Lane A\nWork.\n## Evidence\nevidence-declaration.yaml\n"
        )
        result = validate_prompt_quality(prompt, "supervisor")
        assert result["total_checks"] >= 7, (
            f"Expected at least 7 checks (was 7 before, now 8), got {result['total_checks']}"
        )
