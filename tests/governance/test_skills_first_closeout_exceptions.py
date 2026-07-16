"""Unit tests — Skills-First Control: closeout gate + exception governance.

Covers the fail-closed closeout evidence gate (policy section 24 equivalent) and
the narrow exception mechanism (policy section 8 / prompt section 25).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import closeout as C  # noqa: E402
from tools.governance.skills_first import exceptions as X  # noqa: E402
from tools.governance.skills_first import manifest as M  # noqa: E402
from tools.governance.skills_first.registries import load_skills  # noqa: E402


def _an_active_skill() -> str:
    for s in load_skills():
        if s.is_active and s.command_file and (REPO_ROOT / s.command_file).exists():
            return s.skill_id
    pytest.skip("no active skill with on-disk command file")


def _manifest(allowed):
    return M.create_manifest(
        task_id="TC-CO-001", agent_type="CLAUDE_CODE",
        requested_operation="closeout test", selected_skill_ids=[_an_active_skill()],
        allowed_paths=allowed, write=False)


# ── path scoping ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("allowed,changed,ok", [
    (["tools/governance/**"], "tools/governance/x.py", True),
    (["tools/governance/**"], "src/python/fods/models.py", False),
    (["tools/governance/skills_first/*"], "tools/governance/skills_first/a.py", True),
    (["tools/governance/skills_first/*"], "tools/governance/skills_first/sub/a.py", False),
    (["docs/"], "docs/x/y.md", True),
])
def test_path_allowed_matrix(allowed, changed, ok):
    assert C.path_allowed(changed, allowed) is ok


# ── closeout gate: fail-closed on scope / evidence ─────────────────────────

def test_closeout_blocks_out_of_scope_change():
    m = _manifest(["tools/governance/**"])
    r = C.evaluate(m, ["src/python/fods/models.py"], evidence_paths=[])
    assert r["verdict"] == "CLOSE_BLOCKED"
    assert any("outside allowed_paths" in x for x in r["reasons"])


def test_closeout_blocks_missing_evidence():
    m = _manifest(["tools/governance/**"])
    r = C.evaluate(m, ["tools/governance/x.py"], evidence_paths=[])
    assert r["verdict"] == "CLOSE_BLOCKED"
    assert any("no skill-use evidence" in x for x in r["reasons"])


def test_closeout_ok_with_scope_and_evidence():
    m = _manifest(["tools/governance/skills_first/**"])
    # a real file that resolves as evidence
    r = C.evaluate(m, ["tools/governance/skills_first/audit.py"],
                   evidence_paths=["tools/governance/skills_first/audit.py"])
    assert r["verdict"] == "CLOSE_OK", r["reasons"]


def test_closeout_blocks_on_command_hash_drift():
    m = _manifest(["tools/governance/**"])
    # simulate command drift since resolution
    sid = m["selected_skill_ids"][0]
    m["skill_hashes"][sid] = "deadbeef" * 8
    r = C.evaluate(m, ["tools/governance/x.py"],
                   evidence_paths=["tools/governance/skills_first/audit.py"])
    assert r["verdict"] == "CLOSE_BLOCKED"
    assert any("drifted since resolution" in x for x in r["reasons"])


def test_closeout_blocks_invalid_manifest():
    r = C.evaluate({"schema": "wrong"}, ["a.py"], [])
    assert r["verdict"] == "CLOSE_BLOCKED"
    assert r["checks"]["manifest_valid"] is False


# ── exception governance ───────────────────────────────────────────────────

def _valid_exc(**over):
    base = {
        "exception_id": "SFX-EXC-1",
        "finding_signature": "unregistered_command_md::.claude/commands/x.md",
        "severity": "HIGH",
        "owner": "babar-raza",
        "reason": "awaiting registry normalization window",
        "remediation_task": "TC-HEAL-001",
        "created": "2026-07-16",
        "expires": (date.today() + timedelta(days=14)).isoformat(),
        "compensating_control": "closeout gate blocks the underlying command",
    }
    base.update(over)
    return base


def test_valid_exception_passes():
    assert X.validate_exception(_valid_exc()) == []


def test_expired_exception_rejected():
    errs = X.validate_exception(_valid_exc(
        expires=(date.today() - timedelta(days=1)).isoformat()))
    assert any("expired" in e for e in errs)


def test_broad_exception_rejected():
    errs = X.validate_exception(_valid_exc(finding_signature="*"))
    assert any("too broad" in e for e in errs)


def test_forbidden_reason_rejected():
    errs = X.validate_exception(_valid_exc(reason="urgent"))
    assert any("forbidden reason" in e for e in errs)


def test_missing_field_rejected():
    exc = _valid_exc()
    del exc["owner"]
    errs = X.validate_exception(exc)
    assert any("owner" in e for e in errs)


def test_finding_signature_stable():
    f = {"category": "unregistered_command_md", "file": ".claude/commands/x.md"}
    assert X.finding_signature(f) == "unregistered_command_md::.claude/commands/x.md"
