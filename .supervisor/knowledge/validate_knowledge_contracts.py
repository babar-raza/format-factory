# validate_knowledge_contracts.py — run with .venv/Scripts/python (PyYAML required, not stdlib)
# Exit 0: all VERIFIED_CURRENT contracts pass. Exit 1: any STALE or MISSING_SOURCE.
# DRAFT_PENDING_AUTHORITY contracts are always skipped and never cause failure.
import sys
import hashlib
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available. Run with .venv/Scripts/python", file=sys.stderr)
    sys.exit(2)

REGISTRY = Path(".supervisor/knowledge/registry.yaml")


def check_contract(meta: dict) -> tuple[bool, str]:
    cid = meta["contract_id"]
    status = meta.get("status", "")

    if status == "DRAFT_PENDING_AUTHORITY":
        return True, f"{cid} DRAFT_PENDING_AUTHORITY (skipped — not verified)"

    cpath = Path(meta["path"])
    if not cpath.exists():
        return False, f"{cid} MISSING_CONTRACT_FILE ({cpath})"

    contract = yaml.safe_load(cpath.read_text(encoding="utf-8"))
    hashes = contract.get("source_hashes", [])

    if not hashes:
        return True, f"{cid} VERIFIED_CURRENT (no source_hashes)"

    for entry in hashes:
        src = Path(entry["path"])
        stored = entry["sha256"]
        if not src.exists():
            return False, f"{cid} MISSING_SOURCE ({src})"
        actual = hashlib.sha256(src.read_bytes()).hexdigest()
        if actual != stored:
            return False, (
                f"{cid} STALE (hash diverged for {src})\n"
                f"  stored: {stored}\n"
                f"  actual: {actual}"
            )

    return True, f"{cid} VERIFIED_CURRENT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", help="Check single contract by ID")
    args = parser.parse_args()

    if not REGISTRY.exists():
        print(f"ERROR: registry not found at {REGISTRY}", file=sys.stderr)
        return 1

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    contracts = registry.get("contracts", [])

    if args.contract:
        contracts = [c for c in contracts if c["contract_id"] == args.contract]
        if not contracts:
            print(f"ERROR: contract {args.contract!r} not in registry", file=sys.stderr)
            return 1

    exit_code = 0
    for meta in contracts:
        passed, msg = check_contract(meta)
        print(msg)
        if not passed:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
