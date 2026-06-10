"""autonomy_route_decider.py — Governed autonomy routing layer.

Classifies tasks, decides routes, validates route decisions, and enforces
fail-closed rules so that product work may default to autonomous acceleration
only when qualified, while machinery requires a governed route decision.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.supervisor.autonomy_route_models import (
    ALL_ROUTES,
    ALL_TASK_CATEGORIES,
    DECISION_ACTOR_DEFAULT,
    REQUIRED_DECISION_FIELDS,
    ROUTE_AGENT_GOVERNED_DECISION_REQUIRED,
    ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT,
    ROUTE_BLOCKED,
    ROUTE_GOVERNED_DIRECT_EXECUTION,
    ROUTE_HUMAN_APPROVAL_REQUIRED,
    ROUTE_DECISIONS_DIR,
    SCHEMA_VERSION,
    SOURCE_MUTATING_ACTION_TYPES,
    TASK_CATEGORIES_MACHINERY,
    TASK_CATEGORIES_PRODUCT,
    TASK_CATEGORY_UNKNOWN,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Keyword classifiers
# ---------------------------------------------------------------------------
ACTION_TYPE_TO_CATEGORY: dict[str, str] = {
    "IMPLEMENT_SMALL_PRODUCT_FEATURE": "PRODUCT_IMPLEMENTATION",
    "PRODUCT_SOURCE_PATCH_BOUNDED": "PRODUCT_IMPLEMENTATION",
    "GENERATE_SAMPLE_OUTPUT": "PRODUCT_EXPORT_OR_DOGFOOD",
    "UPDATE_CAPABILITY_MAP": "PRODUCT_CAPABILITY_EXPANSION",
    "RUN_TARGETED_PYTEST": "PRODUCT_TESTING",
    "REPAIR_FAILING_TEST": "PRODUCT_TESTING",
    "GENERATE_TASK_CANDIDATES": "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "UPDATE_STATE": "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "GENERATE_EVIDENCE_STUB": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "UPDATE_PRODUCT_LEDGER": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "RUN_JSON_VALIDATION": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "RUN_MD_NONEMPTY_CHECK": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "PRODUCT_GAP_CLASSIFICATION_READONLY": "SPEC_AUTHORITY_MACHINERY",
}

PRODUCT_KEYWORDS = [
    "add function", "implement", "create src", "python codec",
    "format capability", "gnumeric", "abw", "tsv", "ndjson", "fodg",
    "fodt", "fods", "netpbm", "pbm", "pgm", "ppm", "zst",
]

MACHINERY_KEYWORD_MAP: dict[str, str] = {
    "autonomous_cycle": "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "autonomous_orchestrator": "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "supervisor_loop": "SUPERVISOR_VERDICT_MACHINERY",
    "grade_declared": "SUPERVISOR_VERDICT_MACHINERY",
    "spec-authority": "SPEC_AUTHORITY_MACHINERY",
    "spec_authority": "SPEC_AUTHORITY_MACHINERY",
    "poc-targets": "SPEC_AUTHORITY_MACHINERY",
    "action_queue": "ACTION_QUEUE_MACHINERY",
    "continuation_signal": "ACTION_QUEUE_MACHINERY",
    "governance_validator": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "anti_skip": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "evidence_declaration": "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "prompt_quality": "PROMPT_GENERATION_MACHINERY",
    "generate_next_worker_prompt": "PROMPT_GENERATION_MACHINERY",
    "skill_registry": "GOVERNED_SKILL_OR_GENERATOR_MACHINERY",
    "requirement_capability": "REQUIREMENT_CAPABILITY_MACHINERY",
}

# ---------------------------------------------------------------------------
# Unsafe instruction patterns (for prompt/queue quarantine)
# ---------------------------------------------------------------------------
UNSAFE_INSTRUCTION_PATTERNS = [
    "git commit",
    "git push",
    "npm publish",
    "pypi upload",
    "nuget push",
    "package publish",
    "mcp activate",
    "gate bypass",
    "gate_8_approval",
    "gate_11_approval",
]

ADVISORY_SKIP_MARKERS = [
    "advisory", "stop_reason", "example:", "e.g.", "never use",
    "false stop", "do not", "must not", "should not", "prohibited",
    "forbidden", "not allowed", "warning:", "caution:", "without",
]


# ---------------------------------------------------------------------------
# Route Decision dataclass
# ---------------------------------------------------------------------------
@dataclass
class RouteDecision:
    task_id: str
    task_category: str
    task_summary: str
    proposed_route: str
    final_route: str
    risk_level: str
    decision_status: str
    autonomous_allowed: bool
    acceleration_allowed: bool
    product_source_mutation_allowed: bool
    machinery_mutation_allowed: bool
    human_approval_required: bool
    blocked: bool
    required_evidence: list[str] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=list)
    reason: str = ""
    timestamp: str = ""
    decision_actor: str = DECISION_ACTOR_DEFAULT
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, output_dir: Path | None = None) -> Path:
        d = output_dir or (_REPO_ROOT / ROUTE_DECISIONS_DIR)
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{self.task_id}.json"
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return p


# ---------------------------------------------------------------------------
# classify_task_category
# ---------------------------------------------------------------------------
def classify_task_category(
    task_summary: str,
    action_type: str = "",
    hints: dict[str, Any] | None = None,
) -> str:
    """Return a task category string. Defaults to UNKNOWN_OR_AMBIGUOUS."""
    hints = hints or {}

    # 1. Explicit hint overrides
    explicit = hints.get("task_category", "")
    if explicit and explicit in ALL_TASK_CATEGORIES:
        return explicit

    # 2. Action type mapping
    if action_type and action_type in ACTION_TYPE_TO_CATEGORY:
        return ACTION_TYPE_TO_CATEGORY[action_type]

    # 3. Keyword scan — machinery first (more specific)
    summary_lower = task_summary.lower()
    for keyword, category in MACHINERY_KEYWORD_MAP.items():
        if keyword in summary_lower:
            return category

    # 4. Product keywords
    for kw in PRODUCT_KEYWORDS:
        if kw in summary_lower:
            return "PRODUCT_IMPLEMENTATION"

    return TASK_CATEGORY_UNKNOWN


# ---------------------------------------------------------------------------
# decide_route — fail-closed router
# ---------------------------------------------------------------------------
def decide_route(
    task_id: str,
    task_category: str,
    task_summary: str,
    risk_level: str = "LOW",
    hints: dict[str, Any] | None = None,
) -> RouteDecision:
    """Fail-closed route decision. Every unmatched path terminates at BLOCKED."""
    hints = hints or {}

    required_tests = hints.get("required_tests", [])
    required_evidence = hints.get("required_evidence", [])
    allowed_paths = hints.get("allowed_paths", [])
    forbidden_paths = hints.get("forbidden_paths", [])

    def _make(route: str, reason: str, **overrides: Any) -> RouteDecision:
        is_blocked = route == ROUTE_BLOCKED
        is_autonomous = route == ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT
        is_human = route == ROUTE_HUMAN_APPROVAL_REQUIRED
        is_machinery_allowed = route == ROUTE_GOVERNED_DIRECT_EXECUTION
        return RouteDecision(
            task_id=task_id,
            task_category=task_category,
            task_summary=task_summary,
            proposed_route=route,
            final_route=route,
            risk_level=risk_level,
            decision_status="BLOCKED" if is_blocked else "DECIDED",
            autonomous_allowed=is_autonomous,
            acceleration_allowed=is_autonomous,
            product_source_mutation_allowed=is_autonomous or is_machinery_allowed,
            machinery_mutation_allowed=is_machinery_allowed,
            human_approval_required=is_human,
            blocked=is_blocked,
            required_evidence=required_evidence,
            required_tests=required_tests,
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            reason=reason,
            **overrides,
        )

    # Rule 1: Unknown category → BLOCKED
    if task_category not in ALL_TASK_CATEGORIES:
        return _make(ROUTE_BLOCKED, f"Unknown task category: {task_category!r}")

    # Rule 2: UNKNOWN_OR_AMBIGUOUS → BLOCKED
    if task_category == TASK_CATEGORY_UNKNOWN:
        return _make(ROUTE_BLOCKED, "Task category is UNKNOWN_OR_AMBIGUOUS — fail closed")

    # Rule 3: High risk or explicit human approval → HUMAN_APPROVAL_REQUIRED
    if risk_level == "HIGH" or hints.get("human_approval_required"):
        return _make(ROUTE_HUMAN_APPROVAL_REQUIRED, "High risk or human approval required")

    # Rule 4: Machinery
    if task_category in TASK_CATEGORIES_MACHINERY:
        if hints.get("governed_decision_present"):
            return _make(ROUTE_GOVERNED_DIRECT_EXECUTION,
                         "Machinery with valid governed route decision")
        return _make(ROUTE_AGENT_GOVERNED_DECISION_REQUIRED,
                     "Machinery requires governed route decision before execution")

    # Rule 5: Product — only autonomous when qualified
    if task_category in TASK_CATEGORIES_PRODUCT:
        if required_tests and required_evidence and allowed_paths:
            return _make(ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT,
                         "Product work qualified for autonomous acceleration")
        return _make(ROUTE_AGENT_GOVERNED_DECISION_REQUIRED,
                     "Product work missing required_tests, required_evidence, or allowed_paths")

    # Rule 6: Default fallthrough → BLOCKED
    return _make(ROUTE_BLOCKED, "No matching route rule — fail closed")


# ---------------------------------------------------------------------------
# validate_route_decision
# ---------------------------------------------------------------------------
def validate_route_decision(decision: dict[str, Any]) -> list[str]:
    """Validate a route decision dict. Returns list of errors (empty = valid)."""
    errors: list[str] = []

    missing = REQUIRED_DECISION_FIELDS - set(decision.keys())
    if missing:
        errors.append(f"Missing required fields: {sorted(missing)}")

    fr = decision.get("final_route", "")
    if fr and fr not in ALL_ROUTES:
        errors.append(f"Invalid final_route: {fr!r}")

    tc = decision.get("task_category", "")
    if tc and tc not in ALL_TASK_CATEGORIES:
        errors.append(f"Invalid task_category: {tc!r}")

    if not isinstance(decision.get("autonomous_allowed"), bool):
        errors.append("autonomous_allowed must be a boolean")
    if not isinstance(decision.get("blocked"), bool):
        errors.append("blocked must be a boolean")

    # Consistency: blocked route must have blocked=True
    if fr == ROUTE_BLOCKED and decision.get("blocked") is not True:
        errors.append("BLOCKED route must have blocked=True")

    # Consistency: blocked items must not allow machinery mutation
    if decision.get("blocked") and decision.get("machinery_mutation_allowed"):
        errors.append("blocked items must not have machinery_mutation_allowed=True")

    return errors


# ---------------------------------------------------------------------------
# load_route_decision
# ---------------------------------------------------------------------------
def load_route_decision(
    decision_id: str,
    decisions_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Load a route decision JSON file by task_id. Returns None if not found."""
    d = decisions_dir or (_REPO_ROOT / ROUTE_DECISIONS_DIR)
    p = d / f"{decision_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# check_machinery_mutation_allowed
