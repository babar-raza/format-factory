"""Independent-repository-extraction gate.

product-goal.yaml's own completion_invariants declare: "Every distribution
extracts to an independent repository with preserved canonical source and
package digests." No prior tool in this repository tested this claim --
reproducible_build_gate.py proves TWO in-place builds of the same source
agree; run_package_install_proof.py always builds from src/python/{format}/
inside this monorepo. Neither ever copies a format's own source tree OUT of
the monorepo and builds it there, which is the literal claim this invariant
makes: that a format's own src/python/{format}/ directory is genuinely
self-contained -- buildable with zero access to sibling format directories,
repo-root config files, or any other monorepo-only context -- exactly as
product-goal.yaml's own opening line requires ("each independently built...
without requiring the others").

This gate copies src/python/{format}/ verbatim into a fresh directory
OUTSIDE this repository (the OS temp directory, a different filesystem
location entirely, simulating "an independent repository"), verifies the
copy is byte-identical to the original file-by-file (the "preserved
canonical source" half), builds a wheel+sdist from the isolated copy with
its own cwd (never REPO_ROOT), builds a second wheel+sdist from the
in-place source at the identical SOURCE_DATE_EPOCH, and compares digests
(the "preserved... package digests" half). A build that only succeeds
because REPO_ROOT happens to be an ancestor directory, or that produces a
different digest once genuinely isolated, fails this gate.

Usage:
    python tools/certification/independent_repository_extraction_gate.py \
        --format xliff \
        --output reports/certification/xliff/independent-repository-extraction-gate.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
# Matches build-local-packages.py's own reproducible_build_gate.py sibling --
# a build here must agree with the isolated build at the same epoch.
BUILD_EPOCH = "315532800"

_IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist"}


def _iter_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _IGNORED_NAMES or part.endswith((".pyc", ".pyo", ".egg-info")) for part in path.parts):
            continue
        files.append(path)
    return files


def _tree_digests(root: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in _iter_source_files(root):
        relative = path.relative_to(root).as_posix()
        digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def _copy_tree_ignoring_build_artifacts(source: Path, destination: Path) -> None:
    def _ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in _IGNORED_NAMES or name.endswith((".pyc", ".pyo", ".egg-info"))
        }

    shutil.copytree(source, destination, ignore=_ignore)


def _build(source_dir: Path, out_dir: Path, *, cwd: Path) -> dict[str, Any]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # setuptools' legacy build_py incrementally reuses an existing build/lib/
    # directory rather than clearing it first. A stale build/ left over from
    # an earlier source layout can silently ship a file the current src/
    # tree no longer has (found directly this tick: xliff/build/lib/.../
    # validation/xliff_core_2.0.xsd, an orphaned duplicate of the current
    # validation/schemas/xliff_core_2.0.xsd, from before that file moved).
    # A comparison against a build/ dir in this state is not evidence of
    # anything -- clear it so both sides of the comparison start clean,
    # matching what a genuine fresh checkout would see.
    stale_build_dir = source_dir / "build"
    if stale_build_dir.exists():
        shutil.rmtree(stale_build_dir)

    environment = dict(os.environ)
    environment["SOURCE_DATE_EPOCH"] = BUILD_EPOCH
    environment["PYTHONHASHSEED"] = "0"

    started = time.time()
    completed = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
            "-m",
            "build",
            "--wheel",
            "--sdist",
            "--outdir",
            str(out_dir),
            str(source_dir),
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=str(cwd),
        env=environment,
    )
    seconds = round(time.time() - started, 1)
    if completed.returncode != 0:
        return {
            "ok": False,
            "seconds": seconds,
            "stderr_tail": completed.stderr[-3000:],
            "stdout_tail": completed.stdout[-3000:],
        }

    artifacts = sorted(path for path in out_dir.iterdir() if path.is_file())
    return {
        "ok": True,
        "seconds": seconds,
        "artifacts": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    format_id = arguments.format_id
    source_dir = SRC_PYTHON / format_id
    if not source_dir.is_dir():
        raise SystemExit(f"no such source directory: {source_dir}")

    original_digests = _tree_digests(source_dir)

    # A genuinely independent location: the OS temp directory, not merely a
    # subdirectory of this repository's own .local/ scratch space -- the
    # isolated build's own cwd must have REPO_ROOT nowhere in its ancestry.
    isolated_root = Path(tempfile.mkdtemp(prefix=f"ff6-independent-repo-{format_id}-"))
    try:
        isolated_source = isolated_root / format_id
        print(f"copying {source_dir} -> {isolated_source} (outside the repository) ...", flush=True)
        _copy_tree_ignoring_build_artifacts(source_dir, isolated_source)

        isolated_digests = _tree_digests(isolated_source)
        source_preserved = original_digests == isolated_digests

        print("building from the isolated copy (cwd outside the repository) ...", flush=True)
        isolated_build = _build(isolated_source, isolated_root / "dist", cwd=isolated_root)

        print("building from the in-place monorepo source (control) ...", flush=True)
        in_place_out = REPO_ROOT / ".local" / "independent-repository-extraction" / format_id
        in_place_build = _build(source_dir, in_place_out, cwd=REPO_ROOT)

        extraction_standard = REPO_ROOT / "docs" / "governance" / "python-library-extraction-standard.md"
        if extraction_standard.exists():
            es_sha256 = hashlib.sha256(extraction_standard.read_bytes()).hexdigest()
            extraction_standard_info: dict[str, Any] = {
                "extraction_standard_present": True,
                "extraction_standard_sha256": es_sha256,
                "governance_seed_files": [
                    {
                        "source": "docs/governance/python-library-extraction-standard.md",
                        "target": "EXTRACTION-STANDARD.md",
                        "sha256": es_sha256,
                    },
                ],
            }
        else:
            extraction_standard_info = {
                "extraction_standard_present": False,
                "extraction_standard_warning": "Extraction standard missing from monorepo",
            }

        result: dict[str, Any] = {
            "format_id": format_id,
            "gate": "independent-repository-extraction",
            "source_dir": str(source_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
            "isolated_location": str(isolated_source),
            "source_file_count": len(original_digests),
            "source_preserved_byte_identical": source_preserved,
            "build_epoch": BUILD_EPOCH,
            "isolated_build": isolated_build,
            "in_place_build": in_place_build,
            **extraction_standard_info,
        }

        if not source_preserved:
            only_in_original = sorted(set(original_digests) - set(isolated_digests))
            only_in_copy = sorted(set(isolated_digests) - set(original_digests))
            differing = sorted(
                path
                for path in set(original_digests) & set(isolated_digests)
                if original_digests[path] != isolated_digests[path]
            )
            result["source_preservation_diff"] = {
                "only_in_original": only_in_original,
                "only_in_copy": only_in_copy,
                "content_differs": differing,
            }

        if not (isolated_build["ok"] and in_place_build["ok"]):
            result["verdict"] = "BUILD_FAILED"
            result["extracts_independently"] = False
        else:
            digests_match = isolated_build["artifacts"] == in_place_build["artifacts"]
            result["package_digests_preserved"] = digests_match
            result["extracts_independently"] = bool(source_preserved and digests_match)
            if not source_preserved:
                result["verdict"] = "SOURCE_NOT_PRESERVED"
            elif not digests_match:
                result["verdict"] = "DIGEST_MISMATCH"
                result["differing_artifacts"] = [
                    name
                    for name, digest in in_place_build["artifacts"].items()
                    if isolated_build["artifacts"].get(name) != digest
                ]
            else:
                result["verdict"] = "EXTRACTS_INDEPENDENTLY"

        output = Path(arguments.output)
        if not output.is_absolute():
            output = REPO_ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in result.items() if k not in ("isolated_build", "in_place_build")}, indent=2))
        print(f"\nwritten to {output}")
        return 0 if result.get("verdict") == "EXTRACTS_INDEPENDENTLY" else 1
    finally:
        shutil.rmtree(isolated_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
