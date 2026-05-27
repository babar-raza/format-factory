"""
R70 Train E — test_r70_validator_rejects_final_iv_placeholders.py
Verify that final-independent-verification.txt with unfilled SHA placeholders
is detected as a defect.
"""

import re
import pytest

# Simulated content WITH placeholders (IV-R70-002 defect)
DEFECTIVE_IV = """
Final Independent Verification — R69
=====================================
Inner ZIP SHA: (to be filled after Pass 2 build)
Sidecar SHA: (to be filled after Pass 2 build)
Delivery SHA: (to be filled after delivery package build)
FINAL_IV: R69_COMPLETE
"""

# Simulated content with actual SHAs
CORRECT_IV = """
Final Independent Verification — R69
=====================================
Inner ZIP SHA: 3e02c171fe2c188d4331a885eb1abbfa4261e3475d87766c998bd913157fda22
Sidecar file SHA: 6a08df047d0b841a62b3d995fa6aae40167873629c79dfa471f4e5ddb78a184e
Delivery SHA: 51c66782de73616ada082795ccbcb41ee279211ab0d77229a294f78e0feb8da0
FINAL_IV: R69_COMPLETE_ALL_R68_DEFECTS_REPAIRED_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""

PLACEHOLDER_PATTERNS = ["to be filled", "TO BE FILLED", "(to be filled after"]


def _check_no_placeholders(content):
    errors = []
    for p in PLACEHOLDER_PATTERNS:
        if p in content:
            errors.append(f"Placeholder found: {p!r}")
    return errors


def test_correct_iv_passes_placeholder_check():
    """final-independent-verification.txt with actual SHAs should pass."""
    errors = _check_no_placeholders(CORRECT_IV)
    assert errors == [], f"Expected no errors but got: {errors}"


def test_defective_iv_fails_placeholder_check():
    """final-independent-verification.txt with 'to be filled' should fail."""
    errors = _check_no_placeholders(DEFECTIVE_IV)
    assert len(errors) > 0, "Expected placeholder errors but got none"


def test_correct_iv_has_64_char_sha_for_inner_zip():
    """Inner ZIP SHA field must contain a 64-char hex value."""
    m = re.search(r"Inner ZIP SHA:\s*([0-9a-f]{64})", CORRECT_IV)
    assert m is not None, "Inner ZIP SHA field missing or not 64-char hex"


def test_r69_actual_final_iv_has_no_placeholders():
    """After Train B repair, actual R69 final-independent-verification.txt must be clean."""
    import pathlib
    f = pathlib.Path(".local/r69-metadata/final-independent-verification.txt")
    if not f.exists():
        pytest.skip("final-independent-verification.txt not present (pre-build)")
    content = f.read_text()
    errors = _check_no_placeholders(content)
    assert errors == [], (
        f"R69 final-independent-verification.txt still has placeholders: {errors}"
    )
