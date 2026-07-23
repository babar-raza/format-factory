"""Regression controls for the production contract, proof, and controller."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.format_contract.product_contract import compile_product_contract
from tools.requirements_authority.production_graph import ProductionProofGraph
from tools.supervisor.production_program import (
    SAL_STATUS_SCHEMA_GAP_ID,
    TARGETS_BY_PRODUCT,
    Gap,
    ProductTarget,
    ProductionProgram,
    validate_target_registry,
)


def _contract(format_id: str = "ipynb") -> dict:
    return {
        "contract_metadata": {
            "format_id": format_id,
            "contract_id": f"FC-{format_id.upper()}-V1",
            "family": "test",
            "target_spec_version": "1.0",
            "input_digests": {"sal_facts_sha256": "b" * 64},
        },
        "authoritative_sources": [
            {
                "source_id": f"SRC-{format_id.upper()}-001",
                "title": "Primary",
                "authority_class": "AUTHORITATIVE",
                "acquisition_status": "ACQUIRED",
                "content_hash": "a" * 64,
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
    assert all(
        item["fact_ids"] == ("SAL-IPYNB-00001",)
        for item in first.obligations
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("target_spec_version", "2.0"),
        ("family", "changed-family"),
        ("contract_id", "FC-IPYNB-V2"),
    ],
)
def test_contract_identity_change_invalidates_digest(field: str, value: str) -> None:
    baseline = _contract()
    changed = _contract()
    changed["contract_metadata"][field] = value
    assert compile_product_contract(
        baseline, run_legacy_validator=False
    ).digest != compile_product_contract(changed, run_legacy_validator=False).digest


def test_contract_input_digest_change_invalidates_digest() -> None:
    baseline = _contract()
    changed = _contract()
    changed["contract_metadata"]["input_digests"]["sal_facts_sha256"] = "c" * 64
    assert compile_product_contract(
        baseline, run_legacy_validator=False
    ).digest != compile_product_contract(changed, run_legacy_validator=False).digest


def test_mandatory_capability_without_provenance_fails_closed() -> None:
    source = _contract()
    source["capabilities"][0]["provenance"] = []
    compiled = compile_product_contract(source, run_legacy_validator=False)
    assert "MISSING_PROVENANCE_REFERENCE" in {issue.code for issue in compiled.issues}
    assert not compiled.ready


def test_unpinned_authority_and_foreign_fact_fail_closed() -> None:
    source = _contract()
    source["authoritative_sources"][0].pop("content_hash")
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


def test_machinery_failures_enter_current_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    report = repo / ".supervisor" / "skill-contract-validation-results.yaml"
    report.parent.mkdir(parents=True)
    report.write_text(
        """
- skill_id: broken-skill
  findings:
    - check: command_file_exists
      detail: command file missing
      result: FAIL
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(
        ProductionProgram, "audit_sal_status_policy", lambda _self: []
    )
    program = ProductionProgram(tmp_path / "state")
    observed = program.audit_machinery()
    assert len(observed) == 1
    gap = program.next_gap()
    assert gap is not None
    assert gap.format_id == "_machinery"
    assert gap.obligation_id == "broken-skill"
    assert gap.category == "referential_integrity"


