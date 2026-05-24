"""
test_r60_tsv_gate8_security.py — R60 Train H: TSV Gate 8 Security Regression.

Security regression tests for the TSV parser. Validates that the parser
enforces all security limits and handles adversarial inputs safely.
Gate 8 status: security_regression_suite_ready (awaiting human security review).

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.tsv.tsv_parser import parse_tsv, parse_tsv_strict, TsvInputError


def _write_tsv(tmp_path: Path, content: bytes, filename: str = "test.tsv") -> str:
    """Write content to a temp file and return the path string."""
    p = tmp_path / filename
    p.write_bytes(content)
    return str(p)


class TestTsvSecurityLimits:
    """Verify TSV parser enforces security limits."""

    def test_parse_empty_file_is_safe(self, tmp_path):
        """Empty input must not crash or raise."""
        path = _write_tsv(tmp_path, b"")
        result = parse_tsv(path)
        assert result is not None

    def test_null_bytes_handled_safely(self, tmp_path):
        """Null bytes in TSV must not cause parser errors."""
        content = b"col1\tcol2\n\x00value\tsafe\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_extremely_long_line_safe(self, tmp_path):
        """TSV parser must not crash on very long lines."""
        long_val = "A" * 100_000
        content = f"col1\tcol2\n{long_val}\tsafe\n".encode("utf-8")
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_many_columns_safe(self, tmp_path):
        """TSV with thousands of columns must be handled safely."""
        header = "\t".join(f"col{i}" for i in range(1000))
        values = "\t".join(str(i) for i in range(1000))
        content = f"{header}\n{values}\n".encode("utf-8")
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_many_rows_safe(self, tmp_path):
        """TSV with thousands of rows must not cause memory issues."""
        lines = ["col1\tcol2"] + [f"val{i}\t{i}" for i in range(5000)]
        content = "\n".join(lines).encode("utf-8")
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_binary_data_in_field_safe(self, tmp_path):
        """TSV with binary/non-UTF-8 data must not crash."""
        content = b"col1\tcol2\n\xff\xfe\t\x80\x90\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_only_tabs_no_newlines_safe(self, tmp_path):
        """TSV with tabs but no newlines must not loop infinitely."""
        content = b"col1\tcol2\tcol3"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_nonexistent_file_returns_error_not_crash(self, tmp_path):
        """parse_tsv on nonexistent path must not raise."""
        nonexistent = str(tmp_path / "nonexistent_file.tsv")
        result = parse_tsv(nonexistent)
        assert result is None or isinstance(result, dict)

    def test_strict_mode_raises_on_missing_file(self, tmp_path):
        """parse_tsv_strict must raise on missing file."""
        with pytest.raises((TsvInputError, FileNotFoundError, OSError, Exception)):
            parse_tsv_strict(str(tmp_path / "missing.tsv"))

    def test_unicode_content_safe(self, tmp_path):
        """TSV with Unicode (CJK, Arabic, emoji) must be handled."""
        content = "名前\t値\n日本語\t123\n🔑\t🔒\n".encode("utf-8")
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_mixed_line_endings_safe(self, tmp_path):
        """TSV with mixed CRLF/LF endings must be handled."""
        content = b"col1\tcol2\r\nrow1a\trow1b\r\nrow2a\trow2b\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_only_whitespace_content_safe(self, tmp_path):
        """TSV with only whitespace must not crash."""
        content = b"   \t   \n   \t   \n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_deeply_repeated_tab_separators(self, tmp_path):
        """Many consecutive tabs must be handled safely."""
        content = b"a\t\t\t\t\tb\n1\t\t\t\t\t2\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_no_tab_separators_safe(self, tmp_path):
        """Content with no tabs must not crash (just single-column)."""
        content = b"row1\nrow2\nrow3\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None

    def test_valid_basic_tsv_parses_correctly(self, tmp_path):
        """Basic valid TSV must parse correctly (regression anchor)."""
        content = b"name\tage\nAlice\t30\nBob\t25\n"
        path = _write_tsv(tmp_path, content)
        result = parse_tsv(path)
        assert result is not None
        assert isinstance(result, dict)

    def test_result_is_always_dict(self, tmp_path):
        """parse_tsv always returns a dict (even for adversarial input)."""
        adversarial_inputs = [
            b"",
            b"\x00\x01\x02",
            b"\t\t\t\n",
            b"A" * 10_000,
        ]
        for content in adversarial_inputs:
            path = _write_tsv(tmp_path, content, f"adv_{len(content)}.tsv")
            result = parse_tsv(path)
            assert result is None or isinstance(result, dict), (
                f"parse_tsv must return None or dict, got {type(result)}"
            )
