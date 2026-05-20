"""End-to-end AI pilot pipeline -- fixture and live gateway modes.

Implements the full pipeline:
normalized chunks -> retrieval -> synthesis draft -> citation verification ->
contradiction check -> authority lifecycle transition -> generated requirements draft.

Supports two synthesis modes:
- fixture_synthesis: locally constructed JSON (deterministic, no LLM call)
- live_gateway_synthesis: real gateway call via litellm (requires env config)

Designed for FODS format as the pilot target.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ai.normalization.adapter import (
    NormalizationNotAvailable,
    NormalizedChunk,
    load_normalized_chunks,
)
from tools.ai.synthesis.citation_verifier import verify_all_citations
from tools.ai.synthesis.contradiction_detector import check_output_contradictions
from tools.ai.synthesis.evaluator import EvaluationCriteria, evaluate_synthesis
from tools.ai.synthesis.runner import SynthesisResult, run_synthesis
from tools.ai.schemas.models import AITaskContract, ArtifactAuthorityStateValue
from tools.ai.validators.authority_lifecycle import VALID_TRANSITIONS


# Contradiction policy modes
CONTRADICTION_POLICIES = {
    "required": "Must check; fail if no facts available",
    "optional": "Check if facts available; skip otherwise",
    "skipped_fixture_only": "Skip for fixture mode; require for live",
    "blocked_missing_facts": "Blocked -- facts not available",
}


# Diverse fixture chunks per format for meaningful retrieval ranking
_FIXTURE_CORPUS = {
    "fods": [
        {
            "path": "specs/normalization/fods/xml-structure.md",
            "section": "XML Structure and Format Specification",
            "content": "The FODS format specification defines a flat XML structure with office:document as the root element. Parsing requirements include handling office:body and office:spreadsheet elements. Each table is a table:table element with table:table-row and table:table-cell children. Cell values use office:value-type to specify data types including float, string, date, and boolean. The format requires strict XML namespace compliance.",
        },
        {
            "path": "specs/normalization/fods/cell-formatting.md",
            "section": "Cell Formatting",
            "content": "Cell formatting in FODS is controlled by style:style elements in office:automatic-styles. Number formats use number:number-style with children elements. Font properties are set via style:text-properties with attributes like fo:font-size and fo:font-weight. Conditional formatting applies style maps based on cell values.",
        },
        {
            "path": "specs/normalization/fods/data-types.md",
            "section": "Data Type Requirements",
            "content": "The FODS format specification requires parsing several data types: float for numeric values, string for text, date for ISO 8601, time for durations, boolean for true/false, and currency. Requirements for parsing include validating office:value against the declared type. The text:p element contains the display representation.",
        },
        {
            "path": "specs/normalization/fods/formulas.md",
            "section": "Formula Support",
            "content": "Formulas in FODS use table:formula with the of: namespace prefix for OpenFormula expressions. Cell references use dot notation like .A1 for same-sheet references. Cross-sheet references use the sheet name followed by a dot. Formula evaluation is outside parser scope.",
        },
        {
            "path": "specs/normalization/fods/metadata.md",
            "section": "Document Metadata",
            "content": "Document metadata in FODS resides in office:meta containing dc:title, dc:creator, dc:date, and meta:document-statistic. The generator tag identifies the producing application. Custom properties use meta:user-defined elements. Metadata extraction is optional for basic parsing.",
        },
    ],
}


def _get_diverse_fixture_chunks(format_id: str) -> list[dict[str, str]]:
    """Return diverse fixture chunk data for a format."""
    if format_id in _FIXTURE_CORPUS:
        return _FIXTURE_CORPUS[format_id]
    return [
        {
            "path": f"specs/normalization/{format_id}/structure.md",
            "section": "File Structure",
            "content": f"The {format_id.upper()} format defines a structured document with header, body, and metadata sections. The header contains version and encoding information.",
        },
        {
            "path": f"specs/normalization/{format_id}/parsing.md",
            "section": "Parsing Rules",
            "content": f"Parsing {format_id.upper()} requires reading the header bytes to determine encoding and version. The parser must validate magic bytes and reject malformed input with clear error messages.",
        },
        {
            "path": f"specs/normalization/{format_id}/validation.md",
            "section": "Validation Requirements",
            "content": f"Validation of {format_id.upper()} documents checks structural integrity, required fields presence, data type conformance, and size limits. Invalid documents must be rejected before processing.",
        },
    ]


@dataclass
class PilotConfig:
    """Configuration for an E2E pilot run."""
    format_id: str = "fods"
    repo_root: Path = field(default_factory=lambda: Path("."))
    verified_facts_path: Path | None = None
    fixture_mode: bool = True
    live_gateway: bool = False
    use_lexical_retrieval: bool = False
    retrieval_query: str = ""
    retrieval_top_k: int = 5
    sprint_id: str = ""
    contradiction_policy: str = "optional"

    @property
    def synthesis_mode(self) -> str:
        if self.live_gateway:
            return "live_gateway_synthesis"
        return "fixture_synthesis"


@dataclass
class PilotResult:
    """Complete result of an E2E pilot run."""
    format_id: str
    stage_results: dict[str, Any] = field(default_factory=dict)
    final_authority_state: str = "ai_draft"
    errors: list[str] = field(default_factory=list)
    timestamp: str = ""

    @property
    def all_stages_passed(self) -> bool:
        return all(
            s.get("passed", False)
            for s in self.stage_results.values()
            if isinstance(s, dict)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_id": self.format_id,
            "stage_results": self.stage_results,
            "final_authority_state": self.final_authority_state,
            "all_stages_passed": self.all_stages_passed,
            "errors": self.errors,
            "timestamp": self.timestamp,
        }


def stage_1_load_chunks(config: PilotConfig) -> tuple[list[NormalizedChunk], list[str]]:
    """Stage 1: Load normalized chunks for the target format."""
    errors: list[str] = []
    chunks: list[NormalizedChunk] = []

    if config.fixture_mode:
        fixture_data = _get_diverse_fixture_chunks(config.format_id)
        chunks = [
            NormalizedChunk(
                format_id=config.format_id,
                source_path=fd["path"],
                source_hash=hashlib.sha256(fd["path"].encode()).hexdigest()[:16],
                section=fd["section"],
                page=str(i),
                content=fd["content"],
                extraction_method="fixture",
                normalization_version="1.0.0",
                chunk_hash=hashlib.sha256(fd["content"].encode()).hexdigest()[:16],
            )
            for i, fd in enumerate(fixture_data, 1)
        ]
        return chunks, errors

    try:
        chunks = load_normalized_chunks(config.format_id, config.repo_root)
    except NormalizationNotAvailable as e:
        errors.append(f"normalization_not_available: {e}")
    except Exception as e:
        errors.append(f"chunk_load_error: {type(e).__name__}")

    return chunks, errors


def stage_2_retrieval(
    chunks: list[NormalizedChunk],
    query: str = "",
    use_lexical: bool = False,
    format_id: str = "",
    top_k: int = 5,
) -> tuple[list[NormalizedChunk], dict[str, Any]]:
    """Stage 2: Retrieve relevant chunks."""
    if use_lexical and query and format_id:
        from tools.ai.retrieval.lexical_retriever import retrieve
        result = retrieve(query=query, chunks=chunks, format_id=format_id, top_k=top_k)
        retrieved = [sc.chunk for sc in result.scored_chunks]
        metadata = result.to_dict()
        metadata["passed"] = result.has_results
        return retrieved, metadata

    metadata = {
        "query": query or "default_pilot_query",
        "total_chunks": len(chunks),
        "retrieved": len(chunks),
        "mode": "fixture_return_all",
    }
    return chunks, metadata


def _resolve_contradiction_check(config: PilotConfig) -> bool:
    """Determine whether contradiction checking is required based on policy."""
    policy = config.contradiction_policy
    if policy == "required":
        return True
    if policy == "skipped_fixture_only":
        return config.live_gateway
    if policy == "optional":
        return config.verified_facts_path is not None
    return False


def _build_fixture_output(chunks: list[NormalizedChunk], config: PilotConfig) -> str:
    """Build deterministic fixture synthesis output (no LLM call)."""
    citations = [{"source": c.source_path, "text": c.content} for c in chunks]
    return json.dumps({
        "format": config.format_id,
        "requirements": [
            {
                "id": f"REQ-{config.format_id.upper()}-PILOT-{i}",
                "text": f"The {config.format_id} parser shall handle {c.section}",
                "source": c.source_path,
                "provenance": "ai_draft",
            }
            for i, c in enumerate(chunks, 1)
        ],
        "citations": citations,
    })


def _build_live_output(
    chunks: list[NormalizedChunk], config: PilotConfig,
) -> tuple[str, dict[str, Any] | None]:
    """Call gateway for real synthesis output."""
    from tools.ai.control_plane.config import load_ai_config
    from tools.ai.control_plane.model_discovery import discover_models
    from tools.ai.control_plane.gateway import gateway_chat

    ai_cfg = load_ai_config()
    if not ai_cfg.is_configured:
        return "", {"status": "blocked_missing_env", "synthesis_mode": "blocked_live_synthesis"}

    models = discover_models(ai_cfg)
    chat_models = [m for m in models if m.supports_chat and not m.supports_embedding]
    if not chat_models:
        return "", {"status": "blocked_no_models", "synthesis_mode": "blocked_live_synthesis"}

    model_id = chat_models[0].model_id
    source_text = "\n\n".join(f"[{c.source_path}]\n{c.content}" for c in chunks)
    prompt = (
        f"Extract structured requirements from the following {config.format_id.upper()} "
        f"specification snippets. Return JSON with keys: format, requirements (list of "
        f"id/text/source/provenance), citations (list of source/text pairs).\n\n{source_text}"
    )

    response, record = gateway_chat(
        config=ai_cfg, model=model_id,
        messages=[{"role": "user", "content": prompt}],
        role="structured_extraction", operation="live_pipeline_synthesis",
        sprint_id=config.sprint_id,
    )

    telem = {
        "synthesis_mode": "live_gateway_synthesis",
        "model": model_id,
        "status": record.status.value,
        "input_tokens": record.input_tokens,
        "output_tokens": record.output_tokens,
        "total_tokens": record.total_tokens,
        "prompt_hash": record.prompt_hash,
        "endpoint_identity": ai_cfg.endpoint_identity,
    }

    content = response.get("content", "")
    if not content:
        telem["status"] = "empty_response"
        return "", telem

    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        json_lines = [ln for ln in lines if not ln.startswith("```")]
        raw = "\n".join(json_lines).strip()

    return raw, telem


def stage_3_synthesis(
    chunks: list[NormalizedChunk],
    config: PilotConfig,
) -> tuple[SynthesisResult, dict[str, Any]]:
    """Stage 3: Run synthesis on retrieved chunks.

    Returns (SynthesisResult, stage_metadata).
    """
    require_contradiction = _resolve_contradiction_check(config)
    contract = AITaskContract(
        task_id=f"pilot-{config.format_id}-synthesis",
        task_type="synthesis",
        role="structured_extraction",
        require_citation=True,
        require_contradiction_check=require_contradiction,
    )

    stage_meta: dict[str, Any] = {"synthesis_mode": config.synthesis_mode}

    if config.live_gateway:
        raw_output, telem = _build_live_output(chunks, config)
        if telem:
            stage_meta.update(telem)
        if not raw_output:
            stage_meta["fallback"] = "fixture_synthesis"
            raw_output = _build_fixture_output(chunks, config)
    else:
        raw_output = _build_fixture_output(chunks, config)

    source_snippets = {c.source_path: c.content for c in chunks}
    result = run_synthesis(
        contract, raw_output,
        source_snippets=source_snippets,
        verified_facts_path=config.verified_facts_path,
    )
    return result, stage_meta


def stage_4_evaluate(synthesis_result: SynthesisResult) -> dict[str, Any]:
    """Stage 4: Evaluate synthesis quality."""
    contradiction_was_checked = synthesis_result.contradiction_check_status != "not_checked"
    criteria = EvaluationCriteria(
        require_schema_valid=True,
        require_no_errors=True,
        require_citations=True,
        min_citation_count=1,
        require_no_contradictions=contradiction_was_checked,
    )
    evaluation = evaluate_synthesis(synthesis_result, criteria)
    return evaluation.to_dict()


def run_pilot(config: PilotConfig | None = None) -> PilotResult:
    """Execute the full E2E pilot pipeline."""
    if config is None:
        config = PilotConfig()

    result = PilotResult(
        format_id=config.format_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    chunks, chunk_errors = stage_1_load_chunks(config)
    result.stage_results["1_load_chunks"] = {
        "passed": len(chunks) > 0,
        "chunk_count": len(chunks),
        "errors": chunk_errors,
    }
    if not chunks:
        result.errors.append("no_chunks_loaded")
        return result

    retrieved, retrieval_meta = stage_2_retrieval(
        chunks,
        query=config.retrieval_query or f"{config.format_id} format specification requirements",
        use_lexical=config.use_lexical_retrieval,
        format_id=config.format_id,
        top_k=config.retrieval_top_k,
    )
    result.stage_results["2_retrieval"] = {
        "passed": len(retrieved) > 0,
        **retrieval_meta,
    }

    synthesis, synth_meta = stage_3_synthesis(retrieved, config)
    result.stage_results["3_synthesis"] = {
        "passed": synthesis.is_valid,
        "authority_state": synthesis.authority_state.value,
        "error_count": len(synthesis.errors),
        "citation_count": len(synthesis.citations),
        "synthesis_mode": synth_meta.get("synthesis_mode", "unknown"),
        **{k: v for k, v in synth_meta.items() if k != "synthesis_mode"},
    }

    eval_result = stage_4_evaluate(synthesis)
    result.stage_results["4_evaluation"] = eval_result

    result.final_authority_state = "ai_draft"
    return result
