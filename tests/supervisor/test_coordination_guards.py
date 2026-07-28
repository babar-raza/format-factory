"""TC-COORD-007/009/010: pre_mutation_guard lease check, generator guard,
pre-commit staged-set validation.

Mission AGENT-COORD-2026-07-15. Hermetic: coordination root in tmp_path via
the conftest guard fixture / explicit env; sandbox git repos for staging.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from coordination import db as cdb
from coordination import root as croot
from coordination.errors import GeneratorBlocked
from coordination.generator_guard import (_claim_targets, guarded_generation,
                                          load_manifest)
from coordination.leases import LeaseManager
from coordination.precommit import precommit_check
from coordination.registry import AgentRegistry


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "out").mkdir()
    (repo / "src").mkdir()
    (repo / "out" / "gen.yaml").write_text("old\n", encoding="utf-8")
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    monkeypatch.delenv("FF_AGENT_ID", raising=False)
    monkeypatch.delenv("FF_AGENT_TOKEN", raising=False)
    cdb.ensure_db(root)
    return root, repo


def _manifest(repo: Path, outputs: list[str], gen_id="stubgen") -> Path:
    p = repo / "output-manifest.yaml"
    lines = [f"generator_id: {gen_id}", "mode: exclusive", "outputs:"]
    lines += [f"  - \"{o}\"" for o in outputs]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


class TestGeneratorGuard:
    def test_manifest_validation(self, env):
        root, repo = env
        bad = repo / "bad.yaml"
        bad.write_text("generator_id: x\noutputs: []\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_manifest(bad)
        good = _manifest(repo, ["out/gen.yaml"])
        assert load_manifest(good)["generator_id"] == "stubgen"

    def test_glob_expansion_never_locks_static_prefix_when_matches(
            self, env):
        root, repo = env
        (repo / "src" / "a").mkdir()
        (repo / "src" / "b").mkdir()
        (repo / "src" / "a" / "README.md").write_text("a", encoding="utf-8")
        (repo / "src" / "b" / "README.md").write_text("b", encoding="utf-8")
        targets = _claim_targets(["src/*/README.md"], repo)
        assert sorted(targets) == ["src/a/README.md", "src/b/README.md"]
        # No matches -> conservative static prefix fallback.
        assert _claim_targets(["nowhere/*/x.md"], repo) == ["nowhere"]

    def test_blocked_before_any_write_when_output_leased(self, env):
        root, repo = env
        other = AgentRegistry(root, start=repo).register("claude-code")
        LeaseManager(root, start=repo).claim(other.agent_id, other.token,
                                             ["out/gen.yaml"])
        manifest = _manifest(repo, ["out/gen.yaml"])
        before = (repo / "out" / "gen.yaml").read_text(encoding="utf-8")
        with pytest.raises(GeneratorBlocked) as exc:
            with guarded_generation("stubgen", manifest, root=root,
                                    start=repo):
                (repo / "out" / "gen.yaml").write_text("clobbered",
                                                       encoding="utf-8")
        assert "no files were written" in str(exc.value)
        assert (repo / "out" / "gen.yaml").read_text(
            encoding="utf-8") == before

    def test_success_run_records_manifest_and_releases(self, env):
        root, repo = env
        manifest = _manifest(repo, ["out/gen.yaml"])
        with guarded_generation("stubgen", manifest, root=root,
                                start=repo) as g:
            (repo / "out" / "gen.yaml").write_text("new\n", encoding="utf-8")
            g.record_written(repo / "out" / "gen.yaml")
        records = list((root / "generator-manifests").glob("stubgen-*.json"))
        assert len(records) == 1
        rec = json.loads(records[0].read_text(encoding="utf-8"))
        assert rec["written"] == ["out/gen.yaml"] and rec["drift"] == []
        conn = cdb.connect(root)
        try:
            live = conn.execute("SELECT COUNT(*) AS n FROM leases WHERE"
                                " status IN ('ACTIVE','STALE')").fetchone()["n"]
            assert live == 0  # released on exit
        finally:
            conn.close()

    def test_out_of_manifest_write_flagged_as_drift_conflict(self, env):
        root, repo = env
        manifest = _manifest(repo, ["out/gen.yaml"])
        with guarded_generation("stubgen", manifest, root=root,
                                start=repo) as g:
            (repo / "out" / "extra.yaml").write_text("x", encoding="utf-8")
            g.record_written(repo / "out" / "extra.yaml")
        conn = cdb.connect(root)
        try:
            c = conn.execute("SELECT * FROM conflicts WHERE"
                             " conflict_type='generator-drift'").fetchone()
            assert c is not None
            assert c["resource_key"] == "out/extra.yaml"
        finally:
            conn.close()


class TestPrecommitCheck:
    def _git_repo(self, tmp_path) -> Path:
        repo = tmp_path / "staged-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo,
                       check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo,
                       check=True)
        return repo

    def test_foreign_lease_blocks_staged_commit(self, env, tmp_path,
                                                monkeypatch):
        root, _ = env
        repo = self._git_repo(tmp_path)
        (repo / "feature.py").write_text("work\n", encoding="utf-8")
        subprocess.run(["git", "add", "feature.py"], cwd=repo, check=True)
        owner = AgentRegistry(root, start=repo).register("claude-code",
                                                         task_id="TC-A")
        LeaseManager(root, start=repo).claim(owner.agent_id, owner.token,
                                             ["feature.py"])
        report = precommit_check(root=root, repo=repo)
        assert report["ok"] is False
        assert report["violations"][0]["kind"] == "foreign-lease"
        assert owner.agent_id in report["violations"][0]["message"]

    def test_own_lease_and_clean_files_pass(self, env, tmp_path, monkeypatch):
        root, _ = env
        repo = self._git_repo(tmp_path)
        (repo / "mine.py").write_text("mine\n", encoding="utf-8")
        (repo / "free.py").write_text("free\n", encoding="utf-8")
        subprocess.run(["git", "add", "mine.py", "free.py"], cwd=repo,
                       check=True)
        me = AgentRegistry(root, start=repo).register("claude-code")
        LeaseManager(root, start=repo).claim(me.agent_id, me.token,
                                             ["mine.py"])
        monkeypatch.setenv("FF_AGENT_ID", me.agent_id)
        monkeypatch.setenv("FF_AGENT_TOKEN", me.token)
        report = precommit_check(root=root, repo=repo)
        assert report["ok"] is True

    def test_unresolved_conflict_blocks(self, env, tmp_path):
        root, _ = env
        repo = self._git_repo(tmp_path)
        (repo / "hot.py").write_text("hot\n", encoding="utf-8")
        subprocess.run(["git", "add", "hot.py"], cwd=repo, check=True)
        from coordination.conflicts import ConflictLog
        conn = cdb.connect(root)
        with cdb.immediate(conn):
            ConflictLog(root).record(
                conn, resource_key="hot.py", resource_display="hot.py",
                detected_by="agent-x", conflict_type="unknown-change",
                safe_action="preserve-and-rebaseline")
        conn.close()
        report = precommit_check(root=root, repo=repo)
        assert report["ok"] is False
        assert report["violations"][0]["kind"] == "unresolved-conflict"

    def test_absent_db_is_noop(self, tmp_path, monkeypatch):
        monkeypatch.setenv(croot.ENV_ROOT, str(tmp_path / "nodb"))
        repo = self._git_repo(tmp_path)
        report = precommit_check(root=tmp_path / "nodb", repo=repo)
        assert report["ok"] is True


class TestPreMutationGuardLease:
    @pytest.fixture()
    def guard(self, env, tmp_path, monkeypatch):
        sys.path.insert(0, str(Path("tools") / "governance"))
        import pre_mutation_guard as pmg
        registry_yaml = tmp_path / "skill-registry.yaml"
        registry_yaml.write_text(
            "skills:\n"
            "  - skill_id: test-skill\n"
            "    status: active\n"
            "    allowed_paths: []\n", encoding="utf-8")
        monkeypatch.setattr(pmg, "SKILL_REGISTRY", registry_yaml)
        return pmg

    def test_blocked_without_identity(self, guard, env, monkeypatch):
        root, repo = env
        monkeypatch.chdir(repo)
        result = guard.run("CODEX", "TC-1", "test-skill", ["src/x.py"],
                           "M", "S", dry_run=True)
        assert result["verdict"] == "BLOCKED"
        assert result["rejection_condition"] == "no_coordination_identity"

    def test_blocked_without_lease_then_authorized_with(self, guard, env,
                                                        monkeypatch):
        root, repo = env
        monkeypatch.chdir(repo)
        ra = AgentRegistry(root, start=repo).register("codex")
        monkeypatch.setenv("FF_AGENT_ID", ra.agent_id)
        monkeypatch.setenv("FF_AGENT_TOKEN", ra.token)
        result = guard.run("CODEX", "TC-1", "test-skill", ["src/x.py"],
                           "M", "S", dry_run=True)
        assert result["verdict"] == "BLOCKED"
        assert result["rejection_condition"] == "coordination_lease_missing"
        LeaseManager(root, start=repo).claim(ra.agent_id, ra.token,
                                             ["src/x.py"])
        result = guard.run("CODEX", "TC-1", "test-skill", ["src/x.py"],
                           "M", "S", dry_run=True)
        assert result["verdict"] == "AUTHORIZED"

    def test_foreign_lease_blocks_guard(self, guard, env, monkeypatch):
        root, repo = env
        monkeypatch.chdir(repo)
        other = AgentRegistry(root, start=repo).register("claude-code")
        LeaseManager(root, start=repo).claim(other.agent_id, other.token,
                                             ["src/x.py"])
        me = AgentRegistry(root, start=repo).register("codex")
        monkeypatch.setenv("FF_AGENT_ID", me.agent_id)
        monkeypatch.setenv("FF_AGENT_TOKEN", me.token)
        result = guard.run("CODEX", "TC-1", "test-skill", ["src/x.py"],
                           "M", "S", dry_run=True)
        assert result["verdict"] == "BLOCKED"
        assert result["rejection_condition"] == "coordination_lease_conflict"

    def test_no_require_lease_skip_is_recorded(self, guard, env, monkeypatch):
        root, repo = env
        monkeypatch.chdir(repo)
        result = guard.run("CODEX", "TC-1", "test-skill", ["src/x.py"],
                           "M", "S", dry_run=True, require_lease=False)
        assert result["verdict"] == "AUTHORIZED"
