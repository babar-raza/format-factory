from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import zipfile
from pathlib import Path

import pytest
import yaml

from tools.format_contract import authority_runtime
from tools.format_contract.authority_lock import (
    AuthorityLockError,
    canonical_yaml,
    load_lock,
    merge_locked_sources,
    sync_product_requirements,
)
from tools.format_contract.authority_runtime import (
    audit_contract_declarations,
    materialize_sources,
    probe_url,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "schemas/format-contracts/authority-lock.schema.json"


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _legal() -> dict:
    return {
        "license_id": "TEST",
        "redistribution": "LOCAL_CACHE_ONLY",
        "use_status": "APPROVED_FOR_LOCAL_USE",
        "evidence": "test fixture",
    }


def _limits(size: int = 1024 * 1024) -> dict:
    return {"max_bytes": size, "timeout_seconds": 5, "max_redirects": 2}


def _lock(sources: list[dict]) -> dict:
    return {
        "schema_version": "1.0",
        "lock_id": "FF-AUTHORITY-LOCK-001",
        "sources": sources,
        "generated_by": "test",
        "visibility": "internal",
    }


def _source(
    source_id: str,
    digest: str,
    path: str,
    fetch: dict,
    *,
    authority_class: str = "AUTHORITATIVE",
) -> dict:
    if fetch["kind"] == "URL" and "allowed_hosts" not in fetch:
        fetch = {**fetch, "allowed_hosts": ["example.invalid"]}
    return {
        "source_id": source_id,
        "format_id": "ipynb",
        "title": source_id,
        "organization": "Test",
        "version": "1",
        "authority_class": authority_class,
        "materialized_path": path,
        "expected_sha256": digest,
        "media_type": "application/octet-stream",
        "legal": _legal(),
        "limits": _limits(),
        "fetch": fetch,
    }


class _Response(io.BytesIO):
    status = 200
    headers: dict[str, str] = {}

    def __init__(self, value: bytes, url: str = "https://example.invalid/final"):
        super().__init__(value)
        self._url = url

    def geturl(self) -> str:
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_probe_url_bootstraps_digest_without_persisting_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"new official authority"

    class FakeOpener:
        def open(self, request, timeout):  # noqa: ANN001
            assert request.full_url == "https://example.invalid/standard.zip"
            assert timeout == 7
            return _Response(payload, request.full_url)

    monkeypatch.setattr(
        authority_runtime.urllib.request,
        "build_opener",
        lambda *handlers: FakeOpener(),
    )
    result = probe_url(
        "https://example.invalid/standard.zip",
        allowed_hosts=["example.invalid"],
        max_bytes=1024,
        timeout_seconds=7,
        max_redirects=1,
        expected_sha1=hashlib.sha1(payload, usedforsecurity=False).hexdigest(),
    )
    assert result.sha256 == hashlib.sha256(payload).hexdigest()
    assert result.byte_count == len(payload)
    assert result.expected_sha1_match is True
    assert list(tmp_path.rglob("*")) == []


def test_probe_url_rejects_published_digest_mismatch_and_oversize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"x" * 33

    class FakeOpener:
        def open(self, request, timeout):  # noqa: ANN001
            return _Response(payload, request.full_url)

    monkeypatch.setattr(
        authority_runtime.urllib.request,
        "build_opener",
        lambda *handlers: FakeOpener(),
    )
    kwargs = {
        "allowed_hosts": ["example.invalid"],
        "timeout_seconds": 5,
        "max_redirects": 1,
    }
    with pytest.raises(AuthorityLockError, match="published SHA-1 mismatch"):
        probe_url(
            "https://example.invalid/standard.zip",
            max_bytes=1024,
            expected_sha1="0" * 40,
            **kwargs,
        )
    with pytest.raises(AuthorityLockError, match="download exceeds max_bytes"):
        probe_url(
            "https://example.invalid/standard.zip",
            max_bytes=32,
            **kwargs,
        )
    with pytest.raises(AuthorityLockError, match="HTTPS host policy"):
        probe_url(
            "https://blocked.invalid/standard.zip",
            max_bytes=1024,
            **kwargs,
        )


def test_online_then_offline_replay_is_content_addressed_and_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    direct = b"locked authority"
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        archive.writestr("spec/prose.html", b"<h1>spec</h1>")
    archive_bytes = archive_buffer.getvalue()
    payloads = {
        "https://example.invalid/direct": direct,
        "https://example.invalid/archive": archive_bytes,
    }

    class FakeOpener:
        def open(self, request, timeout):  # noqa: ANN001
            assert timeout == 5
            return _Response(payloads[request.full_url], request.full_url)

    monkeypatch.setattr(
        authority_runtime.urllib.request,
        "build_opener",
        lambda *handlers: FakeOpener(),
    )
    document = _lock(
        [
            _source(
                "SRC-IPYNB-001",
                _digest(direct),
                ".local/format-contracts/acquired/ipynb/direct.bin",
                {
                    "kind": "URL",
                    "locators": [
                        {"url": "https://example.invalid/direct", "immutable": True}
                    ],
                },
            ),
            _source(
                "SRC-IPYNB-002",
                _digest(archive_bytes),
                ".local/format-contracts/acquired/ipynb/archive.zip",
                {
                    "kind": "URL",
                    "locators": [
                        {"url": "https://example.invalid/archive", "immutable": True}
                    ],
                },
            ),
            _source(
                "SRC-IPYNB-003",
                _digest(b"<h1>spec</h1>"),
                ".local/format-contracts/acquired/ipynb/prose.html",
                {
                    "kind": "ZIP_MEMBER",
                    "container_source_id": "SRC-IPYNB-002",
                    "member_path": "spec/prose.html",
                },
            ),
        ]
    )
    first = materialize_sources(tmp_path, document, online=True)
    assert [item.status for item in first] == ["MATCH", "MATCH", "MATCH"]
    assert {item.origin for item in first} == {"network", "archive"}

    def network_must_not_run(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("offline replay attempted network access")

    monkeypatch.setattr(
        authority_runtime.urllib.request, "build_opener", network_must_not_run
    )
    direct_path = tmp_path / ".local/format-contracts/acquired/ipynb/direct.bin"
    direct_path.unlink()
    replay = materialize_sources(tmp_path, document, online=False)
    assert [item.status for item in replay] == ["MATCH", "MATCH", "MATCH"]
    assert direct_path.read_bytes() == direct


def test_failed_digest_never_replaces_existing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / ".local/format-contracts/acquired/ipynb/source.bin"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"preserve me")
    source = _source(
        "SRC-IPYNB-001",
        _digest(b"expected"),
        ".local/format-contracts/acquired/ipynb/source.bin",
        {
            "kind": "URL",
            "locators": [{"url": "https://example.invalid/source", "immutable": True}],
        },
    )
    class WrongOpener:
        def open(self, request, timeout):  # noqa: ANN001
            return _Response(b"wrong", request.full_url)

    monkeypatch.setattr(
        authority_runtime.urllib.request,
        "build_opener",
        lambda *handlers: WrongOpener(),
    )
    result = materialize_sources(tmp_path, _lock([source]), online=True)[0]
    assert result.status == "MISMATCH"
    assert target.read_bytes() == b"preserve me"


def test_lock_validation_rejects_path_escape_and_unknown_container(
    tmp_path: Path,
) -> None:
    schema = tmp_path / "schema.json"
    schema.write_bytes(SCHEMA.read_bytes())
    escaped = _source(
        "SRC-IPYNB-001",
        "a" * 64,
        "../escape.bin",
        {
            "kind": "URL",
            "locators": [{"url": "https://example.invalid/a", "immutable": True}],
        },
    )
    lock_path = tmp_path / "lock.yaml"
    lock_path.write_bytes(canonical_yaml(_lock([escaped])))
    with pytest.raises(AuthorityLockError, match="escapes repository root"):
        load_lock(tmp_path, Path("lock.yaml"), Path("schema.json"))

    member = _source(
        "SRC-IPYNB-002",
        "b" * 64,
        "authority/member.bin",
        {
            "kind": "ZIP_MEMBER",
            "container_source_id": "SRC-IPYNB-404",
            "member_path": "member.bin",
        },
    )
    lock_path.write_bytes(canonical_yaml(_lock([member])))
    with pytest.raises(AuthorityLockError, match="unknown container"):
        load_lock(tmp_path, Path("lock.yaml"), Path("schema.json"))


def test_product_requirement_generation_is_deterministic_and_checkable(
    tmp_path: Path,
) -> None:
    research = {
        "schema_version": "1.0",
        "format_id": "ipynb",
        "canonical": True,
        "findings": [
            {
                "finding_id": "RF-NB-00002",
                "kind": "product_requirement",
                "capability_domain": "CLEAN",
                "requirement": "Clear transient output deterministically for clean version control.",
                "source_ids": ["SRC-NB-003"],
                "review": {"verdict": "ACCEPTED", "reviewer": "test"},
            },
            {
                "finding_id": "RF-NB-00001",
                "kind": "api_expectation",
                "capability_domain": "MODEL",
                "requirement": "Expose typed notebook cells without raw dictionary manipulation.",
                "source_ids": ["SRC-NB-003"],
                "review": {"verdict": "ACCEPTED", "reviewer": "test"},
            },
        ],
        "source_records": [
            {
                "source_id": "SRC-NB-003",
                "title": "Notebook requirements",
                "organization": "Format Factory",
                "authority_class": "PRODUCT_REQUIREMENT",
                "acquisition_status": "ACQUIRED",
            }
        ],
    }
    target = tmp_path / "shared/format-contracts/research/ipynb.yaml"
    target.parent.mkdir(parents=True)
    target.write_text(yaml.safe_dump(research, sort_keys=False), encoding="utf-8")
    first = sync_product_requirements(tmp_path, ["ipynb"])
    requirement_path = (
        tmp_path / "shared/format-contracts/product-requirements/ipynb.yaml"
    )
    first_bytes = requirement_path.read_bytes()
    second = sync_product_requirements(tmp_path, ["ipynb"])
    assert first == second
    assert requirement_path.read_bytes() == first_bytes
    assert sync_product_requirements(tmp_path, ["ipynb"], check=True) == first
    document = yaml.safe_load(first_bytes)
    assert [item["finding_id"] for item in document["requirements"]] == [
        "RF-NB-00001",
        "RF-NB-00002",
    ]


def test_merge_locked_sources_preserves_findings_plane_metadata() -> None:
    existing = [
        {
            "source_id": "SRC-NB-003",
            "title": "old",
            "organization": "Format Factory",
            "authority_class": "PRODUCT_REQUIREMENT",
            "acquisition_status": "ACQUIRED",
            "custom_review_note": "preserve",
        }
    ]
    locked = _source(
        "SRC-NB-003",
        "c" * 64,
        "shared/format-contracts/product-requirements/ipynb.yaml",
        {
            "kind": "LOCAL_FILE",
            "source_path": "shared/format-contracts/product-requirements/ipynb.yaml",
        },
        authority_class="PRODUCT_REQUIREMENT",
    )
    result = merge_locked_sources(existing, _lock([locked]), "ipynb")
    assert result[0]["content_hash"] == "c" * 64
    assert result[0]["custom_review_note"] == "preserve"


def test_contract_audit_reports_undeclared_and_declaration_mismatch(
    tmp_path: Path,
) -> None:
    contract_path = tmp_path / "shared/format-contracts/ipynb.yaml"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        yaml.safe_dump(
            {
                "authoritative_sources": [
                    {
                        "source_id": "SRC-NB-404",
                        "local_path": "missing.bin",
                        "content_hash": "d" * 64,
                        "authority_class": "AUTHORITATIVE",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    results = audit_contract_declarations(tmp_path, _lock([]), ["ipynb"])
    assert len(results) == 1
    assert results[0].status == "UNDECLARED"


def test_atomic_copy_is_safe_for_threads_and_processes(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    target = tmp_path / "target.bin"
    payload = b"authority" * 8192
    source.write_bytes(payload)
    expected = _digest(payload)
    with ThreadPoolExecutor(max_workers=8) as pool:
        thread_results = list(
            pool.map(
                lambda _: authority_runtime._atomic_copy(  # noqa: SLF001
                    source, target, expected
                ),
                range(24),
            )
        )
    assert thread_results == [expected] * 24
    script = (
        "from pathlib import Path\n"
        "from tools.format_contract.authority_runtime import _atomic_copy\n"
        f"print(_atomic_copy(Path({str(source)!r}), Path({str(target)!r}), {expected!r}))\n"
    )
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", script],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(8)
    ]
    process_results = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        assert process.returncode == 0, stderr
        process_results.append(stdout.strip())
    assert process_results == [expected] * 8
    assert target.read_bytes() == payload
    assert list(tmp_path.glob(".target.bin.*.tmp")) == []


def test_redirect_handler_rejects_excess_and_cross_policy_redirects() -> None:
    request = authority_runtime.urllib.request.Request(
        "https://example.invalid/source"
    )
    handler = authority_runtime._HttpsRedirectHandler(  # noqa: SLF001
        1, ["example.invalid"]
    )
    first = handler.redirect_request(
        request,
        None,
        302,
        "Found",
        {},
        "https://example.invalid/next",
    )
    assert first is not None
    with pytest.raises(authority_runtime.urllib.error.HTTPError):
        handler.redirect_request(
            first,
            None,
            302,
            "Found",
            {},
            "https://example.invalid/final",
        )
    with pytest.raises(AuthorityLockError, match="host policy"):
        authority_runtime._validate_network_url(  # noqa: SLF001
            "https://localhost/private", ["example.invalid"]
        )


def test_oversize_stream_and_legal_block_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class OversizeOpener:
        def open(self, request, timeout):  # noqa: ANN001
            return _Response(b"x" * 33, request.full_url)

    monkeypatch.setattr(
        authority_runtime.urllib.request,
        "build_opener",
        lambda *handlers: OversizeOpener(),
    )
    source = _source(
        "SRC-IPYNB-001",
        _digest(b"x" * 33),
        ".local/format-contracts/acquired/ipynb/oversize.bin",
        {
            "kind": "URL",
            "locators": [{"url": "https://example.invalid/source", "immutable": True}],
        },
    )
    source["limits"]["max_bytes"] = 32
    result = materialize_sources(tmp_path, _lock([source]), online=True)[0]
    assert result.status == "MISSING"
    assert "exceeds max_bytes" in result.detail
    source["legal"]["use_status"] = "BLOCKED"
    result = materialize_sources(tmp_path, _lock([source]), online=False)[0]
    assert result.status == "LEGAL_BLOCKED"


def test_zip_member_limits_and_duplicate_target_rejection(tmp_path: Path) -> None:
    archive_path = tmp_path / ".local/format-contracts/acquired/ipynb/archive.zip"
    archive_path.parent.mkdir(parents=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("huge.txt", b"a" * 50_000)
    archive_bytes = archive_path.read_bytes()
    container = _source(
        "SRC-IPYNB-001",
        _digest(archive_bytes),
        archive_path.relative_to(tmp_path).as_posix(),
        {
            "kind": "URL",
            "locators": [{"url": "https://example.invalid/archive", "immutable": True}],
        },
    )
    member = _source(
        "SRC-IPYNB-002",
        _digest(b"a" * 50_000),
        ".local/format-contracts/acquired/ipynb/member.txt",
        {
            "kind": "ZIP_MEMBER",
            "container_source_id": "SRC-IPYNB-001",
            "member_path": "huge.txt",
        },
    )
    result = materialize_sources(tmp_path, _lock([container, member]), online=False)
    assert result[1].status == "MISMATCH"
    assert "compression ratio" in result[1].detail
    duplicate = {**member, "source_id": "SRC-IPYNB-003"}
    duplicate["fetch"] = {
        "kind": "ZIP_MEMBER",
        "container_source_id": "SRC-IPYNB-001",
        "member_path": "missing.txt",
    }
    lock_path = tmp_path / "lock.yaml"
    schema = tmp_path / "schema.json"
    schema.write_bytes(SCHEMA.read_bytes())
    lock_path.write_bytes(canonical_yaml(_lock([container, member, duplicate])))
    with pytest.raises(AuthorityLockError, match="is shared"):
        load_lock(tmp_path, Path("lock.yaml"), Path("schema.json"))
