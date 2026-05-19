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


def scan_for_direct_endpoint_calls(directory: Path) -> list[dict[str, str]]:
    """Detect direct HTTP calls to AI endpoints outside gateway."""
    violations: list[dict[str, str]] = []
    if not directory.exists():
        return violations
    direct_call_patterns = [
        "httpx.Client",
        "httpx.AsyncClient",
        "requests.get",
        "requests.post",
        "urllib.request",
    ]
    ai_context_patterns = [
        "llm.professionalize.com",
        "GPT_OSS",
        "PROFESSIONALIZE",
        "/v1/chat",
        "/v1/models",
        "/v1/embeddings",
    ]
    for filepath in directory.rglob("*.py"):
        if filepath.name in ("gateway.py", "model_discovery.py", "capability_probe.py", "runtime_guard.py"):
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        has_direct_call = any(p in content for p in direct_call_patterns)
        has_ai_context = any(p in content for p in ai_context_patterns)
        if has_direct_call and has_ai_context:
            violations.append({
                "file": str(filepath),
                "pattern": "direct_endpoint_call_outside_gateway",
                "type": "direct_endpoint_bypass",
            })
    return violations


def run_guard(repo_root: Path) -> RuntimeGuardResult:
    """Run the full runtime guard scan on src/ and detect direct endpoint bypasses."""
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

    # Phase 2: detect direct endpoint bypasses in tools/ai
    tools_ai = repo_root / "tools" / "ai"
    if tools_ai.exists():
        scanned_paths.append(str(tools_ai))
        bypass_violations = scan_for_direct_endpoint_calls(tools_ai)
        all_violations.extend(bypass_violations)

    return RuntimeGuardResult(
        scanned_paths=scanned_paths,
        violations=all_violations,
        passed=len(all_violations) == 0,
    )
