"""
test_playbook_schema.py — S-F2F-02B Playbook Validation Tool Tests

Tests for:
1. Schema files are valid JSON and have required structure.
2. Documentation example YAML is valid YAML with correct policy fields.
3. Valid fixtures pass validation (both engines).
4. Invalid fixtures fail validation.
5. validate_playbook.py exit codes behave correctly.
6. validate_playbook.py writes no files.
7. validate_playbook.py does not import or execute replay/apply modules.
8. No replay/apply modules exist.
9. Engine selection behaves correctly.
10. Documentation example passes full JSON Schema when jsonschema is available.
11. Policy check catches missing not_for_execution.

Engine notes:
- 'auto' uses jsonschema when available (PYTHONPATH required on Windows for Roaming install).
- 'fallback_structural' never requires jsonschema.
- 'jsonschema' fails clearly if jsonschema is not installed.
- Structural fallback does NOT claim full JSON Schema compliance.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

import pytest
import yaml

# Repo root derived from this test file's location
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def repo_path(*parts):
    return os.path.join(REPO_ROOT, *parts)


SCHEMA_ACQUISITION = repo_path("schemas", "playbook", "acquisition-playbook.schema.json")
SCHEMA_REVIEW_QUEUE = repo_path("schemas", "playbook", "review-queue.schema.json")
DOCS_EXAMPLE = repo_path("docs", "examples", "acquisition-playbook-fods-documentation-example.yaml")
VALIDATOR = repo_path("tools", "playbook", "validate_playbook.py")

FIXTURE_VALID_ACQUISITION = repo_path("tests", "playbook", "fixtures", "valid-acquisition-playbook.yaml")
FIXTURE_INVALID_MISSING_FIELD = repo_path("tests", "playbook", "fixtures", "invalid-missing-required-field.yaml")
FIXTURE_INVALID_FORBIDDEN = repo_path("tests", "playbook", "fixtures", "invalid-forbidden-authority.yaml")
FIXTURE_VALID_REVIEW_QUEUE = repo_path("tests", "playbook", "fixtures", "valid-review-queue.yaml")
FIXTURE_INVALID_REVIEW_QUEUE = repo_path("tests", "playbook", "fixtures", "invalid-review-queue-missing-items.yaml")

# Check if jsonschema is available in the current Python environment
try:
    import jsonschema as _jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_validator(*args, capture=True):
    """Run validate_playbook.py and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, VALIDATOR] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout, result.stderr


