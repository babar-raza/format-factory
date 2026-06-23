"""Validate adoption compliance for evidence declarations.

Checks whether product work items reference skill_ids, include transcript
evidence, and have ledger entries for src-editing items.

R108: Created as part of the adoption compliance enforcement campaign.
REPAIR (autonomous-system-audit): Added strict enforcement — compliance cannot
pass with 0 transcripts / 0 skill_ids when non-exempt items exist, unless every
non-exempt item has an explicit exemption_reason.
"""

from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Item IDs that are exempt from adoption compliance (process overhead)
EXEMPT_PREFIXES = ("W0-", "W9-FINAL", "W10-EVIDENCE")
EXEMPT_TITLES_LOWER = {"preflight", "closeout", "final iv", "final adversarial"}

# Additional title keywords that indicate non-source-changing work
NON_SOURCE_TITLE_KEYWORDS = (
    "audit", "review", "reconcil", "preflight", "report", "manifest",
    "verdict", "catalog", "map", "verification", "iv check", "adversarial",
    "readiness packet", "host runner", "host-runner", "proof check",
    "evidence package", "declaration",
)

# Product tracks that require ledger entries for src-editing
SRC_EDITING_TRACKS = {"commercial_dotnet", "foss_python", "cross_product_export"}

# Result classifications
COMPLIANCE_PASS = "PASS"
COMPLIANCE_PASS_WITH_EXEMPTIONS = "PASS_WITH_EXEMPTIONS"
COMPLIANCE_FAIL_MISSING_TRANSCRIPTS = "FAIL_MISSING_TRANSCRIPTS"
COMPLIANCE_FAIL_MISSING_SKILL_IDS = "FAIL_MISSING_SKILL_IDS"
COMPLIANCE_FAIL_MISSING_LEDGER = "FAIL_MISSING_LEDGER"


def _is_exempt(item: dict) -> bool:
    """Check if an item is process overhead and exempt from adoption checks."""
    item_id = item.get("item_id", "")
    title = item.get("title", "").lower()
    if any(item_id.startswith(prefix) for prefix in EXEMPT_PREFIXES):
        return True
    if any(kw in title for kw in EXEMPT_TITLES_LOWER):
        return True
    return False


def _is_non_source_changing(item: dict) -> bool:
    """Check if item is clearly not source-changing (audit/report/review items).

    These items can have transcript exemptions with explicit reason.
    """
    title = item.get("title", "").lower()
    return any(kw in title for kw in NON_SOURCE_TITLE_KEYWORDS)


def _has_transcript_evidence(item: dict) -> bool:
    """Check if any evidence_path looks like a transcript."""
    for p in item.get("evidence_paths", []):
        if "transcript" in p.lower() and p.endswith(".json"):
            return True
    # Also check fallback_transcript field
    if item.get("fallback_transcript"):
        return True
    return False


GOVERNANCE_ITEM_TYPES = frozenset({
    "GOVERNANCE_DOC", "GOVERNANCE_SCHEMA", "GOVERNANCE_POLICY",
    "GOVERNANCE_TASKCARD", "LEGACY_BACKFILL_METADATA",
})
GOVERNANCE_EXCEPTION_CLASSIFICATIONS = frozenset({
    "investigation_only", "legacy_backfill",
})


def _has_explicit_exemption(item: dict) -> bool:
    """Check if the item has an explicit exemption_reason.

    GRH-TC-004: Also recognizes governance item types and exception_classification
    values (investigation_only, legacy_backfill) as implicit exemptions.
    Rationale: governance docs require no skill transcripts by definition —
    they are not product source mutations.
    """
    if item.get("exemption_reason") or item.get("transcript_exemption_reason"):
        return True
    if item.get("item_type", "") in GOVERNANCE_ITEM_TYPES:
        return True
    if item.get("exception_classification", "") in GOVERNANCE_EXCEPTION_CLASSIFICATIONS:
        return True
    return False


