"""
Format Factory — Product Action Guard
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
Extended: TC-FF6-EXECUTION-RECOVERY-001 (taskcard-bound authorization, C1)

Guards the orchestrator from executing forbidden product actions.
Classifies product gaps and ensures pilot actions are safe (read-only).
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

from tools.supervisor.forbidden_actions import TRUE_EXTERNAL_GATE_ACTION_TYPES

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent

# Actions absolutely forbidden regardless of context: the canonical
# true-external-gate set, extended with this module's own product-mutation
# path types (not part of the canonical set — these are guard-specific, not
# a second copy of the external-gate list).
FORBIDDEN_ACTION_TYPES = TRUE_EXTERNAL_GATE_ACTION_TYPES | frozenset({
    "MUTATE_PRODUCT_SOURCE",
    "WRITE_TO_SRC",
    "WRITE_TO_TESTS_NET",
    "WRITE_TO_TESTS_PYTHON",
})

# Paths that product pilot actions must never write to
FORBIDDEN_WRITE_PATHS = [
    "src/",
    "tests/net/",
    "tests/python/",
    "registry/",
    "AGENTS.md",
    "GOVERNANCE.md",
    "poc-targets.yaml",
]

# Read-only product actions allowed in pilot
SAFE_PRODUCT_PILOT_ACTIONS = frozenset({
    "READ_POC_TARGETS",
    "READ_GAP_ANALYSIS",
    "CLASSIFY_PRODUCT_GAPS",
    "READ_PRODUCT_STATE",
    "VALIDATE_PRODUCT_EVIDENCE",
    "GENERATE_PRODUCT_REPORT",
    "RUN_JSON_VALIDATION",
    "RUN_YAML_VALIDATION",
    "RUN_MD_NONEMPTY_CHECK",
    "RUN_COMMAND_DISCOVERY",
    "GENERATE_EVIDENCE_STUB",
    "PRODUCT_GAP_CLASSIFICATION_READONLY",
})

# Bounded product-source patch actions (intentionally mutate src/)
# Restricted to FOSS Python source only; src/net/ is always forbidden
BOUNDED_PRODUCT_SOURCE_ACTIONS = frozenset({
    "PRODUCT_SOURCE_PATCH_BOUNDED",
})

# Paths allowed as targets for PRODUCT_SOURCE_PATCH_BOUNDED
ALLOWED_PRODUCT_SOURCE_PATCH_PATHS = [
    "src/python/abw/",
    "src/python/gnumeric/",
    "src/python/zst/",
    "src/python/sylk/",
    "src/python/dif/",
    "src/python/pbm/",
    "src/python/pgm/",
    "src/python/ppm/",
]

# The six FF6 product roots a live taskcard is permitted to declare ownership
# over (TC-FF6-EXECUTION-RECOVERY-001, design C1). A taskcard may authorize
# any exact path under these roots; it may never authorize a path outside them.
FF6_GOVERNED_PRODUCT_ROOTS = [
    "src/python/ipynb/",
    "src/python/openraster/",
    "src/python/nrrd/",
    "src/python/xliff/",
    "src/python/safetensors/",
    "src/python/ubl/",
    "tests/python/ipynb/",
    "tests/python/openraster/",
    "tests/python/nrrd/",
    "tests/python/xliff/",
    "tests/python/safetensors/",
    "tests/python/ubl/",
]

# Roots a taskcard's "Exact writable paths" section can never authorize, even
# if it declares them explicitly. Controller, registry, promotion, release,
# and governance state remain fail-closed regardless of taskcard content.
ALWAYS_FORBIDDEN_TASKCARD_ROOTS = [
    "plans/strategic/ff6/events.jsonl",
    "plans/strategic/ff6/controller-state.yaml",
    "registry/",
    "AGENTS.md",
    "GOVERNANCE.md",
    "poc-targets.yaml",
    ".git/",
]

# Taskcard statuses that must never authorize a write (task is closed/expired).
_TASKCARD_TERMINAL_STATUSES = {"CLOSED", "SUPERSEDED", "CANCELLED", "TERMINAL_CLOSED"}


class TaskAuthorizationError(Exception):
    """Raised when a taskcard cannot authorize the requested path."""


def _default_taskcards_dir() -> Path:
    return _repo_root / "taskcards"


def _parse_frontmatter_status(text: str) -> Optional[str]:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("status:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _extract_section(text: str, heading: str) -> Optional[str]:
    idx = text.find(heading)
    if idx == -1:
        return None
    rest = text[idx + len(heading):]
    next_idx = rest.find("\n## ")
    return rest[:next_idx] if next_idx != -1 else rest


def _extract_backtick_paths(section_body: str) -> List[str]:
    paths: List[str] = []
    for line in section_body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        entry = stripped.lstrip("-").strip()
        while entry.startswith("`"):
            end_tick = entry.find("`", 1)
            if end_tick == -1:
                break
            paths.append(entry[1:end_tick])
            entry = entry[end_tick + 1:].lstrip()
            if entry.startswith(","):
                entry = entry[1:].lstrip()
            else:
                break
    return paths


def _normalize_declared_path(raw: str) -> Optional[str]:
    """Reject traversal/absolute entries. Return a normalized repo-relative
    path (directory entries keep a trailing '/')."""
    if not raw:
        return None
    posix_raw = raw.replace("\\", "/")
    if ".." in PurePosixPath(posix_raw).parts:
        return None
    p = PurePosixPath(posix_raw)
    if p.is_absolute():
        return None
    normalized = str(p)
    if posix_raw.endswith("/"):
        normalized += "/"
    return normalized


def load_taskcard_authorized_paths(
    task_id: str,
    taskcards_dir: Optional[Path] = None,
) -> List[str]:
    """Parse a taskcard's '## Exact writable paths' section into normalized,
    repo-root-relative path prefixes it may mutate.

    Raises TaskAuthorizationError if the taskcard is missing, has no such
    section, or is closed/superseded/cancelled.
    """
    taskcards_dir = taskcards_dir or _default_taskcards_dir()
    card_path = taskcards_dir / f"{task_id}.md"
    if not card_path.exists():
        raise TaskAuthorizationError(f"taskcard not found: {task_id}")

    text = card_path.read_text(encoding="utf-8")
    status = _parse_frontmatter_status(text)
    if status in _TASKCARD_TERMINAL_STATUSES:
        raise TaskAuthorizationError(f"taskcard {task_id} is {status}; cannot authorize writes")

    # Observed taskcard convention is inconsistent in practice: control-repair
    # taskcards head this section "## Exact writable paths" while product
    # taskcards (e.g. TC-FF6-NRRD-GOLDEN-SLICE-001) head it "## Exact
    # writable product paths". Accept either rather than silently
    # authorizing nothing for a well-formed taskcard.
    section = _extract_section(text, "## Exact writable paths")
    if section is None:
        section = _extract_section(text, "## Exact writable product paths")
    if section is None:
        raise TaskAuthorizationError(
            f"taskcard {task_id} has no 'Exact writable paths' / "
            "'Exact writable product paths' section"
        )

    declared = _extract_backtick_paths(section)
    normalized: List[str] = []
    for raw in declared:
        norm = _normalize_declared_path(raw)
        if norm is not None:
            normalized.append(norm)
    return normalized


def is_path_authorized_for_task(
    target_path: str,
    task_id: str,
    taskcards_dir: Optional[Path] = None,
) -> bool:
    """True iff `target_path` is inside FF6_GOVERNED_PRODUCT_ROOTS, is not in
    ALWAYS_FORBIDDEN_TASKCARD_ROOTS, and is explicitly declared (exact match
    or under a declared directory prefix) by the live, non-terminal taskcard
    `task_id`."""
    norm_target = (target_path or "").replace("\\", "/")
    if not norm_target:
        return False

    for forbidden in ALWAYS_FORBIDDEN_TASKCARD_ROOTS:
        if norm_target == forbidden or norm_target.startswith(forbidden):
            return False

    if not any(norm_target.startswith(root) for root in FF6_GOVERNED_PRODUCT_ROOTS):
        return False

    try:
        authorized = load_taskcard_authorized_paths(task_id, taskcards_dir)
    except TaskAuthorizationError:
        return False

    for allowed in authorized:
        if allowed == norm_target:
            return True
        if allowed.endswith("/") and norm_target.startswith(allowed):
            return True
    return False


class GuardViolation(Exception):
    """Raised when an action violates product safety rules."""
    def __init__(self, action_type: str, reason: str):
        self.action_type = action_type
        self.reason = reason
        super().__init__(f"GUARD_VIOLATION [{action_type}]: {reason}")


def _authorize_patch_target(target: str, task_id: Optional[str], action_type: str) -> None:
    """Raise GuardViolation unless `target` is an authorized
    PRODUCT_SOURCE_PATCH_BOUNDED write target. Shared by the primary target
    and every also_modify secondary target so neither can bypass the other."""
    if not target:
        raise GuardViolation(action_type, "PRODUCT_SOURCE_PATCH_BOUNDED requires target_path")

    allowed = False
    if task_id:
        allowed = is_path_authorized_for_task(target, task_id)
    if not allowed:
        allowed = any(target.startswith(p) for p in ALLOWED_PRODUCT_SOURCE_PATCH_PATHS)
    if not allowed:
        raise GuardViolation(
            action_type,
            f"target_path '{target}' not authorized (no taskcard grant, not in "
            "ALLOWED_PRODUCT_SOURCE_PATCH_PATHS)"
        )
    if target.startswith("src/net/"):
        raise GuardViolation(action_type, "src/net/ is forbidden for bounded product patches")


def is_action_safe(action: Dict[str, Any]) -> bool:
    """Return True if the action passes all product safety checks."""
    try:
        check_action(action)
        return True
    except GuardViolation:
        return False


def check_action(action: Dict[str, Any]) -> None:
    """Raise GuardViolation if the action is not safe to execute.

    Checks:
    1. action_type not in FORBIDDEN_ACTION_TYPES
    2. target_path (if any) does not write to forbidden paths
    3. external_gate must be False
    4. PRODUCT_SOURCE_PATCH_BOUNDED: target must be in ALLOWED_PRODUCT_SOURCE_PATCH_PATHS
    """
    action_type = action.get("action_type", "UNKNOWN")

    if action_type in FORBIDDEN_ACTION_TYPES:
        raise GuardViolation(action_type, "action_type is in FORBIDDEN_ACTION_TYPES")

    target_path = action.get("target_path", "")
    if target_path:
        for forbidden in FORBIDDEN_WRITE_PATHS:
            if target_path.startswith(forbidden) or ("/" + forbidden) in target_path:
                # Only block write-type actions (except bounded patch — has its own check)
                if action_type not in BOUNDED_PRODUCT_SOURCE_ACTIONS:
                    write_actions = {"WRITE_", "MUTATE_", "EDIT_", "DELETE_", "PATCH_"}
                    if any(action_type.startswith(w) for w in write_actions):
                        raise GuardViolation(
                            action_type,
                            f"target_path '{target_path}' is in forbidden write path '{forbidden}'"
                        )

    # PRODUCT_SOURCE_PATCH_BOUNDED: target must be authorized either by a live
    # taskcard's exact-path declaration (task_id present, C1) or by the
    # legacy hard-coded FOSS Python allowlist (no task_id — backward compat).
    if action_type in BOUNDED_PRODUCT_SOURCE_ACTIONS:
        target = target_path or action.get("target", "")
        task_id = action.get("task_id")
        _authorize_patch_target(target, task_id, action_type)

    external_gate = action.get("external_gate", False)
    if external_gate:
        raise GuardViolation(action_type, "external_gate=True — requires human operator")


def classify_product_gaps(poc_targets_path: Optional[Path] = None) -> Dict[str, Any]:
    """Read poc-targets.yaml and classify gaps into autonomous vs external-gate.

    Returns a classification dict without mutating any file.
    """
    if poc_targets_path is None:
        poc_targets_path = _repo_root / "poc-targets.yaml"

    if not poc_targets_path.exists():
        return {
            "status": "POC_TARGETS_NOT_FOUND",
            "autonomous_gaps": [],
            "external_gate_gaps": [],
            "commercial_ready": [],
        }

    try:
        import yaml  # type: ignore
        raw = yaml.safe_load(poc_targets_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": f"PARSE_ERROR: {exc}",
            "autonomous_gaps": [],
            "external_gate_gaps": [],
            "commercial_ready": [],
        }

    targets = raw.get("targets", []) if isinstance(raw, dict) else []

    autonomous_gaps: List[Dict[str, Any]] = []
    external_gate_gaps: List[Dict[str, Any]] = []
    commercial_ready: List[Dict[str, Any]] = []

    for target in targets:
        tid = target.get("id", "UNKNOWN")
        gate11 = target.get("gate_11_status", "")
        commercial = target.get("commercial_product_ready", False)

        if commercial and gate11 == "APPROVED":
            commercial_ready.append({"id": tid, "gate_11_status": gate11})
        elif gate11 in ("APPROVED", "PENDING_PUBLICATION"):
            external_gate_gaps.append({"id": tid, "gate_11_status": gate11, "note": "Needs publish/push"})
        else:
            blockers = target.get("blockers", [])
            if blockers:
                external_gate_gaps.append({"id": tid, "blockers": blockers})
            else:
                autonomous_gaps.append({"id": tid})

    return {
        "status": "CLASSIFIED",
        "total_targets": len(targets),
        "autonomous_gaps": autonomous_gaps,
        "external_gate_gaps": external_gate_gaps,
        "commercial_ready": commercial_ready,
        "autonomous_gaps_count": len(autonomous_gaps),
        "external_gate_count": len(external_gate_gaps),
        "commercial_ready_count": len(commercial_ready),
    }


def generate_product_pilot_actions(classification: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate safe read-only pilot actions based on gap classification.

    Returns a list of action dicts (all SAFE_PRODUCT_PILOT_ACTIONS, no writes to src/).
    """
    actions = []

    # Always validate gap analysis JSON
    actions.append({
        "action_type": "RUN_JSON_VALIDATION",
        "target_path": "reports/autonomous-system-acceptance/current-gap-analysis.json",
        "description": "Validate current-gap-analysis.json is well-formed",
        "external_gate": False,
        "preferred_backend": "LOCAL_DETERMINISTIC",
    })

    # Read and classify product state
    actions.append({
        "action_type": "CLASSIFY_PRODUCT_GAPS",
        "target_path": "poc-targets.yaml",
        "description": "Classify product gaps: autonomous vs external-gate",
        "external_gate": False,
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "pilot_classification": classification,
    })

    # Validate product pilot report once it exists
    actions.append({
        "action_type": "RUN_MD_NONEMPTY_CHECK",
        "target_path": "reports/autonomous-system-acceptance/00-preflight.md",
        "description": "Verify sprint preflight document is non-empty",
        "external_gate": False,
        "preferred_backend": "LOCAL_DETERMINISTIC",
    })

    return actions


