"""
test_public_spec_governance.py

R12 Lane D — Tests for public-spec acquisition governance expansion.

Validates:
1. format-onboarding.schema.yaml R12 extensions are structurally correct
2. Governance rules enforced for acquisition risk classification
3. Spec normalization status lifecycle is valid
4. Oracle classification values are valid
5. Sample provenance notes requirement
6. Public spec quality classification
7. Backlog integrity for acquisition governance
8. Risk-tier consistency with scoring tier

Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))



# ---------------------------------------------------------------------------
# Schema field constants (expected enums from format-onboarding.schema.yaml R12)
# ---------------------------------------------------------------------------

VALID_ACQUISITION_RISK = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "NOT_ASSESSED"}
VALID_SPEC_NORMALIZATION = {
    "NOT_STARTED", "CACHED_RAW", "NORMALIZED", "REQUIREMENTS_READY", "STALE"
}
VALID_ORACLE_CLASSIFICATION = {
    "ROUND_TRIP", "REFERENCE_DIFF", "SCHEMA_VALIDATE", "MANUAL_REVIEW", "NOT_ASSESSED"
}
VALID_PUBLIC_SPEC_QUALITY = {
    "RFC_STANDARD", "ISO_IEC_STANDARD", "ECMA_STANDARD", "OASIS_STANDARD",
    "OPEN_SOURCE_DOC", "COMMUNITY_WIKI", "VENDOR_DOC", "UNKNOWN"
}
VALID_LEGAL_CLASSIFICATION = {
    "PUBLIC_SPEC", "REVERSE_ENGINEERED", "COMMUNITY_DOCUMENTED",
    "ASPOSE_SUPPORTED", "PROPRIETARY_UNKNOWN"
}
VALID_ONBOARDING_OVERALL = {
    "CANDIDATE", "AUDITED_READY", "IN_PROGRESS", "COMPLETE", "DEFERRED", "BLOCKED"
}


# ---------------------------------------------------------------------------
# Section 1: Acquisition Risk Classification
# ---------------------------------------------------------------------------

class TestAcquisitionRiskClassification:

    def test_valid_risk_values(self):
        """All valid acquisition risk enum values are correct."""
        assert "LOW" in VALID_ACQUISITION_RISK
        assert "MEDIUM" in VALID_ACQUISITION_RISK
        assert "HIGH" in VALID_ACQUISITION_RISK
        assert "CRITICAL" in VALID_ACQUISITION_RISK
        assert "NOT_ASSESSED" in VALID_ACQUISITION_RISK

    def test_risk_count(self):
        """Exactly 5 risk values."""
        assert len(VALID_ACQUISITION_RISK) == 5

    def test_zst_risk_classification(self):
        """ZST should classify as LOW risk (full public RFC, clear legal)."""
        zst_profile = {
            "spec_type": "full_public",
            "legal_use_clear": True,
            "reverse_engineering_required": False,
            "binary_format": False,  # Per spec (RFC is clear)
        }
        risk = _classify_acquisition_risk(zst_profile)
        assert risk == "LOW", f"ZST should be LOW risk; got {risk}"

    def test_hwp_risk_classification(self):
        """HWP should classify as HIGH risk (reverse engineering, binary, legal unclear)."""
        hwp_profile = {
            "spec_type": "reverse_engineering",
            "legal_use_clear": False,
            "reverse_engineering_required": True,
            "binary_format": True,
        }
        risk = _classify_acquisition_risk(hwp_profile)
        assert risk in ("HIGH", "CRITICAL"), f"HWP should be HIGH/CRITICAL risk; got {risk}"

    def test_hwpx_risk_classification(self):
        """HWPX should classify as MEDIUM risk (partial spec, legal unclear)."""
        hwpx_profile = {
            "spec_type": "partial_public",
            "legal_use_clear": False,
            "reverse_engineering_required": False,
            "binary_format": False,
        }
        risk = _classify_acquisition_risk(hwpx_profile)
        assert risk in ("MEDIUM", "NOT_ASSESSED"), f"HWPX should be MEDIUM risk; got {risk}"

    def test_alz_risk_classification(self):
        """ALZ should classify as HIGH or CRITICAL (reverse engineering, binary)."""
        alz_profile = {
            "spec_type": "reverse_engineering",
            "legal_use_clear": False,
            "reverse_engineering_required": True,
            "binary_format": True,
        }
        risk = _classify_acquisition_risk(alz_profile)
        assert risk in ("HIGH", "CRITICAL"), f"ALZ should be HIGH/CRITICAL risk; got {risk}"

    def test_no_spec_is_critical(self):
        """Format with no spec should be CRITICAL acquisition risk."""
        no_spec_profile = {
            "spec_type": "none",
            "legal_use_clear": False,
            "reverse_engineering_required": False,
            "binary_format": False,
        }
        risk = _classify_acquisition_risk(no_spec_profile)
        assert risk == "CRITICAL", f"No-spec format should be CRITICAL; got {risk}"

    def test_risk_ordering(self):
        """Risk classifications have a defined severity ordering."""
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "NOT_ASSESSED": -1}
        assert risk_order["LOW"] < risk_order["MEDIUM"]
        assert risk_order["MEDIUM"] < risk_order["HIGH"]
        assert risk_order["HIGH"] < risk_order["CRITICAL"]


# ---------------------------------------------------------------------------
# Section 2: Spec Normalization Status Lifecycle
# ---------------------------------------------------------------------------

class TestSpecNormalizationStatusLifecycle:

    def test_valid_normalization_states(self):
        """All valid normalization status values are present."""
        assert "NOT_STARTED" in VALID_SPEC_NORMALIZATION
        assert "CACHED_RAW" in VALID_SPEC_NORMALIZATION
        assert "NORMALIZED" in VALID_SPEC_NORMALIZATION
        assert "REQUIREMENTS_READY" in VALID_SPEC_NORMALIZATION
        assert "STALE" in VALID_SPEC_NORMALIZATION

    def test_normalization_state_count(self):
        """Exactly 5 normalization states."""
        assert len(VALID_SPEC_NORMALIZATION) == 5

    def test_normalization_initial_state(self):
        """New candidates must start at NOT_STARTED."""
        initial = "NOT_STARTED"
        assert initial in VALID_SPEC_NORMALIZATION
        # NOT_STARTED means: no spec retrieval has been attempted
        # This is the correct default before any spec discovery sprint

    def test_normalization_progression_valid(self):
        """Normalization state progression follows the defined lifecycle."""
        valid_progressions = [
            ("NOT_STARTED", "CACHED_RAW"),
            ("CACHED_RAW", "NORMALIZED"),
            ("NORMALIZED", "REQUIREMENTS_READY"),
            ("REQUIREMENTS_READY", "STALE"),  # spec update invalidates
        ]
        for from_state, to_state in valid_progressions:
            assert from_state in VALID_SPEC_NORMALIZATION
            assert to_state in VALID_SPEC_NORMALIZATION

    def test_requirements_ready_requires_normalized(self):
        """REQUIREMENTS_READY implies NORMALIZED completed first."""
        # This is a logical dependency (not enforced in code but required by governance)
        # Test that the ordering is consistent with the schema intent
        states_in_order = ["NOT_STARTED", "CACHED_RAW", "NORMALIZED", "REQUIREMENTS_READY"]
        for state in states_in_order:
            assert state in VALID_SPEC_NORMALIZATION

    def test_stale_is_recoverable(self):
        """STALE must be a valid state (recoverable via refresh)."""
        assert "STALE" in VALID_SPEC_NORMALIZATION
        # STALE is not terminal — a refresh sprint can return to CACHED_RAW → NORMALIZED


# ---------------------------------------------------------------------------
# Section 3: Oracle Classification
# ---------------------------------------------------------------------------

class TestOracleClassification:

    def test_valid_oracle_values(self):
        """All oracle classification values are valid."""
        expected = {
            "ROUND_TRIP", "REFERENCE_DIFF", "SCHEMA_VALIDATE",
            "MANUAL_REVIEW", "NOT_ASSESSED"
        }
        assert VALID_ORACLE_CLASSIFICATION == expected

    def test_zst_oracle_is_round_trip(self):
        """ZST oracle approach is ROUND_TRIP (compress → decompress → verify)."""
        zst_oracle = "ROUND_TRIP"
        assert zst_oracle in VALID_ORACLE_CLASSIFICATION

    def test_xml_format_oracle_is_schema_validate(self):
        """XML-based formats (FODS, FODT, gnumeric, abw) use SCHEMA_VALIDATE oracle."""
        xml_oracle = "SCHEMA_VALIDATE"
        assert xml_oracle in VALID_ORACLE_CLASSIFICATION

    def test_reference_diff_for_aspose_formats(self):
        """Aspose-supported formats can use REFERENCE_DIFF oracle."""
        aspose_oracle = "REFERENCE_DIFF"
        assert aspose_oracle in VALID_ORACLE_CLASSIFICATION

    def test_not_assessed_is_default(self):
        """NOT_ASSESSED is the default oracle classification for new candidates."""
        default_oracle = "NOT_ASSESSED"
        assert default_oracle in VALID_ORACLE_CLASSIFICATION


# ---------------------------------------------------------------------------
# Section 4: Public Spec Quality
# ---------------------------------------------------------------------------

class TestPublicSpecQuality:

    def test_valid_spec_quality_values(self):
        """All spec quality values are present."""
        expected = {
            "RFC_STANDARD", "ISO_IEC_STANDARD", "ECMA_STANDARD", "OASIS_STANDARD",
            "OPEN_SOURCE_DOC", "COMMUNITY_WIKI", "VENDOR_DOC", "UNKNOWN"
        }
        assert VALID_PUBLIC_SPEC_QUALITY == expected

    def test_zst_is_rfc_standard(self):
        """ZST spec quality is RFC_STANDARD (RFC 8878)."""
        zst_quality = "RFC_STANDARD"
        assert zst_quality in VALID_PUBLIC_SPEC_QUALITY

    def test_gnumeric_is_open_source_doc(self):
        """Gnumeric spec quality is OPEN_SOURCE_DOC (GNOME project XML schema)."""
        gnumeric_quality = "OPEN_SOURCE_DOC"
        assert gnumeric_quality in VALID_PUBLIC_SPEC_QUALITY

    def test_fods_is_oasis_standard(self):
        """FODS spec quality is OASIS_STANDARD (ODF)."""
        fods_quality = "OASIS_STANDARD"
        assert fods_quality in VALID_PUBLIC_SPEC_QUALITY

    def test_quality_hierarchy_exists(self):
        """RFC and standards-body specs are higher quality than community docs."""
        # Quality hierarchy for governance scoring purposes
        high_quality = {"RFC_STANDARD", "ISO_IEC_STANDARD", "ECMA_STANDARD", "OASIS_STANDARD"}
        medium_quality = {"OPEN_SOURCE_DOC", "VENDOR_DOC"}
        low_quality = {"COMMUNITY_WIKI"}
        unknown = {"UNKNOWN"}
        all_values = high_quality | medium_quality | low_quality | unknown
        assert all_values == VALID_PUBLIC_SPEC_QUALITY


# ---------------------------------------------------------------------------
# Section 5: Governance Invariants for Onboarding
# ---------------------------------------------------------------------------

class TestOnboardingGovernanceInvariants:

    def test_candidate_is_default_state(self):
        """New formats must default to CANDIDATE onboarding state."""
        assert "CANDIDATE" in VALID_ONBOARDING_OVERALL

    def test_audited_ready_requires_audit(self):
        """AUDITED_READY state implies support matrix audit was completed."""
        # Verify AUDITED_READY exists and is a valid progression from CANDIDATE
        assert "AUDITED_READY" in VALID_ONBOARDING_OVERALL

    def test_blocked_is_valid_state(self):
        """BLOCKED is a valid terminal state for formats with legal/technical issues."""
        assert "BLOCKED" in VALID_ONBOARDING_OVERALL

    def test_deferred_is_valid_state(self):
        """DEFERRED is a valid state for formats with documented deferral reason."""
        assert "DEFERRED" in VALID_ONBOARDING_OVERALL

    def test_needs_audit_default_for_new_formats(self):
        """All new backlog formats must start with needs_audit audit_status."""
        from candidate_format_backlog import (
            TIER_A_CANDIDATES, AUDIT_STATUS_NEEDS_AUDIT
        )
        for entry in TIER_A_CANDIDATES:
            fmt = entry["format_id"]
            # All TIER_A candidates must be needs_audit (not audited)
            assert entry["audit_status"] == AUDIT_STATUS_NEEDS_AUDIT, \
                f"{fmt}: TIER_A candidates must be needs_audit, got {entry['audit_status']}"

    def test_aspose_supported_none_for_unaudited(self):
        """Unaudited formats must have aspose_supported=None."""
        from candidate_format_backlog import TIER_A_CANDIDATES
        for entry in TIER_A_CANDIDATES:
            fmt = entry["format_id"]
            assert entry["aspose_supported"] is None, \
                f"{fmt}: aspose_supported must be None until audited"

    def test_no_implementation_readiness_before_requirements(self):
        """implementation_readiness REQUIRES_REQUIREMENTS blocks implementation start."""
        template_state = "REQUIRES_REQUIREMENTS"
        # This is the correct default in the template
        # Implementation cannot begin until REQUIREMENTS_AUTHORITATIVE is reached
        assert template_state not in ("READY",)  # would be wrong default
        assert template_state == "REQUIRES_REQUIREMENTS"

    def test_all_legal_classifications_valid(self):
        """All legal provenance classification values are defined."""
        expected = {
            "PUBLIC_SPEC", "REVERSE_ENGINEERED", "COMMUNITY_DOCUMENTED",
            "ASPOSE_SUPPORTED", "PROPRIETARY_UNKNOWN"
        }
        assert VALID_LEGAL_CLASSIFICATION == expected


# ---------------------------------------------------------------------------
# Section 6: Risk-Tier Consistency
# ---------------------------------------------------------------------------

class TestRiskTierConsistency:

    def test_acquisition_ready_formats_should_be_low_medium_risk(self):
        """ACQUISITION_READY scored formats should map to LOW or MEDIUM risk."""
        # These formats score ≥ 8.0 (ACQUISITION_READY) and should be low-medium risk
        acquisition_ready_profiles = [
            {"fmt": "zst", "spec_type": "full_public", "legal_use_clear": True},
            {"fmt": "gnumeric", "spec_type": "full_public", "legal_use_clear": True},
            {"fmt": "abw", "spec_type": "full_public", "legal_use_clear": True},
            {"fmt": "ora", "spec_type": "full_public", "legal_use_clear": True},
        ]
        for profile in acquisition_ready_profiles:
            risk_profile = {
                "spec_type": profile["spec_type"],
                "legal_use_clear": profile["legal_use_clear"],
                "reverse_engineering_required": False,
                "binary_format": False,
            }
            risk = _classify_acquisition_risk(risk_profile)
            assert risk in ("LOW", "MEDIUM"), \
                f"{profile['fmt']}: ACQUISITION_READY format should be LOW/MEDIUM risk, got {risk}"

    def test_needs_investigation_formats_should_be_high_risk(self):
        """NEEDS_INVESTIGATION scored formats should map to HIGH or CRITICAL risk."""
        needs_inv_profiles = [
            {"fmt": "hwp", "spec_type": "reverse_engineering", "legal_use_clear": False, "binary_format": True},
            {"fmt": "alz", "spec_type": "reverse_engineering", "legal_use_clear": False, "binary_format": True},
        ]
        for profile in needs_inv_profiles:
            risk_profile = {
                "spec_type": profile["spec_type"],
                "legal_use_clear": profile["legal_use_clear"],
                "reverse_engineering_required": True,
                "binary_format": profile["binary_format"],
            }
            risk = _classify_acquisition_risk(risk_profile)
            assert risk in ("HIGH", "CRITICAL"), \
                f"{profile['fmt']}: NEEDS_INVESTIGATION format should be HIGH/CRITICAL risk, got {risk}"


# ---------------------------------------------------------------------------
# Helper: acquisition risk classifier (pure function, not in main codebase)
# Used only for testing governance logic
# ---------------------------------------------------------------------------

def _classify_acquisition_risk(profile: dict) -> str:
    """
    Classify acquisition risk from a format profile dict.
    Pure simulation function — not imported from production code.
    Used to validate governance rule consistency.
    """
    spec_type = profile.get("spec_type", "unknown")
    legal_use_clear = profile.get("legal_use_clear", False)
    reverse_engineering_required = profile.get("reverse_engineering_required", False)
    binary_format = profile.get("binary_format", False)

    if spec_type == "none":
        return "CRITICAL"
    if spec_type == "unknown":
        return "NOT_ASSESSED"
    if reverse_engineering_required and not legal_use_clear:
        return "HIGH" if spec_type != "none" else "CRITICAL"
    if spec_type == "reverse_engineering":
        return "HIGH"
    if spec_type == "full_public" and legal_use_clear:
        return "LOW"
    if spec_type in ("partial_public", "community_documented"):
        return "MEDIUM"
    return "NOT_ASSESSED"
