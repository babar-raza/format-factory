"""
format_context_resolver.py -- Safe R2 Scaffolding (Lane E)

Authoritative state-resolution layer for the format-factory skill system.

PURPOSE:
  Read registry, acquisition pack, and generated-requirements state for a given format.
  Return a structured context block indicating the format's implementation readiness.
  This is the authoritative source of truth for capability state consumed by lane selection,
  prompt generation, and sprint planning tools.

STATE MACHINE OUTPUT:
  REQUIREMENTS_MISSING          -- no generated-requirements/{format_id}/ directory
  REQUIREMENTS_GENERATED_UNVERIFIED -- files exist but no verifier-review.yaml or result != LANE_R5_PASS
  REQUIREMENTS_VERIFIED_NO_IV   -- LANE_R5_PASS but DEC-034 IV status is PENDING or not recorded
  REQUIREMENTS_AUTHORITATIVE    -- LANE_R5_PASS + DEC-034 IV PASS -- ready for implementation prompts
  BLOCKED                       -- gate not passed, DEC-033 unresolved, or other blocker

ALLOWED:
  - Registry reading
  - Format discovery
  - Capability-state reading
  - Requirements-state reading
  - Stale metadata placeholder support

NOT ALLOWED (governance boundary):
  - Autonomous execution
  - Prompt generation
  - Implementation orchestration
  - AI execution
  - Mutation outside local analysis
  - Gate self-approval

Authority: AGENTS.md Section B, D, AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"
REQS_DIR = REPO_ROOT / "generated-requirements"

# Required requirements files for a complete requirements set
REQUIRED_REQUIREMENTS_FILES = [
    "commercial-requirements.yaml",
    "object-model-requirements.yaml",
    "save-edit-requirements.yaml",
    "conversion-requirements.yaml",
    "traceability-map.yaml",
    "verifier-review.yaml",
]


def _load_yaml(path: Path) -> dict:
    """Load YAML file safely. Returns empty dict on failure."""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise ImportError("PyYAML required: pip install pyyaml")
    except Exception:
        return {}


def _resolve_requirements_state(fmt: str, registry_iv_override: str | None = None) -> dict:
    """
    Resolve the requirements state machine for a format.

    Returns a dict with:
      status: str   (one of the state machine values)
      iv_status: str | None
      verifier_result: str | None
      accepted_count: int | None
      missing_files: list[str]
      stale: None   (stale detection deferred -- GOVERNANCE.md 26.11)
      blocker_reason: str | None

    registry_iv_override: iv_status sourced from registry/format-registry.yaml
      generated_requirements.iv_status (ESTABLISHED normalized to PASS).
      Used as tertiary source after commercial-requirements.yaml and verifier-review.yaml.
    """
    fmt_dir = REQS_DIR / fmt

    if not fmt_dir.exists():
        return {
            "status": "REQUIREMENTS_MISSING",
            "iv_status": None,
            "verifier_result": None,
            "accepted_count": None,
            "missing_files": list(REQUIRED_REQUIREMENTS_FILES),
            "stale": None,
            "blocker_reason": f"generated-requirements/{fmt}/ does not exist",
        }

    missing = [f for f in REQUIRED_REQUIREMENTS_FILES if not (fmt_dir / f).exists()]
    if missing:
        return {
            "status": "REQUIREMENTS_GENERATED_UNVERIFIED",
            "iv_status": None,
            "verifier_result": None,
            "accepted_count": None,
            "missing_files": missing,
            "stale": None,
            "blocker_reason": f"Missing required files: {missing}",
        }

    # All files present -- read verifier review
    vr_data = _load_yaml(fmt_dir / "verifier-review.yaml")
    verdict = vr_data.get("verifier_verdict", {})
    verifier_result = verdict.get("result")

    if verifier_result != "LANE_R5_PASS":
        return {
            "status": "REQUIREMENTS_GENERATED_UNVERIFIED",
            "iv_status": None,
            "verifier_result": verifier_result,
            "accepted_count": None,
            "missing_files": [],
            "stale": None,
            "blocker_reason": f"verifier_verdict.result={verifier_result!r} -- LANE_R5_PASS required",
        }

    # Verifier passed -- check DEC-034 IV status
    # Source priority: commercial-requirements.yaml → verifier-review.yaml → registry (authoritative fallback)
    cr_data = _load_yaml(fmt_dir / "commercial-requirements.yaml")
    iv_status = cr_data.get("iv_status") or vr_data.get("iv_status") or registry_iv_override

    # Count accepted requirements
    accepted = 0
    try:
        for fname in ["commercial-requirements.yaml", "save-edit-requirements.yaml"]:
            fdata = _load_yaml(fmt_dir / fname)
            accepted += sum(
                1 for r in fdata.get("requirements", [])
                if r.get("status") == "ACCEPTED_FOR_VERTICAL_SLICE"
            )
    except Exception:
        accepted = None

    # DEC-034 IV state
    if iv_status is None or iv_status == "PENDING":
        return {
            "status": "REQUIREMENTS_VERIFIED_NO_IV",
            "iv_status": iv_status,
            "verifier_result": verifier_result,
            "accepted_count": accepted,
            "missing_files": [],
            "stale": None,
            "blocker_reason": "DEC-034 IV not yet completed -- separate session required (AGENTS.md AF13)",
        }

    if iv_status == "FAIL":
        return {
            "status": "BLOCKED",
            "iv_status": "FAIL",
            "verifier_result": verifier_result,
            "accepted_count": accepted,
            "missing_files": [],
            "stale": None,
            "blocker_reason": "DEC-034 IV FAIL -- requirements not authoritative; see IV report",
        }

    # iv_status == "PASS" -- AUTHORITATIVE
    return {
        "status": "REQUIREMENTS_AUTHORITATIVE",
        "iv_status": "PASS",
        "verifier_result": verifier_result,
        "accepted_count": accepted,
        "missing_files": [],
        "stale": None,
        "blocker_reason": None,
    }


def _resolve_gate_state(fmt: str) -> dict:
    """Read gate state from registry/format-registry.yaml."""
    if not REGISTRY_PATH.exists():
        return {
            "gates_passed": 0,
            "latest_gate_passed": None,
            "commercial_product_ready": False,
            "gate_11_status": None,
            "blocker": "registry/format-registry.yaml not found",
        }

    try:
        import yaml
        registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "gates_passed": 0,
            "latest_gate_passed": None,
            "commercial_product_ready": False,
            "gate_11_status": None,
            "blocker": "Failed to load registry",
        }

    formats_raw = registry.get("formats", [])
    # Registry formats may be a list of dicts or a dict — handle both
    if isinstance(formats_raw, list):
        fmt_entry = next((f for f in formats_raw if f.get("format_id") == fmt), {})
    else:
        fmt_entry = formats_raw.get(fmt, {})
    if not fmt_entry:
        return {
            "gates_passed": 0,
            "latest_gate_passed": None,
            "commercial_product_ready": False,
            "gate_11_status": None,
            "blocker": f"Format {fmt!r} not found in registry",
        }

    gates = fmt_entry.get("gates", {})
    passed = sum(1 for g in gates.values() if isinstance(g, dict) and g.get("status") == "passed")
    latest = max(
        (int(k.replace("gate_", "")) for k, v in gates.items()
         if isinstance(v, dict) and v.get("status") == "passed"),
        default=None,
    )
    gate_11 = gates.get("gate_11", {})
    gate_11_status = gate_11.get("status") if isinstance(gate_11, dict) else None

    return {
        "gates_passed": passed,
        "latest_gate_passed": latest,
        "commercial_product_ready": False,  # MUST remain false until human approves Gate 11
        "gate_11_status": gate_11_status,
        "blocker": None,
    }


def _collect_known_constraints(fmt: str) -> list:
    """
    Collect critical implementation constraints from verifier review and traceability map.
    These MUST surface in every implementation prompt for this format.
    """
    fmt_dir = REQS_DIR / fmt
    constraints = []

    vr_path = fmt_dir / "verifier-review.yaml"
    if vr_path.exists():
        vr_data = _load_yaml(vr_path)
        verdict = vr_data.get("verifier_verdict", {})
        auth = verdict.get("implementation_authorization", {})
        constraint = auth.get("critical_constraint")
        if constraint:
            constraints.append({"source": "verifier_review", "constraint": constraint})

    tm_path = fmt_dir / "traceability-map.yaml"
    if tm_path.exists():
        tm_data = _load_yaml(tm_path)
        for entry in tm_data.get("critical_requirements", []):
            if isinstance(entry, dict):
                for req_id, desc in entry.items():
                    constraints.append({
                        "requirement_id": req_id,
                        "constraint": desc,
                        "source": "traceability_map",
                    })

    return constraints


def resolve_format_context(fmt: str, verbose: bool = False) -> dict:
    """
    Resolve the complete format context for skill consumption.

    Returns a structured context dict suitable for:
    - Lane selection (Phase R3)
    - Prompt generation (Phase R4)
    - Sprint planning
    - CI readiness checks

    This function is READ-ONLY. It does not modify any files.
    """
    # Load registry iv_status as authoritative fallback (CONWAY-R2R3 Lane A)
    # registry/format-registry.yaml generated_requirements.iv_status: ESTABLISHED → normalized to PASS
    registry_iv_override = None
    try:
        import yaml as _yaml
        _registry = _yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        _formats = _registry.get("formats", [])
        _entry = (
            next((f for f in _formats if f.get("format_id") == fmt), {})
            if isinstance(_formats, list)
            else _formats.get(fmt, {})
        )
        _reg_iv = _entry.get("generated_requirements", {}).get("iv_status")
        if _reg_iv == "ESTABLISHED":
            registry_iv_override = "PASS"
        elif _reg_iv in ("PASS", "FAIL", "PENDING"):
            registry_iv_override = _reg_iv
    except Exception:
        pass

    reqs_state = _resolve_requirements_state(fmt, registry_iv_override=registry_iv_override)
    gate_state = _resolve_gate_state(fmt)
    constraints = _collect_known_constraints(fmt)

    # Stale detection (CONWAY-R7R8 Lane A) — populate the 'stale' field
    try:
        sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))
        from stale_detection import detect_stale_state as _detect_stale
        stale_result = _detect_stale(fmt)
        reqs_state["stale"] = stale_result
    except Exception:
        reqs_state["stale"] = {"verdict": "INDETERMINATE", "reasons": ["stale_detection unavailable"], "checks": {}, "blocker_count": 0}

    context = {
        "format_id": fmt,
        "resolver_version": "1.0",
        "requirements_state": reqs_state,
        "gate_state": gate_state,
        "known_constraints": constraints,
        "governance": {
            "authority_files": [
                "AGENTS.md", "GOVERNANCE.md",
                "plans/master-plan.md", "registry/format-registry.yaml",
            ],
            "commercial_product_ready": False,
            "gate_self_approval_allowed": False,
            "autonomous_implementation_allowed": False,
        },
    }

    if verbose:
        import json
        print(json.dumps(context, indent=2))

    return context


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Format context resolver -- read-only state resolution for format-factory skills"
    )
    parser.add_argument("format", nargs="?", default="all", help="Format ID (fods, fodt) or all")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]

    for fmt in formats:
        ctx = resolve_format_context(fmt, verbose=False)
        reqs = ctx["requirements_state"]
        gates = ctx["gate_state"]

        if args.json:
            import json
            print(json.dumps(ctx, indent=2))
            continue

        print(f"\n=== Format Context: {fmt.upper()} ===")
        print(f"  REQUIREMENTS_STATE:  {reqs['status']}")
        print(f"  VERIFIER_RESULT:     {reqs.get('verifier_result', 'N/A')}")
        print(f"  IV_STATUS:           {reqs.get('iv_status', 'N/A')}")
        print(f"  ACCEPTED_COUNT:      {reqs.get('accepted_count', 'N/A')}")
        print(f"  GATES_PASSED:        {gates['gates_passed']}")
        print(f"  GATE_11_STATUS:      {gates.get('gate_11_status', 'N/A')}")
        print(f"  COMMERCIAL_READY:    {gates['commercial_product_ready']}")
        if reqs.get("blocker_reason"):
            print(f"  BLOCKER:             {reqs['blocker_reason']}")
        if ctx["known_constraints"]:
            print(f"  CRITICAL_CONSTRAINTS: {len(ctx['known_constraints'])} constraint(s)")
            for c in ctx["known_constraints"]:
                rid = c.get("requirement_id", "GLOBAL")
                print(f"    - {rid}: {c.get('constraint', '')[:80]}")


if __name__ == "__main__":
    main()
