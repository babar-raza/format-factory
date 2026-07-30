"""Content-addressed adjudication of generated XLIFF Core dispositions.

The authority-candidate compiler produces deterministic *proposals*.  This
module is a deliberately separate trust boundary: it binds an explicit
semantic decision to the exact candidate, authority occurrences, denominator,
and independently executed canonical SAL proof that support the decision.

Generated proposals are never rewritten or treated as proof.  An adjudication
must account for every proposed obligation ID, explain every rejection, and
survive full input-digest replay before it can increment a verified count.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any

import yaml


SCHEMA = "ff6/xliff-core-candidate-adjudications@2"
ARTIFACT_ID = "FF6-XLIFF-CORE-CANDIDATE-ADJUDICATIONS"
_FORMAT_ID = "xliff"
_DECISION_ID = re.compile(r"^XLF-ADJ-[A-Z0-9][A-Z0-9-]*$")
_OBLIGATION_ID = re.compile(r"^SAL-XLIFF-CORE-[A-Z0-9][A-Z0-9-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_DECISION_FIELDS = frozenset(
    {
        "decision_id",
        "candidate_id",
        "accepted_obligation_ids",
        "rejected_obligations",
        "sal_fact_ids",
        "authority_reason",
    }
)
_OCCURRENCE_BINDING_FIELDS = (
    "profile",
    "source_id",
    "source_sha256",
    "member",
    "member_sha256",
    "location",
    "occurrence_sha256",
)


class AdjudicationError(ValueError):
    """Raised when an adjudication is incomplete, stale, or contradictory."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _require_sha256(value: Any, field: str) -> str:
    normalized = str(value)
    if not _SHA256.fullmatch(normalized):
        raise AdjudicationError(f"{field} must be a lowercase SHA-256")
    return normalized


def _require_sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise AdjudicationError(f"{field} must be a sequence")
    return value


