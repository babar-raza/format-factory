"""Atomic, content-addressed materialization for format authorities."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from .authority_lock import (
    AuthorityLockError,
    records_by_id,
    safe_repo_path,
    sha256_file,
)

CAS_ROOT = Path(".local/format-contracts/authority-cas/sha256")
USER_AGENT = "format-factory-authority-materializer/1.0"


@dataclass(frozen=True)
class AuthorityResult:
    format_id: str
    source_id: str
    repository_path: str
    expected_sha256: str
    observed_sha256: str | None
    status: str
    origin: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _observed(path: Path) -> str | None:
    return sha256_file(path) if path.is_file() else None


def _cas_path(repo_root: Path, digest: str) -> Path:
    return safe_repo_path(
        repo_root, (CAS_ROOT / digest[:2] / digest).as_posix()
    )


def _atomic_copy(source: Path, target: Path, expected: str) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with source.open("rb") as reader, temporary.open("wb") as writer:
            shutil.copyfileobj(reader, writer, length=1024 * 1024)
        observed = sha256_file(temporary)
        if observed != expected:
            raise AuthorityLockError(
                f"copy digest mismatch: expected {expected}, observed {observed}"
            )
        os.replace(temporary, target)
        return observed
    finally:
        temporary.unlink(missing_ok=True)


def _download_to_cas(
    repo_root: Path,
    source: dict[str, Any],
) -> tuple[Path | None, str]:
    expected = str(source["expected_sha256"])
    cas = _cas_path(repo_root, expected)
    if cas.is_file() and sha256_file(cas) == expected:
        return cas, "cache"
    cas.parent.mkdir(parents=True, exist_ok=True)
    max_bytes = int(source["limits"]["max_bytes"])
    failures: list[str] = []
    for locator in source["fetch"]["locators"]:
        url = str(locator["url"])
        temporary_name: str | None = None
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            digest = hashlib.sha256()
            total = 0
            with urllib.request.urlopen(  # noqa: S310 - lock allowlist is validated
                request, timeout=int(source["limits"]["timeout_seconds"])
            ) as response, tempfile.NamedTemporaryFile(
                mode="wb", dir=cas.parent, prefix=".download-", delete=False
            ) as writer:
                temporary_name = writer.name
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > max_bytes:
                        raise AuthorityLockError(
                            f"download exceeds max_bytes={max_bytes}"
                        )
                    digest.update(block)
                    writer.write(block)
            observed = digest.hexdigest()
            if observed != expected:
                failures.append(f"{url}: digest {observed}")
                continue
            os.replace(temporary_name, cas)
            temporary_name = None
            return cas, "network"
        except Exception as exc:  # noqa: BLE001 - try declared fallback locators
            failures.append(f"{url}: {type(exc).__name__}: {exc}")
        finally:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
    return None, " | ".join(failures)


def _materialize_url(
    repo_root: Path,
    source: dict[str, Any],
    *,
    online: bool,
) -> AuthorityResult:
    target = safe_repo_path(repo_root, str(source["materialized_path"]))
    expected = str(source["expected_sha256"])
    existing = _observed(target)
    if existing == expected:
        return _result(source, existing, "MATCH", "materialized")
    cas = _cas_path(repo_root, expected)
    origin = "cache"
    if not (cas.is_file() and sha256_file(cas) == expected):
        if not online:
            return _result(
                source,
                existing,
                "MISMATCH" if existing else "MISSING",
                "offline",
                "verified cache object is unavailable",
            )
        downloaded, origin = _download_to_cas(repo_root, source)
        if downloaded is None:
            return _result(
                source,
                existing,
                "MISMATCH" if existing else "MISSING",
                "network",
                origin,
            )
        cas = downloaded
    observed = _atomic_copy(cas, target, expected)
    return _result(source, observed, "MATCH", origin)


def _materialize_zip_member(
    repo_root: Path,
    source: dict[str, Any],
    all_sources: dict[str, dict[str, Any]],
) -> AuthorityResult:
    target = safe_repo_path(repo_root, str(source["materialized_path"]))
    expected = str(source["expected_sha256"])
    existing = _observed(target)
    if existing == expected:
        return _result(source, existing, "MATCH", "materialized")
    fetch = source["fetch"]
    container = all_sources[str(fetch["container_source_id"])]
    archive_path = safe_repo_path(repo_root, str(container["materialized_path"]))
    if _observed(archive_path) != str(container["expected_sha256"]):
        return _result(
            source,
            existing,
            "MISMATCH" if existing else "MISSING",
            "archive",
            f"container {container['source_id']} is not verified",
        )
    member_name = str(fetch["member_path"])
    max_bytes = int(source["limits"]["max_bytes"])
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            try:
                info = archive.getinfo(member_name)
            except KeyError:
                return _result(
                    source, existing, "MISSING", "archive", f"member absent: {member_name}"
                )
            if info.is_dir() or info.file_size > max_bytes:
                return _result(
                    source,
                    existing,
                    "MISMATCH",
                    "archive",
                    "member is a directory or exceeds max_bytes",
                )
            if info.compress_size and info.file_size / info.compress_size > 200:
                return _result(
                    source, existing, "MISMATCH", "archive", "member compression ratio exceeds 200"
                )
            digest = hashlib.sha256()
            with archive.open(info) as reader, temporary.open("wb") as writer:
                while True:
                    block = reader.read(1024 * 1024)
                    if not block:
                        break
                    digest.update(block)
                    writer.write(block)
        observed = digest.hexdigest()
        if observed != expected:
            return _result(
                source,
                existing,
                "MISMATCH",
                "archive",
                f"member digest {observed}",
            )
        os.replace(temporary, target)
        return _result(source, observed, "MATCH", "archive")
    finally:
        temporary.unlink(missing_ok=True)


def _result(
    source: dict[str, Any],
    observed: str | None,
    status: str,
    origin: str,
    detail: str = "",
) -> AuthorityResult:
    legal = source["legal"]
    if legal["use_status"] == "BLOCKED":
        status = "LEGAL_BLOCKED"
        detail = detail or str(legal.get("notes", "source use is blocked"))
    return AuthorityResult(
        format_id=str(source["format_id"]),
        source_id=str(source["source_id"]),
        repository_path=str(source["materialized_path"]),
        expected_sha256=str(source["expected_sha256"]),
        observed_sha256=observed,
        status=status,
        origin=origin,
        detail=detail,
    )


def audit_sources(
    repo_root: Path,
    lock_document: dict[str, Any],
    formats: Iterable[str] | None = None,
) -> list[AuthorityResult]:
    selected = {item.lower() for item in formats or []}
    results = []
    for source in sorted(lock_document["sources"], key=lambda item: item["source_id"]):
        if selected and str(source["format_id"]).lower() not in selected:
            continue
        target = safe_repo_path(repo_root, str(source["materialized_path"]))
        observed = _observed(target)
        expected = str(source["expected_sha256"])
        results.append(
            _result(
                source,
                observed,
                "MATCH" if observed == expected else ("MISMATCH" if observed else "MISSING"),
                "audit",
            )
        )
    return results


def materialize_sources(
    repo_root: Path,
    lock_document: dict[str, Any],
    *,
    online: bool,
    formats: Iterable[str] | None = None,
) -> list[AuthorityResult]:
    selected = {item.lower() for item in formats or []}
    all_sources = records_by_id(lock_document)
    results: dict[str, AuthorityResult] = {}
    direct = [
        source
        for source in lock_document["sources"]
        if not selected or str(source["format_id"]).lower() in selected
    ]
    for source in sorted(direct, key=lambda item: item["source_id"]):
        kind = source["fetch"]["kind"]
        if kind == "LOCAL_FILE":
            target = safe_repo_path(repo_root, str(source["materialized_path"]))
            observed = _observed(target)
            expected = str(source["expected_sha256"])
            results[source["source_id"]] = _result(
                source,
                observed,
                "MATCH" if observed == expected else ("MISMATCH" if observed else "MISSING"),
                "repository",
            )
        elif kind == "URL":
            results[source["source_id"]] = _materialize_url(
                repo_root, source, online=online
            )
    for source in sorted(direct, key=lambda item: item["source_id"]):
        if source["fetch"]["kind"] == "ZIP_MEMBER":
            results[source["source_id"]] = _materialize_zip_member(
                repo_root, source, all_sources
            )
    return [results[key] for key in sorted(results)]


def audit_contract_declarations(
    repo_root: Path,
    lock_document: dict[str, Any],
    formats: Iterable[str],
) -> list[AuthorityResult]:
    """Audit lock/contract referential integrity and live artifact bytes."""

    by_id = records_by_id(lock_document)
    live = {
        item.source_id: item
        for item in audit_sources(repo_root, lock_document, formats)
    }
    results: list[AuthorityResult] = []
    for format_id in sorted(set(formats)):
        path = safe_repo_path(repo_root, f"shared/format-contracts/{format_id}.yaml")
        contract = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for declaration in contract.get("authoritative_sources", []):
            source_id = str(declaration.get("source_id", ""))
            locked = by_id.get(source_id)
            if locked is None:
                results.append(
                    AuthorityResult(
                        format_id=format_id,
                        source_id=source_id,
                        repository_path=str(declaration.get("local_path", "")),
                        expected_sha256=str(declaration.get("content_hash", "")),
                        observed_sha256=None,
                        status="UNDECLARED",
                        origin="contract",
                        detail="source is absent from authority lock",
                    )
                )
                continue
            mismatches = []
            expected_fields = {
                "format_id": format_id,
                "authority_class": declaration.get("authority_class"),
                "materialized_path": declaration.get("local_path"),
                "expected_sha256": declaration.get("content_hash"),
            }
            for field, expected in expected_fields.items():
                if str(locked.get(field, "")) != str(expected or ""):
                    mismatches.append(field)
            current = live[source_id]
            if mismatches:
                current = AuthorityResult(
                    **{
                        **current.to_dict(),
                        "status": "MISMATCH",
                        "origin": "contract",
                        "detail": "lock/contract mismatch: " + ", ".join(mismatches),
                    }
                )
            results.append(current)
    return sorted(results, key=lambda item: (item.format_id, item.source_id))
