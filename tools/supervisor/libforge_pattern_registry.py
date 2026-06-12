"""
libforge_pattern_registry.py — FF-native LibForge pattern registry.

Maps patterns from external projects (apidev, refdev, specdev) to their
Format Factory integration status and adoption recommendation.

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
No live LLM calls. No external repo imports. Pure deterministic logic.

Pattern sources:
  - apidev: deterministic capability catalog verification (no LLM)
  - refdev: compose/verify loop with single LLM boundary + compile gates
  - specdev: freeze-gate verification pattern with template-driven test drivers

Adoption modes:
  - DIRECT_REUSE_CANDIDATE: can adopt with minimal wrapper
  - WRAPPER_REUSE_CANDIDATE: useful pattern, needs adapter layer
  - FF_NATIVE_REIMPLEMENTATION: must be reimplemented for FF context
  - DEFERRED: valid pattern, not needed yet
  - REJECT_UNSAFE: direct import would introduce unsafe coupling
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class PatternSource(str, Enum):
    APIDEV = "apidev"
    REFDEV = "refdev"
    SPECDEV = "specdev"
    FF_NATIVE = "ff_native"


class PatternCategory(str, Enum):
    CAPABILITY_VERIFICATION = "capability_verification"
    COMPOSE_VERIFY_LOOP = "compose_verify_loop"
    FREEZE_GATE = "freeze_gate"
    TEMPLATE_DRIVER = "template_driver"
    LLM_BOUNDARY = "llm_boundary"
    DETERMINISTIC_POST_GEN_GATE = "deterministic_post_generation_gate"
    ISOLATED_JOB_EXECUTION = "isolated_job_execution"


class AdoptionMode(str, Enum):
    DIRECT_REUSE_CANDIDATE = "DIRECT_REUSE_CANDIDATE"
    WRAPPER_REUSE_CANDIDATE = "WRAPPER_REUSE_CANDIDATE"
    FF_NATIVE_REIMPLEMENTATION = "FF_NATIVE_REIMPLEMENTATION"
    DEFERRED = "DEFERRED"
    REJECT_UNSAFE = "REJECT_UNSAFE"


@dataclass
class FFMapping:
    """Existing FF component that implements or relates to a pattern."""
    component: str
    path: str
    status: str  # "implemented", "partial", "missing"
    notes: str = ""


@dataclass
class PatternRecord:
    pattern_id: str
    source: PatternSource
    category: PatternCategory
    adoption_mode: AdoptionMode
    description: str
    source_path: str  # path or module in source project
    ff_mapping: FFMapping | None = None
    unsafe_coupling: list[str] = field(default_factory=list)
    integration_notes: str = ""
    requires_ff_native: bool = False
    priority: int = 2  # 1=high, 2=medium, 3=low


# ---------------------------------------------------------------------------
# Registry definition
# ---------------------------------------------------------------------------

_REGISTRY: list[PatternRecord] = [
    # --- apidev patterns ---
    PatternRecord(
        pattern_id="APIDEV-CAP-VERIFY",
        source=PatternSource.APIDEV,
        category=PatternCategory.CAPABILITY_VERIFICATION,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Deterministic capability catalog verification: check that every "
            "declared capability entry actually exists in the canonical surface "
            "(UNBOUND, INVENTED, SIGNATURE_FQN_MISMATCH, STALE_DROP detection). "
            "No LLM required."
        ),
        source_path="apidev/verifier.py:verify_coverage()",
        ff_mapping=FFMapping(
            component="CapabilityVerifier",
            path="tools/supervisor/capability_verifier.py",
            status="partial",
            notes="FF CapabilityVerifier checks import validity but not YAML-anchored "
                  "canonical surface comparison. Missing UNBOUND/INVENTED defect classes.",
        ),
        unsafe_coupling=[],
        integration_notes=(
            "FF-native reimplementation recommended: apidev is tightly coupled to "
            "Roslyn .NET assembly extraction and Aspose.PDF YAML schemas. "
            "The pattern (verify declared vs actual) transfers cleanly but the "
            "implementation must use FF's format-registry.yaml as the canonical surface."
        ),
        requires_ff_native=True,
        priority=1,
    ),
    PatternRecord(
        pattern_id="APIDEV-SEED-IDEMPOTENT",
        source=PatternSource.APIDEV,
        category=PatternCategory.DETERMINISTIC_POST_GEN_GATE,
        adoption_mode=AdoptionMode.WRAPPER_REUSE_CANDIDATE,
        description=(
            "Idempotent re-seed: skip existing files unless --force; "
            "with --force, output is deterministic from canonical. "
            "Prevents overwrite loops."
        ),
        source_path="apidev/cli.py:cmd_seed()",
        ff_mapping=FFMapping(
            component="autonomous_cycle.py stale repair",
            path="tools/supervisor/autonomous_cycle.py",
            status="partial",
            notes="FF has stale_queue_repair_hook but no idempotency key enforcement on file writes.",
        ),
        unsafe_coupling=["apidev.capability", "apidev.config"],
        integration_notes=(
            "Pattern is safe to wrap. Adapt the skip-existing + force-override logic "
            "to FF's evidence declaration write paths."
        ),
        requires_ff_native=False,
        priority=2,
    ),
    PatternRecord(
        pattern_id="APIDEV-STALE-DROP-DETECTION",
        source=PatternSource.APIDEV,
        category=PatternCategory.CAPABILITY_VERIFICATION,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Stale drop/annotation detection: STALE_DROP and STALE_ANNOTATION "
            "defect classes detect when sidecar files have drifted from the "
            "canonical catalog entry."
        ),
        source_path="apidev/verifier.py",
        ff_mapping=FFMapping(
            component="governance_validators.py V13",
            path="tools/supervisor/governance_validators.py",
            status="partial",
            notes="V13 checks spec_fact_refs wired but not cross-file sidecar drift.",
        ),
        unsafe_coupling=["apidev.capability", "apidev.config", "dotnet-script"],
        integration_notes="Reimplement for FF: compare evidence-declaration sidecars vs registry.",
        requires_ff_native=True,
        priority=2,
    ),
    # --- refdev patterns ---
    PatternRecord(
        pattern_id="REFDEV-COMPOSE-VERIFY-LOOP",
        source=PatternSource.REFDEV,
        category=PatternCategory.COMPOSE_VERIFY_LOOP,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Compose → verify feedback loop with retry: LLM generates body, "
            "compile-check gate runs, if fail → regenerate with error feedback, "
            "up to N retries. Verify stage builds + runs smoke test."
        ),
        source_path="refdev/orchestrator.py:compose_capability()",
        ff_mapping=FFMapping(
            component="ComposeVerifyLoop",
            path="tools/supervisor/compose_verify_loop.py",
            status="partial",
            notes="FF ComposeVerifyLoop covers the core loop. Missing: product mutation gate "
                  "that prevents source changes outside allowed paths.",
        ),
        unsafe_coupling=[
            "refdev.agent_composer",
            "Aspose.PDF specific system prompts",
            "macOS Homebrew clang paths",
        ],
        integration_notes=(
            "FF ComposeVerifyLoop is the correct FF-native reimplementation. "
            "The missing gap is a product mutation gate check before the compose "
            "step writes to src/python/. Must integrate with SAL/RCAL authority."
        ),
        requires_ff_native=True,
        priority=1,
    ),
    PatternRecord(
        pattern_id="REFDEV-SINGLE-LLM-BOUNDARY",
        source=PatternSource.REFDEV,
        category=PatternCategory.LLM_BOUNDARY,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Single LLM boundary: only agent_composer.py calls the LLM. "
            "All orchestration, verification, and retry logic is deterministic. "
            "This is the most important architectural separation in refdev."
        ),
        source_path="refdev/agent_composer.py",
        ff_mapping=FFMapping(
            component="endpoint_client.py + autonomous_cycle LLM calls",
            path="tools/llm/endpoint_client.py",
            status="partial",
            notes="FF has endpoint_client.py with fail-closed credential and advisory-only output. "
                  "But LLM calls are scattered across supervisor steps rather than isolated to one module.",
        ),
        unsafe_coupling=["refdev.agent_composer (macOS, Aspose-specific prompts)"],
        integration_notes=(
            "FF should enforce: all LLM calls go through endpoint_client.py only. "
            "governance_validators.py and autonomous_cycle.py should never call LLM directly."
        ),
        requires_ff_native=True,
        priority=1,
    ),
    PatternRecord(
        pattern_id="REFDEV-SOFT-SKIP-TOOLCHAIN",
        source=PatternSource.REFDEV,
        category=PatternCategory.DETERMINISTIC_POST_GEN_GATE,
        adoption_mode=AdoptionMode.WRAPPER_REUSE_CANDIDATE,
        description=(
            "Soft-skip pattern: when toolchain is missing (e.g. dotnet, clang), "
            "verifiers return ok=True with a skip message instead of failing. "
            "Compose-gate hard-fails (catches real errors). "
            "Prevents environment-specific test failures."
        ),
        source_path="refdev/verifier.py:470-472",
        ff_mapping=FFMapping(
            component="FreezeGateRunner",
            path="tools/supervisor/freeze_gate_runner.py",
            status="partial",
            notes="FF FreezeGateRunner has soft-skip for missing format fixtures but not "
                  "for missing toolchain binaries.",
        ),
        unsafe_coupling=[],
        integration_notes=(
            "Adopt the soft-skip pattern in FreezeGateRunner for optional gate steps. "
            "Hard-fail only on format or production gates."
        ),
        requires_ff_native=False,
        priority=2,
    ),
    # --- specdev patterns ---
    PatternRecord(
        pattern_id="SPECDEV-FREEZE-GATE",
        source=PatternSource.SPECDEV,
        category=PatternCategory.FREEZE_GATE,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Freeze-gate verification: LLM generates → compile → run deterministic "
            "test → retry on failure. 8 gate kinds × 4-6 languages. "
            "YAML anchor spec with freeze_gate_kind field. "
            "Replay-without-LLM: reuse existing body if gate already passes."
        ),
        source_path="specdev/verifier.py:verify_primitive()",
        ff_mapping=FFMapping(
            component="FreezeGateRunner",
            path="tools/supervisor/freeze_gate_runner.py",
            status="partial",
            notes="FF FreezeGateRunner has ZST binding_roundtrip and contract_validation gates. "
                  "Missing: multi-format gate enumeration, replay-without-LLM path, "
                  "FACT-* citation enforcement across all gate kinds.",
        ),
        unsafe_coupling=[
            "specdev.verifier (clang++/g++/dotnet build commands)",
            "specdev YAML anchor schema (PDF-specific fields)",
            "fixture corpora (external repos required)",
        ],
        integration_notes=(
            "FF FreezeGateRunner is the correct foundation. Extend it with: "
            "(1) multi-format gate registry; "
            "(2) replay-without-LLM path for already-passing formats; "
            "(3) per-format FACT-* citation enforcement."
        ),
        requires_ff_native=True,
        priority=1,
    ),
    PatternRecord(
        pattern_id="SPECDEV-TEMPLATE-DRIVER",
        source=PatternSource.SPECDEV,
        category=PatternCategory.TEMPLATE_DRIVER,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "Template-driven deterministic test driver generation: "
            "8 gate kinds × 4-6 languages = ~40 driver templates. "
            "render_driver() does pure template substitution. "
            "No LLM involved in driver generation."
        ),
        source_path="specdev/drivers/<lang>/",
        ff_mapping=FFMapping(
            component="test_drivers.py",
            path="tools/supervisor/test_drivers.py",
            status="partial",
            notes="FF test_drivers.py has template generation for Python format tests. "
                  "Missing: gate-kind enumeration, multi-language support.",
        ),
        unsafe_coupling=["specdev YAML anchor schema", "Aspose PDF fixture corpora"],
        integration_notes=(
            "Extend test_drivers.py with gate-kind parameter support. "
            "Start with Python-only as FF is Python-first."
        ),
        requires_ff_native=True,
        priority=2,
    ),
    PatternRecord(
        pattern_id="SPECDEV-ISOLATED-JOB-EXECUTION",
        source=PatternSource.SPECDEV,
        category=PatternCategory.ISOLATED_JOB_EXECUTION,
        adoption_mode=AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
        description=(
            "One-job-at-a-time execution: each capability is processed by a "
            "single job (compose + verify + gate). Jobs are independent and "
            "reproducible. No shared mutable state between jobs."
        ),
        source_path="specdev/orchestrator.py",
        ff_mapping=FFMapping(
            component="(missing)",
            path="tools/supervisor/libforge_isolated_job_runner.py",
            status="missing",
            notes="FF has no isolated job runner. ComposeVerifyLoop is close but "
                  "operates on the full FF workspace, not an isolated temp dir.",
        ),
        unsafe_coupling=[],
        integration_notes=(
            "Implement FF-native: libforge_isolated_job_runner.py. "
            "Runs in temp dir by default, dry-run mode, emits JSON result. "
            "Composes with FreezeGateRunner and AST scanner."
        ),
        requires_ff_native=True,
        priority=1,
    ),
]

# Index by pattern_id for fast lookup
_INDEX: dict[str, PatternRecord] = {r.pattern_id: r for r in _REGISTRY}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_patterns() -> list[PatternRecord]:
    """Return all registered patterns."""
    return list(_REGISTRY)


def get_pattern(pattern_id: str) -> PatternRecord | None:
    """Return a pattern by ID, or None if not found."""
    return _INDEX.get(pattern_id)


def get_patterns_by_source(source: PatternSource | str) -> list[PatternRecord]:
    """Return all patterns from a given source."""
    src = PatternSource(source) if isinstance(source, str) else source
    return [r for r in _REGISTRY if r.source == src]


def get_patterns_by_category(category: PatternCategory | str) -> list[PatternRecord]:
    """Return all patterns in a given category."""
    cat = PatternCategory(category) if isinstance(category, str) else category
    return [r for r in _REGISTRY if r.category == cat]


def get_patterns_by_adoption_mode(mode: AdoptionMode | str) -> list[PatternRecord]:
    """Return patterns with a given adoption mode."""
    m = AdoptionMode(mode) if isinstance(mode, str) else mode
    return [r for r in _REGISTRY if r.adoption_mode == m]


def is_safe_to_import(pattern_id: str) -> bool:
    """Return True if the pattern is safe for direct import (no unsafe coupling)."""
    rec = get_pattern(pattern_id)
    if rec is None:
        return False
    return (
        rec.adoption_mode != AdoptionMode.REJECT_UNSAFE
        and len(rec.unsafe_coupling) == 0
    )


def get_ff_missing_gaps() -> list[PatternRecord]:
    """Return patterns where the FF mapping is missing or partial with high priority."""
    gaps = []
    for r in _REGISTRY:
        if r.ff_mapping is None:
            gaps.append(r)
        elif r.ff_mapping.status in ("missing", "partial") and r.priority == 1:
            gaps.append(r)
    return gaps


def to_dict_list() -> list[dict]:
    """Serialize the full registry to a JSON-compatible list of dicts."""
    result = []
    for rec in _REGISTRY:
        d = {
            "pattern_id": rec.pattern_id,
            "source": rec.source.value,
            "category": rec.category.value,
            "adoption_mode": rec.adoption_mode.value,
            "description": rec.description,
            "source_path": rec.source_path,
            "unsafe_coupling": rec.unsafe_coupling,
            "integration_notes": rec.integration_notes,
            "requires_ff_native": rec.requires_ff_native,
            "priority": rec.priority,
        }
        if rec.ff_mapping:
            d["ff_mapping"] = {
                "component": rec.ff_mapping.component,
                "path": rec.ff_mapping.path,
                "status": rec.ff_mapping.status,
                "notes": rec.ff_mapping.notes,
            }
        else:
            d["ff_mapping"] = None
        result.append(d)
    return result
