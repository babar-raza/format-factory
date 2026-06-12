"""
SupervisorVerdictPacketGenerator: 16-field normalized verdict packet.

16 packet fields:
  packet_id, generated_at, source_graph_hash, claims_checked, coverage_records,
  overclaim_risks, stale_claims, unsupported_features, poc_readiness_verdict,
  mainstream_gap_queue_ref, recommended_supervisor_decision, false_pass_risks,
  false_stop_risks, stream_consumption_status, external_tool_boundary, evidence_package_refs

9 supervisor decision values:
  ACCEPT_PRODUCT_PROGRESS, ACCEPT_WITH_LIMITATIONS, REJECT_OVERCLAIM,
  BLOCK_MISSING_DOGFOOD, BLOCK_MISSING_REQUIREMENT, BLOCK_STALE_PROOF,
  CONTINUE_MAINSTREAM_WITH_GAP_QUEUE, CONTINUE_WITH_REROUTE, NEEDS_POLICY_DECISION

False pass risks (>=4):
  1. evidence_package_present_but_claim_not_graph_linked
  2. test_passes_but_not_linked_to_claim
  3. poc_targets_shows_pass_but_requirement_stale
  4. dogfood_output_exists_but_not_validated

False stop risks (>=3):
  1. overclaim_detection_flagging_valid_partial_claim
  2. staleness_flagging_already_recomputed_records
  3. empirical_only_requirement_blocking_acceptable_poc_claim
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from .coverage_evaluator import CoverageRecord
from .graph_store import GraphStore
from .mainstream_gap_queue import GapQueueResult
from .overclaim_detector import OverclaimReport
from .poc_readiness import PocReadinessResult
from .staleness_invalidator import StalenessReport

SUPERVISOR_DECISIONS = [
    "ACCEPT_PRODUCT_PROGRESS",
    "ACCEPT_WITH_LIMITATIONS",
    "REJECT_OVERCLAIM",
    "BLOCK_MISSING_DOGFOOD",
    "BLOCK_MISSING_REQUIREMENT",
    "BLOCK_STALE_PROOF",
    "CONTINUE_MAINSTREAM_WITH_GAP_QUEUE",
    "CONTINUE_WITH_REROUTE",
    "NEEDS_POLICY_DECISION",
]

FALSE_PASS_RISKS = [
    {
        "risk_id": "FPR-001",
        "description": "evidence_package_present_but_claim_not_graph_linked",
        "detail": "An EvidencePackage exists but the CapabilityClaim has no evidenced_by edge. "
                  "The package proves its artifacts, not the claim.",
    },
    {
        "risk_id": "FPR-002",
        "description": "test_passes_but_not_linked_to_claim",
        "detail": "Test files pass in CI but are not linked to a CapabilityClaim via tested_by. "
                  "Tests that are not graph-linked do not count as TestProof.",
    },
    {
        "risk_id": "FPR-003",
        "description": "poc_targets_shows_pass_but_requirement_stale",
        "detail": "poc-targets.yaml shows a format as PASS/ready but the backing "
                  "ProductRequirement is stale. poc-targets is a dashboard, not authority.",
    },
    {
        "risk_id": "FPR-004",
        "description": "dogfood_output_exists_but_not_validated",
        "detail": "A dogfood output file exists on disk but is not validated "
                  "(no path+checksum+validation record in graph). "
                  "Presence alone does not satisfy DogfoodProof.",
    },
]

FALSE_STOP_RISKS = [
    {
        "risk_id": "FSR-001",
        "description": "overclaim_detection_flagging_valid_partial_claim",
        "detail": "OverclaimDetector may flag a valid partial claim as overclaim "
                  "if the claim dimensions are not narrowed yet. "
                  "Remediation: narrow_claim or split_claim, then re-evaluate.",
    },
    {
        "risk_id": "FSR-002",
        "description": "staleness_flagging_already_recomputed_records",
        "detail": "StalenessInvalidationEngine may flag records as stale "
                  "if they were not updated in the graph after recomputation. "
                  "Verify: recompute and re-import before blocking on staleness.",
    },
    {
        "risk_id": "FSR-003",
        "description": "empirical_only_requirement_blocking_acceptable_poc_claim",
        "detail": "An empirical_only ProductRequirement may trigger a strict validator block "
                  "when the claim is actually acceptable for POC with caveat. "
                  "Remediation: reclassify requirement as empirical_only and allow "
                  "accepted_with_limitations claim status.",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SupervisorVerdictPacket:
    """16-field normalized supervisor verdict packet."""
    # Field 1
    packet_id: str
    # Field 2
    generated_at: str
    # Field 3
    source_graph_hash: str
    # Field 4
    claims_checked: int
    # Field 5
    coverage_records: List[Dict[str, Any]]
    # Field 6
    overclaim_risks: List[Dict[str, Any]]
    # Field 7
    stale_claims: List[str]
    # Field 8
    unsupported_features: List[Dict[str, Any]]
    # Field 9
    poc_readiness_verdict: str
    # Field 10
    mainstream_gap_queue_ref: str
    # Field 11
    recommended_supervisor_decision: str
    # Field 12
    false_pass_risks: List[Dict[str, Any]]
    # Field 13
    false_stop_risks: List[Dict[str, Any]]
    # Field 14
    stream_consumption_status: Dict[str, str]
    # Field 15
    external_tool_boundary: Dict[str, str]
    # Field 16
    evidence_package_refs: List[str]

    def __post_init__(self):
        if self.recommended_supervisor_decision not in SUPERVISOR_DECISIONS:
            raise ValueError(
                f"Unknown supervisor decision: {self.recommended_supervisor_decision!r}. "
                f"Valid: {SUPERVISOR_DECISIONS}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "generated_at": self.generated_at,
            "source_graph_hash": self.source_graph_hash,
            "claims_checked": self.claims_checked,
            "coverage_records": self.coverage_records,
            "overclaim_risks": self.overclaim_risks,
            "stale_claims": self.stale_claims,
            "unsupported_features": self.unsupported_features,
            "poc_readiness_verdict": self.poc_readiness_verdict,
            "mainstream_gap_queue_ref": self.mainstream_gap_queue_ref,
            "recommended_supervisor_decision": self.recommended_supervisor_decision,
            "false_pass_risks": self.false_pass_risks,
            "false_stop_risks": self.false_stop_risks,
            "stream_consumption_status": self.stream_consumption_status,
            "external_tool_boundary": self.external_tool_boundary,
            "evidence_package_refs": self.evidence_package_refs,
        }

    def save(self, path) -> None:
        import pathlib
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


class SupervisorVerdictPacketGenerator:
    """
    Generates a normalized 16-field SupervisorVerdictPacket from all evaluator outputs.
    The Supervisor must not infer PASS from prose — only from this packet.
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def generate(
        self,
        coverage_records: List[CoverageRecord],
        overclaim_report: OverclaimReport,
        staleness_report: StalenessReport,
        readiness_result: PocReadinessResult,
        gap_queue_result: GapQueueResult,
        gap_queue_path: str = "reports/requirement-capability-authority-layer-mwp/mainstream-gap-queue.json",
    ) -> SupervisorVerdictPacket:

        graph_hash = self.store.compute_graph_hash()
        packet_id = f"svp:{graph_hash[:16]}:{_now_iso()}"

        # Field 5: coverage records summary (top-level verdicts)
        cov_summary = [
            {"claim_id": r.claim_id, "verdict": r.coverage_verdict,
             "proof_level": r.proof_level, "status": r.coverage_status}
            for r in coverage_records[:50]  # cap for packet size
        ]

        # Field 6: overclaim risks
        overclaim_risks = [f.to_dict() for f in overclaim_report.findings[:20]]

        # Field 7: stale claims
        stale_claims = staleness_report.stale_claim_ids[:50]

        # Field 8: unsupported features
        unsupported_features = [
            {"node_id": n.node_id, "label": n.label,
             "severity": n.metadata.get("severity", "non_blocking"),
             "product_id": n.metadata.get("product_id", "unknown")}
            for n in self.store.nodes_by_type("UnsupportedFeature")
        ]

        # Field 9: POC readiness verdict
        poc_verdict = readiness_result.overall_verdict()

        # Field 10: gap queue ref
        gap_queue_ref = gap_queue_path

        # Field 11: recommended supervisor decision
        decision = self._recommend_decision(
            coverage_records, overclaim_report, staleness_report, readiness_result
        )

        # Field 14: stream consumption status
        stream_status = {
            "mainstream": "consuming_gap_queue",
            "skills": "consuming_requirement_and_claim_ids",
            "acceleration": "consuming_proof_graph_summaries",
            "supervisor": "consuming_verdict_packet",
            "specification_authority": "providing_spec_requirements",
            "evidence": "materializing_artifacts",
        }

        # Field 15: external tool boundary
        ext_boundary = {
            "mcp_tools": "DISABLED_BY_DEFAULT — requires explicit human approval",
            "ghidra_mcp": "DISABLED_BY_DEFAULT",
            "ruflo": "ABSENT — fallback to local coordinator",
            "superpowers": "normalized_skills_only",
        }

        # Field 16: evidence package refs
        evpkg_refs = [
            n.node_id for n in self.store.nodes_by_type("EvidencePackage")
        ]

        return SupervisorVerdictPacket(
            packet_id=packet_id,
            generated_at=_now_iso(),
            source_graph_hash=graph_hash,
            claims_checked=len(coverage_records),
            coverage_records=cov_summary,
            overclaim_risks=overclaim_risks,
            stale_claims=stale_claims,
            unsupported_features=unsupported_features,
            poc_readiness_verdict=poc_verdict,
            mainstream_gap_queue_ref=gap_queue_ref,
            recommended_supervisor_decision=decision,
            false_pass_risks=FALSE_PASS_RISKS,
            false_stop_risks=FALSE_STOP_RISKS,
            stream_consumption_status=stream_status,
            external_tool_boundary=ext_boundary,
            evidence_package_refs=evpkg_refs,
        )

    def _recommend_decision(
        self,
        coverage_records: List[CoverageRecord],
        overclaim_report: OverclaimReport,
        staleness_report: StalenessReport,
        readiness_result: PocReadinessResult,
    ) -> str:
        """Determine recommended supervisor decision from all evaluator outputs."""
        # Check for blocking conditions first
        has_stale_proof = bool(staleness_report.stale_claim_ids)
        has_overclaim = overclaim_report.error_count > 0
        blocked_records = [r for r in coverage_records if r.coverage_verdict == "BLOCKED"]

        if has_stale_proof:
            return "BLOCK_STALE_PROOF"

        if has_overclaim:
            return "REJECT_OVERCLAIM"

        missing_dogfood = [
            r for r in blocked_records if "DogfoodProof" in r.missing_proof_types
        ]
        if missing_dogfood:
            return "BLOCK_MISSING_DOGFOOD"

        missing_req = [
            r for r in blocked_records if "RequirementProof" in r.missing_proof_types
        ]
        if missing_req:
            return "BLOCK_MISSING_REQUIREMENT"

        # Check policy required
        policy_needed = any(
            n.metadata.get("flags", []) and "policy_decision_required" in n.metadata["flags"]
            for n in self.store.nodes_by_type("CapabilityClaim")
        )
        if policy_needed:
            return "NEEDS_POLICY_DECISION"

        # Check partial/limitations
        partial_records = [r for r in coverage_records if r.coverage_verdict == "PARTIAL"]
        if partial_records:
            return "ACCEPT_WITH_LIMITATIONS"

        # No blocks → continue with gap queue if there are gaps
        if coverage_records and all(r.coverage_verdict == "PASS" for r in coverage_records):
            return "ACCEPT_PRODUCT_PROGRESS"

        return "CONTINUE_MAINSTREAM_WITH_GAP_QUEUE"


def generate_supervisor_packet(
    store: GraphStore,
    coverage_records: List[CoverageRecord],
    overclaim_report: OverclaimReport,
    staleness_report: StalenessReport,
    readiness_result: PocReadinessResult,
    gap_queue_result: GapQueueResult,
) -> SupervisorVerdictPacket:
    """Convenience function: generate supervisor verdict packet."""
    generator = SupervisorVerdictPacketGenerator(store)
    return generator.generate(
        coverage_records=coverage_records,
        overclaim_report=overclaim_report,
        staleness_report=staleness_report,
        readiness_result=readiness_result,
        gap_queue_result=gap_queue_result,
    )