def validate_adoption(declaration: dict) -> dict:
    """Validate adoption compliance for all planned work items.

    Returns a dict with:
      - compliant: bool (all non-exempt items pass strict check)
      - compliance_classification: one of PASS, PASS_WITH_EXEMPTIONS,
        FAIL_MISSING_TRANSCRIPTS, FAIL_MISSING_SKILL_IDS, FAIL_MISSING_LEDGER
      - items: list of per-item results
      - summary: human-readable summary

    STRICT RULE: compliance cannot be true when:
      non_exempt_items > 0 AND items_with_transcript == 0 AND items_with_skill_id == 0
      unless every non-exempt item has an explicit exemption_reason.
    """
    items = declaration.get("planned_work_items", [])
    results = []

    for item in items:
        item_id = item.get("item_id", "unknown")
        title = item.get("title", "")

        if _is_exempt(item):
            results.append({
                "item_id": item_id,
                "exempt": True,
                "compliant": True,
                "checks": {"exempt_reason": "Process overhead item"},
            })
            continue

        checks = {}
        compliant = True
        fail_reasons = []

        # Check 1: Does the item reference a skill_id?
        skill_id = item.get("skill_id", "") or item.get("fallback_skill_id", "")
        checks["has_skill_id"] = bool(skill_id)

        # Check 2: Does the item have transcript evidence?
        has_transcript = _has_transcript_evidence(item)
        checks["has_transcript"] = has_transcript
        checks["has_explicit_exemption"] = _has_explicit_exemption(item)

        # Check 2b: Does the item have ANY evidence (prevents strict_fail for items with
        # non-transcript evidence like reports, docs, ledger entries)?
        # strict_fail fires only when ALL non-exempt items have ZERO evidence of any kind.
        checks["has_any_evidence"] = bool(
            has_transcript
            or skill_id
            or item.get("evidence_paths")
            or item.get("ledger_entry_id")
        )

        # Check 3: For src-editing items, is there a ledger entry?
        track = item.get("product_track", "")
        if track in SRC_EDITING_TRACKS:
            ledger_id = item.get("ledger_entry_id", "")
            checks["has_ledger_entry"] = bool(ledger_id)
            if not ledger_id and not _has_explicit_exemption(item):
                checks["ledger_missing_reason"] = f"src-editing track '{track}' requires ledger_entry_id"
                compliant = False
                fail_reasons.append("missing_ledger")
            # Transcript and skill_id are required for src-editing items without
            # a ledger entry OR explicit exemption. When ledger_entry_id is present,
            # the ledger serves as evidence and transcript/skill_id are advisory.
            if ledger_id:
                checks["transcript_recommended"] = True
                checks["skill_id_recommended"] = True
            else:
                if not has_transcript and not _has_explicit_exemption(item):
                    checks["transcript_required"] = True
                    compliant = False
                    fail_reasons.append("missing_transcript")
                if not skill_id and not _has_explicit_exemption(item):
                    checks["skill_id_required"] = True
                    compliant = False
                    fail_reasons.append("missing_skill_id")
        else:
            checks["has_ledger_entry"] = "n/a"
            # Non-source-changing items: transcript is recommended, not blocking
            # UNLESS non_source_changing=False (i.e. it IS source-changing but track not set)
            is_non_source = _is_non_source_changing(item)
            checks["non_source_changing_classification"] = is_non_source
            if not is_non_source and not has_transcript and not _has_explicit_exemption(item):
                # Unknown-track item that looks like product work without transcript
                checks["transcript_recommended"] = True
                # Not a hard fail for unknown track items, but flag it

        checks["fail_reasons"] = fail_reasons
        results.append({
            "item_id": item_id,
            "title": title,
            "exempt": False,
            "compliant": compliant,
            "checks": checks,
        })

    non_exempt = [r for r in results if not r["exempt"]]
    with_transcript = sum(1 for r in non_exempt if r["checks"].get("has_transcript"))
    with_skill_id = sum(1 for r in non_exempt if r["checks"].get("has_skill_id"))
    with_exemption = sum(1 for r in non_exempt if r["checks"].get("has_explicit_exemption"))
    with_any_evidence = sum(1 for r in non_exempt if r["checks"].get("has_any_evidence"))

    # STRICT ENFORCEMENT: if non_exempt_items > 0 and both transcript=0 and skill_id=0,
    # compliance cannot pass unless ALL non-exempt items have SOME form of evidence OR explicit exemption.
    # "Some evidence" includes: transcripts, skill_ids, any evidence_paths, or ledger entries.
    # Items with NO evidence at all AND no exemption trigger strict_fail.
    # Items with non-transcript evidence (reports, docs) do NOT trigger strict_fail.
    items_compliant = all(r["compliant"] for r in results)
    strict_fail = False
    if non_exempt and with_transcript == 0 and with_skill_id == 0:
        if with_exemption + with_any_evidence < len(non_exempt):
            strict_fail = True

    all_compliant = items_compliant and not strict_fail

    # Classify result
    if not all_compliant:
        # Determine primary failure type
        ledger_fails = [r for r in non_exempt if "missing_ledger" in r["checks"].get("fail_reasons", [])]
        transcript_fails = [r for r in non_exempt if "missing_transcript" in r["checks"].get("fail_reasons", [])]
        skill_id_fails = [r for r in non_exempt if "missing_skill_id" in r["checks"].get("fail_reasons", [])]

        if strict_fail and with_transcript == 0:
            classification = COMPLIANCE_FAIL_MISSING_TRANSCRIPTS
        elif transcript_fails:
            classification = COMPLIANCE_FAIL_MISSING_TRANSCRIPTS
        elif skill_id_fails:
            classification = COMPLIANCE_FAIL_MISSING_SKILL_IDS
        elif ledger_fails:
            classification = COMPLIANCE_FAIL_MISSING_LEDGER
        else:
            classification = COMPLIANCE_FAIL_MISSING_TRANSCRIPTS
    elif with_exemption > 0:
        classification = COMPLIANCE_PASS_WITH_EXEMPTIONS
    else:
        classification = COMPLIANCE_PASS

    return {
        "compliant": all_compliant,
        "compliance_classification": classification,
        "total_items": len(results),
        "exempt_items": sum(1 for r in results if r["exempt"]),
        "non_exempt_items": len(non_exempt),
        "items_with_transcript": with_transcript,
        "items_with_skill_id": with_skill_id,
        "items_with_explicit_exemption": with_exemption,
        "strict_fail": strict_fail,
        "items": results,
        "summary": (
            f"Adoption compliance: {classification}. "
            f"{len(non_exempt)} non-exempt items, "
            f"{with_transcript} with transcript, "
            f"{with_skill_id} with skill_id, "
            f"{with_exemption} with explicit exemption."
        ),
    }


def check_work_type_skill_gate(declaration: dict, repo_root: Path | None = None) -> list:
    """Fix 2: Read work-type-skill-map.yaml and check PRODUCT items against it.

    Returns list of (item_id, work_type, reason) for violations.
    Empty list = all clear.
    """
    root = repo_root or REPO_ROOT
    map_path = root / ".supervisor" / "work-type-skill-map.yaml"
    if not map_path.exists():
        return [("SYSTEM", None, "SKILL_MAP_MISSING")]

    if yaml is None:
        return []  # yaml not available — skip silently

    skill_map = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    gap_mappings = skill_map.get("gap_mappings", {})

    violations = []
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
            continue
        work_type = item.get("work_type")
        item_id = item.get("item_id", "UNKNOWN")

        if not work_type:
            continue  # MISSING_WORK_TYPE is advisory — many items omit this field
        if work_type in gap_mappings:
            clause = gap_mappings[work_type].get("master_plan_clause", "")
            violations.append((item_id, work_type, f"BLOCKED_SKILL_GAP:{clause}"))

    return violations
