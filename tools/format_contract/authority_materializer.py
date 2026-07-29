"""CLI for deterministic authority generation, materialization, and audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .authority_lock import (
        AuthorityLockError,
        DEFAULT_LOCK,
        DEFAULT_SCHEMA,
        load_lock,
        sha256_bytes,
        sync_product_requirements,
    )
    from .authority_runtime import (
        AuthorityResult,
        audit_contract_declarations,
        audit_sources,
        materialize_sources,
        probe_url,
    )
except ImportError:  # direct script execution from tools/format_contract
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.format_contract.authority_lock import (  # type: ignore[no-redef]
        AuthorityLockError,
        DEFAULT_LOCK,
        DEFAULT_SCHEMA,
        load_lock,
        sha256_bytes,
        sync_product_requirements,
    )
    from tools.format_contract.authority_runtime import (  # type: ignore[no-redef]
        AuthorityResult,
        audit_contract_declarations,
        audit_sources,
        materialize_sources,
        probe_url,
    )


def _report(
    results: list[AuthorityResult],
    *,
    mode: str,
    lock_sha256: str,
) -> dict[str, Any]:
    statuses = {name: 0 for name in ("MATCH", "MISSING", "MISMATCH", "UNDECLARED", "LEGAL_BLOCKED")}
    for result in results:
        statuses[result.status] = statuses.get(result.status, 0) + 1
    return {
        "schema_version": "1.0",
        "mode": mode,
        "lock_sha256": lock_sha256,
        "results": [item.to_dict() for item in results],
        "summary": statuses,
        "ready": statuses["MISSING"] == statuses["MISMATCH"] == statuses["UNDECLARED"] == statuses["LEGAL_BLOCKED"] == 0,
    }


def _formats(values: list[str] | None) -> list[str]:
    return sorted(set(item.lower() for item in values or []))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    sub = parser.add_subparsers(dest="command", required=True)

    materialize = sub.add_parser("materialize")
    materialize.add_argument("--format", action="append")
    materialize.add_argument("--online", action="store_true")

    audit = sub.add_parser("audit")
    audit.add_argument("--format", action="append")
    audit.add_argument("--contracts", action="store_true")

    sync = sub.add_parser("sync-product-requirements")
    sync.add_argument("--format", action="append", required=True)
    sync.add_argument("--check", action="store_true")

    probe = sub.add_parser("probe-url")
    probe.add_argument("--url", required=True)
    probe.add_argument("--allowed-host", action="append", required=True)
    probe.add_argument("--max-bytes", type=int, required=True)
    probe.add_argument("--timeout-seconds", type=int, required=True)
    probe.add_argument("--max-redirects", type=int, required=True)
    probe.add_argument("--expected-sha1")

    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    try:
        if args.command == "probe-url":
            result = probe_url(
                str(args.url),
                allowed_hosts=args.allowed_host,
                max_bytes=int(args.max_bytes),
                timeout_seconds=int(args.timeout_seconds),
                max_redirects=int(args.max_redirects),
                expected_sha1=args.expected_sha1,
            )
            print(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "mode": "probe-url",
                        "result": result.to_dict(),
                        "ready": True,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0
        if args.command == "sync-product-requirements":
            outputs = sync_product_requirements(
                root, _formats(args.format), check=bool(args.check)
            )
            print(json.dumps({"outputs": outputs, "check": bool(args.check)}, sort_keys=True))
            return 0
        lock, raw = load_lock(root, args.lock, args.schema)
        if args.command == "materialize":
            results = materialize_sources(
                root, lock, online=bool(args.online), formats=_formats(args.format)
            )
            report = _report(
                results,
                mode="online" if args.online else "offline",
                lock_sha256=sha256_bytes(raw),
            )
        else:
            selected = _formats(args.format) or sorted(
                {str(source["format_id"]) for source in lock["sources"]}
            )
            results = (
                audit_contract_declarations(root, lock, selected)
                if args.contracts
                else audit_sources(root, lock, selected)
            )
            report = _report(results, mode="audit", lock_sha256=sha256_bytes(raw))
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 0 if report["ready"] else 2
    except (AuthorityLockError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
