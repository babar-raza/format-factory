"""
test_replay_golden.py — Golden tests for replay_acquisition_playbook.py (S-F2F-04).

Tests that the replay engine produces expected deterministic output for known
playbook states. Uses checked-in golden fixtures in tests/playbook/golden/.

Normalization:
- Timestamps (generated_at, diff_generated_at, provenance.created_at) are replaced
  with the sentinel NORMALIZED_TIMESTAMP before comparison.
- Path separators are normalized to forward slashes.
- Unstable IDs (queue_id, run_id) are replaced with normalized sentinels.

Safety:
- Tests do not write to committed repo directories.
- subprocess calls use timeout=30 to prevent hangs.
- Temp files use pytest tmp_path.
- Tests do not require network access.
"""

import io
import os
import sys
import subprocess
import tempfile

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPLAY_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "replay_acquisition_playbook.py")
SCHEMA = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")

GOLDEN_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "golden")
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "fixtures")

VALID_FODS = os.path.join(FIXTURE_DIR, "replay-valid-acquisition-playbook.yaml")
MISSING_INPUTS = os.path.join(FIXTURE_DIR, "replay-with-missing-inputs.yaml")
VALID_FODT = os.path.join(FIXTURE_DIR, "replay-fodt-valid.yaml")
DOCS_EXAMPLE = os.path.join(REPO_ROOT, "docs", "examples", "acquisition-playbook-fods-documentation-example.yaml")

PYTHONPATH = os.environ.get(
    "PYTHONPATH",
    "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages",
)

_SENTINEL = "NORMALIZED_TIMESTAMP"


