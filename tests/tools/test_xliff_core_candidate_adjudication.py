"""Fail-closed controls for independent XLIFF candidate adjudication."""

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
MODULE_PATH = (
    REPO_ROOT / "tools" / "spec" / "xliff_core_candidate_adjudication.py"
)
CENSUS_PATH = (
    REPO_ROOT / "reports" / "ff6" / "xliff-core-authority-candidate-census.yaml"
)
DENOMINATOR_PATH = (
    REPO_ROOT / "reports" / "ff6" / "xliff-core-obligation-denominator.yaml"
)
DECISIONS_PATH = (
    REPO_ROOT
    / "shared"
    / "sal-facts"
    / "evidence"
    / "xliff-core-candidate-decisions.yaml"
)
ADJUDICATION_PATH = (
    REPO_ROOT
    / "reports"
    / "sal-verification"
    / "xliff-core-candidate-adjudications.yaml"
)
SAL_STORE_PATH = REPO_ROOT / "shared" / "sal-facts" / "xliff.yaml"
SAL_MANIFEST_PATH = (
    REPO_ROOT / "shared" / "sal-facts" / "evidence" / "xliff.yaml"
)
SAL_RECEIPT_PATH = REPO_ROOT / "reports" / "sal-verification" / "xliff.json"
CANDIDATE_ID = "XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90"
TARGET_LANGUAGE_ID = "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001"
SUBFLOW_PAIR_CANDIDATE_ID = "XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1"
SUBFLOW_PAIR_RECIPROCAL_CANDIDATE_ID = (
    "XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF"
)
INLINE_PC_ID = "SAL-XLIFF-CORE-INLINE-PC-001"
INLINE_PAIRING_ID = "SAL-XLIFF-CORE-INLINE-PAIRING-001"
SKELETON_CANDIDATE_ID = "XLF-CAND-CORE-SCHEMATRON-04053F3F140BDD92"
SKELETON_RECIPROCAL_CANDIDATE_ID = (
    "XLF-CAND-CORE-SCHEMATRON-8D50B407E90E354E"
)
SKELETON_REFERENCE_ID = "SAL-XLIFF-CORE-REFERENCE-SKELETON-HREF-001"
SKELETON_HIERARCHY_ID = "SAL-XLIFF-CORE-HIERARCHY-SKELETON-001"
UNIT_CHILDREN_CANDIDATE_ID = "XLF-CAND-CORE-SCHEMATRON-100732DB0BBED389"
UNIT_CHILDREN_ID = "SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001"
UNIT_SEGMENT_ID = "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001"
SOURCE_LANGUAGE_CANDIDATE_ID = (
    "XLF-CAND-CORE-SCHEMATRON-B0961B8D3678CA73"
)
SOURCE_LANGUAGE_ID = "SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001"
SOURCE_REQUIRED_ID = "SAL-XLIFF-CORE-SOURCE-REQUIRED-001"
LANGUAGE_SOURCE_ID = "SAL-XLIFF-CORE-LANGUAGE-SOURCE-001"
TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID = (
    "XLF-CAND-CORE-SCHEMATRON-5D563A565DC6DCFE"
)
TARGET_LANGUAGE_COMPATIBILITY_ID = "SAL-XLIFF-CORE-TARGET-LANGUAGE-001"
LANGUAGE_TARGET_ID = "SAL-XLIFF-CORE-LANGUAGE-TARGET-001"
REJECTED_PROPOSAL_IDS = {
    "SAL-XLIFF-CORE-AGENT-VALIDATOR-001":
        "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER",
    "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001":
        "INCIDENTAL_XPATH_CONTEXT_TOKEN",
    "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001":
        "INCIDENTAL_XPATH_CONTEXT_TOKEN",
    "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001":
        "TRIGGER_DOES_NOT_ESTABLISH_CARDINALITY",
}
SUBFLOW_PAIR_REJECTED_PROPOSAL_IDS = {
    "SAL-XLIFF-CORE-AGENT-VALIDATOR-001":
        "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER",
    "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001":
        "INCIDENTAL_XPATH_CONTEXT_TOKEN",
    "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001":
        "INCIDENTAL_XPATH_CONTEXT_TOKEN",
    INLINE_PC_ID: "ELEMENT_SURFACE_NOT_DIRECT_PAIRING_OWNER",
}


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "xliff_core_candidate_adjudication_under_test",
        MODULE_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_decision_count() -> int:
    return len(_load_yaml(DECISIONS_PATH)["decisions"])


def _sal_inputs() -> tuple[dict[str, Any], dict[str, Any], str, str]:
    claim = (
        "The trgLang attribute is required when target elements occur under "
        "segment or ignorable."
    )
    claim_sha256 = hashlib.sha256(claim.encode("utf-8")).hexdigest()
    proof_sha256 = "9" * 64
    manifest_sha256 = "7" * 64
    receipt_sha256 = "8" * 64
    store = {
        "format_id": "xliff",
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim": claim,
                "verification_status": "verified",
                "provenance": {
                    "verification": {
                        "method": "declarative_authority_v1",
                        "manifest_sha256": manifest_sha256,
                        "receipt_sha256": receipt_sha256,
                        "fact_proof_sha256": proof_sha256,
                    }
                },
            }
        ],
    }
    receipt = {
        "format_id": "xliff",
        "result": "PASS",
        "manifest": {"sha256": manifest_sha256},
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim_sha256": claim_sha256,
                "proof_sha256": proof_sha256,
                "result": "PASS",
            }
        ],
    }
    return store, receipt, manifest_sha256, receipt_sha256


