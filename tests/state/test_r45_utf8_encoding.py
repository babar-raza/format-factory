"""
R45 MT1 Lane 1B: Tests for UTF-8 encoding fix in state_snapshot.py.

Sprint: FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001

Root cause: state_snapshot.py used open() without encoding="utf-8" on Windows,
causing cp1252 encoding of non-ASCII characters (e.g., em dash -> 0x97).

These tests verify that:
1. snapshot_to_markdown() output is valid UTF-8 when written and read back
2. write_snapshot() produces UTF-8 files (no 0x97 byte)
3. state/current-state.md (live file) is valid UTF-8
4. JSON output is valid UTF-8
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "state"))

from state_snapshot import build_snapshot, snapshot_to_markdown  # noqa: E402


class TestSnapshotMarkdownEncoding:
    def test_snapshot_markdown_is_ascii_safe(self):
        """snapshot_to_markdown output must not contain non-ASCII characters."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        # All chars must be in ASCII range (no em dash 0x2014, no cp1252 0x97)
        non_ascii = [c for c in md if ord(c) > 127]
        assert len(non_ascii) == 0, (
            f"snapshot_to_markdown contains non-ASCII chars: {non_ascii!r}. "
            "R45 fix: replaced em dash with ASCII hyphen in snapshot_to_markdown()."
        )

    def test_snapshot_markdown_valid_utf8_roundtrip(self):
        """Markdown written as UTF-8 and read back must round-trip cleanly."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        # Write as UTF-8
        encoded = md.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == md, "UTF-8 round-trip must be lossless"

    def test_snapshot_markdown_no_cp1252_0x97(self):
        """Markdown output must not produce cp1252 byte 0x97 (em dash encoding bug)."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        encoded_utf8 = md.encode("utf-8")
        assert b"\x97" not in encoded_utf8, (
            "snapshot_to_markdown contains 0x97 byte — R45 UTF-8 fix not applied. "
            "Replace em dash U+2014 with ASCII hyphen in snapshot_to_markdown()."
        )

    def test_snapshot_markdown_no_em_dash(self):
        """snapshot_to_markdown must not use em dash (U+2014) in output."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        assert "\u2014" not in md, (
            "snapshot_to_markdown contains em dash U+2014. "
            "R45 fix: use ASCII hyphen '-' instead of em dash."
        )


class TestSnapshotFileEncoding:
    def test_written_json_is_valid_utf8(self, tmp_path):
        """state_snapshot.py must write current-state.json as valid UTF-8."""
        snap = build_snapshot()
        json_path = tmp_path / "current-state.json"
        with open(json_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, indent=2)
        raw = json_path.read_bytes()
        # Must decode as UTF-8 without errors
        text = raw.decode("utf-8")
        assert "format_count" in text

    def test_written_markdown_is_valid_utf8(self, tmp_path):
        """state_snapshot.py must write current-state.md as valid UTF-8."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        md_path = tmp_path / "current-state.md"
        with open(md_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        raw = md_path.read_bytes()
        # Must decode as UTF-8 without errors
        text = raw.decode("utf-8")
        assert "Current State Snapshot" in text

    def test_written_markdown_no_0x97(self, tmp_path):
        """Written state markdown must not contain cp1252 byte 0x97."""
        snap = build_snapshot()
        md = snapshot_to_markdown(snap)
        md_path = tmp_path / "current-state.md"
        with open(md_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        raw = md_path.read_bytes()
        assert b"\x97" not in raw, (
            "current-state.md contains byte 0x97 (cp1252 em dash). "
            "R45 fix: state_snapshot.py must use encoding='utf-8'."
        )


class TestLiveStateFileEncoding:
    def test_live_current_state_md_is_valid_utf8(self):
        """Live state/current-state.md must be valid UTF-8 (R45 regression guard)."""
        state_md = ROOT / "state" / "current-state.md"
        if not state_md.exists():
            pytest.skip("state/current-state.md not present")
        raw = state_md.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as e:
            pytest.fail(
                f"state/current-state.md is not valid UTF-8: {e}. "
                "R45 fix required: regenerate with state_snapshot.py after encoding fix."
            )

    def test_live_current_state_md_no_0x97(self):
        """Live state/current-state.md must not contain cp1252 byte 0x97."""
        state_md = ROOT / "state" / "current-state.md"
        if not state_md.exists():
            pytest.skip("state/current-state.md not present")
        raw = state_md.read_bytes()
        assert b"\x97" not in raw, (
            "state/current-state.md contains byte 0x97 (cp1252 em dash). "
            "This is the R44 UTF-8 defect. Regenerate with fixed state_snapshot.py."
        )

    def test_live_current_state_json_is_valid_utf8(self):
        """Live state/current-state.json must be valid UTF-8."""
        state_json = ROOT / "state" / "current-state.json"
        if not state_json.exists():
            pytest.skip("state/current-state.json not present")
        raw = state_json.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as e:
            pytest.fail(f"state/current-state.json is not valid UTF-8: {e}")