def load_validator_module():
    """Import the validator module for direct API testing."""
    spec = importlib.util.spec_from_file_location("validate_playbook", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. Schema files are valid JSON
# ---------------------------------------------------------------------------

class TestSchemaFilesValidJson:
    def test_acquisition_playbook_schema_is_valid_json(self):
        """acquisition-playbook.schema.json must be valid JSON."""
        assert os.path.isfile(SCHEMA_ACQUISITION), f"Schema file not found: {SCHEMA_ACQUISITION}"
        with open(SCHEMA_ACQUISITION, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), "Schema must be a JSON object"
        assert "$schema" in data, "Schema must have $schema field"
        assert "required" in data, "Schema must have required field"

    def test_review_queue_schema_is_valid_json(self):
        """review-queue.schema.json must be valid JSON."""
        assert os.path.isfile(SCHEMA_REVIEW_QUEUE), f"Schema file not found: {SCHEMA_REVIEW_QUEUE}"
        with open(SCHEMA_REVIEW_QUEUE, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), "Schema must be a JSON object"
        assert "$schema" in data, "Schema must have $schema field"
        assert "required" in data, "Schema must have required field"

    def test_acquisition_schema_has_required_fields_list(self):
        """acquisition-playbook schema required list must include key fields."""
        with open(SCHEMA_ACQUISITION, encoding="utf-8") as f:
            schema = json.load(f)
        required = schema.get("required", [])
        for field in ["schema_version", "playbook_id", "format_id", "status", "forbidden_uses"]:
            assert field in required, f"Schema required must include '{field}'"

    def test_review_queue_schema_has_required_fields_list(self):
        """review-queue schema required list must include key fields."""
        with open(SCHEMA_REVIEW_QUEUE, encoding="utf-8") as f:
            schema = json.load(f)
        required = schema.get("required", [])
        for field in ["schema_version", "queue_id", "items", "governance"]:
            assert field in required, f"Schema required must include '{field}'"

    def test_acquisition_schema_has_not_for_execution_property(self):
        """acquisition-playbook schema must define not_for_execution property (S-F2F-02B repair)."""
        with open(SCHEMA_ACQUISITION, encoding="utf-8") as f:
            schema = json.load(f)
        properties = schema.get("properties", {})
        assert "not_for_execution" in properties, (
            "Schema must define not_for_execution property (schema gap repaired in S-F2F-02B)"
        )
        nfe = properties["not_for_execution"]
        assert nfe.get("type") == "boolean", "not_for_execution must be type boolean"

    def test_acquisition_schema_additional_properties_false(self):
        """acquisition-playbook schema must keep additionalProperties: false."""
        with open(SCHEMA_ACQUISITION, encoding="utf-8") as f:
            schema = json.load(f)
        assert schema.get("additionalProperties") is False, (
            "Schema must keep additionalProperties: false"
        )


# ---------------------------------------------------------------------------
# 2. Documentation example is valid YAML with correct policy fields
# ---------------------------------------------------------------------------

class TestDocsExampleValidYaml:
    def test_docs_example_is_valid_yaml(self):
        """Documentation example must be parseable YAML."""
        assert os.path.isfile(DOCS_EXAMPLE), f"Docs example not found: {DOCS_EXAMPLE}"
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None, "Docs example YAML must not be empty"
        assert isinstance(data, dict), "Docs example must be a YAML mapping"

    def test_docs_example_has_documentation_status(self):
        """Documentation example must have status=documentation_example_only."""
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data.get("status") == "documentation_example_only", (
            "Docs example must have status=documentation_example_only"
        )

    def test_docs_example_has_not_for_execution(self):
        """Documentation example must have not_for_execution: true."""
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data.get("not_for_execution") is True, (
            "Docs example must have not_for_execution: true"
        )

    def test_docs_example_has_required_forbidden_uses(self):
        """Documentation example must have required forbidden_uses."""
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        forbidden = data.get("forbidden_uses", [])
        for required_use in [
            "automatic_gate_approval",
            "spec_or_legal_authority",
            "replacing_dec034",
            "replacing_human_approval",
        ]:
            assert required_use in forbidden, (
                f"Docs example forbidden_uses must include '{required_use}'"
            )


# ---------------------------------------------------------------------------
# 3. Valid fixtures pass validation
# ---------------------------------------------------------------------------

class TestValidFixturesPass:
    def test_valid_acquisition_playbook_passes_auto_engine(self):
        """Valid acquisition playbook fixture must pass validation with auto engine."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 0, (
            f"Expected exit code 0 for valid fixture, got {rc}\nstdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout, (
            f"Expected PLAYBOOK_VALIDATION: PASS in stdout\nstdout: {stdout}"
        )

    def test_valid_acquisition_playbook_passes_structural_engine(self):
        """Valid acquisition playbook fixture must pass structural engine."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "fallback_structural",
        )
        assert rc == 0, (
            f"Expected exit code 0 for valid fixture with structural engine, got {rc}\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout
        assert "fallback_structural" in stderr

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not available in current environment")
    def test_valid_acquisition_playbook_passes_jsonschema_engine(self):
        """Valid acquisition playbook must pass jsonschema engine when available."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "jsonschema",
        )
        assert rc == 0, (
            f"Expected exit code 0 for valid fixture with jsonschema engine, got {rc}\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout
        assert "jsonschema" in stderr

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not available in current environment")
    def test_docs_example_passes_jsonschema_engine(self):
        """Documentation example must pass full JSON Schema validation after S-F2F-02B repair."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", DOCS_EXAMPLE,
            "--kind", "acquisition-playbook",
            "--format-id", "fods",
            "--engine", "jsonschema",
        )
        assert rc == 0, (
            f"Documentation example must pass jsonschema engine after schema repair.\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout

    def test_docs_example_passes_structural_engine(self):
        """Documentation example must pass structural fallback validation."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", DOCS_EXAMPLE,
            "--kind", "acquisition-playbook",
            "--format-id", "fods",
            "--engine", "fallback_structural",
        )
        assert rc == 0, (
            f"Documentation example must pass structural engine.\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout

    def test_docs_example_passes_structural_api(self):
        """Documentation example must pass structural fallback via module API."""
        mod = load_validator_module()
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        errors = mod._validate_acquisition_playbook_structural(data)
        assert errors == [], f"Structural errors: {errors}"
        auth_errors = mod._check_forbidden_authority(data, "acquisition-playbook")
        assert auth_errors == [], f"Authority errors: {auth_errors}"
        policy_errors = mod._check_documentation_example_policy(data, "acquisition-playbook")
        assert policy_errors == [], f"Policy errors: {policy_errors}"

    def test_valid_review_queue_passes(self):
        """Valid review queue fixture must pass validation."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_REVIEW_QUEUE,
            "--input", FIXTURE_VALID_REVIEW_QUEUE,
            "--kind", "review-queue",
            "--format-id", "test-format",
        )
        assert rc == 0, (
            f"Expected exit code 0 for valid review queue, got {rc}\nstdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: PASS" in stdout


# ---------------------------------------------------------------------------
# 4. Invalid fixtures fail validation
# ---------------------------------------------------------------------------

class TestInvalidFixturesFail:
    def test_missing_required_field_fails(self):
        """Fixture missing required 'status' field must fail validation."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_INVALID_MISSING_FIELD,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 1, (
            f"Expected exit code 1 for invalid fixture, got {rc}\nstdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: FAIL" in stdout, (
            f"Expected PLAYBOOK_VALIDATION: FAIL in stdout\nstdout: {stdout}"
        )

    def test_missing_forbidden_authority_fails(self):
        """Fixture missing required forbidden_uses entries must fail."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_INVALID_FORBIDDEN,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 1, (
            f"Expected exit code 1 for forbidden authority fixture, got {rc}\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: FAIL" in stdout

    def test_invalid_review_queue_missing_items_fails(self):
        """Review queue fixture missing 'items' field must fail validation."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_REVIEW_QUEUE,
            "--input", FIXTURE_INVALID_REVIEW_QUEUE,
            "--kind", "review-queue",
            "--format-id", "test-format",
        )
        assert rc == 1, (
            f"Expected exit code 1 for invalid review queue, got {rc}\nstdout: {stdout}\nstderr: {stderr}"
        )
        assert "PLAYBOOK_VALIDATION: FAIL" in stdout

    def test_nonexistent_input_fails(self):
        """Non-existent input file must return exit code 1 with clear message."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", "/nonexistent/path/playbook.yaml",
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 1, f"Expected exit code 1 for nonexistent input, got {rc}"
        assert "PLAYBOOK_VALIDATION: FAIL" in stdout
        assert "FILE_NOT_FOUND" in stdout

    def test_nonexistent_schema_fails(self):
        """Non-existent schema file must return exit code 1 with clear message."""
        rc, stdout, stderr = run_validator(
            "--schema", "/nonexistent/schema.json",
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 1, f"Expected exit code 1 for nonexistent schema, got {rc}"
        assert "PLAYBOOK_VALIDATION: FAIL" in stdout
        assert "FILE_NOT_FOUND" in stdout

    def test_docs_example_fails_policy_if_not_for_execution_missing(self):
        """Policy check must catch missing not_for_execution for documentation_example_only."""
        mod = load_validator_module()
        with open(DOCS_EXAMPLE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # Remove not_for_execution to trigger policy error
        data_no_nfe = {k: v for k, v in data.items() if k != "not_for_execution"}
        policy_errors = mod._check_documentation_example_policy(data_no_nfe, "acquisition-playbook")
        assert len(policy_errors) > 0, (
            "Policy check must report error when not_for_execution is missing "
            "for documentation_example_only status"
        )
        assert any("not_for_execution" in e for e in policy_errors)


# ---------------------------------------------------------------------------
# 5. Engine selection
# ---------------------------------------------------------------------------

class TestEngineSelection:
    def test_structural_engine_reports_fallback_in_stderr(self):
        """Structural engine must report fallback in stderr."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "fallback_structural",
        )
        assert "fallback_structural" in stderr, f"Structural engine must report in stderr: {stderr}"

    def test_structural_engine_does_not_claim_full_json_schema(self):
        """Structural engine stderr must not claim full JSON Schema compliance."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "fallback_structural",
        )
        # Should explicitly say NOT full JSON Schema compliance
        assert "NOT full JSON Schema compliance" in stderr, (
            f"Structural engine must disclaim full compliance: {stderr}"
        )

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not available in current environment")
    def test_jsonschema_engine_reports_version_in_stderr(self):
        """Jsonschema engine must report version in stderr."""
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "jsonschema",
        )
        assert "jsonschema" in stderr, f"Jsonschema engine must report in stderr: {stderr}"

    def test_jsonschema_engine_fails_clearly_when_unavailable(self):
        """jsonschema engine must fail clearly when jsonschema not available in current env.

        This test runs the validator without PYTHONPATH, so jsonschema is not available
        in the default system Python. If jsonschema IS available, we skip this test.
        """
        if JSONSCHEMA_AVAILABLE:
            pytest.skip("jsonschema is available in current environment; cannot test unavailable case")
        rc, stdout, stderr = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--engine", "jsonschema",
        )
        assert rc == 1, f"Expected exit 1 when jsonschema unavailable, got {rc}"
        assert "ENGINE_ERROR" in stdout or "PLAYBOOK_VALIDATION: FAIL" in stdout


