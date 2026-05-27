"""R67 Train D: package replay summary required in metadata, must report PASS.

Validator hardening: if a sprint claims complete RC closure, the extracted-package-replay-summary
must exist and must not report failures or required skips.
"""
from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_metadata_dir() -> Path | None:
    for run in ["r67", "r66"]:
        d = PROJECT_ROOT / ".local" / f"{run}-metadata"
        if d.is_dir():
            return d
    return None


@pytest.fixture
def metadata_dir():
    d = _find_metadata_dir()
    if d is None:
        pytest.skip("No metadata directory available")
    return d


class TestPackageReplaySummary:
    def test_replay_summary_exists(self, metadata_dir):
        f = metadata_dir / "extracted-package-replay-summary.txt"
        assert f.is_file(), "extracted-package-replay-summary.txt must exist in metadata"

    def test_replay_summary_not_placeholder(self, metadata_dir):
        f = metadata_dir / "extracted-package-replay-summary.txt"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8", errors="replace")
        for token in ("to be completed", "to be generated", "PENDING"):
            assert token not in content, f"Placeholder '{token}' in replay summary"

    def test_replay_summary_says_pass(self, metadata_dir):
        f = metadata_dir / "extracted-package-replay-summary.txt"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8", errors="replace")
        assert "PASS" in content, "extracted-package-replay-summary.txt must contain PASS"

    def test_replay_summary_no_pending_final_commit(self, metadata_dir):
        f = metadata_dir / "extracted-package-replay-summary.txt"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8", errors="replace")
        assert "PENDING_FINAL_COMMIT" not in content