def _decision() -> dict[str, Any]:
    return {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0001",
        "candidate_id": CANDIDATE_ID,
        "accepted_obligation_ids": [TARGET_LANGUAGE_ID],
        "rejected_obligations": [
            {
                "obligation_id": obligation_id,
                "reason_code": reason_code,
                "reason": (
                    "Independent reading of the exact Schematron assertion "
                    "does not establish this proposed behavior."
                ),
            }
            for obligation_id, reason_code in sorted(
                REJECTED_PROPOSAL_IDS.items()
            )
        ],
        "sal_fact_ids": ["SAL-XLIFF-00009"],
        "authority_reason": (
            "The assertion test requires /xlf:xliff/@trgLang when its target "
            "context matches. Segment and ignorable identify the trigger "
            "context; they do not define hierarchy or source-target "
            "cardinality, and the assertion is not itself the generic "
            "validator capability."
        ),
    }


def _compile() -> tuple[ModuleType, dict[str, Any], dict[str, Any]]:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    store, receipt, manifest_sha256, receipt_sha256 = _sal_inputs()
    artifact = module.compile_adjudication_artifact(
        candidate_census=census,
        candidate_census_sha256=_sha256(CENSUS_PATH),
        denominator=denominator,
        denominator_sha256=_sha256(DENOMINATOR_PATH),
        sal_store=store,
        sal_store_sha256="6" * 64,
        sal_manifest_sha256=manifest_sha256,
        sal_receipt=receipt,
        sal_receipt_sha256=receipt_sha256,
        decisions=[_decision()],
    )
    return module, census, artifact


def test_trg_lang_adjudication_rejects_incidental_context_overmapping() -> None:
    module, census, artifact = _compile()
    proposal = next(
        row["disposition"]
        for row in census["candidates"]
        if row["candidate_id"] == CANDIDATE_ID
    )
    decision = artifact["decisions"][0]

    assert set(proposal["obligation_ids"]) == {
        TARGET_LANGUAGE_ID,
        *REJECTED_PROPOSAL_IDS,
    }
    assert decision["accepted_obligation_ids"] == [TARGET_LANGUAGE_ID]
    assert {
        row["obligation_id"]: row["reason_code"]
        for row in decision["rejected_obligations"]
    } == REJECTED_PROPOSAL_IDS
    projected = module.apply_adjudication_projection(census, artifact)
    assert projected["verified_disposition_count"] == 1
    assert projected["unverified_disposition_count"] == (
        projected["candidate_count"] - 1
    )


def _pairing_decision(candidate_id: str, sequence: int) -> dict[str, Any]:
    return {
        "decision_id": f"XLF-ADJ-CORE-SCHEMATRON-{sequence:04d}",
        "candidate_id": candidate_id,
        "accepted_obligation_ids": [INLINE_PAIRING_ID],
        "rejected_obligations": [
            {
                "obligation_id": obligation_id,
                "reason_code": reason_code,
                "reason": (
                    "Independent reading of this exact Schematron assertion "
                    "does not establish the proposed behavior as its direct "
                    "semantic owner."
                ),
            }
            for obligation_id, reason_code in sorted(
                SUBFLOW_PAIR_REJECTED_PROPOSAL_IDS.items()
            )
        ],
        "sal_fact_ids": ["SAL-XLIFF-00005"],
        "authority_reason": (
            "This exact XLIFF 2.1 Schematron assertion is one direction of "
            "the mutual subFlowsStart and subFlowsEnd presence constraint. "
            "Its direct denominator owner is the inline pairing obligation; "
            "the generated validator, hierarchy, and element-surface "
            "proposals are incidental or downstream."
        ),
    }


def test_adjudication_accepts_denominator_owner_omitted_by_generator() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    store = _load_yaml(SAL_STORE_PATH)
    receipt = _load_yaml(SAL_RECEIPT_PATH)

    artifact = module.compile_adjudication_artifact(
        candidate_census=census,
        candidate_census_sha256=_sha256(CENSUS_PATH),
        denominator=denominator,
        denominator_sha256=_sha256(DENOMINATOR_PATH),
        sal_store=store,
        sal_store_sha256=_sha256(SAL_STORE_PATH),
        sal_manifest_sha256=_sha256(SAL_MANIFEST_PATH),
        sal_receipt=receipt,
        sal_receipt_sha256=_sha256(SAL_RECEIPT_PATH),
        decisions=[
            _pairing_decision(
                SUBFLOW_PAIR_CANDIDATE_ID,
                2,
            )
        ],
    )

    decision = artifact["decisions"][0]
    assert decision["accepted_obligation_ids"] == [INLINE_PAIRING_ID]
    assert decision["unproposed_accepted_obligation_ids"] == [
        INLINE_PAIRING_ID
    ]
    assert {
        row["obligation_id"] for row in decision["rejected_obligations"]
    } == set(SUBFLOW_PAIR_REJECTED_PROPOSAL_IDS)


