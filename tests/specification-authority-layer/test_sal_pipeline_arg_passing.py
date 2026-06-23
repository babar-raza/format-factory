"""Regression tests for run_spec_pipeline.py build_spec_workbench argument construction.

TC-SAL-PIPE-REGR-001 (2026-06-23): Prevents reintroduction of the empty-string positional
argument bug fixed in commit 0feffaf7.

Root cause: `"--dry-run" if dry_run else ""` passed an empty string `""` as a positional
argument to build_spec_workbench.py when dry_run=False.  argparse rejected it with
"unrecognized arguments: " (exit 2 / WARN) on every live pipeline run.

Fix pattern: `if dry_run: _workbench_cmd.append("--dry-run")` — conditional append only.

Tests verify the exact command list passed to subprocess.run for the build_spec_workbench
step under both dry_run=False (no empty string) and dry_run=True (--dry-run present).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "specification-authority-layer"))


def _captured_workbench_cmds(dry_run: bool) -> list[list]:
    """Run run_pipeline_for_format under mock and return all captured subprocess.run calls."""
    import run_spec_pipeline as rsp

    captured: list[list] = []

    def fake_run(cmd, **kwargs):
        captured.append(list(cmd))
        m = MagicMock()
        m.returncode = 0
        return m

    with patch.object(rsp.subprocess, "run", side_effect=fake_run):
        rsp.run_pipeline_for_format("fods", dry_run=dry_run)

    return captured


def _find_workbench_call(calls: list[list]) -> list | None:
    """Find the build_spec_workbench.py call in the captured subprocess calls."""
    for cmd in calls:
        if any("build_spec_workbench" in str(arg) for arg in cmd):
            return cmd
    return None


class TestSALPipelineArgPassing:
    """TC-SAL-PIPE-REGR-001: build_spec_workbench command must not contain empty-string arguments."""

    def test_live_mode_no_empty_string_in_workbench_cmd(self) -> None:
        """dry_run=False: build_spec_workbench command must NOT contain '' as any element.

        Regression guard: the old bug passed `"--dry-run" if dry_run else ""` which
        added "" to the command list when dry_run=False.
        """
        calls = _captured_workbench_cmds(dry_run=False)
        workbench_cmd = _find_workbench_call(calls)
        assert workbench_cmd is not None, (
            "build_spec_workbench.py was not called by run_pipeline_for_format. "
            "Step 3 may have been removed or renamed."
        )
        assert "" not in workbench_cmd, (
            f"Empty string found in build_spec_workbench command (regression: TC-SAL-PIPE-BUG-001). "
            f"Command: {workbench_cmd}"
        )
        assert "--dry-run" not in workbench_cmd, (
            f"--dry-run should NOT be present in live (dry_run=False) run. "
            f"Command: {workbench_cmd}"
        )

    def test_dry_run_mode_appends_dry_run_flag(self) -> None:
        """dry_run=True: build_spec_workbench command must include '--dry-run' as an element.

        Confirms that the conditional append path (if dry_run: append --dry-run) works.
        """
        calls = _captured_workbench_cmds(dry_run=True)
        workbench_cmd = _find_workbench_call(calls)
        assert workbench_cmd is not None, (
            "build_spec_workbench.py was not called by run_pipeline_for_format in dry_run=True mode."
        )
        assert "--dry-run" in workbench_cmd, (
            f"--dry-run must be appended to build_spec_workbench command when dry_run=True. "
            f"Command: {workbench_cmd}"
        )
        assert "" not in workbench_cmd, (
            f"Empty string must never appear in build_spec_workbench command. "
            f"Command: {workbench_cmd}"
        )

    def test_source_file_does_not_contain_old_buggy_pattern(self) -> None:
        """Static assertion: run_spec_pipeline.py must not contain the old empty-string pattern.

        Checks that `"--dry-run" if dry_run else ""` is absent from the workbench command
        construction code. This is a static guard against reintroduction via a refactor.
        """
        source_path = REPO_ROOT / "tools" / "specification-authority-layer" / "run_spec_pipeline.py"
        assert source_path.exists(), f"run_spec_pipeline.py not found at {source_path}"
        source = source_path.read_text(encoding="utf-8")
        # The old buggy pattern: a ternary that evaluates to "" as a positional arg
        # We check specifically for the empty string in a conditional that feeds a workbench cmd
        lines_with_empty_ternary = [
            line.strip() for line in source.splitlines()
            if '"--dry-run" if dry_run else ""' in line
            or "if dry_run else \"\"" in line
        ]
        assert not lines_with_empty_ternary, (
            f"Regression: found empty-string ternary pattern in run_spec_pipeline.py. "
            f"Lines: {lines_with_empty_ternary}"
        )
