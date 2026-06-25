"""knowledge_freshness_validator.py — V68 Knowledge Contract Freshness Check.

Checks all VERIFIED_CURRENT contracts in .supervisor/knowledge/registry.yaml against
their source_hashes. WARN (non-blocking) on STALE. PASS on fresh. SKIP on DRAFT.

Callable from governance_validator_runner.py (validate_knowledge_freshness) OR
standalone via CLI (prints WARNING lines to stdout, exits 0 always — non-blocking).

Requires .venv/Scripts/python (PyYAML is in .venv, not stdlib).
"""
import hashlib
import sys
from pathlib import Path

REGISTRY = Path(".supervisor/knowledge/registry.yaml")


def validate_knowledge_freshness(declaration: dict, repo_root: Path | None = None) -> dict:
    """V68: Knowledge contract freshness check (WARN-only, never blocks sprint)."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
    try:
        import yaml
    except ImportError:
        return {"validator": "V68_knowledge_freshness", "result": "PASS",
                "items": ["PyYAML unavailable — skipped"], "summary": "SKIPPED (no yaml)",
                "blocks_sprint": False}

    reg_path = repo_root / REGISTRY
    if not reg_path.exists():
        return {"validator": "V68_knowledge_freshness", "result": "PASS",
                "items": ["registry.yaml not found — skipped"], "summary": "SKIPPED (no registry)",
                "blocks_sprint": False}

    try:
        registry = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"validator": "V68_knowledge_freshness", "result": "WARN",
                "items": [f"Registry parse error: {exc}"], "summary": "WARN: registry parse failed",
                "blocks_sprint": False}

    stale = []
    checked = []
    for meta in registry.get("contracts", []):
        cid = meta["contract_id"]
        status = meta.get("status", "")
        if status != "VERIFIED_CURRENT":
            continue  # DRAFT → silent skip
        cpath = repo_root / Path(meta["path"])
        try:
            contract = yaml.safe_load(cpath.read_text(encoding="utf-8"))
        except Exception as exc:
            stale.append(f"{cid} CONTRACT_UNREADABLE: {exc}")
            continue
        for entry in contract.get("source_hashes", []):
            src = repo_root / Path(entry["path"])
            if not src.exists():
                stale.append(f"{cid} MISSING_SOURCE: {entry['path']}")
                continue
            actual = hashlib.sha256(src.read_bytes()).hexdigest()
            if actual != entry["sha256"]:
                stale.append(f"{cid} STALE: hash diverged for {entry['path']}")
            else:
                checked.append(f"{cid} VERIFIED_CURRENT ({entry['path']})")

    if stale:
        return {"validator": "V68_knowledge_freshness", "result": "WARN",
                "items": stale, "summary": f"WARN: {len(stale)} stale/missing source(s)",
                "blocks_sprint": False}
    return {"validator": "V68_knowledge_freshness", "result": "PASS",
            "items": checked, "summary": f"PASS: {len(checked)} source hash(es) verified",
            "blocks_sprint": False}


if __name__ == "__main__":
    # Standalone CLI: non-blocking, exit 0 always
    repo_root = Path(__file__).resolve().parents[2]
    result = validate_knowledge_freshness({}, repo_root)
    label = "KNOWLEDGE FRESHNESS"
    if result["result"] == "WARN":
        print(f"WARNING: {label}: {result['summary']}")
        for item in result["items"]:
            print(f"  - {item}")
    else:
        print(f"{label}: {result['summary']}")
    sys.exit(0)  # Never block — always exit 0
