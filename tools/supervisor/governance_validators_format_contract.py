"""Governance validators V232-V241 — Format Contract Layer (L30).

Portfolio-wide enforcement over shared/format-contracts/*.yaml, wrapping the
L30 check engine (tools/format_contract/contract_validator.py). Registered in
registry/governance/validator-id-authority.yaml; counted in
governance_validator_runner._EXPECTED_VALIDATOR_COUNT.

Mission FCL-MACHINERY-2026-07-16 (plans/layers/format-contract-layer.md §21).
"""

from __future__ import annotations

import sys
from pathlib import Path

from governance_validators_contract import validator

_FC_TOOLS = Path(__file__).resolve().parent.parent / "format_contract"
if str(_FC_TOOLS) not in sys.path:
    sys.path.insert(0, str(_FC_TOOLS))


def _contracts(repo_root: Path) -> list[Path]:
    root = Path(repo_root) / "shared" / "format-contracts"
    if not root.is_dir():
        return []
    return sorted(p for p in root.glob("*.yaml") if p.is_file())


def _result(name: str, result: str, items: list, summary: str, blocks: bool) -> dict:
    return {"validator": name, "result": result, "items": items,
            "summary": summary, "blocks_sprint": blocks and result == "FAIL"}


def _run_check(repo_root: Path, name: str, check_name: str, blocks: bool = True) -> dict:
    """Run one L30 check function across every committed contract."""
    import contract_validator as cv
    from canonical_io import load_yaml

    check_fn = getattr(cv, f"check_{check_name}")
    items = []
    for path in _contracts(repo_root):
        doc = load_yaml(path)
        if not doc:
            items.append({"contract": path.name, "issue": "unreadable/empty"})
            continue
        try:
            res = check_fn(doc)
        except Exception as exc:  # noqa: BLE001
            items.append({"contract": path.name, "issue": f"check error: {exc}"})
            continue
        if res["result"] != "PASS":
            items.append({"contract": path.name, "failures": res["items"][:5]})
    if not _contracts(repo_root):
        return _result(name, "PASS", [], "no contracts present (layer bootstrapping)", blocks)
    result = "PASS" if not items else "FAIL"
    return _result(name, result, items,
                   f"{check_name} over {len(_contracts(repo_root))} contracts: "
                   f"{len(items)} failing", blocks)


@validator(rule_id="V232", domain="format_contract",
           description="Every committed format contract validates against the L30 JSON schema",
           skill_ids=["compile-format-contract", "validate-format-contract"])
