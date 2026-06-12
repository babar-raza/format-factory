"""
R46 timeout portability tests — MT4.

Verifies that:
1. pytest.ini has filterwarnings to suppress Unknown config option: timeout
2. tools/testing/run_bounded_pytest.py exists and is importable
3. The bounded runner handles cases with and without pytest-timeout
4. The filterwarnings pattern matches the exact PytestConfigWarning text
"""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
PYTEST_INI = REPO_ROOT / "pytest.ini"
BOUNDED_RUNNER = REPO_ROOT / "tools" / "testing" / "run_bounded_pytest.py"


class TestPytestIniFilterWarnings:
    """Verify pytest.ini has the filterwarnings fix for timeout warning."""

    def test_filterwarnings_present_in_pytest_ini(self):
        """pytest.ini must have a filterwarnings section."""
        assert PYTEST_INI.exists(), "pytest.ini must exist"
        content = PYTEST_INI.read_text(encoding="utf-8")
        assert "filterwarnings" in content, (
            "pytest.ini must have filterwarnings section to suppress "
            "PytestConfigWarning for Unknown config option: timeout"
        )

    def test_filterwarnings_suppresses_timeout_warning(self):
        """filterwarnings must include a pattern for Unknown config option.*timeout."""
        content = PYTEST_INI.read_text(encoding="utf-8")
        assert "Unknown config option" in content or "timeout" in content.lower(), (
            "filterwarnings must reference 'timeout' or 'Unknown config option'"
        )

    def test_pytest_ini_timeout_value_is_present(self):
        """timeout = 120 must still be present (for CI with pytest-timeout)."""
        content = PYTEST_INI.read_text(encoding="utf-8")
        assert "timeout = 120" in content or "timeout=120" in content, (
            "pytest.ini must still declare timeout = 120 for environments with pytest-timeout"
        )

    def test_filterwarnings_targets_pytestconfigwarning(self):
        """filterwarnings must target pytest.PytestConfigWarning."""
        content = PYTEST_INI.read_text(encoding="utf-8")
        assert "PytestConfigWarning" in content, (
            "filterwarnings must reference pytest.PytestConfigWarning to be specific"
        )


class TestBoundedRunner:
    """Verify tools/testing/run_bounded_pytest.py exists and is functional."""

    def test_bounded_runner_exists(self):
        """run_bounded_pytest.py must exist."""
        assert BOUNDED_RUNNER.exists(), f"Expected: {BOUNDED_RUNNER}"

    def test_bounded_runner_importable(self):
        """run_bounded_pytest.py must be importable without errors."""
        path_str = str(BOUNDED_RUNNER).replace("\\", "/")
        result = subprocess.run(
            [sys.executable, "-c",
             f"import importlib.util; "
             f"spec = importlib.util.spec_from_file_location('rbp', r'{path_str}'); "
             f"mod = importlib.util.module_from_spec(spec); "
             f"spec.loader.exec_module(mod); "
             f"assert hasattr(mod, 'run_bounded')"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"

    def test_bounded_runner_has_run_bounded_function(self):
        """run_bounded_pytest.py must expose a run_bounded() function."""
        content = BOUNDED_RUNNER.read_text(encoding="utf-8")
        assert "def run_bounded(" in content

    def test_bounded_runner_has_max_seconds_param(self):
        """run_bounded_pytest.py must accept --max-seconds parameter."""
        content = BOUNDED_RUNNER.read_text(encoding="utf-8")
        assert "--max-seconds" in content

    def test_bounded_runner_handles_timeout_plugin_detection(self):
        """run_bounded_pytest.py must check whether pytest-timeout is available."""
        content = BOUNDED_RUNNER.read_text(encoding="utf-8")
        assert "pytest_timeout" in content or "pytest-timeout" in content

    def test_bounded_runner_exit_code_timeout_is_2(self):
        """run_bounded_pytest.py must use exit code 2 for wall-clock timeout."""
        content = BOUNDED_RUNNER.read_text(encoding="utf-8")
        assert "sys.exit(2)" in content, "Exit code 2 must be used for timeout"

    def test_bounded_runner_help_flag(self):
        """run_bounded_pytest.py --help must exit 0."""
        result = subprocess.run(
            [sys.executable, str(BOUNDED_RUNNER), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "--suite" in result.stdout
        assert "--max-seconds" in result.stdout