def test_subflow_pair_adjudication_requires_both_reciprocal_decisions() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    candidates = {
        row["candidate_id"]: row
        for row in census["candidates"]
    }
    selected_rule = json.loads(
        candidates[SUBFLOW_PAIR_CANDIDATE_ID]["occurrences"][0][
            "normalized_requirement"
        ]
    )
    reciprocal_rule = json.loads(
        candidates[SUBFLOW_PAIR_RECIPROCAL_CANDIDATE_ID]["occurrences"][0][
            "normalized_requirement"
        ]
    )
    assert selected_rule == {
        "context": (
            "xlf:pc[@subFlowsStart]"
            "[ancestor::xlf:segment|ancestor::xlf:ignorable]"
        ),
        "kind": "assert",
        "message": "'subFlowsStart' and 'subFlowsEnd' must be used in pair.",
        "test": "@subFlowsEnd",
    }
    assert reciprocal_rule == {
        "context": (
            "xlf:pc[@subFlowsEnd]"
            "[ancestor::xlf:segment|ancestor::xlf:ignorable]"
        ),
        "kind": "assert",
        "message": "'subFlowsStart' and 'subFlowsEnd' must be used in pair.",
        "test": "@subFlowsStart",
    }

    decision_source = _load_yaml(DECISIONS_PATH)
    decisions = [
        row
        for row in decision_source["decisions"]
        if row["candidate_id"]
        in {
            SUBFLOW_PAIR_CANDIDATE_ID,
            SUBFLOW_PAIR_RECIPROCAL_CANDIDATE_ID,
        }
    ]
    assert len(decisions) == 2, (
        "the mutual-presence obligation requires one independent decision "
        "for each exact reciprocal Schematron assertion"
    )
    for decision in decisions:
        assert decision["accepted_obligation_ids"] == [INLINE_PAIRING_ID]
        assert {
            row["obligation_id"]: row["reason_code"]
            for row in decision["rejected_obligations"]
        } == SUBFLOW_PAIR_REJECTED_PROPOSAL_IDS
        assert decision["sal_fact_ids"] == ["SAL-XLIFF-00005"]

    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert INLINE_PAIRING_ID in accepted
    assert INLINE_PC_ID not in accepted
    assert evidence["accepted_obligation_candidate_ids"][
        INLINE_PAIRING_ID
    ] == sorted(
        [
            SUBFLOW_PAIR_CANDIDATE_ID,
            SUBFLOW_PAIR_RECIPROCAL_CANDIDATE_ID,
        ]
    )
    decision_count = _canonical_decision_count()
    assert evidence["decision_count"] == decision_count
    assert evidence["verified_disposition_count"] == decision_count
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - decision_count
    )


def _skeleton_decision() -> dict[str, Any]:
    return {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0004",
        "candidate_id": SKELETON_CANDIDATE_ID,
        "accepted_obligation_ids": [SKELETON_REFERENCE_ID],
        "rejected_obligations": [
            {
                "obligation_id": "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
                "reason_code": (
                    "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
                ),
                "reason": (
                    "A conforming validator enforces this report, but the "
                    "report establishes only the skeleton href and content "
                    "constraint."
                ),
            }
        ],
        "unproposed_rejected_obligations": [
            {
                "obligation_id": SKELETON_HIERARCHY_ID,
                "reason_code": "ELEMENT_CONTEXT_NOT_HIERARCHY_RULE",
                "reason": (
                    "The skeleton context identifies the element whose "
                    "content and href are constrained; it establishes no "
                    "parent-child placement or cardinality rule."
                ),
            }
        ],
        "sal_fact_ids": ["SAL-XLIFF-00017"],
        "authority_reason": (
            "The exact report rejects a skeleton that has neither href nor "
            "child content. Its direct semantic owner is the skeleton "
            "href/content reference obligation; validator behavior is "
            "downstream and element context alone does not establish the "
            "broader hierarchy obligation."
        ),
    }


def _skeleton_reciprocal_decision() -> dict[str, Any]:
    decision = _skeleton_decision()
    decision["decision_id"] = "XLF-ADJ-CORE-SCHEMATRON-0005"
    decision["candidate_id"] = SKELETON_RECIPROCAL_CANDIDATE_ID
    decision["authority_reason"] = (
        "The exact report rejects a skeleton that combines href with child "
        "content. Its direct semantic owner is the existing skeleton "
        "href/content reference obligation; validator behavior is downstream "
        "and element context alone does not establish the broader hierarchy "
        "obligation."
    )
    return decision


def _unit_children_decision() -> dict[str, Any]:
    return {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0006",
        "candidate_id": UNIT_CHILDREN_CANDIDATE_ID,
        "accepted_obligation_ids": [UNIT_CHILDREN_ID],
        "rejected_obligations": [
            {
                "obligation_id": "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
                "reason_code": (
                    "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
                ),
                "reason": (
                    "A conforming validator enforces this report, but the "
                    "report directly establishes unit child cardinality."
                ),
            },
            {
                "obligation_id": UNIT_SEGMENT_ID,
                "reason_code": (
                    "CHILD_SURFACE_NOT_DIRECT_PARENT_CARDINALITY_OWNER"
                ),
                "reason": (
                    "The segment element is the required child surface; the "
                    "report constrains the parent unit and does not establish "
                    "the complete segment element model."
                ),
            },
        ],
        "sal_fact_ids": ["SAL-XLIFF-00002"],
        "authority_reason": (
            "The exact XLIFF 2.1 Schematron report selects unit elements and "
            "reports not(child::xlf:segment), directly requiring at least "
            "one segment child. Together with verified SAL-XLIFF-00002 for "
            "the stable unit child choice, the direct denominator owner is "
            "the unit-children cardinality obligation. The segment proposal "
            "is a child surface and generic validator behavior is downstream."
        ),
    }


