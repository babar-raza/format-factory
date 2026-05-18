"""Runtime AI-import guard — scans src/python/ and src/net/ for forbidden imports.

Blocks imports/references to AI libraries and env vars in product source.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from tools.ai.schemas.models import RuntimeGuardResult


def _load_forbidden_patterns(contracts_dir: Path) -> dict:
    """Load forbidden patterns from YAML contract."""
    contract_path = contracts_dir / "forbidden-runtime-imports.yaml"
    if not contract_path.exists():
        return {
            "forbidden_imports": [],
            "forbidden_env_references": [],
            "forbidden_url_references": [],
        }
    with open(contract_path) as f:
        return yaml.safe_load(f)


def scan_directory(
    directory: Path,
    forbidden_imports: list[str],
    forbidden_env_refs: list[str],
    forbidden_url_refs: list[str],
) -> list[dict[str, str]]:
    """Scan a directory for forbidden AI patterns."""
    violations: list[dict[str, str]] = []

    if not directory.exists():
        return violations

    # Scan Python files
    for ext in ("*.py", "*.cs", "*.csproj"):
        for filepath in directory.rglob(ext):
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for pattern in forbidden_imports:
                if pattern in content:
                    violations.append({
                        "file": str(filepath),
                        "pattern": pattern,
                        "type": "forbidden_import",
                    })

            for pattern in forbidden_env_refs:
                if pattern in content:
                    violations.append({
                        "file": str(filepath),
                        "pattern": pattern,
                        "type": "forbidden_env_reference",
                    })

            for pattern in forbidden_url_refs:
                if pattern in content:
                    violations.append({
                        "file": str(filepath),
                        "pattern": pattern,
                        "type": "forbidden_url_reference",
                    })

    return violations


def run_guard(repo_root: Path) -> RuntimeGuardResult:
    """Run the full runtime guard scan on src/python/ and src/net/."""
    contracts_dir = repo_root / "tools" / "ai" / "contracts"
    patterns = _load_forbidden_patterns(contracts_dir)

    forbidden_imports = patterns.get("forbidden_imports", [])
    forbidden_env = patterns.get("forbidden_env_references", [])
    forbidden_urls = patterns.get("forbidden_url_references", [])

    scanned_paths = []
    all_violations: list[dict[str, str]] = []

    for subdir in ["src/python", "src/net"]:
        path = repo_root / subdir
        scanned_paths.append(str(path))
        violations = scan_directory(path, forbidden_imports, forbidden_env, forbidden_urls)
        all_violations.extend(violations)

    return RuntimeGuardResult(
        scanned_paths=scanned_paths,
        violations=all_violations,
        passed=len(all_violations) == 0,
    )
