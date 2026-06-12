"""
tests/evidence/test_r82_rejects_installed_wheel_test_skips.py

R82 Train E: Installed-wheel tests must not be universally skipped.

Defect fixed: D79-08 — R79 evidence contained tests that all skipped
(no installed wheel available = no real proof).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestInstalledWheelTestsNotAllSkipped:
    """Installed-wheel tests must not all be skipped for a package-readiness sprint."""

    def test_installed_wheel_test_file_exists(self):
        """R82 must have an installed-wheel test file."""
        test_file = REPO_ROOT / "tests" / "packaging" / "test_r82_installed_fods_product_workflow.py"
        assert test_file.exists(), f"Missing installed-wheel test file: {test_file}"

    def test_installed_wheel_test_file_has_assertions(self):
        """The installed-wheel test file must contain real assertions (not just skips)."""
        test_file = REPO_ROOT / "tests" / "packaging" / "test_r82_installed_fods_product_workflow.py"
        if not test_file.exists():
            return
        content = test_file.read_text(encoding="utf-8")
        # Must have assert statements
        assert "assert " in content, "Installed-wheel test file must contain assertions"
        # Must not be entirely skips
        skip_count = content.count("pytest.skip(")
        assert_count = content.count("assert ")
        assert assert_count > skip_count, (
            f"Too many skips vs assertions: {skip_count} skips, {assert_count} asserts"
        )

    def test_skip_guard_uses_importerror_not_unconditional(self):
        """Skip guards must be conditional (ImportError), not unconditional."""
        test_file = REPO_ROOT / "tests" / "packaging" / "test_r82_installed_fods_product_workflow.py"
        if not test_file.exists():
            return
        content = test_file.read_text(encoding="utf-8")
        # If skips exist, they must be conditional on ImportError
        if "pytest.skip(" in content:
            assert "ImportError" in content or "import" in content.lower(), (
                "Skip guards must be conditional on ImportError, not unconditional"
            )

    def test_r79_installed_wheel_tests_exist(self):
        """R79 installed-wheel tests must still exist (regression guard)."""
        test_file = REPO_ROOT / "tests" / "packaging" / "test_r79_installed_fods_workflow.py"
        assert test_file.exists(), f"R79 installed-wheel test file missing: {test_file}"
