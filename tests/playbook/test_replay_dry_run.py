"""
test_replay_dry_run.py — Tests for replay_acquisition_playbook.py (S-F2F-03).

Sprint: S-F2F-03 (Dry-Run Replay and Review Queue Export)
Scope: validate, dry-run, explain, export-review-queue modes.
       Apply mode must be rejected.
       No file writes to repo directories.
       Format-agnostic: tests use --format-id fods and --format-id fodt.
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPLAY_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "replay_acquisition_playbook.py")
SCHEMA = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")
DOCS_EXAMPLE = os.path.join(
    REPO_ROOT, "docs", "examples", "acquisition-playbook-fods-documentation-example.yaml"
)
VALID_FIXTURE = os.path.join(
    REPO_ROOT, "tests", "playbook", "fixtures", "replay-valid-acquisition-playbook.yaml"
)
MISSING_INPUT_FIXTURE = os.path.join(
    REPO_ROOT, "tests", "playbook", "fixtures", "replay-with-missing-inputs.yaml"
)
PYTHONPATH = os.environ.get(
    "PYTHONPATH",
    "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages",
)


def run_replay(args: list[str]) -> tuple[int, str, str]:
    """Run replay_acquisition_playbook.py with given args. Returns (exit_code, stdout, stderr)."""
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
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Tool existence checks
# ---------------------------------------------------------------------------
class TestToolExists:
    def test_replay_tool_exists(self):
        assert os.path.isfile(REPLAY_TOOL), f"Replay tool must exist: {REPLAY_TOOL}"

    def test_replay_tool_is_python(self):
        with open(REPLAY_TOOL, encoding="utf-8") as f:
            content = f.read()
        assert content.strip(), "Replay tool must not be empty"
        # Parse as valid Python
        ast.parse(content)

    def test_fixtures_exist(self):
        assert os.path.isfile(VALID_FIXTURE), f"Valid fixture must exist: {VALID_FIXTURE}"
        assert os.path.isfile(MISSING_INPUT_FIXTURE), (
            f"Missing-input fixture must exist: {MISSING_INPUT_FIXTURE}"
        )


# ---------------------------------------------------------------------------
# Apply mode guard
# ---------------------------------------------------------------------------
class TestApplyModeRejected:
    def test_apply_mode_not_in_choices(self):
        """replay_acquisition_playbook.py --help must not list 'apply' as a valid mode."""
        rc, stdout, stderr = run_replay(["--help"])
        combined = stdout + stderr
        assert "apply" not in combined.lower() or "apply mode is NOT" in combined, (
            "If 'apply' appears in help, it must be in a rejection message only. "
            f"Got: {combined[:500]}"
        )

    def test_apply_not_in_mode_choices(self):
        """argparse choices for --mode must not include 'apply'."""
        rc, stdout, stderr = run_replay(["--mode", "apply", "--format-id", "fods",
                                         "--playbook", DOCS_EXAMPLE])
        assert rc != 0, "Passing --mode apply must exit non-zero"

    def test_apply_mode_not_in_source(self):
        """replay_acquisition_playbook.py must not define an apply mode IMPLEMENTATION.
        Guard/rejection functions (e.g. _reject_apply_mode) are allowed.
        Implementation-style names (mode_apply, apply_mode, do_apply, execute_apply) are not.
        """
        with open(REPLAY_TOOL, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        # Only forbid names that indicate an apply-mode implementation, not guards
        forbidden_apply_patterns = [
            "mode_apply", "apply_mode", "do_apply",
            "execute_apply", "run_apply", "apply_proposed", "apply_authorized",
        ]
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name.lower()
                for pattern in forbidden_apply_patterns:
                    assert pattern not in name, (
                        f"Found apply mode implementation function: {node.name}. "
                        "Apply mode must not be implemented (S-F2F-06 not authorized)."
                    )

    def test_apply_not_in_argparse_choices(self):
        """Argparse choices for --mode in source must not contain 'apply'."""
        with open(REPLAY_TOOL, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = getattr(node, "func", None)
                if func and getattr(func, "attr", None) == "add_argument":
                    for kw in node.keywords:
                        if kw.arg == "choices" and isinstance(kw.value, ast.List):
                            choices = [
                                elt.value for elt in kw.value.elts
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                            ]
                            for choice in choices:
                                assert "apply" not in choice.lower(), (
                                    f"Found 'apply' in argparse choices: {choices}. "
                                    "Apply mode must not be an allowed choice."
                                )


# ---------------------------------------------------------------------------
# Mode: validate
# ---------------------------------------------------------------------------
class TestValidateMode:
    def test_validate_docs_example_pass(self):
        """Validate mode passes on the docs documentation example."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fods",
            "--playbook", DOCS_EXAMPLE,
        ])
        assert rc == 0, f"validate mode should exit 0 for valid playbook. stderr={stderr}"
        assert "REPLAY_VALIDATE: PASS" in stdout

    def test_validate_valid_fixture_pass(self):
        """Validate mode passes on the valid test fixture."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc == 0, f"validate on valid fixture should pass. stderr={stderr}"
        assert "REPLAY_VALIDATE: PASS" in stdout

    def test_validate_missing_input_fixture_pass(self):
        """Validate mode passes on missing-input fixture (valid schema, file absence detected in dry-run)."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fods",
            "--playbook", MISSING_INPUT_FIXTURE,
        ])
        assert rc == 0, f"validate on missing-input fixture schema should pass. stderr={stderr}"
        assert "REPLAY_VALIDATE: PASS" in stdout

    def test_validate_format_id_mismatch_fails(self):
        """Validate mode fails if --format-id doesn't match playbook format_id."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fodt",  # playbook is fods
            "--playbook", DOCS_EXAMPLE,
        ])
        assert rc != 0
        assert "REPLAY_VALIDATE: FAIL" in stdout

    def test_validate_nonexistent_file_fails(self):
        """Validate mode exits non-zero for missing playbook file."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fods",
            "--playbook", "this/file/does/not/exist.yaml",
        ])
        assert rc != 0


