"""verify_package_install.py — Package install verifier (CT-INSTALL-001).

Handles three installation types:
  DIRECTORY   — non-editable copy in site-packages (sha256 comparison)
  EDITABLE    — PEP 660 / legacy .pth editable (source IS the install; no sync needed)
  NOT_INSTALLED — package missing entirely (error)

NOT_INSTALLED never produces "All packages in sync."

Usage:
    python tools/assurance/verify_package_install.py [--pkg PKG] [--fix]

Exit codes:
    0 — all packages in sync or editable (no action required)
    1 — at least one NOT_INSTALLED, SOURCE_MISSING, or STALE file found
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_ROOT = REPO_ROOT / "src" / "python"
VENV_ROOT = REPO_ROOT / ".venv" / "Lib" / "site-packages"

PACKAGES = ["abw", "sylk", "zst", "dif"]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _detect_install_type(pkg: str, site_packages: Path) -> str:
    """Return install type for pkg.

    Returns one of: 'DIRECTORY', 'EDITABLE_PTH', 'EDITABLE_DIRECT_URL', 'NOT_INSTALLED'.
    """
    if (site_packages / pkg).is_dir():
        return "DIRECTORY"

    # PEP 660 / legacy editable: __editable__.*{pkg}*.pth or {pkg}.pth
    pth_matches = list(site_packages.glob(f"*{pkg}*.pth")) + list(site_packages.glob(f"{pkg}.pth"))
    if pth_matches:
        return "EDITABLE_PTH"

    # PEP 660 via direct_url.json with editable flag
    for dist_info in site_packages.glob(f"{pkg}-*.dist-info"):
        direct_url = dist_info / "direct_url.json"
        if direct_url.exists():
            try:
                data = json.loads(direct_url.read_text(encoding="utf-8"))
                if data.get("dir_info", {}).get("editable") or data.get("editable"):
                    return "EDITABLE_DIRECT_URL"
            except Exception:
                pass

    return "NOT_INSTALLED"


def check_package(pkg: str, fix: bool = False, site_packages: Path | None = None) -> list[dict]:
    """Check one package. Returns list of finding dicts."""
    sp = site_packages if site_packages is not None else VENV_ROOT
    src_dir = SRC_ROOT / pkg

    if not src_dir.exists():
        return [{"file": pkg, "status": "SOURCE_MISSING", "action": "error"}]

    install_type = _detect_install_type(pkg, sp)

    if install_type in ("EDITABLE_PTH", "EDITABLE_DIRECT_URL"):
        return [{"file": pkg, "status": "EDITABLE_INSTALL",
                 "install_type": install_type, "action": "none"}]

    if install_type == "NOT_INSTALLED":
        return [{"file": pkg, "status": "NOT_INSTALLED", "action": "error"}]

    # DIRECTORY: compare source vs installed
    installed_dir = sp / pkg
    findings = []
    for src_file in sorted(src_dir.rglob("*.py")):
        rel = src_file.relative_to(src_dir)
        installed_file = installed_dir / rel

        if not installed_file.exists():
            findings.append({"file": str(rel), "status": "MISSING_IN_INSTALL",
                              "action": "copy" if fix else "report"})
            if fix:
                installed_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, installed_file)
            continue

        src_hash = _sha256(src_file)
        inst_hash = _sha256(installed_file)
        if src_hash != inst_hash:
            findings.append({
                "file": str(rel), "status": "STALE",
                "src_hash": src_hash[:12], "inst_hash": inst_hash[:12],
                "action": "copy" if fix else "report",
            })
            if fix:
                shutil.copy2(src_file, installed_file)
        else:
            findings.append({"file": str(rel), "status": "IN_SYNC", "action": "none"})

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify package installs are present and in sync."
    )
    parser.add_argument("--pkg", choices=PACKAGES, help="Check only this package")
    parser.add_argument("--fix", action="store_true",
                        help="Copy stale files from src to site-packages")
    args = parser.parse_args(argv)

    pkgs = [args.pkg] if args.pkg else PACKAGES
    any_error = False

    for pkg in pkgs:
        findings = check_package(pkg, fix=args.fix)
        errors = [f for f in findings if f["status"] in
                  ("NOT_INSTALLED", "SOURCE_MISSING", "STALE", "MISSING_IN_INSTALL")
                  and not args.fix]
        editable = [f for f in findings if f["status"] == "EDITABLE_INSTALL"]
        synced = [f for f in findings if f["status"] == "IN_SYNC"]

        if editable:
            print(f"[{pkg}] EDITABLE install ({editable[0]['install_type']}) — source is install, no sync needed")
        elif errors:
            for f in errors:
                print(f"[{pkg}] {f['status']}: {f['file']}")
                if "src_hash" in f:
                    print(f"       src={f['src_hash']}... inst={f['inst_hash']}...")
        else:
            stale = [f for f in findings if f["status"] in ("STALE", "MISSING_IN_INSTALL")]
            print(f"[{pkg}] {len(synced)} in sync, {len(stale)} stale")

        if errors:
            any_error = True

    if any_error:
        print("\nErrors found. Run --fix to sync non-editable installs, "
              "or reinstall: pip install -e src/python/{pkg}")
        return 1

    print("\nAll packages verified (in sync or editable).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
