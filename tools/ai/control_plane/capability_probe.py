"""Capability probe — minimal harmless check that a model is responsive.

Only sends trivial prompts. No synthesis, no generation, no agentic tasks.
"""

from __future__ import annotations

from tools.ai.control_plane.config import AIConfig
from tools.ai.control_plane.gateway import gateway_chat
from tools.ai.prompts.registry import get_template
from tools.ai.schemas.models import AIUsageRecord, CallStatus


def probe_model(
    config: AIConfig,
    model_id: str,
    sprint_id: str = "",
) -> tuple[bool, str, AIUsageRecord]:
    """Send a harmless probe to verify model responsiveness.

    Returns (success, response_text, telemetry_record).
    """
    template = get_template("capability_probe_v1")
    if template is None:
        record = AIUsageRecord(
            model=model_id,
            operation="capability_probe",
            status=CallStatus.error,
            error_class_redacted="missing_probe_template",
        )
        return False, "", record

    messages = [{"role": "user", "content": template.template_text}]

    response, record = gateway_chat(
        config=config,
        model=model_id,
        messages=messages,
        role="structured_extraction",
        operation="capability_probe",
        sprint_id=sprint_id,
    )
    record.prompt_hash = template.prompt_hash

    success = record.status == CallStatus.success and bool(response.get("content"))
    return success, response.get("content", ""), record
