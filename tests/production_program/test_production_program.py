"""Regression controls for the production contract, proof, and controller."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tools.format_contract.product_contract import compile_product_contract
from tools.requirements_authority.production_graph import ProductionProofGraph
from tools.supervisor.production_program import (
    SAL_STATUS_SCHEMA_GAP_ID,
    TARGETS_BY_PRODUCT,
    Gap,
    ProductTarget,
    ProductionProgram,
    source_creation_authorization,
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


def _proof_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    import tools.format_contract.product_contract as contract_module
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    source = repo / "src" / "python" / "ipynb"
    module_root = source / "src" / "format_factory" / "ipynb"
    module_root.mkdir(parents=True)
    (module_root / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    test_path = repo / "tests" / "python" / "ipynb" / "test_contract.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_contract(): assert True\n", encoding="utf-8")
    contract_path = repo / "shared" / "format-contracts" / "ipynb.yaml"
    contract_path.parent.mkdir(parents=True)
    artifact = repo / "authorities" / "ipynb.bin"
    artifact.parent.mkdir()
    artifact.write_bytes(b"test authority")
    contract = _contract()
    contract["authoritative_sources"][0]["local_path"] = "authorities/ipynb.bin"
    contract["authoritative_sources"][0]["content_hash"] = hashlib.sha256(
        artifact.read_bytes()
    ).hexdigest()
    contract_path.write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    for relative in (
        "tools/supervisor/production_program.py",
        "tools/format_contract/product_contract.py",
        "tools/requirements_authority/production_graph.py",
    ):
        tool = repo / relative
        tool.parent.mkdir(parents=True, exist_ok=True)
        tool.write_text(f"# {relative}\n", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(contract_module, "REPO_ROOT", repo)
    return repo, source, test_path


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


def test_authority_class_is_preserved_and_digest_bound() -> None:
    baseline = _contract()
    changed = _contract()
    changed["authoritative_sources"][0]["authority_class"] = "PRODUCT_REQUIREMENT"

    baseline_compiled = compile_product_contract(
        baseline, run_legacy_validator=False
    )
    changed_compiled = compile_product_contract(
        changed, run_legacy_validator=False
    )

    assert baseline_compiled.authorities[0]["authority_class"] == "AUTHORITATIVE"
    assert changed_compiled.authorities[0]["authority_class"] == "PRODUCT_REQUIREMENT"
    assert baseline_compiled.digest != changed_compiled.digest


def test_loaded_authority_is_bound_to_repository_artifact_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.format_contract.product_contract as contract_module

    contract = _contract()
    artifact = tmp_path / "authorities" / "spec.bin"
    artifact.parent.mkdir()
    artifact.write_bytes(b"normative-v1")
    authority = contract["authoritative_sources"][0]
    authority["local_path"] = "authorities/spec.bin"
    authority["content_hash"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    contract_path = tmp_path / "shared" / "format-contracts" / "ipynb.yaml"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(yaml.safe_dump(contract), encoding="utf-8")
    monkeypatch.setattr(contract_module, "REPO_ROOT", tmp_path)

    first = contract_module.load_and_compile(contract_path)
    assert first.authorities[0]["artifact_verified"] is True
    assert first.authorities[0]["artifact_sha256"] == authority["content_hash"]
    assert not {
        issue.code for issue in first.issues
    } & {
        "AUTHORITY_ARTIFACT_PATH_MISSING",
        "AUTHORITY_ARTIFACT_PATH_UNSAFE",
        "AUTHORITY_ARTIFACT_MISSING",
        "AUTHORITY_ARTIFACT_DIGEST_MISMATCH",
    }

    artifact.write_bytes(b"normative-v2")
    changed = contract_module.load_and_compile(contract_path)
    assert changed.digest != first.digest
    assert changed.authorities[0]["acquired"] is False
    assert "AUTHORITY_ARTIFACT_DIGEST_MISMATCH" in {
        issue.code for issue in changed.issues
    }


def test_loaded_authority_rejects_path_outside_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.format_contract.product_contract as contract_module

    contract = _contract()
    authority = contract["authoritative_sources"][0]
    authority["local_path"] = "../outside.bin"
    contract_path = tmp_path / "contract.yaml"
    contract_path.write_text(yaml.safe_dump(contract), encoding="utf-8")
    monkeypatch.setattr(contract_module, "REPO_ROOT", tmp_path)

    compiled = contract_module.load_and_compile(contract_path)
    assert compiled.authorities[0]["acquired"] is False
    assert "AUTHORITY_ARTIFACT_PATH_UNSAFE" in {
        issue.code for issue in compiled.issues
    }


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


def test_equal_priority_gaps_follow_locked_format_wave_order(tmp_path: Path) -> None:
    program = ProductionProgram(tmp_path)
    nrrd = Gap("G-NRRD", "nrrd", "read", "security", "HIGH", "missing")
    safetensors = Gap(
        "G-SAFE", "safetensors", "read", "security", "HIGH", "missing"
    )
    program.reconcile_gap(nrrd)
    program.reconcile_gap(safetensors)
    assert program.next_gap() == safetensors


def test_blocked_format_cannot_stall_an_actionable_product(tmp_path: Path) -> None:
    program = ProductionProgram(tmp_path)
    blocked = Gap(
        "G-ORA",
        "openraster",
        "PRODUCTION_PACKAGE_CHASSIS",
        "referential_integrity",
        "HIGH",
        "Gate 9 is not passed",
        blocking_status="BLOCKED_DEPENDENCY",
    )
    actionable = Gap(
        "G-XLIFF",
        "xliff",
        "PRODUCTION_PACKAGE_CHASSIS",
        "referential_integrity",
        "HIGH",
        "package is missing",
    )
    program.reconcile_gap(blocked)
    program.reconcile_gap(actionable)
    assert program.next_gap() == actionable
    assert program.next_blocked_gap() == blocked
    status = program.status()
    assert status["open_gap_count"] == 2
    assert status["blocked_gap_count"] == 1


def test_source_creation_requires_complete_gate_9_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    registry = repo / "registry" / "format-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        """
formats:
  - format_id: ora
    implementation_authorized: false
    gates:
      gate_9:
        status: not_started
        approved_by: null
        approved_date: null
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    target = ProductTarget("openraster", "ora", "openraster")
    denied = source_creation_authorization(target)
    assert denied["authorized"] is False
    assert "implementation_authorized=true" in denied["reason"]

    registry.write_text(
        registry.read_text(encoding="utf-8")
        .replace("implementation_authorized: false", "implementation_authorized: true")
        .replace("status: not_started", "status: passed_oss_readiness")
        .replace("approved_by: null", "approved_by: delegated-gate-decision")
        .replace("approved_date: null", "approved_date: 2026-07-23"),
        encoding="utf-8",
    )
    allowed = source_creation_authorization(target)
    assert allowed["authorized"] is True
    assert len(allowed["registry_sha256"]) == 64


