"""
authority_conveyor.py
Sprint: SPEC-AUTHORITY-LAYER-CONVEYOR-ACCELERATION-AND-OPS-CLEANUP-001

Repeatable authority conveyor tool.

Given a format ID and target authority level, this tool:
1. Loads current authority state for the format.
2. Determines what is needed to reach the target level.
3. Returns a structured action plan with facts, requirements, tests, and matrix update.

This is a READ-ONLY planning tool. It does NOT modify spec-cache, source code,
or tests. It produces a work plan that a sprint can execute.

Authority Level Definitions:
  P0: No spec available
  P1: Schema/metadata only (informal or proprietary spec)
  P2: Spec cached, no facts extracted
  P3: Candidate facts extracted (needs_review)
  P4: Verified facts (deterministic spec citation)
  P5: Verified facts cited in source code AND tests
  P6: Proof graph complete (spec→fact→code→test→evidence)

Usage:
  python authority_conveyor.py --format-id zst --target-level 5
  python authority_conveyor.py --format-id fods --target-level 6 --json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ImportError:
    _yaml = None
    _YAML_AVAILABLE = False


def _repo_root() -> Path:
    """Find the git repository root."""
    current = Path(__file__).resolve()
    for p in [current, *current.parents]:
        if (p / ".git").exists():
            return p
    return Path(__file__).resolve().parent.parent.parent


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        if _YAML_AVAILABLE:
            return _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return {}
    except Exception:
        return {}


def _load_authority_gate(format_id: str, repo_root: Path) -> dict:
    """Load current authority level from authority_gate_validation."""
    try:
        import importlib.util
        agv_path = repo_root / "tools" / "supervisor" / "authority_gate_validation.py"
        spec = importlib.util.spec_from_file_location("authority_gate_validation", agv_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.validate_format_authority(format_id, repo_root=repo_root)
    except Exception as e:
        return {"error": str(e), "authority_level_int": -1, "authority_level": "UNKNOWN"}


def _load_facts(format_id: str, repo_root: Path) -> list[dict]:
    """Load all facts for a format from spec-cache."""
    spec_dir = repo_root / ".local" / "spec-cache" / format_id.lower()
    if not spec_dir.exists():
        return []
    facts = []
    for ff in spec_dir.rglob("verified-facts-review.yaml"):
        data = _load_yaml(ff)
        facts.extend(data.get("facts", []))
    return facts


def _find_code_citations(format_id: str, repo_root: Path) -> list[str]:
    """Find source files that cite FACT-{FORMAT}-NNN."""
    src_dir = repo_root / "src" / "python" / format_id.lower()
    if not src_dir.exists():
        return []
    pattern = f"FACT-{format_id.upper()}-"
    cited = []
    for py_file in src_dir.rglob("*.py"):
        try:
            if pattern in py_file.read_text(encoding="utf-8"):
                cited.append(str(py_file.relative_to(repo_root)))
        except Exception:
            pass
    return cited


def _find_test_citations(format_id: str, repo_root: Path) -> list[str]:
    """Find test files that cite FACT-{FORMAT}-NNN."""
    test_dir = repo_root / "tests" / "python" / format_id.lower()
    if not test_dir.exists():
        return []
    pattern = f"FACT-{format_id.upper()}-"
    cited = []
    for py_file in test_dir.rglob("*.py"):
        try:
            if pattern in py_file.read_text(encoding="utf-8"):
                cited.append(str(py_file.relative_to(repo_root)))
        except Exception:
            pass
    return cited


def _find_proof_graphs(format_id: str, repo_root: Path) -> list[str]:
    """Find proof graph files for a format."""
    graphs = []
    for search_dir in [repo_root / "reports", repo_root / ".local" / "spec-cache"]:
        if not search_dir.exists():
            continue
        for f in search_dir.rglob(f"*{format_id.lower()}*proof*graph*"):
            graphs.append(str(f.relative_to(repo_root)))
    return graphs


def _determine_gap_to_target(
    current_level: int,
    target_level: int,
    facts: list[dict],
    code_citations: list[str],
    test_citations: list[str],
    proof_graphs: list[str],
    format_id: str,
) -> list[dict]:
    """Return ordered list of steps needed to go from current to target level."""
    steps = []
    fmt = format_id.lower()

    verified_facts = [f for f in facts if f.get("provenance", {}).get("verification_status") == "verified"]
    candidate_facts = [f for f in facts if f.get("provenance", {}).get("verification_status") == "needs_review"]
    verified_ids = [f.get("claim_id") for f in verified_facts]

    if current_level < 2 <= target_level:
        steps.append({
            "step": 1,
            "from_level": "P0/P1",
            "to_level": "P2",
            "action": f"Cache spec source for {fmt} under .local/spec-cache/{fmt}/",
            "type": "SPEC_CACHE",
            "blocked_by": f"Requires: locate and download spec document for {fmt}",
            "outputs": [f".local/spec-cache/{fmt}/v1/spec-index.yaml"],
        })

    if current_level < 3 <= target_level:
        steps.append({
            "step": 2,
            "from_level": "P2",
            "to_level": "P3",
            "action": f"Extract candidate facts from {fmt} spec. Create workbench/verified-facts-review.yaml",
            "type": "FACT_EXTRACTION",
            "blocked_by": "Requires: P2 (spec cached)",
            "outputs": [f".local/spec-cache/{fmt}/v1/workbench/verified-facts-review.yaml"],
        })

    if current_level < 4 <= target_level:
        unchecked = [f.get("claim_id") for f in candidate_facts]
        steps.append({
            "step": 3,
            "from_level": "P3",
            "to_level": "P4",
            "action": (
                f"Verify {len(candidate_facts)} candidate fact(s) via deterministic spec text search. "
                f"Set verification_status=verified, validated_by=deterministic_spec_text_search."
            ),
            "type": "FACT_VERIFICATION",
            "blocked_by": "Requires: P3 (candidate facts extracted)",
            "candidate_fact_ids": unchecked,
            "outputs": [f".local/spec-cache/{fmt}/v1/workbench/verified-facts-review.yaml (updated)"],
        })

    if current_level < 5 <= target_level:
        steps.append({
            "step": 4,
            "from_level": "P4",
            "to_level": "P5",
            "action": (
                f"Cite verified fact IDs {verified_ids} in src/python/{fmt}/ (inline comment). "
                f"Create test file that references fact IDs in docstring."
            ),
            "type": "FACT_CITATION",
            "blocked_by": "Requires: P4 (verified facts)",
            "verified_fact_ids": verified_ids,
            "code_action": f"Add '# FACT-{fmt.upper()}-NNN: ...' comment to src/python/{fmt}/*.py",
            "test_action": f"Create tests/python/{fmt}/test_rNNN_{fmt}_fact_traceability.py",
            "outputs": [
                f"src/python/{fmt}/*.py (comment added)",
                f"tests/python/{fmt}/test_rNNN_{fmt}_fact_traceability.py",
            ],
        })

    if current_level < 6 <= target_level:
        steps.append({
            "step": 5,
            "from_level": "P5",
            "to_level": "P6",
            "action": (
                f"Build proof graph YAML: spec_source -> fact -> code -> test -> evidence. "
                f"Store under reports/authority-conveyor-*/."
            ),
            "type": "PROOF_GRAPH",
            "blocked_by": "Requires: P5 (code + test citations)",
            "verified_fact_ids": verified_ids,
            "code_cited_in": code_citations,
            "test_cited_in": test_citations,
            "outputs": [
                f"reports/authority-conveyor-YYYYMMDD/{fmt}-p6-proof-graph.yaml",
                f"reports/authority-conveyor-YYYYMMDD/{fmt}-authority-ledger-entry.json",
            ],
        })

    return steps


def run_conveyor(
    format_id: str,
    target_level: int,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """
    Run the authority conveyor for a format.

    Args:
        format_id: The format identifier (e.g., 'fods', 'zst').
        target_level: Target authority level (0-6).
        repo_root: Repository root (auto-detected if None).

    Returns:
        Conveyor result dict with current state, gap analysis, action plan,
        and a summary of what is needed.
    """
    if repo_root is None:
        repo_root = _repo_root()

    fmt = format_id.lower()

    # Load current authority state
    authority = _load_authority_gate(fmt, repo_root)
    current_level = authority.get("authority_level_int", 0)

    # Load facts and citations
    facts = _load_facts(fmt, repo_root)
    code_citations = _find_code_citations(fmt, repo_root)
    test_citations = _find_test_citations(fmt, repo_root)
    proof_graphs = _find_proof_graphs(fmt, repo_root)

    verified_facts = [f for f in facts if f.get("provenance", {}).get("verification_status") == "verified"]
    candidate_facts = [f for f in facts if f.get("provenance", {}).get("verification_status") == "needs_review"]

    # Determine what needs to be done
    gap_steps = _determine_gap_to_target(
        current_level=current_level,
        target_level=target_level,
        facts=facts,
        code_citations=code_citations,
        test_citations=test_citations,
        proof_graphs=proof_graphs,
        format_id=fmt,
    )

    already_at_or_above_target = current_level >= target_level

    # Build matrix update entry
    matrix_entry = {
        "format_id": fmt,
        "current_level": f"P{current_level}",
        "target_level": f"P{target_level}",
        "gap_steps": len(gap_steps),
        "already_complete": already_at_or_above_target,
        "verified_facts_count": len(verified_facts),
        "candidate_facts_count": len(candidate_facts),
        "code_citations_count": len(code_citations),
        "test_citations_count": len(test_citations),
        "proof_graphs_found": len(proof_graphs),
    }

    return {
        "format_id": fmt,
        "current_level": f"P{current_level}",
        "current_level_int": current_level,
        "target_level": f"P{target_level}",
        "target_level_int": target_level,
        "already_at_or_above_target": already_at_or_above_target,
        "authority_blockers": authority.get("blockers", []),
        "exception_allowed": authority.get("exception_allowed"),
        "readiness_allowed": authority.get("readiness_allowed", False),
        "product_expansion_allowed": authority.get("product_expansion_allowed", False),
        "facts_summary": {
            "total": len(facts),
            "verified": len(verified_facts),
            "candidate": len(candidate_facts),
            "verified_ids": [f.get("claim_id") for f in verified_facts],
            "candidate_ids": [f.get("claim_id") for f in candidate_facts],
        },
        "citations_summary": {
            "code_cited_files": code_citations,
            "test_cited_files": test_citations,
            "proof_graph_files": proof_graphs,
        },
        "gap_steps": gap_steps,
        "gap_count": len(gap_steps),
        "matrix_update": matrix_entry,
        "next_action": authority.get("next_action", ""),
        "spec_state_summary": authority.get("spec_state_summary", {}),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run authority conveyor for a format.")
    parser.add_argument("--format-id", "-f", required=True, help="Format ID (e.g., fods, zst)")
    parser.add_argument("--target-level", "-t", type=int, default=6,
                        help="Target authority level (0-6, default 6)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = run_conveyor(args.format_id, args.target_level)

    if args.json or not sys.stdout.isatty():
        print(json.dumps(result, indent=2))
    else:
        print(f"Format:          {result['format_id']}")
        print(f"Current Level:   {result['current_level']}")
        print(f"Target Level:    {result['target_level']}")
        print(f"Already At Target: {result['already_at_or_above_target']}")
        print(f"Gap Steps:       {result['gap_count']}")
        print(f"Verified Facts:  {result['facts_summary']['verified_ids']}")
        print(f"Code Citations:  {result['citations_summary']['code_cited_files']}")
        print(f"Test Citations:  {result['citations_summary']['test_cited_files']}")
        print(f"Readiness OK:    {result['readiness_allowed']}")
        if result["gap_steps"]:
            print("\nAction Plan:")
            for step in result["gap_steps"]:
                print(f"  Step {step['step']}: {step['from_level']} -> {step['to_level']}: {step['action']}")

    return 0 if result["already_at_or_above_target"] else 1


if __name__ == "__main__":
    sys.exit(main())