# ---------------------------------------------------------------------------
def check_machinery_mutation_allowed(
    item: dict[str, Any],
    decisions_dir: Path | None = None,
) -> tuple[bool, str]:
    """Check if an item is allowed to perform machinery mutation.

    Returns (allowed, reason).
    """
    cat = item.get("task_category", "")

    # No task_category: check if legacy/backfill non-source-mutating
    if not cat:
        if item.get("legacy_backfill") and item.get("action_type") not in SOURCE_MUTATING_ACTION_TYPES:
            return True, "Legacy/backfill non-source-mutating item — warn only"
        if item.get("action_type") in SOURCE_MUTATING_ACTION_TYPES:
            return False, "Source-mutating item missing task_category — blocked"
        # Non-source-mutating without category — allow with warn for backward compat
        return True, "Non-source-mutating item without task_category — allowed (backward compat)"

    # Product category — allowed
    if cat in TASK_CATEGORIES_PRODUCT:
        return True, "Product category — product mutation allowed"

    # Machinery category — must have valid route decision
    if cat in TASK_CATEGORIES_MACHINERY:
        rdid = item.get("route_decision_id", "")
        if not rdid:
            return False, f"Machinery category {cat!r} missing route_decision_id"
        decision = load_route_decision(rdid, decisions_dir)
        if decision is None:
            return False, f"Route decision {rdid!r} not found on disk"
        errors = validate_route_decision(decision)
        if errors:
            return False, f"Route decision {rdid!r} invalid: {errors}"
        if decision.get("blocked"):
            return False, f"Route decision {rdid!r} is blocked"
        if decision.get("task_id") != item.get("task_id", item.get("action_id", "")):
            return False, f"Route decision task_id mismatch: expected {item.get('task_id')}"
        if decision.get("task_category") != cat:
            return False, f"Route decision category mismatch: {decision.get('task_category')} vs {cat}"
        if not decision.get("machinery_mutation_allowed"):
            return False, f"Route decision {rdid!r} does not allow machinery mutation"
        return True, "Machinery with valid governed route decision"

    # Unknown → blocked
    return False, f"Unknown task category {cat!r} — blocked"


