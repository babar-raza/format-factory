"""Prompt template registry with hash/version tracking.

Only minimal harmless probe templates for Phase 1.
No production prompts, no secrets.
"""

from __future__ import annotations

from tools.ai.schemas.models import PromptTemplateRecord

# Phase 1 probe templates only — harmless capability checks
PROBE_TEMPLATES: dict[str, PromptTemplateRecord] = {}


def register_template(template_id: str, version: str, template_text: str) -> PromptTemplateRecord:
    """Register a prompt template and compute its hash."""
    record = PromptTemplateRecord(
        template_id=template_id,
        version=version,
        template_text=template_text,
    )
    record.compute_hash()
    PROBE_TEMPLATES[template_id] = record
    return record


def get_template(template_id: str) -> PromptTemplateRecord | None:
    """Retrieve a registered template by ID."""
    return PROBE_TEMPLATES.get(template_id)


# Register Phase 1 harmless probe templates
register_template(
    template_id="capability_probe_v1",
    version="1.0.0",
    template_text="Respond with exactly: PROBE_OK",
)

register_template(
    template_id="model_identity_probe_v1",
    version="1.0.0",
    template_text="What model are you? Respond in one short sentence.",
)