# ---------------------------------------------------------------------------
# Mode: dry-run
# ---------------------------------------------------------------------------
class TestDryRunMode:
    def test_dry_run_docs_example_skips(self):
        """Dry-run skips documentation_example_only playbooks."""
        rc, stdout, stderr = run_replay([
            "--mode", "dry-run",
            "--format-id", "fods",
            "--playbook", DOCS_EXAMPLE,
        ])
        assert rc == 0, f"dry-run on docs example should exit 0 (skip). stderr={stderr}"
        assert "SKIP" in stdout or "not_for_execution" in stdout

    def test_dry_run_valid_fixture_passes(self):
        """Dry-run passes when all required inputs exist."""
        rc, stdout, stderr = run_replay([
            "--mode", "dry-run",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc == 0, f"dry-run on valid fixture should pass. stdout={stdout} stderr={stderr}"
        assert "REPLAY_DRY_RUN: PASS" in stdout

    def test_dry_run_missing_inputs_produces_conflicts(self):
        """Dry-run detects conflicts when required inputs are absent."""
        rc, stdout, stderr = run_replay([
            "--mode", "dry-run",
            "--format-id", "fods",
            "--playbook", MISSING_INPUT_FIXTURE,
        ])
        assert rc != 0, f"dry-run on missing-input fixture should exit non-zero. stdout={stdout}"
        assert "CONFLICTS" in stdout

    def test_dry_run_writes_no_repo_files(self):
        """Dry-run must not write any files to the repo directory."""
        import time
        before_mtime = {}
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            # Skip hidden dirs and .local/
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in ("__pycache__",)
            ]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                try:
                    before_mtime[fp] = os.path.getmtime(fp)
                except OSError:
                    pass

        run_replay([
            "--mode", "dry-run",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])

        new_files = []
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in ("__pycache__",)
            ]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                if fp not in before_mtime:
                    new_files.append(fp)

        assert not new_files, f"dry-run wrote new files to repo: {new_files}"

    def test_dry_run_format_id_mismatch_fails(self):
        """Dry-run fails if --format-id doesn't match playbook format_id."""
        rc, stdout, stderr = run_replay([
            "--mode", "dry-run",
            "--format-id", "fodt",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc != 0
        assert "REPLAY_DRY_RUN: FAIL" in stdout


# ---------------------------------------------------------------------------
# Mode: explain
# ---------------------------------------------------------------------------
class TestExplainMode:
    def test_explain_docs_example(self):
        """Explain mode prints operation descriptions for docs example."""
        rc, stdout, stderr = run_replay([
            "--mode", "explain",
            "--format-id", "fods",
            "--playbook", DOCS_EXAMPLE,
        ])
        assert rc == 0, f"explain should exit 0. stderr={stderr}"
        assert "PLAYBOOK_ID" in stdout
        assert "FORMAT_ID" in stdout
        assert "REPLAY_EXPLAIN: DONE" in stdout

    def test_explain_valid_fixture(self):
        """Explain mode works on the valid test fixture."""
        rc, stdout, stderr = run_replay([
            "--mode", "explain",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc == 0, f"explain on valid fixture should pass. stderr={stderr}"
        assert "Operation 1" in stdout
        assert "REPLAY_EXPLAIN: DONE" in stdout

    def test_explain_writes_nothing(self):
        """Explain mode does not write files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, stdout, stderr = run_replay([
                "--mode", "explain",
                "--format-id", "fods",
                "--playbook", DOCS_EXAMPLE,
            ])
        # If explain wrote to tmpdir, it would appear in stdout. It should not.
        assert "OUTPUT" not in stdout or "REVIEW_QUEUE_OUTPUT" not in stdout


# ---------------------------------------------------------------------------
# Mode: export-review-queue
# ---------------------------------------------------------------------------
class TestExportReviewQueueMode:
    def test_export_review_queue_docs_example_skips(self):
        """export-review-queue skips documentation_example playbooks."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            tmp_path = f.name
        try:
            rc, stdout, stderr = run_replay([
                "--mode", "export-review-queue",
                "--format-id", "fods",
                "--playbook", DOCS_EXAMPLE,
                "--output", tmp_path,
            ])
            assert rc == 0
            assert "SKIP" in stdout
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_review_queue_valid_produces_empty_queue(self):
        """export-review-queue produces a valid empty queue for a no-conflict playbook."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            tmp_path = f.name
        try:
            rc, stdout, stderr = run_replay([
                "--mode", "export-review-queue",
                "--format-id", "fods",
                "--playbook", VALID_FIXTURE,
                "--output", tmp_path,
            ])
            assert rc == 0, f"export-review-queue on valid fixture should pass. stdout={stdout}"
            assert "PASS" in stdout

            with open(tmp_path, encoding="utf-8") as f:
                queue = yaml.safe_load(f)

            assert queue["schema_version"] == "1.0"
            assert queue["source_format_id"] == "fods"
            assert queue["summary"]["total_items"] == 0
            assert queue["governance"]["cannot_approve_gates"] is True
            assert queue["governance"]["high_severity_blocks_apply"] is True
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_review_queue_conflicts_produces_items(self):
        """export-review-queue produces conflict items for a missing-input playbook."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            tmp_path = f.name
        try:
            rc, stdout, stderr = run_replay([
                "--mode", "export-review-queue",
                "--format-id", "fods",
                "--playbook", MISSING_INPUT_FIXTURE,
                "--output", tmp_path,
            ])
            assert rc != 0, "export-review-queue with conflicts should exit non-zero"
            assert "CONFLICTS" in stdout

            with open(tmp_path, encoding="utf-8") as f:
                queue = yaml.safe_load(f)

            assert queue["summary"]["total_items"] > 0
            assert queue["summary"]["open_items"] > 0
            # Governance block is always present
            assert queue["governance"]["cannot_approve_gates"] is True
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_review_queue_output_required(self):
        """export-review-queue exits non-zero if --output is missing."""
        rc, stdout, stderr = run_replay([
            "--mode", "export-review-queue",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc != 0

    def test_export_review_queue_rejects_repo_output_path(self):
        """export-review-queue rejects --output paths inside committed repo directories."""
        bad_output = os.path.join(REPO_ROOT, "tools", "playbook", "bad-output.yaml")
        rc, stdout, stderr = run_replay([
            "--mode", "export-review-queue",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
            "--output", bad_output,
        ])
        assert rc != 0
        assert "REPLAY_ERROR" in stderr or "targets a committed repo" in stderr

    def test_export_review_queue_schema_compliance(self):
        """Queue output conforms to review-queue.schema.json required fields."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            tmp_path = f.name
        try:
            run_replay([
                "--mode", "export-review-queue",
                "--format-id", "fods",
                "--playbook", MISSING_INPUT_FIXTURE,
                "--output", tmp_path,
            ])
            with open(tmp_path, encoding="utf-8") as f:
                queue = yaml.safe_load(f)

            required_top = [
                "schema_version", "queue_id", "run_id", "generated_at",
                "source_playbook_id", "source_format_id", "items", "summary", "governance",
            ]
            for field in required_top:
                assert field in queue, f"Missing required field in queue: {field}"

            assert queue["governance"]["cannot_approve_gates"] is True
            assert queue["governance"]["cannot_replace_dec034"] is True
            assert queue["governance"]["high_severity_blocks_apply"] is True

            for item in queue["items"]:
                required_item = [
                    "item_id", "format_id", "gate", "operation_id", "target_path",
                    "issue_type", "severity", "deterministic_failure_reason",
                    "required_action", "status", "owner_role", "blocks_apply_mode",
                    "blocks_gate_progress", "provenance",
                ]
                for field in required_item:
                    assert field in item, f"Missing field in queue item: {field}"
                # High/blocker severity must block apply
                if item["severity"] in ("high", "blocker"):
                    assert item["blocks_apply_mode"] is True, (
                        f"Item {item['item_id']} severity={item['severity']} "
                        f"must have blocks_apply_mode=True"
                    )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Format-agnostic: fodt
# ---------------------------------------------------------------------------
class TestFormatAgnostic:
    def test_fodt_format_id_mismatch_caught(self):
        """Using --format-id fodt on a fods playbook is caught as a mismatch."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fodt",
            "--playbook", VALID_FIXTURE,  # valid fixture has format_id: fods
        ])
        assert rc != 0
        assert "FAIL" in stdout

    def test_fods_format_id_works(self):
        """Using --format-id fods on a fods playbook works correctly."""
        rc, stdout, stderr = run_replay([
            "--mode", "validate",
            "--format-id", "fods",
            "--playbook", VALID_FIXTURE,
        ])
        assert rc == 0


# ---------------------------------------------------------------------------
# No product source / no repo mutation
# ---------------------------------------------------------------------------
class TestNoRepoMutation:
    def test_replay_tool_does_not_import_product_modules(self):
        """replay_acquisition_playbook.py must not import product-layer modules."""
        with open(REPLAY_TOOL, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        forbidden_imports = {"fods", "fodt", "src.python", "src.net"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                for forbidden in forbidden_imports:
                    assert not module.startswith(forbidden), (
                        f"replay tool imports product module: {module}"
                    )

    def test_replay_tool_does_not_call_network(self):
        """replay_acquisition_playbook.py must not import networking modules."""
        with open(REPLAY_TOOL, encoding="utf-8") as f:
            source = f.read()
        network_modules = ["urllib", "requests", "httpx", "aiohttp", "http.client", "socket"]
        for mod in network_modules:
            assert mod not in source, (
                f"replay tool must not use network module: {mod}"
            )
