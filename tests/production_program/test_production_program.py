"""Regression controls for the production contract, proof, and controller."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.format_contract.product_contract import compile_product_contract
from tools.requirements_authority.production_graph import ProductionProofGraph
from tools.supervisor.production_program import Gap, ProductionProgram


def _contract(format_id: str = "ipynb") -> dict:
    return {
        "contract_metadata": {"format_id": format_id},
        "authoritative_sources": [
            {
                "source_id": f"SRC-{format_id.upper()}-001",
                "title": "Primary",
                "authority_class": "AUTHORITATIVE",
                "acquisition_status": "ACQUIRED",
                "sha256": "a" * 64,
            }
        ],
        "capabilities": [
            {
                "capability_id": f"{format_id.upper()}-READ-001",
                "level": "MUST",
                "provenance": [f"SAL-{format_id.upper()}-00001"],
                "required_behavior": ["Parse the complete required document structure."],
                "security_requirements": ["Reject payloads exceeding configured resource limits."],
                "required_tests": ["positive", "negative"],
                "release_gates": ["executed evidence required"],
            }
        ],
    }


def test_product_contract_is_deterministic_and_deferral_is_not_coverage() -> None:
    source = _contract()
    source["capabilities"][0]["deferral_reason"] = "later"
    first = compile_product_contract(source, run_legacy_validator=False)
    second = compile_product_contract(source, run_legacy_validator=False)
    assert first.digest == second.digest
    assert len(first.obligations) == 2
    assert {item["kind"] for item in first.obligations} == {"positive", "rejection"}


def test_unpinned_authority_and_foreign_fact_fail_closed() -> None:
    source = _contract()
    source["authoritative_sources"][0].pop("sha256")
    source["capabilities"][0]["provenance"].append("SAL-NRRD-99999")
    compiled = compile_product_contract(source, run_legacy_validator=False)
    codes = {issue.code for issue in compiled.issues}
    assert {"AUTHORITY_NOT_PINNED", "FOREIGN_FORMAT_FACT"} <= codes
    assert not compiled.ready


def test_three_equivalent_graph_runs_have_identical_digest() -> None:
    digests = []
    for created_at in ("one", "two", "three"):
        graph = ProductionProofGraph()
        node = graph.add_content_node(
            "AuthorityArtifact",
            "spec",
            {"format_id": "ipynb", "acquired": True},
            input_digests={"spec": "a" * 64},
        )
        node.created_at = created_at
        digests.append(graph.graph_digest())
    assert len(set(digests)) == 1


def test_changed_input_invalidates_every_dependent() -> None:
    graph = ProductionProofGraph()
    authority = graph.add_content_node(
        "AuthorityArtifact",
        "spec",
        {"format_id": "ipynb", "acquired": True},
        input_digests={"spec": "a" * 64},
    )
    obligation = graph.add_content_node(
        "NormativeObligation",
        "SAL-IPYNB-OBL-1",
        {"format_id": "ipynb", "level": "MUST"},
        input_digests={"spec": "a" * 64},
    )
    source = graph.add_content_node(
        "SourceSymbol",
        "reader.load",
        {"format_id": "ipynb"},
        input_digests={"source": "b" * 64},
    )
    graph.add_dependency(obligation, authority)
    graph.add_dependency(source, obligation)
    invalid = graph.invalidated_nodes({"spec": "c" * 64, "source": "b" * 64})
    assert {authority.node_id, obligation.node_id, source.node_id} <= invalid


def test_manual_promotion_label_cannot_override_live_proof() -> None:
    graph = ProductionProofGraph()
    graph.add_content_node(
        "Promotion",
        "manual",
        {"format_id": "ipynb", "state": "RELEASED"},
        input_digests={},
    )
    decision = graph.compute_promotion("ipynb", current_identity_digests={})
    assert decision.state == "UNASSESSED"


def test_gap_priority_is_deterministic(tmp_path: Path) -> None:
    program = ProductionProgram(tmp_path)
    low = Gap("G2", "ubl", "optional", "optional", "LOW", "optional")
    high = Gap("G1", "ipynb", "authority", "authority", "CRITICAL", "missing")
    program.reconcile_gap(low)
    program.reconcile_gap(high)
    assert program.next_gap() == high
    reloaded = ProductionProgram(tmp_path)
    assert reloaded.next_gap() == high


def test_controller_resumes_last_verified_transition(tmp_path: Path) -> None:
    program = ProductionProgram(tmp_path)
    program.transition("ipynb", "SNAPSHOT", evidence={"digest": "a"})
    reloaded = ProductionProgram(tmp_path)
    assert reloaded.formats["ipynb"].state == "SNAPSHOT"
    journal = [
        json.loads(line)
        for line in (tmp_path / "journal.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert journal[-1]["to"] == "SNAPSHOT"


def test_invalid_transition_fails_closed(tmp_path: Path) -> None:
    program = ProductionProgram(tmp_path)
    with pytest.raises(ValueError, match="unsafe transition"):
        program.transition("ipynb", "VERIFY", evidence={})
