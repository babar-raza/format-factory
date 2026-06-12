"""Lane J tests — risk controls and validation gates.

Tests for executable risk checks including runtime AI-free guard,
authority state visibility, gateway enforcement, secret redaction,
fallback restriction, and cross-format isolation.
"""

from pathlib import Path

from tools.ai.validators.risk_controls import (
    check_authority_states_visible,
    check_cross_format_isolation,
    check_gateway_enforcement,
    check_no_fallback_for_restricted_roles,
    check_runtime_ai_free,
    check_secret_redaction,
    run_all_risk_checks,
)


class TestRuntimeAIFree:
    def test_clean_src(self, tmp_path):
        # Create clean src dirs
        (tmp_path / "src" / "python" / "fods").mkdir(parents=True)
        (tmp_path / "src" / "net" / "fods").mkdir(parents=True)
        (tmp_path / "tools" / "ai" / "contracts").mkdir(parents=True)
        result = check_runtime_ai_free(tmp_path)
        assert result["passed"] is True

    def test_dirty_src_with_ai_import(self, tmp_path):
        (tmp_path / "src" / "python" / "fods").mkdir(parents=True)
        (tmp_path / "src" / "net").mkdir(parents=True)
        (tmp_path / "tools" / "ai" / "contracts").mkdir(parents=True)
        dirty_file = tmp_path / "src" / "python" / "fods" / "codec.py"
        dirty_file.write_text("import litellm\n")
        # Write forbidden patterns contract
        import yaml
        contract = {
            "forbidden_imports": ["litellm"],
            "forbidden_env_references": [],
            "forbidden_url_references": [],
        }
        (tmp_path / "tools" / "ai" / "contracts" / "forbidden-runtime-imports.yaml").write_text(
            yaml.dump(contract)
        )
        result = check_runtime_ai_free(tmp_path)
        assert result["passed"] is False
        assert len(result["violations"]) > 0


class TestControlExistence:
    def test_authority_states_visible(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        (tools_ai / "validators").mkdir(parents=True)
        (tools_ai / "contracts").mkdir(parents=True)
        (tools_ai / "validators" / "authority_lifecycle.py").write_text("# exists")
        (tools_ai / "contracts" / "artifact-authority-states.yaml").write_text("# exists")
        result = check_authority_states_visible(tools_ai)
        assert result["passed"] is True

    def test_gateway_enforcement(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        (tools_ai / "control_plane").mkdir(parents=True)
        (tools_ai / "validators").mkdir(parents=True)
        (tools_ai / "control_plane" / "gateway.py").write_text("# exists")
        (tools_ai / "validators" / "runtime_guard.py").write_text("# exists")
        result = check_gateway_enforcement(tools_ai)
        assert result["passed"] is True

    def test_secret_redaction(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        (tools_ai / "validators").mkdir(parents=True)
        (tools_ai / "validators" / "secret_redaction.py").write_text("# exists")
        result = check_secret_redaction(tools_ai)
        assert result["passed"] is True


class TestNoFallbackRestricted:
    def test_router_has_no_fallback(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        (tools_ai / "control_plane").mkdir(parents=True)
        (tools_ai / "control_plane" / "model_router.py").write_text("NO_FALLBACK_ROLES = {}")
        result = check_no_fallback_for_restricted_roles(tools_ai)
        assert result["passed"] is True


class TestCrossFormatIsolation:
    def test_namespace_manager_has_rejection(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        (tools_ai / "retrieval").mkdir(parents=True)
        (tools_ai / "retrieval" / "namespace_manager.py").write_text("class CrossNamespaceError: pass")
        result = check_cross_format_isolation(tools_ai)
        assert result["passed"] is True


class TestRunAllChecks:
    def test_run_all_on_repo_root(self):
        repo_root = Path("c:/Users/prora/OneDrive/Documents/GitHub/format-factory")
        results = run_all_risk_checks(repo_root)
        assert len(results) == 6
        for r in results:
            assert "check" in r
            assert "passed" in r