def _candidate_index(candidate_census: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if candidate_census.get("format_id") != _FORMAT_ID:
        raise AdjudicationError("candidate census belongs to a foreign format")
    candidates = _require_sequence(
        candidate_census.get("candidates"),
        "candidate census candidates",
    )
    result: dict[str, Mapping[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise AdjudicationError("candidate census contains a non-mapping row")
        candidate_id = str(candidate.get("candidate_id", ""))
        if not candidate_id or candidate_id in result:
            raise AdjudicationError("candidate census has a missing or duplicate ID")
        _require_sha256(
            candidate.get("candidate_content_sha256"),
            f"{candidate_id}.candidate_content_sha256",
        )
        occurrences = _require_sequence(
            candidate.get("occurrences"),
            f"{candidate_id}.occurrences",
        )
        if not occurrences:
            raise AdjudicationError(f"{candidate_id} has no authority occurrence")
        for occurrence in occurrences:
            if not isinstance(occurrence, Mapping):
                raise AdjudicationError(
                    f"{candidate_id} contains a non-mapping occurrence"
                )
            for field in ("source_sha256", "member_sha256", "occurrence_sha256"):
                _require_sha256(
                    occurrence.get(field),
                    f"{candidate_id}.{field}",
                )
        result[candidate_id] = candidate
    if candidate_census.get("candidate_count") != len(result):
        raise AdjudicationError("candidate census count is contradictory")
    return result


def _expected_obligation_ids(denominator: Mapping[str, Any]) -> set[str]:
    if denominator.get("format_id") != _FORMAT_ID:
        raise AdjudicationError("obligation denominator belongs to a foreign format")
    expectations = _require_sequence(
        denominator.get("expectations"),
        "denominator expectations",
    )
    result: set[str] = set()
    for expectation in expectations:
        if not isinstance(expectation, Mapping):
            raise AdjudicationError("denominator contains a non-mapping expectation")
        obligation_id = str(expectation.get("obligation_id", ""))
        if (
            not _OBLIGATION_ID.fullmatch(obligation_id)
            or obligation_id in result
        ):
            raise AdjudicationError(
                "denominator has an invalid, foreign, or duplicate obligation ID"
            )
        result.add(obligation_id)
    if denominator.get("expected_obligation_count") != len(result):
        raise AdjudicationError("denominator expected-obligation count is stale")
    return result


def _sal_proof_index(
    *,
    sal_store: Mapping[str, Any],
    sal_manifest_sha256: str,
    sal_receipt: Mapping[str, Any],
    sal_receipt_sha256: str,
) -> dict[str, dict[str, str]]:
    if (
        sal_store.get("format_id") != _FORMAT_ID
        or sal_receipt.get("format_id") != _FORMAT_ID
    ):
        raise AdjudicationError("canonical SAL inputs belong to a foreign format")
    if sal_receipt.get("result") != "PASS":
        raise AdjudicationError("canonical SAL receipt is not PASS")
    manifest = sal_receipt.get("manifest")
    if (
        not isinstance(manifest, Mapping)
        or manifest.get("sha256") != sal_manifest_sha256
    ):
        raise AdjudicationError("canonical SAL manifest digest is stale")
    receipt_rows = _require_sequence(
        sal_receipt.get("facts"),
        "canonical SAL receipt facts",
    )
    receipt_index: dict[str, Mapping[str, Any]] = {}
    for row in receipt_rows:
        if not isinstance(row, Mapping):
            raise AdjudicationError("canonical SAL receipt has a non-mapping fact")
        fact_id = str(row.get("fact_id", ""))
        if not fact_id or fact_id in receipt_index:
            raise AdjudicationError("canonical SAL receipt fact IDs are not unique")
        receipt_index[fact_id] = row

    facts = _require_sequence(sal_store.get("facts"), "canonical SAL facts")
    proof_index: dict[str, dict[str, str]] = {}
    for fact in facts:
        if not isinstance(fact, Mapping):
            raise AdjudicationError("canonical SAL store has a non-mapping fact")
        fact_id = str(fact.get("fact_id", ""))
        if not fact_id or fact_id in proof_index:
            raise AdjudicationError("canonical SAL fact IDs are missing or duplicate")
        if fact.get("verification_status") != "verified":
            continue
        provenance = fact.get("provenance")
        verification = (
            provenance.get("verification")
            if isinstance(provenance, Mapping)
            else None
        )
        if not isinstance(verification, Mapping):
            continue
        receipt_row = receipt_index.get(fact_id)
        if receipt_row is None or receipt_row.get("result") != "PASS":
            continue
        claim = str(fact.get("claim", ""))
        claim_sha256 = hashlib.sha256(claim.encode("utf-8")).hexdigest()
        if receipt_row.get("claim_sha256") != claim_sha256:
            continue
        proof_sha256 = str(receipt_row.get("proof_sha256", ""))
        if (
            verification.get("method") != "declarative_authority_v1"
            or verification.get("manifest_sha256") != sal_manifest_sha256
            or verification.get("receipt_sha256") != sal_receipt_sha256
            or verification.get("fact_proof_sha256") != proof_sha256
            or not _SHA256.fullmatch(proof_sha256)
        ):
            continue
        proof_index[fact_id] = {
            "claim_sha256": claim_sha256,
            "fact_proof_sha256": proof_sha256,
        }
    return proof_index


def _proposal_ids(candidate: Mapping[str, Any]) -> list[str]:
    disposition = candidate.get("disposition")
    if not isinstance(disposition, Mapping):
        raise AdjudicationError(
            f"{candidate.get('candidate_id')} lacks a generated proposal"
        )
    if disposition.get("validation_status") != (
        "SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED"
    ):
        raise AdjudicationError(
            f"{candidate.get('candidate_id')} proposal has invalid trust status"
        )
    if disposition.get("kind") != "MAP_EXPECTED_OBLIGATION":
        raise AdjudicationError(
            "this adjudication schema currently requires a mapped proposal"
        )
    raw_ids = _require_sequence(
        disposition.get("obligation_ids"),
        f"{candidate.get('candidate_id')}.proposal.obligation_ids",
    )
    ids = [str(value) for value in raw_ids]
    if not ids or len(ids) != len(set(ids)):
        raise AdjudicationError("generated proposal IDs are empty or duplicate")
    return ids


def _normalize_decision(
    raw: Mapping[str, Any],
    *,
    candidates: Mapping[str, Mapping[str, Any]],
    expected_ids: set[str],
    sal_proofs: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    missing = sorted(_REQUIRED_DECISION_FIELDS - set(raw))
    if missing:
        raise AdjudicationError(f"adjudication decision lacks fields: {missing}")
    decision_id = str(raw["decision_id"])
    if not _DECISION_ID.fullmatch(decision_id):
        raise AdjudicationError(f"invalid decision_id: {decision_id}")
    candidate_id = str(raw["candidate_id"])
    candidate = candidates.get(candidate_id)
    if candidate is None:
        raise AdjudicationError(f"{decision_id} references an unknown candidate")
    authority_reason = " ".join(str(raw["authority_reason"]).split())
    if len(authority_reason) < 40:
        raise AdjudicationError(f"{decision_id} lacks a reasoned authority decision")

    accepted_raw = _require_sequence(
        raw["accepted_obligation_ids"],
        f"{decision_id}.accepted_obligation_ids",
    )
    accepted = [str(value) for value in accepted_raw]
    if not accepted or len(accepted) != len(set(accepted)):
        raise AdjudicationError(
            f"{decision_id} accepted obligation IDs are empty or duplicate"
        )
    if any(not _OBLIGATION_ID.fullmatch(value) for value in accepted):
        raise AdjudicationError(
            f"{decision_id} contains a foreign-format obligation ID"
        )
    unknown = sorted(set(accepted) - expected_ids)
    if unknown:
        raise AdjudicationError(
            f"{decision_id} references unknown obligation IDs: {unknown}"
        )

    rejected_raw = _require_sequence(
        raw["rejected_obligations"],
        f"{decision_id}.rejected_obligations",
    )
    rejected: list[dict[str, str]] = []
    rejected_ids: list[str] = []
    for item in rejected_raw:
        if not isinstance(item, Mapping):
            raise AdjudicationError(
                f"{decision_id} has a non-mapping rejection"
            )
        obligation_id = str(item.get("obligation_id", ""))
        reason_code = str(item.get("reason_code", "")).strip()
        reason = " ".join(str(item.get("reason", "")).split())
        if (
            not _OBLIGATION_ID.fullmatch(obligation_id)
            or not reason_code
            or len(reason) < 30
        ):
            raise AdjudicationError(
                f"{decision_id} has an invalid or unreasoned rejection"
            )
        rejected_ids.append(obligation_id)
        rejected.append(
            {
                "obligation_id": obligation_id,
                "reason_code": reason_code,
                "reason": reason,
            }
        )
    if len(rejected_ids) != len(set(rejected_ids)):
        raise AdjudicationError(f"{decision_id} rejects an obligation twice")
    if set(accepted) & set(rejected_ids):
        raise AdjudicationError(
            f"{decision_id} both accepts and rejects an obligation"
        )
    proposal_ids = set(_proposal_ids(candidate))
    rejected_id_set = set(rejected_ids)
    accepted_id_set = set(accepted)
    foreign_rejections = sorted(rejected_id_set - proposal_ids)
    if foreign_rejections:
        raise AdjudicationError(
            f"{decision_id} rejects obligations absent from the proposal: "
            f"{foreign_rejections}"
        )
    undispositioned = sorted(
        proposal_ids - accepted_id_set - rejected_id_set
    )
    if undispositioned:
        raise AdjudicationError(
            f"{decision_id} does not disposition every proposed obligation: "
            f"{undispositioned}"
        )
    unproposed_accepted = sorted(accepted_id_set - proposal_ids)
    unproposed_rejected_raw = _require_sequence(
        raw.get("unproposed_rejected_obligations", []),
        f"{decision_id}.unproposed_rejected_obligations",
    )
    unproposed_rejected: list[dict[str, str]] = []
    unproposed_rejected_ids: list[str] = []
    for item in unproposed_rejected_raw:
        if not isinstance(item, Mapping):
            raise AdjudicationError(
                f"{decision_id} has a non-mapping unproposed rejection"
            )
        obligation_id = str(item.get("obligation_id", ""))
        reason_code = str(item.get("reason_code", "")).strip()
        reason = " ".join(str(item.get("reason", "")).split())
        if (
            not _OBLIGATION_ID.fullmatch(obligation_id)
            or not reason_code
            or len(reason) < 30
        ):
            raise AdjudicationError(
                f"{decision_id} has an invalid or unreasoned "
                "unproposed rejection"
            )
        unproposed_rejected_ids.append(obligation_id)
        unproposed_rejected.append(
            {
                "obligation_id": obligation_id,
                "reason_code": reason_code,
                "reason": reason,
            }
        )
    unproposed_rejected_id_set = set(unproposed_rejected_ids)
    if len(unproposed_rejected_ids) != len(unproposed_rejected_id_set):
        raise AdjudicationError(
            f"{decision_id} rejects an unproposed obligation twice"
        )
    unknown_unproposed_rejections = sorted(
        unproposed_rejected_id_set - expected_ids
    )
    if unknown_unproposed_rejections:
        raise AdjudicationError(
            f"{decision_id} rejects unknown unproposed obligations: "
            f"{unknown_unproposed_rejections}"
        )
    invalid_unproposed_rejections = sorted(
        unproposed_rejected_id_set
        & (proposal_ids | accepted_id_set | rejected_id_set)
    )
    if invalid_unproposed_rejections:
        raise AdjudicationError(
            f"{decision_id} unproposed rejections overlap proposed or "
            f"accepted obligations: {invalid_unproposed_rejections}"
        )

    sal_fact_ids_raw = _require_sequence(
        raw["sal_fact_ids"],
        f"{decision_id}.sal_fact_ids",
    )
    sal_fact_ids = [str(value) for value in sal_fact_ids_raw]
    if not sal_fact_ids or len(sal_fact_ids) != len(set(sal_fact_ids)):
        raise AdjudicationError(
            f"{decision_id} SAL fact IDs are empty or duplicate"
        )
    missing_proofs = sorted(set(sal_fact_ids) - set(sal_proofs))
    if missing_proofs:
        raise AdjudicationError(
            f"{decision_id} lacks current canonical SAL proof: {missing_proofs}"
        )

    occurrences = _require_sequence(
        candidate.get("occurrences"),
        f"{candidate_id}.occurrences",
    )
    authority_bindings = [
        {field: str(occurrence[field]) for field in _OCCURRENCE_BINDING_FIELDS}
        for occurrence in occurrences
        if isinstance(occurrence, Mapping)
    ]
    if len(authority_bindings) != len(occurrences):
        raise AdjudicationError(f"{candidate_id} has a malformed occurrence")
    normalized: dict[str, Any] = {
        "decision_id": decision_id,
        "candidate_id": candidate_id,
        "candidate_content_sha256": str(
            candidate["candidate_content_sha256"]
        ),
        "proposal_sha256": _digest(candidate["disposition"]),
        "proposed_obligation_ids": sorted(proposal_ids),
        "authority_occurrences": authority_bindings,
        "accepted_obligation_ids": sorted(accepted),
        "unproposed_accepted_obligation_ids": unproposed_accepted,
        "rejected_obligations": sorted(
            rejected,
            key=lambda value: value["obligation_id"],
        ),
        "sal_proofs": [
            {
                "fact_id": fact_id,
                **dict(sal_proofs[fact_id]),
            }
            for fact_id in sorted(sal_fact_ids)
        ],
        "authority_reason": authority_reason,
        "outcome": "VERIFIED_AUTHORITY_DISPOSITION",
    }
    if unproposed_rejected:
        normalized["unproposed_rejected_obligations"] = sorted(
            unproposed_rejected,
            key=lambda value: value["obligation_id"],
        )
    normalized["decision_sha256"] = _digest(normalized)
    return normalized


def compile_adjudication_artifact(
    *,
    candidate_census: Mapping[str, Any],
    candidate_census_sha256: str,
    denominator: Mapping[str, Any],
    denominator_sha256: str,
    sal_store: Mapping[str, Any],
    sal_store_sha256: str,
    sal_manifest_sha256: str,
    sal_receipt: Mapping[str, Any],
    sal_receipt_sha256: str,
    decisions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compile and validate one deterministic adjudication artifact."""

    input_digests = {
        "candidate_census_sha256": _require_sha256(
            candidate_census_sha256,
            "candidate_census_sha256",
        ),
        "denominator_sha256": _require_sha256(
            denominator_sha256,
            "denominator_sha256",
        ),
        "sal_store_sha256": _require_sha256(
            sal_store_sha256,
            "sal_store_sha256",
        ),
        "sal_manifest_sha256": _require_sha256(
            sal_manifest_sha256,
            "sal_manifest_sha256",
        ),
        "sal_receipt_sha256": _require_sha256(
            sal_receipt_sha256,
            "sal_receipt_sha256",
        ),
    }
    candidates = _candidate_index(candidate_census)
    expected_ids = _expected_obligation_ids(denominator)
    sal_proofs = _sal_proof_index(
        sal_store=sal_store,
        sal_manifest_sha256=input_digests["sal_manifest_sha256"],
        sal_receipt=sal_receipt,
        sal_receipt_sha256=input_digests["sal_receipt_sha256"],
    )
    normalized = [
        _normalize_decision(
            decision,
            candidates=candidates,
            expected_ids=expected_ids,
            sal_proofs=sal_proofs,
        )
        for decision in decisions
    ]
    decision_ids = [row["decision_id"] for row in normalized]
    candidate_ids = [row["candidate_id"] for row in normalized]
    if len(decision_ids) != len(set(decision_ids)):
        raise AdjudicationError("duplicate adjudication decision ID")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise AdjudicationError("a candidate has multiple adjudications")
    normalized.sort(key=lambda row: row["candidate_id"])
    accepted_obligation_candidate_ids: dict[str, list[str]] = {}
    for row in normalized:
        for obligation_id in row["accepted_obligation_ids"]:
            accepted_obligation_candidate_ids.setdefault(
                obligation_id,
                [],
            ).append(row["candidate_id"])
    accepted_obligation_candidate_ids = {
        obligation_id: sorted(candidate_ids_for_obligation)
        for obligation_id, candidate_ids_for_obligation in sorted(
            accepted_obligation_candidate_ids.items()
        )
    }
    artifact: dict[str, Any] = {
        "schema": SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "artifact_type": "candidate_disposition_adjudications",
        "visibility": "generated",
        "publish_allowed": False,
        "generated_by": "codex",
        "format_id": _FORMAT_ID,
        **input_digests,
        "adjudicator_sha256": module_sha256(),
        "candidate_census_artifact_id": str(
            candidate_census.get("artifact_id", "")
        ),
        "denominator_artifact_id": str(denominator.get("artifact_id", "")),
        "candidate_count": len(candidates),
        "decision_count": len(normalized),
        "verified_disposition_count": len(normalized),
        "unverified_disposition_count": len(candidates) - len(normalized),
        "disposition_verification_complete": len(normalized) == len(candidates),
        "verified_candidate_ids": sorted(candidate_ids),
        "accepted_obligation_candidate_ids": (
            accepted_obligation_candidate_ids
        ),
        "decisions": normalized,
        "status": "PARTIAL_VERIFIED" if normalized else "NO_VERIFIED_DECISIONS",
        "truth_boundary": (
            "Only listed content-addressed decisions are verified. Generated "
            "candidate proposals remain non-promoting, and this partial "
            "artifact does not complete XLF-04."
        ),
    }
    artifact["input_closure_sha256"] = _digest(input_digests)
    artifact["decision_set_sha256"] = _digest(normalized)
    return artifact


def validate_adjudication_artifact(
    artifact: Mapping[str, Any],
    *,
    candidate_census: Mapping[str, Any],
    candidate_census_sha256: str,
    denominator: Mapping[str, Any],
    denominator_sha256: str,
    sal_store: Mapping[str, Any],
    sal_store_sha256: str,
    sal_manifest_sha256: str,
    sal_receipt: Mapping[str, Any],
    sal_receipt_sha256: str,
) -> None:
    """Replay all bindings and reject any stale or edited adjudication."""

    decisions = _require_sequence(
        artifact.get("decisions"),
        "adjudication decisions",
    )
    raw_decisions: list[dict[str, Any]] = []
    for decision in decisions:
        if not isinstance(decision, Mapping):
            raise AdjudicationError("adjudication contains a non-mapping decision")
        raw_decisions.append(
            {
                "decision_id": decision.get("decision_id"),
                "candidate_id": decision.get("candidate_id"),
                "accepted_obligation_ids": decision.get(
                    "accepted_obligation_ids"
                ),
                "rejected_obligations": decision.get("rejected_obligations"),
                "sal_fact_ids": [
                    proof.get("fact_id")
                    for proof in _require_sequence(
                        decision.get("sal_proofs"),
                        "decision SAL proofs",
                    )
                    if isinstance(proof, Mapping)
                ],
                "authority_reason": decision.get("authority_reason"),
                **(
                    {
                        "unproposed_rejected_obligations": decision[
                            "unproposed_rejected_obligations"
                        ]
                    }
                    if "unproposed_rejected_obligations" in decision
                    else {}
                ),
            }
        )
    expected = compile_adjudication_artifact(
        candidate_census=candidate_census,
        candidate_census_sha256=candidate_census_sha256,
        denominator=denominator,
        denominator_sha256=denominator_sha256,
        sal_store=sal_store,
        sal_store_sha256=sal_store_sha256,
        sal_manifest_sha256=sal_manifest_sha256,
        sal_receipt=sal_receipt,
        sal_receipt_sha256=sal_receipt_sha256,
        decisions=raw_decisions,
    )
    if dict(artifact) != expected:
        raise AdjudicationError(
            "adjudication artifact contradicts its content-addressed replay"
        )


def apply_adjudication_projection(
    candidate_census: Mapping[str, Any],
    adjudications: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a census projection whose verified count uses decisions only."""

    if (
        adjudications.get("schema") != SCHEMA
        or adjudications.get("artifact_id") != ARTIFACT_ID
        or adjudications.get("format_id") != _FORMAT_ID
    ):
        raise AdjudicationError("invalid adjudication artifact identity")
    projected = deepcopy(dict(candidate_census))
    candidates = _candidate_index(projected)
    decisions = _require_sequence(
        adjudications.get("decisions"),
        "adjudication decisions",
    )
    verified: set[str] = set()
    by_candidate: dict[str, Mapping[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, Mapping):
            raise AdjudicationError("adjudication contains a non-mapping decision")
        candidate_id = str(decision.get("candidate_id", ""))
        if candidate_id not in candidates or candidate_id in verified:
            raise AdjudicationError(
                "adjudication references an unknown or duplicate candidate"
            )
        if (
            decision.get("candidate_content_sha256")
            != candidates[candidate_id].get("candidate_content_sha256")
        ):
            raise AdjudicationError(
                f"{candidate_id} adjudication candidate digest is stale"
            )
        verified.add(candidate_id)
        by_candidate[candidate_id] = decision
    for candidate_id, decision in by_candidate.items():
        candidate = candidates[candidate_id]
        if not isinstance(candidate, dict):
            raise AdjudicationError(
                f"{candidate_id} candidate row is not mutable"
            )
        candidate["adjudicated_disposition"] = {
            "decision_id": decision["decision_id"],
            "decision_sha256": decision["decision_sha256"],
            "accepted_obligation_ids": decision["accepted_obligation_ids"],
            "unproposed_accepted_obligation_ids": decision[
                "unproposed_accepted_obligation_ids"
            ],
            "rejected_obligations": decision["rejected_obligations"],
            "validation_status": "CANONICAL_SAL_VERIFIED",
        }
    projected["adjudication_input"] = {
        "artifact_id": ARTIFACT_ID,
        "decision_set_sha256": adjudications.get("decision_set_sha256"),
        "decision_count": len(verified),
    }
    projected["verified_disposition_count"] = len(verified)
    projected["unverified_disposition_count"] = (
        int(projected["candidate_count"]) - len(verified)
    )
    projected["disposition_verification_complete"] = (
        projected["unverified_disposition_count"] == 0
    )
    return projected


def module_sha256() -> str:
    """Return the current adjudicator implementation digest."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def artifact_bytes(artifact: Mapping[str, Any]) -> bytes:
    """Return stable LF-normalized YAML bytes for an adjudication artifact."""

    text = yaml.safe_dump(
        dict(artifact),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    )
    return text.replace("\r\n", "\n").encode("utf-8")


def _load_mapping(path: Path, label: str) -> tuple[bytes, dict[str, Any]]:
    try:
        data = path.read_bytes()
        value = yaml.safe_load(data)
    except (OSError, yaml.YAMLError) as exc:
        raise AdjudicationError(f"{label} is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise AdjudicationError(f"{label} must be a mapping")
    return data, value


def validated_obligation_ids_from_paths(
    *,
    adjudications_path: Path,
    candidate_census_path: Path,
    denominator_path: Path,
    sal_store_path: Path,
    sal_manifest_path: Path,
    sal_receipt_path: Path,
) -> tuple[set[str], dict[str, Any]]:
    """Validate an entire proof closure and return its accepted obligations."""

    adjudication_bytes, adjudications = _load_mapping(
        adjudications_path,
        "adjudication artifact",
    )
    census_bytes, census = _load_mapping(
        candidate_census_path,
        "candidate census",
    )
    denominator_bytes, denominator = _load_mapping(
        denominator_path,
        "obligation denominator",
    )
    store_bytes, store = _load_mapping(
        sal_store_path,
        "canonical SAL store",
    )
    manifest_bytes, manifest = _load_mapping(
        sal_manifest_path,
        "canonical SAL manifest",
    )
    receipt_bytes, receipt = _load_mapping(
        sal_receipt_path,
        "canonical SAL receipt",
    )
    if manifest.get("format_id") != _FORMAT_ID:
        raise AdjudicationError("canonical SAL manifest format is not xliff")
    validate_adjudication_artifact(
        adjudications,
        candidate_census=census,
        candidate_census_sha256=hashlib.sha256(census_bytes).hexdigest(),
        denominator=denominator,
        denominator_sha256=hashlib.sha256(denominator_bytes).hexdigest(),
        sal_store=store,
        sal_store_sha256=hashlib.sha256(store_bytes).hexdigest(),
        sal_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        sal_receipt=receipt,
        sal_receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
    )
    obligation_ids = {
        str(obligation_id)
        for decision in _require_sequence(
            adjudications.get("decisions"),
            "adjudication decisions",
        )
        if isinstance(decision, Mapping)
        for obligation_id in _require_sequence(
            decision.get("accepted_obligation_ids"),
            "accepted obligation IDs",
        )
    }
    evidence = {
        "artifact_id": ARTIFACT_ID,
        "artifact_sha256": hashlib.sha256(adjudication_bytes).hexdigest(),
        "input_closure_sha256": adjudications["input_closure_sha256"],
        "decision_set_sha256": adjudications["decision_set_sha256"],
        "decision_count": adjudications["decision_count"],
        "verified_disposition_count": adjudications[
            "verified_disposition_count"
        ],
        "unverified_disposition_count": adjudications[
            "unverified_disposition_count"
        ],
        "verified_candidate_ids": adjudications["verified_candidate_ids"],
        "accepted_obligation_candidate_ids": adjudications[
            "accepted_obligation_candidate_ids"
        ],
    }
    return obligation_ids, evidence


def _write_artifact(output: Path, artifact: Mapping[str, Any]) -> str:
    data = artifact_bytes(artifact)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return hashlib.sha256(data).hexdigest()


def _check_artifact(output: Path, artifact: Mapping[str, Any]) -> str:
    expected = artifact_bytes(artifact)
    observed = output.read_bytes() if output.is_file() else None
    if observed != expected:
        observed_sha256 = (
            hashlib.sha256(observed).hexdigest()
            if observed is not None
            else "MISSING"
        )
        raise AdjudicationError(
            "adjudication output drift: expected "
            f"{hashlib.sha256(expected).hexdigest()}, observed "
            f"{observed_sha256}"
        )
    return hashlib.sha256(expected).hexdigest()


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compile content-addressed XLIFF Core candidate adjudications "
            "against current canonical SAL proof."
        )
    )
    parser.add_argument("--candidate-census", type=Path, required=True)
    parser.add_argument("--denominator", type=Path, required=True)
    parser.add_argument("--sal-store", type=Path, required=True)
    parser.add_argument("--sal-manifest", type=Path, required=True)
    parser.add_argument("--sal-receipt", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run deterministic adjudication compilation or drift checking."""

    args = _argument_parser().parse_args(argv)
    census_bytes, census = _load_mapping(
        args.candidate_census,
        "candidate census",
    )
    denominator_bytes, denominator = _load_mapping(
        args.denominator,
        "obligation denominator",
    )
    store_bytes, store = _load_mapping(args.sal_store, "canonical SAL store")
    manifest_bytes, manifest = _load_mapping(
        args.sal_manifest,
        "canonical SAL manifest",
    )
    receipt_bytes, receipt = _load_mapping(
        args.sal_receipt,
        "canonical SAL receipt",
    )
    _decision_bytes, decision_input = _load_mapping(
        args.decisions,
        "adjudication decisions",
    )
    if (
        decision_input.get("schema")
        != "ff6/xliff-core-candidate-adjudication-decisions@1"
        or decision_input.get("format_id") != _FORMAT_ID
    ):
        raise AdjudicationError("invalid adjudication decision-set identity")
    raw_decisions = _require_sequence(
        decision_input.get("decisions"),
        "adjudication decision-set decisions",
    )
    if not all(isinstance(value, Mapping) for value in raw_decisions):
        raise AdjudicationError("decision set contains a non-mapping decision")
    artifact = compile_adjudication_artifact(
        candidate_census=census,
        candidate_census_sha256=hashlib.sha256(census_bytes).hexdigest(),
        denominator=denominator,
        denominator_sha256=hashlib.sha256(denominator_bytes).hexdigest(),
        sal_store=store,
        sal_store_sha256=hashlib.sha256(store_bytes).hexdigest(),
        sal_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        sal_receipt=receipt,
        sal_receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
        decisions=list(raw_decisions),
    )
    if manifest.get("format_id") != _FORMAT_ID:
        raise AdjudicationError("canonical SAL manifest format is not xliff")
    digest = (
        _check_artifact(args.output, artifact)
        if args.check
        else _write_artifact(args.output, artifact)
    )
    print(
        json.dumps(
            {
                "check": args.check,
                "decision_count": artifact["decision_count"],
                "digest": digest,
                "output": args.output.as_posix(),
                "schema": SCHEMA,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
