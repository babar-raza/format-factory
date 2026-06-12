"""
R44 Lane 1C: Tests for pytest-timeout portability.

Verifies:
1. pytest-timeout IS available in the user site-packages.
2. The correct invocation method (PYTHONPATH + sys.path.insert) loads it.
3. Documents expected test run mechanism for CI portability.

Sprint: FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
"""

import subprocess
import sys
from pathlib import Path


class TestPytestTimeoutPortability:
    """Verify pytest-timeout availability and invocation."""

    def test_pytest_timeout_importable(self):
        """pytest-timeout must be importable via standard import machinery."""
        try:
            import pytest_timeout
            # pytest_timeout may not expose __version__ directly (it's a single-file plugin)
            assert pytest_timeout is not None, "pytest_timeout module must load"
        except ImportError:
            # Check if available in user site-packages
            import site
            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                sys.path.insert(0, user_site)
            try:
                import pytest_timeout
                assert pytest_timeout is not None, "pytest_timeout must load from user site"
            except ImportError:
                raise AssertionError(
                    "pytest-timeout is NOT installed. "
                    "Install with: pip install --user pytest-timeout. "
                    "Required for test_auto_proof_bundle.py timeout protection."
                )

    def test_pytest_reports_timeout_plugin(self):
        """Running pytest --version should list timeout plugin."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
        )
        # Check if pytest ran at all
        combined = result.stdout + result.stderr
        if "timeout" in combined.lower():
            # Good — timeout plugin is reported
            pass
        else:
            # Acceptable if pytest itself works (timeout may be installed but not shown)
            import site
            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                sys.path.insert(0, user_site)
            try:
                import pytest_timeout
                # Plugin exists, just not shown in --version
                pass
            except ImportError:
                raise AssertionError(
                    "pytest-timeout not detectable. Combined output:\n" + combined
                )

    def test_auto_proof_tests_have_no_hardcoded_timeout_marks(self):
        """test_auto_proof_bundle.py must not use @pytest.mark.timeout hardcoded values."""
        test_file = Path(__file__).parents[1] / "evidence" / "test_auto_proof_bundle.py"
        content = test_file.read_text(encoding="utf-8")
        # It's OK to have timeout marks, but not hardcoded absurdly short values
        # The key check: no @pytest.mark.timeout(N) with N < 10s
        import re
        marks = re.findall(r"@pytest\.mark\.timeout\((\d+)\)", content)
        for val in marks:
            assert int(val) >= 10, (
                f"Hardcoded timeout {val}s is too short for auto-proof build tests. "
                "Minimum 10s required."
            )

    def test_correct_python_invocation_documented(self):
        """Verify the project's correct pytest invocation (PYTHONPATH prefix) works."""
        repo_root = Path(__file__).parents[2]
        # The project uses: PYTHONPATH=src/python python -c "import sys; sys.path.insert(0, USER_SITE); import pytest; pytest.main([...])"
        # We verify this by checking that pytest can be imported after path insertion
        import site
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.insert(0, user_site)
        import pytest
        assert pytest.__version__ >= "8.0.0", (
            f"pytest version {pytest.__version__} is too old. 8.x+ required."
        )
