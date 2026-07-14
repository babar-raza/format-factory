"""governance_validators_agent_parity.py — Agent parity drift-prevention validators.

TC-ACP-015-01 (FF-AGENTS-PARITY-001, 2026-07-13):
  V183: validate_agent_opt_in_not_default
    — Verify inventory_capabilities.py uses opt-in (codex_supported/kilo_supported),
      not the banned opt-out default (codex_excluded). FAIL if regression detected.

  V184: validate_kilo_column_in_registry
    — Verify all active entries in .governance/capabilities/registry.yaml have
      agent_surfaces.kilo field (added by TC-ACP-002). WARN-only.

  V185: validate_canonical_contract_integrity
    — Verify docs/agents/canonical-agent-contract.yaml covers exactly 22 RC entries
      (RC-001 through RC-022). FAIL if missing.

  V186: validate_agent_bundles_current
    — Verify codex-bundle.yaml and kilo-bundle.yaml are not stale relative to
      .governance/capabilities/registry.yaml (mtime check). WARN-only.
"""

from __future__ import annotations

from pathlib import Path
from governance_validators_contract import validator  # noqa: F401

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@validator(rule_id="V_VALIDATE_AGENT_OPT_IN_NOT_DEFAULT", domain="agent_parity")
def validate_agent_opt_in_not_default(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V183: Verify inventory_capabilities.py uses opt-in (not opt-out) defaults.

    TC-ACP-002 changed codex surface from opt-out (not codex_excluded) to opt-in
    (codex_supported: true). This validator checks the banned opt-out pattern is absent.
    blocks_sprint=True on regression (FAIL).
    """
    repo = repo_root or _REPO_ROOT
    inv_py = repo / "tools" / "capability_sync" / "inventory_capabilities.py"

    if not inv_py.exists():
        return {
            "validator": "V183",
            "result": "WARN",
            "blocks_sprint": False,
            "summary": "V183: inventory_capabilities.py not found — skipping opt-in check",
        }

    source = inv_py.read_text(encoding="utf-8", errors="replace")
    if 'not skill.get("codex_excluded' in source:
        return {
            "validator": "V183",
            "result": "FAIL",
            "blocks_sprint": True,
            "summary": (
                "V183: REGRESSION — opt-out pattern 'not skill.get(\"codex_excluded)' found "
                "in inventory_capabilities.py. TC-ACP-002 requires opt-in (codex_supported). "
                "Fix: replace with 'bool(skill.get(\"codex_supported\", False))'."
            ),
        }

    if "codex_supported" not in source:
        return {
            "validator": "V183",
            "result": "FAIL",
            "blocks_sprint": True,
            "summary": (
                "V183: FAIL — 'codex_supported' not found in inventory_capabilities.py. "
                "TC-ACP-002 requires opt-in field. "
                "Fix: add bool(skill.get('codex_supported', False)) to compute_agent_surfaces."
            ),
        }

    return {
        "validator": "V183",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V183: inventory_capabilities.py uses opt-in (codex_supported) — PASS",
    }


@validator(rule_id="V_VALIDATE_KILO_COLUMN_IN_REGISTRY", domain="agent_parity")
def validate_kilo_column_in_registry(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V184: Verify all active capabilities in registry.yaml have agent_surfaces.kilo field.

    TC-ACP-002 added the kilo field. This validator checks for drift where capabilities
    are added without the kilo field. WARN-only (non-blocking).
    """
    repo = repo_root or _REPO_ROOT
    registry_path = repo / ".governance" / "capabilities" / "registry.yaml"

    if not registry_path.exists():
        return {
            "validator": "V184",
            "result": "WARN",
            "blocks_sprint": False,
            "summary": "V184: .governance/capabilities/registry.yaml not found — skipping",
        }

    try:
        import yaml
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {
            "validator": "V184",
            "result": "WARN",
            "blocks_sprint": False,
            "summary": f"V184: registry.yaml parse error — {exc}",
        }

    missing = []
    for cap in data.get("capabilities", []):
        if cap.get("status") != "active":
            continue
        surfaces = cap.get("agent_surfaces", {})
        if "kilo" not in surfaces:
            missing.append(cap.get("capability_id", "unknown"))

    if missing:
        return {
            "validator": "V184",
            "result": "WARN",
            "blocks_sprint": False,
            "missing_kilo_field": missing,
            "summary": (
                f"V184: {len(missing)} active capability(ies) missing agent_surfaces.kilo field: "
                f"{missing[:5]}{'...' if len(missing) > 5 else ''}. "
                "Fix: re-run inventory_capabilities.py to regenerate registry."
            ),
        }

    return {
        "validator": "V184",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": f"V184: all active capabilities have agent_surfaces.kilo field — PASS",
    }


@validator(rule_id="V_VALIDATE_CANONICAL_CONTRACT_INTEGRITY", domain="agent_parity")
def validate_canonical_contract_integrity(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V185: Verify canonical-agent-contract.yaml covers all 22 RC entries.

    TC-ACP-003 created the contract. This validator checks that it has not been
    corrupted or truncated. FAIL if fewer than 22 RC entries present (blocks sprint).
    """
    repo = repo_root or _REPO_ROOT
    contract_path = repo / "docs" / "agents" / "canonical-agent-contract.yaml"

    if not contract_path.exists():
        return {
            "validator": "V185",
            "result": "FAIL",
            "blocks_sprint": True,
            "summary": (
                "V185: docs/agents/canonical-agent-contract.yaml missing. "
                "TC-ACP-003 requires this file. Run TC-ACP-003 to recreate."
            ),
        }

    try:
        import yaml
        data = yaml.safe_load(contract_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {
            "validator": "V185",
            "result": "FAIL",
            "blocks_sprint": True,
            "summary": f"V185: canonical-agent-contract.yaml parse error — {exc}",
        }

    semantics = data.get("capability_semantics", [])
    count = len(semantics)
    if count < 22:
        found_ids = [e.get("capability_id", "?") for e in semantics if isinstance(e, dict)]
        return {
            "validator": "V185",
            "result": "FAIL",
            "blocks_sprint": True,
            "rc_count": count,
            "summary": (
                f"V185: canonical-agent-contract.yaml has {count} RC entries "
                f"(expected 22). Found: {found_ids}. "
                "Fix: restore all 22 RC entries per TC-ACP-003."
            ),
        }

    return {
        "validator": "V185",
        "result": "PASS",
        "blocks_sprint": False,
        "rc_count": count,
        "summary": f"V185: canonical-agent-contract.yaml has {count} RC entries — PASS",
    }


@validator(rule_id="V_VALIDATE_AGENT_BUNDLES_CURRENT", domain="agent_parity")
def validate_agent_bundles_current(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V186: Verify agent bundles are not stale relative to capability registry.

    codex-bundle.yaml and kilo-bundle.yaml should be regenerated whenever
    .governance/capabilities/registry.yaml changes. WARN if bundles are older.
    blocks_sprint=False (advisory only — bundles are regenerated by run_sync.py).
    """
    repo = repo_root or _REPO_ROOT
    registry_path = repo / ".governance" / "capabilities" / "registry.yaml"
    codex_bundle = repo / "docs" / "agents" / "bundles" / "codex-bundle.yaml"
    kilo_bundle = repo / "docs" / "agents" / "bundles" / "kilo-bundle.yaml"

    if not registry_path.exists():
        return {
            "validator": "V186",
            "result": "WARN",
            "blocks_sprint": False,
            "summary": "V186: registry.yaml not found — skipping bundle freshness check",
        }

    warnings = []
    for bundle_path, agent in [(codex_bundle, "codex"), (kilo_bundle, "kilo")]:
        if not bundle_path.exists():
            warnings.append(f"{agent}-bundle.yaml missing")
            continue
        reg_mtime = registry_path.stat().st_mtime
        bundle_mtime = bundle_path.stat().st_mtime
        if bundle_mtime < reg_mtime:
            warnings.append(
                f"{agent}-bundle.yaml is older than registry.yaml "
                f"(bundle: {bundle_mtime:.0f}, registry: {reg_mtime:.0f}) "
                "— run python tools/capability_sync/run_sync.py to refresh"
            )

    if warnings:
        return {
            "validator": "V186",
            "result": "WARN",
            "blocks_sprint": False,
            "bundle_warnings": warnings,
            "summary": f"V186: {len(warnings)} stale bundle warning(s): {warnings[0]}",
        }

    return {
        "validator": "V186",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V186: all agent bundles are current relative to registry.yaml — PASS",
    }
