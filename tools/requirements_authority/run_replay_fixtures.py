"""
GoldenReplaySuite: run all 6 golden replay fixture packs and verify determinism.

6 fixture packs:
  a. clean_fods_export       — clean FODS export claim, all proof satisfied
  b. fodt_export_not_save_overclaim — FODT export-only, save overclaim detected
  c. netpbm_partial_variant_coverage — Netpbm partial variant coverage
  d. zst_roundtrip_clean     — ZST roundtrip clean proof
  e. sylk_missing_dogfood    — SYLK claim missing dogfood
  f. dif_empirical_only_caveated — DIF empirical-only requirement

Determinism test: same input JSONL fixture → same graph hash across 3 reruns.
"""
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .coverage_evaluator import CapabilityCoverageEvaluator
from .graph_store import GraphStore
from .overclaim_detector import OverclaimDetector
from .staleness_invalidator import StalenessInvalidationEngine
from .validators import GraphValidator

FIXTURE_PACKS = [
    "clean_fods_export",
    "fodt_export_not_save_overclaim",
    "netpbm_partial_variant_coverage",
    "zst_roundtrip_clean",
    "sylk_missing_dogfood",
    "dif_empirical_only_caveated",
]


@dataclass
class FixtureResult:
    fixture_name: str
    graph_hash: str
    coverage_verdict: str         # PASS | FAIL | PARTIAL | BLOCKED
    overclaim_found: bool
    stale_found: bool
    validator_errors: int
    expected_coverage_verdict: str
    expected_overclaim: bool
    expected_stale: bool
    passed: bool
    notes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "graph_hash": self.graph_hash,
            "coverage_verdict": self.coverage_verdict,
            "overclaim_found": self.overclaim_found,
            "stale_found": self.stale_found,
            "validator_errors": self.validator_errors,
            "expected_coverage_verdict": self.expected_coverage_verdict,
            "expected_overclaim": self.expected_overclaim,
            "expected_stale": self.expected_stale,
            "passed": self.passed,
            "notes": self.notes,
            "error": self.error,
        }


@dataclass
class DeterminismResult:
    fixture_name: str
    hashes: List[str]  # 3 reruns
    deterministic: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "hashes": self.hashes,
            "deterministic": self.deterministic,
            "notes": self.notes,
        }


@dataclass
class ReplaySuiteResult:
    fixture_results: List[FixtureResult] = field(default_factory=list)
    determinism_results: List[DeterminismResult] = field(default_factory=list)
    overall_pass: bool = False
    total_fixtures: int = 0
    passed_fixtures: int = 0
    determinism_pass: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_pass": self.overall_pass,
            "total_fixtures": self.total_fixtures,
            "passed_fixtures": self.passed_fixtures,
            "determinism_pass": self.determinism_pass,
            "fixture_results": [r.to_dict() for r in self.fixture_results],
            "determinism_results": [d.to_dict() for d in self.determinism_results],
        }


def _load_store_from_fixture(fixture_dir: Path) -> GraphStore:
    """Load GraphStore from nodes.jsonl + edges.jsonl in fixture_dir."""
    return GraphStore.load_from_dir(fixture_dir)


def _load_expected(fixture_dir: Path) -> Dict[str, Any]:
    """Load expected_coverage.json from fixture_dir."""
    p = fixture_dir / "expected_coverage.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _run_single_fixture(fixture_dir: Path, fixture_name: str) -> FixtureResult:
    """Run all evaluators on a single fixture pack."""
    try:
        store = _load_store_from_fixture(fixture_dir)
        expected = _load_expected(fixture_dir)

        graph_hash = store.compute_graph_hash()

        # Run validator
        validator = GraphValidator(store)
        val_result = validator.validate()

        # Run coverage evaluator
        evaluator = CapabilityCoverageEvaluator(store)
        cov_records = evaluator.evaluate_all()
        cov_summary = evaluator.compute_summary(cov_records)
        actual_verdict = cov_summary.get("overall_verdict", "COVERAGE_BLOCKED")

        # Run overclaim detector
        detector = OverclaimDetector(store)
        overclaim_report = detector.detect_all()
        actual_overclaim = overclaim_report.error_count > 0

        # Run staleness engine
        staleness_engine = StalenessInvalidationEngine(store)
        stale_report = staleness_engine.run()
        actual_stale = bool(stale_report.stale_claim_ids)

        # Compare against expected
        exp_verdict = expected.get("expected_overall_verdict", "COVERAGE_CLEAN")
        exp_overclaim = expected.get("expected_overclaim", False)
        exp_stale = expected.get("expected_stale", False)

        # Map expected values
        verdict_ok = actual_verdict == exp_verdict
        overclaim_ok = actual_overclaim == exp_overclaim
        stale_ok = actual_stale == exp_stale

        passed = verdict_ok and overclaim_ok and stale_ok and val_result.is_valid

        notes = []
        if not verdict_ok:
            notes.append(f"Coverage verdict mismatch: got {actual_verdict!r}, expected {exp_verdict!r}")
        if not overclaim_ok:
            notes.append(f"Overclaim mismatch: got {actual_overclaim}, expected {exp_overclaim}")
        if not stale_ok:
            notes.append(f"Staleness mismatch: got {actual_stale}, expected {exp_stale}")
        if not val_result.is_valid:
            notes.append(f"Validator errors: {len(val_result.errors)}")

        return FixtureResult(
            fixture_name=fixture_name,
            graph_hash=graph_hash,
            coverage_verdict=actual_verdict,
            overclaim_found=actual_overclaim,
            stale_found=actual_stale,
            validator_errors=len(val_result.errors),
            expected_coverage_verdict=exp_verdict,
            expected_overclaim=exp_overclaim,
            expected_stale=exp_stale,
            passed=passed,
            notes=notes,
        )
    except Exception as e:
        return FixtureResult(
            fixture_name=fixture_name,
            graph_hash="",
            coverage_verdict="ERROR",
            overclaim_found=False,
            stale_found=False,
            validator_errors=0,
            expected_coverage_verdict="",
            expected_overclaim=False,
            expected_stale=False,
            passed=False,
            error=str(e),
        )


