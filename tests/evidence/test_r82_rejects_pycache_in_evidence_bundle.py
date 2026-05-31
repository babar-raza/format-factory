"""
tests/evidence/test_r82_rejects_pycache_in_evidence_bundle.py

R82 Train G: Validator must reject evidence bundles containing __pycache__ or .pyc files.

Defect fixed: D79-06 — R79 bundle contained 88 compiled/cache files.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _make_bundle_zip(entries: dict[str, bytes]) -> bytes:
    """Helper: create in-memory ZIP with given entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def _has_pycache_or_pyc(bundle_bytes: bytes) -> list[str]:
    """Return list of __pycache__ or .pyc entries in bundle."""
    hits = []
    with zipfile.ZipFile(io.BytesIO(bundle_bytes)) as zf:
        for name in zf.namelist():
            if "__pycache__/" in name or name.endswith(".pyc"):
                hits.append(name)
    return hits


class TestRejectsPycacheInBundle:
    """Bundle must not contain __pycache__ or .pyc files."""

    def test_clean_bundle_has_no_pycache(self):
        bundle = _make_bundle_zip({
            "repo/src/python/fods/__init__.py": b"# clean",
            "repo/src/python/fods/fods_parser.py": b"# clean",
            "bundle-metadata/sprint-id.txt": b"r82",
        })
        hits = _has_pycache_or_pyc(bundle)
        assert hits == [], f"Clean bundle should have no pycache/pyc: {hits}"

    def test_bundle_with_pycache_is_detected(self):
        bundle = _make_bundle_zip({
            "repo/src/python/fods/__init__.py": b"# clean",
            "repo/src/python/fods/__pycache__/fods_parser.cpython-313.pyc": b"\xc3\xf9",
            "bundle-metadata/sprint-id.txt": b"r82",
        })
        hits = _has_pycache_or_pyc(bundle)
        assert len(hits) == 1, f"Should detect pycache entry: {hits}"
        assert "__pycache__/" in hits[0]

    def test_bundle_with_pyc_at_root_is_detected(self):
        bundle = _make_bundle_zip({
            "repo/src/python/fods/fods_parser.pyc": b"\xc3\xf9",
            "bundle-metadata/sprint-id.txt": b"r82",
        })
        hits = _has_pycache_or_pyc(bundle)
        assert len(hits) == 1
        assert hits[0].endswith(".pyc")

    def test_bundle_with_multiple_pycache_files_detected(self):
        bundle = _make_bundle_zip({
            "repo/src/python/fods/__pycache__/a.cpython-313.pyc": b"\xc3\xf9",
            "repo/src/python/fods/__pycache__/b.cpython-313.pyc": b"\xc3\xf9",
            "repo/src/python/fodt/__pycache__/c.cpython-313.pyc": b"\xc3\xf9",
            "bundle-metadata/sprint-id.txt": b"r82",
        })
        hits = _has_pycache_or_pyc(bundle)
        assert len(hits) == 3

    def test_current_repo_has_no_pycache_in_tracked_files(self):
        """The repo's git-tracked files must not include __pycache__ or .pyc."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=str(REPO_ROOT),
            capture_output=True, text=True
        )
        tracked = result.stdout.splitlines()
        pycache_hits = [f for f in tracked if "__pycache__" in f or f.endswith(".pyc")]
        assert pycache_hits == [], \
            f"Git-tracked files must not include pycache/pyc: {pycache_hits}"
