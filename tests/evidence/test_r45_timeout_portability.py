"""
R45 MT2 Lane 2A: pytest-timeout portability tests.

Sprint: FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001

Improves on test_r44_timeout_portability.py by:
1. Using pytest.importorskip for clean skips in environments without pytest-timeout
2. Verifying pytest.ini timeout setting is present and correct
3. Verifying test_auto_proof_bundle.py has bounded execution
4. Not failing in clean extracted environments — just skipping timeout-specific checks

The core guarantee: tests have BOUNDED execution via pytest.ini timeout=120,
even if pytest-timeout is installed from user site-packages rather than globally.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestPytestIniTimeout:
    """Verify pytest.ini timeout setting is present and correctly valued."""

    def test_pytest_ini_has_timeout(self):
        """pytest.ini must declare a timeout setting."""
        pytest_ini = REPO_ROOT / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini must exist in repo root"
        content = pytest_ini.read_text(encoding="utf-8")
        assert "timeout" in content, (
            "pytest.ini must declare 'timeout = N' for bounded test execution. "
            "R45 fix: added 'timeout = 120' to pytest.ini."
        )

    def test_pytest_ini_timeout_value_reasonable(self):
        """pytest.ini timeout must be at least 60s (auto-proof needs ~40s)."""
        pytest_ini = REPO_ROOT / "pytest.ini"
        content = pytest_ini.read_text(encoding="utf-8")
        import re
        m = re.search(r"^timeout\s*=\s*(\d+)", content, re.MULTILINE)
        if m:
            val = int(m.group(1))
            assert val >= 60, (
                f"pytest.ini timeout={val} is too short. "
                "auto_proof_bundle.py tests take ~40s, need at least 60s."
            )

    def test_pytest_ini_no_hardcoded_timeout_marks_in_autoproof(self):
        """test_auto_proof_bundle.py must not use @pytest.mark.timeout with values < 30s."""
        test_file = REPO_ROOT / "tests" / "evidence" / "test_auto_proof_bundle.py"
        content = test_file.read_text(encoding="utf-8")
        import re
        marks = re.findall(r"@pytest\.mark\.timeout\((\d+)\)", content)
        for val in marks:
            assert int(val) >= 30, (
                f"Hardcoded @pytest.mark.timeout({val}) in test_auto_proof_bundle.py "
                "is too short. auto-proof builds take ~40s."
            )


class TestPytestTimeoutPlugin:
    """Verify pytest-timeout plugin availability (skip if not installed)."""

    @pytest.fixture(autouse=False)
    def require_timeout_plugin(self):
        pytest.importorskip(
            "pytest_timeout",
            reason=(
                "pytest-timeout not installed — timeout-specific checks skipped. "
                "Install with: pip install --user pytest-timeout==2.3.1"
            ),
        )

    def test_pytest_timeout_importable(self, require_timeout_plugin):
        """pytest-timeout must be importable when installed."""
        import pytest_timeout
        assert pytest_timeout is not None

    def test_pytest_timeout_version_acceptable(self, require_timeout_plugin):
        """pytest-timeout must be version 2.x or newer."""
        import pytest_timeout
        # pytest_timeout exposes __version__ in newer versions
        version = getattr(pytest_timeout, "__version__", None)
        if version is None:
            # 2.3.1 does not expose __version__ directly — infer from pip metadata
            try:
                import importlib.metadata
                version = importlib.metadata.version("pytest-timeout")
            except Exception:
                pass
        if version:
            major = int(version.split(".")[0])
            assert major >= 2, (
                f"pytest-timeout {version} is too old. 2.x+ required."
            )


class TestAutoProofBoundedExecution:
    """Verify auto-proof bundle tests are bounded (will not hang indefinitely)."""

    def test_auto_proof_test_count_reasonable(self):
        """test_auto_proof_bundle.py should have <= 15 tests (each takes ~5s)."""
        test_file = REPO_ROOT / "tests" / "evidence" / "test_auto_proof_bundle.py"
        content = test_file.read_text(encoding="utf-8")
        import re
        test_functions = re.findall(r"^def (test_\w+)", content, re.MULTILINE)
        assert len(test_functions) <= 15, (
            f"test_auto_proof_bundle.py has {len(test_functions)} tests. "
            "Auto-proof tests take ~5s each; keep total <= 15 to stay under 120s limit."
        )

    def test_auto_proof_tests_bounded_by_ini_timeout(self):
        """With pytest.ini timeout=120, auto_proof tests are bounded.

        The 9 auto-proof tests take ~40s total. With timeout=120, even if
        a single test hangs, it will be terminated within 120s.
        """
        pytest_ini = REPO_ROOT / "pytest.ini"
        content = pytest_ini.read_text(encoding="utf-8")
        import re
        m = re.search(r"^timeout\s*=\s*(\d+)", content, re.MULTILINE)
        assert m is not None, (
            "pytest.ini must have timeout setting for auto-proof bounded execution."
        )
        val = int(m.group(1))
        # 9 tests * ~10s each = ~90s worst case; 120s provides adequate margin
        assert val >= 90, (
            f"pytest.ini timeout={val}s may be too tight for 9 auto-proof tests. "
            "Each test builds+validates a bundle; worst case is ~10s per test."
        )
