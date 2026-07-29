"""Negative controls for XLIFF Core authority-candidate content binding."""

# generated_by: codex

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "spec" / "extract_sal_facts.py"
BINDING_MODULE_PATH = (
    REPO_ROOT / "tools" / "spec" / "xliff_core_candidate_binding.py"
)
CENSUS_PATH = (
    REPO_ROOT / "reports" / "ff6" / "xliff-core-authority-candidate-census.yaml"
)
DENOMINATOR_PATH = (
    REPO_ROOT / "reports" / "ff6" / "xliff-core-obligation-denominator.yaml"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "extract_sal_facts_candidate_binding_under_test",
        MODULE_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_binding_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "xliff_core_candidate_binding_under_test",
        BINDING_MODULE_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _single_profile_candidate(census: dict[str, Any]) -> dict[str, Any]:
    return next(
        candidate
        for candidate in census["candidates"]
        if len(candidate["occurrences"]) == 1
    )


@pytest.mark.parametrize(
    ("source_kind", "location", "requirement", "expected_class"),
    [
        (
            "NORMATIVE_PROSE",
            "prose/core/example/para[1]",
            "Agents must preserve the value.",
            "PROSE_MODAL_PARAGRAPH",
        ),
        (
            "NORMATIVE_PROSE",
            "prose/core/example/listitem[1]",
            "Writers should preserve the value.",
            "PROSE_MODAL_LIST_ITEM",
        ),
        (
            "NON_MODAL_PROSE",
            "prose-nonmodal/core/example/para[1]",
            "The value identifies a resource.",
            "PROSE_NON_MODAL_PARAGRAPH",
        ),
        (
            "NON_MODAL_PROSE",
            "prose-nonmodal/core/example/listitem[1]",
            "A resource identifier.",
            "PROSE_NON_MODAL_LIST_ITEM",
        ),
        (
            "CORE_XSD",
            "xsd/element:xliff",
            '{"attributes":{"name":"xliff"},"kind":"element"}',
            "XSD_ELEMENT_DECLARATION",
        ),
        (
            "CORE_XSD",
            "xsd/element:xliff/complexType:1/sequence:1/element:file",
            (
                '{"attributes":{"maxOccurs":"unbounded","minOccurs":"1",'
                '"ref":"xlf:file"},"kind":"element"}'
            ),
            "XSD_ELEMENT_PARTICLE_CARDINALITY",
        ),
        (
            "CORE_XSD",
            "xsd/element:xliff/complexType:1/attribute:version",
            (
                '{"attributes":{"name":"version","use":"required"},'
                '"kind":"attribute"}'
            ),
            "XSD_ATTRIBUTE_DECLARATION_CARDINALITY",
        ),
        (
            "CORE_XSD",
            "xsd/element:xliff/complexType:1/sequence:1",
            '{"attributes":{},"kind":"sequence"}',
            "XSD_ORDER_SEQUENCE",
        ),
        (
            "CORE_XSD",
            "xsd/element:xliff/complexType:1/any:1",
            '{"attributes":{"processContents":"lax"},"kind":"any"}',
            "XSD_WILDCARD_ELEMENT",
        ),
        (
            "CORE_XSD",
            "xsd/simpleType:state/restriction:1/enumeration:final",
            '{"attributes":{"value":"final"},"kind":"enumeration"}',
            "XSD_FACET_ENUMERATION",
        ),
        (
            "CORE_XSD",
            "xsd/simpleType:state/restriction:1",
            '{"attributes":{"base":"xs:string"},"kind":"restriction"}',
            "XSD_TYPE_RESTRICTION",
        ),
        (
            "CORE_XSD",
            "xsd/key:unitId/selector:1",
            '{"attributes":{"xpath":"xlf:unit"},"kind":"selector"}',
            "XSD_IDENTITY_SELECTOR",
        ),
        (
            "CORE_SCHEMATRON",
            "schematron/rule[1]/assert[1]",
            '{"kind":"assert","test":"@id"}',
            "SCHEMATRON_ASSERT",
        ),
        (
            "CORE_SCHEMATRON",
            "schematron/rule[1]/report[1]",
            '{"kind":"report","test":"@id"}',
            "SCHEMATRON_REPORT",
        ),
    ],
)
def test_candidate_binding_module_assigns_explicit_semantic_classes(
    source_kind: str,
    location: str,
    requirement: str,
    expected_class: str,
) -> None:
    binding = _load_binding_module()

    assert (
        binding.classify_candidate(
            source_kind=source_kind,
            semantic_location=location,
            normalized_requirement=requirement,
        )
        == expected_class
    )
    assert expected_class in binding.CORE_CANDIDATE_CLASSES


def test_candidate_binding_module_hashes_every_occurrence_field() -> None:
    binding = _load_binding_module()
    occurrence = {
        "profile": "xliff_2.1",
        "source_id": "SRC-XLF-002",
        "source_sha256": "1" * 64,
        "member": "schemas/xliff_core_2.1.sch",
        "member_sha256": "2" * 64,
        "location": "schematron/rule[1]/assert[1]",
        "candidate_class": "SCHEMATRON_ASSERT",
        "normalized_requirement": '{"kind":"assert","test":"@id"}',
    }

    bound = binding.bind_occurrence(occurrence)

    assert bound["requirement_sha256"] == hashlib.sha256(
        occurrence["normalized_requirement"].encode("utf-8")
    ).hexdigest()
    assert len(bound["occurrence_sha256"]) == 64
    binding.validate_bound_occurrence(bound)
    for field in occurrence:
        tampered = dict(bound)
        tampered[field] = f"{tampered[field]}-forged"
        with pytest.raises(binding.CandidateBindingError):
            binding.validate_bound_occurrence(tampered)

    candidate = {
        "candidate_id": "XLF-CAND-CORE-SCHEMATRON-EXAMPLE",
        "source_kind": "CORE_SCHEMATRON",
        "candidate_class": "SCHEMATRON_ASSERT",
        "semantic_location": "schematron/rule[1]/assert[1]",
        "profile_relation": "ADDED_IN_XLIFF_2_1",
        "stable_profiles": ["xliff_2.1"],
        "occurrences": [bound],
    }
    first_digest = binding.candidate_content_sha256(candidate)
    changed = deepcopy(candidate)
    changed_base = {
        field: changed["occurrences"][0][field] for field in occurrence
    }
    changed_base["normalized_requirement"] = (
        '{"kind":"assert","message":"changed","test":"@id"}'
    )
    changed["occurrences"][0] = binding.bind_occurrence(changed_base)
    changed_digest = binding.candidate_content_sha256(changed)
    assert first_digest != changed_digest
    assert first_digest == hashlib.sha256(
        json.dumps(
            candidate,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    wrong_source_kind = deepcopy(candidate)
    wrong_source_kind["source_kind"] = "CORE_XSD"
    with pytest.raises(
        binding.CandidateBindingError,
        match="class|source kind",
    ):
        binding.candidate_content_sha256(wrong_source_kind)


def test_candidate_binding_module_checks_rehashed_authority_forgery() -> None:
    binding = _load_binding_module()
    base = {
        "profile": "xliff_2.1",
        "source_id": "SRC-XLF-002",
        "source_sha256": "1" * 64,
        "member": "schemas/xliff_core_2.1.sch",
        "member_sha256": "2" * 64,
        "location": "schematron/rule[1]/assert[1]",
        "candidate_class": "SCHEMATRON_ASSERT",
        "normalized_requirement": '{"kind":"assert","test":"@id"}',
    }
    authority_inputs = [
        {
            "authority_class": "XLIFF_STANDARD_PACKAGE",
            "profile": "xliff_2.1",
            "source_id": "SRC-XLF-002",
            "source_sha256": "1" * 64,
        }
    ]
    authority_member_inputs = [
        {
            "profile": "xliff_2.1",
            "source_id": "SRC-XLF-002",
            "source_sha256": "1" * 64,
            "member": "schemas/xliff_core_2.1.sch",
            "member_sha256": "2" * 64,
        }
    ]
    bound = binding.bind_occurrence(base)
    binding.validate_occurrence_authority(
        bound,
        authority_inputs=authority_inputs,
        authority_member_inputs=authority_member_inputs,
    )

    for field in ("source_sha256", "member_sha256"):
        forged_base = dict(base)
        forged_base[field] = "f" * 64
        forged = binding.bind_occurrence(forged_base)
        with pytest.raises(
            binding.CandidateBindingError,
            match="authority",
        ):
            binding.validate_occurrence_authority(
                forged,
                authority_inputs=authority_inputs,
                authority_member_inputs=authority_member_inputs,
            )


def test_candidate_binding_module_covers_every_census_xsd_kind() -> None:
    binding = _load_binding_module()

    assert binding.XSD_CANDIDATE_KINDS == {
        "all",
        "any",
        "anyAttribute",
        "attribute",
        "choice",
        "complexType",
        "element",
        "enumeration",
        "extension",
        "field",
        "fractionDigits",
        "group",
        "import",
        "key",
        "keyref",
        "length",
        "list",
        "maxExclusive",
        "maxInclusive",
        "maxLength",
        "minExclusive",
        "minInclusive",
        "minLength",
        "pattern",
        "restriction",
        "selector",
        "sequence",
        "simpleType",
        "totalDigits",
        "union",
        "unique",
        "whiteSpace",
    }


def test_core_census_emits_content_bound_candidate_identity() -> None:
    extractor = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)

    assert census["schema"] == "ff6/xliff-core-authority-census@2"
    assert census["authority_member_inputs"]
    for candidate in census["candidates"]:
        assert candidate["candidate_class"] in extractor._CORE_CANDIDATE_CLASSES
        assert len(candidate["candidate_content_sha256"]) == 64
        for occurrence in candidate["occurrences"]:
            assert occurrence["candidate_class"] == candidate["candidate_class"]
            assert len(occurrence["occurrence_sha256"]) == 64

    extractor.validate_xliff_core_authority_census(
        census,
        expected_obligation_inventory=denominator,
    )


def test_core_census_classifies_non_modal_prose_without_coarse_fallbacks() -> None:
    census = _load_yaml(CENSUS_PATH)

    assert census["candidate_scope_complete"] is True
    assert census["non_modal_prose_census_complete"] is True
    assert census["non_modal_prose_disposition_complete"] is True
    assert census["non_modal_prose_classification_verified"] is False
    assert "non_modal_prose_classification_complete" not in census
    assert census["disposition_verification_complete"] is False
    assert census["unverified_disposition_count"] == census["candidate_count"]
    assert census["candidate_count"] > 542
    assert census["candidate_count_by_source_kind"]["NON_MODAL_PROSE"] > 0
    non_modal = [
        candidate
        for candidate in census["candidates"]
        if candidate["source_kind"] == "NON_MODAL_PROSE"
    ]
    assert non_modal
    assert {
        candidate["candidate_class"] for candidate in non_modal
    } <= {
        "PROSE_NON_MODAL_PARAGRAPH",
        "PROSE_NON_MODAL_LIST_ITEM",
    }
    assert all(
        candidate["disposition"].get("mapping_precision")
        != "COARSE_STRUCTURAL_FALLBACK"
        for candidate in census["candidates"]
    )
    assert all(
        not candidate["disposition"]["mapping_precision"].startswith("EXACT_")
        for candidate in census["candidates"]
    )
    assert all(
        "FALLBACK" not in rule_id
        for candidate in census["candidates"]
        for rule_id in candidate["disposition"]["mapping_rule_ids"]
    )
    assert census["disposition_precision_counts"].get(
        "COARSE_STRUCTURAL_FALLBACK",
        0,
    ) == 0
    assert census["disposition_precision_counts"][
        "STRUCTURAL_CLASS_MAPPING_UNVERIFIED"
    ] == 78


def test_core_census_recomputes_dispositions_instead_of_trusting_labels() -> None:
    extractor = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    tampered = deepcopy(census)
    mapped = next(
        candidate
        for candidate in tampered["candidates"]
        if candidate["disposition"]["kind"] == "MAP_EXPECTED_OBLIGATION"
    )
    mapped["disposition"]["mapping_rule_ids"] = ["SEMANTIC_TOKEN:FORGED"]

    with pytest.raises(
        extractor.ExtractionError,
        match="deterministic disposition",
    ):
        extractor.validate_xliff_core_authority_census(
            tampered,
            expected_obligation_inventory=denominator,
        )


def test_core_census_rejects_extraneous_authority_member_identity() -> None:
    extractor = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    tampered = deepcopy(census)
    foreign = deepcopy(tampered["authority_member_inputs"][0])
    foreign["member"] = "schemas/foreign-preview.xsd"
    foreign["member_sha256"] = "f" * 64
    tampered["authority_member_inputs"].append(foreign)

    with pytest.raises(
        extractor.ExtractionError,
        match="authority member|projection|binding",
    ):
        extractor.validate_xliff_core_authority_census(
            tampered,
            expected_obligation_inventory=denominator,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "normalized_requirement",
        "requirement_sha256",
        "member_sha256",
        "source_sha256",
        "location",
        "occurrence_sha256",
        "candidate_content_sha256",
        "candidate_class",
    ],
)
def test_core_census_rejects_forged_candidate_content(mutation: str) -> None:
    extractor = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    tampered = deepcopy(census)
    candidate = _single_profile_candidate(tampered)
    occurrence = candidate["occurrences"][0]

    if mutation == "normalized_requirement":
        occurrence["normalized_requirement"] += " forged"
    elif mutation == "requirement_sha256":
        occurrence["requirement_sha256"] = "0" * 64
    elif mutation == "member_sha256":
        occurrence["member_sha256"] = "0" * 64
    elif mutation == "source_sha256":
        occurrence["source_sha256"] = "0" * 64
    elif mutation == "location":
        occurrence["location"] += "/forged"
    elif mutation == "occurrence_sha256":
        occurrence["occurrence_sha256"] = "0" * 64
    elif mutation == "candidate_content_sha256":
        candidate["candidate_content_sha256"] = "0" * 64
    else:
        candidate["candidate_class"] = "FORGED_CANDIDATE_CLASS"

    with pytest.raises(extractor.ExtractionError, match="binding|digest|class"):
        extractor.validate_xliff_core_authority_census(
            tampered,
            expected_obligation_inventory=denominator,
        )
