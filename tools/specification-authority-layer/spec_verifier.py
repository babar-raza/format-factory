"""
spec_verifier.py — Verify extracted requirements against source sections.

Verification: confirm that each CandidateRequirement's text_fragment appears
in or can be traced back to the source artifact (anti-hallucination check).

Also provides anti-bypass checks:
  - reject requirements with no source_id
  - reject requirements citing unregistered sources
  - reject requirements from ai_summary-only context
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class VerificationResult:
    req_id: str
    source_id: str
    status: str  # VERIFIED | UNVERIFIABLE | ANTI_BYPASS_REJECTED
    reason: str
    verified_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "req_id": self.req_id,
            "source_id": self.source_id,
            "status": self.status,
            "reason": self.reason,
            "verified_at": self.verified_at,
        }


def verify_requirements(
    requirements: List[Dict[str, Any]],
    normalized_artifact: Optional[Dict[str, Any]] = None,
    registered_source_ids: Optional[List[str]] = None,
    artifacts_dir: Optional[str] = None,
) -> List[VerificationResult]:
    """
    Verify a list of requirement dicts.

    Anti-bypass:
      - Rejects if source_id is not in registered_source_ids (if provided)
      - Verifies text_fragment appears in normalized artifact sections

    Returns list of VerificationResult.
    """
    results = []

    for req in requirements:
        req_id = req.get("req_id", "UNKNOWN")
        source_id = req.get("source_id", "")
        text_fragment = req.get("text_fragment", "")

        # Anti-bypass: no source_id
        if not source_id:
            results.append(VerificationResult(
                req_id=req_id,
                source_id=source_id,
                status="ANTI_BYPASS_REJECTED",
                reason="No source_id — memory-only requirement not allowed.",
            ))
            continue

        # Anti-bypass: source not registered
        if registered_source_ids is not None and source_id not in registered_source_ids:
            results.append(VerificationResult(
                req_id=req_id,
                source_id=source_id,
                status="ANTI_BYPASS_REJECTED",
                reason=f"source_id {source_id!r} not in registered sources.",
            ))
            continue

        # Verify text_fragment exists in normalized artifact
        if normalized_artifact is not None:
            found = False
            for sec in normalized_artifact.get("sections", []):
                if text_fragment[:50].lower() in (sec.get("content", "") + sec.get("heading", "")).lower():
                    found = True
                    break
            if found:
                results.append(VerificationResult(
                    req_id=req_id,
                    source_id=source_id,
                    status="VERIFIED",
                    reason="Text fragment found in normalized artifact sections.",
                ))
            else:
                results.append(VerificationResult(
                    req_id=req_id,
                    source_id=source_id,
                    status="UNVERIFIABLE",
                    reason="Text fragment not found in normalized artifact — may be paraphrase.",
                ))
        else:
            # No artifact for cross-check — mark as UNVERIFIABLE but not rejected
            results.append(VerificationResult(
                req_id=req_id,
                source_id=source_id,
                status="UNVERIFIABLE",
                reason="No normalized artifact provided for cross-check.",
            ))

    return results


def check_anti_bypass(claim: Dict[str, Any], registered_source_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Anti-bypass check for a single capability claim.
    Returns {"pass": True/False, "violations": [...]}
    """
    violations = []

    source_refs = claim.get("source_refs", [])
    if not source_refs:
        violations.append("No source_refs — memory-only claim not allowed.")

    if registered_source_ids is not None:
        for sr in source_refs:
            if sr not in registered_source_ids:
                violations.append(f"source_ref {sr!r} not registered.")

    raw_ai_summary = claim.get("raw_ai_summary_only", False)
    if raw_ai_summary:
        violations.append("raw_ai_summary_only=True — AI summary without source_refs not allowed.")

    context_pack_sha = claim.get("context_pack_sha256", "")
    if claim.get("requires_context_pack", False) and not context_pack_sha:
        violations.append("requires_context_pack=True but no context_pack_sha256 provided.")

    return {
        "pass": len(violations) == 0,
        "violations": violations,
    }
