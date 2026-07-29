"""Regression tests for the deterministic production capability compiler."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from tools.format_contract.capability_universe import (
    UniverseError,
    check_outputs,
    compile_universe,
    write_outputs,
)
from tools.format_contract.capability_universe_command import scaffold_enrichment

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_SCHEMA = (
    REPO_ROOT / "schemas/format-contracts/authority-lock.schema.json"
)


def _write_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    authority = root / "authorities" / "ipynb.bin"
    authority.parent.mkdir(parents=True)
    authority.write_bytes(b"authority")
    contract = {
        "contract_metadata": {
            "format_id": "ipynb",
            "contract_id": "FC-IPYNB-V1",
            "family": "test",
            "target_spec_version": "4.5",
        },
        "authoritative_sources": [
            {
                "source_id": "SRC-NB-001",
                "title": "Notebook schema",
                "organization": "Test",
                "version": "4.5",
                "authority_class": "AUTHORITATIVE",
                "acquisition_status": "ACQUIRED",
                "local_path": "authorities/ipynb.bin",
                "content_hash": hashlib.sha256(authority.read_bytes()).hexdigest(),
            }
        ],
        "capabilities": [
            {
                "capability_id": "IPYNB-READ-001",
                "level": "MUST",
                "provenance": ["SAL-IPYNB-00001", "POL-TEST-READ-01"],
                "required_behavior": ["Read notebook JSON."],
                "security_requirements": ["Reject oversized input."],
                "required_tests": ["positive", "negative"],
            },
            {
                "capability_id": "IPYNB-EXEC-001",
                "level": "SHOULD",
                "provenance": ["SAL-IPYNB-00002"],
                "required_behavior": ["Describe execution metadata."],
            },
        ],
    }
    facts = {
        "facts": [
            {"fact_id": "SAL-IPYNB-00001", "claim": "Notebook is JSON."},
            {"fact_id": "SAL-IPYNB-00002", "claim": "Code cells hold execution metadata."},
        ]
    }
    policy = {
        "schema": "ff6/capability-policy@1",
        "goal_id": "FF6-PRODUCTION-LIBRARIES-001",
        "classifications": [
            "STABLE_REQUIRED",
            "OPTIONAL_ADAPTER_REQUIRED",
            "PREVIEW_ISOLATED",
            "EXCLUDED_WITH_AUTHORITY",
        ],
        "formats": {
            "ipynb": {
                "target_profiles": ["nbformat_4_0", "nbformat_4_5"],
                "classification_locks": {
                    "IPYNB-EXEC-001": "EXCLUDED_WITH_AUTHORITY"
                },
            }
        },
    }
    common = {
        "stable_name": "Read",
        "developer_use_cases": ["Load a notebook."],
        "spec_profiles": ["nbformat_4_5"],
        "authority_fact_ids": ["SAL-IPYNB-00001", "POL-TEST-READ-01"],
        "public_symbols": "PLANNED",
        "source_symbols": "PLANNED",
        "model_invariants": ["JSON structure is retained."],
        "preservation_contract": ["Unknown metadata is retained."],
        "error_contract": ["Structured error."],
        "security_contract": ["No execution."],
        "resource_limits": ["Input bytes are bounded."],
        "performance_budget": "PLANNED",
        "dependency_policy": "PLANNED",
        "positive_tests": "PLANNED",
        "negative_tests": "PLANNED",
        "property_tests": "PLANNED",
        "roundtrip_tests": "PLANNED",
        "fixtures": "PLANNED",
        "independent_oracles": "PLANNED",
        "documentation_examples": "PLANNED",
        "compatibility_status": "PLANNED",
        "proof_node_ids": "PLANNED",
        "invalidation_inputs": ["contract", "SAL", "policy"],
        "taskcard_ids": ["TC-TEST"],
        "release_state": "PLANNED",
    }
    read = {"capability_id": "IPYNB-READ-001", "classification": "STABLE_REQUIRED", **common}
    execute = {
        "capability_id": "IPYNB-EXEC-001",
        "classification": "EXCLUDED_WITH_AUTHORITY",
        **copy.deepcopy(common),
        "stable_name": "Notebook execution",
        "authority_fact_ids": ["SAL-IPYNB-00002"],
        "exclusion": {
            "authority_basis": "The file format describes code and metadata but does not require execution.",
            "user_disposition": "Use a separately audited execution service; this library never executes code.",
        },
    }
    _write_yaml(root / "shared/format-contracts/ipynb.yaml", contract)
    _write_yaml(
        root / "shared/format-contracts/authority-lock.yaml",
        {
            "schema_version": "1.0",
            "lock_id": "FF-AUTHORITY-LOCK-001",
            "sources": [
                {
                    "source_id": "SRC-NB-001",
                    "format_id": "ipynb",
                    "title": "Notebook schema",
                    "organization": "Test",
                    "version": "4.5",
                    "authority_class": "AUTHORITATIVE",
                    "materialized_path": "authorities/ipynb.bin",
                    "expected_sha256": hashlib.sha256(
                        authority.read_bytes()
                    ).hexdigest(),
                    "media_type": "application/octet-stream",
                    "legal": {
                        "license_id": "TEST",
                        "redistribution": "LOCAL_CACHE_ONLY",
                        "use_status": "APPROVED_FOR_LOCAL_USE",
                        "evidence": "test fixture",
                    },
                    "limits": {
                        "max_bytes": 1024,
                        "timeout_seconds": 1,
                        "max_redirects": 0,
                    },
                    "fetch": {
                        "kind": "LOCAL_FILE",
                        "source_path": "authorities/ipynb.bin",
                    },
                }
            ],
            "generated_by": "test",
            "visibility": "internal",
        },
    )
    authority_schema = (
        root / "schemas/format-contracts/authority-lock.schema.json"
    )
    authority_schema.parent.mkdir(parents=True, exist_ok=True)
    authority_schema.write_bytes(AUTHORITY_SCHEMA.read_bytes())
    _write_yaml(root / "shared/sal-facts/ipynb.yaml", facts)
    _write_yaml(
        root / "shared/sal-facts/evidence/ipynb.yaml",
        {
            "targets": {"schema": {"source_id": "SRC-NB-001"}},
            "facts": [
                {
                    "fact_id": "SAL-IPYNB-00001",
                    "assertions": [{"target": "schema"}],
                },
                {
                    "fact_id": "SAL-IPYNB-00002",
                    "assertions": [{"target": "schema"}],
                },
            ],
        },
    )
    _write_yaml(
        root / "shared/format-contracts/policy/shared-library-contract.yaml",
        {"capabilities": []},
    )
    _write_yaml(
        root / "shared/format-contracts/policy/family-packs/test.yaml",
        {"capabilities": [{"id": "POL-TEST-READ-01"}]},
    )
    _write_yaml(root / "shared/format-contracts/research/ipynb.yaml", {"findings": []})
    _write_yaml(root / "policy.yaml", policy)
    _write_yaml(
        root / "enrichments/ipynb.yaml",
        {
            "schema": "ff6/capability-enrichment@1",
            "format_id": "ipynb",
            "capabilities": [read, execute],
        },
    )
    compiler = root / "tools/compiler.py"
    compiler.parent.mkdir(parents=True)
    compiler.write_text("# compiler v1\n", encoding="utf-8")
    schema = root / "schemas/universe.json"
    schema.parent.mkdir(parents=True, exist_ok=True)
    schema.write_text(
        json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema"}),
        encoding="utf-8",
    )
    return root


def _compile(root: Path):
    return compile_universe(
        root,
        ("ipynb",),
        policy_path=Path("policy.yaml"),
        enrichment_dir=Path("enrichments"),
        compiler_paths=(Path("tools/compiler.py"),),
        schema_paths=(Path("schemas/universe.json"),),
    )


def test_scaffold_preserves_curated_detail_and_refreshes_contract_fields(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    policy_path = root / "policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    policy["formats"]["ipynb"]["profile_applicability"] = {
        "IPYNB-EXEC-001": ["nbformat_4_5"]
    }
    policy["formats"]["ipynb"]["exclusions"] = {
        "IPYNB-EXEC-001": {
            "authority_basis": "Stored code is data, not an execution protocol.",
            "user_disposition": "Use an isolated execution service.",
        }
    }
    _write_yaml(policy_path, policy)
    contract_path = root / "shared/format-contracts/ipynb.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract["capabilities"][0]["provenance"].append("SAL-IPYNB-00003")
    _write_yaml(contract_path, contract)

    scaffold_enrichment(
        root,
        "ipynb",
        policy_path=Path("policy.yaml"),
        output_path=Path("enrichments/ipynb.yaml"),
        task_id="TC-REFRESH",
    )

    result = yaml.safe_load(
        (root / "enrichments/ipynb.yaml").read_text(encoding="utf-8")
    )
    by_id = {item["capability_id"]: item for item in result["capabilities"]}
    read = by_id["IPYNB-READ-001"]
    execute = by_id["IPYNB-EXEC-001"]
    assert read["stable_name"] == "Read"
    assert read["model_invariants"] == ["JSON structure is retained."]
    assert read["spec_profiles"] == ["nbformat_4_0", "nbformat_4_5"]
    assert read["authority_fact_ids"] == [
        "SAL-IPYNB-00001",
        "POL-TEST-READ-01",
        "SAL-IPYNB-00003",
    ]
    assert read["taskcard_ids"] == ["TC-TEST", "TC-REFRESH"]
    assert execute["spec_profiles"] == ["nbformat_4_5"]
    assert execute["exclusion"] == policy["formats"]["ipynb"]["exclusions"][
        "IPYNB-EXEC-001"
    ]


def test_compiler_emits_every_canonical_obligation_and_no_parallel_ids(
    tmp_path: Path,
) -> None:
    result = _compile(_repo(tmp_path))
    obligations = yaml.safe_load(result.outputs["obligations/ipynb.yaml"])[
        "obligations"
    ]
    assert len(obligations) == 3
    assert all(item["obligation_id"].startswith("SAL-IPYNB-OBL-") for item in obligations)
    assert {item["capability_id"] for item in obligations} == {
        "IPYNB-READ-001",
        "IPYNB-EXEC-001",
    }
    capabilities = yaml.safe_load(result.outputs["capabilities/ipynb.yaml"])[
        "capabilities"
    ]
    linked = {
        obligation_id
        for capability in capabilities
        for obligation_id in capability["normative_obligation_ids"]
    }
    assert linked == {item["obligation_id"] for item in obligations}
    assert all(item["authority_source_ids"] == ["SRC-NB-001"] for item in obligations)
    assert all(item["spec_profiles"] for item in obligations)
    assert {
        tuple(item["spec_profiles"])
        for item in obligations
        if item["capability_id"] == "IPYNB-READ-001"
    } == {("nbformat_4_5",)}
    assert result.manifest["authority_artifacts"] == [
        {
            "format_id": "ipynb",
            "source_id": "SRC-NB-001",
            "repository_path": "authorities/ipynb.bin",
            "expected_sha256": hashlib.sha256(b"authority").hexdigest(),
            "observed_sha256": hashlib.sha256(b"authority").hexdigest(),
            "status": "MATCH",
        }
    ]
    assert "schemas/universe.json" in result.manifest["input_digests"]


def test_compiler_is_byte_deterministic_and_input_complete(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first = _compile(root)
    second = _compile(root)
    third = _compile(root)
    assert first.outputs == second.outputs == third.outputs
    assert first.manifest["diagnostic_authority_override"] is False
    assert first.manifest["promotion_eligible"] is True


def test_required_product_surface_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    policy_path = root / "policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    policy["formats"]["ipynb"]["required_capability_ids"] = [
        "IPYNB-READ-001",
        "IPYNB-MISSING-001",
    ]
    _write_yaml(policy_path, policy)
    with pytest.raises(UniverseError, match="required product surface is missing"):
        _compile(root)


def test_obligation_profiles_reject_values_outside_target(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    enrichment_path = root / "enrichments/ipynb.yaml"
    enrichment = yaml.safe_load(enrichment_path.read_text(encoding="utf-8"))
    enrichment["capabilities"][0]["spec_profiles"] = ["nbformat_5_0"]
    _write_yaml(enrichment_path, enrichment)
    with pytest.raises(UniverseError, match="profiles outside the selected stable target"):
        _compile(root)


def test_authority_artifact_mutation_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "authorities/ipynb.bin").write_bytes(b"mutated")
    with pytest.raises(UniverseError, match="AUTHORITY_ARTIFACT_DIGEST_MISMATCH"):
        _compile(root)


def test_authority_declaration_drift_and_omission_fail_closed(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    contract_path = root / "shared/format-contracts/ipynb.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract["authoritative_sources"][0]["title"] = "Drifted title"
    _write_yaml(contract_path, contract)
    with pytest.raises(UniverseError, match="AUTHORITY_LOCK_DECLARATION_MISMATCH"):
        _compile(root)

    root = _repo(tmp_path / "omitted")
    contract_path = root / "shared/format-contracts/ipynb.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract["authoritative_sources"] = []
    _write_yaml(contract_path, contract)
    with pytest.raises(UniverseError, match="AUTHORITY_LOCK_SOURCE_UNDECLARED"):
        _compile(root)


def test_diagnostic_authority_override_is_explicitly_non_promoting(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    (root / "authorities/ipynb.bin").write_bytes(b"mutated")
    result = compile_universe(
        root,
        ("ipynb",),
        policy_path=Path("policy.yaml"),
        enrichment_dir=Path("enrichments"),
        compiler_paths=(Path("tools/compiler.py"),),
        schema_paths=(Path("schemas/universe.json"),),
        allow_blocked_authority=True,
    )
    coverage = yaml.safe_load(result.outputs["capability-coverage.yaml"])
    assert coverage["assessment_status"] == "DIAGNOSTIC_ONLY"
    assert result.manifest["diagnostic_authority_override"] is True
    assert result.manifest["promotion_eligible"] is False
    assert result.manifest["authority_blocked_formats"] == ["ipynb"]


@pytest.mark.parametrize(
    "relative",
    [
        "policy.yaml",
        "tools/compiler.py",
        "schemas/universe.json",
        "shared/format-contracts/ipynb.yaml",
        "shared/sal-facts/ipynb.yaml",
        "shared/sal-facts/evidence/ipynb.yaml",
        "enrichments/ipynb.yaml",
        "shared/format-contracts/policy/shared-library-contract.yaml",
        "shared/format-contracts/policy/family-packs/test.yaml",
        "shared/format-contracts/research/ipynb.yaml",
        "shared/format-contracts/authority-lock.yaml",
        "schemas/format-contracts/authority-lock.schema.json",
    ],
)
def test_each_input_category_invalidates_aggregate(
    tmp_path: Path, relative: str
) -> None:
    root = _repo(tmp_path)
    baseline = _compile(root).manifest["aggregate_sha256"]
    path = root / relative
    path.write_bytes(path.read_bytes() + b"\n \n")
    assert _compile(root).manifest["aggregate_sha256"] != baseline


def test_compiler_rejects_missing_foreign_and_unlocked_classification(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    enrichment_path = root / "enrichments/ipynb.yaml"
    enrichment = yaml.safe_load(enrichment_path.read_text(encoding="utf-8"))
    enrichment["capabilities"].pop()
    _write_yaml(enrichment_path, enrichment)
    with pytest.raises(UniverseError, match="capability identity mismatch"):
        _compile(root)

    root = _repo(tmp_path / "foreign")
    enrichment_path = root / "enrichments/ipynb.yaml"
    enrichment = yaml.safe_load(enrichment_path.read_text(encoding="utf-8"))
    enrichment["capabilities"][0]["authority_fact_ids"][0] = "SAL-NRRD-00001"
    _write_yaml(enrichment_path, enrichment)
    with pytest.raises(UniverseError, match="foreign fact"):
        _compile(root)

    root = _repo(tmp_path / "lock")
    enrichment_path = root / "enrichments/ipynb.yaml"
    enrichment = yaml.safe_load(enrichment_path.read_text(encoding="utf-8"))
    enrichment["capabilities"][1]["classification"] = "OPTIONAL_ADAPTER_REQUIRED"
    _write_yaml(enrichment_path, enrichment)
    with pytest.raises(UniverseError, match="classification lock"):
        _compile(root)


def test_check_mode_detects_drift_without_writing(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = _compile(root)
    output = root / "out"
    write_outputs(output, result.outputs)
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    check_outputs(output, result.outputs)
    target = output / "capabilities/ipynb.yaml"
    target.write_text("drift\n", encoding="utf-8")
    with pytest.raises(UniverseError, match="output drift"):
        check_outputs(output, result.outputs)
    after = {
        p.relative_to(output): p.read_bytes()
        for p in output.rglob("*")
        if p.is_file() and p != target
    }
    assert after == {path: data for path, data in before.items() if path != Path("capabilities/ipynb.yaml")}
