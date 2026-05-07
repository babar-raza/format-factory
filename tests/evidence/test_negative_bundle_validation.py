#!/usr/bin/env python3
"""
Negative tests for validate_evidence_bundle.py.

Tests that the validator correctly FAILS for:
1. Thin bundles (fewer metadata files than required minimum)
2. Bundles containing PENDING marker text in metadata files (--check-no-pending)

Run from repo root:
    python tests/evidence/test_negative_bundle_validation.py

Exits 0 if all tests PASS, 1 if any test FAILS.
"""

import sys
import tempfile
import zipfile
from pathlib import Path

# Add tools/evidence to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "evidence"))

from validate_evidence_bundle import validate_bundle  # noqa: E402


def build_minimal_contract(tmp_dir: Path, min_meta: int = 5) -> Path:
    """Write a minimal contract YAML for tests."""
    contract = tmp_dir / "test-contract.yaml"
    contract.write_text(
        f"""\
contract_id: test-negative
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: {min_meta}
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
        encoding="utf-8",
    )
    return contract


def build_bundle_with_meta(tmp_dir: Path, meta_files: dict) -> Path:
    """Build a bundle zip with the given metadata files. No repo files."""
    bundle_path = tmp_dir / "test-bundle.zip"
    with zipfile.ZipFile(bundle_path, "w") as zf:
        # Add a minimal repo file so the repo/ folder exists
        zf.writestr("repo/placeholder.txt", "placeholder")
        # Add metadata files
        for name, content in meta_files.items():
            zf.writestr(f"bundle-metadata/{name}", content)
    return bundle_path


def test_thin_bundle_fails():
    """Validator must FAIL when metadata count is below min_metadata_count."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract requires at least 5 metadata files
        contract = build_minimal_contract(tmp_dir, min_meta=5)
        # Bundle has only 2 metadata files
        meta = {
            "file1.md": "content 1",
            "file2.md": "content 2",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if result:
            print("FAIL: test_thin_bundle_fails — validator returned PASS but should have FAILed")
            return False
        print("PASS: test_thin_bundle_fails — validator correctly returned FAIL for thin bundle")
        return True


def test_pending_report_fails_with_flag():
    """Validator must FAIL when --check-no-pending is set and metadata contains PENDING marker."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract with low min_metadata so we don't fail on that
        contract = build_minimal_contract(tmp_dir, min_meta=1)
        # Bundle has a metadata file with PENDING marker
        meta = {
            "verdict.md": "**Validation status:** PENDING (bundle not yet built)\n",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if result:
            print("FAIL: test_pending_report_fails_with_flag — validator returned PASS but should have FAILed")
            return False
        print("PASS: test_pending_report_fails_with_flag — validator correctly returned FAIL for PENDING marker")
        return True


def test_pending_report_passes_without_flag():
    """Validator must PASS when --check-no-pending is NOT set, even if PENDING marker present."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=1)
        # Same PENDING marker, but no_pending=False
        meta = {
            "verdict.md": "**Validation status:** PENDING (bundle not yet built)\n",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if not result:
            print("FAIL: test_pending_report_passes_without_flag — validator returned FAIL but should have PASSed")
            return False
        print("PASS: test_pending_report_passes_without_flag — validator correctly PASSED when flag not set")
        return True


def test_clean_bundle_passes_no_pending():
    """Validator must PASS when --check-no-pending is set and no PENDING markers present."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=1)
        meta = {
            "verdict.md": "**Validation status:** BUNDLE_VALIDATION: PASS\n",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if not result:
            print("FAIL: test_clean_bundle_passes_no_pending — validator returned FAIL but should have PASSed")
            return False
        print("PASS: test_clean_bundle_passes_no_pending — validator correctly PASSED for clean bundle")
        return True


def main():
    print("=" * 60)
    print("Negative Tests: validate_evidence_bundle.py")
    print("=" * 60)
    print()

    tests = [
        test_thin_bundle_fails,
        test_pending_report_fails_with_flag,
        test_pending_report_passes_without_flag,
        test_clean_bundle_passes_no_pending,
    ]

    results = []
    for test_fn in tests:
        print(f"--- {test_fn.__name__} ---")
        results.append(test_fn())
        print()

    passed = sum(1 for r in results if r)
    total = len(results)
    print("=" * 60)
    if passed == total:
        print(f"ALL TESTS PASS: {passed}/{total}")
        sys.exit(0)
    else:
        print(f"TESTS FAILED: {passed}/{total} passed")
        sys.exit(1)


if __name__ == "__main__":
    main()
