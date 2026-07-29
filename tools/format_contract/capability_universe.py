"""Deterministic production capability and obligation projection compiler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from .capability_universe_runtime import (
    UniverseCompilation,
    UniverseError,
    add_input_digest,
    canonical_json,
    load_yaml,
    safe_path,
    sha256,
    validate_outputs,
    yaml_bytes,
)
from .capability_universe_validation import (
    CLASSIFICATIONS,
    DERIVED_FIELDS,
    LEGACY_CLASSIFICATIONS,
    REQUIRED_ENRICHMENT_FIELDS,
    iter_ids,
    validate_enrichment,
)
from .product_contract import CompiledProductContract, compile_product_contract


def _contract_context(
    root: Path,
    format_id: str,
    contract: dict[str, Any],
    input_digests: dict[str, str],
) -> tuple[set[str], list[dict[str, Any]]]:
    family = str(contract.get("contract_metadata", {}).get("family", ""))
    paths = [
        Path("shared/format-contracts/policy/shared-library-contract.yaml"),
        Path(f"shared/format-contracts/policy/family-packs/{family}.yaml"),
        Path(f"shared/format-contracts/research/{format_id}.yaml"),
    ]
    identities: set[str] = set()
    inputs: list[dict[str, Any]] = []
    for relative in paths:
        value, _ = load_yaml(root, relative)
        identities.update(iter_ids(value))
        inputs.append(add_input_digest(root, relative, input_digests))
    return identities, inputs


def _authority_state(
    compiled: CompiledProductContract,
) -> tuple[str, list[dict[str, Any]]]:
    issues = [
        {
            "code": issue.code,
            "severity": issue.severity,
            "message": issue.message,
            "reference": issue.reference,
        }
        for issue in compiled.issues
        if issue.code.startswith("AUTHORITY_")
    ]
    return ("READY" if not issues else "BLOCKED"), issues


def compile_universe(
    repo_root: Path,
    format_ids: Sequence[str],
    *,
    policy_path: Path,
    enrichment_dir: Path,
    compiler_paths: Sequence[Path] | None = None,
    schema_paths: Sequence[Path] | None = None,
    allow_blocked_authority: bool = False,
) -> UniverseCompilation:
    root = repo_root.resolve()
    ordered_formats = tuple(dict.fromkeys(str(item).lower() for item in format_ids))
    if not ordered_formats:
        raise UniverseError("at least one format is required")
    policy, _ = load_yaml(root, policy_path)
    if tuple(policy.get("classifications", ())) != CLASSIFICATIONS:
        raise UniverseError("policy classification vocabulary is not locked")
    format_policy = policy.get("formats")
    if not isinstance(format_policy, dict):
        raise UniverseError("policy formats mapping is missing")

    inputs: dict[str, str] = {}
    add_input_digest(root, policy_path, inputs)
    default_compilers = (
        Path("tools/format_contract/capability_universe.py"),
        Path("tools/format_contract/capability_universe_command.py"),
        Path("tools/format_contract/capability_universe_runtime.py"),
        Path("tools/format_contract/capability_universe_validation.py"),
        Path("tools/format_contract/product_contract.py"),
    )
    for relative in compiler_paths or default_compilers:
        add_input_digest(root, relative, inputs)
    default_schemas = (Path("schemas/ff6/capability-universe.schema.json"),)
    for relative in schema_paths or default_schemas:
        add_input_digest(root, relative, inputs)

    outputs: dict[str, bytes] = {}
    per_format_summary: dict[str, Any] = {}
    classification_counts = {item: 0 for item in CLASSIFICATIONS}
    total_obligations = 0
    authority_blocked: list[str] = []
    authority_artifacts: list[dict[str, Any]] = []
    all_capability_ids: set[str] = set()
    all_obligation_ids: set[str] = set()

    for format_id in ordered_formats:
        if format_id not in format_policy:
            raise UniverseError(f"format is absent from policy: {format_id}")
        contract_path = Path(f"shared/format-contracts/{format_id}.yaml")
        facts_path = Path(f"shared/sal-facts/{format_id}.yaml")
        fact_evidence_path = Path(f"shared/sal-facts/evidence/{format_id}.yaml")
        enrichment_path = enrichment_dir / f"{format_id}.yaml"
        contract, _ = load_yaml(root, contract_path)
        fact_store, _ = load_yaml(root, facts_path)
        fact_evidence, _ = load_yaml(root, fact_evidence_path)
        enrichment, _ = load_yaml(root, enrichment_path)
        common_input_keys = set(inputs)
        for relative in (
            contract_path,
            facts_path,
            fact_evidence_path,
            enrichment_path,
        ):
            add_input_digest(root, relative, inputs)
        policy_ids, policy_inputs = _contract_context(
            root, format_id, contract, inputs
        )
        format_input_keys = common_input_keys | {
            contract_path.as_posix(),
            facts_path.as_posix(),
            fact_evidence_path.as_posix(),
            enrichment_path.as_posix(),
            *(item["path"] for item in policy_inputs),
        }

        contract_format = str(
            contract.get("contract_metadata", {}).get("format_id", "")
        ).lower()
        if contract_format != format_id:
            raise UniverseError(
                f"contract format mismatch: expected {format_id}, got {contract_format}"
            )
        facts = {
            str(item["fact_id"]): item
            for item in fact_store.get("facts", [])
            if isinstance(item, dict) and item.get("fact_id")
        }
        evidence_targets = fact_evidence.get("targets", {}) or {}
        fact_source_ids: dict[str, list[str]] = {}
        for fact in fact_evidence.get("facts", []) or []:
            source_ids = {
                str(evidence_targets.get(assertion.get("target"), {}).get("source_id"))
                for assertion in fact.get("assertions", []) or []
                if isinstance(assertion, dict)
                and evidence_targets.get(assertion.get("target"), {}).get("source_id")
            }
            fact_source_ids[str(fact.get("fact_id"))] = sorted(source_ids)
        contract_capabilities = {
            str(item["capability_id"]): item
            for item in contract.get("capabilities", [])
            if isinstance(item, dict) and item.get("capability_id")
        }
        records = enrichment.get("capabilities", [])
        if not isinstance(records, list):
            raise UniverseError(f"{format_id}: enrichment capabilities must be a list")
        locks = format_policy[format_id].get("classification_locks", {}) or {}
        by_id = validate_enrichment(
            format_id,
            records,
            contract_capabilities,
            facts,
            policy_ids,
            locks,
        )

        compiled = compile_product_contract(
            contract, run_legacy_validator=False, authority_root=root
        )
        authority_status, authority_issues = _authority_state(compiled)
        for source in contract.get("authoritative_sources", []) or []:
            source_id = str(source.get("source_id", ""))
            repository_path = str(source.get("local_path", ""))
            expected = str(source.get("content_hash", "")).lower()
            observed: str | None = None
            status = "UNDECLARED"
            if repository_path and expected:
                artifact_path = safe_path(root, Path(repository_path))
                if artifact_path.is_file():
                    observed = sha256(artifact_path.read_bytes())
                    status = "MATCH" if observed == expected else "MISMATCH"
                else:
                    status = "MISSING"
            authority_artifacts.append(
                {
                    "format_id": format_id,
                    "source_id": source_id,
                    "repository_path": repository_path,
                    "expected_sha256": expected,
                    "observed_sha256": observed,
                    "status": status,
                }
            )
        if authority_status != "READY":
            authority_blocked.append(format_id)
            if not allow_blocked_authority:
                raise UniverseError(
                    f"{format_id}: authority closure is blocked: "
                    + ", ".join(issue["code"] for issue in authority_issues)
                )

        obligations_by_capability: dict[str, list[dict[str, Any]]] = {
            item: [] for item in contract_capabilities
        }
        obligation_records: list[dict[str, Any]] = []
        for item in compiled.obligations:
            obligation_id = str(item["obligation_id"])
            capability_id = str(item["capability_id"])
            if obligation_id in all_obligation_ids:
                raise UniverseError(f"duplicate obligation ID: {obligation_id}")
            if capability_id not in obligations_by_capability:
                raise UniverseError(
                    f"{obligation_id}: unknown owner {capability_id}"
                )
            all_obligation_ids.add(obligation_id)
            authority_sources = sorted(
                {
                    source_id
                    for fact_id in item["fact_ids"]
                    for source_id in fact_source_ids.get(str(fact_id), [])
                }
            )
            record = {
                "obligation_id": obligation_id,
                "format_id": format_id,
                "profile_id": item["profile_id"],
                "capability_id": capability_id,
                "classification": by_id[capability_id]["classification"],
                "level": item["level"],
                "kind": item["kind"],
                "source_field": item["source_field"],
                "authority_reference_ids": list(item["provenance_ids"]),
                "authority_fact_ids": list(item["fact_ids"]),
                "authority_source_ids": authority_sources,
                "rule_text": item["text"],
                "required_tests": list(item["required_tests"]),
                "release_gates": list(item["release_gates"]),
                "verification_status": "UNVERIFIED",
                "proof_node_ids": "PLANNED",
                "invalidation_inputs": sorted(format_input_keys),
            }
            obligations_by_capability[capability_id].append(record)
            obligation_records.append(record)
        obligation_records.sort(key=lambda item: item["obligation_id"])

        capability_records: list[dict[str, Any]] = []
        for capability_id in sorted(by_id):
            if capability_id in all_capability_ids:
                raise UniverseError(f"duplicate capability ID: {capability_id}")
            all_capability_ids.add(capability_id)
            source = by_id[capability_id]
            obligations = obligations_by_capability[capability_id]
            if not obligations:
                raise UniverseError(f"{capability_id}: no canonical obligations")
            record = {
                "capability_id": capability_id,
                "format_id": format_id,
                "stable_name": source["stable_name"],
                "classification": source["classification"],
                "developer_use_cases": source["developer_use_cases"],
                "spec_profiles": source["spec_profiles"],
                "authority_fact_ids": source["authority_fact_ids"],
                "normative_obligation_ids": [
                    item["obligation_id"] for item in obligations
                ],
            }
            for field in REQUIRED_ENRICHMENT_FIELDS:
                if field not in record:
                    record[field] = source[field]
            if "exclusion" in source:
                record["exclusion"] = source["exclusion"]
            classification_counts[str(source["classification"])] += 1
            capability_records.append(record)

        targets = list(format_policy[format_id].get("target_profiles", []))
        claimed_profiles = sorted(
            {
                str(profile)
                for record in capability_records
                for profile in record["spec_profiles"]
            }
        )
        missing_profiles = sorted(set(targets) - set(claimed_profiles))
        known_surface_gaps = list(
            format_policy[format_id].get("known_surface_gaps", [])
        )
        source_digest_map = {
            relative: inputs[relative] for relative in sorted(format_input_keys)
        }
        outputs[f"capabilities/{format_id}.yaml"] = yaml_bytes(
            {
                "schema": "ff6/format-capabilities@2",
                "goal_id": policy.get("goal_id"),
                "format_id": format_id,
                "contract_id": contract["contract_metadata"].get("contract_id"),
                "target_spec_version": contract["contract_metadata"].get(
                    "target_spec_version"
                ),
                "target_profiles": targets,
                "authority_status": authority_status,
                "capability_count": len(capability_records),
                "source_input_digests": source_digest_map,
                "capabilities": capability_records,
            }
        )
        outputs[f"obligations/{format_id}.yaml"] = yaml_bytes(
            {
                "schema": "ff6/format-obligations@2",
                "goal_id": policy.get("goal_id"),
                "format_id": format_id,
                "contract_id": contract["contract_metadata"].get("contract_id"),
                "authority_status": authority_status,
                "obligation_count": len(obligation_records),
                "source_input_digests": source_digest_map,
                "obligations": obligation_records,
            }
        )
        per_format_summary[format_id] = {
            "capability_count": len(capability_records),
            "obligation_count": len(obligation_records),
            "authority_status": authority_status,
            "authority_issues": authority_issues,
            "target_profiles": targets,
            "claimed_profiles": claimed_profiles,
            "missing_profiles": missing_profiles,
            "known_surface_gaps": known_surface_gaps,
            "classifications": {
                name: sum(
                    record["classification"] == name
                    for record in capability_records
                )
                for name in CLASSIFICATIONS
            },
        }
        total_obligations += len(obligation_records)

    outputs["capability-taxonomy.yaml"] = yaml_bytes(
        {
            "schema": "ff6/capability-taxonomy@2",
            "goal_id": policy.get("goal_id"),
            "classifications": [
                {
                    "id": item,
                    "description": policy.get("classification_descriptions", {}).get(
                        item, ""
                    ),
                }
                for item in CLASSIFICATIONS
            ],
        }
    )
    assessment = "COMPILED"
    if authority_blocked:
        assessment = "COMPILED_AUTHORITY_BLOCKED"
    if any(
        summary["missing_profiles"] or summary["known_surface_gaps"]
        for summary in per_format_summary.values()
    ):
        assessment = "NEEDS_PROFILE_OR_SURFACE_REPAIR"
    outputs["capability-coverage.yaml"] = yaml_bytes(
        {
            "schema": "ff6/capability-coverage@2",
            "goal_id": policy.get("goal_id"),
            "assessment_status": assessment,
            "summary": {
                "formats": len(ordered_formats),
                "total_capabilities": len(all_capability_ids),
                "total_obligations": total_obligations,
                "classifications": classification_counts,
                "authority_blocked_formats": sorted(authority_blocked),
                "certifications": 0,
                "promotions": 0,
            },
            "per_format": per_format_summary,
            "invariants": [
                "Compilation is not implementation or certification evidence.",
                "Every emitted obligation uses canonical ProductContract identity.",
                "Every obligation has exactly one capability owner.",
                "Missing authority, profile, or surface coverage remains blocking.",
            ],
        }
    )

    output_digests = {
        path: sha256(data) for path, data in sorted(outputs.items())
    }
    manifest_body = {
        "schema": "ff6/capability-manifest@2",
        "goal_id": policy.get("goal_id"),
        "formats": list(ordered_formats),
        "input_digests": dict(sorted(inputs.items())),
        "output_digests": output_digests,
        "authority_artifacts": sorted(
            authority_artifacts,
            key=lambda item: (item["format_id"], item["source_id"]),
        ),
        "authority_blocked_formats": sorted(authority_blocked),
    }
    aggregate = sha256(canonical_json(manifest_body))
    manifest = {**manifest_body, "aggregate_sha256": aggregate}
    outputs["capability-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    validation_schema = safe_path(root, (schema_paths or default_schemas)[0])
    validate_outputs(validation_schema, outputs)
    return UniverseCompilation(outputs=dict(sorted(outputs.items())), manifest=manifest)


def main(argv: Sequence[str] | None = None) -> int:
    """Load the CLI lazily so the compiler remains a reusable library module."""

    from .capability_universe_command import main as command_main

    return command_main(argv)


# Compatibility exports for the initial compiler API.
from .capability_universe_runtime import check_outputs, write_outputs  # noqa: E402,F401


if __name__ == "__main__":
    raise SystemExit(main())
