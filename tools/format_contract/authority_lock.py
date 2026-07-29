"""Canonical authority-lock loading, validation, and deterministic projections.

The lock is the sole acquisition contract for format-contract authorities.  It
does not claim that bytes exist: materialization and strict ProductContract
compilation compute that state from the filesystem on every run.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK = Path("shared/format-contracts/authority-lock.yaml")
DEFAULT_SCHEMA = Path("schemas/format-contracts/authority-lock.schema.json")
PRODUCT_REQUIREMENTS = Path("shared/format-contracts/product-requirements")
SHA256_LENGTH = 64


class AuthorityLockError(ValueError):
    """The authority lock is missing, malformed, contradictory, or unsafe."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_repo_path(root: Path, value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute():
        raise AuthorityLockError(f"absolute repository path is forbidden: {value}")
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise AuthorityLockError(f"path escapes repository root: {value}") from exc
    return resolved


def load_lock(
    repo_root: Path = REPO_ROOT,
    lock_path: Path = DEFAULT_LOCK,
    schema_path: Path = DEFAULT_SCHEMA,
) -> tuple[dict[str, Any], bytes]:
    """Load and JSON-Schema validate the canonical lock, retaining exact bytes."""

    lock_file = safe_repo_path(repo_root, lock_path.as_posix())
    schema_file = safe_repo_path(repo_root, schema_path.as_posix())
    if not lock_file.is_file():
        raise AuthorityLockError(f"authority lock is missing: {lock_path.as_posix()}")
    if not schema_file.is_file():
        raise AuthorityLockError(f"authority lock schema is missing: {schema_path.as_posix()}")
    raw = lock_file.read_bytes()
    document = yaml.safe_load(raw) or {}
    if not isinstance(document, dict):
        raise AuthorityLockError("authority lock must be a YAML mapping")
    try:
        import jsonschema

        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        errors = sorted(
            jsonschema.Draft202012Validator(schema).iter_errors(document),
            key=lambda error: list(error.absolute_path),
        )
    except (json.JSONDecodeError, OSError) as exc:
        raise AuthorityLockError(f"authority lock schema cannot be loaded: {exc}") from exc
    if errors:
        rendered = []
        for error in errors[:10]:
            location = "/".join(str(part) for part in error.absolute_path) or "<root>"
            rendered.append(f"{location}: {error.message}")
        raise AuthorityLockError("authority lock schema failed: " + " | ".join(rendered))
    _validate_semantics(repo_root, document)
    return document, raw


def _validate_semantics(repo_root: Path, document: dict[str, Any]) -> None:
    records = document.get("sources", [])
    by_id: dict[str, dict[str, Any]] = {}
    by_path: dict[str, str] = {}
    for source in records:
        source_id = str(source["source_id"])
        if source_id in by_id:
            raise AuthorityLockError(f"duplicate authority source ID: {source_id}")
        by_id[source_id] = source
        materialized_path = str(source["materialized_path"])
        safe_repo_path(repo_root, materialized_path)
        if materialized_path in by_path:
            raise AuthorityLockError(
                f"materialized path {materialized_path} is shared by "
                f"{by_path[materialized_path]} and {source_id}"
            )
        by_path[materialized_path] = source_id
        expected = str(source["expected_sha256"])
        if len(expected) != SHA256_LENGTH or any(c not in "0123456789abcdef" for c in expected):
            raise AuthorityLockError(f"{source_id}: expected_sha256 is not lowercase SHA-256")
        fetch = source["fetch"]
        kind = fetch["kind"]
        if kind == "LOCAL_FILE":
            source_path = str(fetch["source_path"])
            safe_repo_path(repo_root, source_path)
            if source_path != materialized_path:
                raise AuthorityLockError(
                    f"{source_id}: LOCAL_FILE source_path must equal materialized_path"
                )
        elif kind == "URL":
            if not fetch.get("locators"):
                raise AuthorityLockError(f"{source_id}: URL source has no locators")
        elif kind == "ZIP_MEMBER":
            container = str(fetch["container_source_id"])
            if container == source_id:
                raise AuthorityLockError(f"{source_id}: archive cannot contain itself")
    for source in records:
        fetch = source["fetch"]
        if fetch["kind"] == "ZIP_MEMBER":
            container = str(fetch["container_source_id"])
            record = by_id.get(container)
            if record is None:
                raise AuthorityLockError(
                    f"{source['source_id']}: unknown container source {container}"
                )
            if record["fetch"]["kind"] != "URL":
                raise AuthorityLockError(
                    f"{source['source_id']}: container {container} must be a URL source"
                )


def records_by_id(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(source["source_id"]): source for source in document.get("sources", [])}


def records_for_format(
    document: dict[str, Any], format_id: str
) -> list[dict[str, Any]]:
    return sorted(
        (
            source
            for source in document.get("sources", [])
            if str(source.get("format_id", "")).lower() == format_id.lower()
        ),
        key=lambda source: str(source["source_id"]),
    )


