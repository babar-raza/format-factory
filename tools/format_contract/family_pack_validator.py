"""Validate a format-family policy pack and its routing/readiness closure."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_PACK_KEYS = {
    "schema_version",
    "family",
    "applicability",
    "identity_defaults",
    "scope_defaults",
    "shared_groups",
    "depth_floors",
    "validation_layers",
    "security_defaults",
    "domains",
}
REQUIRED_DOMAIN_KEYS = {
    "domain",
    "category",
    "level",
    "title",
    "production_meaning",
    "developer_use_case",
    "baseline_behavior",
    "fact_keywords",
    "required_tests",
    "release_gates",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _issue(code: str, message: str, path: str = "") -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _semantic_text(domain: dict[str, Any]) -> list[tuple[str, str]]:
    output = [
        ("production_meaning", str(domain.get("production_meaning", ""))),
        ("developer_use_case", str(domain.get("developer_use_case", ""))),
    ]
    for field in ("required_tests", "release_gates"):
        output.extend((field, text) for text in _strings(domain.get(field)))
    for item in domain.get("baseline_behavior", []) or []:
        if isinstance(item, dict):
            output.append(("baseline_behavior", str(item.get("text", ""))))
    return output


def validate_family_pack(
    pack: dict[str, Any],
    family_map: dict[str, Any],
    requirements: dict[str, Any],
    shared_contract: dict[str, Any],
) -> dict[str, Any]:
    """Return a canonical validation report without mutating inputs."""

    issues: list[dict[str, str]] = []
    missing = sorted(REQUIRED_PACK_KEYS.difference(pack))
    for key in missing:
        issues.append(_issue("PACK_FIELD_MISSING", f"missing required field {key!r}", key))

    family = str(pack.get("family", "")).strip()
    if not family:
        issues.append(_issue("FAMILY_ID_MISSING", "family must be a non-empty string", "family"))

    applicability = pack.get("applicability")
    if not isinstance(applicability, dict):
        issues.append(
            _issue(
                "APPLICABILITY_MISSING",
                "applicability must declare representative_formats, semantic_scope, and excluded_concepts",
                "applicability",
            )
        )
        applicability = {}
    representatives = _strings(applicability.get("representative_formats"))
    semantic_scope = str(applicability.get("semantic_scope", "")).strip()
    excluded = [item.casefold() for item in _strings(applicability.get("excluded_concepts"))]
    if not representatives:
        issues.append(
            _issue(
                "REPRESENTATIVE_FORMAT_MISSING",
                "at least one representative format is required",
                "applicability.representative_formats",
            )
        )
    if not semantic_scope:
        issues.append(
            _issue(
                "SEMANTIC_SCOPE_MISSING",
                "semantic_scope must state the family's positive applicability boundary",
                "applicability.semantic_scope",
            )
        )
    if not excluded:
        issues.append(
            _issue(
                "EXCLUSION_BOUNDARY_MISSING",
                "excluded_concepts must name nearby family concepts that must not leak into obligations",
                "applicability.excluded_concepts",
            )
        )

    mapped = family_map.get("map", {})
    if not isinstance(mapped, dict):
        issues.append(_issue("FAMILY_MAP_INVALID", "family map must contain a map mapping", "map"))
        mapped = {}
    for format_id in representatives:
        if mapped.get(format_id) != family:
            issues.append(
                _issue(
                    "REPRESENTATIVE_MAPPING_MISMATCH",
                    f"{format_id!r} maps to {mapped.get(format_id)!r}, expected {family!r}",
                    f"map.{format_id}",
                )
            )

    known_shared = shared_contract.get("groups", {})
    if not isinstance(known_shared, dict):
        known_shared = {}
    shared_groups = pack.get("shared_groups", [])
    if not isinstance(shared_groups, list):
        issues.append(
            _issue("SHARED_GROUPS_INVALID", "shared_groups must be a list", "shared_groups")
        )
        shared_groups = []
    for group in shared_groups:
        if group not in known_shared:
            issues.append(
                _issue(
                    "UNKNOWN_SHARED_GROUP",
                    f"shared group {group!r} does not exist",
                    "shared_groups",
                )
            )

    domains = pack.get("domains", [])
    if not isinstance(domains, list) or not domains:
        issues.append(_issue("DOMAINS_MISSING", "domains must be a non-empty list", "domains"))
        domains = []
    domain_ids: set[str] = set()
    policy_ids: set[str] = set()
    for index, raw_domain in enumerate(domains):
        path = f"domains[{index}]"
        if not isinstance(raw_domain, dict):
            issues.append(_issue("DOMAIN_INVALID", "domain must be a mapping", path))
            continue
        for key in sorted(REQUIRED_DOMAIN_KEYS.difference(raw_domain)):
            issues.append(
                _issue("DOMAIN_FIELD_MISSING", f"missing required field {key!r}", f"{path}.{key}")
            )
        domain_id = str(raw_domain.get("domain", "")).strip()
        if domain_id in domain_ids:
            issues.append(_issue("DUPLICATE_DOMAIN", f"duplicate domain {domain_id!r}", path))
        domain_ids.add(domain_id)
        if raw_domain.get("level") not in {"MUST", "SHOULD", "MAY"}:
            issues.append(
                _issue(
                    "DOMAIN_LEVEL_INVALID",
                    "level must be MUST, SHOULD, or MAY",
                    f"{path}.level",
                )
            )
        behavior = raw_domain.get("baseline_behavior", [])
        if not isinstance(behavior, list) or not behavior:
            issues.append(
                _issue(
                    "BASELINE_BEHAVIOR_MISSING",
                    "baseline_behavior must be a non-empty list",
                    f"{path}.baseline_behavior",
                )
            )
            behavior = []
        for behavior_index, item in enumerate(behavior):
            item_path = f"{path}.baseline_behavior[{behavior_index}]"
            if not isinstance(item, dict):
                issues.append(_issue("BASELINE_BEHAVIOR_INVALID", "item must be a mapping", item_path))
                continue
            policy_id = str(item.get("id", "")).strip()
            text = str(item.get("text", "")).strip()
            if not policy_id.startswith("POL-"):
                issues.append(
                    _issue(
                        "POLICY_ID_INVALID",
                        "baseline behavior IDs must use the POL- policy namespace",
                        f"{item_path}.id",
                    )
                )
            if policy_id in policy_ids:
                issues.append(
                    _issue("DUPLICATE_POLICY_ID", f"duplicate policy ID {policy_id!r}", item_path)
                )
            policy_ids.add(policy_id)
            if not text:
                issues.append(
                    _issue(
                        "BASELINE_TEXT_MISSING",
                        "baseline behavior text must be non-empty",
                        f"{item_path}.text",
                    )
                )
        for field, text in _semantic_text(raw_domain):
            folded = text.casefold()
            for concept in excluded:
                if concept and concept in folded:
                    issues.append(
                        _issue(
                            "EXCLUDED_CONCEPT_LEAK",
                            f"excluded concept {concept!r} appears in requirement text",
                            f"{path}.{field}",
                        )
                    )

    categories = requirements.get("categories", {})
    family_rules = requirements.get("families", {}).get(family)
    if not isinstance(family_rules, dict):
        issues.append(
            _issue(
                "READINESS_POLICY_MISSING",
                f"fact-category requirements have no family entry for {family!r}",
                f"families.{family}",
            )
        )
        family_rules = {}
    required_categories = _strings(family_rules.get("required_categories"))
    weights = family_rules.get("weights", {})
    if not isinstance(weights, dict):
        weights = {}
        issues.append(
            _issue("READINESS_WEIGHTS_INVALID", "weights must be a mapping", f"families.{family}.weights")
        )
    if set(required_categories) != set(weights):
        issues.append(
            _issue(
                "READINESS_WEIGHT_KEYS_MISMATCH",
                "weights must cover exactly the required categories",
                f"families.{family}.weights",
            )
        )
    for category in required_categories:
        if category not in categories:
            issues.append(
                _issue(
                    "UNKNOWN_FACT_CATEGORY",
                    f"unknown fact category {category!r}",
                    f"families.{family}.required_categories",
                )
            )
    try:
        weight_sum = sum(float(value) for value in weights.values())
    except (TypeError, ValueError):
        weight_sum = math.nan
    if not math.isclose(weight_sum, 1.0, rel_tol=0.0, abs_tol=1e-9):
        issues.append(
            _issue(
                "READINESS_WEIGHTS_NOT_NORMALIZED",
                f"readiness weights sum to {weight_sum!r}, expected 1.0",
                f"families.{family}.weights",
            )
        )
    threshold = family_rules.get("threshold")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 < threshold <= 1:
        issues.append(
            _issue(
                "READINESS_THRESHOLD_INVALID",
                "threshold must be numeric in (0, 1]",
                f"families.{family}.threshold",
            )
        )

    return {
        "schema": "format-factory/family-pack-validation@1",
        "family": family,
        "representative_formats": sorted(representatives),
        "domain_count": len(domains),
        "policy_id_count": len(policy_ids),
        "valid": not issues,
        "issues": sorted(issues, key=lambda item: (item["code"], item["path"], item["message"])),
    }


def validate_paths(
    pack_path: Path,
    family_map_path: Path,
    requirements_path: Path,
    shared_contract_path: Path,
) -> dict[str, Any]:
    pack = _load_yaml(pack_path)
    report = validate_family_pack(
        pack,
        _load_yaml(family_map_path),
        _load_yaml(requirements_path),
        _load_yaml(shared_contract_path),
    )
    expected_family = pack_path.stem
    if report["family"] != expected_family:
        report["issues"].append(
            _issue(
                "FAMILY_FILENAME_MISMATCH",
                f"pack declares {report['family']!r}, filename requires {expected_family!r}",
                "family",
            )
        )
        report["valid"] = False
    return report


def _canonical(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument(
        "--family-map",
        type=Path,
        default=REPO_ROOT / "shared/format-contracts/policy/format-family-map.yaml",
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=REPO_ROOT / "shared/format-contracts/policy/fact-category-requirements.yaml",
    )
    parser.add_argument(
        "--shared-contract",
        type=Path,
        default=REPO_ROOT / "shared/format-contracts/policy/shared-library-contract.yaml",
    )
    parser.add_argument("--verify-idempotency", action="store_true")
    args = parser.parse_args(argv)
    report = validate_paths(
        args.pack.resolve(),
        args.family_map.resolve(),
        args.requirements.resolve(),
        args.shared_contract.resolve(),
    )
    encoded = _canonical(report)
    if args.verify_idempotency:
        replay = _canonical(
            validate_paths(
                args.pack.resolve(),
                args.family_map.resolve(),
                args.requirements.resolve(),
                args.shared_contract.resolve(),
            )
        )
        if encoded != replay:
            report["valid"] = False
            report["issues"].append(
                _issue("NONDETERMINISTIC_VALIDATION", "equivalent validation replays differ")
            )
            encoded = _canonical(report)
    print(json.dumps(json.loads(encoded), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
