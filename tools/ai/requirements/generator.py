"""AI-generated requirements pipeline — schema-validated requirements with provenance.

Generates requirements from normalized spec chunks and synthesis outputs.
Every requirement carries provenance linking to source evidence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class GeneratedRequirement:
    """A single AI-generated requirement with full provenance."""
    req_id: str
    text: str
    format_id: str
    source_chunk_hash: str = ""
    source_path: str = ""
    source_section: str = ""
    authority_state: str = "ai_draft"
    priority: str = "AI_PROPOSAL"
    verifier_status: str = "pending_review"
    verifier_reason: str = ""
    generation_timestamp: str = ""
    generation_hash: str = ""

    def compute_hash(self) -> str:
        raw = f"{self.req_id}|{self.text}|{self.source_chunk_hash}"
        self.generation_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.generation_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "req_id": self.req_id,
            "text": self.text,
            "format_id": self.format_id,
            "source_chunk_hash": self.source_chunk_hash,
            "source_path": self.source_path,
            "source_section": self.source_section,
            "authority_state": self.authority_state,
            "priority": self.priority,
            "verifier_status": self.verifier_status,
            "verifier_reason": self.verifier_reason,
            "generation_timestamp": self.generation_timestamp,
            "generation_hash": self.generation_hash,
        }


REQUIREMENT_SCHEMA = {
    "required_fields": [
        "req_id", "text", "format_id", "source_chunk_hash",
        "authority_state", "priority", "verifier_status",
    ],
    "valid_priorities": [
        "EXISTING_SOURCE", "TEST_EVIDENCE", "VERIFIED_FACT",
        "SPEC", "PRODUCT_DECISION", "AI_PROPOSAL",
    ],
    "valid_authority_states": ["ai_draft", "schema_validated", "verifier_reviewed"],
    "valid_verifier_statuses": ["pending_review", "accepted", "rejected"],
}


def validate_requirement(req: GeneratedRequirement) -> list[str]:
    """Validate a generated requirement against the schema."""
    errors: list[str] = []
    if not req.req_id:
        errors.append("missing req_id")
    if not req.text:
        errors.append("missing text")
    if not req.format_id:
        errors.append("missing format_id")
    if not req.source_chunk_hash:
        errors.append("missing source_chunk_hash (no provenance)")
    if req.priority not in REQUIREMENT_SCHEMA["valid_priorities"]:
        errors.append(f"invalid priority: {req.priority}")
    if req.verifier_status not in REQUIREMENT_SCHEMA["valid_verifier_statuses"]:
        errors.append(f"invalid verifier_status: {req.verifier_status}")
    return errors


def review_requirement(
    req: GeneratedRequirement,
    accept: bool,
    reason: str = "",
) -> GeneratedRequirement:
    """Apply verifier review to a requirement."""
    req.verifier_status = "accepted" if accept else "rejected"
    req.verifier_reason = reason
    if accept:
        req.authority_state = "verifier_reviewed"
    return req


def generate_requirements_from_synthesis(
    synthesis_output: dict[str, Any],
    format_id: str,
) -> list[GeneratedRequirement]:
    """Extract requirements from a synthesis output dict."""
    requirements: list[GeneratedRequirement] = []
    raw_reqs = synthesis_output.get("requirements", [])

    for i, raw in enumerate(raw_reqs):
        if not isinstance(raw, dict):
            continue
        req = GeneratedRequirement(
            req_id=raw.get("id", f"REQ-{format_id.upper()}-GEN-{i+1:03d}"),
            text=raw.get("text", ""),
            format_id=format_id,
            source_chunk_hash=raw.get("source_chunk_hash", ""),
            source_path=raw.get("source", ""),
            source_section=raw.get("section", ""),
            priority="AI_PROPOSAL",
            generation_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        req.compute_hash()
        requirements.append(req)

    return requirements


def write_requirements_packet(
    requirements: list[GeneratedRequirement],
    output_path: Path,
) -> Path:
    """Write a requirements packet as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "format": requirements[0].format_id if requirements else "unknown",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority_state": "ai_draft",
        "count": len(requirements),
        "requirements": [r.to_dict() for r in requirements],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return output_path
