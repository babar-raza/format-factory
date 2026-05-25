"""
test_r63_sidecar_not_inside_zip.py — R63 Train C: sidecar must NOT be inside the ZIP bundle.

Verifies:
1. R63 contract declares sidecar as external (not embedded in ZIP).
2. When R63 bundle exists locally, sidecar JSON is NOT inside the ZIP.
3. Gitignore pattern prevents accidental commit of sidecar.
4. The external sidecar policy is consistently enforced across contracts.

DESIGN NOTE (IV-R62-004 repair):
All ZIP-dependent checks skip gracefully when .local/r63-pass2-final.zip is absent.
This ensures clean-checkout compatibility.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
IV-R62-001 (sidecar not delivered — external delivery enforcement)
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


R63_CONTRACT_PATH = (
    PROJECT_ROOT / "tools" / "evidence" / "contracts"
    / "r63-ai-assisted-rc-closure-and-workahead.yaml"
)
R63_ZIP_PATH = PROJECT_ROOT / ".local" / "r63-pass2-final.zip"
R63_SIDECAR_PATH = (
    PROJECT_ROOT / "reports" / "r63" / "r63-pass2-final.zip.sha256-proof.json"
)
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"


class TestR63ContractExternalSidecarPolicy:
    """R63 contract must declare external sidecar (not embedded)."""

    def test_contract_exists(self):
        assert R63_CONTRACT_PATH.exists()

    def test_contract_final_proof_policy_external_sidecar(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in content, (
            "R63 contract must declare final_proof_policy: external_sidecar"
        )

    def test_contract_sidecar_required_true(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content

    def test_contracts_consistently_use_external_sidecar(self):
        """Both R62 and R63 contracts must use external_sidecar policy."""
        contracts_dir = PROJECT_ROOT / "tools" / "evidence" / "contracts"
        for contract_file in ["r62-ai-accelerated-sidecar-python-rc.yaml",
                              "r63-ai-assisted-rc-closure-and-workahead.yaml"]:
            path = contracts_dir / contract_file
            if path.exists():
                content = path.read_text(encoding="utf-8")
                assert "final_proof_policy: external_sidecar" in content, (
                    f"{contract_file} must declare final_proof_policy: external_sidecar"
                )


class TestR63GitignoreSidecarExclusion:
    """Gitignore must prevent sidecar from being accidentally committed."""

    def test_gitignore_has_sha256_proof_pattern(self):
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert ".sha256-proof.json" in content, (
            "Gitignore must exclude *.sha256-proof.json files"
        )

    def test_r63_sidecar_not_in_git_index(self):
        """R63 sidecar file must not be tracked by git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "reports/r63/r63-pass2-final.zip.sha256-proof.json"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        assert result.stdout.strip() == "", (
            "R63 sidecar must NOT be in git index (external delivery policy)"
        )

    def test_r62_sidecar_not_in_git_index(self):
        """R62 sidecar must also not be tracked by git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "reports/r62/r62-pass2-final.zip.sha256-proof.json"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        assert result.stdout.strip() == "", (
            "R62 sidecar must NOT be in git index (external delivery policy)"
        )


class TestR63SidecarNotInsideZip:
    """When R63 ZIP exists locally, sidecar must NOT be inside it."""

    def test_r63_zip_sidecar_not_inside_if_zip_present(self):
        if not R63_ZIP_PATH.exists():
            pytest.skip(f"R63 ZIP not present (local dev only after Train M): {R63_ZIP_PATH}")
        with zipfile.ZipFile(R63_ZIP_PATH, "r") as zf:
            names = zf.namelist()
        sidecar_entries = [n for n in names if n.endswith(".sha256-proof.json")]
        assert sidecar_entries == [], (
            f"R63 ZIP must NOT contain sidecar file inside; found: {sidecar_entries}"
        )

    def test_r63_zip_has_entries_if_present(self):
        if not R63_ZIP_PATH.exists():
            pytest.skip("R63 ZIP not present (local dev only after Train M)")
        with zipfile.ZipFile(R63_ZIP_PATH, "r") as zf:
            names = zf.namelist()
        assert len(names) > 0, "R63 ZIP must have entries"

    def test_r63_sidecar_exists_alongside_zip_if_zip_present(self):
        if not R63_ZIP_PATH.exists():
            pytest.skip("R63 ZIP not present (local dev only after Train M)")
        assert R63_SIDECAR_PATH.exists(), (
            f"R63 sidecar must exist alongside ZIP at: {R63_SIDECAR_PATH}\n"
            "Sidecar is delivered externally, not inside ZIP."
        )

    def test_r62_zip_sidecar_not_inside_if_zip_present(self):
        r62_zip = PROJECT_ROOT / ".local" / "r62-pass2-final.zip"
        if not r62_zip.exists():
            pytest.skip("R62 ZIP not present (local dev only)")
        with zipfile.ZipFile(r62_zip, "r") as zf:
            names = zf.namelist()
        sidecar_entries = [n for n in names if n.endswith(".sha256-proof.json")]
        assert sidecar_entries == [], (
            f"R62 ZIP must NOT contain sidecar inside; found: {sidecar_entries}"
        )
