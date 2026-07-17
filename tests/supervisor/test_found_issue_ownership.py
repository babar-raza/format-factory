"""tests/supervisor/test_found_issue_ownership.py

Tests for governance_validators_found_issue.py — V139-V142 (register-level validators).

V139: validate_found_issue_register_present   — WARN when tests fail but register empty
V140: validate_issue_accounting_reconciles    — FAIL when register has unknown status
V141: validate_no_prose_only_findings         — WARN when dismissal prose in declaration
V142: validate_invalid_ownership_disposition  — FAIL when invalid disposition in register
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from governance_validators_found_issue import (
    validate_found_issue_register_present,
    validate_invalid_ownership_disposition,
    validate_issue_accounting_reconciles,
    validate_no_prose_only_findings,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repo(issues: list[dict]) -> Path:
    """Create a temp dir with registry/found-issue-register.yaml populated."""
    td = Path(tempfile.mkdtemp())
    (td / "registry").mkdir()
    reg = {"version": 1, "issues": issues}
    (td / "registry" / "found-issue-register.yaml").write_text(
        yaml.dump(reg), encoding="utf-8"
    )
    return td


def _make_repo_no_register() -> Path:
    """Create a temp dir WITHOUT a found-issue-register.yaml."""
    td = Path(tempfile.mkdtemp())
    (td / "registry").mkdir()
    return td


# ---------------------------------------------------------------------------
# V139 — validate_found_issue_register_present
# ---------------------------------------------------------------------------


def test_v139_pass_no_failures():
    """V139 PASS: Declaration has no test failures — no check needed."""
    decl = {"sprint_id": "S-001", "tests_run": {"failed": 0}, "failing_tests": []}
    r = validate_found_issue_register_present(decl, _make_repo_no_register())
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v139_pass_has_issues_in_register():
    """V139 PASS: Tests failed AND register has entries."""
    td = _make_repo([{"issue_id": "FI-001", "status": "discovered"}])
    decl = {"sprint_id": "S-001", "tests_run": {"failed": 2}}
    r = validate_found_issue_register_present(decl, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v139_warn_tests_failed_register_empty():
    """V139 WARN: Tests failed but register is empty."""
    td = _make_repo([])
    decl = {"sprint_id": "S-001", "tests_run": {"failed": 3}}
    r = validate_found_issue_register_present(decl, td)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_v139_warn_tests_failed_register_missing():
    """V139 WARN: Tests failed and register file doesn't exist."""
    td = _make_repo_no_register()
    decl = {"sprint_id": "S-001", "tests_run": {"failed": 1}}
    r = validate_found_issue_register_present(decl, td)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_v139_pass_no_sprint_id():
    """V139 PASS: No sprint_id — cannot correlate issues, skip check."""
    td = _make_repo([])
    decl = {"tests_run": {"failed": 5}}  # no sprint_id or run_id
    r = validate_found_issue_register_present(decl, td)
    assert r["result"] == "PASS"


def test_v139_pass_failing_tests_list():
    """V139 PASS: failing_tests list present with entries AND register has issues."""
    td = _make_repo([{"issue_id": "FI-001", "status": "classified"}])
    decl = {"sprint_id": "S-002", "failing_tests": ["test_foo", "test_bar"]}
    r = validate_found_issue_register_present(decl, td)
    assert r["result"] == "PASS"


# ---------------------------------------------------------------------------
# V140 — validate_issue_accounting_reconciles
# ---------------------------------------------------------------------------