# ---------------------------------------------------------------------------
# check_action_route_allowed — pre-dispatch gate
# ---------------------------------------------------------------------------
def check_action_route_allowed(
    action: dict[str, Any],
    decisions_dir: Path | None = None,
) -> tuple[bool, str]:
    """Pre-dispatch route enforcement. Returns (allowed, reason).

    Checks:
    1. Source-mutating items without task_category → blocked (unless legacy/backfill)
    2. Machinery items without valid route decision → blocked
    3. Unknown category → blocked
    4. Product source-mutating items must have route_decision_id
    5. Non-source-mutating items without category allowed for backward compat (legacy only)
    """
    cat = action.get("task_category", "")
    action_type = action.get("action_type", "")
    is_legacy = action.get("legacy_backfill", False)

    # Current-run source-mutating without category → blocked
    if not cat and action_type in SOURCE_MUTATING_ACTION_TYPES:
        if not is_legacy:
            return False, "Source-mutating action without task_category — blocked"

    # Current-run with category but no legacy flag
    if cat and not is_legacy:
        # Machinery check
        if cat in TASK_CATEGORIES_MACHINERY:
            return check_machinery_mutation_allowed(action, decisions_dir)

        # Unknown/ambiguous category → blocked
        if cat == TASK_CATEGORY_UNKNOWN:
            return False, "UNKNOWN_OR_AMBIGUOUS task category — blocked"

        # Product source-mutating: must have route_decision_id
        if cat in TASK_CATEGORIES_PRODUCT and action_type in SOURCE_MUTATING_ACTION_TYPES:
            rdid = action.get("route_decision_id", "")
            if not rdid:
                return False, "Product source-mutating action missing route_decision_id — blocked"
            decision = load_route_decision(rdid, decisions_dir)
            if decision is None:
                return False, f"Route decision {rdid!r} not found on disk"
            errors = validate_route_decision(decision)
            if errors:
                return False, f"Route decision {rdid!r} invalid: {errors}"
            if decision.get("blocked"):
                return False, f"Route decision {rdid!r} is blocked"
            if decision.get("task_id") != action.get("task_id", action.get("action_id", "")):
                return False, f"Route decision task_id mismatch"
            if decision.get("task_category") != cat:
                return False, f"Route decision category mismatch: {decision.get('task_category')} vs {cat}"
            if not decision.get("required_tests"):
                return False, "Route decision has empty required_tests"
            if not decision.get("required_evidence"):
                return False, "Route decision has empty required_evidence"
            if not decision.get("allowed_paths"):
                return False, "Route decision has empty allowed_paths"
            return True, "Product source-mutating action with valid route decision"

        # Product non-source-mutating: allowed
        if cat in TASK_CATEGORIES_PRODUCT:
            return True, "Product non-source-mutating action — allowed"

    # Legacy backward compat for machinery
    if cat in TASK_CATEGORIES_MACHINERY:
        return check_machinery_mutation_allowed(action, decisions_dir)

    # Unknown/ambiguous category → blocked
    if cat == TASK_CATEGORY_UNKNOWN:
        return False, "UNKNOWN_OR_AMBIGUOUS task category — blocked"

    return True, "Action route check passed"


