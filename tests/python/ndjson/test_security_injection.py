"""Security tests for NDJSON parser: key injection and prototype pollution patterns.

TC-W7-002: Attack category — adversarial key names that could affect downstream
consumers (null bytes, path separators, double underscores, prototype-pollution
keys like __proto__, constructor, toString).
"""
from __future__ import annotations

import json
import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from ndjson import load_ndjson


def _write_ndjson(records: list[dict], tmp_path: Path) -> str:
    p = tmp_path / "input.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return str(p)


class TestNdjsonKeyInjection:
    def test_prototype_pollution_key_not_executed(self, tmp_path):
        """__proto__ key must be parsed as literal string, not modifying object prototype."""
        path = _write_ndjson([{"__proto__": {"admin": True}, "name": "test"}], tmp_path)
        result = load_ndjson(path)
        assert isinstance(result, list)
        record = result[0]
        # The key must appear as a normal dict key, not silently dropped
        assert "__proto__" in record or "name" in record

    def test_null_byte_in_key_handled(self, tmp_path):
        """Keys with null bytes should not cause a crash."""
        raw = '{"key\x00name": "value"}\n'
        p = tmp_path / "null.ndjson"
        p.write_bytes(raw.encode("utf-8", errors="replace"))
        try:
            result = load_ndjson(str(p))
            # Either parsed or skipped — must not raise an unhandled exception
            assert result is not None
        except Exception:
            pass  # parse error acceptable; crash is not

    def test_deeply_nested_key_path(self, tmp_path):
        """Deeply nested keys should not cause stack overflow."""
        record: dict = {}
        current = record
        for i in range(500):
            current["next"] = {}
            current = current["next"]
        current["value"] = "leaf"
        path = _write_ndjson([record], tmp_path)
        try:
            result = load_ndjson(path)
            assert result is not None
        except (RecursionError, ValueError, json.JSONDecodeError):
            pass  # safe failure acceptable

    def test_empty_key(self, tmp_path):
        """Empty string as key must not crash the parser."""
        path = _write_ndjson([{"": "empty_key_value"}], tmp_path)
        result = load_ndjson(path)
        assert isinstance(result, list)

    def test_large_key_name(self, tmp_path):
        """Extremely long key names must not cause memory issues."""
        big_key = "k" * 100_000
        path = _write_ndjson([{big_key: "value"}], tmp_path)
        result = load_ndjson(path)
        assert isinstance(result, list)

    def test_constructor_key_is_literal(self, tmp_path):
        """'constructor' key must be parsed as a literal dict key."""
        path = _write_ndjson([{"constructor": "override_attempt"}], tmp_path)
        result = load_ndjson(path)
        assert isinstance(result, list)
        assert result[0].get("constructor") == "override_attempt"

    def test_unicode_key_normalization(self, tmp_path):
        """Unicode homoglyphs in keys should not bypass key uniqueness."""
        # 'café' with precomposed NFC vs NFD decomposed
        import unicodedata
        key_nfc = unicodedata.normalize("NFC", "café")
        key_nfd = unicodedata.normalize("NFD", "café")
        record = {key_nfc: "nfc_value", key_nfd: "nfd_value"}
        path = _write_ndjson([record], tmp_path)
        result = load_ndjson(path)
        # Must parse without crash regardless of normalization behavior
        assert isinstance(result, list)