def _source_language_decision() -> dict[str, Any]:
    return {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0007",
        "candidate_id": SOURCE_LANGUAGE_CANDIDATE_ID,
        "accepted_obligation_ids": [SOURCE_LANGUAGE_ID],
        "rejected_obligations": [
            {
                "obligation_id": "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
                "reason_code": (
                    "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
                ),
                "reason": (
                    "A conforming validator enforces this report, but the "
                    "report directly establishes source-language "
                    "compatibility with the document srcLang."
                ),
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",
                "reason_code": "INCIDENTAL_XPATH_CONTEXT_TOKEN",
                "reason": (
                    "The ignorable parent limits applicability and does not "
                    "establish an independent hierarchy rule."
                ),
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",
                "reason_code": "INCIDENTAL_XPATH_CONTEXT_TOKEN",
                "reason": (
                    "The segment parent limits applicability and does not "
                    "establish an independent hierarchy rule."
                ),
            },
            {
                "obligation_id": SOURCE_REQUIRED_ID,
                "reason_code": "TRIGGER_DOES_NOT_ESTABLISH_CARDINALITY",
                "reason": (
                    "The report applies when a source element with xml:lang "
                    "exists; it does not establish source presence or "
                    "cardinality."
                ),
            },
        ],
        "unproposed_rejected_obligations": [
            {
                "obligation_id": LANGUAGE_SOURCE_ID,
                "reason_code": (
                    "EXPLICIT_MATCH_DOES_NOT_ESTABLISH_INHERITANCE"
                ),
                "reason": (
                    "The report checks an explicit source xml:lang value. It "
                    "does not establish how an omitted value inherits from "
                    "the enclosing srcLang."
                ),
            }
        ],
        "sal_fact_ids": ["SAL-XLIFF-39A807E74F92A266"],
        "authority_reason": (
            "The exact XLIFF 2.1 Core Schematron report checks source "
            "xml:lang against root srcLang, and the XLIFF 2.1 Core prose "
            "requires the explicit or inherited source language to match "
            "srcLang. The parent names are applicability context, source "
            "presence is only a trigger, generic validation is downstream, "
            "and omitted-value inheritance is a separate obligation."
        ),
    }


def _target_language_compatibility_decision() -> dict[str, Any]:
    return {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0008",
        "candidate_id": TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID,
        "accepted_obligation_ids": [TARGET_LANGUAGE_COMPATIBILITY_ID],
        "rejected_obligations": [
            {
                "obligation_id": "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
                "reason_code": (
                    "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
                ),
                "reason": (
                    "A conforming validator enforces this report, but the "
                    "report directly establishes target-language "
                    "compatibility with the document trgLang."
                ),
            },
            {
                "obligation_id": TARGET_LANGUAGE_ID,
                "reason_code": (
                    "ROOT_PRESENCE_RULE_NOT_VALUE_COMPATIBILITY_RULE"
                ),
                "reason": (
                    "The document target-language obligation establishes "
                    "when root trgLang is present; it does not own value "
                    "compatibility for an explicit target xml:lang."
                ),
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",
                "reason_code": "INCIDENTAL_XPATH_CONTEXT_TOKEN",
                "reason": (
                    "The ignorable parent limits applicability and does not "
                    "establish an independent hierarchy rule."
                ),
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",
                "reason_code": "INCIDENTAL_XPATH_CONTEXT_TOKEN",
                "reason": (
                    "The segment parent limits applicability and does not "
                    "establish an independent hierarchy rule."
                ),
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001",
                "reason_code": "TRIGGER_DOES_NOT_ESTABLISH_CARDINALITY",
                "reason": (
                    "The report applies when a target with xml:lang exists; "
                    "it does not establish target presence or cardinality."
                ),
            },
        ],
        "unproposed_rejected_obligations": [
            {
                "obligation_id": LANGUAGE_TARGET_ID,
                "reason_code": (
                    "EXPLICIT_MATCH_DOES_NOT_ESTABLISH_INHERITANCE"
                ),
                "reason": (
                    "The report checks an explicit target xml:lang value. It "
                    "does not establish how an omitted value inherits from "
                    "the enclosing trgLang."
                ),
            }
        ],
        "sal_fact_ids": ["SAL-XLIFF-6F42212680161FF2"],
        "authority_reason": (
            "The XLIFF 2.0 prose requires exact target xml:lang equality "
            "with root trgLang. The normative XLIFF 2.1 F4T Schematron "
            "accepts equality or a more-specific target language through "
            "not(lang($trgLang)); XLIFF 2.1 explicitly gives normative "
            "separate machine-readable content precedence over conflicting "
            "display prose. This profile-specific value rule belongs to the "
            "existing target-language compatibility obligation. Root "
            "presence, hierarchy, cardinality, generic validation, and "
            "omitted-value inheritance are separate obligations."
        ),
    }