# ---------------------------------------------------------------------------
# check_prompt_for_unsafe_instructions
# ---------------------------------------------------------------------------
def check_prompt_for_unsafe_instructions(prompt_text: str) -> dict[str, Any]:
    """Scan prompt text for executable unauthorized mutation instructions.

    Returns a dict with 'pass' (bool), 'violations' (list), and 'quarantine_needed' (bool).
    Advisory/policy sections describing what NOT to do are skipped.
    """
    violations: list[str] = []

    for line in prompt_text.splitlines():
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        # Skip advisory/policy context lines
        if any(marker in line_lower for marker in ADVISORY_SKIP_MARKERS):
            continue
        for pat in UNSAFE_INSTRUCTION_PATTERNS:
            if pat in line_lower:
                violations.append(line.strip()[:120])
                break

    return {
        "check": "no_unauthorized_mutation_instructions",
        "pass": len(violations) == 0,
        "violations": violations[:10],
        "quarantine_needed": len(violations) > 0,
        "detail": f"{len(violations)} unsafe instruction lines" if violations else "clean",
    }


# ---------------------------------------------------------------------------
# quarantine_unsafe_prompt
# ---------------------------------------------------------------------------
def quarantine_unsafe_prompt(
    prompt_text: str,
    reason: str,
    quarantine_dir: Path | None = None,
) -> Path:
    """Write unsafe prompt to quarantine directory. Returns quarantine file path."""
    d = quarantine_dir or (_REPO_ROOT / ".local" / "supervisor" / "quarantine")
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    p = d / f"{ts}-unsafe-prompt.md"
    content = f"# QUARANTINED PROMPT\n\nReason: {reason}\nTimestamp: {ts}\n\n---\n\n{prompt_text}"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# validate_product_mutation_evidence
