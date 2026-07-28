"""test_cli_skill_gate_parity.py — Codex/Claude Code skill-gate parity.

docs/governance/skill-only-policy.yaml and docs/governance/codex-adapter.md
(line 21) both state the skill-only policy "applies equally to Claude Code
and Codex." Before this fix, only gate.py's PreToolUse hook (Claude Code)
ever called skill_gate.evaluate_path() -- Codex's own mandatory entry point,
`python -m tools.supervisor.coordination preflight` (per the adapter's §3a
contract), only ran the coordination-lease check. This suite proves the CLI
`preflight` verb now runs the identical decision as the hook: same verdict
tiers, same path-scoped check_mode, same block/allow outcome, same advisory
logging -- for a caller that never goes through Claude Code's hook mechanism.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from coordination import db as cdb  # noqa: E402
from coordination import root as croot  # noqa: E402
from coordination.hooks import skill_gate  # noqa: E402

CHECK_ID = skill_gate.CHECK_ID


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / "tools" / "governance" / "skills_first").mkdir(parents=True)
    (repo / ".git").mkdir()
    target = repo / "tools" / "governance" / "skills_first" / "new_file.py"
    target.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    monkeypatch.delenv("FF_AGENT_ID", raising=False)
    monkeypatch.delenv("FF_AGENT_TOKEN", raising=False)
    monkeypatch.delenv("FF_COORD_BYPASS", raising=False)
    monkeypatch.chdir(repo)
    cdb.ensure_db(root)
    return root, repo


def _register_codex(root):
    from coordination.cli import main as cli_main
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli_main(["--json", "register", "--provider", "codex",
                        "--task", "TC-CODEX-1"])
    assert code == 0
    out = json.loads(buf.getvalue())
    return out["data"]["agent_id"], out["data"]["token"]


def test_codex_preflight_advisory_mode_allows_and_logs(env, capsys):
    """check_mode:skill_resolution defaults to advisory -- Codex's CLI-driven
    preflight must ALLOW a skill-governed, unmanifested write (exit 0) and
    log the would-block event, exactly like the Claude Code hook does."""
    from coordination.cli import main as cli_main
    root, repo = env
    aid, tok = _register_codex(root)
    capsys.readouterr()

    code = cli_main(["--json", "--agent", aid, "--token", tok,
                     "preflight", "--file",
                     "tools/governance/skills_first/new_file.py"])
    assert code == 0, "advisory mode must allow, not block"

    log_path = root / "advisory-log.jsonl"
    assert log_path.exists()
    lines = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]
    events = [l for l in lines if l.get("check") == CHECK_ID]
    assert events, "expected an advisory-logged skill_resolution event from the CLI path"
    assert events[-1]["tier"] == skill_gate.SKILL_EXISTS_BUT_NO_MANIFEST
    assert events[-1]["tool"] == "cli:preflight"


def test_codex_preflight_enforcing_mode_blocks_with_exit_7(env, capsys):
    """Promoting check_mode:skill_resolution to enforcing must block Codex's
    CLI-driven preflight (exit 7) exactly as it would block the Claude Code
    hook -- this is the parity the fix establishes."""
    from coordination.cli import main as cli_main
    root, repo = env
    aid, tok = _register_codex(root)

    conn = cdb.connect(root)
    try:
        cdb.set_check_mode(conn, CHECK_ID, "enforcing", "test", "promotion")
    finally:
        conn.close()
    capsys.readouterr()

    code = cli_main(["--json", "--agent", aid, "--token", tok,
                     "preflight", "--file",
                     "tools/governance/skills_first/new_file.py"])
    assert code == 7, "enforcing check_mode must block via the new exit code"
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False
    assert "manifest" in out["error"] and "--skill" in out["error"]


def test_codex_preflight_never_resolved_path_always_allows(env, capsys):
    """NO_SKILL_RESOLVED_FOR_PATH must always allow regardless of check_mode
    -- the CLI path must not become MORE restrictive than the hook."""
    from coordination.cli import main as cli_main
    root, repo = env
    (repo / "unrelated").mkdir()
    (repo / "unrelated" / "x.txt").write_text("x\n", encoding="utf-8")
    aid, tok = _register_codex(root)

    conn = cdb.connect(root)
    try:
        cdb.set_check_mode(conn, CHECK_ID, "enforcing", "test", "promotion")
    finally:
        conn.close()

    code = cli_main(["--json", "--agent", aid, "--token", tok,
                     "preflight", "--file", "unrelated/x.txt"])
    assert code == 0


def test_codex_preflight_manifest_covering_always_allows(env, monkeypatch):
    """A live manifest covering the path must allow the CLI path exactly like
    the hook, even with check_mode enforcing."""
    from coordination.cli import main as cli_main
    root, repo = env
    aid, tok = _register_codex(root)

    conn = cdb.connect(root)
    try:
        cdb.set_check_mode(conn, CHECK_ID, "enforcing", "test", "promotion")
    finally:
        conn.close()

    fake_manifest_dir = root / "manifests"
    fake_manifest_dir.mkdir()
    from datetime import datetime, timedelta, timezone
    fake = {
        "execution_id": "sfx-cli-test-cover",
        "status": "CREATED",
        "allowed_paths": ["tools/governance/skills_first/**"],
        "expires_at": (datetime.now(timezone.utc)
                       + timedelta(hours=1)).isoformat(),
    }
    (fake_manifest_dir / "sfx-cli-test-cover.json").write_text(
        json.dumps(fake), encoding="utf-8")
    import tools.governance.skills_first.manifest as M
    monkeypatch.setattr(M, "MANIFEST_DIR", fake_manifest_dir)

    code = cli_main(["--json", "--agent", aid, "--token", tok,
                     "preflight", "--file",
                     "tools/governance/skills_first/new_file.py"])
    assert code == 0


def test_skill_gate_never_blocks_when_lease_already_denied(env, capsys):
    """The skill-gate check must never run (let alone override) when the
    coordination-lease preflight itself already denied the write -- mirrors
    gate.py's 'can never override a coordination denial' invariant."""
    from coordination.cli import main as cli_main
    root, repo = env
    aid, tok = _register_codex(root)
    bid, btok = _register_codex(root)  # second, distinct agent identity
    capsys.readouterr()

    assert cli_main(["--json", "--agent", aid, "--token", tok, "claim",
                     "--resource",
                     "tools/governance/skills_first/new_file.py"]) == 0
    capsys.readouterr()

    conn = cdb.connect(root)
    try:
        cdb.set_check_mode(conn, CHECK_ID, "enforcing", "test", "promotion")
    finally:
        conn.close()

    code = cli_main(["--json", "--agent", bid, "--token", btok,
                     "preflight", "--file",
                     "tools/governance/skills_first/new_file.py"])
    assert code == 2, "lease conflict (exit 2) must win, not skill-gate's exit 7"
