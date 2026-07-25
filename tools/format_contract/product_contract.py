"""Production projection and strict compilation of format contracts.

The existing Format Contract remains the canonical authored input.  This
module expands it into complete, stable obligations and refuses to treat
URL-only authorities, unresolved facts, or prose deferrals as production
coverage.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from .contract_validator import validate_contract

REPO_ROOT = Path(__file__).resolve().parents[2]
SAL_ID = re.compile(r"^SAL-([A-Z0-9]+)-([A-Z0-9_-]+)$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
OBLIGATION_FIELDS = (
    ("required_behavior", "positive"),
    ("normative_rules", "positive"),
    ("preservation_rules", "positive"),
    ("validation_rules", "positive"),
    ("security_requirements", "rejection"),
    ("performance_requirements", "positive"),
    ("error_behavior", "rejection"),
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


@dataclass(frozen=True)
class ContractIssue:
    code: str
    severity: str
    message: str
    reference: str = ""


@dataclass(frozen=True)
class CompiledProductContract:
    format_id: str
    profile_id: str
    target_spec_version: str
    source_digest: str
    digest: str
    authorities: tuple[dict[str, Any], ...]
    obligations: tuple[dict[str, Any], ...]
    issues: tuple[ContractIssue, ...]
    source: dict[str, Any]

    @property
    def ready(self) -> bool:
        return not any(issue.severity in {"CRITICAL", "HIGH"} for issue in self.issues)


def _stable_obligation_id(format_id: str, capability_id: str, field: str, text: str) -> str:
    digest = hashlib.sha256(
        _canonical([format_id, capability_id, field, text])
    ).hexdigest()[:16].upper()
    return f"SAL-{format_id.upper()}-OBL-{digest}"


def _iter_lines(capability: dict[str, Any]) -> Iterable[tuple[str, str, str]]:
    for field, kind in OBLIGATION_FIELDS:
        for value in capability.get(field, []) or []:
            text = str(value).strip()
            if text:
                yield field, kind, text


def compile_product_contract(
    contract: dict[str, Any],
    *,
    profile_id: str = "production",
    run_legacy_validator: bool = True,
    authority_root: Path | None = None,
) -> CompiledProductContract:
    meta = contract.get("contract_metadata", {})
    format_id = str(meta.get("format_id", "")).lower()
    target_spec_version = str(meta.get("target_spec_version", ""))
    source_digest = hashlib.sha256(_canonical(contract)).hexdigest()
    issues: list[ContractIssue] = []

    if run_legacy_validator:
        report = validate_contract(contract)
        if report["verdict"] != "PASS":
            for check in report["checks"]:
                if check["result"] == "FAIL":
                    issues.append(
                        ContractIssue(
                            "LEGACY_CONTRACT_INVALID",
                            "HIGH",
                            f"{check['check']} failed: {check['items'][:3]}",
                        )
                    )

    authorities: list[dict[str, Any]] = []
    for source in contract.get("authoritative_sources", []) or []:
        digest = source.get("content_hash")
        authority_class = source.get("authority_class")
        acquired_label = (
            source.get("acquisition_status") == "ACQUIRED"
            and isinstance(digest, str)
            and SHA256.fullmatch(digest) is not None
        )
        local_path = source.get("local_path")
        artifact_sha256: str | None = None
        artifact_verified = False
        if authority_class == "AUTHORITATIVE" and authority_root is not None:
            reference = str(source.get("source_id", ""))
            if not local_path:
                issues.append(
                    ContractIssue(
                        "AUTHORITY_ARTIFACT_PATH_MISSING",
                        "CRITICAL",
                        "authoritative source has no repository-local artifact path",
                        reference,
                    )
                )
            else:
                root = authority_root.resolve()
                artifact = (root / str(local_path)).resolve()
                try:
                    artifact.relative_to(root)
                except ValueError:
                    issues.append(
                        ContractIssue(
                            "AUTHORITY_ARTIFACT_PATH_UNSAFE",
                            "CRITICAL",
                            "authoritative source artifact resolves outside the repository",
                            reference,
                        )
                    )
                else:
                    if not artifact.is_file():
                        issues.append(
                            ContractIssue(
                                "AUTHORITY_ARTIFACT_MISSING",
                                "CRITICAL",
                                "authoritative source artifact does not exist",
                                reference,
                            )
                        )
                    else:
                        artifact_sha256 = hashlib.sha256(artifact.read_bytes()).hexdigest()
                        artifact_verified = artifact_sha256 == digest
                        if not artifact_verified:
                            issues.append(
                                ContractIssue(
                                    "AUTHORITY_ARTIFACT_DIGEST_MISMATCH",
                                    "CRITICAL",
                                    "authoritative source artifact bytes do not match content_hash",
                                    reference,
                                )
                            )
        elif authority_class != "AUTHORITATIVE":
            artifact_verified = True
        authority = {
            "source_id": source.get("source_id"),
            "title": source.get("title"),
            "version": source.get("version"),
            "authority_class": authority_class,
            "canonical_url": source.get("canonical_url"),
            "local_path": local_path,
            "content_hash": digest,
            "artifact_sha256": artifact_sha256,
            "artifact_verified": artifact_verified,
            "acquired": acquired_label
            and (authority_root is None or artifact_verified),
        }
        authorities.append(authority)
        if authority_class == "AUTHORITATIVE" and not acquired_label:
            issues.append(
                ContractIssue(
                    "AUTHORITY_NOT_PINNED",
                    "CRITICAL",
                    "authoritative source is not an acquired, SHA-256-pinned artifact",
                    str(source.get("source_id", "")),
                )
            )

    obligations: list[dict[str, Any]] = []
    for capability in contract.get("capabilities", []) or []:
        capability_id = str(capability.get("capability_id", ""))
        level = str(capability.get("level", "MUST"))
        provenance_ids = tuple(
            sorted({str(item) for item in capability.get("provenance", []) or []})
        )
        if level == "MUST" and not provenance_ids:
            issues.append(
                ContractIssue(
                    "MISSING_PROVENANCE_REFERENCE",
                    "CRITICAL",
                    "MUST capability has no authority, fact, research, or policy reference",
                    capability_id,
                )
            )
        capability_fact_ids: set[str] = set()
        for fact_id in provenance_ids:
            match = SAL_ID.match(str(fact_id))
            if not match:
                # Legacy POL/RF identifiers remain aliases during migration,
                # but never become new production fact identities.
                continue
            fact_format = match.group(1).lower()
            if fact_format != format_id:
                issues.append(
                    ContractIssue(
                        "FOREIGN_FORMAT_FACT",
                        "CRITICAL",
                        f"{fact_id} belongs to {fact_format}, not {format_id}",
                        capability_id,
                    )
                )
            if fact_id in capability_fact_ids:
                issues.append(
                    ContractIssue(
                        "DUPLICATE_FACT_REFERENCE",
                        "HIGH",
                        f"duplicate production fact reference {fact_id}",
                        capability_id,
                    )
                )
            capability_fact_ids.add(str(fact_id))

        lines = list(_iter_lines(capability))
        if level == "MUST" and not lines:
            issues.append(
                ContractIssue(
                    "MISSING_MANDATORY_OBLIGATION",
                    "CRITICAL",
                    "MUST capability has no compilable normative obligation",
                    capability_id,
                )
            )
        for field, kind, text in lines:
            obligations.append(
                {
                    "obligation_id": _stable_obligation_id(
                        format_id, capability_id, field, text
                    ),
                    "format_id": format_id,
                    "profile_id": profile_id,
                    "capability_id": capability_id,
                    "level": level,
                    "kind": kind,
                    "source_field": field,
                    "text": text,
                    "provenance_ids": provenance_ids,
                    "fact_ids": tuple(sorted(capability_fact_ids)),
                    "required_tests": tuple(capability.get("required_tests", []) or []),
                    "release_gates": tuple(capability.get("release_gates", []) or []),
                    # Deferral text is audit context only and is deliberately
                    # absent from satisfaction inputs.
                }
            )

    obligations.sort(key=lambda item: item["obligation_id"])
    authorities.sort(key=lambda item: str(item["source_id"]))
    projection = {
        "format_id": format_id,
        "profile_id": profile_id,
        "contract_id": meta.get("contract_id"),
        "family": meta.get("family"),
        "target_spec_version": target_spec_version,
        "input_digests": dict(sorted((meta.get("input_digests") or {}).items())),
        "source_digest": source_digest,
        "authorities": authorities,
        "obligations": obligations,
    }
    return CompiledProductContract(
        format_id=format_id,
        profile_id=profile_id,
        target_spec_version=target_spec_version,
        source_digest=source_digest,
        digest=hashlib.sha256(_canonical(projection)).hexdigest(),
        authorities=tuple(authorities),
        obligations=tuple(obligations),
        issues=tuple(sorted(issues, key=lambda issue: (issue.severity, issue.code, issue.reference))),
        source=contract,
    )


def load_and_compile(path: Path, *, profile_id: str = "production") -> CompiledProductContract:
    if not path.exists():
        missing = {
            "contract_metadata": {"format_id": path.stem},
            "authoritative_sources": [],
            "capabilities": [],
        }
        compiled = compile_product_contract(
            missing, profile_id=profile_id, run_legacy_validator=False
        )
        return CompiledProductContract(
            **{
                **compiled.__dict__,
                "issues": compiled.issues
                + (
                    ContractIssue(
                        "CONTRACT_MISSING",
                        "CRITICAL",
                        f"product contract does not exist: {path.as_posix()}",
                    ),
                ),
            }
        )
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return compile_product_contract(
        document,
        profile_id=profile_id,
        authority_root=REPO_ROOT,
    )
