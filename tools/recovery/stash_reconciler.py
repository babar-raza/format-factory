"""Deterministic, exact-path stash recovery for detached Git worktrees.

generated_by: codex
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


PROHIBITED_PARTS = {".git", ".local", ".env"}


def run_git(cwd: Path, *args: str, check: bool = True, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return result.stdout


def full_commit(repo: Path, revision: str) -> str:
    value = run_git(repo, "rev-parse", f"{revision}^{{commit}}").decode().strip()
    if len(value) != 40:
        raise ValueError(f"revision did not resolve to a full commit: {revision}")
    return value


def tree_map(repo: Path, revision: str) -> dict[str, str]:
    output = run_git(repo, "ls-tree", "-rz", revision)
    result: dict[str, str] = {}
    for entry in output.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        result[raw_path.decode("utf-8", errors="surrogateescape")] = metadata.split()[2].decode()
    return result


def safe_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or any(part in PROHIBITED_PARTS for part in path.parts):
        raise ValueError(f"prohibited recovery path: {value}")
    if not path.parts:
        raise ValueError("empty recovery path")
    return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inventory(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    main_commit = full_commit(repo, args.main_commit)
    main_tree = tree_map(repo, main_commit)
    rows: list[dict[str, Any]] = []
    for raw in args.stash:
        index_text, stash_rev, base_rev = raw.split(":", 2)
        stash_commit = full_commit(repo, stash_rev)
        base_commit = full_commit(repo, base_rev)
        base_tree = tree_map(repo, base_commit)
        stash_tree = tree_map(repo, stash_commit)
        names = run_git(repo, "diff", "--name-only", "-z", base_commit, stash_commit)
        for raw_path in names.split(b"\0"):
            if not raw_path:
                continue
            path = safe_path(raw_path.decode("utf-8", errors="surrogateescape"))
            base_blob = base_tree.get(path)
            stash_blob = stash_tree.get(path)
            main_blob = main_tree.get(path)
            if stash_blob == main_blob:
                relation = "EXACT_IN_MAIN"
            elif main_blob == base_blob:
                relation = "UNIQUE_NOT_IN_MAIN"
            elif stash_blob != base_blob and main_blob != base_blob:
                relation = "DIVERGENT"
            else:
                relation = "OTHER"
            rows.append(
                {
                    "base_blob": base_blob,
                    "base_commit": base_commit,
                    "main_blob": main_blob,
                    "main_commit": main_commit,
                    "path": path,
                    "relation": relation,
                    "stash_blob": stash_blob,
                    "stash_commit": stash_commit,
                    "stash_index": int(index_text),
                }
            )
    rows.sort(key=lambda row: (row["stash_index"], row["path"]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"STASH_INVENTORY: PASS rows={len(rows)} output={output.resolve()}")
    return 0


def worktree_guard(repo: Path, worktree: Path) -> None:
    root = Path(run_git(repo, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    target_root = Path(run_git(worktree, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if root == target_root:
        raise ValueError("root worktree mutation is forbidden")
    branch = run_git(worktree, "branch", "--show-current").decode().strip()
    if branch:
        raise ValueError(f"worktree must be detached, found branch: {branch}")
    registered = run_git(repo, "worktree", "list", "--porcelain").decode()
    if f"worktree {target_root.as_posix()}" not in registered.replace("\\", "/"):
        raise ValueError("target is not a registered Git worktree")


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("mode") not in {"unique", "three_way"}:
        raise ValueError("manifest mode must be unique or three_way")
    paths = value.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("manifest paths must be a non-empty list")
    value["paths"] = [safe_path(item) for item in paths]
    if len(value["paths"]) != len(set(value["paths"])):
        raise ValueError("manifest contains duplicate paths")
    return value


def working_blob(worktree: Path, path: str) -> str | None:
    target = worktree / Path(path)
    if not target.is_file():
        return None
    return run_git(worktree, "hash-object", "--", path).decode().strip()


def materialize(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    archive = Path(args.archive_dir).resolve()
    manifest_path = Path(args.manifest).resolve()
    receipt_path = Path(args.receipt).resolve()
    worktree_guard(repo, worktree)
    if not archive.is_dir() or not (archive / "SHA256-MANIFEST.json").is_file():
        raise ValueError("verified recovery archive or SHA256-MANIFEST.json is missing")
    manifest = load_manifest(manifest_path)
    stash_commit = full_commit(repo, args.stash_commit)
    base_commit = full_commit(repo, args.base_commit)
    stash_tree = tree_map(repo, stash_commit)
    base_tree = tree_map(repo, base_commit)
    changed: list[str] = []
    no_op: list[str] = []
    conflicts: list[str] = []
    before: dict[str, str | None] = {}
    after: dict[str, str | None] = {}

    if manifest["mode"] == "unique":
        for path in manifest["paths"]:
            expected_base = base_tree.get(path)
            expected_stash = stash_tree.get(path)
            current_head = tree_map(worktree, "HEAD").get(path)
            current_working = working_blob(worktree, path)
            before[path] = current_working
            if current_working == expected_stash:
                no_op.append(path)
                after[path] = current_working
                continue
            if current_head != expected_base or current_working != current_head:
                raise ValueError(
                    f"unique guard failed for {path}: "
                    f"HEAD={current_head} base={expected_base} working={current_working}"
                )
            if expected_stash is None:
                run_git(worktree, "rm", "-f", "--", path)
            else:
                run_git(worktree, "checkout", stash_commit, "--", path)
            after[path] = working_blob(worktree, path)
            if after[path] != expected_stash:
                raise RuntimeError(f"post-materialization blob mismatch: {path}")
            changed.append(path)
    else:
        with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as stream:
            patch_path = Path(stream.name)
            stream.write(
                run_git(repo, "diff", "--binary", base_commit, stash_commit, "--", *manifest["paths"])
            )
        try:
            result = subprocess.run(
                ["git", "apply", "--3way", str(patch_path)],
                cwd=worktree,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode:
                conflicts = manifest["paths"]
                raise RuntimeError(
                    f"three-way apply failed: {result.stderr.decode('utf-8', errors='replace')}"
                )
            changed = manifest["paths"]
            for path in manifest["paths"]:
                before[path] = base_tree.get(path)
                after[path] = working_blob(worktree, path)
        finally:
            patch_path.unlink(missing_ok=True)

    receipt = {
        "archive_dir": str(archive),
        "base_commit": base_commit,
        "before_blobs": before,
        "after_blobs": after,
        "changed_paths": changed,
        "conflicts": conflicts,
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "mode": manifest["mode"],
        "no_op_paths": no_op,
        "result": "PASS",
        "skill_id": "reconcile-stashed-work",
        "stash_commit": stash_commit,
        "worktree": str(worktree),
    }
    write_json(receipt_path, receipt)
    print(
        f"STASH_MATERIALIZE: PASS changed={len(changed)} "
        f"no_op={len(no_op)} receipt={receipt_path}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--repo", default=".")
    sub = root.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("--main-commit", required=True)
    inv.add_argument("--stash", action="append", required=True)
    inv.add_argument("--output", required=True)
    inv.set_defaults(func=inventory)
    mat = sub.add_parser("materialize")
    mat.add_argument("--worktree", required=True)
    mat.add_argument("--stash-commit", required=True)
    mat.add_argument("--base-commit", required=True)
    mat.add_argument("--manifest", required=True)
    mat.add_argument("--archive-dir", required=True)
    mat.add_argument("--receipt", required=True)
    mat.set_defaults(func=materialize)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except (ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"STASH_RECONCILIATION: FAIL {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
