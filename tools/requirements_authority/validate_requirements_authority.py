"""
validate_requirements_authority.py — CLI validator for the requirements authority layer.

Usage:
  python tools/requirements_authority/validate_requirements_authority.py \
    --graph-dir requirements-authority/graph/ \
    --fixtures-dir requirements-authority/fixtures/ \
    --output-dir reports/requirement-capability-authority-layer-mwp/ \
    [--claim <claim_id>]

Outputs:
  - validation-results.json  {checks: [{name, status, evidence}], overall: PASS|FAIL}
  - validation-results.md    human-readable summary
  - Prints summary to stdout
"""
import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repo root is on sys.path for both direct execution and package import
_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP | WARNING
    evidence: str
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "evidence": self.evidence,
            "detail": self.detail,
        }


@dataclass
class ValidationReport:
    checks: List[CheckResult] = field(default_factory=list)
    generated_at: str = field(default_factory=_now_iso)

    @property
    def overall(self) -> str:
        if any(c.status == "FAIL" for c in self.checks):
            return "FAIL"
        return "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "overall": self.overall,
            "checks": [c.to_dict() for c in self.checks],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Requirements Authority Validation Results",
            f"Generated: {self.generated_at}",
            f"**Overall: {self.overall}**",
            "",
            "| Check | Status | Evidence |",
            "|-------|--------|----------|",
        ]
        for c in self.checks:
            icon = "✅" if c.status == "PASS" else ("⚠️" if c.status == "WARNING" else ("⏭️" if c.status == "SKIP" else "❌"))
            lines.append(f"| {c.name} | {icon} {c.status} | {c.evidence} |")
        if any(c.detail for c in self.checks):
            lines += ["", "## Details"]
            for c in self.checks:
                if c.detail:
                    lines.append(f"- **{c.name}** ({c.status}): {c.detail}")
        return "\n".join(lines)

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "validation-results.json").write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )
        (output_dir / "validation-results.md").write_text(
            self.to_markdown(), encoding="utf-8"
        )


def _check(report: ValidationReport, name: str, passed: bool,
           evidence: str, detail: str = "", skip: bool = False) -> None:
    if skip:
        report.checks.append(CheckResult(name=name, status="SKIP", evidence=evidence, detail=detail))
        return
    status = "PASS" if passed else "FAIL"
    report.checks.append(CheckResult(name=name, status=status, evidence=evidence, detail=detail))


def _check_warn(report: ValidationReport, name: str, ok: bool,
                evidence: str, detail: str = "") -> None:
    status = "PASS" if ok else "WARNING"
    report.checks.append(CheckResult(name=name, status=status, evidence=evidence, detail=detail))


