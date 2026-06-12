"""
test_r74_rejects_validation_command_log_pending.py

R74 Train B: Validator must reject bundles where validation-command-log.txt
contains '-> PENDING' (full suite result never filled in).

Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_no_pending_reports


def _make_meta(fname: str, content: str) -> dict:
    return {fname: content}


class TestRejectsCommandLogPending:
    """R74: validation-command-log.txt with '-> PENDING' must be rejected."""

    def test_suite_pending_detected_in_command_log(self):
        metadata = _make_meta(
            "validation-command-log.txt",
            "1. Build packages: 10/10 built\n"
            "2. .NET tests: 161 PASS\n"
            "3. Full test suite:\n"
            "   .local/venv/Scripts/python -m pytest tests/ -q -> PENDING\n"
            "VALIDATION_COMMAND_LOG: COMPLETE\n"
        )
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "'-> PENDING' in command log must be detected"
        assert any("validation-command-log.txt" in f for f, _ in hits)

    def test_full_suite_pending_detected(self):
        metadata = _make_meta(
            "validation-command-log.txt",
            "full suite -> PENDING\n"
        )
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0

    def test_clean_command_log_passes(self):
        metadata = _make_meta(
            "validation-command-log.txt",
            "1. Full test suite:\n"
            "   .local/venv/Scripts/python -m pytest tests/ -q\n"
            "   Result: 6120 passed, 0 failed, 30 skipped\n"
            "AUTHORITATIVE_TEST_RESULT: 6120 passed, 0 failed, 30 skipped\n"
            "VALIDATION_COMMAND_LOG: COMPLETE\n"
        )
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0, f"Clean command log must pass but got: {hits}"

    def test_r73_stale_command_log_rejected(self):
        """Prove the exact R73 stale command log would now fail."""
        r73_stale = (
            "4. R73 new tests:\n"
            "   .local/venv/Scripts/python -m pytest tests/python/fods/test_r73_fods_merged_cell_span.py -> 8 PASS\n"
            "5. Full test suite:\n"
            "   .local/venv/Scripts/python -m pytest tests/ [--ignore model_discovery] -q -> PENDING\n"
            "VALIDATION_COMMAND_LOG: COMPLETE\n"
        )
        metadata = _make_meta("validation-command-log.txt", r73_stale)
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "R73-style stale command log must now be rejected"
