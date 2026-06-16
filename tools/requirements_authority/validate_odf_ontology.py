"""
Validator: ODF Ontology YAML consumer.
Reads registry/odf-ontology/qname-to-code-map.yaml and validates structure.
Used to confirm the deployed ontology is well-formed and non-empty.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
_ONTOLOGY_ROOT = _REPO / "registry" / "odf-ontology"
_QNAME_MAP = _ONTOLOGY_ROOT / "qname-to-code-map.yaml"


def validate_qname_map() -> dict:
    """Load and validate qname-to-code-map.yaml. Returns validation result dict."""
    try:
        import yaml
    except ImportError:
        return {"ok": False, "error": "pyyaml not installed"}

    if not _QNAME_MAP.exists():
        return {"ok": False, "error": f"qname-to-code-map.yaml not found at {_QNAME_MAP}"}

    with open(_QNAME_MAP, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return {"ok": False, "error": "qname-to-code-map.yaml is not a YAML mapping"}

    mappings = data.get("mappings", {})
    if not mappings:
        return {"ok": False, "error": "mappings key missing or empty"}

    schema_version = data.get("schema_version")
    entry_count = len(mappings)

    issues = []
    for qname, entry in mappings.items():
        if not isinstance(entry, dict):
            issues.append(f"{qname}: entry is not a mapping")
            continue
        if "canonical_class" not in entry:
            issues.append(f"{qname}: missing canonical_class")

    return {
        "ok": len(issues) == 0,
        "schema_version": schema_version,
        "entry_count": entry_count,
        "issues": issues,
        "path": str(_QNAME_MAP),
    }


def validate_all_ontology_files() -> dict:
    """Validate presence and basic structure of all 9 ontology YAMLs."""
    required = [
        "prefix-namespace-registry.yaml",
        "qname-to-code-map.yaml",
        "namespace-tree.yaml",
        "canonical-class-inventory.yaml",
        "attribute-property-map.yaml",
        "containment-graph.yaml",
        "naming-exceptions.yaml",
        "legacy-alias-map.yaml",
        "migration-plan.yaml",
    ]
    results = {}
    for fname in required:
        path = _ONTOLOGY_ROOT / fname
        results[fname] = {"exists": path.exists(), "path": str(path)}

    all_present = all(r["exists"] for r in results.values())
    qname_result = validate_qname_map()

    return {
        "all_files_present": all_present,
        "file_count": len(required),
        "files": results,
        "qname_map_valid": qname_result,
    }


if __name__ == "__main__":
    import json
    result = validate_all_ontology_files()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_files_present"] and result["qname_map_valid"]["ok"] else 1)