# ---------------------------------------------------------------------------
def validate_product_mutation_evidence(evidence: dict[str, Any]) -> list[str]:
    """Validate a product mutation route evidence dict against required fields.

    Returns list of errors (empty = valid).
    """
    errors: list[str] = []
    required = [
        "mutation_id", "task_id", "route_decision_id", "authorized_route",
        "allowed_paths_used", "forbidden_paths_checked", "tests_proving_mutation",
    ]
    for field in required:
        if field not in evidence:
            errors.append(f"Missing required field: {field}")
    if evidence.get("allowed_paths_used") is not None and not isinstance(evidence.get("allowed_paths_used"), list):
        errors.append("allowed_paths_used must be a list")
    if evidence.get("tests_proving_mutation") is not None and not isinstance(evidence.get("tests_proving_mutation"), list):
        errors.append("tests_proving_mutation must be a list")
    if evidence.get("tests_proving_mutation") is not None and len(evidence.get("tests_proving_mutation", [])) == 0:
        errors.append("tests_proving_mutation must be non-empty")
    return errors


# ---------------------------------------------------------------------------
# enrich_work_item_with_route — route-aware next-work adapter
# ---------------------------------------------------------------------------
def enrich_work_item_with_route(
    item: dict[str, Any],
    decisions_dir: Path | None = None,
) -> dict[str, Any]:
    """Add route metadata to a next-work/action-queue item.

    If item already has task_category and route_decision_id, validate them.
    If not, classify and decide route, then attach metadata.
    Returns enriched copy (does not mutate original).
    """
    enriched = dict(item)

    # Classify if missing
    if not enriched.get("task_category"):
        summary = enriched.get("task_summary", enriched.get("title", ""))
        action_type = enriched.get("action_type", "")
        enriched["task_category"] = classify_task_category(summary, action_type)

    # Mark advisory if unclassified
    if enriched["task_category"] == TASK_CATEGORY_UNKNOWN:
        enriched["route_status"] = "ADVISORY_ONLY"
        enriched["executable"] = False
        return enriched

    # Decide route if no decision exists
    if not enriched.get("route_decision_id"):
        task_id = enriched.get("task_id", enriched.get("action_id", ""))
        if not task_id:
            enriched["route_status"] = "BLOCKED_NO_TASK_ID"
            enriched["executable"] = False
            return enriched

        decision = decide_route(
            task_id=task_id,
            task_category=enriched["task_category"],
            task_summary=enriched.get("task_summary", enriched.get("title", "")),
            hints={
                "required_tests": enriched.get("required_tests", []),
                "required_evidence": enriched.get("required_evidence", []),
                "allowed_paths": enriched.get("allowed_paths", []),
                "forbidden_paths": enriched.get("forbidden_paths", []),
            },
        )
        decision.write(decisions_dir)
        enriched["route_decision_id"] = task_id
        enriched["route_status"] = decision.decision_status
        enriched["executable"] = not decision.blocked
        enriched["final_route"] = decision.final_route
    else:
        enriched["route_status"] = "PRE_EXISTING"
        enriched["executable"] = True

    return enriched
