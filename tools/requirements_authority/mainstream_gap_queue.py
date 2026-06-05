"""
MainstreamGapQueueGenerator: 11-step deterministic gap queue algorithm.

11-step algorithm:
  1.  Load POC target model
  2.  Load proof graph
  3.  Compute claim coverage
  4.  Identify blocked claims
  5.  Group by product/family
  6.  Rank by POC impact
  7.  Rank by smallest missing proof
  8.  Prefer required commercial + FOSS set
  9.  Include DIF/Gnumeric only if they speed POC
  10. Generate lane-specific gaps with expected files/tests/dogfood
  11. Emit mainstream-gap-queue.json

10 priority scoring fields:
  poc_required_weight, product_family_weight, missing_proof_count, dogfood_unlock_score,
  implementation_present_bonus, tests_present_bonus, overclaim_penalty, stale_penalty,
  cross_stream_packet_bonus, risk_penalty

15 queue entry fields:
  gap_id, target_product, format_id, claim_id, missing_proof_type, next_action,
  expected_files, expected_tests, expected_dogfood, recommended_lane, validation_command,
  estimated_unlock, dependencies, stop_conditions, priority_score
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .coverage_evaluator import CoverageRecord, CapabilityCoverageEvaluator
from .graph_store import GraphStore
from .models import POC_TARGETS, REQUIRED_TARGETS, GraphNode
from .poc_readiness import TARGET_REQUIRED_CAPABILITIES, STRETCH_TARGETS

# Product family weights (higher = more important)
PRODUCT_FAMILY_WEIGHTS: Dict[str, float] = {
    "fods":       10.0,
    "fodt":       10.0,
    "netpbm-net": 9.0,
    "zst":        8.0,
    "netpbm-py":  8.0,
    "sylk":       6.0,
    "dif":        5.0,
    "gnumeric":   3.0,  # stretch
}

# Required commercial+FOSS core set (higher multiplier)
REQUIRED_PRODUCT_BONUS = 2.0

# Missing proof count → unlock effort mapping
PROOF_UNLOCK_EFFORT = {
    "RequirementProof":      3,
    "ImplementationProof":   5,
    "TestProof":             3,
    "DogfoodProof":          4,
    "EvidencePackageProof":  2,
    "FreshnessProof":        2,
    "LimitationProof":       1,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GapQueueEntry:
    """15-field queue entry for a single gap."""
    gap_id: str
    target_product: str
    format_id: str
    claim_id: str
    missing_proof_type: str          # primary missing proof
    next_action: str
    expected_files: List[str]
    expected_tests: List[str]
    expected_dogfood: List[str]
    recommended_lane: str
    validation_command: str
    estimated_unlock: int            # effort points (lower = faster)
    dependencies: List[str]
    stop_conditions: List[str]
    priority_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "target_product": self.target_product,
            "format_id": self.format_id,
            "claim_id": self.claim_id,
            "missing_proof_type": self.missing_proof_type,
            "next_action": self.next_action,
            "expected_files": self.expected_files,
            "expected_tests": self.expected_tests,
            "expected_dogfood": self.expected_dogfood,
            "recommended_lane": self.recommended_lane,
            "validation_command": self.validation_command,
            "estimated_unlock": self.estimated_unlock,
            "dependencies": self.dependencies,
            "stop_conditions": self.stop_conditions,
            "priority_score": self.priority_score,
        }


@dataclass
class GapQueueResult:
    entries: List[GapQueueEntry] = field(default_factory=list)
    generated_at: str = field(default_factory=_now_iso)
    graph_hash: str = ""
    algorithm_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "graph_hash": self.graph_hash,
            "total_gaps": len(self.entries),
            "algorithm_steps": self.algorithm_steps,
            "entries": [e.to_dict() for e in self.entries],
        }

    def save(self, path) -> None:
        import pathlib
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


class MainstreamGapQueueGenerator:
    """
    Generates the mainstream-gap-queue.json following the 11-step algorithm.
    Output is deterministic for the same graph state.
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def generate(self) -> GapQueueResult:
        result = GapQueueResult(graph_hash=self.store.compute_graph_hash())

        # Step 1: Load POC target model
        result.algorithm_steps.append("Step 01: Load POC target model")
        poc_targets = list(POC_TARGETS)

        # Step 2: Load proof graph
        result.algorithm_steps.append(f"Step 02: Proof graph loaded — graph_hash={result.graph_hash[:16]}...")

        # Step 3: Compute claim coverage
        result.algorithm_steps.append("Step 03: Compute claim coverage")
        evaluator = CapabilityCoverageEvaluator(self.store)
        all_records = evaluator.evaluate_all()

        # Step 4: Identify blocked claims
        result.algorithm_steps.append("Step 04: Identify blocked claims")
        blocked = [r for r in all_records if r.coverage_verdict in ("BLOCKED", "PARTIAL")]
        result.algorithm_steps.append(f"  Found {len(blocked)} blocked/partial claims")

        # Step 5: Group by product/family
        result.algorithm_steps.append("Step 05: Group blocked claims by product/family")
        by_product: Dict[str, List[CoverageRecord]] = {}
        for rec in blocked:
            claim = self.store.get_node(rec.claim_id)
            product_id = claim.metadata.get("product_id", "unknown") if claim else "unknown"
            by_product.setdefault(product_id, []).append(rec)

        # Steps 6–9: Score and filter
        result.algorithm_steps.append("Step 06: Rank by POC impact")
        result.algorithm_steps.append("Step 07: Rank by smallest missing proof")
        result.algorithm_steps.append("Step 08: Prefer required commercial + FOSS set")
        result.algorithm_steps.append("Step 09: Include DIF/Gnumeric only if they speed POC")

        entries: List[GapQueueEntry] = []
        gap_counter = 0

        for product_id in sorted(poc_targets):
            records_for_product = by_product.get(product_id, [])

            # Include DIF/Gnumeric only if helpful (step 9)
            if product_id == "gnumeric" and not records_for_product:
                # No blocked gnumeric claims → skip stretch target
                continue
            if product_id == "dif":
                # DIF included only if faster than SYLK
                sylk_records = by_product.get("sylk", [])
                dif_faster = len(records_for_product) < len(sylk_records)
                if not dif_faster and not records_for_product:
                    continue

            # No gaps for this product
            if not records_for_product:
                continue

            for rec in records_for_product:
                gap_counter += 1
                entry = self._build_entry(gap_counter, product_id, rec)
                entries.append(entry)

        # Step 10: Generate lane-specific gaps
        result.algorithm_steps.append("Step 10: Generate lane-specific gaps with expected artifacts")

        # Sort by priority score (descending), then by target + claim for determinism
        entries.sort(key=lambda e: (-e.priority_score, e.target_product, e.claim_id))

        # Step 11: Emit gap queue
        result.algorithm_steps.append("Step 11: Emit mainstream-gap-queue.json")
        result.entries = entries

        return result

    def _build_entry(
        self, counter: int, product_id: str, rec: CoverageRecord
    ) -> GapQueueEntry:
        """Build a single 15-field gap queue entry."""
        claim = self.store.get_node(rec.claim_id)
        operation = rec.metadata.get("operation", "unknown")
        format_id = claim.metadata.get("format_id", product_id) if claim else product_id
        primary_missing = rec.missing_proof_types[0] if rec.missing_proof_types else "Unknown"

        # Priority scoring
        family_weight = PRODUCT_FAMILY_WEIGHTS.get(product_id, 1.0)
        poc_required = REQUIRED_PRODUCT_BONUS if product_id in REQUIRED_TARGETS else 1.0
        missing_count = len(rec.missing_proof_types)
        dogfood_unlock = 2.0 if "DogfoodProof" in rec.missing_proof_types else 0.0
        impl_bonus = 1.0 if rec.metadata.get("has_implementation") else 0.0
        test_bonus = 0.5 if rec.metadata.get("has_tests") else 0.0
        overclaim_penalty = -2.0 if "overclaim" in rec.coverage_status else 0.0
        stale_penalty = -3.0 if "stale" in rec.coverage_status else 0.0
        cross_stream_bonus = 0.5  # default
        risk_penalty = -1.0 if missing_count > 3 else 0.0

        priority_score = (
            family_weight * poc_required
            + dogfood_unlock
            + impl_bonus
            + test_bonus
            + cross_stream_bonus
            + overclaim_penalty
            + stale_penalty
            + risk_penalty
            - missing_count * 0.5
        )

        # Estimated unlock effort
        unlock_effort = sum(PROOF_UNLOCK_EFFORT.get(mp, 3) for mp in rec.missing_proof_types)

        # Detect architecture-blocked export claims (missing target writer library).
        # A claim is architecture-blocked if it has a blocked_by edge to an UnsupportedFeature,
        # or its metadata indicates a target writer is missing.
        claim_metadata = claim.metadata if claim else {}
        blocked_by_nodes = self.store.get_targets(rec.claim_id, "blocked_by")
        has_blocked_by_unsupported = any(
            n.node_type == "UnsupportedFeature" for n in blocked_by_nodes
        )
        blocked_reason = claim_metadata.get("blocked_reason", "")
        arch_blocked = (
            has_blocked_by_unsupported
            or "architecture_blocked_missing_target_writer" in blocked_reason
            or "target writer" in blocked_reason.lower()
            or "architecture_blocked" in blocked_reason
            or claim_metadata.get("coverage_status") == "ARCHITECTURE_BLOCKED_MISSING_TARGET_WRITER"
        )

        # Recommended lane based on operation — architecture-blocked exports get special routing
        if arch_blocked:
            lane = "Target-Writer-Architecture"
        elif operation in ("dogfood", "export"):
            lane = "Mainstream-Dogfood"
        elif operation in ("parse", "load", "inspect"):
            lane = "Mainstream-Parse"
        elif operation in ("save", "write", "roundtrip"):
            lane = "Mainstream-Write"
        else:
            lane = "Mainstream-General"

        # Build expected artifacts
        if arch_blocked:
            # Architecture-blocked: need writer library, not dogfood
            target_lib = {
                "export_csv": "FormatFactory.Csv",
                "export_html": "FormatFactory.Html",
                "export_markdown": "FormatFactory.Markdown",
                "export_txt": "FormatFactory.Txt",
            }.get(operation, f"FormatFactory.{operation.title()}")
            expected_files = [
                f"src/net/{format_id.lower()}/{target_lib}/...",
                f"src/net/{format_id.lower()}/... (source exporter must call {target_lib})",
            ]
            expected_tests = [
                f"tests/net/{format_id.lower()}/test_{operation}_writer_*.py"
            ]
            expected_dogfood = []  # no dogfood until writer exists
        else:
            expected_files = [
                f"src/{'python' if 'py' in product_id else 'net'}/{format_id.lower()}/..."
            ]
            expected_tests = [
                f"tests/{'python' if 'py' in product_id else 'net'}/{format_id.lower()}/test_{operation}_*.py"
            ]
            expected_dogfood = (
                [f"examples/{'python' if 'py' in product_id else 'net'}/{format_id.lower()}/{operation}_dogfood.*"]
                if "DogfoodProof" in rec.missing_proof_types else []
            )

        validation_command = (
            f"python tools/requirements_authority/validate_requirements_authority.py "
            f"--claim {rec.claim_id}"
        )

        if arch_blocked:
            stop_conditions = [
                f"claim_id='{rec.claim_id}' reaches coverage_verdict=PASS",
                f"Target writer library created and {rec.claim_id} implementation calls it",
                "Do NOT proceed with /add-dogfood-export until writer library exists",
            ]
        else:
            stop_conditions = [
                f"claim_id='{rec.claim_id}' reaches coverage_verdict=PASS",
                f"All missing proof types resolved: {rec.missing_proof_types}",
            ]

        if arch_blocked:
            target_lib = {
                "export_csv": "FormatFactory.Csv",
                "export_html": "FormatFactory.Html",
                "export_markdown": "FormatFactory.Markdown",
                "export_txt": "FormatFactory.Txt",
            }.get(operation, f"FormatFactory.{operation.title()}")
            next_action = (
                f"Create missing target writer library {target_lib} for {format_id}/{operation} — "
                f"source exporter must call {target_lib} writer — "
                f"do NOT use /add-dogfood-export until writer library exists"
            )
        else:
            next_action = f"Provide {primary_missing} for {product_id}/{operation} claim"

        return GapQueueEntry(
            gap_id=f"gap:{product_id}:{operation}:{counter:04d}",
            target_product=product_id,
            format_id=format_id,
            claim_id=rec.claim_id,
            missing_proof_type="TargetWriterLibraryMissing" if arch_blocked else primary_missing,
            next_action=next_action,
            expected_files=expected_files,
            expected_tests=expected_tests,
            expected_dogfood=expected_dogfood,
            recommended_lane=lane,
            validation_command=validation_command,
            estimated_unlock=unlock_effort,
            dependencies=rec.missing_proof_types[1:],  # secondary missing proofs
            stop_conditions=stop_conditions,
            priority_score=round(priority_score, 3),
        )


def generate_gap_queue(store: GraphStore) -> GapQueueResult:
    """Convenience function: generate mainstream gap queue."""
    generator = MainstreamGapQueueGenerator(store)
    return generator.generate()