def test_openraster_target_uses_canonical_ora_contract_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.format_contract.product_contract as contract_module
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    package = repo / "src" / "python" / "openraster"
    tests = repo / "tests" / "python" / "openraster"
    contract = repo / "shared" / "format-contracts" / "ora.yaml"
    package.mkdir(parents=True)
    tests.mkdir(parents=True)
    contract.parent.mkdir(parents=True)
    (package / "marker.py").write_text("PACKAGE = 'openraster'\n", encoding="utf-8")
    (tests / "test_marker.py").write_text("def test_marker(): pass\n", encoding="utf-8")
    contract.write_text("contract_metadata:\n  format_id: ora\n", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", repo)

    compiled_paths: list[Path] = []

    def fake_compile(path: Path) -> SimpleNamespace:
        compiled_paths.append(path)
        return SimpleNamespace(
            format_id="ora",
            digest="a" * 64,
            ready=True,
            obligations=(),
            issues=(),
        )

    monkeypatch.setattr(contract_module, "load_and_compile", fake_compile)
    program = ProductionProgram(tmp_path / "state")
    snapshot = program.discover("openraster")
    evidence = program.compile_contract("openraster")

    assert TARGETS_BY_PRODUCT["openraster"].contract_format_id == "ora"
    assert snapshot["format_id"] == "openraster"
    assert snapshot["contract_format_id"] == "ora"
    assert snapshot["source_package_id"] == "openraster"
    assert snapshot["paths"] == [
        "src/python/openraster",
        "tests/python/openraster",
        "shared/format-contracts/ora.yaml",
    ]
    assert compiled_paths == [contract]
    assert evidence["format_id"] == "openraster"
    assert evidence["contract_format_id"] == "ora"
    assert set(program.formats) >= {"openraster"}
    assert "ora" not in program.formats


def test_identity_targets_retain_previous_path_behavior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    for target in TARGETS_BY_PRODUCT.values():
        if target.product_id == "openraster":
            continue
        assert target.contract_format_id == target.product_id
        assert target.source_package_id == target.product_id

    first = ProductionProgram(tmp_path / "state-one").discover("ipynb")
    second = ProductionProgram(tmp_path / "state-two").discover("ipynb")
    assert first == second


def test_compiled_contract_identity_mismatch_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.format_contract.product_contract as contract_module
    import tools.supervisor.production_program as module

    monkeypatch.setattr(module, "REPO_ROOT", tmp_path / "repo")
    monkeypatch.setattr(
        contract_module,
        "load_and_compile",
        lambda _path: SimpleNamespace(
            format_id="openraster",
            digest="b" * 64,
            ready=True,
            obligations=(),
            issues=(),
        ),
    )
    program = ProductionProgram(tmp_path / "state")
    program.transition("openraster", "SNAPSHOT", evidence={})
    with pytest.raises(ValueError, match="compiled contract identity mismatch"):
        program.compile_contract("openraster")


def test_target_contract_ids_are_backed_by_canonical_registry() -> None:
    evidence = validate_target_registry()
    assert len(evidence["registry_sha256"]) == 64
    assert set(evidence["contract_format_ids"]) == {
        target.contract_format_id for target in TARGETS_BY_PRODUCT.values()
    }


def test_sal_status_audit_resolves_schema_drift_and_tracks_fact_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    schema_source = (
        Path(module.__file__).resolve().parents[2]
        / "schemas"
        / "sal-facts"
        / "sal-facts-schema.json"
    )
    schema = repo / "schemas" / "sal-facts" / "sal-facts-schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_bytes(schema_source.read_bytes())
    store = repo / "shared" / "sal-facts" / "testfmt.yaml"
    store.parent.mkdir(parents=True)
    contract = repo / "shared" / "format-contracts" / "testfmt.yaml"
    contract.parent.mkdir(parents=True)
    store.write_text(
        """
format_id: testfmt
facts:
  - fact_id: SAL-TESTFMT-00001
    qname: FACT-TESTFMT-001
    claim: A structurally derived test fact.
    verification_status: structural_derivation
""".lstrip(),
        encoding="utf-8",
    )
    contract.write_text(
        """
contract_metadata:
  format_id: testfmt
capabilities:
  - capability_id: TESTFMT-READ-001
    level: MUST
    provenance: [SAL-TESTFMT-00001]
""".lstrip(),
        encoding="utf-8",
    )
    target = ProductTarget("testproduct", "testfmt", "testproduct")
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(module, "TARGETS", (target,))

    program = ProductionProgram(tmp_path / "state")
    program.reconcile_gap(
        Gap(
            SAL_STATUS_SCHEMA_GAP_ID,
            "_machinery",
            "SAL_SCHEMA_STATUS_ENUM",
            "referential_integrity",
            "HIGH",
            "stale",
        )
    )
    observed = program.audit_sal_status_policy()
    assert program.gaps[SAL_STATUS_SCHEMA_GAP_ID].state == "RESOLVED"
    authority_gap = next(
        gap for gap in observed if gap["format_id"] == "testproduct"
    )
    assert "structural_derivation=1" in authority_gap["root_cause"]

    store.write_text(
        store.read_text(encoding="utf-8").replace(
            "structural_derivation", "verified"
        ),
        encoding="utf-8",
    )
    assert not program.audit_sal_status_policy()
    assert program.gaps[authority_gap["gap_id"]].state == "RESOLVED"
