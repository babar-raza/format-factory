"""
build-local-packages.py — Local (non-publishing) package build script.

Reads package-matrix.yaml and pyproject.template.toml, then:
1. Instantiates pyproject.toml for each package into .local/package-builds/python-foss/<package>/
2. Attempts `python -m build --wheel --sdist` for each package.
3. Records checksums and sizes.
4. Does NOT publish to PyPI or any external registry.

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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGE_MATRIX = REPO_ROOT / "packaging" / "python" / "package-matrix.yaml"
TEMPLATE = REPO_ROOT / "packaging" / "python" / "pyproject.template.toml"
BUILD_DIR = REPO_ROOT / ".local" / "package-builds" / "python-foss"
SRC_PYTHON = REPO_ROOT / "src" / "python"

PACKAGE_DESCRIPTIONS = {
    "zst": "Minimal FOSS Zstandard (.zst) codec",
    "fodp": "Minimal FOSS Flat OpenDocument Presentation (.fodp) parser",
    "fodg": "Minimal FOSS Flat OpenDocument Graphics (.fodg) parser",
    "gnumeric": "Minimal FOSS Gnumeric spreadsheet (.gnumeric) parser",
    "abw": "Minimal FOSS AbiWord document (.abw) parser",
    "fods": "Minimal FOSS Flat OpenDocument Spreadsheet (.fods) parser",
    "fodt": "Minimal FOSS Flat OpenDocument Text (.fodt) parser",
}

PACKAGE_DEPS = {
    "zst": '["zstandard>=0.21.0"]',
    "fodp": "[]",
    "fodg": "[]",
    "gnumeric": "[]",
    "abw": "[]",
    "fods": "[]",
    "fodt": "[]",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_package(module: str, package_name: str, version: str = "0.1.0.dev0") -> dict:
    """Instantiate template and attempt local wheel/sdist build."""
    pkg_dir = BUILD_DIR / package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Copy source into build staging
    src = SRC_PYTHON / module
    dst_src = pkg_dir / "src" / "python" / module
    if dst_src.exists():
        shutil.rmtree(dst_src)
    shutil.copytree(src, dst_src)

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

    # Instantiate pyproject.toml
    template = TEMPLATE.read_text(encoding="utf-8")
    pyproject = (
        template
        .replace("{{PACKAGE_NAME}}", package_name)
        .replace("{{MODULE_NAME}}", module)
        .replace("{{VERSION}}", version)
        .replace("{{DESCRIPTION}}", PACKAGE_DESCRIPTIONS.get(module, f"Minimal FOSS {module} codec"))
        .replace("{{DEPENDENCIES}}", PACKAGE_DEPS.get(module, "[]"))
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

    # Attempt build
    dist_dir = pkg_dir / "dist"
    dist_dir.mkdir(exist_ok=True)

    # Inject user site-packages so build/hatchling are found even via system Python
    import site as _site
    user_sp = _site.getusersitepackages()
    env = os.environ.copy()
    existing_pypath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (user_sp + os.pathsep + existing_pypath).rstrip(os.pathsep)

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--sdist",
             "--outdir", str(dist_dir), str(pkg_dir)],
            capture_output=True, text=True, timeout=180, env=env,
        )
        if proc.returncode == 0:
            result["status"] = "built"
            for artifact in sorted(dist_dir.iterdir()):
                result["artifacts"].append({
                    "file": artifact.name,
                    "size_bytes": artifact.stat().st_size,
                    "sha256": sha256_file(artifact),
                })
        else:
            result["status"] = "build_failed"
            result["error"] = proc.stderr[-2000:] if proc.stderr else proc.stdout[-2000:]
    except FileNotFoundError:
        result["status"] = "build_backend_unavailable"
        result["error"] = "python -m build not available (install: pip install build)"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"

    return result


def main():
    try:
        import yaml
        with open(PACKAGE_MATRIX, encoding="utf-8") as f:
            matrix = yaml.safe_load(f)
        packages = matrix["packages"]
    except ImportError:
        print("PyYAML not available — using hardcoded package list")
        packages = [
            {"module_import": m, "package_name": f"aspose-format-factory-{m}"}
            for m in ["zst", "fodp", "fodg", "gnumeric", "abw"]
        ]

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for pkg in packages:
        module = pkg["module_import"]
        name = pkg["package_name"]
        print(f"Building {name} (module: {module}) ...")
        r = build_package(module, name)
        results.append(r)
        status = r["status"]
        print(f"  -> {status}")
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
