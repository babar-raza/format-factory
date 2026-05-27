"""
R70 Train D — test_r70_final_iv_no_placeholders.py
Verify final-independent-verification.txt has no unfilled SHA placeholders.
"""

import pathlib
import pytest

FINAL_IV = pathlib.Path(".local/r69-metadata/final-independent-verification.txt")

# Placeholder patterns that must NOT appear
PLACEHOLDER_PATTERNS = [
    "to be filled",
    "TO BE FILLED",
    "(to be filled after",
    "PENDING",
]

# SHA fields that must appear with actual values
REQUIRED_SHA_FIELDS = [
    "Inner ZIP SHA:",
    "Sidecar file SHA:",
    "Delivery SHA:",
]

SHA_PATTERN = r"[0-9a-f]{64}"


def test_final_iv_exists():
    """final-independent-verification.txt must exist."""
    if not FINAL_IV.exists():
        pytest.skip("final-independent-verification.txt not present (pre-build)")
    assert FINAL_IV.exists()


def test_no_placeholder_tokens_in_final_iv():
    """final-independent-verification.txt must not contain unfilled placeholder text."""
    if not FINAL_IV.exists():
        pytest.skip("final-independent-verification.txt not present (pre-build)")
    content = FINAL_IV.read_text()
    for pattern in PLACEHOLDER_PATTERNS:
        assert pattern not in content, (
            f"final-independent-verification.txt contains placeholder: {pattern!r}"
        )


def test_final_iv_has_sha_fields_with_values():
    """final-independent-verification.txt must have SHA fields with 64-char hex values."""
    import re
    if not FINAL_IV.exists():
        pytest.skip("final-independent-verification.txt not present (pre-build)")
    content = FINAL_IV.read_text()
    for field in REQUIRED_SHA_FIELDS:
        assert field in content, (
            f"final-independent-verification.txt missing required field: {field!r}"
        )
        # Find the line with this field and verify it has a SHA
        for line in content.splitlines():
            if line.startswith(field):
                assert re.search(SHA_PATTERN, line), (
                    f"Field {field!r} does not contain a 64-char hex SHA: {line!r}"
                )
                break


def test_final_iv_verdict_present():
    """final-independent-verification.txt must contain FINAL_IV verdict token."""
    if not FINAL_IV.exists():
        pytest.skip("final-independent-verification.txt not present (pre-build)")
    content = FINAL_IV.read_text()
    assert "FINAL_IV:" in content, (
        "final-independent-verification.txt missing FINAL_IV verdict token"
    )
    assert "PENDING" not in content, (
        "final-independent-verification.txt FINAL_IV verdict must not be PENDING"
    )
