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


def source_digest(repo_root: Path, fmt: str) -> str:
    """Deterministic content hash of src/python/<fmt>/ — binds a proof to the
    exact source state it was produced from. Sorted walk; ignores bytecode
    caches and egg-info metadata (they vary without source meaning changing)."""
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
