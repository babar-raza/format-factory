"""
OverclaimDetector: 10 overclaim patterns with per-pattern remediation actions.

Remediation actions enum:
  narrow_claim, split_claim, add_unsupported_feature, require_dogfood,
  require_tests, require_implementation, downgrade_status, mark_empirical_only,
  request_policy_decision, reject_claim

10 overclaim patterns:
  1. Full claimed, partial proof → split: partial accepted + blocked remaining
  2. Save claimed, export proof → downgrade to export claim
  3. Roundtrip claimed, parse only → reject roundtrip; create parse claim
  4. All variants claimed, one variant tested → variant-specific claims
  5. Commercial ready, helpers only → block readiness; require dogfood/output proof
  6. Dogfood complete, no output artifact → keep dogfood_present; block coverage_validated
  7. Test coverage exists, not linked to claim → coverage remains unvalidated
  8. Spec-backed, only empirical → reclassify as empirical_only with caveat
  9. Accepted, requirement stale → demote to stale; revalidation required
 10. Supports format, blocking unsupported feature → policy decision or accepted_with_limitations
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .graph_store import GraphStore
from .models import GraphNode

REMEDIATION_ACTIONS = {
    "narrow_claim",
    "split_claim",
    "add_unsupported_feature",
    "require_dogfood",
    "require_tests",
    "require_implementation",
    "downgrade_status",
    "mark_empirical_only",
    "request_policy_decision",
    "reject_claim",
}


@dataclass
class OverclaimFinding:
    pattern_number: int
    claim_id: str
    description: str
    remediation_action: str
    remediation_detail: str
    severity: str = "ERROR"  # ERROR | WARNING

    def __post_init__(self):
        if self.remediation_action not in REMEDIATION_ACTIONS:
            raise ValueError(f"Unknown remediation_action: {self.remediation_action!r}. "
                             f"Valid: {sorted(REMEDIATION_ACTIONS)}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_number": self.pattern_number,
            "claim_id": self.claim_id,
            "description": self.description,
            "remediation_action": self.remediation_action,
            "remediation_detail": self.remediation_detail,
            "severity": self.severity,
        }


@dataclass
class OverclaimReport:
    findings: List[OverclaimFinding] = field(default_factory=list)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARNING")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self.findings],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "has_overclaims": self.has_findings,
        }


class OverclaimDetector:
    """
    Detects overclaim patterns across all CapabilityClaim nodes in a GraphStore.
    Produces an OverclaimReport with per-finding remediation actions.
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def detect_all(self) -> OverclaimReport:
        """Run all 10 overclaim pattern detectors."""
        report = OverclaimReport()
        claims = sorted(self.store.nodes_by_type("CapabilityClaim"), key=lambda c: c.node_id)
        for claim in claims:
            report.findings.extend(self._pattern_1_full_claimed_partial_proof(claim))
            report.findings.extend(self._pattern_2_save_with_export_proof(claim))
            report.findings.extend(self._pattern_3_roundtrip_parse_only(claim))
            report.findings.extend(self._pattern_4_all_variants_one_tested(claim))
            report.findings.extend(self._pattern_5_commercial_ready_helpers_only(claim))
            report.findings.extend(self._pattern_6_dogfood_no_output_artifact(claim))
            report.findings.extend(self._pattern_7_test_not_linked_to_claim(claim))
            report.findings.extend(self._pattern_8_spec_backed_empirical_only(claim))
            report.findings.extend(self._pattern_9_accepted_stale_requirement(claim))
            report.findings.extend(self._pattern_10_blocking_unsupported_feature(claim))
        return report

    # ── Pattern 1: Full support claimed, partial proof ───────────────────────

    def _pattern_1_full_claimed_partial_proof(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        operation = claim.metadata.get("operation", "")
        has_impl = bool(self.store.get_targets(claim.node_id, "implemented_by"))
        has_tests = bool(self.store.get_targets(claim.node_id, "tested_by"))
        has_dogfood = bool(self.store.get_targets(claim.node_id, "dogfooded_by"))

        # Full roundtrip claimed (read_write) but only partial artifacts
        if operation == "roundtrip" and not (has_impl and has_tests and has_dogfood):
            findings.append(OverclaimFinding(
                pattern_number=1,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' claims full roundtrip support "
                    f"(impl={has_impl}, tests={has_tests}, dogfood={has_dogfood}) "
                    f"but proof is incomplete."
                ),
                remediation_action="split_claim",
                remediation_detail=(
                    "Split into: one claim for the supported sub-operation "
                    "(e.g., LOAD_EXPORT) with existing proof, and one BLOCKED claim "
                    "for the remaining unsupported operations."
                ),
            ))
        return findings

    # ── Pattern 2: Save claimed, export proof ────────────────────────────────

    def _pattern_2_save_with_export_proof(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        operation = claim.metadata.get("operation", "")
        fidelity = claim.metadata.get("fidelity", "")
        direction = claim.metadata.get("direction", "")

        if operation == "save" and direction in ("export_only", "write_only", "read_only"):
            findings.append(OverclaimFinding(
                pattern_number=2,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' uses operation='save' but direction='{direction}' "
                    f"indicates only export/write proof exists. "
                    f"'save' implies same-format round-trip preservation."
                ),
                remediation_action="downgrade_status",
                remediation_detail=(
                    "Downgrade operation from 'save' to 'export'. "
                    "Create a separate BLOCKED 'save' claim if same-format roundtrip is needed."
                ),
            ))
        return findings

    # ── Pattern 3: Roundtrip claimed, parse only ─────────────────────────────

    def _pattern_3_roundtrip_parse_only(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        operation = claim.metadata.get("operation", "")
        has_write_evidence = any(
            a.metadata.get("operation") in ("save", "write", "export", "roundtrip")
            for a in self.store.get_targets(claim.node_id, "implemented_by")
        )
        if operation == "roundtrip" and not has_write_evidence:
            has_tests = bool(self.store.get_targets(claim.node_id, "tested_by"))
            if has_tests:
                findings.append(OverclaimFinding(
                    pattern_number=3,
                    claim_id=claim.node_id,
                    description=(
                        f"Claim '{claim.node_id}' claims roundtrip but has parse/load "
                        f"implementation only (no write evidence in artifacts)."
                    ),
                    remediation_action="reject_claim",
                    remediation_detail=(
                        "Reject roundtrip claim. Create a PARSE or LOAD claim "
                        "for existing test evidence. Create a BLOCKED 'write'/'save' "
                        "claim for the missing write capability."
                    ),
                ))
        return findings

    # ── Pattern 4: All variants claimed, one variant tested ──────────────────

    def _pattern_4_all_variants_one_tested(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        variant_scope = claim.metadata.get("variant", "")
        tested_variants = claim.metadata.get("tested_variants", [])
        claimed_variants = claim.metadata.get("claimed_variants", [])

        if (variant_scope == "all" or variant_scope == "") and claimed_variants and tested_variants:
            untested = set(claimed_variants) - set(tested_variants)
            if untested:
                findings.append(OverclaimFinding(
                    pattern_number=4,
                    claim_id=claim.node_id,
                    description=(
                        f"Claim '{claim.node_id}' covers 'all variants' but only "
                        f"{sorted(tested_variants)} are tested. "
                        f"Untested variants: {sorted(untested)}."
                    ),
                    remediation_action="narrow_claim",
                    remediation_detail=(
                        f"Create variant-specific claims for each tested variant: "
                        f"{sorted(tested_variants)}. "
                        f"Create BLOCKED claims for untested variants: {sorted(untested)}."
                    ),
                ))
        return findings

    # ── Pattern 5: Commercial ready, helpers only ────────────────────────────

    def _pattern_5_commercial_ready_helpers_only(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        if claim.status not in ("accepted_for_poc", "accepted_with_limitations"):
            return findings

        has_dogfood = bool(self.store.get_targets(claim.node_id, "dogfooded_by"))
        has_evidence = bool(self.store.get_targets(claim.node_id, "evidenced_by"))
        is_commercial_ready = claim.metadata.get("commercial_ready", False)

        if is_commercial_ready and not (has_dogfood and has_evidence):
            findings.append(OverclaimFinding(
                pattern_number=5,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' is marked commercial_ready but lacks "
                    f"dogfood proof (has_dogfood={has_dogfood}) or evidence package "
                    f"(has_evidence={has_evidence})."
                ),
                remediation_action="require_dogfood",
                remediation_detail=(
                    "Block commercial readiness claim. Require: (1) dogfood output artifact "
                    "with path+checksum+validation, (2) evidence package with materialized artifacts."
                ),
                severity="ERROR",
            ))
        return findings

    # ── Pattern 6: Dogfood complete, no output artifact ──────────────────────

    def _pattern_6_dogfood_no_output_artifact(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        dogfood_nodes = self.store.get_targets(claim.node_id, "dogfooded_by")
        for df in dogfood_nodes:
            has_output_path = bool(df.metadata.get("output_path") or df.metadata.get("path"))
            has_checksum = bool(df.metadata.get("sha256") or df.metadata.get("checksum"))
            if not (has_output_path and has_checksum):
                findings.append(OverclaimFinding(
                    pattern_number=6,
                    claim_id=claim.node_id,
                    description=(
                        f"DogfoodArtifact '{df.node_id}' for claim '{claim.node_id}' "
                        f"lacks output_path or checksum "
                        f"(path={has_output_path}, sha256={has_checksum})."
                    ),
                    remediation_action="require_dogfood",
                    remediation_detail=(
                        "Keep dogfood_present status but block coverage_validated. "
                        "Require: output file path + SHA-256 checksum + validation result."
                    ),
                    severity="WARNING",
                ))
        return findings

    # ── Pattern 7: Test coverage exists, not linked to claim ─────────────────

    def _pattern_7_test_not_linked_to_claim(self, claim: GraphNode) -> List[OverclaimFinding]:
        """
        This pattern requires external knowledge of unlinked tests.
        We detect it from metadata flags if set during import.
        """
        findings = []
        if claim.metadata.get("has_unlinked_tests", False):
            findings.append(OverclaimFinding(
                pattern_number=7,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' has test files in the repo but they are not "
                    f"linked via tested_by edge. Coverage remains unvalidated."
                ),
                remediation_action="require_tests",
                remediation_detail=(
                    "Link the existing test files to this claim via tested_by edges "
                    "in the proof graph. Test files that are not graph-linked do not "
                    "contribute to coverage_validated status."
                ),
                severity="WARNING",
            ))
        return findings

    # ── Pattern 8: Spec-backed, only empirical ───────────────────────────────

    def _pattern_8_spec_backed_empirical_only(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        req_sources = self.store.get_targets(claim.node_id, "derives_from")
        spec_backed = any(
            r.node_type == "SpecRequirementRef" and r.status not in ("stale", "superseded")
            for r in req_sources
        )
        empirical_only = any(
            r.node_type == "EmpiricalEvidence" and r.status not in ("stale", "superseded")
            for r in req_sources
        )
        has_official_spec = any(
            r.node_type == "SpecRequirementRef"
            and r.metadata.get("spec_type") == "official"
            for r in req_sources
        )

        if spec_backed and empirical_only and not has_official_spec:
            findings.append(OverclaimFinding(
                pattern_number=8,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' references a spec requirement but backing "
                    f"evidence is empirical-only (no official spec source)."
                ),
                remediation_action="mark_empirical_only",
                remediation_detail=(
                    "Reclassify ProductRequirement as 'empirical_only' with visible caveat. "
                    "Claim status may remain accepted but must show empirical_only provenance."
                ),
                severity="WARNING",
            ))
        return findings

    # ── Pattern 9: Accepted, requirement stale ───────────────────────────────

    def _pattern_9_accepted_stale_requirement(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        accepted_statuses = {"accepted_for_poc", "accepted_with_limitations"}
        if claim.status not in accepted_statuses:
            return findings

        req_sources = self.store.get_targets(claim.node_id, "derives_from")
        stale_reqs = [
            r for r in req_sources
            if r.node_type == "ProductRequirement" and r.status in ("stale", "superseded")
        ]
        for req in stale_reqs:
            findings.append(OverclaimFinding(
                pattern_number=9,
                claim_id=claim.node_id,
                description=(
                    f"Accepted claim '{claim.node_id}' depends on stale/superseded "
                    f"ProductRequirement '{req.node_id}' (status={req.status})."
                ),
                remediation_action="downgrade_status",
                remediation_detail=(
                    f"Demote claim '{claim.node_id}' to status='stale'. "
                    f"Revalidation required after requirement '{req.node_id}' is updated."
                ),
                severity="ERROR",
            ))
        return findings

    # ── Pattern 10: Blocking unsupported feature ─────────────────────────────

    def _pattern_10_blocking_unsupported_feature(self, claim: GraphNode) -> List[OverclaimFinding]:
        findings = []
        limitations = self.store.get_targets(claim.node_id, "limited_by")
        blocking_features = [
            n for n in limitations
            if n.node_type == "UnsupportedFeature"
            and n.metadata.get("severity", "non_blocking") == "blocking"
        ]
        if blocking_features and claim.status == "accepted_for_poc":
            feature_ids = [n.node_id for n in blocking_features]
            findings.append(OverclaimFinding(
                pattern_number=10,
                claim_id=claim.node_id,
                description=(
                    f"Claim '{claim.node_id}' is accepted_for_poc but has "
                    f"BLOCKING UnsupportedFeature(s): {feature_ids}."
                ),
                remediation_action="request_policy_decision",
                remediation_detail=(
                    "Downgrade to 'accepted_with_limitations' if the limitation is acceptable, "
                    "OR obtain a policy_decision record confirming the blocking feature "
                    "is out-of-scope for POC. Current status 'accepted_for_poc' with a "
                    "blocking unsupported feature is an overclaim."
                ),
                severity="ERROR",
            ))
        return findings


def detect_overclaims(store: GraphStore) -> OverclaimReport:
    """Convenience function: run all overclaim patterns on a store."""
    detector = OverclaimDetector(store)
    return detector.detect_all()
