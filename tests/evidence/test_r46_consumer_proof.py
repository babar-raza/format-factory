"""
R46 consumer proof replayability tests — MT3.

Verifies that FODS and FODT .NET consumer projects can be:
1. Restored using a NuGet feed derived from bundle-metadata/package-artifacts/
2. Run successfully, printing PASS output

This closes R45 blocker #2: in R45, consumer proof used .local/consumer-proof/local-feed/
which is gitignored. R46 proves the consumer is replayable from bundled artifacts.

Key difference from R45 test_r45_consumer_proof.py:
- R45: checks .local/consumer-proof/ directory (gitignored, not in bundle)
- R46: checks .local/r46-metadata/package-artifacts/ (included in bundle-metadata/)
"""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PACKAGE_ARTIFACTS = REPO_ROOT / ".local" / "r46-metadata" / "package-artifacts"
CONSUMER_PROOF_R46 = REPO_ROOT / ".local" / "consumer-proof-r46"


class TestPackageArtifactsPresent:
    """Verify actual artifact files are in the bundle-able metadata directory."""

    def test_fods_wheel_in_package_artifacts(self):
        """FODS wheel must be in r46-metadata/package-artifacts/ (included in bundle)."""
        wheels = list(PACKAGE_ARTIFACTS.glob("aspose_format_factory_fods-*.whl"))
        assert len(wheels) >= 1, (
            f"No FODS .whl in {PACKAGE_ARTIFACTS}. "
            "R46 requires actual artifacts in bundle-metadata/package-artifacts/ "
            "(not just hashes/manifests as in R45)."
        )

    def test_fodt_wheel_in_package_artifacts(self):
        """FODT wheel must be in r46-metadata/package-artifacts/ (included in bundle)."""
        wheels = list(PACKAGE_ARTIFACTS.glob("aspose_format_factory_fodt-*.whl"))
        assert len(wheels) >= 1, (
            f"No FODT .whl in {PACKAGE_ARTIFACTS}. "
            "R46 requires actual artifacts in bundle-metadata/package-artifacts/."
        )

    def test_fods_nupkg_in_package_artifacts(self):
        """FODS nupkg must be in r46-metadata/package-artifacts/ (included in bundle)."""
        nupkgs = list(PACKAGE_ARTIFACTS.glob("FormatFactory.Fods.*.nupkg"))
        assert len(nupkgs) >= 1, f"No FODS .nupkg in {PACKAGE_ARTIFACTS}"

    def test_fodt_nupkg_in_package_artifacts(self):
        """FODT nupkg must be in r46-metadata/package-artifacts/ (included in bundle)."""
        nupkgs = list(PACKAGE_ARTIFACTS.glob("FormatFactory.Fodt.*.nupkg"))
        assert len(nupkgs) >= 1, f"No FODT .nupkg in {PACKAGE_ARTIFACTS}"


class TestFodsConsumerFromBundledArtifacts:
    """FODS .NET consumer restores and runs from r46-metadata/package-artifacts/."""

    def test_fods_consumer_project_exists(self):
        """R46 FODS consumer project must exist at consumer-proof-r46/fods-consumer/."""
        assert (CONSUMER_PROOF_R46 / "fods-consumer").exists()

    def test_fods_consumer_nuget_config_points_to_package_artifacts(self):
        """nuget.config must reference r46-metadata/package-artifacts/ not .local/consumer-proof/."""
        nuget_cfg = CONSUMER_PROOF_R46 / "nuget.config"
        assert nuget_cfg.exists(), f"nuget.config not found at {nuget_cfg}"
        content = nuget_cfg.read_text(encoding="utf-8")
        assert "r46-metadata/package-artifacts" in content or "r46-metadata\\package-artifacts" in content, (
            "R46 nuget.config must point to r46-metadata/package-artifacts/ "
            "(not .local/consumer-proof/local-feed/ as in R45)"
        )

    def test_fods_consumer_runs_pass(self):
        """dotnet run on FODS consumer must print FODS_CONSUMER_PROOF: PASS."""
        consumer_dir = CONSUMER_PROOF_R46 / "fods-consumer"
        if not consumer_dir.exists():
            pytest.skip("FODS consumer-proof-r46 not present")
        result = subprocess.run(
            ["dotnet", "run"],
            cwd=str(consumer_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = result.stdout + result.stderr
        assert "FODS_CONSUMER_PROOF: PASS" in output, (
            f"FODS consumer run did not print PASS.\nOutput: {output}"
        )
        assert result.returncode == 0

    def test_fods_consumer_sheet_count_at_least_one(self):
        """FODS consumer output must show sheet_count >= 1."""
        consumer_dir = CONSUMER_PROOF_R46 / "fods-consumer"
        if not consumer_dir.exists():
            pytest.skip("FODS consumer-proof-r46 not present")
        result = subprocess.run(
            ["dotnet", "run"],
            cwd=str(consumer_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = result.stdout + result.stderr
        import re
        m = re.search(r"sheet_count=(\d+)", output)
        assert m is not None, f"sheet_count not in output: {output}"
        assert int(m.group(1)) >= 1


class TestFodtConsumerFromBundledArtifacts:
    """FODT .NET consumer restores and runs from r46-metadata/package-artifacts/."""

    def test_fodt_consumer_project_exists(self):
        """R46 FODT consumer project must exist at consumer-proof-r46/fodt-consumer/."""
        assert (CONSUMER_PROOF_R46 / "fodt-consumer").exists()

    def test_fodt_consumer_runs_pass(self):
        """dotnet run on FODT consumer must print FODT_CONSUMER_PROOF: PASS."""
        consumer_dir = CONSUMER_PROOF_R46 / "fodt-consumer"
        if not consumer_dir.exists():
            pytest.skip("FODT consumer-proof-r46 not present")
        result = subprocess.run(
            ["dotnet", "run"],
            cwd=str(consumer_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = result.stdout + result.stderr
        assert "FODT_CONSUMER_PROOF: PASS" in output, (
            f"FODT consumer run did not print PASS.\nOutput: {output}"
        )
        assert result.returncode == 0

    def test_fodt_consumer_paragraph_count_at_least_one(self):
        """FODT consumer output must show paragraph_count >= 1."""
        consumer_dir = CONSUMER_PROOF_R46 / "fodt-consumer"
        if not consumer_dir.exists():
            pytest.skip("FODT consumer-proof-r46 not present")
        result = subprocess.run(
            ["dotnet", "run"],
            cwd=str(consumer_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = result.stdout + result.stderr
        import re
        m = re.search(r"paragraph_count=(\d+)", output)
        assert m is not None, f"paragraph_count not in output: {output}"
        assert int(m.group(1)) >= 1
