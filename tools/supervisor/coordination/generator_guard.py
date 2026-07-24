"""Generator output guard (TC-COORD-009).

A generator must fail BEFORE writing when its declared output set overlaps
another agent's live lease, and must not silently write outside its
manifest. Two integration styles:

1. In-process retrofit:
       with guarded_generation("capability_sync",
                                REPO / "tools/capability_sync/output-manifest.yaml") as g:
           ...writes...
           g.record_written(path)          # enables drift detection

2. Subprocess bridge for generators too risky to refactor:
       python -m tools.supervisor.coordination guard-run \
           --generator-id autonomous_cycle --manifest-file <yaml> -- <command>

Manifest convention (checked in): tools/<pkg>/output-manifest.yaml
   generator_id: <id>
   mode: exclusive
   outputs: [<repo-relative path or glob>, ...]
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
from contextlib import contextmanager
from pathlib import Path

from .conflicts import ConflictLog
from .db import connect, emit_event, ensure_db, immediate
from .errors import GeneratorBlocked, LeaseConflict
from .ids import iso, utcnow
from .leases import LeaseManager
from .preflight import resolve_identity
from .registry import AgentRegistry
from .root import canonical_resource, resolve_coordination_root, worktree_identity

_GLOB_CHARS = set("*?[")


def load_manifest(manifest_path: str | Path) -> dict:
    import yaml

    data = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "generator_id" not in data \
            or not isinstance(data.get("outputs"), list) or not data["outputs"]:
        raise ValueError(
            f"invalid output manifest {manifest_path}: needs generator_id"
            " and a non-empty outputs list")
    return data


_GLOB_EXPAND_CAP = 300


def _claim_targets(outputs: list[str], wt_path: str | Path) -> list[str]:
    """Concrete paths are claimed directly. Glob entries are expanded against
    the worktree and the matches claimed individually -- claiming the static
    prefix of `src/python/*/README.md` would exclusively lock all of
    src/python, which is exactly the over-broad behaviour this system exists
    to stop. Only when a glob matches nothing (or explodes past the cap) do
    we fall back to the static prefix directory."""
    targets: list[str] = []
    for out in outputs:
        norm = out.replace("\\", "/")
        if not any(c in _GLOB_CHARS for c in norm):
            targets.append(norm)
            continue
        matches = [p.relative_to(wt_path).as_posix()
                   for p in Path(wt_path).glob(norm)]
        if matches and len(matches) <= _GLOB_EXPAND_CAP:
            targets.extend(matches)
            continue
        parts: list[str] = []
        for part in norm.split("/"):
            if any(c in _GLOB_CHARS for c in part):
                break
            parts.append(part)
        targets.append("/".join(parts) if parts else ".")
    return targets


def _in_manifest(key: str, outputs: list[str]) -> bool:
    for out in outputs:
        pat = out.replace("\\", "/").casefold()
        if key == pat or fnmatch.fnmatch(key, pat):
            return True
        if not any(c in _GLOB_CHARS for c in pat) and key.startswith(pat + "/"):
            return True
    return False


class GeneratorGuard:
    def __init__(self, generator_id: str, outputs: list[str], agent_id: str,
                 lease_ids: list[str], root: Path, wt_path: str):
        self.generator_id = generator_id
        self.outputs = outputs
        self.agent_id = agent_id
        self.lease_ids = lease_ids
        self.root = root
        self.wt_path = wt_path
        self.written: list[str] = []
        self.drift: list[str] = []

    def record_written(self, path: str | Path) -> None:
        import os

        key, _display = canonical_resource(str(path), self.wt_path)
        rel = os.path.relpath(os.path.realpath(str(path)),
                              os.path.realpath(self.wt_path))
        display = rel.replace("\\", "/")
        self.written.append(display)
        if not _in_manifest(key, self.outputs):
            self.drift.append(display)


@contextmanager
def guarded_generation(generator_id: str, manifest_path: str | Path, *,
                       root: Path | None = None,
                       start: str | Path | None = None,
                       agent_id: str | None = None, token: str | None = None):
    root = root or resolve_coordination_root(start)
    ensure_db(root)
    manifest = load_manifest(manifest_path)
    if manifest["generator_id"] != generator_id:
        raise ValueError(
            f"manifest generator_id '{manifest['generator_id']}' does not"
            f" match '{generator_id}'")
    outputs = [str(o) for o in manifest["outputs"]]
    _, wt_path = worktree_identity(start)

    registry = AgentRegistry(root, start=start)
    ident = resolve_identity(registry, agent_id=agent_id, token=token)
    ephemeral = ident is None
    if ephemeral:
        ra = registry.register(f"generator-{generator_id}",
                               agent_type="headless",
                               execution_mode="headless",
                               task_id=f"generator:{generator_id}")
        ident = (ra.agent_id, ra.token)
    aid, tok = ident

    lm = LeaseManager(root, start=start)
    resources = _claim_targets(outputs, wt_path) + [f"cmd:{generator_id}"]
    try:
        leases = lm.claim(aid, tok, resources,
                          intended_ops=["regenerate"],
                          task_id=f"generator:{generator_id}")
    except LeaseConflict as exc:
        raise GeneratorBlocked(
            generator_id,
            f"output '{exc.resource_key}' is leased by"
            f" {exc.holder_agent_id} (lease {exc.holder_lease_id});"
            " refusing to start -- no files were written") from exc

    guard = GeneratorGuard(generator_id, outputs, aid,
                           [l["lease_id"] for l in leases], root, wt_path)
    try:
        yield guard
    finally:
        _finish(guard, lm, registry, aid, tok, ephemeral)


def _finish(guard: GeneratorGuard, lm: LeaseManager, registry: AgentRegistry,
            aid: str, tok: str, ephemeral: bool) -> None:
    root = guard.root
    run_record = {
        "generator_id": guard.generator_id,
        "agent_id": aid,
        "declared_outputs": guard.outputs,
        "written": guard.written,
        "drift": guard.drift,
        "finished_at": iso(),
    }
    manifests_dir = root / "generator-manifests"
    manifests_dir.mkdir(exist_ok=True)
    stamp = utcnow().strftime("%Y%m%dT%H%M%S")
    (manifests_dir / f"{guard.generator_id}-{stamp}.json").write_text(
        json.dumps(run_record, indent=2), encoding="utf-8")

    conn = connect(root)
    try:
        with immediate(conn):
            if guard.drift:
                clog = ConflictLog(root)
                for d in guard.drift:
                    key, _ = canonical_resource(d, guard.wt_path)
                    clog.record(
                        conn, resource_key=key, resource_display=d,
                        detected_by=aid, conflict_type="generator-drift",
                        attempted_op="regenerate",
                        safe_action="add-to-manifest-or-revert-output",
                        classification="GENERATED")
            emit_event(conn, "generator", guard.generator_id,
                       "GENERATOR_RUN", actor=aid,
                       detail={"written": len(guard.written),
                               "drift": len(guard.drift)})
    finally:
        conn.close()

    try:
        lm.release(aid, tok, guard.lease_ids)
    except Exception:
        pass
    if ephemeral:
        try:
            registry.complete(aid, tok, reason="generator run finished")
        except Exception:
            pass


def guard_run_cli(root: Path, generator_id: str, manifest_file: str,
                  command: list[str], registry, lm, emit) -> int:
    """Subprocess bridge used by the CLI `guard-run` verb."""
    cmd = [c for c in command if c != "--"]
    if not cmd:
        return emit(False, 1, None, "no command given after --")
    try:
        with guarded_generation(generator_id, manifest_file,
                                root=root) as guard:
            proc = subprocess.run(cmd)
            code = proc.returncode
        return emit(code == 0, code,
                    {"generator_id": generator_id, "command_exit": code,
                     "drift": guard.drift})
    except GeneratorBlocked as exc:
        return emit(False, exc.exit_code, None, str(exc))
    except (ValueError, OSError) as exc:
        return emit(False, 1, None, str(exc))
