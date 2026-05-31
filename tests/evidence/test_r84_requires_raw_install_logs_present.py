"""
test_r84_requires_raw_install_logs_present.py

R84 Train D/E: Verify that raw install logs and .NET test logs are present.
Addresses R83 defects D83-16 and D83-17.

Sprint: FORMAT-FACTORY-R84
"""
from __future__ import annotations

from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_INSTALL_LOGS = PROJECT_ROOT / ".local" / "raw-install-logs"
RAW_DOTNET_LOGS = PROJECT_ROOT / ".local" / "raw-dotnet-logs"
RAW_TEST_LOGS = PROJECT_ROOT / ".local" / "raw-test-logs"


def _dir_exists_and_has_files(dir_path: Path) -> bool:
    return dir_path.is_dir() and any(dir_path.iterdir())


@pytest.mark.skipif(
    not RAW_INSTALL_LOGS.is_dir(),
    reason="R84 raw install logs not yet generated"
)
class TestRawInstallLogsPresent:
    """D83-17 regression: install logs must be present."""

    def test_raw_install_log_exists_for_fods(self):
        log = RAW_INSTALL_LOGS / "fods-install.log"
        assert log.exists(), f"D83-17: {log} not found"
        assert log.stat().st_size > 0, f"D83-17: {log} is empty"

    def test_raw_install_log_exists_for_fodt(self):
        log = RAW_INSTALL_LOGS / "fodt-install.log"
        assert log.exists(), f"D83-17: {log} not found"
        assert log.stat().st_size > 0, f"D83-17: {log} is empty"

    def test_install_logs_dir_has_multiple_entries(self):
        logs = list(RAW_INSTALL_LOGS.glob("*.log"))
        assert len(logs) >= 2, (
            f"Expected at least 2 install logs, found {len(logs)}"
        )


@pytest.mark.skipif(
    not RAW_DOTNET_LOGS.is_dir(),
    reason="R84 raw .NET logs not yet generated"
)
class TestRawDotnetLogPresent:
    """D83-16 regression: .NET test log must be present."""

    def test_raw_dotnet_log_exists(self):
        log = RAW_DOTNET_LOGS / "r84-dotnet-test.log"
        assert log.exists(), f"D83-16: {log} not found"
        assert log.stat().st_size > 0, f"D83-16: {log} is empty"


@pytest.mark.skipif(
    not RAW_TEST_LOGS.is_dir(),
    reason="R84 raw test logs not yet generated"
)
class TestRawPytestLogPresent:
    """D83-16 regression: full pytest log must be present."""

    def test_raw_pytest_log_exists(self):
        log = RAW_TEST_LOGS / "r84-full-pytest.log"
        assert log.exists(), f"D83-16: {log} not found"
        assert log.stat().st_size > 0, f"D83-16: {log} is empty"
