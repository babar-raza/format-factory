"""package_proof_common.py — shared logic for the package-install-proof system.

Single implementation of the source digest used by BOTH the proof orchestrator
(tools/run_package_install_proof.py) and the V226 coverage validator
(governance_validators_package_proof.py). Two copies of this function would
drift and silently break staleness detection — do not duplicate it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROOF_MANIFEST_REL = "reports/package-install-proof/proof-manifest.json"
PACKAGE_MATRIX_REL = "packaging/python/package-matrix.yaml"
PROOF_RUNTIME_INPUTS = (
    "packaging/python/build-local-packages.py",
    "packaging/python/proof-requirements.txt",
    "tools/run_package_install_proof.py",
    "tools/supervisor/package_proof_common.py",
    "tests/python/packaging/test_package_install_proof_all_formats.py",
)
_TRANSIENT_ROOT_DIRECTORIES = frozenset({"build", "dist", ".mypy_cache", ".ruff_cache"})


def _is_transient_tree_path(relative: Path) -> bool:
    """Exclude deterministic build byproducts, never authored package inputs."""
    parts = relative.parts
    return (
        bool(parts and parts[0] in _TRANSIENT_ROOT_DIRECTORIES)
        or "__pycache__" in parts
        or relative.suffix == ".pyc"
        or any(part.endswith(".egg-info") for part in parts)
    )


def package_proof_id(entry: dict[str, Any]) -> str:
    """Return the canonical content identity for one package proof entry."""
    material_entry = dict(entry)
    material_entry.pop("proof_id", None)
    forbidden = {"proved_at", "generated_at", "timestamp"} & set(material_entry)
    if forbidden:
        raise ValueError(
            f"canonical package proof contains non-deterministic fields: {sorted(forbidden)}"
        )
    material = json.dumps(
        material_entry,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "PACKAGE-PROOF-" + hashlib.sha256(material).hexdigest().upper()


def _update_file(hasher: Any, root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    hasher.update(relative.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(path.read_bytes())
    hasher.update(b"\0")


def _update_tree(hasher: Any, repo_root: Path, relative_root: str) -> None:
    root = (repo_root / relative_root).resolve()
    resolved_repo = repo_root.resolve()
    if root != resolved_repo and resolved_repo not in root.parents:
        raise ValueError(f"proof input escapes repository: {relative_root}")
    if not root.is_dir():
        raise FileNotFoundError(f"proof input directory missing: {relative_root}")
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if _is_transient_tree_path(Path(relative)):
            continue
        hasher.update(f"{relative_root.rstrip('/')}/{relative}".encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")


def proof_input_digest(repo_root: Path, package: dict[str, Any]) -> str:
    """Hash the complete local input closure that gives an install proof meaning.

    Source-only binding is insufficient: a matrix import target, builder, proof
    test, dependency source, or requirements change can alter the observed
    result without touching ``src/python/<format>``.
    """
    repo_root = Path(repo_root).resolve()
    hasher = hashlib.sha256()
    canonical_package = json.dumps(
        package,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    hasher.update(b"package-matrix-entry\0")
    hasher.update(canonical_package)
    hasher.update(b"\0")

    source_path = package.get("source_path") or f"src/python/{package['format_id']}"
    _update_tree(hasher, repo_root, source_path)
    for dependency in sorted(
        package.get("local_dependencies") or [],
        key=lambda item: (item["package_name"], item["source_path"]),
    ):
        _update_tree(hasher, repo_root, dependency["source_path"])

    for relative in PROOF_RUNTIME_INPUTS:
        path = repo_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"proof runtime input missing: {relative}")
        _update_file(hasher, repo_root, path)
    return hasher.hexdigest()


def source_digest(repo_root: Path, fmt: str, *, committed: bool = False) -> str:
    """Deterministic content hash of src/python/<fmt>/ — binds a proof to the
    exact source state it was produced from. Sorted walk; ignores bytecode
    caches and egg-info metadata (they vary without source meaning changing).

    When committed=True, reads from git HEAD instead of the working tree.
    This eliminates flapping when concurrent agents modify source files."""
    if committed:
        return _source_digest_committed(repo_root, fmt)
    src = Path(repo_root) / "src" / "python" / fmt
    h = hashlib.sha256()
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src).as_posix()
        if _is_transient_tree_path(Path(rel)):
            continue
        h.update(rel.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _source_digest_committed(repo_root: Path, fmt: str) -> str:
    """Compute source_digest from git HEAD — immune to working-tree races."""
    from committed_fs import committed_list_files, committed_read_bytes

    prefix = f"src/python/{fmt}"
    files = committed_list_files(repo_root, prefix)
    h = hashlib.sha256()
    for fpath in files:
        rel = fpath[len(prefix) + 1:]  # strip prefix + /
        if "__pycache__" in rel or rel.endswith(".pyc") or ".egg-info" in rel:
            continue
        h.update(rel.encode("utf-8"))
        h.update(committed_read_bytes(repo_root, fpath))
    return h.hexdigest()