def validate_contract_schema(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_schema", "schema")


@validator(rule_id="V233", domain="format_contract",
           description="Every contract capability cites resolvable SAL-/RF-/POL- provenance IDs",
           skill_ids=["compile-format-contract", "validate-format-contract"])
def validate_contract_provenance(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_provenance", "provenance")


@validator(rule_id="V234", domain="format_contract",
           description="Every contract capability declares depth_required + rationale at/above family floor",
           skill_ids=["validate-format-contract"])
def validate_contract_depth(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_depth", "depth")


@validator(rule_id="V235", domain="format_contract",
           description="No unexpanded shallow/generic requirement language in contracts",
           skill_ids=["validate-format-contract"])
def validate_contract_shallow_language(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_shallow_language", "shallow_language")


@validator(rule_id="V236", domain="format_contract",
           description="Contract capability IDs are well-formed and unique",
           skill_ids=["validate-format-contract"])
def validate_contract_capability_ids(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_capability_ids", "duplicate_ids")


@validator(rule_id="V237", domain="format_contract",
           description="Every MUST contract capability carries tests and release gates",
           skill_ids=["validate-format-contract"])
def validate_contract_test_gate(declaration: dict, repo_root: Path) -> dict:
    return _run_check(repo_root, "validate_contract_test_gate", "test_gate")


def _drift_comparable(doc: dict) -> dict:
    """Strip fields that legitimately differ on every staleness (input_digests are
    recorded in the body by design) so drift comparison reflects substantive content,
    not the digest mismatch that staleness itself already reports."""
    import copy

    stripped = copy.deepcopy(doc)
    stripped.get("contract_metadata", {}).pop("input_digests", None)
    return stripped


@validator(rule_id="V238", domain="format_contract",
           description="Contract input_digests match current committed stores (freshness + drift)",
           skill_ids=["refresh-format-contract"])
def validate_contract_freshness(declaration: dict, repo_root: Path) -> dict:
    import contract_validator as cv
    from canonical_io import canonical_dump, load_yaml

    items = []
    stale_only: list[str] = []
    drifted: list[str] = []
    for path in _contracts(repo_root):
        fmt = path.stem
        doc = load_yaml(path)
        if not doc:
            continue
        if cv.check_freshness(doc)["result"] == "PASS":
            continue
        try:
            import contract_compiler as cc
            _, recompiled = cc.compile_contract(fmt)
        except Exception:  # noqa: BLE001
            stale_only.append(fmt)
            items.append({"contract": path.name, "issue": "stale (recompile failed)"})
            continue
        if not recompiled:
            stale_only.append(fmt)
            items.append({"contract": path.name, "issue": "stale (readiness-blocked)"})
            continue
        if canonical_dump(_drift_comparable(doc)) != canonical_dump(_drift_comparable(recompiled)):
            drifted.append(fmt)
            items.append({"contract": path.name, "issue": "DRIFTED — recompilation differs from committed"})
        else:
            stale_only.append(fmt)
            items.append({"contract": path.name, "issue": "stale digests but content unchanged"})

    if drifted:
        return _result("validate_contract_freshness", "FAIL", items,
                        f"{len(drifted)} contracts drifted (recompilation differs): "
                        f"{', '.join(drifted)}; {len(stale_only)} stale-only", True)
    if stale_only:
        res = _result("validate_contract_freshness", "WARN", items,
                       f"{len(stale_only)} contracts stale but content unchanged", False)
        res["result"] = "WARN"
        return res
    return _result("validate_contract_freshness", "PASS", [],
                    "all contracts fresh", False)


@validator(rule_id="V239", domain="format_contract",
           description="Contract compilation is deterministic (two in-memory compiles byte-equal)",
           skill_ids=["compile-format-contract"])
def validate_contract_determinism(declaration: dict, repo_root: Path) -> dict:
    import contract_compiler as cc
    from canonical_io import canonical_dump

    items = []
    checked = 0
    for path in _contracts(repo_root):
        fmt = path.stem
        try:
            _, d1 = cc.compile_contract(fmt)
            _, d2 = cc.compile_contract(fmt)
        except Exception as exc:  # noqa: BLE001
            items.append({"contract": path.name, "issue": f"recompile error: {exc}"})
            continue
        if not d1:
            continue  # readiness-blocked now; staleness is V238's concern
        checked += 1
        if canonical_dump(d1) != canonical_dump(d2):
            items.append({"contract": path.name, "issue": "two compilations differ"})
    result = "PASS" if not items else "FAIL"
    return _result("validate_contract_determinism", result, items,
                   f"determinism verified for {checked} compilable contracts", True)


@validator(rule_id="V240", domain="format_contract",
           description="Hand-edit guard: committed contract body must equal recompiled output when input digests are current",
           skill_ids=["compile-format-contract"])
def validate_contract_hand_edit_guard(declaration: dict, repo_root: Path) -> dict:
    import contract_compiler as cc
    import contract_validator as cv
    from canonical_io import canonical_dump, load_yaml

    items = []
    for path in _contracts(repo_root):
        fmt = path.stem
        doc = load_yaml(path)
        if not doc:
            continue
        fresh = cv.check_freshness(doc)["result"] == "PASS"
        if not fresh:
            continue  # stale inputs are V238's WARN, not a hand-edit
        try:
            _, recompiled = cc.compile_contract(fmt)
        except Exception:  # noqa: BLE001
            continue
        if not recompiled:
            continue
        committed = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if committed != canonical_dump(recompiled):
            items.append({
                "contract": path.name,
                "issue": "body differs from recompilation while input digests are current — "
                         "hand-edited contract body (contracts are compiler-generated only)",
            })
    result = "PASS" if not items else "FAIL"
    return _result("validate_contract_hand_edit_guard", result, items,
                   "hand-edit guard over fresh contracts", True)


@validator(rule_id="V241", domain="format_contract",
           description="Consumption: formats with contract + product source have reconciliation output (WARN)",
           skill_ids=["reconcile-contract-capabilities", "compile-contract-gaps"])
def validate_contract_consumption(declaration: dict, repo_root: Path) -> dict:
    repo = Path(repo_root)
    items = []
    for path in _contracts(repo):
        fmt = path.stem
        if not (repo / "src" / "python" / fmt).is_dir():
            continue
        recon = repo / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json"
        if not recon.is_file():
            items.append({"contract": path.name,
                          "issue": "no reconciliation report (run /reconcile-contract-capabilities)"})
    result = "PASS" if not items else "WARN"
    return _result("validate_contract_consumption", result, items,
                   "contract-to-implementation reconciliation coverage", False)
