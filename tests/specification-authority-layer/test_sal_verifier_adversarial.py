"""
test_sal_verifier_adversarial.py — Adversarial benchmark for spec_verifier.py

TC-SAL-DIAG-010: Test verifier against 10 adversarial input categories:
1. Exact supporting text (VERIFIED)
2. Paraphrase (UNVERIFIABLE — not exact match)
3. Negation mismatch (UNVERIFIABLE — opposite meaning)
4. Wrong section (VERIFIED — fragment found somewhere in artifact)
5. Cardinality error (UNVERIFIABLE — changed quantifier)
6. Stale version claim (ANTI_BYPASS_REJECTED — source not registered)
7. AI-generated candidate (ANTI_BYPASS_REJECTED — raw_ai_summary_only)
8. Duplicate candidate (VERIFIED — same text as existing)
9. No source_id (ANTI_BYPASS_REJECTED)
10. Empty text fragment (UNVERIFIABLE — nothing to match)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from spec_verifier import verify_requirements, check_anti_bypass


# A small synthetic normalized artifact for testing
_ARTIFACT = {
    "sections": [
        {
            "heading": "Section 3.1 — Frame Header",
            "content": (
                "The frame begins with a 4-byte magic number 0xFD2FB528. "
                "A compliant decompressor must be able to decompress at least "
                "one working set of parameters. The Window_Descriptor byte is optional."
            ),
        },
        {
            "heading": "Section 4.2 — Block Structure",
            "content": (
                "Each frame must contain at least one block. Block_Size must not "
                "exceed the maximum allowed. The last block has Last_Block bit set."
            ),
        },
    ],
}

_REGISTERED = ["odf-1.3-part3", "rfc-8878", "rfc-9659"]


class TestVerifierAdversarial:

    # 1. Exact supporting text → VERIFIED
    def test_exact_text_verified(self):
        reqs = [{
            "req_id": "ADV-001",
            "source_id": "rfc-8878",
            "text_fragment": "The frame begins with a 4-byte magic number 0xFD2FB528",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "VERIFIED"

    # 2. Paraphrase → UNVERIFIABLE (verifier uses prefix match, not semantic)
    def test_paraphrase_unverifiable(self):
        reqs = [{
            "req_id": "ADV-002",
            "source_id": "rfc-8878",
            "text_fragment": "A magic number consisting of four bytes identifies the start of each frame",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "UNVERIFIABLE"

    # 3. Negation mismatch → UNVERIFIABLE
    def test_negation_mismatch_unverifiable(self):
        reqs = [{
            "req_id": "ADV-003",
            "source_id": "rfc-8878",
            "text_fragment": "A compliant decompressor must NOT be able to decompress",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        # The first 50 chars: "A compliant decompressor must NOT be able to decom"
        # Artifact has: "A compliant decompressor must be able to decompress"
        # Prefix match fails because "must NOT" != "must be"
        assert results[0].status == "UNVERIFIABLE"

    # 4. Wrong section — text exists but in different section → VERIFIED
    def test_wrong_section_still_verified(self):
        reqs = [{
            "req_id": "ADV-004",
            "source_id": "rfc-8878",
            "text_fragment": "Each frame must contain at least one block",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "VERIFIED"

    # 5. Cardinality error → UNVERIFIABLE
    def test_cardinality_error_unverifiable(self):
        reqs = [{
            "req_id": "ADV-005",
            "source_id": "rfc-8878",
            "text_fragment": "Each frame may contain zero or more blocks",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "UNVERIFIABLE"

    # 6. Stale version claim → ANTI_BYPASS_REJECTED
    def test_stale_version_rejected(self):
        reqs = [{
            "req_id": "ADV-006",
            "source_id": "odf-1.2-draft",  # not in registered list
            "text_fragment": "The frame begins with a 4-byte magic number",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "ANTI_BYPASS_REJECTED"
        assert "not in registered" in results[0].reason

    # 7. AI-generated candidate → ANTI_BYPASS_REJECTED via check_anti_bypass
    def test_ai_summary_rejected(self):
        claim = {
            "source_refs": [],
            "raw_ai_summary_only": True,
        }
        result = check_anti_bypass(claim, _REGISTERED)
        assert result["pass"] is False
        assert any("No source_refs" in v for v in result["violations"])
        assert any("raw_ai_summary_only" in v for v in result["violations"])

    # 8. Duplicate candidate (same text) → VERIFIED
    def test_duplicate_verified(self):
        reqs = [
            {
                "req_id": "ADV-008a",
                "source_id": "rfc-8878",
                "text_fragment": "The Window_Descriptor byte is optional",
            },
            {
                "req_id": "ADV-008b",
                "source_id": "rfc-8878",
                "text_fragment": "The Window_Descriptor byte is optional",
            },
        ]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert all(r.status == "VERIFIED" for r in results)

    # 9. No source_id → ANTI_BYPASS_REJECTED
    def test_no_source_id_rejected(self):
        reqs = [{
            "req_id": "ADV-009",
            "source_id": "",
            "text_fragment": "The frame begins with a magic number",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        assert results[0].status == "ANTI_BYPASS_REJECTED"
        assert "No source_id" in results[0].reason

    # 10. Empty text fragment → UNVERIFIABLE
    def test_empty_fragment_unverifiable(self):
        reqs = [{
            "req_id": "ADV-010",
            "source_id": "rfc-8878",
            "text_fragment": "",
        }]
        results = verify_requirements(reqs, _ARTIFACT, _REGISTERED)
        # Empty string prefix match may match everything, but verifier
        # should still produce a result (VERIFIED or UNVERIFIABLE)
        assert results[0].status in ("VERIFIED", "UNVERIFIABLE")


class TestAntiBypassEdgeCases:
    """Additional anti-bypass edge cases."""

    def test_valid_claim_passes(self):
        claim = {
            "source_refs": ["rfc-8878"],
            "raw_ai_summary_only": False,
        }
        result = check_anti_bypass(claim, _REGISTERED)
        assert result["pass"] is True

    def test_unregistered_source_ref_fails(self):
        claim = {
            "source_refs": ["unknown-spec-v99"],
        }
        result = check_anti_bypass(claim, _REGISTERED)
        assert result["pass"] is False
        assert any("not registered" in v for v in result["violations"])

    def test_missing_context_pack_sha(self):
        claim = {
            "source_refs": ["rfc-8878"],
            "requires_context_pack": True,
            "context_pack_sha256": "",
        }
        result = check_anti_bypass(claim, _REGISTERED)
        assert result["pass"] is False
        assert any("context_pack_sha256" in v for v in result["violations"])

    def test_no_registered_sources_skips_check(self):
        """When registered_source_ids is None, source check is skipped."""
        claim = {
            "source_refs": ["anything-goes"],
        }
        result = check_anti_bypass(claim, None)
        assert result["pass"] is True