def test_v140_pass_empty_register():
    """V140 PASS: No issues to reconcile."""
    td = _make_repo([])
    r = validate_issue_accounting_reconciles({}, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v140_pass_missing_register():
    """V140 PASS: Register file missing — nothing to reconcile."""
    r = validate_issue_accounting_reconciles({}, _make_repo_no_register())
    assert r["result"] == "PASS"


def test_v140_pass_all_valid_statuses():
    """V140 PASS: All statuses map to known buckets."""
    issues = [
        {"issue_id": "FI-001", "status": "discovered"},
        {"issue_id": "FI-002", "status": "verified"},
        {"issue_id": "FI-003", "status": "governed_exclusion"},
        {"issue_id": "FI-004", "status": "in_repair"},
        {"issue_id": "FI-005", "status": "closed"},
    ]
    td = _make_repo(issues)
    r = validate_issue_accounting_reconciles({}, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v140_fail_unknown_status():
    """V140 FAIL: Issue with unrecognized status."""
    issues = [
        {"issue_id": "FI-001", "status": "healing"},  # invalid status
    ]
    td = _make_repo(issues)
    r = validate_issue_accounting_reconciles({}, td)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert any("FI-001" in item for item in r["items"])


def test_v140_fail_multiple_unknown_statuses():
    """V140 FAIL: Multiple unknown statuses reported."""
    issues = [
        {"issue_id": "FI-001", "status": "pre_existing"},
        {"issue_id": "FI-002", "status": "wont_fix"},
    ]
    td = _make_repo(issues)
    r = validate_issue_accounting_reconciles({}, td)
    assert r["result"] == "FAIL"
    assert len(r["items"]) == 2


# ---------------------------------------------------------------------------
# V141 — validate_no_prose_only_findings
# ---------------------------------------------------------------------------


def test_v141_pass_no_prose():
    """V141 PASS: No dismissal language in declaration."""
    decl = {
        "worker_self_verdict": "All tests pass. Fixed the import error.",
        "planned_work_items": [{"id": "WI-001", "notes": "Added missing spec_qname."}],
    }
    r = validate_no_prose_only_findings(decl)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v141_warn_preexisting_in_verdict():
    """V141 WARN: 'pre-existing' in worker_self_verdict."""
    decl = {"worker_self_verdict": "Fixed the pre-existing failures that were already failing."}
    r = validate_no_prose_only_findings(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_v141_warn_dismissal_in_notes():
    """V141 WARN: Dismissal language in planned_work_items notes."""
    decl = {
        "worker_self_verdict": "Sprint complete.",
        "planned_work_items": [
            {"id": "WI-001", "notes": "Skipped — this is probably harmless."}
        ],
    }
    r = validate_no_prose_only_findings(decl)
    assert r["result"] == "WARN"
    assert "WI-001" in r["items"][0]


def test_v141_pass_empty_declaration():
    """V141 PASS: Empty declaration has no prose to scan."""
    r = validate_no_prose_only_findings({})
    assert r["result"] == "PASS"


# ---------------------------------------------------------------------------
# V142 — validate_invalid_ownership_disposition
# ---------------------------------------------------------------------------


def test_v142_pass_empty_register():
    """V142 PASS: No issues in register."""
    td = _make_repo([])
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v142_pass_missing_register():
    """V142 PASS: Register file missing."""
    r = validate_invalid_ownership_disposition({}, _make_repo_no_register())
    assert r["result"] == "PASS"


def test_v142_pass_all_valid_ownership_dispositions():
    """V142 PASS: All issues use valid ownership dispositions."""
    issues = [
        {"issue_id": "FI-001", "status": "closed", "disposition": "HEALED_AND_VERIFIED"},
        {"issue_id": "FI-002", "status": "closed", "disposition": "VALID_GOVERNED_EXCLUSION"},
        {"issue_id": "FI-003", "status": "blocked_external", "disposition": "BLOCKED_TRUE_EXTERNAL_DEPENDENCY"},
        {"issue_id": "FI-004", "status": "duplicate", "disposition": "DUPLICATE_OF_ACTIVE_ISSUE"},
    ]
    td = _make_repo(issues)
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v142_rejects_preexisting_disposition():
    """V142 FAIL: disposition='pre_existing' is not a valid ownership disposition."""
    issues = [
        {"issue_id": "FI-001", "status": "closed", "disposition": "pre_existing"},
    ]
    td = _make_repo(issues)
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert any("FI-001" in item for item in r["items"])


def test_v142_rejects_unrelated_disposition():
    """V142 FAIL: disposition='unrelated' is not a valid ownership disposition."""
    issues = [
        {"issue_id": "FI-007", "status": "closed", "disposition": "unrelated"},
    ]
    td = _make_repo(issues)
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True


def test_v142_pass_no_disposition_in_flight():
    """V142 PASS: Issues with no disposition (in-flight) are not flagged."""
    issues = [
        {"issue_id": "FI-001", "status": "in_repair"},  # no disposition yet
        {"issue_id": "FI-002", "status": "classified"},
    ]
    td = _make_repo(issues)
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v142_rejects_novel_invalid_disposition_not_in_denylist():
    """TC-STRUCT-002 (2026-07-17): allowlist regression pin, real FI-025 shape.

    The pre-fix V142 only checked a fixed denylist of known-bad strings
    (pre_existing, unrelated, not_caused_by_me, ignored, outside_current_task)
    and never checked OWNERSHIP_VALID_DISPOSITIONS at all. The real,
    live `FI-025` entry in registry/found-issue-register.yaml carries
    `disposition: OPEN_OUT_OF_SCOPE` -- a value that matches none of those 5
    denylist strings and sailed through undetected. This reproduces that
    exact shape and asserts the allowlist-based check now catches it.
    """
    issues = [
        {"issue_id": "FI-025", "status": "discovered", "disposition": "OPEN_OUT_OF_SCOPE"},
    ]
    td = _make_repo(issues)
    r = validate_invalid_ownership_disposition({}, td)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert any("FI-025" in item and "OPEN_OUT_OF_SCOPE" in item for item in r["items"])


def test_v142_pass_all_six_allowlisted_dispositions():
    """Every one of the 6 valid ownership dispositions must PASS individually."""
    valid = [
        "HEALED_AND_VERIFIED", "DUPLICATE_OF_ACTIVE_ISSUE",
        "INVALID_FINDING_WITH_PROOF", "VALID_GOVERNED_EXCLUSION",
        "BLOCKED_TRUE_EXTERNAL_DEPENDENCY", "WAITING_VALID_GATE_11_AUTHORIZATION",
    ]
    for i, disp in enumerate(valid):
        issues = [{"issue_id": f"FI-{i:03d}", "status": "closed", "disposition": disp}]
        td = _make_repo(issues)
        r = validate_invalid_ownership_disposition({}, td)
        assert r["result"] == "PASS", f"{disp} should be allowlisted"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_all_validators_pass_empty_declaration():
    """All V139-V142 handle empty declaration without crashing."""
    td = _make_repo([])
    assert validate_found_issue_register_present({}, td)["result"] == "PASS"
    assert validate_issue_accounting_reconciles({}, td)["result"] == "PASS"
    assert validate_no_prose_only_findings({})["result"] == "PASS"
    assert validate_invalid_ownership_disposition({}, td)["result"] == "PASS"


def test_all_validators_pass_missing_register():
    """All V139-V142 handle missing register without crashing."""
    td = _make_repo_no_register()
    assert validate_found_issue_register_present({}, td)["result"] == "PASS"
    assert validate_issue_accounting_reconciles({}, td)["result"] == "PASS"
    assert validate_no_prose_only_findings({})["result"] == "PASS"
    assert validate_invalid_ownership_disposition({}, td)["result"] == "PASS"


# ---------------------------------------------------------------------------
# TC-FIOP-005: Section-21 Validators (V_VALIDATE_FI_*)
# ---------------------------------------------------------------------------

from governance_validators_found_issue import (  # noqa: E402
    validate_found_issue_task_closure_unaccounted,
    validate_found_issue_no_deleted_test_without_analysis,
    validate_found_issue_downstream_patch_while_upstream_defective,
    validate_found_issue_closure_without_verification,
    validate_found_issue_untaskcarded_in_final_report,
    validate_found_issue_no_fixture_edit_without_authority,
)


def test_vfi_task_closure_unaccounted_blocks_when_undisposed():
    """V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED: FAIL if undisposed issues at closure."""
    decl = {
        "worker_self_grade": "PASS",
        "found_issues": [{"issue_id": "FI-TEST", "disposition": None}],
    }
    r = validate_found_issue_task_closure_unaccounted(decl)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True


def test_vfi_task_closure_unaccounted_pass_when_all_disposed():
    """V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED: PASS when all issues disposed."""
    decl = {
        "worker_self_grade": "PASS",
        "found_issues": [{"issue_id": "FI-TEST", "disposition": "HEALED_AND_VERIFIED"}],
    }
    r = validate_found_issue_task_closure_unaccounted(decl)
    assert r["result"] == "PASS"


def test_vfi_no_deleted_test_pass_when_no_removed_tests():
    """V_VALIDATE_FI_NO_DELETED_TEST: PASS if no removed test files."""
    decl = {"changed_files": ["src/python/fods/models.py"]}
    r = validate_found_issue_no_deleted_test_without_analysis(decl)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_vfi_downstream_patch_warn_when_govblock_downstream_only():
    """V_VALIDATE_FI_DOWNSTREAM_PATCH: WARN if GOV_BLOCK present but only reports/ changed."""
    decl = {
        "rework_items": [{"validator": "GOV_BLOCK:monolith_detection_validator"}],
        "changed_files": ["reports/supervisor/next-sprint.md"],
    }
    r = validate_found_issue_downstream_patch_while_upstream_defective(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_vfi_downstream_patch_pass_when_upstream_changed():
    """V_VALIDATE_FI_DOWNSTREAM_PATCH: PASS if src/ files changed alongside GOV_BLOCK."""
    decl = {
        "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
        "changed_files": ["src/python/fods/models.py", "reports/supervisor/next-sprint.md"],
    }
    r = validate_found_issue_downstream_patch_while_upstream_defective(decl)
    assert r["result"] == "PASS"


def test_vfi_closure_no_verify_fails_when_missing_verdict(tmp_path):
    """V_VALIDATE_FI_CLOSURE_NO_VERIFY: FAIL if closed issue has no verification_verdict."""
    reg = tmp_path / "registry" / "found-issue-register.yaml"
    reg.parent.mkdir(parents=True)
    reg.write_text(
        "issues:\n"
        "  - issue_id: FI-X\n"
        "    disposition: HEALED_AND_VERIFIED\n"
        "    verification_verdict: null\n"
    )
    r = validate_found_issue_closure_without_verification({}, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True


def test_vfi_closure_no_verify_pass_when_verdict_present(tmp_path):
    """V_VALIDATE_FI_CLOSURE_NO_VERIFY: PASS if closed issue has verification_verdict."""
    reg = tmp_path / "registry" / "found-issue-register.yaml"
    reg.parent.mkdir(parents=True)
    reg.write_text(
        "issues:\n"
        "  - issue_id: FI-X\n"
        "    disposition: HEALED_AND_VERIFIED\n"
        "    verification_verdict: 'All tests PASS'\n"
    )
    r = validate_found_issue_closure_without_verification({}, tmp_path)
    assert r["result"] == "PASS"


def test_vfi_untaskcarded_report_warn_when_issue_lang_no_found_issues():
    """V_VALIDATE_FI_UNTASKCARDED_REPORT: WARN if issue language without found_issues."""
    decl = {"worker_self_verdict": "The test failed unexpectedly.", "found_issues": []}
    r = validate_found_issue_untaskcarded_in_final_report(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_vfi_untaskcarded_report_pass_when_found_issues_present():
    """V_VALIDATE_FI_UNTASKCARDED_REPORT: PASS if found_issues present."""
    decl = {
        "worker_self_verdict": "The test failed unexpectedly.",
        "found_issues": [{"issue_id": "FI-X", "disposition": "HEALED_AND_VERIFIED"}],
    }
    r = validate_found_issue_untaskcarded_in_final_report(decl)
    assert r["result"] == "PASS"


def test_vfi_fixture_edit_warn_when_fixture_changed_no_authority():
    """V_VALIDATE_FI_FIXTURE_EDIT: WARN if fixture file changed without authority."""
    decl = {"changed_files": ["tests/fods/fixtures/sample.yaml"]}
    r = validate_found_issue_no_fixture_edit_without_authority(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False


def test_vfi_fixture_edit_pass_when_found_issues_present():
    """V_VALIDATE_FI_FIXTURE_EDIT: PASS if found_issues present (authority established)."""
    decl = {
        "changed_files": ["tests/fods/fixtures/sample.yaml"],
        "found_issues": [{"issue_id": "FI-X"}],
    }
    r = validate_found_issue_no_fixture_edit_without_authority(decl)
    assert r["result"] == "PASS"
