"""TC-S6P4-FINAL-001b (select-6 Phase 4 final re-audit): V231 gate9
grandfather baseline integrity digest.

Closes the residual half of SF1: registry/gate9-coverage-baseline.yaml's
"write-once, do not add a new format" rule was a comment with zero
mechanical enforcement until this validator existed.
"""
from __future__ import annotations

import hashlib

import yaml

from governance_validators_gate9_baseline_integrity import (
    _EXPECTED_BASELINE_SHA256,
    validate_gate9_baseline_integrity as v231,
)

_PINNED_FORMATS = ["zst", "fodp", "fodg", "gnumeric", "abw", "ndjson", "toml"]


def _write_baseline(tmp_path, format_ids):
    (tmp_path / "registry").mkdir(parents=True, exist_ok=True)
    entries = [{"format_id": f} for f in format_ids]
    (tmp_path / "registry" / "gate9-coverage-baseline.yaml").write_text(
        yaml.safe_dump({"grandfathered_pre_phase3": entries}), encoding="utf-8"
    )


class TestV231:
    def test_no_baseline_file_warns(self, tmp_path):
        r = v231({}, tmp_path)
        assert r["result"] == "WARN"
        assert r["blocks_sprint"] is False

    def test_pinned_set_passes(self, tmp_path):
        _write_baseline(tmp_path, _PINNED_FORMATS)
        r = v231({}, tmp_path)
        assert r["result"] == "PASS"
        assert r["blocks_sprint"] is False

    def test_pinned_set_order_independent(self, tmp_path):
        """The digest is over the sorted set, so YAML re-ordering (e.g. from
        a formatting pass) must not trip the validator."""
        _write_baseline(tmp_path, list(reversed(_PINNED_FORMATS)))
        assert v231({}, tmp_path)["result"] == "PASS"

    def test_silently_added_format_fails(self, tmp_path):
        """The exact attack this validator closes: appending a new
        format_id to dodge V227/V228/V229 without updating the pinned
        digest."""
        _write_baseline(tmp_path, _PINNED_FORMATS + ["sneaky_new_format"])
        r = v231({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True
        assert "drifted" in r["summary"]

    def test_removed_format_fails(self, tmp_path):
        _write_baseline(tmp_path, _PINNED_FORMATS[:-1])
        r = v231({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True

    def test_empty_baseline_fails(self, tmp_path):
        _write_baseline(tmp_path, [])
        r = v231({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True

    def test_pinned_digest_matches_pinned_format_list(self):
        """Guards the pinned constant itself against a silent hand-edit of
        _EXPECTED_BASELINE_SHA256 that isn't backed by the documented
        7-format set."""
        canon = "|".join(sorted(_PINNED_FORMATS))
        assert hashlib.sha256(canon.encode("utf-8")).hexdigest() == _EXPECTED_BASELINE_SHA256

    def test_live_repo_baseline_passes(self):
        """Regression proof: the real repo's baseline file matches the
        pinned digest right now."""
        from pathlib import Path

        repo = Path(__file__).resolve().parents[2]
        r = v231({}, repo)
        assert r["result"] == "PASS", r["summary"]