def source_record_projection(source: dict[str, Any]) -> dict[str, Any]:
    """Project a lock record into the existing L30 research source vocabulary."""

    fetch = source["fetch"]
    locator = None
    if fetch["kind"] == "URL":
        locator = fetch["locators"][0]["url"]
    return {
        "title": source["title"],
        "source_id": source["source_id"],
        "organization": source["organization"],
        "version": source["version"],
        "local_path": source["materialized_path"],
        "canonical_url": locator,
        "content_hash": source["expected_sha256"],
        "authority_class": source["authority_class"],
        # This is a declaration label only. Strict readiness is always computed
        # from bytes and never from this field.
        "acquisition_status": "ACQUIRED",
    }


def merge_locked_sources(
    existing: Iterable[dict[str, Any]],
    lock_document: dict[str, Any],
    format_id: str,
) -> list[dict[str, Any]]:
    """Replace matching source declarations from the lock without losing extras."""

    merged = {
        str(record.get("source_id")): dict(record)
        for record in existing
        if record.get("source_id")
    }
    for source in records_for_format(lock_document, format_id):
        source_id = str(source["source_id"])
        record = dict(merged.get(source_id, {}))
        record.update(source_record_projection(source))
        merged[source_id] = record
    return [merged[key] for key in sorted(merged)]


def product_requirement_document(
    repo_root: Path, format_id: str, source_id: str
) -> dict[str, Any]:
    """Derive the tracked internal-requirement authority from reviewed findings."""

    research_path = safe_repo_path(
        repo_root, f"shared/format-contracts/research/{format_id}.yaml"
    )
    research = yaml.safe_load(research_path.read_text(encoding="utf-8")) or {}
    source = next(
        (
            item
            for item in research.get("source_records", [])
            if item.get("source_id") == source_id
        ),
        None,
    )
    if source is None or source.get("authority_class") != "PRODUCT_REQUIREMENT":
        raise AuthorityLockError(
            f"{format_id}: PRODUCT_REQUIREMENT source {source_id} is missing"
        )
    requirements = []
    retained = (
        "finding_id",
        "kind",
        "capability_domain",
        "depth_hint",
        "requirement",
        "api_expectations",
        "required_tests",
        "security_requirements",
        "review",
    )
    for finding in research.get("findings", []):
        if source_id not in (finding.get("source_ids") or []):
            continue
        requirements.append(
            {field: finding[field] for field in retained if field in finding}
        )
    requirements.sort(key=lambda item: str(item.get("finding_id", "")))
    if not requirements:
        raise AuthorityLockError(
            f"{format_id}: source {source_id} has no reviewed requirements"
        )
    return {
        "schema_version": "1.0",
        "source_id": source_id,
        "format_id": format_id,
        "authority_class": "PRODUCT_REQUIREMENT",
        "status": "VERIFIED_CURRENT",
        "title": source["title"],
        "organization": source.get("organization", "Format Factory"),
        "derived_from": research_path.relative_to(repo_root.resolve()).as_posix(),
        "requirements": requirements,
        "generated_by": "codex",
        "visibility": "internal",
    }


def canonical_yaml(value: dict[str, Any]) -> bytes:
    return (
        yaml.safe_dump(
            value,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        )
        .replace("\r\n", "\n")
        .encode("utf-8")
    )


def sync_product_requirements(
    repo_root: Path,
    formats: Iterable[str],
    *,
    check: bool = False,
) -> dict[str, str]:
    """Generate or check deterministic tracked PRODUCT_REQUIREMENT documents."""

    outputs: dict[str, str] = {}
    for format_id in sorted(set(formats)):
        research_path = safe_repo_path(
            repo_root, f"shared/format-contracts/research/{format_id}.yaml"
        )
        research = yaml.safe_load(research_path.read_text(encoding="utf-8")) or {}
        internal = [
            source
            for source in research.get("source_records", [])
            if source.get("authority_class") == "PRODUCT_REQUIREMENT"
        ]
        if len(internal) != 1:
            raise AuthorityLockError(
                f"{format_id}: expected exactly one PRODUCT_REQUIREMENT source"
            )
        source_id = str(internal[0]["source_id"])
        document = product_requirement_document(repo_root, format_id, source_id)
        data = canonical_yaml(document)
        relative = PRODUCT_REQUIREMENTS / f"{format_id}.yaml"
        target = safe_repo_path(repo_root, relative.as_posix())
        if check:
            if not target.is_file() or target.read_bytes() != data:
                raise AuthorityLockError(
                    f"product requirement output drift: {relative.as_posix()}"
                )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
            temporary.write_bytes(data)
            os.replace(temporary, target)
        outputs[relative.as_posix()] = sha256_bytes(data)
    return outputs
