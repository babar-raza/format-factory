"""Evidence hygiene enforcement tests — per EVIDENCE-HYGIENE-ENFORCEMENT taskcard.

Tests:
1. No pre-commit bundle without emergency flag (P-EVID-001)
2. Authoritative test result line validation (P-EVID-003)
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))


class TestNoPreCommitBundleWithoutEmergency:
    """P-EVID-001: Post-commit bundle preferred.

    Metadata files must not claim BUNDLE_BUILT_BEFORE_COMMIT
    unless emergency_blocker_bundle: true is present.
    """

    def _make_metadata(self, tmp_path, bundle_timing="post_commit", emergency=False):
        meta = {
            "bundle_timing": bundle_timing,
            "emergency_blocker_bundle": emergency,
            "sprint_id": "TEST-SPRINT-001",
        }
        f = tmp_path / "bundle-metadata.json"
        f.write_text(json.dumps(meta), encoding="utf-8")
        return f

    def test_post_commit_bundle_passes(self, tmp_path):
        f = self._make_metadata(tmp_path, bundle_timing="post_commit")
        meta = json.loads(f.read_text(encoding="utf-8"))
        assert meta["bundle_timing"] != "pre_commit" or meta.get("emergency_blocker_bundle")

    def test_pre_commit_with_emergency_flag_passes(self, tmp_path):
        f = self._make_metadata(tmp_path, bundle_timing="pre_commit", emergency=True)
        meta = json.loads(f.read_text(encoding="utf-8"))
        # pre_commit is allowed when emergency_blocker_bundle is True
        if meta["bundle_timing"] == "pre_commit":
            assert meta.get("emergency_blocker_bundle") is True

    def test_pre_commit_without_emergency_flag_fails(self, tmp_path):
        f = self._make_metadata(tmp_path, bundle_timing="pre_commit", emergency=False)
        meta = json.loads(f.read_text(encoding="utf-8"))
        # This should be a policy violation
        is_violation = (
            meta["bundle_timing"] == "pre_commit"
            and not meta.get("emergency_blocker_bundle")
        )
        assert is_violation is True, "pre_commit without emergency flag must be detected as violation"


class TestAuthoritativeTestResultLine:
    """P-EVID-003: Authoritative test result line required.

    validation-command-log.txt must contain an AUTHORITATIVE_TEST_RESULT line
    in the format: AUTHORITATIVE_TEST_RESULT: <N> passed, <M> skipped (scope: full_suite)
    """

    def _make_log(self, tmp_path, content):
        f = tmp_path / "validation-command-log.txt"
        f.write_text(content, encoding="utf-8")
        return f

    def _has_authoritative_line(self, path):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("AUTHORITATIVE_TEST_RESULT:"):
                # Validate format: "N passed, M skipped (scope: ...)"
                rest = line.split(":", 1)[1].strip()
                if "passed" in rest and "scope:" in rest:
                    return True
        return False

    def test_valid_authoritative_line(self, tmp_path):
        log = self._make_log(
            tmp_path,
            "Running tests...\nAUTHORITATIVE_TEST_RESULT: 12605 passed, 42 skipped (scope: full_suite)\nDone.",
        )
        assert self._has_authoritative_line(log) is True

    def test_missing_authoritative_line(self, tmp_path):
        log = self._make_log(tmp_path, "Running tests...\n12605 passed\nDone.")
        assert self._has_authoritative_line(log) is False

    def test_malformed_authoritative_line(self, tmp_path):
        log = self._make_log(
            tmp_path, "AUTHORITATIVE_TEST_RESULT: some random text without passed"
        )
        assert self._has_authoritative_line(log) is False

    def test_authoritative_line_with_scope(self, tmp_path):
        log = self._make_log(
            tmp_path,
            "AUTHORITATIVE_TEST_RESULT: 500 passed, 10 skipped (scope: tests/python/)",
        )
        assert self._has_authoritative_line(log) is True
