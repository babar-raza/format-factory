"""
R45 MT4: .NET consumer project proof tests.

Sprint: FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001

Verifies that the .NET FODS and FODT consumer projects:
1. Can be built from the local NuGet feed
2. Produce the expected PASS output when run against real samples
3. Are self-contained (use only the NuGet package, not the source project)

This closes R44 blocker #1 and #11: ".NET consumer project proof not completed".
"""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONSUMER_DIR = REPO_ROOT / ".local" / "consumer-proof"
FODS_CONSUMER = CONSUMER_DIR / "fods-consumer"
FODT_CONSUMER = CONSUMER_DIR / "fodt-consumer"
NUGET_CONFIG = CONSUMER_DIR / "nuget.config"
LOCAL_FEED = CONSUMER_DIR / "local-feed"


def _dotnet_available():
    """Check if dotnet CLI is available."""
    try:
        result = subprocess.run(
            ["dotnet", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture(scope="session", autouse=False)
def dotnet_available():
    if not _dotnet_available():
        pytest.skip("dotnet CLI not available")


class TestFodsConsumerProject:
    """Verify FormatFactory.Fods NuGet package can be restored and used."""

    def test_fods_consumer_project_exists(self):
        """FODS consumer project must exist in .local/consumer-proof/."""
        assert FODS_CONSUMER.exists(), (
            f"FODS consumer project not found at {FODS_CONSUMER}. "
            "R45 MT4: consumer project must be created before this test runs."
        )
        assert (FODS_CONSUMER / "FodsConsumer.csproj").exists()
        assert (FODS_CONSUMER / "Program.cs").exists()

    def test_local_feed_has_fods_nupkg(self):
        """Local NuGet feed must contain FormatFactory.Fods nupkg."""
        assert LOCAL_FEED.exists(), f"Local feed not found: {LOCAL_FEED}"
        nupkgs = list(LOCAL_FEED.glob("FormatFactory.Fods*.nupkg"))
        assert len(nupkgs) >= 1, (
            f"No FormatFactory.Fods nupkg in local feed {LOCAL_FEED}. "
            "Run: dotnet pack src/net/fods/ -o .local/consumer-proof/local-feed/"
        )

    def test_fods_consumer_runs_successfully(self, dotnet_available):
        """FODS consumer project must run and produce PASS output."""
        result = subprocess.run(
            ["dotnet", "run", "--no-restore"],
            capture_output=True, text=True,
            cwd=str(FODS_CONSUMER),
            timeout=60,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"FODS consumer project failed (returncode={result.returncode}). "
            f"Output:\n{combined}"
        )
        assert "FODS_CONSUMER_PROOF: PASS" in combined, (
            f"FODS consumer output did not contain PASS. Output:\n{combined}"
        )
        assert "package_restored=true" in combined
        assert "sheet_count=" in combined

    def test_fods_consumer_sheet_count_positive(self, dotnet_available):
        """FODS consumer must report at least 1 sheet from minimal-spreadsheet.fods."""
        result = subprocess.run(
            ["dotnet", "run", "--no-restore"],
            capture_output=True, text=True,
            cwd=str(FODS_CONSUMER),
            timeout=60,
        )
        import re
        m = re.search(r"sheet_count=(\d+)", result.stdout)
        assert m is not None, f"sheet_count not found in output: {result.stdout}"
        assert int(m.group(1)) >= 1, f"Expected >= 1 sheet, got: {m.group(1)}"


class TestFodtConsumerProject:
    """Verify FormatFactory.Fodt NuGet package can be restored and used."""

    def test_fodt_consumer_project_exists(self):
        """FODT consumer project must exist in .local/consumer-proof/."""
        assert FODT_CONSUMER.exists(), (
            f"FODT consumer project not found at {FODT_CONSUMER}."
        )
        assert (FODT_CONSUMER / "FodtConsumer.csproj").exists()
        assert (FODT_CONSUMER / "Program.cs").exists()

    def test_local_feed_has_fodt_nupkg(self):
        """Local NuGet feed must contain FormatFactory.Fodt nupkg."""
        assert LOCAL_FEED.exists(), f"Local feed not found: {LOCAL_FEED}"
        nupkgs = list(LOCAL_FEED.glob("FormatFactory.Fodt*.nupkg"))
        assert len(nupkgs) >= 1, (
            f"No FormatFactory.Fodt nupkg in local feed {LOCAL_FEED}."
        )

    def test_fodt_consumer_runs_successfully(self, dotnet_available):
        """FODT consumer project must run and produce PASS output."""
        result = subprocess.run(
            ["dotnet", "run", "--no-restore"],
            capture_output=True, text=True,
            cwd=str(FODT_CONSUMER),
            timeout=60,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"FODT consumer project failed (returncode={result.returncode}). "
            f"Output:\n{combined}"
        )
        assert "FODT_CONSUMER_PROOF: PASS" in combined, (
            f"FODT consumer output did not contain PASS. Output:\n{combined}"
        )
        assert "package_restored=true" in combined
        assert "paragraph_count=" in combined

    def test_fodt_consumer_paragraph_count_positive(self, dotnet_available):
        """FODT consumer must report at least 1 paragraph from minimal-document.fodt."""
        result = subprocess.run(
            ["dotnet", "run", "--no-restore"],
            capture_output=True, text=True,
            cwd=str(FODT_CONSUMER),
            timeout=60,
        )
        import re
        m = re.search(r"paragraph_count=(\d+)", result.stdout)
        assert m is not None, f"paragraph_count not found in output: {result.stdout}"
        assert int(m.group(1)) >= 1, f"Expected >= 1 paragraph, got: {m.group(1)}"