def test_chassis_audit_marks_unapproved_source_as_blocked_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.supervisor.production_program as module

    repo = tmp_path / "repo"
    registry = repo / "registry" / "format-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        """
formats:
  - format_id: ora
    gates:
      gate_9:
        status: not_started
        approved_by: null
        approved_date: null
""".lstrip(),
        encoding="utf-8",
    )
    core_module = (
        repo / "src" / "python" / "core" / "src" / "format_factory" / "core"
    )
    core_module.mkdir(parents=True)
    (core_module / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "python" / "core" / "pyproject.toml").write_text(
        """
[project]
name = "format-factory-core"
requires-python = ">=3.11"
""".lstrip(),
        encoding="utf-8",
    )
    (repo / "tests" / "python" / "core").mkdir(parents=True)
    target = ProductTarget("openraster", "ora", "openraster")
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(module, "TARGETS", (target,))
    monkeypatch.setattr(module, "TARGETS_BY_PRODUCT", {"openraster": target})

    program = ProductionProgram(tmp_path / "state")
    observed = program._audit_chassis()
    gap = next(item for item in observed if item["format_id"] == "openraster")
    assert gap["blocking_status"] == "BLOCKED_DEPENDENCY"
    assert gap["owning_task"] == "AUTO-OPENRASTER-GATE9-READINESS"
    assert "Gate 9" in gap["root_cause"]
    assert program.next_gap() is None
    assert program.next_blocked_gap() is not None


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
    relabeled = program.audit_sal_status_policy()
    relabeled_gap = next(
        gap for gap in relabeled if gap["format_id"] == "testproduct"
    )
    assert "no content-addressed verification record=1" in relabeled_gap["root_cause"]
    assert program.gaps[authority_gap["gap_id"]].state == "OPEN"


def test_verified_label_without_live_receipt_still_blocks_promotion(
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
    store.write_text(
        """
format_id: testfmt
facts:
  - fact_id: SAL-TESTFMT-00001
    qname: FACT-TESTFMT-001
    claim: A fact whose label was edited without proof.
    verification_status: verified
