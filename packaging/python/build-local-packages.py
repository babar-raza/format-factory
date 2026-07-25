"""
build-local-packages.py — Local (non-publishing) package build script.

Reads package-matrix.yaml, then:
1. Builds `native_pyproject` entries from their authoritative source tree.
2. Retains template staging for explicitly legacy entries.
3. Builds declared local dependency projects before their consumer.
4. Attempts `python -m build --wheel --sdist` for each selected package.
5. Records checksums and sizes.
6. Does NOT publish to PyPI or any external registry.

publication_authorized: false
commercial_ready: false
Sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGE_MATRIX = REPO_ROOT / "packaging" / "python" / "package-matrix.yaml"
TEMPLATE = REPO_ROOT / "packaging" / "python" / "pyproject.template.toml"
BUILD_DIR = REPO_ROOT / ".local" / "package-builds" / "python-foss"
SRC_PYTHON = REPO_ROOT / "src" / "python"

# Package descriptions and dependencies live in package-matrix.yaml (single source
# of truth since the GAP-FORENSIC-001 heal). Do not add per-package dicts here.


def _ignore_transient_source(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name
        in {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "build",
            "dist",
        }
        or name.endswith((".pyc", ".pyo", ".egg-info"))
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _project_metadata(source_dir: Path) -> tuple[str, str]:
    pyproject_path = source_dir / "pyproject.toml"
    if not pyproject_path.is_file():
        raise ValueError(f"native_pyproject source has no pyproject.toml: {source_dir}")
    with pyproject_path.open("rb") as fh:
        project = tomllib.load(fh).get("project") or {}
    name = project.get("name")
    version = project.get("version")
    if not isinstance(name, str) or not name:
        raise ValueError(f"native pyproject has no [project].name: {pyproject_path}")
    if not isinstance(version, str) or not version:
        raise ValueError(f"native pyproject has no [project].version: {pyproject_path}")
    return name, version


def _build_source(source_dir: Path, package_name: str, version: str) -> dict:
    """Build one source tree into its content-owned central artifact directory."""
    pkg_dir = BUILD_DIR / package_name
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "package_name": package_name,
        "version": version,
        "build_dir": str(source_dir),
        "artifacts": [],
        "status": "unknown",
        "error": None,
    }

    # Inject user site-packages so build/hatchling are found even via system Python.
    import site as _site

    user_sp = _site.getusersitepackages()
    env = os.environ.copy()
    existing_pypath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (user_sp + os.pathsep + existing_pypath).rstrip(os.pathsep)
    # PEP 427 ZIP member timestamps otherwise inherit mutable source/build times.
    # The repository's native build adapters use the same stable epoch for sdists.
    env["SOURCE_DATE_EPOCH"] = "315532800"

    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--sdist",
                "--outdir",
                str(dist_dir),
                str(source_dir),
            ],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        if proc.returncode == 0:
            result["status"] = "built"
            for artifact in sorted(dist_dir.iterdir()):
                result["artifacts"].append(
                    {
                        "file": artifact.name,
                        "size_bytes": artifact.stat().st_size,
                        "sha256": sha256_file(artifact),
                    }
                )
            dist_latest = pkg_dir / "dist-latest"
            if dist_latest.exists():
                shutil.rmtree(dist_latest)
            shutil.copytree(dist_dir, dist_latest)
        else:
            result["status"] = "build_failed"
            result["error"] = proc.stderr[-2000:] if proc.stderr else proc.stdout[-2000:]
    except FileNotFoundError:
        result["status"] = "build_backend_unavailable"
        result["error"] = "python -m build not available (install: pip install build)"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
    return result


def _build_native_project(
    source_path: str,
    expected_name: str,
    version_override: str | None = None,
) -> dict:
    source_dir = (REPO_ROOT / source_path).resolve()
    if REPO_ROOT.resolve() not in source_dir.parents:
        raise ValueError(f"native source_path escapes repository: {source_path}")
    actual_name, actual_version = _project_metadata(source_dir)
    if actual_name != expected_name:
        raise ValueError(
            f"matrix package_name {expected_name!r} does not match native project {actual_name!r}"
        )
    if version_override is not None and version_override != actual_version:
        raise ValueError(
            f"--version {version_override!r} cannot override native project version "
            f"{actual_version!r}; edit the authoritative pyproject instead"
        )
    result = _build_source(source_dir, actual_name, actual_version)
    result["module"] = None
    result["build_mode"] = "native_pyproject"
    return result


def build_package(pkg: dict, version: str | None = None) -> dict:
    """Build a native project or stage a legacy project, then build artifacts.

    `pkg` is the full package-matrix.yaml entry; description and dependencies
    come from the matrix, not from local dicts.
    """
    if pkg.get("build_mode", "legacy_staging") == "native_pyproject":
        dependency_results = []
        for dependency in pkg.get("local_dependencies") or []:
            dependency_results.append(
                _build_native_project(
                    dependency["source_path"],
                    dependency["package_name"],
                )
            )
        failed_dependencies = [
            result for result in dependency_results if result["status"] != "built"
        ]
        if failed_dependencies:
            return {
                "package_name": pkg["package_name"],
                "module": pkg["module_import"],
                "version": None,
                "build_mode": "native_pyproject",
                "build_dir": str(REPO_ROOT / pkg["source_path"]),
                "artifacts": [],
                "status": "dependency_build_failed",
                "error": failed_dependencies,
                "local_dependencies": dependency_results,
            }
        result = _build_native_project(
            pkg["source_path"],
            pkg["package_name"],
            version,
        )
        result["module"] = pkg["module_import"]
        result["local_dependencies"] = dependency_results
        return result

    version = version or "0.1.0.dev0"
    module = pkg["module_import"]
    package_name = pkg["package_name"]
    pkg_dir = BUILD_DIR / package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Copy source into build staging
    src = SRC_PYTHON / module
    dst_src = pkg_dir / "src" / "python" / module
    if dst_src.exists():
        shutil.rmtree(dst_src)
    shutil.copytree(src, dst_src, ignore=_ignore_transient_source)

    # Write README
    (pkg_dir / "README.md").write_text(
        f"# {package_name}\n\n"
        f"**ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE**\n\n"
        f"Minimal FOSS implementation for the `{module}` format.\n\n"
        f"- `publication_authorized: false`\n"
        f"- `commercial_product_ready: false`\n"
        f"- Capability: alpha-foss-preview\n",
        encoding="utf-8",
    )

    # Instantiate pyproject.toml (description/dependencies from the matrix entry)
    template = TEMPLATE.read_text(encoding="utf-8")
    pyproject = (
        template
        .replace("{{PACKAGE_NAME}}", package_name)
        .replace("{{MODULE_NAME}}", module)
        .replace("{{VERSION}}", version)
        .replace("{{DESCRIPTION}}", pkg.get("description") or f"Minimal FOSS {module} codec")
        .replace("{{DEPENDENCIES}}", json.dumps(pkg.get("dependencies") or []))
    )
    (pkg_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8")

    result = {
        "package_name": package_name,
        "module": module,
        "version": version,
        "build_dir": str(pkg_dir),
        "artifacts": [],
        "status": "unknown",
        "error": None,
    }

    built = _build_source(pkg_dir, package_name, version)
    built["module"] = module
    built["build_mode"] = "legacy_staging"
    return built


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build local Python FOSS packages")
    parser.add_argument("--format", default=None, help="Build only this format (e.g. fods)")
    parser.add_argument("--version", default=None, help="Override version (e.g. 0.1.0)")
    args = parser.parse_args()

    try:
        import yaml
    except ImportError:
        # No silent partial-fleet fallback: building a hardcoded subset while
        # claiming a fleet build is exactly the drift GAP-FORENSIC-001 came from.
        print("ERROR: PyYAML required to read package-matrix.yaml (pip install pyyaml)")
        return 1
    with open(PACKAGE_MATRIX, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    packages = matrix["packages"]

    if args.format:
        packages = [p for p in packages if p["format_id"] == args.format]
        if not packages:
            print(f"ERROR: format '{args.format}' not found in package matrix")
            return 1

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for pkg in packages:
        module = pkg["module_import"]
        name = pkg["package_name"]
        version = args.version
        display_version = version or (
            "native" if pkg.get("build_mode") == "native_pyproject" else "0.1.0.dev0"
        )
        print(f"Building {name} (module: {module}, version: {display_version}) ...")
        r = build_package(pkg, version)
        results.append(r)
        status = r["status"]
        print(f"  -> {status}", end="")
        if r.get("artifacts"):
            print(f" ({len(r['artifacts'])} artifact(s))")
        else:
            print()
        if r.get("artifacts"):
            for a in r["artifacts"]:
                print(f"    {a['file']} ({a['size_bytes']} bytes, sha256={a['sha256'][:16]}...)")

    report_path = BUILD_DIR / "build-report.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nReport written to: {report_path}")

    # Summary
    built = sum(1 for r in results if r["status"] == "built")
    failed = sum(1 for r in results if r["status"] not in ("built",))
    print(f"\nBuilt: {built}/{len(results)}, Issues: {failed}")
    print("\nNOTE: publication_authorized=false. Do NOT upload to PyPI.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
