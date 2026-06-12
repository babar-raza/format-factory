"""
test_r74_rejects_to_be_filled_placeholders.py

R74 Train B: Validator must reject bundles where final-independent-verification.txt
(or .md) contains '[to be filled after X build]' placeholders.

Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import zipfile
import io
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_closeout_hygiene_tokens


def _make_zip_with_file(path_in_zip: str, content: str) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr(path_in_zip, content)
    buf.seek(0)
    return buf


class TestRejectsToBeFilledPlaceholders:
    """R74: [to be filled after X build] must be caught in final-iv .txt files."""

    def test_to_be_filled_after_pass1_detected_txt(self):
        buf = _make_zip_with_file(
            "bundle-metadata/final-independent-verification.txt",
            "R74 Final Independent Verification\n"
            "BUNDLE_VALIDATION_PASS_1_SHA: [to be filled after Pass 1 build]\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: [to be filled after Pass 2 build]\n"
            "SIDECAR_SHA: [to be filled after sidecar generation]\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, "[to be filled after] must be caught in .txt file"
        assert any("final-independent-verification.txt" in p for p, _ in hits)

    def test_to_be_filled_after_pass2_detected_txt(self):
        buf = _make_zip_with_file(
            "repo/reports/r74/final-independent-verification.txt",
            "BUNDLE_VALIDATION_PASS_2_SHA: [to be filled after Pass 2 build]\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, "[to be filled after Pass 2 build] must be caught"

    def test_to_be_filled_after_detected_md(self):
        buf = _make_zip_with_file(
            "bundle-metadata/final-independent-verification.md",
            "SIDECAR_SHA: [to be filled after sidecar generation]\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, "[to be filled after] in .md must also be caught"

    def test_clean_final_iv_passes(self):
        buf = _make_zip_with_file(
            "bundle-metadata/final-independent-verification.txt",
            "R74 Final Independent Verification\n"
            "BUNDLE_VALIDATION_PASS_1_SHA: fe21c886272675dc3711ba2ff8a819e8c81e18dd393af131f3ec6a911bc8250f\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: ffa23117339ec309161305cf91de8af3bece848db301f919c6b09051a45111a5\n"
            "SIDECAR_SHA: 12ecae49ff66109f32605d7883e331b01b93712f90613aa4365728533b688e5d\n"
            "IV_VERDICT: R74_CLEAN\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) == 0, f"Clean final IV must pass but got: {hits}"

    def test_r73_stale_final_iv_rejected(self):
        """Prove the exact R73 stale final-independent-verification.txt is now rejected."""
        r73_stale = (
            "BUNDLE_VALIDATION_PASS_1_SHA: [to be filled after Pass 1 build]\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: [to be filled after Pass 2 build]\n"
            "SIDECAR_SHA: [to be filled after sidecar generation]\n"
        )
        buf = _make_zip_with_file(
            "bundle-metadata/final-independent-verification.txt", r73_stale
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, "R73-style stale final IV must now be rejected"

    def test_external_sidecar_proof_pending_detected(self):
        buf = _make_zip_with_file(
            "bundle-metadata/external-sidecar-proof-summary.txt",
            "EXTERNAL_SIDECAR_PROOF_SUMMARY: PENDING_BUNDLE_BUILD\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, "PENDING_BUNDLE_BUILD in sidecar summary must be caught by closeout hygiene"
