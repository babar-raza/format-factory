"""Integration + adversarial + regression tests — Skills-First Control.

- Integration: full resolve -> manifest -> closeout flow over the REAL registries.
- Regression: the healed control state stays green (no CRITICAL, validator not FAIL).
- Adversarial: registries fail closed on malformed input; invalid/expired exceptions
  cannot launder a finding; the gate cannot be passed by naming a skill alone.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance import validate_skills_first_control as V  # noqa: E402
from tools.governance.skills_first import audit as A  # noqa: E402
from tools.governance.skills_first import closeout as C  # noqa: E402
from tools.governance.skills_first import exceptions as X  # noqa: E402
from tools.governance.skills_first import manifest as M  # noqa: E402
from tools.governance.skills_first import registries as REG  # noqa: E402
from tools.governance.skills_first import resolve as R  # noqa: E402


# ── integration: full governed flow ────────────────────────────────────────

def test_full_resolve_manifest_closeout_flow():
    res = R.resolve("run governance validators", ["tools/governance/x.py"])
    assert res["verdict"] == "RESOLVED"
    m = M.create_manifest(
        task_id="TC-INT-001", agent_type="CLAUDE_CODE",
        requested_operation="integration flow",
        selected_skill_ids=[res["selected_skill_id"]],
        allowed_paths=["tools/governance/skills_first/**"],
        resolution_decision=res["resolution_decision"], write=False)
    # in-scope change WITH evidence -> closeable
    out = C.evaluate(m, ["tools/governance/skills_first/manifest.py"],
                     evidence_paths=["tools/governance/skills_first/manifest.py"])
    assert out["verdict"] == "CLOSE_OK", out["reasons"]


# ── regression: healed state stays green ───────────────────────────────────

def test_audit_has_no_critical_findings():
    report = A.run_audit(scan_generators=False)
    assert report["severity_counts"]["CRITICAL"] == 0
    assert report["counts"]["skills_active"] > 100
    assert report["counts"]["commands_registered"] > 100


def test_control_validator_not_failing():
    result = V.run(warn_high=False)
    assert result["verdict"] in ("PASS", "PASS_WITH_WARNINGS"), result


def test_two_healed_commands_are_governed_now():
    report = A.run_audit(scan_generators=False)
    owner_less = [f["file"] for f in report["findings"]
                  if f.get("category") == "unregistered_command_md"]
    assert ".claude/commands/fix-exception-hierarchy.md" not in owner_less
    assert ".claude/commands/wire-analytics-module.md" not in owner_less


# ── adversarial: registries fail CLOSED on malformed input ─────────────────

def test_registry_loader_fails_closed_on_malformed_yaml(tmp_path, monkeypatch):
    bad = tmp_path / "skills.yaml"
    bad.write_text("skills: [ this is : : broken", encoding="utf-8")
    monkeypatch.setattr(REG, "SKILL_REGISTRY", bad)
    with pytest.raises(REG.RegistryError):
        REG.load_skills()


def test_registry_loader_fails_closed_on_non_mapping_top_level(tmp_path, monkeypatch):
    bad = tmp_path / "skills.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    monkeypatch.setattr(REG, "SKILL_REGISTRY", bad)
    with pytest.raises(REG.RegistryError):
        REG.load_skills()


def test_audit_propagates_config_error_not_clean_pass(tmp_path, monkeypatch):
    bad = tmp_path / "cmd.yaml"
    bad.write_text("commands: not-a-list\n", encoding="utf-8")
    monkeypatch.setattr(REG, "COMMAND_REGISTRY", bad)
    with pytest.raises(REG.RegistryError):
        A.run_audit(scan_generators=False)


# ── adversarial: invalid/expired exceptions cannot launder a finding ───────

def test_expired_exception_does_not_cover_signature(tmp_path, monkeypatch):
    store = tmp_path / "acc.yaml"
    store.write_text(
        "exceptions:\n"
        "  - exception_id: E1\n"
        "    finding_signature: 'unregistered_command_md::.claude/commands/x.md'\n"
        "    severity: HIGH\n"
        "    owner: babar-raza\n"
        "    reason: awaiting window\n"
        "    remediation_task: TC-1\n"
        "    created: '2026-07-01'\n"
        "    expires: '2000-01-01'\n"       # expired
        "    compensating_control: closeout gate\n",
        encoding="utf-8")
    monkeypatch.setattr(X, "STORE", store)
    valid, invalid = X.active_accepted_signatures()
    assert "unregistered_command_md::.claude/commands/x.md" not in valid
    assert invalid and any("expired" in e for e in invalid[0]["errors"])


def test_broad_exception_is_invalid_not_covering(tmp_path, monkeypatch):
    store = tmp_path / "acc.yaml"
    store.write_text(
        "exceptions:\n"
        "  - exception_id: E2\n"
        "    finding_signature: '*'\n"
        "    severity: HIGH\n"
        "    owner: x\n"
        "    reason: cleanup\n"
        "    remediation_task: TC-2\n"
        "    created: '2026-07-16'\n"
        "    expires: '2099-01-01'\n"
        "    compensating_control: none\n",
        encoding="utf-8")
    monkeypatch.setattr(X, "STORE", store)
    valid, invalid = X.active_accepted_signatures()
    assert "*" not in valid
    assert invalid


def test_valid_exception_covers_exact_signature(tmp_path, monkeypatch):
    sig = "unregistered_command_md::.claude/commands/x.md"
    store = tmp_path / "acc.yaml"
    store.write_text(
        "exceptions:\n"
        "  - exception_id: E3\n"
        f"    finding_signature: '{sig}'\n"
        "    severity: HIGH\n"
        "    owner: babar-raza\n"
        "    reason: awaiting normalization window\n"
        "    remediation_task: TC-3\n"
        "    created: '2026-07-16'\n"
        f"    expires: '{(date.today() + timedelta(days=30)).isoformat()}'\n"
        "    compensating_control: closeout gate\n",
        encoding="utf-8")
    monkeypatch.setattr(X, "STORE", store)
    valid, invalid = X.active_accepted_signatures()
    assert sig in valid and not invalid


# ── adversarial: naming a skill is never sufficient ────────────────────────

def test_naming_skill_without_evidence_still_blocks():
    m = M.create_manifest(
        task_id="TC-ADV-001", agent_type="CLAUDE_CODE",
        requested_operation="pretend work",
        selected_skill_ids=[next(s.skill_id for s in REG.load_skills()
                                 if s.is_active and s.command_file
                                 and (REPO_ROOT / s.command_file).exists())],
        allowed_paths=["tools/governance/**"], write=False)
    out = C.evaluate(m, ["tools/governance/real_change.py"], evidence_paths=[])
    assert out["verdict"] == "CLOSE_BLOCKED"
