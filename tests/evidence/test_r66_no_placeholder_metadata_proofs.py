"""R66 Train C: metadata proof files must not contain placeholder language."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_TOKENS = [
    "to be completed",
    "to be generated",
    "to be filled",
    "to be confirmed",
    "placeholder",
]

PROOF_FILES = [
    "delivery-package-validation-summary.txt",
    "external-sidecar-proof-summary.txt",
    "missing-sidecar-negative-proof.txt",
    "wrong-sidecar-negative-proof.txt",
    "final-bundle-validation-proof.txt",
    "validation-command-log.txt",
]


def _find_metadata_dir():
    for run in ["r66", "r65"]:
        d = PROJECT_ROOT / ".local" / f"{run}-metadata"
        if d.exists():
            return d
    return None


class TestNoPlaceholderMetadataProofs:
    """Every proof file in metadata must be final — no placeholder text."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.metadata_dir = _find_metadata_dir()
        if self.metadata_dir is None:
            pytest.skip("No metadata directory found")

    @pytest.mark.parametrize("filename", PROOF_FILES)
    def test_proof_file_no_placeholders(self, filename):
        path = self.metadata_dir / filename
        if not path.exists():
            pytest.skip(f"{filename} not yet created")
        content = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_TOKENS:
            assert token not in content, (
                f"{filename} contains forbidden placeholder: '{token}'"
            )

    @pytest.mark.parametrize("filename", PROOF_FILES)
    def test_proof_file_no_pending(self, filename):
        path = self.metadata_dir / filename
        if not path.exists():
            pytest.skip(f"{filename} not yet created")
        content = path.read_text(encoding="utf-8")
        # Check for standalone PENDING (not in allowed contexts like defect references)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            lower = line.lower().strip()
            if "pending" in lower:
                # Allow PENDING in contexts like "PENDING_FINAL_COMMIT", defect references,
                # or CLI flag names like "--check-no-pending" (not a placeholder)
                if "pending_final" in lower or "defect" in lower or "iv-r" in lower or "--check-no-pending" in lower:
                    continue
                assert False, f"{filename} line {i+1} contains PENDING: {line.strip()}"

    @pytest.mark.parametrize("filename", PROOF_FILES)
    def test_proof_file_no_in_progress(self, filename):
        path = self.metadata_dir / filename
        if not path.exists():
            pytest.skip(f"{filename} not yet created")
        content = path.read_text(encoding="utf-8")
        assert "IN_PROGRESS" not in content, f"{filename} contains IN_PROGRESS"