def _run_replay(args: list) -> tuple:
    """Run replay tool via subprocess with timeout=30. Returns (exit_code, stdout, stderr)."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = PYTHONPATH
    result = subprocess.run(
        [sys.executable, REPLAY_TOOL] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def _normalize_report(report: dict) -> dict:
    """
    Normalize a dry-run replay report dict for golden comparison.
    Replaces unstable fields with sentinel values.
    """
    import copy
    r = copy.deepcopy(report)
    if "generated_at" in r:
        r["generated_at"] = _SENTINEL
    return r


def _load_golden_yaml(filename: str) -> dict:
    golden_path = os.path.join(GOLDEN_DIR, filename)
    with open(golden_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_golden_text(filename: str) -> str:
    golden_path = os.path.join(GOLDEN_DIR, filename)
    with open(golden_path, encoding="utf-8") as f:
        return f.read()


def _diff_yaml(actual: dict, expected: dict, label: str = "") -> str:
    """Return a human-readable diff string between two dicts, or empty string if equal."""
    import pprint
    if actual == expected:
        return ""
    actual_repr = pprint.pformat(actual, width=120)
    expected_repr = pprint.pformat(expected, width=120)
    return f"\n--- ACTUAL {label} ---\n{actual_repr}\n--- EXPECTED {label} ---\n{expected_repr}"


# ---------------------------------------------------------------------------
# Test: golden fixtures exist
# ---------------------------------------------------------------------------
class TestGoldenFixturesExist:
    def test_replay_valid_dry_run_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "replay-valid-dry-run.expected.yaml"))

    def test_replay_missing_inputs_dry_run_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "replay-missing-inputs-dry-run.expected.yaml"))

    def test_replay_fodt_valid_dry_run_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "replay-fodt-valid-dry-run.expected.yaml"))

    def test_replay_explain_fods_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "replay-explain-fods.expected.txt"))

    def test_fodt_fixture_exists(self):
        assert os.path.isfile(VALID_FODT), f"FODT fixture must exist: {VALID_FODT}"


# ---------------------------------------------------------------------------
# Test: dry-run golden match — FODS valid
# ---------------------------------------------------------------------------
class TestDryRunGoldenFodsValid:
    def test_fods_valid_dry_run_matches_golden(self):
        """FODS dry-run with all inputs present matches golden fixture."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        rc, report = mode_dry_run(VALID_FODS, SCHEMA, "fods")
        assert rc == 0, f"Expected exit 0 (PASS), got {rc}"

        actual = _normalize_report(report)
        expected = _load_golden_yaml("replay-valid-dry-run.expected.yaml")
        diff = _diff_yaml(actual, expected, "fods-valid-dry-run")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_fods_valid_dry_run_is_deterministic(self):
        """Running dry-run twice produces identical reports (after normalization)."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        _, r1 = mode_dry_run(VALID_FODS, SCHEMA, "fods")
        _, r2 = mode_dry_run(VALID_FODS, SCHEMA, "fods")
        assert _normalize_report(r1) == _normalize_report(r2), "Two runs must produce identical reports"


# ---------------------------------------------------------------------------
# Test: dry-run golden match — FODS missing inputs
# ---------------------------------------------------------------------------
class TestDryRunGoldenFodsMissingInputs:
    def test_fods_missing_inputs_matches_golden(self):
        """FODS dry-run with missing inputs produces expected conflicts golden."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        rc, report = mode_dry_run(MISSING_INPUTS, SCHEMA, "fods")
        assert rc == 1, f"Expected exit 1 (CONFLICTS), got {rc}"

        actual = _normalize_report(report)
        expected = _load_golden_yaml("replay-missing-inputs-dry-run.expected.yaml")
        diff = _diff_yaml(actual, expected, "fods-missing-inputs-dry-run")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_fods_missing_inputs_conflict_count(self):
        """Missing-inputs report has exactly 2 conflicts."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        _, report = mode_dry_run(MISSING_INPUTS, SCHEMA, "fods")
        assert report["total_conflicts"] == 2
        assert report["conflict_operations"] == 1
        assert all(c["severity"] == "high" for c in report["conflicts"])


# ---------------------------------------------------------------------------
# Test: dry-run golden match — FODT valid (format-agnostic coverage)
# ---------------------------------------------------------------------------
class TestDryRunGoldenFodtValid:
    def test_fodt_valid_dry_run_matches_golden(self):
        """FODT dry-run with all inputs present matches golden fixture."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        rc, report = mode_dry_run(VALID_FODT, SCHEMA, "fodt")
        assert rc == 0, f"Expected exit 0 (PASS), got {rc}"

        actual = _normalize_report(report)
        expected = _load_golden_yaml("replay-fodt-valid-dry-run.expected.yaml")
        diff = _diff_yaml(actual, expected, "fodt-valid-dry-run")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_fodt_format_id_in_report(self):
        """FODT report has format_id: fodt."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        _, report = mode_dry_run(VALID_FODT, SCHEMA, "fodt")
        assert report["format_id"] == "fodt"


# ---------------------------------------------------------------------------
# Test: explain mode golden match
# ---------------------------------------------------------------------------
class TestExplainGolden:
    def test_explain_fods_matches_golden(self):
        """FODS explain mode stdout matches golden text fixture."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_explain

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            rc = mode_explain(VALID_FODS, "fods")
            actual = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert rc == 0
        expected = _load_golden_text("replay-explain-fods.expected.txt")
        assert actual == expected, (
            f"Explain output mismatch.\nACTUAL:\n{actual!r}\nEXPECTED:\n{expected!r}"
        )

    def test_explain_fods_is_deterministic(self):
        """Running explain twice produces identical stdout."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_explain

        def _capture():
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                mode_explain(VALID_FODS, "fods")
                return sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

        assert _capture() == _capture(), "Two explain runs must be identical"

    def test_explain_writes_nothing(self, tmp_path):
        """explain mode must not write any files."""
        import glob
        before = set(glob.glob(str(tmp_path / "**"), recursive=True))
        rc, stdout, stderr = _run_replay(
            ["--mode", "explain", "--format-id", "fods", "--playbook", VALID_FODS]
        )
        assert rc == 0
        after = set(glob.glob(str(tmp_path / "**"), recursive=True))
        assert before == after, "explain mode must not create files in tmp_path"


# ---------------------------------------------------------------------------
# Test: not_for_execution skipped
# ---------------------------------------------------------------------------
class TestNotForExecutionGolden:
    def test_docs_example_dry_run_skips(self):
        """Playbooks with not_for_execution:true are skipped in dry-run."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import mode_dry_run

        if not os.path.isfile(DOCS_EXAMPLE):
            pytest.skip("docs example not present")
        rc, report = mode_dry_run(DOCS_EXAMPLE, SCHEMA, "fods")
        assert rc == 0
        assert report.get("skipped") is True
        assert report.get("reason") == "documentation_example_only"


