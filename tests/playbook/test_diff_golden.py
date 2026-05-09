"""
test_diff_golden.py — Golden tests for diff_playbook_outputs.py (S-F2F-04).

Tests that the diff tool produces expected deterministic output for known
report pairs. Uses checked-in golden fixtures in tests/playbook/golden/.

Normalization:
- diff_generated_at is replaced with NORMALIZED_TIMESTAMP.
"""

import os
import sys
import subprocess

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIFF_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "diff_playbook_outputs.py")
GOLDEN_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "golden")
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "fixtures")

VALID_FODS = os.path.join(FIXTURE_DIR, "replay-valid-acquisition-playbook.yaml")
MISSING_INPUTS = os.path.join(FIXTURE_DIR, "replay-with-missing-inputs.yaml")

PYTHONPATH = os.environ.get(
    "PYTHONPATH",
    "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages",
)

_SENTINEL = "NORMALIZED_TIMESTAMP"


def _normalize_diff(diff: dict) -> dict:
    """Replace unstable fields in a diff report."""
    import copy
    d = copy.deepcopy(diff)
    if "diff_generated_at" in d:
        d["diff_generated_at"] = _SENTINEL
    return d


def _load_golden_yaml(filename: str) -> dict:
    path = os.path.join(GOLDEN_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_report(playbook_path: str, format_id: str) -> dict:
    """Run mode_dry_run and return the report dict."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
    from replay_acquisition_playbook import mode_dry_run
    schema = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")
    _, report = mode_dry_run(playbook_path, schema, format_id)
    return report


def _diff_yaml(actual: dict, expected: dict, label: str = "") -> str:
    import pprint
    if actual == expected:
        return ""
    return (
        f"\n--- ACTUAL {label} ---\n{pprint.pformat(actual)}"
        f"\n--- EXPECTED {label} ---\n{pprint.pformat(expected)}"
    )


# ---------------------------------------------------------------------------
# Test: golden fixtures exist
# ---------------------------------------------------------------------------
class TestDiffGoldenFixturesExist:
    def test_diff_unchanged_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "diff-unchanged.expected.yaml"))

    def test_diff_regression_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "diff-regression.expected.yaml"))

    def test_diff_improvement_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "diff-improvement.expected.yaml"))


# ---------------------------------------------------------------------------
# Test: diff UNCHANGED golden
# ---------------------------------------------------------------------------
class TestDiffUnchangedGolden:
    def test_identical_reports_match_golden(self):
        """Diff of identical reports matches UNCHANGED golden."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        report = _make_report(VALID_FODS, "fods")
        actual = _normalize_diff(diff_reports(report, report))
        expected = _load_golden_yaml("diff-unchanged.expected.yaml")
        diff = _diff_yaml(actual, expected, "diff-unchanged")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_diff_unchanged_is_deterministic(self):
        """Two runs of diff(same, same) produce identical results."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        report = _make_report(VALID_FODS, "fods")
        d1 = _normalize_diff(diff_reports(report, report))
        d2 = _normalize_diff(diff_reports(report, report))
        assert d1 == d2, "Diff must be deterministic"

    def test_diff_unchanged_exits_zero_via_cli(self, tmp_path):
        """CLI diff of identical files exits 0."""
        import tempfile
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        if "PYTHONPATH" not in env:
            env["PYTHONPATH"] = PYTHONPATH

        # Write two identical reports to temp files
        report = _make_report(VALID_FODS, "fods")
        report_path = tmp_path / "report.yaml"
        with open(report_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(report, f, default_flow_style=False, allow_unicode=True)

        result = subprocess.run(
            [sys.executable, DIFF_TOOL,
             "--baseline", str(report_path),
             "--current", str(report_path)],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env, timeout=30,
        )
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"


# ---------------------------------------------------------------------------
# Test: diff REGRESSION golden
# ---------------------------------------------------------------------------
class TestDiffRegressionGolden:
    def test_regression_matches_golden(self):
        """Diff of valid(baseline) vs missing-inputs(current) matches REGRESSION golden."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        baseline = _make_report(VALID_FODS, "fods")
        current = _make_report(MISSING_INPUTS, "fods")
        actual = _normalize_diff(diff_reports(baseline, current))
        expected = _load_golden_yaml("diff-regression.expected.yaml")
        diff = _diff_yaml(actual, expected, "diff-regression")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_regression_is_deterministic(self):
        """Regression diff is stable across two runs."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        baseline = _make_report(VALID_FODS, "fods")
        current = _make_report(MISSING_INPUTS, "fods")
        d1 = _normalize_diff(diff_reports(baseline, current))
        d2 = _normalize_diff(diff_reports(baseline, current))
        assert d1 == d2

    def test_regression_exits_nonzero_via_cli(self, tmp_path):
        """CLI diff of baseline=valid, current=missing-inputs exits non-zero (REGRESSION)."""
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        if "PYTHONPATH" not in env:
            env["PYTHONPATH"] = PYTHONPATH

        baseline_report = _make_report(VALID_FODS, "fods")
        current_report = _make_report(MISSING_INPUTS, "fods")

        baseline_path = tmp_path / "baseline.yaml"
        current_path = tmp_path / "current.yaml"
        import yaml
        with open(baseline_path, "w", encoding="utf-8") as f:
            yaml.dump(baseline_report, f, default_flow_style=False)
        with open(current_path, "w", encoding="utf-8") as f:
            yaml.dump(current_report, f, default_flow_style=False)

        result = subprocess.run(
            [sys.executable, DIFF_TOOL,
             "--baseline", str(baseline_path),
             "--current", str(current_path)],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env, timeout=30,
        )
        assert result.returncode != 0, f"Expected non-zero for REGRESSION, got {result.returncode}"
        assert "REGRESSION" in result.stdout


# ---------------------------------------------------------------------------
# Test: diff IMPROVEMENT golden
# ---------------------------------------------------------------------------
class TestDiffImprovementGolden:
    def test_improvement_matches_golden(self):
        """Diff of missing-inputs(baseline) vs valid(current) matches IMPROVEMENT golden."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        baseline = _make_report(MISSING_INPUTS, "fods")
        current = _make_report(VALID_FODS, "fods")
        actual = _normalize_diff(diff_reports(baseline, current))
        expected = _load_golden_yaml("diff-improvement.expected.yaml")
        diff = _diff_yaml(actual, expected, "diff-improvement")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_improvement_is_deterministic(self):
        """Improvement diff is stable across two runs."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import diff_reports

        baseline = _make_report(MISSING_INPUTS, "fods")
        current = _make_report(VALID_FODS, "fods")
        d1 = _normalize_diff(diff_reports(baseline, current))
        d2 = _normalize_diff(diff_reports(baseline, current))
        assert d1 == d2


# ---------------------------------------------------------------------------
# Test: unsafe output path for diff tool
# ---------------------------------------------------------------------------
class TestDiffUnsafeOutputPath:
    def test_diff_output_rejects_committed_repo_path(self):
        """_guard_output_path in diff tool must reject committed repo paths."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from diff_playbook_outputs import _guard_output_path

        for prefix in ["tools", "schemas", "plans", "tests"]:
            bad_path = os.path.join(REPO_ROOT, prefix, "bad-diff.yaml")
            with pytest.raises(SystemExit) as exc_info:
                _guard_output_path(bad_path)
            assert exc_info.value.code == 2
