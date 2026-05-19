"""Tests for Phase 2 runtime guard enhancements — Lane D."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.validators.runtime_guard import (
    run_guard,
    scan_directory,
    scan_for_direct_endpoint_calls,
)


class TestDirectEndpointBypass:
    def test_detects_bypass_with_ai_context(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai" / "evil"
        tools_ai.mkdir(parents=True)
        bad = tools_ai / "bad_caller.py"
        bad.write_text(
            'import httpx\n'
            'client = httpx.Client()\n'
            'resp = client.get("https://llm.professionalize.com/v1/models")\n'
        )
        violations = scan_for_direct_endpoint_calls(tmp_path / "tools" / "ai")
        assert len(violations) == 1
        assert violations[0]["type"] == "direct_endpoint_bypass"

    def test_ignores_gateway_itself(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        tools_ai.mkdir(parents=True)
        gw = tools_ai / "gateway.py"
        gw.write_text(
            'import httpx\n'
            'client = httpx.Client()\n'
            'resp = client.get("https://llm.professionalize.com/v1/models")\n'
        )
        violations = scan_for_direct_endpoint_calls(tools_ai)
        assert len(violations) == 0

    def test_ignores_discovery(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai"
        tools_ai.mkdir(parents=True)
        disc = tools_ai / "model_discovery.py"
        disc.write_text(
            'import httpx\n'
            'client = httpx.Client()\n'
            'url = "https://llm.professionalize.com/v1/models"\n'
        )
        violations = scan_for_direct_endpoint_calls(tools_ai)
        assert len(violations) == 0

    def test_no_violation_without_ai_context(self, tmp_path):
        tools_ai = tmp_path / "tools" / "ai" / "util"
        tools_ai.mkdir(parents=True)
        clean = tools_ai / "helper.py"
        clean.write_text(
            'import httpx\n'
            'client = httpx.Client()\n'
            'resp = client.get("https://example.com/data")\n'
        )
        violations = scan_for_direct_endpoint_calls(tmp_path / "tools" / "ai")
        assert len(violations) == 0

    def test_no_violation_for_missing_dir(self, tmp_path):
        violations = scan_for_direct_endpoint_calls(tmp_path / "nonexistent")
        assert len(violations) == 0


class TestGuardPhase2Integration:
    def test_guard_still_passes_on_real_repo(self):
        result = run_guard(REPO_ROOT)
        assert result.passed is True, f"Violations: {result.violations}"

    def test_guard_scans_tools_ai(self):
        result = run_guard(REPO_ROOT)
        tools_ai_scanned = any("tools" in p and "ai" in p for p in result.scanned_paths)
        assert tools_ai_scanned is True


class TestForbiddenImportInTestPaths:
    def test_tests_ai_is_allowed_location(self):
        """tests/ai/ is the ONLY accepted AI test location."""
        result = run_guard(REPO_ROOT)
        assert result.passed is True