def write_product_gap_classification(
    classification: Dict[str, Any],
    output_path: Optional[Path] = None,
) -> Path:
    """Write gap classification JSON to reports directory."""
    if output_path is None:
        output_path = _repo_root / "reports" / "autonomous-system-acceptance" / "product-pilot" / "product-gap-classification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(classification, indent=2), encoding="utf-8")
    return output_path


def run_product_gap_classification_readonly(
    output_path: Optional[Path] = None,
    poc_targets_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Execute PRODUCT_GAP_CLASSIFICATION_READONLY action.

    Reads poc-targets.yaml and product reports (read-only).
    Classifies each gap with a machine-readable category.
    Writes JSON output. Never mutates any product file.
    """
    if output_path is None:
        output_path = _repo_root / "reports" / "h6-queue-product-loop" / "product-pilot" / "product-gap-classification.json"

    # Step 1: classify gaps from poc-targets.yaml
    classification = classify_product_gaps(poc_targets_path)

    # Step 2: build detailed classification with categories
    detailed: List[Dict[str, Any]] = []

    poc_path = poc_targets_path or (_repo_root / "poc-targets.yaml")
    if poc_path.exists():
        try:
            import yaml  # type: ignore
            raw = yaml.safe_load(poc_path.read_text(encoding="utf-8"))
            targets = raw.get("targets", []) if isinstance(raw, dict) else []
        except Exception:
            targets = []
    else:
        targets = []

    for target in targets[:6]:  # limit to 6 for bounded execution
        tid = target.get("id", "UNKNOWN")
        commercial = target.get("commercial_product_ready", False)
        gate11 = target.get("gate_11_status", "")
        blockers = target.get("blockers", [])

        if commercial and gate11 == "APPROVED":
            category = "true_external_gate"
            reason = "Gate 11 approved — pending publication authorization"
            next_action = "AWAIT_GATE_11_PUBLICATION"
        elif gate11 in ("PENDING_APPROVAL", "PENDING"):
            category = "true_external_gate"
            reason = f"gate_11_status={gate11} — requires human approval"
            next_action = "AWAIT_GATE_11_APPROVAL"
        elif blockers:
            category = "blocked_external"
            reason = f"blockers: {', '.join(str(b) for b in blockers)}"
            next_action = "RESOLVE_BLOCKER"
        elif not commercial:
            category = "agent_owned_safe"
            reason = "Not yet commercial-ready — agent can pursue further implementation"
            next_action = "CONTINUE_IMPLEMENTATION_SPRINT"
        else:
            category = "requires_product_source_mutation"
            reason = "Requires src/ changes — not safe for read-only pilot"
            next_action = "SCHEDULE_PRODUCT_SOURCE_SPRINT"

        detailed.append({
            "id": tid,
            "category": category,
            "reason": reason,
            "next_action": next_action,
            "commercial_product_ready": commercial,
            "gate_11_status": gate11,
        })

    result = {
        "schema_version": 1,
        "action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY",
        "status": "SUCCESS",
        "generated_at": _now_iso(),
        "classification_summary": classification,
        "detailed_classification": detailed,
        "total_classified": len(detailed),
        "agent_owned_safe_count": sum(1 for d in detailed if d["category"] == "agent_owned_safe"),
        "external_gate_count": sum(1 for d in detailed if d["category"] == "true_external_gate"),
        "blocked_external_count": sum(1 for d in detailed if d["category"] == "blocked_external"),
        "forbidden_write_paths": FORBIDDEN_WRITE_PATHS,
        "product_source_mutated": False,
        "poc_targets_mutated": False,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run_product_source_patch_bounded(
    action: Dict[str, Any],
    allowed_write_roots: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Execute PRODUCT_SOURCE_PATCH_BOUNDED action.

    Applies a bounded addition (function add, import update) to a single
    FOSS Python source file. Validates target is in ALLOWED_PRODUCT_SOURCE_PATCH_PATHS.
    Captures the before-state for rollback.

    action must contain:
        target_path: str — the Python source file to modify
        patch_type: str — "add_function" or "add_export"
        patch_code: str — the code to insert
        insert_before: str (optional) — insert before this anchor string
        also_modify: list[dict] (optional) — additional files to update

    Returns result dict with product_source_mutated=True on success.
    """
    action_type = action.get("action_type", "PRODUCT_SOURCE_PATCH_BOUNDED")
    task_id = action.get("task_id", action.get("action_id", "unknown"))
    target_path_str = action.get("target_path", "")
    patch_type = action.get("patch_type", "add_function")
    patch_code = action.get("patch_code", "")
    insert_before = action.get("insert_before")
    also_modify = action.get("also_modify", [])
    result_path_str = action.get("result_path", "")

    # Guard check
    check_action(action)

    target_path = _repo_root / target_path_str
    if not target_path.exists():
        return {
            "action_type": action_type,
            "status": "FAILED",
            "error": f"target_path not found: {target_path_str}",
            "product_source_mutated": False,
        }

    # Capture before-state for rollback
    original_content = target_path.read_text(encoding="utf-8")

    try:
        if patch_type == "add_function" and patch_code:
            if insert_before and insert_before in original_content:
                new_content = original_content.replace(
                    insert_before,
                    patch_code + "\n\n" + insert_before,
                    1,
                )
            else:
                # Append to end of file
                new_content = original_content.rstrip() + "\n\n" + patch_code + "\n"
            target_path.write_text(new_content, encoding="utf-8")

        elif patch_type == "add_export" and patch_code:
            new_content = original_content.rstrip() + "\n" + patch_code + "\n"
            target_path.write_text(new_content, encoding="utf-8")

        else:
            return {
                "action_type": action_type,
                "status": "FAILED",
                "error": f"unsupported patch_type: {patch_type}",
                "product_source_mutated": False,
            }

        # Apply also_modify patches. Each secondary target must clear the same
        # authorization as the primary target — also_modify is not a path-
        # validation bypass (TC-FF6-EXECUTION-RECOVERY-001, defect 4).
        also_modified = []
        for mod in also_modify:
            mod_target_str = mod.get("target_path", "")
            _authorize_patch_target(mod_target_str, action.get("task_id"), action_type)
            mod_path = _repo_root / mod_target_str
            if mod_path.exists():
                mod_orig = mod_path.read_text(encoding="utf-8")
                mod_patch_type = mod.get("patch_type", "add_export")
                mod_patch_code = mod.get("patch_code", "")
                mod_insert_before = mod.get("insert_before")
                if mod_patch_type == "add_function" and mod_patch_code:
                    if mod_insert_before and mod_insert_before in mod_orig:
                        mod_new = mod_orig.replace(mod_insert_before, mod_patch_code + "\n\n" + mod_insert_before, 1)
                    else:
                        mod_new = mod_orig.rstrip() + "\n\n" + mod_patch_code + "\n"
                    mod_path.write_text(mod_new, encoding="utf-8")
                elif mod_patch_type == "add_export" and mod_patch_code:
                    mod_new = mod_orig.rstrip() + "\n" + mod_patch_code + "\n"
                    mod_path.write_text(mod_new, encoding="utf-8")
                also_modified.append(str(mod.get("target_path", "")))

        result = {
            "schema_version": 1,
            "action_type": action_type,
            "task_id": task_id,
            "status": "SUCCESS",
            "generated_at": _now_iso(),
            "target_path": target_path_str,
            "patch_type": patch_type,
            "also_modified": also_modified,
            "product_source_mutated": True,
            "poc_targets_mutated": False,
            "rollback_instruction": f"git checkout HEAD -- {target_path_str}" + (
                " " + " ".join(also_modified) if also_modified else ""
            ),
            "before_length": len(original_content),
            "after_length": len(target_path.read_text(encoding="utf-8")),
        }

        if result_path_str:
            rp = Path(result_path_str) if Path(result_path_str).is_absolute() else _repo_root / result_path_str
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(result, indent=2), encoding="utf-8")
            result["result_path"] = result_path_str

        return result

    except Exception as exc:
        # Rollback on failure
        target_path.write_text(original_content, encoding="utf-8")
        return {
            "action_type": action_type,
            "status": "FAILED",
            "error": str(exc),
            "product_source_mutated": False,
            "rollback_applied": True,
        }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
