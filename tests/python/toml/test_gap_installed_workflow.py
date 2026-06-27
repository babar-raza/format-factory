"""
tests/python/toml/test_gap_installed_workflow.py

Closes gap: GAP-TOML-FOSS-INSTALLED_WO-001
  — add test coverage for TOML Installed Workflow

Verifies that installed_workflow() is defined in toml_codec.py and works
correctly as a round-trip proof function for the TOML format.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLES = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_SAMPLES / "minimal.toml")

BUILD_DIR = _REPO / ".local" / "package-builds" / "python-foss"
VERSION = "0.1.0.dev0"
TOML_WHEEL = str(
    BUILD_DIR / "aspose-format-factory-toml" / "dist"
    / f"aspose_format_factory_toml-{VERSION}-py3-none-any.whl"
)


# ---------------------------------------------------------------------------
# Source-level tests: installed_workflow() from toml_codec
# ---------------------------------------------------------------------------

class TestInstalledWorkflowDefined:
    """GAP-TOML-FOSS-INSTALLED_WO-001: installed_workflow is importable."""

    def test_importable_from_toml_codec(self):
        from toml.toml_codec import installed_workflow
        assert callable(installed_workflow)

    def test_importable_from_src(self):
        import sys
        sys.path.insert(0, str(_REPO / "src" / "python"))
        from toml.toml_codec import installed_workflow
        assert callable(installed_workflow)


class TestInstalledWorkflowOutput:
    """GAP-TOML-FOSS-INSTALLED_WO-001: installed_workflow returns correct output."""

    def test_returns_dict(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert isinstance(result, dict)

    def test_format_field(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert result["format"] == "toml"

    def test_loaded_field(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert result["loaded"] is True

    def test_key_count_positive(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert result["key_count"] >= 1

    def test_key_count_type(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert isinstance(result["key_count"], int)

    def test_result_keys_present(self):
        from toml.toml_codec import installed_workflow
        result = installed_workflow(_MINIMAL)
        assert "format" in result
        assert "loaded" in result
        assert "key_count" in result


class TestInstalledWorkflowWithInlineToml:
    """GAP-TOML-FOSS-INSTALLED_WO-001: installed_workflow works on inline TOML string."""

    def test_inline_string(self, tmp_path):
        from toml.toml_codec import installed_workflow
        toml_content = b'name = "test"\nvalue = 42\n'
        p = tmp_path / "test.toml"
        p.write_bytes(toml_content)
        result = installed_workflow(str(p))
        assert result["loaded"] is True
        assert result["key_count"] >= 1

    def test_empty_document(self, tmp_path):
        from toml.toml_codec import installed_workflow
        p = tmp_path / "empty.toml"
        p.write_bytes(b"")
        result = installed_workflow(str(p))
        assert result["format"] == "toml"
        assert result["loaded"] is True
        assert result["key_count"] == 0


# ---------------------------------------------------------------------------
# Wheel-level tests: TOML wheel installs and exposes core API
# ---------------------------------------------------------------------------

class TestTomlWheelInstalledWorkflow:
    """GAP-TOML-FOSS-INSTALLED_WO-001: TOML wheel installs and exposes installed_workflow."""

    def test_toml_wheel_exists(self):
        assert os.path.isfile(TOML_WHEEL), f"TOML wheel not found: {TOML_WHEEL}"

    def test_toml_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(TOML_WHEEL), f"Not a valid zip/wheel: {TOML_WHEEL}"

    def test_toml_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="toml-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 TOML_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n{result.stderr}"
            )

    def test_toml_exposes_installed_workflow_from_wheel(self):
        with tempfile.TemporaryDirectory(prefix="toml-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", TOML_WHEEL],
                capture_output=True, text=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {repr(tmpdir)}); "
                 f"from toml.toml_codec import installed_workflow; "
                 f"print('TOML_IW_OK')"],
                capture_output=True, text=True
            )
            assert "TOML_IW_OK" in result.stdout, (
                f"installed_workflow not importable from installed wheel.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
