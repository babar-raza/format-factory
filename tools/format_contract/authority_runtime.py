"""Atomic, content-addressed materialization for format authorities."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
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
USER_AGENT = (
    "Mozilla/5.0 (compatible; format-factory-authority-materializer/1.0; "
    "+https://gitlab.com/format-factory)"
)


def _host_allowed(host: str | None, allowed_hosts: Iterable[str]) -> bool:
    if not host:
        return False
    candidate = host.rstrip(".").lower()
    for allowed in allowed_hosts:
        rule = allowed.rstrip(".").lower()
        if rule.startswith("*."):
            suffix = rule[1:]
            if candidate.endswith(suffix) and candidate != suffix[1:]:
                return True
        elif candidate == rule:
            return True
    return False


def _validate_network_url(url: str, allowed_hosts: Iterable[str]) -> None:
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme.lower() != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or not _host_allowed(parsed.hostname, allowed_hosts)
    ):
        raise AuthorityLockError(f"network URL is outside the HTTPS host policy: {url}")


class _HttpsRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Bound redirects and re-check the scheme and host on every hop."""

    def __init__(self, max_redirects: int, allowed_hosts: Iterable[str]) -> None:
        super().__init__()
        self._max_redirects = max_redirects
        self._allowed_hosts = tuple(allowed_hosts)
        self._redirect_count = 0

    def redirect_request(  # type: ignore[override]
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        self._redirect_count += 1
        if self._redirect_count > self._max_redirects:
            raise urllib.error.HTTPError(
                req.full_url,
                code,
                f"redirect limit exceeded ({self._max_redirects})",
                headers,
                fp,
            )
        _validate_network_url(newurl, self._allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


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


def _replace_verified(
    temporary: Path,
    target: Path,
    expected: str,
    *,
    attempts: int = 12,
) -> None:
    """Place verified bytes despite bounded Windows sharing races.

    Concurrent materializers are permitted to race only when every contender
    has already verified the same expected digest. If another contender wins,
    its target bytes satisfy this call and the caller removes its own temporary
    file. A different target digest never counts as success.
    """

    last_error: PermissionError | None = None
    for attempt in range(attempts):
        try:
            os.replace(temporary, target)
            return
        except PermissionError as exc:
            last_error = exc
            try:
                if target.is_file() and sha256_file(target) == expected:
                    return
            except PermissionError:
                pass
            if attempt + 1 < attempts:
                time.sleep(min(0.005 * (2**attempt), 0.1))
    if last_error is not None:
        raise last_error
    raise AuthorityLockError(f"atomic replacement failed without an error: {target}")


def _atomic_copy(source: Path, target: Path, expected: str) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with source.open("rb") as reader, tempfile.NamedTemporaryFile(
            mode="wb",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as writer:
            temporary_name = writer.name
            shutil.copyfileobj(reader, writer, length=1024 * 1024)
        temporary = Path(temporary_name)
        observed = sha256_file(temporary)
        if observed != expected:
            raise AuthorityLockError(
                f"copy digest mismatch: expected {expected}, observed {observed}"
            )
        _replace_verified(temporary, target, expected)
        if not temporary.exists():
            temporary_name = None
        return observed
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


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
    timeout = int(source["limits"]["timeout_seconds"])
    max_redirects = int(source["limits"]["max_redirects"])
    allowed_hosts = tuple(str(item) for item in source["fetch"]["allowed_hosts"])
    failures: list[str] = []
    for locator in source["fetch"]["locators"]:
        url = str(locator["url"])
        temporary_name: str | None = None
        try:
            _validate_network_url(url, allowed_hosts)
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            opener = urllib.request.build_opener(
                _HttpsRedirectHandler(max_redirects, allowed_hosts)
            )
            digest = hashlib.sha256()
            total = 0
            with opener.open(  # noqa: S310 - lock allowlist is validated
                request, timeout=timeout
            ) as response, tempfile.NamedTemporaryFile(
                mode="wb", dir=cas.parent, prefix=".download-", delete=False
            ) as writer:
                temporary_name = writer.name
                final_url = str(response.geturl())
                _validate_network_url(final_url, allowed_hosts)
                status = int(getattr(response, "status", 200))
                if not 200 <= status < 300:
                    raise AuthorityLockError(f"unexpected HTTP status {status}")
                content_length = response.headers.get("Content-Length")
                if content_length is not None and int(content_length) > max_bytes:
                    raise AuthorityLockError(
                        f"declared Content-Length exceeds max_bytes={max_bytes}"
                    )
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
            _replace_verified(Path(temporary_name), cas, expected)
            if not Path(temporary_name).exists():
                temporary_name = None
            return (
                cas,
                f"network status={status} final_url={final_url} bytes={total}",
            )
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
    detail = ""
    if not (cas.is_file() and sha256_file(cas) == expected):
        if not online:
            return _result(
                source,
                existing,
                "MISMATCH" if existing else "MISSING",
                "offline",
                "verified cache object is unavailable",
            )
        downloaded, download_evidence = _download_to_cas(repo_root, source)
        if downloaded is None:
            return _result(
                source,
                existing,
                "MISMATCH" if existing else "MISSING",
                "network",
                download_evidence,
            )
        cas = downloaded
        origin = "network"
        detail = download_evidence
    observed = _atomic_copy(cas, target, expected)
    return _result(source, observed, "MATCH", origin, detail)


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
    temporary_name: str | None = None
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
            with archive.open(info) as reader, tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as writer:
                temporary_name = writer.name
                while True:
                    block = reader.read(1024 * 1024)
                    if not block:
                        break
                    digest.update(block)
                    writer.write(block)
        temporary = Path(temporary_name)
        observed = digest.hexdigest()
        if observed != expected:
            return _result(
                source,
                existing,
                "MISMATCH",
                "archive",
                f"member digest {observed}",
            )
        _replace_verified(temporary, target, expected)
        if not temporary.exists():
            temporary_name = None
        return _result(source, observed, "MATCH", "archive")
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


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
