"""Reproducible-build gate: build a distribution twice and compare digests.

The claim this gate is meant to support is that anyone can rebuild a published
artifact from source and get the same bytes. Two builds agreeing is necessary
but not sufficient evidence for that -- a comparison that could not have
detected a difference proves nothing, and there are several ways to accidentally
write one: comparing a file against itself, comparing digests of paths that both
failed to exist, or letting the second build be served from a cache.

So the gate runs a third build with a deliberately different SOURCE_DATE_EPOCH
and requires it to produce a *different* digest. If all three agree, the
comparison is insensitive to a change it must be sensitive to, and the gate
fails rather than reporting success.

Usage:
    python tools/certification/reproducible_build_gate.py \
        --package-dir src/python/ipynb \
        --output reports/certification/ipynb/reproducible-build.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# The build backend's own default. Two builds must agree at this value.
DEFAULT_EPOCH = "315532800"
# Any other valid epoch. A build here must NOT match, or the comparison is blind.
CONTROL_EPOCH = "1600000000"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_once(package_dir: Path, out_dir: Path, epoch: str) -> dict:
    """Build sdist+wheel into a fresh directory and digest every artifact."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    environment = dict(os.environ)
    environment["SOURCE_DATE_EPOCH"] = epoch
    environment["PYTHONHASHSEED"] = "0"

    started = time.time()
    completed = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
            "-m",
            "build",
            "--outdir",
            str(out_dir),
            str(package_dir),
        ],
        capture_output=True,
        text=True,
        timeout=1800,
        cwd=str(REPO_ROOT),
        env=environment,
    )
    seconds = round(time.time() - started, 1)
    if completed.returncode != 0:
        return {
            "ok": False,
            "epoch": epoch,
            "seconds": seconds,
            "stderr_tail": completed.stderr[-3000:],
            "stdout_tail": completed.stdout[-3000:],
        }

    artifacts = sorted(path for path in out_dir.iterdir() if path.is_file())
    return {
        "ok": True,
        "epoch": epoch,
        "seconds": seconds,
        "artifacts": {path.name: _digest(path) for path in artifacts},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--work-dir",
        default=None,
        help="scratch directory for the three builds (default: .local/reproducible-build)",
    )
    arguments = parser.parse_args()

    package_dir = Path(arguments.package_dir)
    if not package_dir.is_absolute():
        package_dir = REPO_ROOT / package_dir
    work_dir = (
        Path(arguments.work_dir)
        if arguments.work_dir
        else REPO_ROOT / ".local" / "reproducible-build" / package_dir.name
    )

    print("build 1 of 3 (default epoch)", flush=True)
    first = build_once(package_dir, work_dir / "build-1", DEFAULT_EPOCH)
    print("build 2 of 3 (default epoch)", flush=True)
    second = build_once(package_dir, work_dir / "build-2", DEFAULT_EPOCH)
    print("build 3 of 3 (control epoch -- must differ)", flush=True)
    control = build_once(package_dir, work_dir / "build-control", CONTROL_EPOCH)

    result: dict = {
        "package_dir": str(package_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "default_epoch": DEFAULT_EPOCH,
        "control_epoch": CONTROL_EPOCH,
        "build_1": first,
        "build_2": second,
        "build_control": control,
    }

    if not (first["ok"] and second["ok"] and control["ok"]):
        result["verdict"] = "BUILD_FAILED"
        result["reproducible"] = False
    else:
        identical = first["artifacts"] == second["artifacts"]
        control_differs = {
            name: control["artifacts"].get(name) != digest
            for name, digest in first["artifacts"].items()
        }
        # The control only has to move something. A wheel whose only timestamps
        # are already pinned may legitimately match; the sdist must not.
        comparison_is_sensitive = any(control_differs.values())

        result["artifacts_identical_across_two_builds"] = identical
        result["control_epoch_changed_which_artifacts"] = control_differs
        result["comparison_proven_sensitive"] = comparison_is_sensitive
        result["reproducible"] = bool(identical and comparison_is_sensitive)
        if not comparison_is_sensitive:
            result["verdict"] = "COMPARISON_BLIND"
            result["reason"] = (
                "changing SOURCE_DATE_EPOCH changed no artifact digest, so the "
                "comparison cannot detect a difference and the match is not evidence"
            )
        elif not identical:
            result["verdict"] = "NOT_REPRODUCIBLE"
            result["differing"] = [
                name
                for name, digest in first["artifacts"].items()
                if second["artifacts"].get(name) != digest
            ]
        else:
            result["verdict"] = "REPRODUCIBLE"

    output = Path(arguments.output)
    if not output.is_absolute():
        output = REPO_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if not k.startswith("build_")}, indent=2))
    print(f"\nwritten to {output}")
    return 0 if result.get("verdict") == "REPRODUCIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