# ---------------------------------------------------------------------------
# 6. Exit code correctness
# ---------------------------------------------------------------------------

class TestExitCodes:
    def test_valid_input_exits_zero(self):
        """Valid input must produce exit code 0."""
        rc, _, _ = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 0

    def test_invalid_input_exits_one(self):
        """Invalid input must produce exit code 1."""
        rc, _, _ = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_INVALID_MISSING_FIELD,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert rc == 1

    def test_json_output_valid_has_pass(self):
        """JSON output for valid input must have playbook_validation: PASS."""
        rc, stdout, _ = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--json-output",
        )
        assert rc == 0
        result = json.loads(stdout)
        assert result.get("playbook_validation") == "PASS"
        assert result.get("errors") == []

    def test_json_output_invalid_has_fail(self):
        """JSON output for invalid input must have playbook_validation: FAIL with errors."""
        rc, stdout, _ = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_INVALID_MISSING_FIELD,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--json-output",
        )
        assert rc == 1
        result = json.loads(stdout)
        assert result.get("playbook_validation") == "FAIL"
        assert len(result.get("errors", [])) > 0

    def test_json_output_has_engine_field(self):
        """JSON output must include json_schema_engine field."""
        rc, stdout, _ = run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
            "--json-output",
        )
        result = json.loads(stdout)
        assert "json_schema_engine" in result, "JSON output must have json_schema_engine field"