def test_target_language_compatibility_is_profile_specific_and_owned_once(
) -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    candidate = next(
        row
        for row in census["candidates"]
        if row["candidate_id"] == TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID
    )

    assert candidate["stable_profiles"] == ["xliff_2.1"]
    assert candidate["candidate_content_sha256"] == (
        "2f48f02786ace40f8e45306a2622fb031a0650a1004e6d4b316f3dd5ec44ee4d"
    )
    occurrence = candidate["occurrences"][0]
    assert occurrence["member_sha256"] == (
        "d4275f2d2574f892624bcd8f83bcc3001c75d623e4eb36896d15d147f16ed7a2"
    )
    assert occurrence["requirement_sha256"] == (
        "85279eddf8546a96b332e7a7b5388cb4639d886f2a6a0f7168048ec3e7e483ec"
    )
    assert occurrence["occurrence_sha256"] == (
        "639468d347a85cb3843f43bba0d0bdc9065beda22aee96021cb10f37374137fe"
    )
    assert json.loads(occurrence["normalized_requirement"]) == {
        "context": (
            "xlf:target[@xml:lang][parent::xlf:segment | "
            "parent::xlf:ignorable]"
        ),
        "kind": "report",
        "message": (
            "'xml:lang' attribute of the 'target' element and 'trgLang' "
            "attribute of the 'xliff' are not matching."
        ),
        "test": "not(lang($trgLang))",
    }
    assert set(candidate["disposition"]["obligation_ids"]) == {
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
        TARGET_LANGUAGE_ID,
        "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",
        "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",
        "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001",
    }

    decision_source = _load_yaml(DECISIONS_PATH)
    canonical_decisions = [
        row
        for row in decision_source["decisions"]
        if row["candidate_id"] == TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID
    ]
    assert canonical_decisions == [_target_language_compatibility_decision()]

    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert TARGET_LANGUAGE_COMPATIBILITY_ID in accepted
    assert TARGET_LANGUAGE_ID in accepted
    assert LANGUAGE_TARGET_ID not in accepted
    assert "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001" not in accepted
    assert evidence["accepted_obligation_candidate_ids"][
        TARGET_LANGUAGE_COMPATIBILITY_ID
    ] == [TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID]
    assert evidence["decision_count"] == 8
    assert evidence["verified_disposition_count"] == 8
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - 8
    )

    compiled_decision = next(
        row
        for row in _load_yaml(ADJUDICATION_PATH)["decisions"]
        if row["candidate_id"] == TARGET_LANGUAGE_COMPATIBILITY_CANDIDATE_ID
    )
    assert compiled_decision["unproposed_accepted_obligation_ids"] == [
        TARGET_LANGUAGE_COMPATIBILITY_ID
    ]


def test_source_language_adjudicates_only_document_compatibility_owner() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    candidate = next(
        row
        for row in census["candidates"]
        if row["candidate_id"] == SOURCE_LANGUAGE_CANDIDATE_ID
    )

    assert candidate["candidate_content_sha256"] == (
        "fc6bfe29b9efb1589d19e9f040ca0901bcdd8db4fe0a327760cd043257e41062"
    )
    occurrence = candidate["occurrences"][0]
    assert occurrence["requirement_sha256"] == (
        "4d6ff61b0af6ae593955517ebde43ac5bba05e48440a601f05fa91d54df6e464"
    )
    assert occurrence["occurrence_sha256"] == (
        "0102e918c34b6b8147324a33411e35b93d03740b2c1eb4a283e90c00bf3fb7ea"
    )
    assert json.loads(occurrence["normalized_requirement"]) == {
        "context": (
            "xlf:source[@xml:lang][parent::xlf:segment | "
            "parent::xlf:ignorable]"
        ),
        "kind": "report",
        "message": (
            "'xml:lang' attribute of the 'source' element and 'srcLang' "
            "attribute of the 'xliff' are not matching."
        ),
        "test": "not(lang($srcLang))",
    }
    assert set(candidate["disposition"]["obligation_ids"]) == {
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
        SOURCE_LANGUAGE_ID,
        "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",
        "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",
        SOURCE_REQUIRED_ID,
    }

    decision_source = _load_yaml(DECISIONS_PATH)
    canonical_decisions = [
        row
        for row in decision_source["decisions"]
        if row["candidate_id"] == SOURCE_LANGUAGE_CANDIDATE_ID
    ]
    assert canonical_decisions == [_source_language_decision()]

    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert SOURCE_LANGUAGE_ID in accepted
    assert SOURCE_REQUIRED_ID not in accepted
    assert LANGUAGE_SOURCE_ID not in accepted
    assert evidence["accepted_obligation_candidate_ids"][SOURCE_LANGUAGE_ID] == [
        SOURCE_LANGUAGE_CANDIDATE_ID
    ]
    decision_count = _canonical_decision_count()
    assert evidence["decision_count"] == decision_count
    assert evidence["verified_disposition_count"] == decision_count
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - decision_count
    )


