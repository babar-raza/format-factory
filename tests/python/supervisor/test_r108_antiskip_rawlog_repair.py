"""R108 Wave 2: Anti-skip raw-log detection repair tests.

Verify that detect_missing_raw_logs() finds logs in subdirectories
and accepts both 'raw_log' and 'raw-log' artifact types.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from anti_skip_checker import detect_missing_raw_logs  # noqa: E402


class TestRawLogSubdirectoryDetection:
    """Logs in raw-logs/ subdirectory should be found."""

    def test_log_in_raw_logs_subdir(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            raw_logs = tmp / "raw-logs"
            raw_logs.mkdir()
            (raw_logs / "test-all-supervisors.log").write_text("test output", encoding="utf-8")
            result = detect_missing_raw_logs(tmp)
            assert not result["is_violation"]
            assert len(result["logs_found"]) >= 1

    def test_log_at_top_level(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "raw-test-log.txt").write_text("test output", encoding="utf-8")
            result = detect_missing_raw_logs(tmp)
            assert not result["is_violation"]

    def test_no_logs_anywhere(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "readme.md").write_text("hello", encoding="utf-8")
            result = detect_missing_raw_logs(tmp)
            assert result["is_violation"]


class TestRawLogArtifactTypeMatch:
    """Declaration artifacts with type 'raw-log' (hyphen) should be found."""

    def test_raw_hyphen_log_type_accepted(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            log_file = tmp / "my.log"
            log_file.write_text("log data", encoding="utf-8")
            decl = {
                "evidence_artifacts": [
                    {"path": str(log_file), "type": "raw-log"}
                ]
            }
            result = detect_missing_raw_logs(tmp, declaration=decl)
            assert not result["is_violation"]

    def test_raw_underscore_log_type_accepted(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            log_file = tmp / "my.log"
            log_file.write_text("log data", encoding="utf-8")
            decl = {
                "evidence_artifacts": [
                    {"path": str(log_file), "type": "raw_log"}
                ]
            }
            result = detect_missing_raw_logs(tmp, declaration=decl)
            assert not result["is_violation"]

    def test_wrong_type_not_matched(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            log_file = tmp / "data.json"
            log_file.write_text("{}", encoding="utf-8")
            decl = {
                "evidence_artifacts": [
                    {"path": str(log_file), "type": "transcript-json"}
                ]
            }
            result = detect_missing_raw_logs(tmp, declaration=decl)
            assert result["is_violation"]