# ---------------------------------------------------------------------------
# 7. No-write proof: validator must not create any files
# ---------------------------------------------------------------------------

class TestNoWriteProof:
    def test_validator_does_not_write_files(self):
        """Validator must not create any files in the repo when running."""
        before_files = set()
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", ".local", "__pycache__")]
            for fname in files:
                before_files.add(os.path.join(root, fname))

        run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_INVALID_MISSING_FIELD,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        run_validator(
            "--schema", SCHEMA_REVIEW_QUEUE,
            "--input", FIXTURE_VALID_REVIEW_QUEUE,
            "--kind", "review-queue",
            "--format-id", "test-format",
        )

        after_files = set()
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", ".local", "__pycache__")]
            for fname in files:
                after_files.add(os.path.join(root, fname))

        new_files = after_files - before_files
        new_non_cache = {f for f in new_files if ".pyc" not in f and "__pycache__" not in f}
        assert not new_non_cache, (
            f"Validator created unexpected files: {new_non_cache}"
        )

    def test_validator_does_not_create_review_queues(self):
        """Validator must not create plans/review-queues/ directory."""
        review_queues_dir = repo_path("plans", "review-queues")
        run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert not os.path.exists(review_queues_dir), (
            f"Validator must not create {review_queues_dir}"
        )

    def test_validator_does_not_create_playbook_outputs(self):
        """Validator must not create any acquisition-pack playbook files."""
        run_validator(
            "--schema", SCHEMA_ACQUISITION,
            "--input", FIXTURE_VALID_ACQUISITION,
            "--kind", "acquisition-playbook",
            "--format-id", "test-format",
        )
        assert not os.path.exists(repo_path("acquisition-packs", "fods", "playbook.yaml"))
        assert not os.path.exists(repo_path("acquisition-packs", "fodt", "playbook.yaml"))
        assert not os.path.exists(repo_path("acquisition-packs", "_families"))


