"""Content-addressed proof validation for promoting SAL facts.

The human-readable ``verification_status`` label is never sufficient by
itself.  A promoting fact must point at a receipt whose complete live input
closure still matches: claim, manifest, verifier implementation, and pinned
authority artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a proof value without timestamps, paths, or ordering noise."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_digest(value: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def claim_digest(claim: str) -> str:
    return sha256_bytes(claim.encode("utf-8"))


def resolve_repo_path(repo_root: Path, relative_path: str) -> Path:
    """Resolve a proof input while rejecting absolute and escaping paths."""

    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"proof path must be repository-relative: {relative_path}")
    root = repo_root.resolve()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"proof path escapes repository: {relative_path}")
    return resolved


def fact_proof_closure(
    fact: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """Return deterministic live digests for every declared proof input."""

    verification = (fact.get("provenance") or {}).get("verification")
    closure: dict[str, Any] = {
        "fact_id": str(fact.get("fact_id", "")),
        "claim_sha256": claim_digest(str(fact.get("claim", ""))),
        "verification_status": str(fact.get("verification_status", "")),
        "inputs": [],
    }
    if not isinstance(verification, dict):
        closure["verification_record"] = "MISSING"
        return closure

    declared_paths = [
        str(verification.get("manifest_path", "")),
        str(verification.get("receipt_path", "")),
    ]
    receipt: dict[str, Any] = {}
    receipt_path_value = str(verification.get("receipt_path", ""))
    if receipt_path_value:
        try:
            receipt_path = resolve_repo_path(repo_root, receipt_path_value)
            if receipt_path.is_file():
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            receipt = {}
    declared_paths.extend(
        str(item.get("path", ""))
        for item in receipt.get("tool_closure", [])
        if item.get("path")
    )
    declared_paths.extend(
        str(item.get("path", ""))
        for item in receipt.get("sources", [])
        if item.get("path")
    )
    for relative_path in sorted(set(filter(None, declared_paths))):
        try:
            path = resolve_repo_path(repo_root, relative_path)
            digest = sha256_file(path) if path.is_file() else "MISSING"
        except (OSError, ValueError):
            digest = "INVALID"
        closure["inputs"].append({"path": relative_path, "sha256": digest})
    return closure


def validate_fact_promotion(
    fact: dict[str, Any],
    repo_root: Path,
) -> tuple[bool, str]:
    """Validate the live content closure of one ``verified`` SAL fact."""

    if fact.get("verification_status") != "verified":
        return False, "verification status is not verified"
    verification = (fact.get("provenance") or {}).get("verification")
    if not isinstance(verification, dict):
        return False, "verified fact has no content-addressed verification record"

    required = {
        "method",
        "manifest_path",
        "manifest_sha256",
        "receipt_path",
        "receipt_sha256",
        "fact_proof_sha256",
    }
    missing = sorted(required - set(verification))
    if missing:
        return False, "verification record is missing: " + ", ".join(missing)
    if verification["method"] != "declarative_authority_v1":
        return False, f"unsupported verification method: {verification['method']}"

    try:
        receipt_path = resolve_repo_path(repo_root, str(verification["receipt_path"]))
        manifest_path = resolve_repo_path(repo_root, str(verification["manifest_path"]))
    except ValueError as error:
        return False, str(error)
    if not receipt_path.is_file() or not manifest_path.is_file():
        return False, "verification receipt or manifest is missing"
    if sha256_file(receipt_path) != verification["receipt_sha256"]:
        return False, "verification receipt digest changed"
    if sha256_file(manifest_path) != verification["manifest_sha256"]:
        return False, "verification manifest digest changed"

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, f"verification receipt is unreadable: {error}"
    if receipt.get("result") != "PASS":
        return False, "verification receipt is not a passing receipt"
    if receipt.get("manifest", {}).get("sha256") != verification["manifest_sha256"]:
        return False, "receipt does not bind the live manifest"

    for tool in receipt.get("tool_closure", []):
        try:
            path = resolve_repo_path(repo_root, str(tool["path"]))
        except (KeyError, ValueError) as error:
            return False, f"invalid verifier closure entry: {error}"
        if not path.is_file() or sha256_file(path) != tool.get("sha256"):
            return False, f"verifier closure changed: {tool.get('path')}"

    for source in receipt.get("sources", []):
        try:
            path = resolve_repo_path(repo_root, str(source["path"]))
        except (KeyError, ValueError) as error:
            return False, f"invalid authority source entry: {error}"
        if not path.is_file() or sha256_file(path) != source.get("sha256"):
            return False, f"authority artifact changed: {source.get('source_id')}"

    fact_id = str(fact.get("fact_id", ""))
    fact_record = next(
        (
            item
            for item in receipt.get("facts", [])
            if item.get("fact_id") == fact_id
        ),
        None,
    )
    if not isinstance(fact_record, dict) or fact_record.get("result") != "PASS":
        return False, "receipt has no passing record for the fact"
    if fact_record.get("claim_sha256") != claim_digest(str(fact.get("claim", ""))):
        return False, "live fact claim differs from verified claim"
    proof_payload = {
        key: value for key, value in fact_record.items() if key != "proof_sha256"
    }
    expected_proof = record_digest(proof_payload)
    if fact_record.get("proof_sha256") != expected_proof:
        return False, "fact proof record digest is invalid"
    if verification["fact_proof_sha256"] != expected_proof:
        return False, "fact does not bind its receipt proof record"
    return True, "content-addressed authority proof is live"
