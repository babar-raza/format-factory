"""Validate adoption compliance for evidence declarations.

Checks whether product work items reference skill_ids, include transcript
evidence, and have ledger entries for src-editing items.

R108: Created as part of the adoption compliance enforcement campaign.
REPAIR (autonomous-system-audit): Added strict enforcement — compliance cannot
pass with 0 transcripts / 0 skill_ids when non-exempt items exist, unless every
non-exempt item has an explicit exemption_reason.
"""

from __future__ import annotations

import json
import sys
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


def _has_explicit_exemption(item: dict) -> bool:
    """Check if the item has an explicit exemption_reason."""
    return bool(item.get("exemption_reason") or item.get("transcript_exemption_reason"))


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

        # Check 3: For src-editing items, is there a ledger entry?
        track = item.get("product_track", "")
        if track in SRC_EDITING_TRACKS:
            ledger_id = item.get("ledger_entry_id", "")
            checks["has_ledger_entry"] = bool(ledger_id)
            if not ledger_id and not _has_explicit_exemption(item):
                checks["ledger_missing_reason"] = f"src-editing track '{track}' requires ledger_entry_id"
                compliant = False
                fail_reasons.append("missing_ledger")
            # Source-changing items always require transcript unless explicitly exempted
            if not has_transcript and not _has_explicit_exemption(item):
                checks["transcript_required"] = True
                compliant = False
                fail_reasons.append("missing_transcript")
            # Source-changing items always require skill_id unless explicitly exempted
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

    # STRICT ENFORCEMENT: if non_exempt_items > 0 and both transcript=0 and skill_id=0,
    # compliance cannot pass unless ALL non-exempt items have explicit exemptions
    strict_fail = False
    if non_exempt and with_transcript == 0 and with_skill_id == 0:
        if with_exemption < len(non_exempt):
            strict_fail = True

    items_compliant = all(r["compliant"] for r in results)
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