""".lstrip(),
        encoding="utf-8",
    )
    contract = repo / "shared" / "format-contracts" / "testfmt.yaml"
    contract.parent.mkdir(parents=True)
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
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(
        module,
        "TARGETS",
        (ProductTarget("testproduct", "testfmt", "testproduct"),),
    )

    observed = ProductionProgram(tmp_path / "state").audit_sal_status_policy()
    authority_gap = next(
        gap for gap in observed if gap["format_id"] == "testproduct"
    )
    assert "no content-addressed verification record=1" in authority_gap["root_cause"]


def test_source_and_test_presence_do_not_satisfy_mandatory_obligations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _proof_repo(tmp_path, monkeypatch)
    program = ProductionProgram(tmp_path / "state")

    evidence = program.audit_implementation("ipynb")

    assert evidence["mandatory_obligation_count"] == 2
    assert evidence["unmet_obligation_count"] == 2
    assert evidence["promotion"]["state"] == "IMPLEMENTATION_IN_PROGRESS"
    gaps = [
        gap
        for gap in program.gaps.values()
        if gap.format_id == "ipynb" and gap.state == "OPEN"
    ]
    assert len(gaps) == 2
    assert all("no live digest-bound executed" in gap.root_cause for gap in gaps)


def test_one_executed_result_satisfies_only_its_bound_obligation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")

    proof = program.execute_proof(
        "ipynb",
        positive["obligation_id"],
        polarity="positive",
        test_paths=[test_path.relative_to(_repo).as_posix()],
        fixture_paths=[],
        package_paths=[],
        command=[sys.executable, "-c", "print('executed')"],
    )
    evidence = program.audit_implementation("ipynb")

    assert proof["executed"] is True
    assert evidence["unmet_obligation_count"] == 1
    remaining = evidence["promotion"]["unmet_obligations"]
    assert positive["obligation_id"] not in remaining
    assert len(remaining) == 1


@pytest.mark.parametrize("mutation", ("change", "delete"))
def test_changed_or_deleted_test_revokes_executed_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")
    program.execute_proof(
        "ipynb",
        positive["obligation_id"],
        polarity="positive",
        test_paths=[test_path.relative_to(repo).as_posix()],
        fixture_paths=[],
        package_paths=[],
        command=[sys.executable, "-c", "print('executed')"],
    )

    if mutation == "change":
        test_path.write_text("def test_contract(): assert 1 == 1\n", encoding="utf-8")
    else:
        test_path.unlink()
    evidence = program.audit_implementation("ipynb")

    assert evidence["promotion"]["state"] == "INVALIDATED"
    assert positive["obligation_id"] in evidence["stale_proof_obligations"]
    gap = next(
        gap
        for gap in program.gaps.values()
        if gap.obligation_id == positive["obligation_id"]
    )
    assert gap.invalidation_reason == "proof_input_changed"


def test_wrong_polarity_and_nonzero_command_cannot_record_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")
    args = {
        "format_id": "ipynb",
        "obligation_id": positive["obligation_id"],
        "test_paths": [test_path.relative_to(repo).as_posix()],
        "fixture_paths": [],
        "package_paths": [],
    }

    with pytest.raises(ValueError, match="requires positive proof"):
        program.execute_proof(
            **args,
            polarity="negative",
            command=[sys.executable, "-c", "print('wrong polarity')"],
        )
    with pytest.raises(RuntimeError, match="exit code 7"):
        program.execute_proof(
            **args,
            polarity="positive",
            command=[sys.executable, "-c", "raise SystemExit(7)"],
        )
    assert program.proofs == {}


def test_input_modified_during_execution_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    fixture = repo / "samples" / "input.bin"
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(b"before")
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")

    with pytest.raises(ValueError, match="inputs changed during execution"):
        program.execute_proof(
            "ipynb",
            positive["obligation_id"],
            polarity="positive",
            test_paths=[test_path.relative_to(repo).as_posix()],
            fixture_paths=[fixture.relative_to(repo).as_posix()],
            package_paths=[],
            command=[
                sys.executable,
                "-c",
                "from pathlib import Path; Path('samples/input.bin').write_bytes(b'after')",
            ],
        )
    assert program.proofs == {}


def test_package_and_executed_environment_are_digest_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    package = repo / ".local" / "packages" / "format_factory_ipynb.whl"
    package.parent.mkdir(parents=True)
    package.write_bytes(b"wheel-one")
    monkeypatch.setattr(
        ProductionProgram,
        "_installed_wheel_manifest",
        staticmethod(
            lambda _command, packages: [
                {
                    "wheel_name": packages[0].name,
                    "wheel_sha256": "a" * 64,
                    "distribution": "format-factory-ipynb",
                    "version": "1.0",
                    "verified_file_count": 1,
                    "installed_content_digest": "b" * 64,
                }
            ]
        ),
    )
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")

    proof = program.execute_proof(
        "ipynb",
        positive["obligation_id"],
        polarity="positive",
        test_paths=[test_path.relative_to(repo).as_posix()],
        fixture_paths=[],
        package_paths=[package.relative_to(repo).as_posix()],
        command=[sys.executable, "-c", "print('installed wheel exercised')"],
    )

    assert proof["package_paths"] == (
        ".local/packages/format_factory_ipynb.whl",
    )
    assert proof["package_digest"]
    assert proof["environment"]["executable_sha256"]
    assert proof["environment"]["runtime"]["python"]
    program.audit_implementation("ipynb")
    node_types = {
        json.loads(line)["node_type"]
        for line in (
            program.graph_root / "ipynb" / "nodes.jsonl"
        ).read_text(encoding="utf-8").splitlines()
    }
    assert {"BuiltPackage", "InstalledPackageResult"} <= node_types

    package.write_bytes(b"wheel-two")
    evidence = program.audit_implementation("ipynb")
    assert evidence["promotion"]["state"] == "INVALIDATED"
    assert positive["obligation_id"] in evidence["stale_proof_obligations"]


def test_package_modified_during_execution_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    package = repo / ".local" / "packages" / "format_factory_ipynb.whl"
    package.parent.mkdir(parents=True)
    package.write_bytes(b"before")
    monkeypatch.setattr(
        ProductionProgram,
        "_installed_wheel_manifest",
        staticmethod(
            lambda _command, packages: [
                {
                    "wheel_name": packages[0].name,
                    "wheel_sha256": "a" * 64,
                    "distribution": "format-factory-ipynb",
                    "version": "1.0",
                    "verified_file_count": 1,
                    "installed_content_digest": "b" * 64,
                }
            ]
        ),
    )
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")

    with pytest.raises(ValueError, match="inputs changed during execution"):
        program.execute_proof(
            "ipynb",
            positive["obligation_id"],
            polarity="positive",
            test_paths=[test_path.relative_to(repo).as_posix()],
            fixture_paths=[],
            package_paths=[package.relative_to(repo).as_posix()],
            command=[
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "Path('.local/packages/format_factory_ipynb.whl')"
                    ".write_bytes(b'after')"
                ),
            ],
        )
    assert program.proofs == {}


def test_uninstalled_wheel_cannot_be_claimed_as_installed(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / "ff_proof_never_installed-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "ff_proof_never_installed-1.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: ff-proof-never-installed\nVersion: 1.0\n",
        )
        archive.writestr("ff_proof_never_installed/__init__.py", "VALUE = 1\n")

    with pytest.raises(ValueError, match="installed wheel verification failed"):
        ProductionProgram._installed_wheel_manifest(
            [sys.executable, "-c", "print('unused')"], [wheel]
        )


def test_changed_proof_tool_revokes_executed_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _source, test_path = _proof_repo(tmp_path, monkeypatch)
    compiled = compile_product_contract(_contract(), run_legacy_validator=False)
    positive = next(
        item for item in compiled.obligations if item["kind"] == "positive"
    )
    program = ProductionProgram(tmp_path / "state")
    program.execute_proof(
        "ipynb",
        positive["obligation_id"],
        polarity="positive",
        test_paths=[test_path.relative_to(repo).as_posix()],
        fixture_paths=[],
        package_paths=[],
        command=[sys.executable, "-c", "print('executed')"],
    )

    tool = repo / "tools" / "supervisor" / "production_program.py"
    tool.write_text("# changed proof tool\n", encoding="utf-8")
    evidence = program.audit_implementation("ipynb")

    assert evidence["promotion"]["state"] == "INVALIDATED"
    assert positive["obligation_id"] in evidence["stale_proof_obligations"]


def test_three_implementation_projections_are_byte_identical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _proof_repo(tmp_path, monkeypatch)
    graph_digests = []
    graph_bytes = []
    for index in range(3):
        program = ProductionProgram(tmp_path / f"state-{index}")
        evidence = program.audit_implementation("ipynb")
        graph_digests.append(evidence["graph_digest"])
        graph_bytes.append(
            (
                (program.graph_root / "ipynb" / "nodes.jsonl").read_bytes(),
                (program.graph_root / "ipynb" / "edges.jsonl").read_bytes(),
            )
        )
    assert len(set(graph_digests)) == 1
    assert graph_bytes[0] == graph_bytes[1] == graph_bytes[2]
