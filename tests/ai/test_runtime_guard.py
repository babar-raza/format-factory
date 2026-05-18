"""Tests for runtime AI-import guard."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.validators.runtime_guard import run_guard, scan_directory


class TestRuntimeGuard:
    def test_guard_passes_on_real_repo(self):
        result = run_guard(REPO_ROOT)
        assert result.passed is True, f"Violations: {result.violations}"

    def test_guard_detects_forbidden_import(self, tmp_path):
        src_python = tmp_path / "src" / "python"
        src_python.mkdir(parents=True)
        bad_file = src_python / "bad.py"
        bad_file.write_text("import litellm\n")

        violations = scan_directory(
            src_python,
            forbidden_imports=["litellm"],
            forbidden_env_refs=[],
            forbidden_url_refs=[],
        )
        assert len(violations) == 1
        assert violations[0]["pattern"] == "litellm"

    def test_guard_detects_forbidden_env_ref(self, tmp_path):
        src_net = tmp_path / "src" / "net"
        src_net.mkdir(parents=True)
        bad_file = src_net / "Config.cs"
        bad_file.write_text('var key = Environment.GetEnvironmentVariable("GPT_OSS_API_KEY");\n')

        violations = scan_directory(
            src_net,
            forbidden_imports=[],
            forbidden_env_refs=["GPT_OSS_API_KEY"],
            forbidden_url_refs=[],
        )
        assert len(violations) == 1
        assert violations[0]["type"] == "forbidden_env_reference"

    def test_guard_detects_forbidden_url(self, tmp_path):
        src_python = tmp_path / "src" / "python"
        src_python.mkdir(parents=True)
        bad_file = src_python / "client.py"
        bad_file.write_text('url = "https://llm.professionalize.com/v1"\n')

        violations = scan_directory(
            src_python,
            forbidden_imports=[],
            forbidden_env_refs=[],
            forbidden_url_refs=["llm.professionalize.com"],
        )
        assert len(violations) == 1
        assert violations[0]["type"] == "forbidden_url_reference"

    def test_guard_passes_clean_directory(self, tmp_path):
        src = tmp_path / "src" / "python"
        src.mkdir(parents=True)
        clean = src / "clean.py"
        clean.write_text("import os\nprint('hello')\n")

        violations = scan_directory(
            src,
            forbidden_imports=["litellm", "openai"],
            forbidden_env_refs=["GPT_OSS_API_KEY"],
            forbidden_url_refs=["llm.professionalize.com"],
        )
        assert len(violations) == 0

    def test_guard_handles_missing_directory(self, tmp_path):
        violations = scan_directory(
            tmp_path / "nonexistent",
            forbidden_imports=["litellm"],
            forbidden_env_refs=[],
            forbidden_url_refs=[],
        )
        assert len(violations) == 0
