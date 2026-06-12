"""
public_spec_readiness_scorer.py -- Lane D Deliverable (FORMAT-FACTORY-R10)

Public-Spec Readiness Scorer for the format-factory governed planning layer.

PURPOSE:
  Score format candidates on their readiness for format acquisition, based
  on publicly available information. All scores are deterministic; no internet
  access, no fetching, no external credentials.

SCORING DIMENSIONS (8 criteria, 0-10 each):
  1. spec_availability        -- Is a public specification available?
  2. spec_completeness        -- How complete/authoritative is the spec?
  3. complexity               -- Inverse of format complexity (simpler = higher score)
  4. sample_availability      -- Are open-license sample files available?
  5. legal_clarity            -- Is provenance/legal use clear?
  6. parser_feasibility       -- Can we build a parser from available info?
  7. oracle_feasibility       -- Can we build a test oracle (round-trip)?
  8. requirements_gen_readiness -- Can requirements be generated deterministically?

COMPOSITE SCORE:
  Weighted average of the 8 dimensions.
  0-3:   NOT_READY (spec/legal issues; requires human investigation)
  4-5:   NEEDS_INVESTIGATION (partial info; advisory review before proceeding)
  6-7:   CANDIDATE_READY (sufficient info to begin support matrix audit)
  8-10:  ACQUISITION_READY (strong candidate for immediate acquisition planning)

NOT ALLOWED:
  - Internet access
  - Claiming unsupported_by_aspose=true without audit
  - Advancing a format without human review at each gate

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Readiness tier constants
READINESS_NOT_READY = "NOT_READY"
READINESS_NEEDS_INVESTIGATION = "NEEDS_INVESTIGATION"
READINESS_CANDIDATE_READY = "CANDIDATE_READY"
READINESS_ACQUISITION_READY = "ACQUISITION_READY"

# Readiness thresholds
THRESHOLD_NOT_READY = 3.0
THRESHOLD_NEEDS_INVESTIGATION = 5.0
THRESHOLD_CANDIDATE_READY = 7.0

# Score dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
    "spec_availability": 0.20,
    "spec_completeness": 0.15,
    "complexity": 0.10,
    "sample_availability": 0.10,
    "legal_clarity": 0.15,
    "parser_feasibility": 0.15,
    "oracle_feasibility": 0.05,
    "requirements_gen_readiness": 0.10,
}

# Governance flags
_GOVERNANCE_FLAGS = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "no_internet_access": True,
    "scores_are_estimates_not_decisions": True,
}

# Spec type → spec_availability + spec_completeness scores
SPEC_TYPE_SCORES = {
    "full_public": {"spec_availability": 10, "spec_completeness": 9},
    "partial_public": {"spec_availability": 7, "spec_completeness": 5},
    "community_documented": {"spec_availability": 6, "spec_completeness": 4},
    "reverse_engineering": {"spec_availability": 4, "spec_completeness": 3},
    "none": {"spec_availability": 0, "spec_completeness": 0},
    "unknown": {"spec_availability": 1, "spec_completeness": 1},
}

# Category complexity profiles (inverse — simpler = higher score)
CATEGORY_COMPLEXITY_SCORES = {
    "archive": 7,        # Typically simpler structure
    "image": 6,          # Variable complexity
    "word_processing": 5,
    "spreadsheet": 5,
    "presentation": 4,
    "page_layout": 3,    # Complex page model
    "cad_3d": 2,         # Very complex
    "gis": 4,
    "email_pim": 5,
    "project_management": 4,
    "game_voxel": 6,
    "ebook": 6,
    "audio_video": 3,
}


def _stable_hash(data: Any) -> str:
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _classify_readiness(score: float) -> str:
    if score <= THRESHOLD_NOT_READY:
        return READINESS_NOT_READY
    elif score <= THRESHOLD_NEEDS_INVESTIGATION:
        return READINESS_NEEDS_INVESTIGATION
    elif score <= THRESHOLD_CANDIDATE_READY:
        return READINESS_CANDIDATE_READY
    else:
        return READINESS_ACQUISITION_READY


def score_format(
    fmt: str,
    spec_type: str,
    category: str,
    sample_files_known: bool = False,
    legal_use_clear: bool = False,
    open_source_reference: bool = False,
    existing_parsers_known: bool = False,
    binary_format: bool = False,
) -> dict:
    """
    Score a format candidate for public-spec readiness.

    Parameters
    ----------
    fmt : str
        Format ID
    spec_type : str
        Spec availability type from candidate_format_backlog constants
    category : str
        Format category
    sample_files_known : bool
        Whether open-license sample files are known to exist
    legal_use_clear : bool
        Whether legal/provenance use is clearly established
    open_source_reference : bool
        Whether an open-source reference implementation exists
    existing_parsers_known : bool
        Whether existing parsers are known (aids oracle feasibility)
    binary_format : bool
        Whether format is binary (increases complexity, decreases parser feasibility)

    Returns
    -------
    dict — scored readiness report
    """
    # Spec scores
    spec_scores = SPEC_TYPE_SCORES.get(spec_type, SPEC_TYPE_SCORES["unknown"])
    spec_availability = spec_scores["spec_availability"]
    spec_completeness = spec_scores["spec_completeness"]

    # Complexity (inverse: simpler is better)
    base_complexity = CATEGORY_COMPLEXITY_SCORES.get(category, 5)
    complexity = max(0, base_complexity - (3 if binary_format else 0))

    # Sample availability
    sample_score = 8 if sample_files_known else (4 if spec_type in ("full_public", "partial_public") else 2)

    # Legal clarity
    if legal_use_clear:
        legal_score = 9
    elif spec_type == "full_public":
        legal_score = 7
    elif open_source_reference:
        legal_score = 6
    else:
        legal_score = 3

    # Parser feasibility
    parser_base = spec_scores["spec_completeness"]
    if open_source_reference:
        parser_base = min(10, parser_base + 2)
    if binary_format:
        parser_base = max(0, parser_base - 2)
    parser_feasibility = parser_base

    # Oracle feasibility
    if existing_parsers_known or open_source_reference:
        oracle_score = 7
    elif spec_type in ("full_public",):
        oracle_score = 5
    else:
        oracle_score = 2

    # Requirements generation readiness
    if spec_type == "full_public" and legal_use_clear:
        req_gen = 9
    elif spec_type in ("full_public", "partial_public"):
        req_gen = 6
    elif spec_type == "community_documented":
        req_gen = 4
    else:
        req_gen = 1

    # Compute weighted composite
    raw_scores = {
        "spec_availability": spec_availability,
        "spec_completeness": spec_completeness,
        "complexity": complexity,
        "sample_availability": sample_score,
        "legal_clarity": legal_score,
        "parser_feasibility": parser_feasibility,
        "oracle_feasibility": oracle_score,
        "requirements_gen_readiness": req_gen,
    }

    composite = sum(
        raw_scores[dim] * weight
        for dim, weight in DIMENSION_WEIGHTS.items()
    )
    composite = round(composite, 2)
    readiness_tier = _classify_readiness(composite)

    score_id = _stable_hash({
        "fmt": fmt,
        "spec_type": spec_type,
        "category": category,
        "binary_format": binary_format,
        "sample_files_known": sample_files_known,
        "legal_use_clear": legal_use_clear,
        "open_source_reference": open_source_reference,
        "existing_parsers_known": existing_parsers_known,
    })

    # Actionable recommendations
    recommendations = _generate_recommendations(
        fmt, spec_type, readiness_tier, raw_scores, legal_use_clear, sample_files_known
    )

    return {
        "format_id": fmt,
        "score_id": score_id,
        "composite_score": composite,
        "readiness_tier": readiness_tier,
        "dimension_scores": raw_scores,
        "dimension_weights": dict(DIMENSION_WEIGHTS),
        "spec_type": spec_type,
        "category": category,
        "binary_format": binary_format,
        "sample_files_known": sample_files_known,
        "legal_use_clear": legal_use_clear,
        "open_source_reference": open_source_reference,
        "existing_parsers_known": existing_parsers_known,
        "recommendations": recommendations,
        "score_note": (
            f"Score for {fmt.upper()}: {composite}/10 ({readiness_tier}). "
            f"This is an ESTIMATE based on publicly available information. "
            f"Scores do not authorize acquisition — human review required."
        ),
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
    }


def _generate_recommendations(
    fmt: str,
    spec_type: str,
    readiness_tier: str,
    scores: dict,
    legal_use_clear: bool,
    sample_files_known: bool,
) -> list[str]:
    recs = []
    if scores["spec_availability"] < 5:
        recs.append(f"[REC] Locate or document public specification for {fmt.upper()} before proceeding")
    if scores["legal_clarity"] < 5:
        recs.append(f"[REC] Obtain legal/provenance clearance for {fmt.upper()} before acquisition")
    if not sample_files_known:
        recs.append(f"[REC] Identify open-license sample files for {fmt.upper()}")
    if scores["requirements_gen_readiness"] < 5:
        recs.append("[REC] Requirements generation requires spec normalization first")
    if readiness_tier == READINESS_NOT_READY:
        recs.append(f"[REC] {fmt.upper()} is NOT_READY — do not proceed without human investigation")
    elif readiness_tier == READINESS_NEEDS_INVESTIGATION:
        recs.append(f"[REC] {fmt.upper()} requires investigation sprint before acquisition planning")
    elif readiness_tier in (READINESS_CANDIDATE_READY, READINESS_ACQUISITION_READY):
        recs.append(f"[REC] Begin with support-matrix audit for {fmt.upper()}")
    return recs


def score_multiple_formats(format_specs: list[dict]) -> dict:
    """
    Score multiple format candidates.

    Parameters
    ----------
    format_specs : list[dict]
        List of format spec dicts with 'fmt', 'spec_type', 'category', etc.

    Returns
    -------
    dict — aggregate scoring results, ranked by composite_score
    """
    scores = []
    for spec in format_specs:
        fmt = spec["fmt"]
        result = score_format(
            fmt=fmt,
            spec_type=spec.get("spec_type", "unknown"),
            category=spec.get("category", "word_processing"),
            sample_files_known=spec.get("sample_files_known", False),
            legal_use_clear=spec.get("legal_use_clear", False),
            open_source_reference=spec.get("open_source_reference", False),
            existing_parsers_known=spec.get("existing_parsers_known", False),
            binary_format=spec.get("binary_format", False),
        )
        scores.append(result)

    scores.sort(key=lambda s: s["composite_score"], reverse=True)

    tier_distribution: dict[str, int] = {}
    for s in scores:
        t = s["readiness_tier"]
        tier_distribution[t] = tier_distribution.get(t, 0) + 1

    return {
        "scored_formats": [s["format_id"] for s in scores],
        "scores": {s["format_id"]: s for s in scores},
        "ranked": [{"format_id": s["format_id"], "score": s["composite_score"],
                    "tier": s["readiness_tier"]} for s in scores],
        "tier_distribution": tier_distribution,
        "top_candidate": scores[0]["format_id"] if scores else None,
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
    }


# Built-in scoring for standard candidates
STANDARD_CANDIDATE_SPECS = [
    {"fmt": "hwpx", "spec_type": "partial_public", "category": "word_processing",
     "sample_files_known": True, "legal_use_clear": False, "binary_format": False},
    {"fmt": "hwp", "spec_type": "reverse_engineering", "category": "word_processing",
     "sample_files_known": True, "legal_use_clear": False, "binary_format": True},
    {"fmt": "hwt", "spec_type": "partial_public", "category": "word_processing",
     "sample_files_known": False, "legal_use_clear": False, "binary_format": False},
    {"fmt": "alz", "spec_type": "reverse_engineering", "category": "archive",
     "sample_files_known": True, "legal_use_clear": False, "binary_format": True},
    {"fmt": "egg", "spec_type": "partial_public", "category": "archive",
     "sample_files_known": True, "legal_use_clear": False, "binary_format": False},
    {"fmt": "gnumeric", "spec_type": "full_public", "category": "spreadsheet",
     "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True},
    {"fmt": "abw", "spec_type": "full_public", "category": "word_processing",
     "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True},
    {"fmt": "sla", "spec_type": "full_public", "category": "page_layout",
     "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True},
    {"fmt": "qoi", "spec_type": "full_public", "category": "image",
     "sample_files_known": True, "legal_use_clear": True},
    {"fmt": "zst", "spec_type": "full_public", "category": "archive",
     "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True},
]


def score_standard_candidates() -> dict:
    """Score all standard candidate formats."""
    return score_multiple_formats(STANDARD_CANDIDATE_SPECS)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Public-spec readiness scorer")
    parser.add_argument("format", nargs="?", default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.format == "all":
        result = score_standard_candidates()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Public-Spec Readiness Scores ===")
            for r in result["ranked"]:
                print(f"  {r['format_id']:12s} {r['score']:5.2f}  {r['tier']}")
    else:
        spec = next((s for s in STANDARD_CANDIDATE_SPECS if s["fmt"] == args.format), None)
        if not spec:
            spec = {"fmt": args.format, "spec_type": "unknown", "category": "word_processing"}
        result = score_format(**spec)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== Readiness Score: {args.format.upper()} ===")
            print(f"  Score:  {result['composite_score']}/10")
            print(f"  Tier:   {result['readiness_tier']}")
            for dim, val in result["dimension_scores"].items():
                print(f"  {dim:30s}: {val}")
            for rec in result["recommendations"]:
                print(f"  {rec}")


if __name__ == "__main__":
    main()