def test_unit_segment_minimum_adjudicates_only_parent_cardinality_owner() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    candidate = next(
        row
        for row in census["candidates"]
        if row["candidate_id"] == UNIT_CHILDREN_CANDIDATE_ID
    )

    assert candidate["candidate_content_sha256"] == (
        "7564733d38472805796896373cbdbe7807510721c9dfbac29e53843862bcf1cf"
    )
    occurrence = candidate["occurrences"][0]
    assert occurrence["requirement_sha256"] == (
        "51c4d1ac9834b99f5a029894cc3c179117a7b9b8de50794bed8acd36132ede7d"
    )
    assert occurrence["occurrence_sha256"] == (
        "903d76dd0cb8472539255ce5075a884460844bc4975a030906ffb793377d3648"
    )
    assert json.loads(occurrence["normalized_requirement"]) == {
        "context": "xlf:unit",
        "kind": "report",
        "message": "Incomplete 'unit'; it must have at least one 'segment' child.",
        "test": "not(child::xlf:segment)",
    }
    assert set(candidate["disposition"]["obligation_ids"]) == {
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
        UNIT_SEGMENT_ID,
        UNIT_CHILDREN_ID,
    }

    decision_source = _load_yaml(DECISIONS_PATH)
    canonical_decision = next(
        row
        for row in decision_source["decisions"]
        if row["candidate_id"] == UNIT_CHILDREN_CANDIDATE_ID
    )
    assert canonical_decision == _unit_children_decision()

    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert UNIT_CHILDREN_ID in accepted
    assert UNIT_SEGMENT_ID not in accepted
    assert evidence["accepted_obligation_candidate_ids"][UNIT_CHILDREN_ID] == [
        UNIT_CHILDREN_CANDIDATE_ID
    ]
    decision_count = _canonical_decision_count()
    assert evidence["decision_count"] == decision_count
    assert evidence["verified_disposition_count"] == decision_count
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - decision_count
    )


def test_skeleton_href_adjudication_records_incidental_unproposed_owner() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    store = _load_yaml(SAL_STORE_PATH)
    receipt = _load_yaml(SAL_RECEIPT_PATH)
    candidate = next(
        row
        for row in census["candidates"]
        if row["candidate_id"] == SKELETON_CANDIDATE_ID
    )
    assert candidate["stable_profiles"] == ["xliff_2.1"]
    assert json.loads(candidate["occurrences"][0]["normalized_requirement"]) == {
        "context": "xlf:skeleton",
        "kind": "report",
        "message": (
            "'skeleton' element must not be empty when the 'href' attribute "
            "is missing."
        ),
        "test": "not(@href) and not(child::node())",
    }
    assert set(candidate["disposition"]["obligation_ids"]) == {
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
        SKELETON_REFERENCE_ID,
    }

    artifact = module.compile_adjudication_artifact(
        candidate_census=census,
        candidate_census_sha256=_sha256(CENSUS_PATH),
        denominator=denominator,
        denominator_sha256=_sha256(DENOMINATOR_PATH),
        sal_store=store,
        sal_store_sha256=_sha256(SAL_STORE_PATH),
        sal_manifest_sha256=_sha256(SAL_MANIFEST_PATH),
        sal_receipt=receipt,
        sal_receipt_sha256=_sha256(SAL_RECEIPT_PATH),
        decisions=[_skeleton_decision()],
    )

    decision = artifact["decisions"][0]
    assert decision["accepted_obligation_ids"] == [SKELETON_REFERENCE_ID]
    assert decision["unproposed_accepted_obligation_ids"] == []
    assert {
        row["obligation_id"]: row["reason_code"]
        for row in decision["rejected_obligations"]
    } == {
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001":
            "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
    }
    assert decision["unproposed_rejected_obligations"] == [
        {
            "obligation_id": SKELETON_HIERARCHY_ID,
            "reason_code": "ELEMENT_CONTEXT_NOT_HIERARCHY_RULE",
            "reason": (
                "The skeleton context identifies the element whose content "
                "and href are constrained; it establishes no parent-child "
                "placement or cardinality rule."
            ),
        }
    ]
    canonical_source = _load_yaml(DECISIONS_PATH)
    canonical_decision = next(
        row
        for row in canonical_source["decisions"]
        if row["candidate_id"] == SKELETON_CANDIDATE_ID
    )
    assert canonical_decision == _skeleton_decision()
    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert SKELETON_REFERENCE_ID in accepted
    assert SKELETON_HIERARCHY_ID not in accepted
    assert evidence["accepted_obligation_candidate_ids"][
        SKELETON_REFERENCE_ID
    ] == sorted(
        [SKELETON_CANDIDATE_ID, SKELETON_RECIPROCAL_CANDIDATE_ID]
    )
    decision_count = _canonical_decision_count()
    assert evidence["decision_count"] == decision_count
    assert evidence["verified_disposition_count"] == decision_count
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - decision_count
    )


