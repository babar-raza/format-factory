"""V110 — dotnet-path-canonical: block prohibited src/dotnet/ product paths.

Scans evidence declarations for references to src/dotnet/open-source or
src/dotnet/commercial in changed_files, evidence_paths, or work_item files.

Historical documentation mentions (e.g. in docs/history/ or prohibition notices)
are NOT blocked — this validator only fires when a path appears as an active
product source path in a declaration.

Authority: registry/repository-layout.yaml
"""

from governance_validators_contract import validator  # noqa: F401
# Paths prohibited in active product declarations.
# src/dotnet/ itself (without a product subdir) is allowed in docs/history/;
# only the never-to-be-created product subdirectories are blocked here.
_PROHIBITED_ACTIVE_PATHS = [
    "src/dotnet/open-source",
    "src/dotnet/commercial",
]


@validator(rule_id="V_VALIDATE_DOTNET_PATH_CANONICAL", domain="path")
def validate_dotnet_path_canonical(
    declaration: dict, repo_root=None
) -> dict:
    """V110: No changed_files, evidence_paths, or work_item files may reference
    prohibited src/dotnet/ product paths.

    Args:
        declaration: Evidence declaration dict (from evidence-declaration.yaml).
        repo_root: Unused; accepted for runner compatibility.

    Returns:
        Validator result dict with keys: validator_id, rule, status,
        blocks_sprint, violations (on FAIL), summary.
    """
    violations = []

    def _check(paths, context: str) -> None:
        for p in paths or []:
            normalized = str(p).replace("\\", "/")
            for prohibited in _PROHIBITED_ACTIVE_PATHS:
                if prohibited in normalized:
                    violations.append(
                        {
                            "context": context,
                            "offending_path": normalized,
                            "prohibited_pattern": prohibited,
                            "canonical": "src/net/{format}/",
                            "authority": "registry/repository-layout.yaml",
                            "remediation": (
                                "Use resolve_product_path('dotnet', format_id) "
                                "from tools/supervisor/path_resolver.py"
                            ),
                        }
                    )

    _check(declaration.get("changed_files", []), "changed_files")
    _check(declaration.get("evidence_paths", []), "evidence_paths")

    for item in declaration.get("planned_work_items", []):
        item_id = item.get("id", "?")
        _check(item.get("files", []), f"work_item:{item_id}.files")

    if violations:
        return {
            "validator_id": "V110",
            "rule": "dotnet-path-canonical",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations,
            "summary": (
                f"{len(violations)} reference(s) to prohibited src/dotnet/ product path(s). "
                "The canonical .NET product source root is src/net/. "
                "See registry/repository-layout.yaml."
            ),
        }

    return {
        "validator_id": "V110",
        "rule": "dotnet-path-canonical",
        "status": "PASS",
        "blocks_sprint": False,
        "violations": [],
        "summary": "No prohibited src/dotnet/ product paths found in declaration.",
    }
