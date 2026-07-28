from __future__ import annotations

from copy import deepcopy

from tools.format_contract.family_pack_validator import validate_family_pack


def valid_inputs() -> tuple[dict, dict, dict, dict]:
    pack = {
        "schema_version": "1.0",
        "family": "binary_tensor",
        "applicability": {
            "representative_formats": ["safetensors"],
            "semantic_scope": "Header-described raw tensor payloads.",
            "excluded_concepts": ["detached file", "compression codec", "spatial axis"],
        },
        "identity_defaults": {},
        "scope_defaults": {},
        "shared_groups": ["lifecycle_io"],
        "preservation_defaults": {
            "structural_roundtrip": ["Preserve tensor descriptors."],
            "lexical_roundtrip": ["Normalize JSON metadata."],
            "unknown_construct_policy": "Retain safe unknown descriptor fields.",
            "loss_reporting_policy": "Report unsafe unknown fields before writing.",
        },
        "depth_floors": {},
        "validation_layers": [],
        "security_defaults": {"limits": ["Bound header and payload bytes."]},
        "domains": [
            {
                "domain": "HEADER",
                "category": "parse",
                "level": "MUST",
                "title": "Header",
                "production_meaning": "Parse the complete binary prefix and JSON metadata.",
                "developer_use_case": "Inspect tensor descriptors without reading payload bytes.",
                "baseline_behavior": [
                    {"id": "POL-BT-HEADER-01", "text": "Parse the exact prefix and header."}
                ],
                "fact_keywords": ["header"],
                "required_tests": ["Header vectors and malformed negatives."],
                "release_gates": ["Every header rule has executed evidence."],
            }
        ],
    }
    family_map = {"map": {"safetensors": "binary_tensor"}}
    requirements = {
        "categories": {"structure_roots": {}, "data_model": {}},
        "families": {
            "binary_tensor": {
                "threshold": 0.8,
                "required_categories": ["structure_roots", "data_model"],
                "weights": {"structure_roots": 0.4, "data_model": 0.6},
            }
        },
    }
    shared = {"groups": {"lifecycle_io": {}}}
    return pack, family_map, requirements, shared


def test_valid_family_pack_is_deterministic() -> None:
    inputs = valid_inputs()
    first = validate_family_pack(*deepcopy(inputs))
    second = validate_family_pack(*deepcopy(inputs))
    assert first == second
    assert first["valid"]
    assert first["issues"] == []
    assert first["domain_count"] == 1
    assert first["policy_id_count"] == 1


def test_rejects_mapping_weight_and_excluded_concept_defects() -> None:
    pack, family_map, requirements, shared = valid_inputs()
    family_map["map"]["safetensors"] = "scientific_raster"
    requirements["families"]["binary_tensor"]["weights"] = {
        "structure_roots": 0.7,
        "data_model": 0.7,
    }
    pack["domains"][0]["baseline_behavior"][0]["text"] = (
        "Parse detached file references from the tensor header."
    )

    report = validate_family_pack(pack, family_map, requirements, shared)

    assert not report["valid"]
    assert {issue["code"] for issue in report["issues"]} == {
        "EXCLUDED_CONCEPT_LEAK",
        "READINESS_WEIGHTS_NOT_NORMALIZED",
        "REPRESENTATIVE_MAPPING_MISMATCH",
    }


def test_rejects_duplicate_policy_ids_and_unknown_shared_group() -> None:
    pack, family_map, requirements, shared = valid_inputs()
    duplicate = deepcopy(pack["domains"][0])
    duplicate["domain"] = "MODEL"
    pack["domains"].append(duplicate)
    pack["shared_groups"].append("not_registered")

    report = validate_family_pack(pack, family_map, requirements, shared)

    assert not report["valid"]
    assert {issue["code"] for issue in report["issues"]} == {
        "DUPLICATE_POLICY_ID",
        "UNKNOWN_SHARED_GROUP",
    }


def test_rejects_excluded_concept_from_selected_shared_group() -> None:
    pack, family_map, requirements, shared = valid_inputs()
    shared["groups"]["lifecycle_io"] = {
        "items": [
            {
                "id": "POL-SLC-LIFECYCLE-01",
                "text": "Resolve each detached file relative to the document.",
            }
        ]
    }

    report = validate_family_pack(pack, family_map, requirements, shared)

    assert not report["valid"]
    assert [issue["code"] for issue in report["issues"]] == [
        "EXCLUDED_CONCEPT_LEAK"
    ]
    assert report["issues"][0]["path"] == (
        "shared_groups.lifecycle_io.items[0].text"
    )


def test_rejects_missing_family_specific_preservation_and_limits() -> None:
    pack, family_map, requirements, shared = valid_inputs()
    pack.pop("preservation_defaults")
    pack["security_defaults"] = {}

    report = validate_family_pack(pack, family_map, requirements, shared)

    assert not report["valid"]
    assert {issue["code"] for issue in report["issues"]} == {
        "PRESERVATION_DEFAULTS_MISSING",
        "SECURITY_LIMITS_MISSING",
    }