@pytest.mark.parametrize(
    "mutation",
    ["unknown", "proposed", "accepted", "duplicate"],
)
def test_skeleton_unproposed_rejections_fail_closed(mutation: str) -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    store = _load_yaml(SAL_STORE_PATH)
    receipt = _load_yaml(SAL_RECEIPT_PATH)
    decision = _skeleton_decision()
    rejected = decision["unproposed_rejected_obligations"]
    if mutation == "unknown":
        rejected[0]["obligation_id"] = (
            "SAL-XLIFF-CORE-NOT-IN-DENOMINATOR-001"
        )
    elif mutation == "proposed":
        rejected[0]["obligation_id"] = (
            "SAL-XLIFF-CORE-AGENT-VALIDATOR-001"
        )
    elif mutation == "accepted":
        rejected[0]["obligation_id"] = SKELETON_REFERENCE_ID
    else:
        rejected.append(deepcopy(rejected[0]))

    with pytest.raises(module.AdjudicationError):
        module.compile_adjudication_artifact(
            candidate_census=census,
            candidate_census_sha256=_sha256(CENSUS_PATH),
            denominator=denominator,
            denominator_sha256=_sha256(DENOMINATOR_PATH),
            sal_store=store,
            sal_store_sha256=_sha256(SAL_STORE_PATH),
            sal_manifest_sha256=_sha256(SAL_MANIFEST_PATH),
            sal_receipt=receipt,
            sal_receipt_sha256=_sha256(SAL_RECEIPT_PATH),
            decisions=[decision],
        )


def test_skeleton_href_obligation_requires_both_reciprocal_reports() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    candidates = {
        row["candidate_id"]: row
        for row in census["candidates"]
    }
    selected_rule = json.loads(
        candidates[SKELETON_CANDIDATE_ID]["occurrences"][0][
            "normalized_requirement"
        ]
    )
    reciprocal_rule = json.loads(
        candidates[SKELETON_RECIPROCAL_CANDIDATE_ID]["occurrences"][0][
            "normalized_requirement"
        ]
    )
    assert selected_rule == {
        "context": "xlf:skeleton",
        "kind": "report",
        "message": (
            "'skeleton' element must not be empty when the 'href' attribute "
            "is missing."
        ),
        "test": "not(@href) and not(child::node())",
    }
    assert reciprocal_rule == {
        "context": "xlf:skeleton",
        "kind": "report",
        "message": (
            "'skeleton' element must be empty when containing 'href' "
            "attribute."
        ),
        "test": "@href and  child::node()",
    }

    decision_source = _load_yaml(DECISIONS_PATH)
    decisions = [
        row
        for row in decision_source["decisions"]
        if row["candidate_id"]
        in {
            SKELETON_CANDIDATE_ID,
            SKELETON_RECIPROCAL_CANDIDATE_ID,
        }
    ]
    assert len(decisions) == 2, (
        "the skeleton href/content biconditional requires one independent "
        "decision for each exact reciprocal Schematron report"
    )
    expected_decisions = {
        SKELETON_CANDIDATE_ID: _skeleton_decision(),
        SKELETON_RECIPROCAL_CANDIDATE_ID:
            _skeleton_reciprocal_decision(),
    }
    for decision in decisions:
        assert decision == expected_decisions[decision["candidate_id"]]

    accepted, evidence = module.validated_obligation_ids_from_paths(
        adjudications_path=ADJUDICATION_PATH,
        candidate_census_path=CENSUS_PATH,
        denominator_path=DENOMINATOR_PATH,
        sal_store_path=SAL_STORE_PATH,
        sal_manifest_path=SAL_MANIFEST_PATH,
        sal_receipt_path=SAL_RECEIPT_PATH,
    )
    assert accepted >= {SKELETON_REFERENCE_ID}
    assert SKELETON_HIERARCHY_ID not in accepted
    assert evidence["accepted_obligation_candidate_ids"][
        SKELETON_REFERENCE_ID
    ] == sorted(
        [SKELETON_CANDIDATE_ID, SKELETON_RECIPROCAL_CANDIDATE_ID]
    )
    decision_count = _canonical_decision_count()
    assert evidence["decision_count"] == decision_count
    assert evidence["verified_disposition_count"] == decision_count
    assert evidence["unverified_disposition_count"] == (
        census["candidate_count"] - decision_count
    )


def test_generated_proposal_never_counts_as_verified_without_adjudication() -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    empty = {
        "schema": module.SCHEMA,
        "artifact_id": module.ARTIFACT_ID,
        "format_id": "xliff",
        "candidate_census_sha256": _sha256(CENSUS_PATH),
        "decisions": [],
        "decision_count": 0,
    }

    projected = module.apply_adjudication_projection(census, empty)

    assert projected["verified_disposition_count"] == 0
    assert projected["unverified_disposition_count"] == census["candidate_count"]
    assert projected["disposition_verification_complete"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        "candidate_content",
        "occurrence",
        "authority_member",
        "denominator",
        "decision",
    ],
)
def test_adjudication_invalidates_when_any_proof_input_changes(
    mutation: str,
) -> None:
    module, census, artifact = _compile()
    denominator = _load_yaml(DENOMINATOR_PATH)
    store, receipt, manifest_sha256, receipt_sha256 = _sal_inputs()
    changed_census = deepcopy(census)
    changed_artifact = deepcopy(artifact)
    changed_denominator_sha256 = _sha256(DENOMINATOR_PATH)
    candidate = next(
        row
        for row in changed_census["candidates"]
        if row["candidate_id"] == CANDIDATE_ID
    )
    if mutation == "candidate_content":
        candidate["candidate_content_sha256"] = "0" * 64
    elif mutation == "occurrence":
        candidate["occurrences"][0]["occurrence_sha256"] = "0" * 64
    elif mutation == "authority_member":
        candidate["occurrences"][0]["member_sha256"] = "0" * 64
    elif mutation == "denominator":
        changed_denominator_sha256 = "0" * 64
    else:
        changed_artifact["decisions"][0]["authority_reason"] += " changed"

    with pytest.raises(module.AdjudicationError):
        module.validate_adjudication_artifact(
            changed_artifact,
            candidate_census=changed_census,
            candidate_census_sha256=_sha256(CENSUS_PATH),
            denominator=denominator,
            denominator_sha256=changed_denominator_sha256,
            sal_store=store,
            sal_store_sha256="6" * 64,
            sal_manifest_sha256=manifest_sha256,
            sal_receipt=receipt,
            sal_receipt_sha256=receipt_sha256,
        )


