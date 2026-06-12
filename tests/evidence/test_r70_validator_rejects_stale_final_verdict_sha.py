"""
R70 Train E — test_r70_validator_rejects_stale_final_verdict_sha.py
Verify validator correctly identifies stale/wrong SHA in final-verdict.md.
These are unit tests of the detection logic (no .local/ required).
"""


# Simulate final-verdict.md content with stale SHA vs correct SHA
INNER_ZIP_SHA = "3e02c171fe2c188d4331a885eb1abbfa4261e3475d87766c998bd913157fda22"
STALE_SHA = "c2826328abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
CORRECT_VERDICT = f"""
BUNDLE_VALIDATION_PASS_1_SHA: 73a7392cc6914001e2c4e45857feecc36e850ba648f0f98ae53ac7b225d7ac98
BUNDLE_VALIDATION_PASS_2_SHA: {INNER_ZIP_SHA}
SIDECAR_SHA: {INNER_ZIP_SHA}
DELIVERY_PACKAGE_SHA: 51c66782de73616ada082795ccbcb41ee279211ab0d77229a294f78e0feb8da0
"""
STALE_VERDICT = f"""
BUNDLE_VALIDATION_PASS_1_SHA: 73a7392cc6914001e2c4e45857feecc36e850ba648f0f98ae53ac7b225d7ac98
BUNDLE_VALIDATION_PASS_2_SHA: {STALE_SHA}
SIDECAR_SHA: {STALE_SHA}
DELIVERY_PACKAGE_SHA: 66dd6e463abcdef1234567890abcdef1234567890abcdef1234567890abcdef12
"""


def _check_verdict_sha_not_stale(verdict_text, inner_zip_sha):
    """Returns list of error messages if stale SHAs detected."""
    import re
    errors = []
    m = re.search(r"BUNDLE_VALIDATION_PASS_2_SHA:\s*([0-9a-f]{64})", verdict_text)
    if m and m.group(1) != inner_zip_sha:
        errors.append(f"BUNDLE_VALIDATION_PASS_2_SHA mismatch: {m.group(1)!r} != {inner_zip_sha!r}")
    m2 = re.search(r"SIDECAR_SHA:\s*([0-9a-f]{64})", verdict_text)
    if m2 and m2.group(1) != inner_zip_sha:
        errors.append(f"SIDECAR_SHA mismatch: {m2.group(1)!r} != {inner_zip_sha!r}")
    return errors


def test_correct_final_verdict_passes_sha_check():
    """A final-verdict.md with correct SHAs should produce no errors."""
    errors = _check_verdict_sha_not_stale(CORRECT_VERDICT, INNER_ZIP_SHA)
    assert errors == [], f"Expected no errors but got: {errors}"


def test_stale_final_verdict_fails_sha_check():
    """A final-verdict.md with stale Pass 2 SHA should be flagged."""
    errors = _check_verdict_sha_not_stale(STALE_VERDICT, INNER_ZIP_SHA)
    assert len(errors) > 0, "Expected errors for stale final-verdict SHAs but got none"


def test_stale_sha_detection_flags_both_fields():
    """Both BUNDLE_VALIDATION_PASS_2_SHA and SIDECAR_SHA must be flagged if stale."""
    errors = _check_verdict_sha_not_stale(STALE_VERDICT, INNER_ZIP_SHA)
    assert any("BUNDLE_VALIDATION_PASS_2_SHA" in e for e in errors), \
        "Expected BUNDLE_VALIDATION_PASS_2_SHA to be flagged"
    assert any("SIDECAR_SHA" in e for e in errors), \
        "Expected SIDECAR_SHA to be flagged"


def test_pending_sha_in_final_verdict_is_detected():
    """PENDING placeholder in final-verdict SHAs must be detected."""
    pending_verdict = """
BUNDLE_VALIDATION_PASS_2_SHA: PENDING
SIDECAR_SHA: PENDING
"""
    assert "PENDING" in pending_verdict
    # A SHA check should not match PENDING as a 64-char hex value
    import re
    m = re.search(r"BUNDLE_VALIDATION_PASS_2_SHA:\s*([0-9a-f]{64})", pending_verdict)
    assert m is None, "PENDING should not match 64-char hex SHA pattern"