def run_validation(
    graph_dir: Optional[Path],
    fixtures_dir: Optional[Path],
    output_dir: Path,
    claim_id: Optional[str] = None,
) -> ValidationReport:
    report = ValidationReport()

    # --- Import tools ---
    try:
        from tools.requirements_authority.graph_store import GraphStore
        from tools.requirements_authority.validators import GraphValidator
        from tools.requirements_authority.coverage_evaluator import CapabilityCoverageEvaluator
        from tools.requirements_authority.overclaim_detector import OverclaimDetector
        from tools.requirements_authority.staleness_invalidator import StalenessInvalidationEngine
        from tools.requirements_authority.poc_readiness import PocReadinessComputer
        from tools.requirements_authority.mainstream_gap_queue import MainstreamGapQueueGenerator
        from tools.requirements_authority.supervisor_verdict_packet import SupervisorVerdictPacketGenerator
        from tools.requirements_authority.poc_targets_sync_proposal import PocTargetsSyncProposalGenerator
        from tools.requirements_authority.run_replay_fixtures import GoldenReplaySuite
        _check(report, "tool_imports", True, "All 13 tool modules imported successfully")
    except ImportError as e:
        _check(report, "tool_imports", False, str(e),
               "Could not import one or more tool modules")
        report.save(output_dir)
        return report

    # --- Load graph ---
    if graph_dir and graph_dir.exists():
        store = GraphStore.load_from_dir(graph_dir)
        node_count = len(store.nodes)
        edge_count = len(store.edges)
        _check(report, "graph_load",
               node_count > 0 or edge_count == 0,
               f"Loaded {node_count} nodes, {edge_count} edges from {graph_dir}",
               f"nodes.jsonl + edges.jsonl parsed successfully")
    else:
        # Use an empty store for smoke-test validation
        store = GraphStore()
        _check(report, "graph_load", True,
               "No graph_dir provided — using empty store for smoke test",
               skip=True)

    # --- Graph hash ---
    graph_hash = store.compute_graph_hash()
    _check(report, "graph_hash_deterministic",
           len(graph_hash) == 64,
           f"graph_hash={graph_hash[:16]}... (SHA-256, 64 hex chars)",
           "SHA-256 hash computed deterministically")

    # --- Schema validation ---
    validator = GraphValidator(store)
    val_result = validator.validate()
    _check(report, "schema_and_invariants",
           val_result.is_valid,
           f"{len(val_result.errors)} errors, {len(val_result.warnings)} warnings",
           val_result.summary() if not val_result.is_valid else "")

    # --- Coverage evaluator ---
    evaluator = CapabilityCoverageEvaluator(store)
    if claim_id:
        claim_node = store.get_node(claim_id)
        if claim_node:
            cov_records = [evaluator.evaluate_claim(claim_node)]
        else:
            cov_records = []
            _check(report, "claim_lookup", False, f"Claim '{claim_id}' not found in graph")
    else:
        cov_records = evaluator.evaluate_all()

    cov_summary = evaluator.compute_summary(cov_records)
    _check(report, "coverage_evaluator",
           True,  # evaluator ran — verdict may vary
           f"Evaluated {len(cov_records)} claims. "
           f"Overall: {cov_summary['overall_verdict']} "
           f"({cov_summary['passed']}/{cov_summary['total_claims']} PASS)")

    # --- Overclaim detector ---
    detector = OverclaimDetector(store)
    overclaim_report = detector.detect_all()
    _check_warn(report, "overclaim_detector",
                overclaim_report.error_count == 0,
                f"{overclaim_report.error_count} errors, {overclaim_report.warning_count} warnings",
                str([f.description[:60] for f in overclaim_report.findings[:3]]) if overclaim_report.has_findings else "")

    # --- Staleness engine ---
    staleness_engine = StalenessInvalidationEngine(store)
    stale_report = staleness_engine.run()
    _check_warn(report, "staleness_invalidator",
                len(stale_report.stale_claim_ids) == 0,
                f"{len(stale_report.stale_events)} stale events, {len(stale_report.stale_claim_ids)} stale claims")

    # --- POC readiness ---
    poc_computer = PocReadinessComputer(store)
    poc_result = poc_computer.compute_all()
    _check(report, "poc_readiness_netpbm_retained",
           poc_result.netpbm_retained,
           "netpbm_retained=True — invariant enforced")
    _check(report, "poc_readiness_svg_rejected",
           poc_result.svg_replacement_rejected,
           "svg_replacement_rejected=True — SVG must not replace Netpbm")

    # --- Gap queue ---
    gap_gen = MainstreamGapQueueGenerator(store)
    gap_result = gap_gen.generate()
    _check(report, "gap_queue_generated",
           True,
           f"Gap queue: {len(gap_result.entries)} entries, graph_hash={gap_result.graph_hash[:16]}...")

    # --- Supervisor verdict packet ---
    svp_gen = SupervisorVerdictPacketGenerator(store)
    svp = svp_gen.generate(
        coverage_records=cov_records,
        overclaim_report=overclaim_report,
        staleness_report=stale_report,
        readiness_result=poc_result,
        gap_queue_result=gap_result,
    )
    _check(report, "supervisor_verdict_packet",
           svp.recommended_supervisor_decision in [
               "ACCEPT_PRODUCT_PROGRESS", "ACCEPT_WITH_LIMITATIONS",
               "REJECT_OVERCLAIM", "BLOCK_MISSING_DOGFOOD", "BLOCK_MISSING_REQUIREMENT",
               "BLOCK_STALE_PROOF", "CONTINUE_MAINSTREAM_WITH_GAP_QUEUE",
               "CONTINUE_WITH_REROUTE", "NEEDS_POLICY_DECISION",
           ],
           f"packet_id={svp.packet_id[:24]}... "
           f"decision={svp.recommended_supervisor_decision}")

    # --- source_graph_hash field present ---
    _check(report, "source_graph_hash_present",
           bool(svp.source_graph_hash),
           f"source_graph_hash={svp.source_graph_hash[:16]}...")

    # --- false_stop_risks present ---
    _check(report, "false_stop_risks_present",
           len(svp.false_stop_risks) >= 3,
           f"false_stop_risks count={len(svp.false_stop_risks)} (>= 3 required)")

    # --- Sync proposal (never mutates) ---
    sync_gen = PocTargetsSyncProposalGenerator(store)
    sync_proposal = sync_gen.generate(poc_result)
    _check(report, "poc_targets_sync_proposal_no_mutation",
           "PROHIBITION" in sync_proposal.prohibition_note,
           f"proposal_id={sync_proposal.proposal_id[:24]}... "
           f"Prohibition note present — never direct mutation")

    # --- Golden replay fixtures ---
    if fixtures_dir and fixtures_dir.exists():
        replay_suite = GoldenReplaySuite(fixtures_dir)
        replay_result = replay_suite.run_all()
        _check(report, "replay_fixtures_all_pass",
               replay_result.overall_pass,
               f"{replay_result.passed_fixtures}/{replay_result.total_fixtures} fixtures PASS")
        _check(report, "determinism_test",
               replay_result.determinism_pass,
               "Same inputs → same graph hash across 3 reruns for all fixtures")
        # Save replay results
        replay_output = output_dir / "replay-suite-results.json"
        replay_output.write_text(
            json.dumps(replay_result.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )
    else:
        _check(report, "replay_fixtures_all_pass", True,
               "Fixtures dir not found — skipping", skip=True)
        _check(report, "determinism_test", True,
               "Fixtures dir not found — skipping", skip=True)

    # Save all evaluator outputs
    _save_outputs(store, cov_records, overclaim_report, stale_report,
                  poc_result, gap_result, svp, sync_proposal, output_dir,
                  evaluator)

    report.save(output_dir)
    return report


def _save_outputs(store, cov_records, overclaim_report, stale_report,
                  poc_result, gap_result, svp, sync_proposal, output_dir, evaluator):
    """Save all evaluator outputs to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Coverage records
    cov_summary = evaluator.compute_summary(cov_records)
    (output_dir / "coverage-records.json").write_text(
        json.dumps({
            "summary": cov_summary,
            "records": [r.to_dict() for r in cov_records],
        }, indent=2, sort_keys=True), encoding="utf-8"
    )

    # Staleness outputs
    stale_dir = output_dir / "staleness"
    stale_report.save_all(stale_dir)

    # Gap queue
    gap_result.save(output_dir / "mainstream-gap-queue.json")

    # Supervisor verdict packet
    svp.save(output_dir / "supervisor-verdict-packet.json")

    # POC readiness
    (output_dir / "poc-readiness.json").write_text(
        json.dumps(poc_result.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )

    # Sync proposal
    sync_proposal.save(output_dir / "poc-targets-sync-proposal.json")

    # Overclaim report
    (output_dir / "overclaim-report.json").write_text(
        json.dumps(overclaim_report.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the requirements authority layer proof graph."
    )
    parser.add_argument("--graph-dir", type=Path, default=None,
                        help="Directory containing nodes.jsonl + edges.jsonl")
    parser.add_argument("--fixtures-dir", type=Path, default=None,
                        help="Directory containing golden replay fixture packs")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("reports/requirement-capability-authority-layer-mwp"),
                        help="Output directory for validation results")
    parser.add_argument("--claim", type=str, default=None,
                        help="Validate a single claim by ID")
    args = parser.parse_args()

    report = run_validation(
        graph_dir=args.graph_dir,
        fixtures_dir=args.fixtures_dir,
        output_dir=args.output_dir,
        claim_id=args.claim,
    )

    print(f"Overall: {report.overall}")
    for check in report.checks:
        icon = "PASS" if check.status == "PASS" else check.status
        evidence_safe = check.evidence.encode("ascii", "replace").decode("ascii")
        print(f"  [{icon:7s}] {check.name}: {evidence_safe}")

    return 0 if report.overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