def _run_determinism_test(fixture_dir: Path, fixture_name: str) -> DeterminismResult:
    """Run the same fixture 3 times and verify graph hash is identical."""
    hashes = []
    for _ in range(3):
        try:
            store = _load_store_from_fixture(fixture_dir)
            hashes.append(store.compute_graph_hash())
        except Exception as e:
            hashes.append(f"ERROR:{e}")

    deterministic = len(set(hashes)) == 1 and "ERROR" not in hashes[0]
    notes = "All 3 runs produced identical hash." if deterministic else f"Hashes differ: {hashes}"
    return DeterminismResult(
        fixture_name=fixture_name,
        hashes=hashes,
        deterministic=deterministic,
        notes=notes,
    )


class GoldenReplaySuite:
    """
    Runs all 6 golden replay fixture packs and determinism test.
    Fixtures are loaded from the `requirements-authority/fixtures/` directory.
    """

    def __init__(self, fixtures_root: Path):
        self.fixtures_root = fixtures_root

    def run_all(self) -> ReplaySuiteResult:
        result = ReplaySuiteResult(total_fixtures=len(FIXTURE_PACKS))

        for fixture_name in FIXTURE_PACKS:
            fixture_dir = self.fixtures_root / fixture_name
            if not fixture_dir.exists():
                result.fixture_results.append(FixtureResult(
                    fixture_name=fixture_name,
                    graph_hash="",
                    coverage_verdict="MISSING",
                    overclaim_found=False,
                    stale_found=False,
                    validator_errors=0,
                    expected_coverage_verdict="",
                    expected_overclaim=False,
                    expected_stale=False,
                    passed=False,
                    error=f"Fixture directory not found: {fixture_dir}",
                ))
                continue

            fixture_result = _run_single_fixture(fixture_dir, fixture_name)
            result.fixture_results.append(fixture_result)

            determ_result = _run_determinism_test(fixture_dir, fixture_name)
            result.determinism_results.append(determ_result)

        result.passed_fixtures = sum(1 for r in result.fixture_results if r.passed)
        result.determinism_pass = all(d.deterministic for d in result.determinism_results)
        result.overall_pass = (
            result.passed_fixtures == result.total_fixtures and result.determinism_pass
        )

        return result

    def run_and_save(self, output_dir: Path) -> ReplaySuiteResult:
        """Run all fixtures and save results JSON."""
        result = self.run_all()
        output_dir.mkdir(parents=True, exist_ok=True)
        p = output_dir / "replay-suite-results.json"
        p.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return result


def run_replay_fixtures(fixtures_root: Path, output_dir: Optional[Path] = None) -> ReplaySuiteResult:
    """Convenience function: run all 6 golden replay fixture packs."""
    suite = GoldenReplaySuite(fixtures_root)
    if output_dir:
        return suite.run_and_save(output_dir)
    return suite.run_all()


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent.parent
    fixtures_root = repo_root / "requirements-authority" / "fixtures"
    output_dir = repo_root / "reports" / "requirement-capability-authority-layer-mwp"

    result = run_replay_fixtures(fixtures_root, output_dir)
    print(f"Replay suite: {result.passed_fixtures}/{result.total_fixtures} fixtures PASS")
    print(f"Determinism: {'PASS' if result.determinism_pass else 'FAIL'}")
    print(f"Overall: {'PASS' if result.overall_pass else 'FAIL'}")
    sys.exit(0 if result.overall_pass else 1)
