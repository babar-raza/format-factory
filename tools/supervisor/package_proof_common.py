"""package_proof_common.py — shared logic for the package-install-proof system.

Single implementation of the source digest used by BOTH the proof orchestrator
(tools/run_package_install_proof.py) and the V226 coverage validator
(governance_validators_package_proof.py). Two copies of this function would
drift and silently break staleness detection — do not duplicate it.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

PROOF_MANIFEST_REL = "reports/package-install-proof/proof-manifest.json"
PACKAGE_MATRIX_REL = "packaging/python/package-matrix.yaml"


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
        if "__pycache__" in rel or rel.endswith(".pyc") or ".egg-info" in rel:
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
