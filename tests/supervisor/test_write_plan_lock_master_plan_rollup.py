"""TC-S6P4-SYS-004 (select-6 Phase 4): master-plan rollup check.

Closes SF4: plan closure previously had zero verification that
plans/master-plan.md reflects what a closing plan built.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SUPERVISOR = Path(__file__).resolve().parents[2] / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from write_plan_lock import _check_master_plan_rollup  # noqa: E402


def _setup(tmp_path, format_ids, plan_text, master_text):
    (tmp_path / "registry").mkdir(parents=True, exist_ok=True)
    import yaml
    (tmp_path / "registry" / "format-registry.yaml").write_text(
        yaml.safe_dump({"formats": [{"format_id": f} for f in format_ids]}),
        encoding="utf-8")
    (tmp_path / "plans").mkdir(parents=True, exist_ok=True)
    (tmp_path / "plans" / "master-plan.md").write_text(master_text, encoding="utf-8")
    plan_dir = tmp_path / "plans" / ".claude"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "test-plan.md").write_text(plan_text, encoding="utf-8")
    return "plans/.claude/test-plan.md"


class TestMasterPlanRollupCheck:
    def test_mentioned_format_absent_from_master_plan_warns(self, tmp_path):
        rel = _setup(tmp_path, ["newfmt"], "Work on newfmt is complete.", "unrelated content")
        warnings = _check_master_plan_rollup(rel, tmp_path)
        assert len(warnings) == 1
        assert "newfmt" in warnings[0]

    def test_mentioned_format_present_in_master_plan_no_warning(self, tmp_path):
        rel = _setup(tmp_path, ["newfmt"], "Work on newfmt is complete.",
                    "## newfmt status: done")
        warnings = _check_master_plan_rollup(rel, tmp_path)
        assert warnings == []

    def test_format_not_mentioned_in_plan_no_warning(self, tmp_path):
        rel = _setup(tmp_path, ["newfmt", "other"], "This plan is about other only.",
                    "unrelated")
        warnings = _check_master_plan_rollup(rel, tmp_path)
        assert len(warnings) == 1
        assert "other" in warnings[0]

    def test_word_boundary_avoids_false_positive(self, tmp_path):
        # 'csv' must not match inside 'csvkit' in the plan text.
        rel = _setup(tmp_path, ["csv"], "We use csvkit for something unrelated.", "")
        warnings = _check_master_plan_rollup(rel, tmp_path)
        assert warnings == []

    def test_missing_registry_returns_empty_not_raises(self, tmp_path):
        (tmp_path / "plans" / ".claude").mkdir(parents=True)
        (tmp_path / "plans" / ".claude" / "p.md").write_text("x", encoding="utf-8")
        (tmp_path / "plans" / "master-plan.md").write_text("y", encoding="utf-8")
        assert _check_master_plan_rollup("plans/.claude/p.md", tmp_path) == []

    def test_missing_plan_file_returns_empty_not_raises(self, tmp_path):
        assert _check_master_plan_rollup("plans/.claude/nonexistent.md", tmp_path) == []

    def test_real_select6_plan_text_reproduces_m3_finding_against_empty_master_plan(
        self, tmp_path
    ):
        """Regression proof (rewritten TC-S6P4-FINAL-001d, select-6 Phase 4
        final re-audit, 2026-07-16): the original version of this test
        asserted against the LIVE plans/master-plan.md, expecting it to
        still be missing all 6 select-6 format mentions -- the exact M3
        finding. TC-S6P4-PROD-010 subsequently added master-plan.md Section
        107 to legitimately close M3, which made the live-repo assertion
        false for the right reason (the fix landed) but fail the test for
        the wrong one (looks like a regression). A replay proof must not
        depend on live state a later, legitimate fix is expected to change.

        This rewrite keeps the real plan file's actual text (frozen -- the
        select-6 plan's own body isn't rewritten by this fix) but pairs it
        with a synthetic, empty master-plan.md via _setup(), so the
        mechanism is proven directly without depending on whether the real
        master-plan.md currently mentions the 6 formats or not."""
        repo = Path(__file__).resolve().parents[2]
        real_plan_path = repo / "plans" / ".claude" / "put-the-select-6-snappy-dijkstra.md"
        if not real_plan_path.exists():
            pytest.skip("select-6 plan file not present in this checkout")
        plan_text = real_plan_path.read_text(encoding="utf-8")
        rel = _setup(
            tmp_path,
            ["ipynb", "safetensors", "xliff", "nrrd", "ubl", "mtlx"],
            plan_text,
            "unrelated master-plan content with no format mentions",
        )
        warnings = _check_master_plan_rollup(rel, tmp_path)
        found = {w.split("'")[1] for w in warnings}
        assert {"ipynb", "safetensors", "xliff", "nrrd", "ubl", "mtlx"} <= found, (
            "the real select-6 plan text no longer mentions all 6 format_ids by name -- "
            "verify the plan file wasn't accidentally truncated"
        )

    def test_live_repo_select6_rollup_now_closed(self):
        """Companion proof: against the REAL, current master-plan.md, the
        select-6 plan must now produce NO format-mention warnings --
        TC-S6P4-PROD-010 added Section 107 specifically to close M3, and
        this is the live confirmation that it stayed closed."""
        repo = Path(__file__).resolve().parents[2]
        real_plan_path = repo / "plans" / ".claude" / "put-the-select-6-snappy-dijkstra.md"
        if not real_plan_path.exists():
            pytest.skip("select-6 plan file not present in this checkout")
        warnings = _check_master_plan_rollup(
            "plans/.claude/put-the-select-6-snappy-dijkstra.md", repo)
        found = {w.split("'")[1] for w in warnings if "'" in w}
        select6 = {"ipynb", "safetensors", "xliff", "nrrd", "ubl", "mtlx"}
        assert not (select6 & found), (
            f"M3 has regressed -- these select-6 formats are once again missing from "
            f"plans/master-plan.md: {select6 & found}"
        )
