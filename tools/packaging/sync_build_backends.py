"""Keep every distribution's reproducible-build backend identical to one source.

PEP 517 resolves `backend-path` relative to the package directory, and each
Format Factory distribution must stay independently publishable, so a shared
import is not available at build time -- every distribution needs its own copy
of the adapter. Copies drift. Measured 2026-08-04 across the six FF6 packages:
four carried the adapter in three different formattings (ipynb, nrrd, and an
identical xliff/ubl pair), and two did not carry it at all.

Those two, core and safetensors, failed the reproducible-build gate: identical
wheels, differing sdists on consecutive builds. `format-factory-core` is the
shared dependency of all six libraries, so its sdist being non-reproducible
undermines the reproducibility claim for the whole program.

This tool writes the canonical template into each package and can verify no copy
has drifted, so the defect is closed by construction rather than by vigilance.

Usage:
    python tools/packaging/sync_build_backends.py --check     # CI / validator
    python tools/packaging/sync_build_backends.py --write     # apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "tools" / "packaging" / "reproducible_build_backend.py.template"
BACKEND_FILENAME = "_build_backend.py"

# The FF6 production libraries plus the shared core they all depend on.
# OpenRaster has no source tree yet (GAP-021) and so has no distribution.
MANAGED_PACKAGES = ("core", "ipynb", "nrrd", "safetensors", "ubl", "xliff")

PYPROJECT_BUILD_SYSTEM = """[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "_build_backend"
backend-path = ["."]
"""


def package_dir(name: str) -> Path:
    return REPO_ROOT / "src" / "python" / name


def check() -> list[str]:
    """Return a list of problems. Empty means every copy is canonical."""
    canonical = TEMPLATE.read_text(encoding="utf-8")
    problems: list[str] = []

    for name in MANAGED_PACKAGES:
        directory = package_dir(name)
        if not directory.is_dir():
            problems.append(f"{name}: no package directory at {directory}")
            continue

        backend = directory / BACKEND_FILENAME
        if not backend.exists():
            problems.append(
                f"{name}: {BACKEND_FILENAME} is absent -- sdists will not be reproducible"
            )
        elif backend.read_text(encoding="utf-8") != canonical:
            problems.append(f"{name}: {BACKEND_FILENAME} has drifted from the template")

        pyproject = directory / "pyproject.toml"
        if not pyproject.exists():
            problems.append(f"{name}: no pyproject.toml")
            continue
        text = pyproject.read_text(encoding="utf-8")
        if 'build-backend = "_build_backend"' not in text:
            problems.append(
                f"{name}: pyproject.toml does not select the reproducible backend"
            )
        elif 'backend-path = ["."]' not in text:
            problems.append(f"{name}: pyproject.toml selects the backend without backend-path")

        # A distribution that selects an in-tree backend but does not ship it in
        # the sdist cannot be built from that sdist -- `python -m build` fails at
        # "Building wheel from sdist" with "Backend '_build_backend' is not
        # available". Found exactly this way on core and safetensors.
        manifest = directory / "MANIFEST.in"
        if not manifest.exists():
            problems.append(
                f"{name}: no MANIFEST.in, so the sdist omits {BACKEND_FILENAME} "
                "and cannot be built from"
            )
        elif BACKEND_FILENAME not in manifest.read_text(encoding="utf-8"):
            problems.append(
                f"{name}: MANIFEST.in does not include {BACKEND_FILENAME}; "
                "the sdist would be unbuildable"
            )

    return problems


def write() -> list[str]:
    """Write the canonical backend into every managed package. Returns changes made."""
    canonical = TEMPLATE.read_text(encoding="utf-8")
    changes: list[str] = []

    for name in MANAGED_PACKAGES:
        directory = package_dir(name)
        if not directory.is_dir():
            continue

        backend = directory / BACKEND_FILENAME
        existing = backend.read_text(encoding="utf-8") if backend.exists() else None
        if existing != canonical:
            backend.write_text(canonical, encoding="utf-8")
            changes.append(
                f"{name}: {'updated' if existing is not None else 'created'} {BACKEND_FILENAME}"
            )

        manifest = directory / "MANIFEST.in"
        manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
        if BACKEND_FILENAME not in manifest_text:
            lines = [f"include {BACKEND_FILENAME}"]
            for optional in ("CHANGELOG.md", "SECURITY.md", "requirements-build.lock"):
                if (directory / optional).exists() and optional not in manifest_text:
                    lines.append(f"include {optional}")
            addition = "\n".join(lines) + "\n"
            manifest.write_text(addition + manifest_text, encoding="utf-8")
            changes.append(
                f"{name}: MANIFEST.in now ships {BACKEND_FILENAME} in the sdist"
            )

        pyproject = directory / "pyproject.toml"
        if not pyproject.exists():
            continue
        text = pyproject.read_text(encoding="utf-8")
        if 'build-backend = "_build_backend"' in text and 'backend-path = ["."]' in text:
            continue
        if 'build-backend = "setuptools.build_meta"' not in text:
            changes.append(f"{name}: MANUAL -- unrecognised [build-system], not rewritten")
            continue
        # Replace only the build-backend line and add backend-path beside it, so
        # nothing else in the file moves.
        updated = text.replace(
            'build-backend = "setuptools.build_meta"',
            'build-backend = "_build_backend"\nbackend-path = ["."]',
        )
        pyproject.write_text(updated, encoding="utf-8")
        changes.append(f"{name}: pyproject.toml now selects the reproducible backend")

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="report drift, change nothing")
    group.add_argument("--write", action="store_true", help="write the canonical backend")
    arguments = parser.parse_args()

    if arguments.check:
        problems = check()
        if problems:
            print("build-backend drift detected:", file=sys.stderr)
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            return 1
        print(f"all {len(MANAGED_PACKAGES)} managed packages carry the canonical backend")
        return 0

    changes = write()
    if not changes:
        print("no changes -- every managed package was already canonical")
        return 0
    for change in changes:
        print(f"  {change}")
    remaining = check()
    if remaining:
        print("still not canonical after writing:", file=sys.stderr)
        for problem in remaining:
            print(f"  {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
