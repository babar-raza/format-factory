"""
authority_gate_validation.py
Sprint: SPEC-AUTHORITY-LAYER-FAST-OPS-INTEGRATION-AND-AUTHORITY-CONVEYOR-001

Reusable authority gate validation tool.

Input:  format_id (str)
Output: {
    authority_level: str (P0-P6),
    authority_level_int: int (0-6),
    blockers: list[str],
    next_action: str,
    debt_entry: dict | None,
    readiness_allowed: bool,
    product_expansion_allowed: bool,
    spec_fact_refs_required: bool,
    exception_allowed: str | None,
}

Authority Level Definitions:
  P0: No spec available or accessible
  P1: Schema/metadata only (informal or proprietary)
  P2: Spec accessible/cached, no facts extracted
  P3: Candidate facts extracted (needs_review)
  P4: Verified facts (deterministic spec citation)
  P5: Fact cited in code/tests
  P6: Proof graph complete (spec→fact→code→test→evidence)

Usage:
  python authority_gate_validation.py --format-id fods
  python authority_gate_validation.py --format-id zst --json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Minimum P-level for product expansion (PRODUCT_SOURCE/TEST/REQUIREMENT items)
MIN_PRODUCT_EXPANSION_LEVEL = 4  # P4+ for autonomous product work

# P-levels that allow READINESS/RELEASE_GATE items
MIN_READINESS_LEVEL = 4  # P4+ required; lower levels need fallback_authority_approved

# Formats with no_public_spec_available (cannot reach P4+ through normal path)
NO_PUBLIC_SPEC_FORMATS = frozenset({
    "sylk",
    "dif",
    "abw",  # AWM/AWML not a formal published standard
    "tsv",  # no formal RFC
    "txt",  # no format-specific spec
    "markdown",  # community standard only
})

# Schema-only formats (P1 by nature)
SCHEMA_ONLY_FORMATS = frozenset({
    "gnumeric",  # gnumeric.xsd is the only authority
})


def _repo_root() -> Path:
    """Find the git repository root."""
    current = Path(__file__).resolve()
    for p in [current, *current.parents]:
        if (p / ".git").exists():
            return p
    return Path(__file__).resolve().parent.parent.parent


def _load_yaml_safe(path: Path) -> dict:
    """Load YAML file safely, returning empty dict on failure."""
    if not path.exists():
        return {}
    try:
        if yaml is not None:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        # Fallback: very basic YAML parsing not available — return empty
        return {}
    except Exception:
        return {}


def _load_format_spec_state(format_id: str, repo_root: Path) -> dict:
    """Load spec state from spec-cache for a given format."""
    spec_dir = repo_root / ".local" / "spec-cache" / format_id.lower()
    if not spec_dir.exists():
        return {"spec_cached": False, "spec_index": None}

    # Find spec-index.yaml
    spec_index_paths = list(spec_dir.rglob("spec-index.yaml"))
    spec_index = {}
    if spec_index_paths:
        spec_index = _load_yaml_safe(spec_index_paths[0])

    # Find verified-facts-review.yaml files
    facts_files = list(spec_dir.rglob("verified-facts-review.yaml"))
    facts_data: list[dict] = []
    for ff in facts_files:
        data = _load_yaml_safe(ff)
        facts_data.extend(data.get("facts", []))

    verified_facts = [f for f in facts_data if f.get("provenance", {}).get("verification_status") == "verified"]
    candidate_facts = [f for f in facts_data if f.get("provenance", {}).get("verification_status") == "needs_review"]

    return {
        "spec_cached": True,
        "spec_index": spec_index,
        "facts_total": len(facts_data),
        "facts_verified": len(verified_facts),
        "facts_candidate": len(candidate_facts),
        "verified_fact_ids": [f.get("claim_id") for f in verified_facts],
        "candidate_fact_ids": [f.get("claim_id") for f in candidate_facts],
    }


def _check_code_citations(format_id: str, repo_root: Path) -> dict:
    """Check if any source files cite a verified fact ID for this format."""
    src_dir = repo_root / "src" / "python" / format_id.lower()
    if not src_dir.exists():
        return {"has_code_citations": False, "cited_files": []}

    cited_files = []
    pattern = f"FACT-{format_id.upper()}-"
    for py_file in src_dir.rglob("*.py"):
        try:
            if pattern in py_file.read_text(encoding="utf-8"):
                cited_files.append(str(py_file.relative_to(repo_root)))
        except Exception:
            pass
    return {"has_code_citations": bool(cited_files), "cited_files": cited_files}


def _check_test_citations(format_id: str, repo_root: Path) -> dict:
    """Check if any test files cite a verified fact ID for this format."""
    test_dir = repo_root / "tests" / "python" / format_id.lower()
    if not test_dir.exists():
        return {"has_test_citations": False, "cited_test_files": []}

    cited_files = []
    pattern = f"FACT-{format_id.upper()}-"
    for py_file in test_dir.rglob("*.py"):
        try:
            if pattern in py_file.read_text(encoding="utf-8"):
                cited_files.append(str(py_file.relative_to(repo_root)))
        except Exception:
            pass
    return {"has_test_citations": bool(cited_files), "cited_test_files": cited_files}


def _check_proof_graph(format_id: str, repo_root: Path) -> dict:
    """Check if a proof graph exists for this format."""
    proof_graph_paths = []
    # Check standard locations
    for d in ["reports/authority-conveyor-20260608", "reports/supervisor", ".local/spec-cache"]:
        for f in (repo_root / d).rglob(f"*{format_id.lower()}*proof*graph*") if (repo_root / d).exists() else []:
            proof_graph_paths.append(str(f))
    return {
        "has_proof_graph": bool(proof_graph_paths),
        "proof_graph_paths": proof_graph_paths,
    }


def validate_format_authority(format_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """
    Validate authority gate for a given format.

    Args:
        format_id: The format identifier (e.g., 'fods', 'zst', 'gnumeric')
        repo_root: Path to git repo root (auto-detected if None)

    Returns:
        dict with authority_level, blockers, next_action, debt_entry, etc.
    """
    if repo_root is None:
        repo_root = _repo_root()

    fmt = format_id.lower()

    # Load spec state
    spec_state = _load_format_spec_state(fmt, repo_root)
    code_state = _check_code_citations(fmt, repo_root)
    test_state = _check_test_citations(fmt, repo_root)
    proof_state = _check_proof_graph(fmt, repo_root)

    spec_cached = spec_state.get("spec_cached", False)
    facts_verified = spec_state.get("facts_verified", 0)
    facts_candidate = spec_state.get("facts_candidate", 0)
    has_code_citations = code_state.get("has_code_citations", False)
    has_test_citations = test_state.get("has_test_citations", False)
    has_proof_graph = proof_state.get("has_proof_graph", False)

    # Determine authority level
    blockers: list[str] = []
    authority_level_int = 0

    # Schema-only and no-public-spec formats are P1 regardless of spec_cached
    if fmt in NO_PUBLIC_SPEC_FORMATS:
        authority_level_int = 1  # P1: no formal spec
        blockers.append(f"no_public_spec_available: {fmt} has no accessible formal spec")
    elif fmt in SCHEMA_ONLY_FORMATS:
        authority_level_int = 1  # P1: schema only (debt-only classification)
        blockers.append(f"schema_only: {fmt} authority is schema metadata (debt-only classification)")
    elif not spec_cached:
        authority_level_int = 0  # P0: no spec at all
        blockers.append(f"no_spec: no spec-cache entry found for {fmt}")
    else:
        # Spec cached
        if facts_verified == 0 and facts_candidate == 0:
            authority_level_int = 2  # P2: spec cached but no facts
            blockers.append(f"no_facts: spec cached but no facts extracted for {fmt}")
        elif facts_verified == 0 and facts_candidate > 0:
            authority_level_int = 3  # P3: candidate facts only
            blockers.append(f"unverified_facts: {facts_candidate} candidate facts — run verification")
        elif facts_verified > 0 and not has_code_citations:
            authority_level_int = 4  # P4: verified facts but no code citations
            blockers.append(f"no_code_citations: {facts_verified} verified facts but none cited in code")
        elif facts_verified > 0 and has_code_citations and not has_test_citations:
            authority_level_int = 5  # P5: cited in code but not in tests
            blockers.append(f"no_test_citations: facts cited in code but not in test files")
        elif facts_verified > 0 and has_code_citations and has_test_citations and not has_proof_graph:
            authority_level_int = 5  # P5: all citations present but no proof graph
            blockers.append(f"no_proof_graph: citations complete but proof graph YAML not found")
        elif facts_verified > 0 and has_code_citations and has_test_citations and has_proof_graph:
            authority_level_int = 6  # P6: complete
            blockers = []

    authority_level = f"P{authority_level_int}"

    # Determine readiness and expansion permissions
    readiness_allowed = authority_level_int >= MIN_READINESS_LEVEL
    product_expansion_allowed = authority_level_int >= MIN_PRODUCT_EXPANSION_LEVEL

    # Exception classification that may apply
    exception_allowed: str | None = None
    if fmt in NO_PUBLIC_SPEC_FORMATS:
        exception_allowed = "no_public_spec_available"
    elif fmt in SCHEMA_ONLY_FORMATS:
        exception_allowed = "schema_authority_available"
    elif authority_level_int < 4:
        exception_allowed = "legacy_backfill"

    # Next action
    next_action = _determine_next_action(fmt, authority_level_int, spec_state, blockers)

    # Debt entry (if there are blockers)
    debt_entry: dict | None = None
    if blockers:
        debt_entry = {
            "format_id": fmt,
            "authority_level": authority_level,
            "debt_class": "AUTHORITY_GATE_DEBT",
            "blockers": blockers,
            "resolution": next_action,
        }

    return {
        "format_id": fmt,
        "authority_level": authority_level,
        "authority_level_int": authority_level_int,
        "blockers": blockers,
        "next_action": next_action,
        "debt_entry": debt_entry,
        "readiness_allowed": readiness_allowed,
        "product_expansion_allowed": product_expansion_allowed,
        "spec_fact_refs_required": authority_level_int < MIN_READINESS_LEVEL,
        "exception_allowed": exception_allowed,
        "spec_state_summary": {
            "spec_cached": spec_cached,
            "facts_verified": facts_verified,
            "facts_candidate": facts_candidate,
            "verified_fact_ids": spec_state.get("verified_fact_ids", []),
        },
        "code_state_summary": {
            "has_code_citations": has_code_citations,
            "cited_files": code_state.get("cited_files", []),
        },
        "test_state_summary": {
            "has_test_citations": has_test_citations,
            "cited_test_files": test_state.get("cited_test_files", []),
        },
        "proof_graph_summary": {
            "has_proof_graph": has_proof_graph,
            "paths": proof_state.get("proof_graph_paths", []),
        },
    }


def _determine_next_action(
    format_id: str,
    level: int,
    spec_state: dict,
    blockers: list[str],
) -> str:
    if format_id in NO_PUBLIC_SPEC_FORMATS:
        return (
            f"Document no_public_spec_available exception for {format_id}. "
            "Use legacy_backfill or fallback_authority_approved for existing product work."
        )
    if format_id in SCHEMA_ONLY_FORMATS:
        return (
            f"Locate formal spec documentation for {format_id} (schema only at present). "
            "Cache spec and extract verified facts. schema_authority_available is debt-only — "
            "cannot claim READINESS without verified spec_fact_refs."
        )
    if level == 0:
        return f"Find and cache spec source for {format_id} under .local/spec-cache/{format_id}/"
    if level == 1:
        return f"Locate formal spec for {format_id}. If none exists, document no_public_spec_available."
    if level == 2:
        return f"Extract candidate facts from cached {format_id} spec. Create workbench/verified-facts-review.yaml."
    if level == 3:
        n = spec_state.get("facts_candidate", 0)
        return (
            f"Verify {n} candidate facts for {format_id} via deterministic spec text search. "
            "Set verification_status=verified and validated_by=deterministic_spec_text_search."
        )
    if level == 4:
        ids = spec_state.get("verified_fact_ids", [])
        return (
            f"Cite verified fact(s) {ids} in src/python/{format_id}/ source code (inline comment). "
            "Add test that references fact ID in docstring."
        )
    if level == 5:
        return (
            f"Build proof graph YAML: spec_source→fact→code→test→evidence. "
            "Store in reports/authority-conveyor-*/. Verify all edges are present."
        )
    return "Authority P6 achieved. Maintain by keeping citations and tests up to date."


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate authority gate for a format.")
    parser.add_argument("--format-id", "-f", required=True, help="Format ID (e.g., fods, zst)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = validate_format_authority(args.format_id)

    if args.json or not sys.stdout.isatty():
        print(json.dumps(result, indent=2))
    else:
        print(f"Format: {result['format_id']}")
        print(f"Authority Level: {result['authority_level']}")
        print(f"Readiness Allowed: {result['readiness_allowed']}")
        print(f"Product Expansion Allowed: {result['product_expansion_allowed']}")
        print(f"Exception Allowed: {result['exception_allowed'] or 'none'}")
        print(f"Blockers: {result['blockers']}")
        print(f"Next Action: {result['next_action']}")
        if result.get("spec_state_summary", {}).get("verified_fact_ids"):
            print(f"Verified Facts: {result['spec_state_summary']['verified_fact_ids']}")

    return 0 if not result["blockers"] else 1


if __name__ == "__main__":
    sys.exit(main())
