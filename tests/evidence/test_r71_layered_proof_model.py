"""
R71 Train B — test_r71_layered_proof_model.py
Verify the layered proof authority model is enforced by the validator.

Proof authority layers:
  1. Inner evidence ZIP: source tree, reports, tests, artifacts, inner bundle validation
  2. External sidecar: SHA-256 / size / entries of inner evidence ZIP
  3. Delivery manifest: sidecar file SHA, sidecar-claimed inner ZIP SHA, outer package facts
  4. Outer delivery package: may be recorded externally / in final response only

Inner final-verdict rules:
  - MUST NOT contain DELIVERY_PACKAGE_SHA: PENDING
  - MUST NOT contain DELIVERY_PACKAGE_SHA: <64-char hex> (concrete outer SHA)
  - MAY contain DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative
  - MAY omit DELIVERY_PACKAGE_SHA entirely
"""

import io
import re
import sys
import zipfile
import pathlib
import pytest

# Load the validator module
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from tools.evidence.validate_evidence_bundle import check_inner_verdict_delivery_sha_authority


def _make_bundle_with_verdict(verdict_content: str) -> zipfile.ZipFile:
    """Create an in-memory ZIP file with a minimal final-verdict.md."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/reports/r71/final-verdict.md", verdict_content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


VERDICT_WITH_PENDING = """
# R71 Final Verdict
BUNDLE_VALIDATION_PASS_2_SHA: sidecar_authoritative
SIDECAR_SHA: sidecar_authoritative
DELIVERY_PACKAGE_SHA: PENDING
VERDICT: R71_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""

VERDICT_WITH_CONCRETE_SHA = """
# R71 Final Verdict
BUNDLE_VALIDATION_PASS_2_SHA: sidecar_authoritative
SIDECAR_SHA: sidecar_authoritative
DELIVERY_PACKAGE_SHA: 0e6016b876863fe40b1ac9f69f11a2813e609b53a0f0fd285fab95ea51a7ec97
VERDICT: R71_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""

VERDICT_WITH_SEMANTIC_LABEL = """
# R71 Final Verdict
BUNDLE_VALIDATION_PASS_2_SHA: sidecar_authoritative
SIDECAR_SHA: sidecar_authoritative
DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative
VERDICT: R71_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""

VERDICT_WITHOUT_DELIVERY_SHA = """
# R71 Final Verdict
BUNDLE_VALIDATION_PASS_2_SHA: sidecar_authoritative
SIDECAR_SHA: sidecar_authoritative
VERDICT: R71_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""

# R70's actual inner-verdict (the defect we're fixing)
VERDICT_R70_DEFECTIVE = """
BUNDLE_VALIDATION_PASS_2_SHA: af7c9b76abe7d80f66e55c4b457cb433569612aa48c3f114775da4a953996372
SIDECAR_SHA: af7c9b76abe7d80f66e55c4b457cb433569612aa48c3f114775da4a953996372
DELIVERY_PACKAGE_SHA: PENDING
"""


def test_pending_delivery_sha_is_rejected():
    """DELIVERY_PACKAGE_SHA: PENDING in inner verdict must fail."""
    zf = _make_bundle_with_verdict(VERDICT_WITH_PENDING)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert len(errors) > 0, "Expected error for DELIVERY_PACKAGE_SHA: PENDING"
    assert any("PENDING" in e for e in errors), "Error must mention PENDING"


def test_concrete_outer_sha_is_rejected():
    """A concrete 64-char hex delivery package SHA inside inner verdict must fail."""
    zf = _make_bundle_with_verdict(VERDICT_WITH_CONCRETE_SHA)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert len(errors) > 0, "Expected error for concrete outer delivery SHA"
    assert any("concrete" in e.lower() or "0e6016b8" in e for e in errors), \
        "Error must mention the concrete SHA"


def test_semantic_label_passes():
    """DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative must pass."""
    zf = _make_bundle_with_verdict(VERDICT_WITH_SEMANTIC_LABEL)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert errors == [], f"Expected no errors for semantic label but got: {errors}"


def test_omitted_delivery_sha_passes():
    """Omitting DELIVERY_PACKAGE_SHA entirely must pass."""
    zf = _make_bundle_with_verdict(VERDICT_WITHOUT_DELIVERY_SHA)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert errors == [], f"Expected no errors for omitted field but got: {errors}"


def test_r70_defective_verdict_is_rejected():
    """R70's actual inner-verdict (IV-R71-002) must be detected as defective."""
    zf = _make_bundle_with_verdict(VERDICT_R70_DEFECTIVE)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert len(errors) > 0, "R70 defective verdict should fail layered proof check"


def test_markdown_list_references_are_not_flagged():
    """List items like '- DELIVERY_PACKAGE_SHA: PENDING' must not be flagged."""
    verdict = """
# R71 Final Verdict
Prior sprint had these defects:
- DELIVERY_PACKAGE_SHA: PENDING
- DELIVERY_PACKAGE_SHA: 0e6016b876863fe40b1ac9f69f11a2813e609b53a0f0fd285fab95ea51a7ec97

DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative
VERDICT: R71_LOCAL_RC_SEALED_PUBLICATION_BLOCKED
"""
    zf = _make_bundle_with_verdict(verdict)
    errors = check_inner_verdict_delivery_sha_authority(zf)
    assert errors == [], f"List item references must not be flagged but got: {errors}"