# ---------------------------------------------------------------------------
# 8. No replay/apply modules exist or are imported
# ---------------------------------------------------------------------------

class TestNoReplayApplyModules:
    def test_replay_module_exists_and_has_no_apply_mode(self):
        """replay_acquisition_playbook.py (S-F2F-03) must exist and must not implement apply mode."""
        replay_path = repo_path("tools", "playbook", "replay_acquisition_playbook.py")
        assert os.path.exists(replay_path), (
            "replay_acquisition_playbook.py must exist (created by S-F2F-03)"
        )
        import ast as _ast
        with open(replay_path, encoding="utf-8") as f:
            source = f.read()
        tree = _ast.parse(source)
        # Apply mode IMPLEMENTATION functions must not exist (guards are OK)
        forbidden_impl_patterns = [
            "mode_apply", "apply_mode", "do_apply", "execute_apply",
            "run_apply", "apply_proposed", "apply_authorized",
        ]
        for node in _ast.walk(tree):
            if isinstance(node, _ast.FunctionDef):
                name = node.name.lower()
                for pattern in forbidden_impl_patterns:
                    assert pattern not in name, (
                        f"Found apply mode implementation: {node.name}. "
                        "Apply mode is not authorized (S-F2F-06 not yet approved)."
                    )

    def test_diff_module_exists(self):
        """diff_playbook_outputs.py (S-F2F-03) must exist."""
        assert os.path.exists(
            repo_path("tools", "playbook", "diff_playbook_outputs.py")
        ), "diff_playbook_outputs.py must exist (created by S-F2F-03)"

    def test_export_review_queue_module_exists(self):
        """export_review_queue.py (S-F2F-03) must exist."""
        assert os.path.exists(
            repo_path("tools", "playbook", "export_review_queue.py")
        ), "export_review_queue.py must exist (created by S-F2F-03)"

    def test_create_golden_case_module_does_not_exist(self):
        """create_golden_case.py must not exist."""
        assert not os.path.exists(
            repo_path("tools", "playbook", "create_golden_case.py")
        ), "create_golden_case.py must not exist"

    def test_golden_test_directory_does_not_exist(self):
        """tests/playbook/golden/ must not exist."""
        assert not os.path.exists(
            repo_path("tests", "playbook", "golden")
        ), "tests/playbook/golden/ must not exist"

    def test_review_queues_directory_does_not_exist(self):
        """plans/review-queues/ must not exist."""
        assert not os.path.exists(
            repo_path("plans", "review-queues")
        ), "plans/review-queues/ must not exist"

    def test_no_unauthorized_product_source_directories(self):
        """Unauthorized product source directories must not exist.
        Note: src/python/fods/ is authorized by Gate 10 + TC-0050 Phase 4 prompt.
        Unauthorized: src/python/fodt/ (TC-0052 not started), src/net/fods/ (DEC-033 blocked),
        src/net/fodt/ (DEC-033 blocked), acquisition-packs/_families/ (S-F2F-05 not authorized).
        """
        forbidden_dirs = [
            repo_path("src", "python", "fodt"),    # TC-0052 not started
            repo_path("src", "net", "fods"),        # DEC-033 unresolved
            repo_path("src", "net", "fodt"),        # DEC-033 unresolved
            repo_path("acquisition-packs", "_families"),  # S-F2F-05 not authorized
        ]
        for d in forbidden_dirs:
            assert not os.path.exists(d), f"Unauthorized directory must not exist: {d}"

    def test_validator_source_does_not_import_replay(self):
        """validate_playbook.py source must not import replay or apply modules."""
        with open(VALIDATOR, encoding="utf-8") as f:
            source = f.read()
        import re
        forbidden_modules = [
            "replay_acquisition_playbook",
            "diff_playbook_outputs",
            "export_review_queue",
            "create_golden_case",
        ]
        for module in forbidden_modules:
            assert module not in source, (
                f"validate_playbook.py must not import or reference module '{module}'"
            )
        # Check that apply_mode is not referenced as a module or function name
        forbidden_patterns = [
            r"\bimport apply_mode\b",
            r"\bfrom apply_mode\b",
            r"\bapply_mode\s*\(",
        ]
        for pattern in forbidden_patterns:
            assert not re.search(pattern, source), (
                f"validate_playbook.py must not reference apply_mode module: {pattern}"
            )