@pytest.mark.parametrize(
    "mutation",
    ["unknown", "duplicate", "foreign", "missing", "unreasoned"],
)
def test_malformed_or_unreasoned_decisions_fail_closed(mutation: str) -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    store, receipt, manifest_sha256, receipt_sha256 = _sal_inputs()
    decision = _decision()
    if mutation == "unknown":
        decision["accepted_obligation_ids"] = [
            "SAL-XLIFF-CORE-NOT-IN-DENOMINATOR-001"
        ]
    elif mutation == "duplicate":
        decision["accepted_obligation_ids"] *= 2
    elif mutation == "foreign":
        decision["accepted_obligation_ids"] = ["SAL-NRRD-HEADER-001"]
    elif mutation == "missing":
        decision.pop("rejected_obligations")
    else:
        decision["authority_reason"] = ""

    with pytest.raises(module.AdjudicationError):
        module.compile_adjudication_artifact(
            candidate_census=census,
            candidate_census_sha256=_sha256(CENSUS_PATH),
            denominator=denominator,
            denominator_sha256=_sha256(DENOMINATOR_PATH),
            sal_store=store,
            sal_store_sha256="6" * 64,
            sal_manifest_sha256=manifest_sha256,
            sal_receipt=receipt,
            sal_receipt_sha256=receipt_sha256,
            decisions=[decision],
        )


def test_cli_writes_and_checks_content_addressed_adjudications(
    tmp_path: Path,
) -> None:
    module = _load_module()
    census = _load_yaml(CENSUS_PATH)
    denominator = _load_yaml(DENOMINATOR_PATH)
    manifest_path = tmp_path / "manifest.yaml"
    receipt_path = tmp_path / "receipt.json"
    store_path = tmp_path / "store.yaml"
    decisions_path = tmp_path / "decisions.yaml"
    output_path = tmp_path / "adjudications.yaml"

    manifest_path.write_text(
        "schema: test-manifest\nformat_id: xliff\n",
        encoding="utf-8",
    )
    manifest_sha256 = _sha256(manifest_path)
    claim = (
        "The trgLang attribute is required when target elements occur under "
        "segment or ignorable."
    )
    receipt = {
        "format_id": "xliff",
        "result": "PASS",
        "manifest": {"sha256": manifest_sha256},
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim_sha256": hashlib.sha256(
                    claim.encode("utf-8")
                ).hexdigest(),
                "proof_sha256": "9" * 64,
                "result": "PASS",
            }
        ],
    }
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    receipt_sha256 = _sha256(receipt_path)
    store = {
        "format_id": "xliff",
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim": claim,
                "verification_status": "verified",
                "provenance": {
                    "verification": {
                        "method": "declarative_authority_v1",
                        "manifest_sha256": manifest_sha256,
                        "receipt_sha256": receipt_sha256,
                        "fact_proof_sha256": "9" * 64,
                    }
                },
            }
        ],
    }
    store_path.write_text(
        yaml.safe_dump(store, sort_keys=False),
        encoding="utf-8",
    )
    decisions_path.write_text(
        yaml.safe_dump(
            {
                "schema": (
                    "ff6/xliff-core-candidate-adjudication-decisions@1"
                ),
                "format_id": "xliff",
                "decisions": [_decision()],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    common = [
        "--candidate-census",
        str(CENSUS_PATH),
        "--denominator",
        str(DENOMINATOR_PATH),
        "--sal-store",
        str(store_path),
        "--sal-manifest",
        str(manifest_path),
        "--sal-receipt",
        str(receipt_path),
        "--decisions",
        str(decisions_path),
        "--output",
        str(output_path),
    ]

    assert module.main(common) == 0
    first_bytes = output_path.read_bytes()
    artifact = yaml.safe_load(first_bytes)
    assert artifact["decision_count"] == 1
    assert artifact["candidate_count"] == census["candidate_count"]
    assert artifact["verified_disposition_count"] == 1
    assert artifact["unverified_disposition_count"] == (
        census["candidate_count"] - 1
    )
    assert artifact["disposition_verification_complete"] is False
    assert artifact["candidate_census_sha256"] == _sha256(CENSUS_PATH)
    assert artifact["denominator_sha256"] == _sha256(DENOMINATOR_PATH)
    assert artifact["sal_store_sha256"] == _sha256(store_path)
    assert artifact["sal_manifest_sha256"] == manifest_sha256
    assert artifact["sal_receipt_sha256"] == receipt_sha256
    assert module.main([*common, "--check"]) == 0
    assert output_path.read_bytes() == first_bytes