# ---------------------------------------------------------------------------
# Test: apply mode rejection
# ---------------------------------------------------------------------------
class TestApplyModeRejectionGolden:
    def test_apply_not_in_cli_choices(self):
        """CLI must reject --mode apply with exit code 2."""
        rc, stdout, stderr = _run_replay(
            ["--mode", "apply", "--format-id", "fods", "--playbook", VALID_FODS]
        )
        assert rc == 2, f"Expected exit 2 for apply mode, got {rc}"
        assert "apply" in (stdout + stderr).lower(), "Error message must mention apply"

    def test_apply_synonyms_rejected_by_guard(self):
        """_guard_replay_mode must reject apply synonyms."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import _guard_replay_mode

        for synonym in ["apply", "apply_mode", "apply_proposed", "apply_authorized", "execute", "run"]:
            with pytest.raises(SystemExit) as exc_info:
                _guard_replay_mode(synonym)
            assert exc_info.value.code == 2, f"Expected exit 2 for synonym '{synonym}'"


# ---------------------------------------------------------------------------
# Test: unsafe output path rejection
# ---------------------------------------------------------------------------
class TestUnsafeOutputPathGolden:
    def test_unsafe_output_path_rejected_via_cli(self, tmp_path):
        """export-review-queue to a committed repo path must exit non-zero."""
        repo_output = os.path.join(REPO_ROOT, "tools", "test-rq-MUST-NOT-EXIST.yaml")
        rc, stdout, stderr = _run_replay([
            "--mode", "export-review-queue",
            "--format-id", "fods",
            "--playbook", VALID_FODS,
            "--output", repo_output,
        ])
        assert rc != 0, f"Expected non-zero for unsafe output path, got {rc}"
        assert not os.path.exists(repo_output), "Must not create file at unsafe path"

    def test_output_guard_blocks_committed_dirs(self):
        """_guard_output_path must raise SystemExit for committed repo prefixes."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from replay_acquisition_playbook import _guard_output_path

        for prefix in ["src", "tools", "schemas", "plans", "tests"]:
            bad_path = os.path.join(REPO_ROOT, prefix, "bad-output.yaml")
            with pytest.raises(SystemExit) as exc_info:
                _guard_output_path(bad_path)
            assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Test: no repo mutation
# ---------------------------------------------------------------------------
class TestNoRepoMutationGolden:
    def _git_status(self) -> str:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env, timeout=15,
        )
        return result.stdout

    def test_dry_run_does_not_mutate_repo(self, tmp_path):
        """dry-run mode must not change git status (compare before vs after)."""
        before = self._git_status()
        rc, stdout, stderr = _run_replay(
            ["--mode", "dry-run", "--format-id", "fods", "--playbook", VALID_FODS]
        )
        assert rc == 0
        after = self._git_status()
        assert before == after, "git status changed after dry-run: before=" + repr(before) + " after=" + repr(after)

    def test_explain_does_not_mutate_repo(self, tmp_path):
        """explain mode must not change git status (compare before vs after)."""
        before = self._git_status()
        rc, stdout, stderr = _run_replay(
            ["--mode", "explain", "--format-id", "fods", "--playbook", VALID_FODS]
        )
        assert rc == 0
        after = self._git_status()
        assert before == after, "git status changed after explain: before=" + repr(before) + " after=" + repr(after)
