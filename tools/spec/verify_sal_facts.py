"""Verify SAL facts with exact, declarative assertions over pinned authorities.

This tool intentionally does not infer truth from keyword overlap.  A fact is
promoted only when every assertion in its reviewed evidence manifest passes
against exact content-addressed authority bytes.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft4Validator

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.spec.sal_proof import (
    canonical_json_bytes,
    claim_digest,
    record_digest,
    sha256_bytes,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATHS = (
    "tools/spec/verify_sal_facts.py",
    "tools/spec/sal_proof.py",
)
SUPPORTED_ASSERTIONS = frozenset(
    {
        "json_pointer_equals",
        "json_pointer_contains",
        "json_pointer_has_keys",
        "json_schema_accepts",
        "json_schema_rejects",
        "text_contains",
    }
)


class VerificationError(RuntimeError):
    """Raised for malformed or unverifiable evidence definitions."""


def _json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise VerificationError(f"JSON pointer must start with '/': {pointer}")
    current = document
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as error:
                raise VerificationError(f"JSON pointer not found: {pointer}") from error
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise VerificationError(f"JSON pointer not found: {pointer}")
    return current


def _normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _read_member(artifact: Path, member: str | None) -> bytes:
    if not member:
        return artifact.read_bytes()
    if tarfile.is_tarfile(artifact):
        with tarfile.open(artifact, mode="r:*") as archive:
            try:
                extracted = archive.extractfile(member)
            except KeyError as error:
                raise VerificationError(f"tar member is missing: {member}") from error
            if extracted is None:
                raise VerificationError(f"tar member is not a file: {member}")
            return extracted.read()
    if zipfile.is_zipfile(artifact):
        with zipfile.ZipFile(artifact) as archive:
            try:
                return archive.read(member)
            except KeyError as error:
                raise VerificationError(f"ZIP member is missing: {member}") from error
    raise VerificationError(f"member requested from unsupported artifact: {artifact}")


def _assertion_result(
    assertion: dict[str, Any],
    content: bytes,
) -> dict[str, Any]:
    kind = str(assertion.get("kind", ""))
    assertion_id = str(assertion.get("assertion_id", ""))
    if not assertion_id:
        raise VerificationError("every assertion requires assertion_id")
    if kind not in SUPPORTED_ASSERTIONS:
        raise VerificationError(f"unsupported assertion kind: {kind}")

    result: dict[str, Any] = {
        "assertion_id": assertion_id,
        "kind": kind,
        "result": "FAIL",
    }
    if kind.startswith("json_"):
        try:
            document = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise VerificationError(f"assertion target is not JSON: {error}") from error
        pointer = str(assertion.get("pointer", ""))
        if kind.startswith("json_schema_"):
            schema = (
                _json_pointer(document, pointer)
                if pointer
                else document
            )
            if pointer and isinstance(document, dict) and "definitions" in document:
                schema = {
                    **schema,
                    "definitions": document["definitions"],
                }
            instance = assertion.get("instance")
            errors = sorted(
                Draft4Validator(schema).iter_errors(instance),
                key=lambda error: list(error.path),
            )
            passed = not errors if kind == "json_schema_accepts" else bool(errors)
            result.update(
                {
                    "pointer": pointer,
                    "instance_sha256": sha256_bytes(
                        canonical_json_bytes(instance)
                    ),
                    "validation_error_count": len(errors),
                    "result": "PASS" if passed else "FAIL",
                }
            )
            return result

        observed = _json_pointer(document, pointer)
        expected = assertion.get("expected")
        if kind == "json_pointer_equals":
            passed = observed == expected
        elif kind == "json_pointer_contains":
            passed = isinstance(observed, list) and expected in observed
        else:
            passed = (
                set(str(item) for item in expected) <= set(observed)
                if isinstance(observed, dict) and isinstance(expected, list)
                else False
            )
        result.update(
            {
                "pointer": pointer,
                "expected_sha256": sha256_bytes(canonical_json_bytes(expected)),
                "observed_sha256": sha256_bytes(canonical_json_bytes(observed)),
                "result": "PASS" if passed else "FAIL",
            }
        )
        return result

    try:
        text = content.decode(str(assertion.get("encoding", "utf-8")))
    except (LookupError, UnicodeDecodeError) as error:
        raise VerificationError(f"text assertion decode failed: {error}") from error
    expected_text = str(assertion.get("expected", ""))
    if len(_normalized_text(expected_text)) < 24:
        raise VerificationError(
            f"text assertion {assertion_id} is too short to be discriminating"
        )
    normalized_expected = _normalized_text(expected_text)
    normalized_observed = _normalized_text(text)
    passed = normalized_expected in normalized_observed
    result.update(
        {
            "expected_sha256": sha256_bytes(normalized_expected.encode("utf-8")),
            "observed_document_sha256": sha256_bytes(content),
            "result": "PASS" if passed else "FAIL",
        }
    )
    return result


def _research_sources(repo_root: Path, format_id: str) -> dict[str, dict[str, Any]]:
    path = repo_root / "shared" / "format-contracts" / "research" / f"{format_id}.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        str(record["source_id"]): record
        for record in document.get("source_records", [])
    }


def verify_format(repo_root: Path, format_id: str) -> dict[str, Any]:
    manifest_path = (
        repo_root / "shared" / "sal-facts" / "evidence" / f"{format_id}.yaml"
    )
    store_path = repo_root / "shared" / "sal-facts" / f"{format_id}.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    store = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
    if manifest.get("format_id") != format_id or store.get("format_id") != format_id:
        raise VerificationError("manifest/store format identity mismatch")
    if manifest.get("coverage") != "complete":
        raise VerificationError("promotion manifests must declare coverage: complete")

    store_facts = {
        str(fact["fact_id"]): fact for fact in store.get("facts", [])
    }
    evidence_facts = manifest.get("facts", [])
    evidence_ids = [str(fact.get("fact_id", "")) for fact in evidence_facts]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise VerificationError("evidence manifest contains duplicate fact IDs")
    if set(evidence_ids) != set(store_facts):
        missing = sorted(set(store_facts) - set(evidence_ids))
        foreign = sorted(set(evidence_ids) - set(store_facts))
        raise VerificationError(
            f"evidence coverage mismatch; missing={missing}, foreign={foreign}"
        )

    research = _research_sources(repo_root, format_id)
    targets = manifest.get("targets", {})
    if not isinstance(targets, dict):
        raise VerificationError("manifest targets must be a mapping")
    source_cache: dict[str, bytes] = {}
    receipt_sources: dict[str, dict[str, str]] = {}
    fact_results: list[dict[str, Any]] = []
    for definition in evidence_facts:
        fact_id = str(definition["fact_id"])
        live_fact = store_facts[fact_id]
        expected_claim_digest = str(definition.get("claim_sha256", ""))
        live_claim_digest = claim_digest(str(live_fact.get("claim", "")))
        assertions_out: list[dict[str, Any]] = []
        fact_pass = expected_claim_digest == live_claim_digest

        for raw_assertion in definition.get("assertions", []):
            target_id = raw_assertion.get("target")
            target = targets.get(target_id, {}) if target_id else {}
            if target_id and (
                target_id not in targets or not isinstance(target, dict)
            ):
                raise VerificationError(f"unknown authority target: {target_id}")
            assertion = {**target, **raw_assertion}
            source_id = str(assertion.get("source_id", ""))
            if source_id not in research:
                raise VerificationError(
                    f"{fact_id} cites unknown research source {source_id}"
                )
            source = research[source_id]
            if source.get("acquisition_status") != "ACQUIRED":
                raise VerificationError(f"{source_id} is not acquired")
            relative_path = str(source.get("local_path", ""))
            artifact = (repo_root / relative_path).resolve()
            if repo_root.resolve() not in artifact.parents:
                raise VerificationError(f"authority path escapes repository: {relative_path}")
            declared_digest = str(source.get("content_hash", ""))
            actual_digest = sha256_file(artifact)
            if actual_digest != declared_digest:
                raise VerificationError(f"authority digest mismatch: {source_id}")
            receipt_sources[source_id] = {
                "source_id": source_id,
                "path": relative_path.replace("\\", "/"),
                "sha256": actual_digest,
            }

            member = assertion.get("member")
            cache_key = f"{source_id}:{member or ''}"
            if cache_key not in source_cache:
                source_cache[cache_key] = _read_member(
                    artifact, str(member) if member else None
                )
            content = source_cache[cache_key]
            member_digest = sha256_bytes(content)
            if member_digest != assertion.get("member_sha256"):
                raise VerificationError(
                    f"authority member digest mismatch: {source_id}:{member}"
                )
            outcome = _assertion_result(assertion, content)
            outcome.update(
                {
                    "source_id": source_id,
                    "member": str(member) if member else None,
                    "member_sha256": member_digest,
                }
            )
            assertions_out.append(outcome)
            fact_pass = fact_pass and outcome["result"] == "PASS"

        if not assertions_out:
            raise VerificationError(f"{fact_id} has no authority assertions")
        fact_record: dict[str, Any] = {
            "fact_id": fact_id,
            "claim_sha256": live_claim_digest,
            "assertions": assertions_out,
            "result": "PASS" if fact_pass else "FAIL",
        }
        fact_record["proof_sha256"] = record_digest(fact_record)
        fact_results.append(fact_record)

    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "format_id": format_id,
        "manifest": {
            "path": manifest_path.relative_to(repo_root).as_posix(),
            "sha256": sha256_file(manifest_path),
        },
        "tool_closure": [
            {"path": path, "sha256": sha256_file(repo_root / path)}
            for path in VERIFIER_PATHS
        ],
        "sources": sorted(receipt_sources.values(), key=lambda item: item["source_id"]),
        "facts": sorted(fact_results, key=lambda item: item["fact_id"]),
    }
    receipt["result"] = (
        "PASS"
        if len(fact_results) == len(store_facts)
        and all(item["result"] == "PASS" for item in fact_results)
        else "FAIL"
    )
    return receipt


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def apply_receipt(
    repo_root: Path,
    format_id: str,
    receipt: dict[str, Any],
) -> tuple[Path, Path]:
    receipt_path = repo_root / "reports" / "sal-verification" / f"{format_id}.json"
    receipt_bytes = canonical_json_bytes(receipt)
    _atomic_write(receipt_path, receipt_bytes)
    if receipt.get("result") != "PASS":
        return receipt_path, repo_root / "shared" / "sal-facts" / f"{format_id}.yaml"

    receipt_sha256 = sha256_bytes(receipt_bytes)
    store_path = repo_root / "shared" / "sal-facts" / f"{format_id}.yaml"
    store = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
    records = {str(item["fact_id"]): item for item in receipt["facts"]}
    for fact in store.get("facts", []):
        fact_id = str(fact["fact_id"])
        record = records[fact_id]
        fact["verification_status"] = "verified"
        provenance = fact.setdefault("provenance", {})
        provenance["verification"] = {
            "method": "declarative_authority_v1",
            "manifest_path": receipt["manifest"]["path"],
            "manifest_sha256": receipt["manifest"]["sha256"],
            "receipt_path": receipt_path.relative_to(repo_root).as_posix(),
            "receipt_sha256": receipt_sha256,
            "fact_proof_sha256": record["proof_sha256"],
        }
    rendered = yaml.safe_dump(
        store,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    ).encode("utf-8")
    _atomic_write(store_path, rendered)
    return receipt_path, store_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify exact SAL facts against pinned authority artifacts"
    )
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()

    try:
        receipt = verify_format(arguments.repo_root.resolve(), arguments.format_id)
        if arguments.apply:
            receipt_path, store_path = apply_receipt(
                arguments.repo_root.resolve(), arguments.format_id, receipt
            )
            print(
                json.dumps(
                    {
                        "result": receipt["result"],
                        "receipt": receipt_path.as_posix(),
                        "store": store_path.as_posix(),
                    },
                    sort_keys=True,
                )
            )
        else:
            print(canonical_json_bytes(receipt).decode("utf-8"), end="")
        return 0 if receipt["result"] == "PASS" else 1
    except (OSError, KeyError, TypeError, VerificationError, yaml.YAMLError) as error:
        print(json.dumps({"result": "ERROR", "error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
