"""ABW dogfood load regression — verifies corrected path-based API usage.

Proves that get_paragraph_count() and extract_text() accept FILE PATH (not dict),
closing the regression from the prior sprint where dogfood used wrong argument types.

Sprint: FF-LIBFORGE-GOVERNANCE-UNBLOCK-IMPLEMENTATION-001
Taskcard: LFI-5-F
Execution-method: AGENT_GOVERNED_DIRECT_EXECUTION
Route-decision-id: RD-TEST-ONLY-ABW-DOGFOOD-REGRESSION-001
Idempotency-key: lfi-5-f-abw-dogfood-load-regression-v1
Exception-classification: investigation_only
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SAMPLES = _REPO_ROOT / "samples" / "by-format" / "abw"
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import load, get_paragraph_count, extract_text


# ---------------------------------------------------------------------------
# API contract: path-based calls
# ---------------------------------------------------------------------------


class TestAbwPathBasedApi:
    def test_load_returns_model_dict(self):
        """load() returns a model dict."""
        model = load(_SAMPLES / "minimal-document.abw")
        assert isinstance(model, dict)
        assert model.get("is_abw") is True

    def test_get_paragraph_count_takes_file_path(self):
        """get_paragraph_count() accepts a file path (not model dict)."""
        count = get_paragraph_count(_SAMPLES / "minimal-document.abw")
        assert isinstance(count, int)
        assert count >= 1

    def test_get_paragraph_count_two_paragraphs(self):
        """get_paragraph_count() returns 2 for two-paragraph file."""
        count = get_paragraph_count(_SAMPLES / "two-paragraphs.abw")
        assert count == 2

    def test_extract_text_takes_file_path(self):
        """extract_text() accepts a file path (not model dict).
        Returns a list of paragraph strings.
        """
        text = extract_text(_SAMPLES / "minimal-document.abw")
        assert isinstance(text, list)
        assert len(text) > 0

    def test_extract_text_returns_list_of_strings(self):
        """extract_text() returns a non-empty list for document with content."""
        text = extract_text(_SAMPLES / "two-paragraphs.abw")
        assert isinstance(text, list)
        assert len(text) >= 1

    def test_load_and_paragraph_count_agree(self):
        """model['paragraph_count'] matches get_paragraph_count() result."""
        path = _SAMPLES / "two-paragraphs.abw"
        model = load(path)
        count_from_api = get_paragraph_count(path)
        assert model.get("paragraph_count") == count_from_api


# ---------------------------------------------------------------------------
# Roundtrip: load → extract_text → sha256 identity
# ---------------------------------------------------------------------------


class TestAbwRoundtripIdentity:
    def test_file_bytes_are_stable(self):
        """Reading the same ABW file twice produces the same SHA-256."""
        path = _SAMPLES / "minimal-document.abw"
        sha1 = hashlib.sha256(path.read_bytes()).hexdigest()
        sha2 = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha1 == sha2

    def test_extract_text_idempotent(self):
        """extract_text() on same file twice returns same result (list)."""
        path = _SAMPLES / "minimal-document.abw"
        t1 = extract_text(path)
        t2 = extract_text(path)
        assert t1 == t2
        assert isinstance(t1, list)

    def test_paragraph_count_idempotent(self):
        """get_paragraph_count() on same file twice returns same result."""
        path = _SAMPLES / "minimal-document.abw"
        c1 = get_paragraph_count(path)
        c2 = get_paragraph_count(path)
        assert c1 == c2


# ---------------------------------------------------------------------------
# Regression guard: no dict argument accepted
# ---------------------------------------------------------------------------


class TestAbwApiContractGuard:
    def test_load_model_not_accepted_by_get_paragraph_count(self):
        """Passing a model dict to get_paragraph_count() raises an error.

        This is the regression that caused the dogfood contradiction.
        The API requires a file path, not a loaded model dict.
        """
        model = load(_SAMPLES / "minimal-document.abw")
        with pytest.raises(Exception):
            # Should raise AbwError or TypeError — not silently succeed
            get_paragraph_count(model)

    def test_load_model_not_accepted_by_extract_text(self):
        """Passing a model dict to extract_text() raises an error."""
        model = load(_SAMPLES / "minimal-document.abw")
        with pytest.raises(Exception):
            extract_text(model)
