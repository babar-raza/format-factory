"""Governance validators V232-V241, V247-V248 — Format Contract Layer (L30).

Portfolio-wide enforcement over shared/format-contracts/*.yaml, wrapping the
L30 check engine (tools/format_contract/contract_validator.py). Registered in
registry/governance/validator-id-authority.yaml; counted in
governance_validator_runner._EXPECTED_VALIDATOR_COUNT.

Mission FCL-MACHINERY-2026-07-16 (plans/layers/format-contract-layer.md §21).

V247/V248 (plans/.claude/investigate-and-plan-a-snuggly-grove.md Changes 2 and 3)
correlate the two independent format-maturity views — spec coverage (Gate 9) and
contract reconciliation — which no earlier validator compared at any level.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from governance_validators_contract import validator

_FC_TOOLS = Path(__file__).resolve().parent.parent / "format_contract"
if str(_FC_TOOLS) not in sys.path:
    sys.path.insert(0, str(_FC_TOOLS))

# Non-contract YAML files that live in shared/format-contracts/ alongside the
# compiler-generated {fmt}.yaml contracts. _contracts() MUST exclude these: every
# file it returns is fed to the L30 schema check (V232), recompiled (V238/V239)
# and byte-compared against compiler output (V240), so a stray hand-authored YAML
# here would hard-FAIL and block sprints under a format_id that does not exist.
_NON_CONTRACT_YAML = frozenset({"coverage-capability-xref.yaml"})

_XREF_RELPATH = "shared/format-contracts/coverage-capability-xref.yaml"


def _contracts(repo_root: Path) -> list[Path]:
    root = Path(repo_root) / "shared" / "format-contracts"
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.glob("*.yaml")
        if p.is_file() and p.name not in _NON_CONTRACT_YAML
    )


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


# ─────────────────────────────────────────────────────────────────────────────
# V247 / V248 — coverage-to-contract coherence (Changes 2 and 3)
# ─────────────────────────────────────────────────────────────────────────────

_DONE_STATUSES = frozenset({"TESTED", "ORACLE_PROVEN"})


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _coverage_report(repo: Path, fmt: str) -> dict | None:
    return _load_json(repo / "reports" / "spec-coverage" / f"{fmt}-coverage-report.json")


def _reconciliation(repo: Path, fmt: str) -> dict | None:
    return _load_json(repo / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json")


def _feature_manifest(repo: Path, fmt: str) -> dict | None:
    return _load_json(repo / "reports" / "spec-coverage" / "manifests" / f"{fmt}-feature-manifest.json")


def _load_xref(repo: Path) -> dict | None:
    """Load the hand-curated coverage/capability cross-reference, or None."""
    from canonical_io import load_yaml

    path = repo / _XREF_RELPATH
    if not path.is_file():
        return None
    try:
        return load_yaml(path) or None
    except Exception:  # noqa: BLE001
        return None


def _dual_system_formats(repo: Path) -> list[str]:
    """Formats carrying BOTH a compiled contract and a spec-coverage report.

    Only these have two maturity views to compare. safetensors currently has a
    coverage report but no contract, so it is not dual-system and V247 skips it.
    """
    out = []
    for path in _contracts(repo):
        fmt = path.stem
        if (repo / "reports" / "spec-coverage" / f"{fmt}-coverage-report.json").is_file():
            out.append(fmt)
    return sorted(out)


def _xref_for(xref: dict | None, fmt: str) -> dict:
    if not xref:
        return {}
    return (xref.get("formats") or {}).get(fmt) or {}


# Rule A gate outcomes. FIRE_* produce WARN items; SUPPRESS_* are counted into a
# per-format INFO item so the suppression is auditable rather than invisible.
_GATE_FIRE_EVIDENCED = "evidenced"
_GATE_FIRE_XREF_UNAVAILABLE = "xref_unavailable"
_GATE_FIRE_CAP_NOT_IN_XREF = "capability_not_in_xref"
_GATE_SUPPRESS_NO_MAPPED = "no_mapped_coverage"
_GATE_SUPPRESS_NOT_IMPLEMENTED = "mapped_coverage_not_implemented"


def _gate_capability(section: dict, cap_id: str, cov_status: dict) -> dict:
    """Decide whether an unstarted MUST capability really contradicts Gate 9.

    Rule A's bare premise — gate_9_eligible AND a MUST capability at NOT_STARTED —
    was measured firing on 6/6 dual-system formats (20 items: 85% vacuous, 5%
    logically inverted). It is not a contradiction detector without this gate,
    because Gate 9 eligibility only says something about a capability when some
    coverage feature actually maps to it AND claims to be IMPLEMENTED.

    Fires only on real evidence conflict; degrades toward firing (never toward
    silence) whenever the xref cannot answer the question.
    """
    if not section:
        return {
            "decision": "FIRE",
            "xref_gate": _GATE_FIRE_XREF_UNAVAILABLE,
            "mapped_coverage_items": [],
            "interpretation": (
                "no curated xref section for this format, so whether Gate 9 claims "
                "anything about this capability is unknown — falling back to unguarded "
                "Rule A rather than hiding a possible gap behind a missing file"
            ),
        }
    mapped = [
        m.get("coverage_id") for m in (section.get("mappings") or [])
        if cap_id in (m.get("capability_ids") or [])
    ]
    if not mapped:
        if cap_id in (section.get("unmapped_capabilities") or []):
            return {
                "decision": "SUPPRESS",
                "xref_gate": _GATE_SUPPRESS_NO_MAPPED,
                "mapped_coverage_items": [],
                "interpretation": (
                    "no coverage feature enumerates this capability (declared unmapped), "
                    "so Gate 9 eligibility asserts nothing about it — an unstarted "
                    "capability here is ordinary outstanding work, not a contradiction"
                ),
            }
        return {
            "decision": "FIRE",
            "xref_gate": _GATE_FIRE_CAP_NOT_IN_XREF,
            "mapped_coverage_items": [],
            "interpretation": (
                "capability is absent from the xref entirely (V248 reports it as "
                "orphaned), so coverage evidence is unknown — Rule A falls back to "
                "firing rather than assuming no claim exists"
            ),
        }
    items = [{"feature_id": c, "status": cov_status.get(c, "UNKNOWN")} for c in mapped]
    implemented = [i for i in items if i["status"] == "IMPLEMENTED"]
    if not implemented:
        return {
            "decision": "SUPPRESS",
            "xref_gate": _GATE_SUPPRESS_NOT_IMPLEMENTED,
            "mapped_coverage_items": items,
            "interpretation": (
                "no mapped coverage feature is IMPLEMENTED — both systems agree this "
                "work is outstanding, and agreement is not a contradiction"
            ),
        }
    if len(implemented) == len(items):
        interp = (
            "every mapped coverage feature is IMPLEMENTED while the capability is "
            "NOT_STARTED — the gap is capability depth, not spec-feature absence"
        )
    else:
        interp = (
            "some mapped coverage features are IMPLEMENTED while the capability is "
            "NOT_STARTED — Gate 9 claims evidence the capability does not reflect"
        )
    return {
        "decision": "FIRE",
        "xref_gate": _GATE_FIRE_EVIDENCED,
        "mapped_coverage_items": items,
        "interpretation": interp,
    }


def _rule_a(fmt: str, cov: dict, rec: dict, section: dict) -> list[dict]:
    """Gate-9-eligible but MUST capabilities unstarted, gated on xref evidence (WARN).

    Emits one WARN per capability that survives the gate, plus at most one INFO
    item recording every capability the gate suppressed and why.
    """
    if not cov.get("gate_9_eligible"):
        return []
    unstarted = [
        c for c in (rec.get("capabilities") or [])
        if c.get("level") == "MUST" and c.get("observed_status") == "NOT_STARTED"
    ]
    if not unstarted:
        return []

    cov_items = cov.get("items") or []
    cov_status = {i.get("feature_id"): i.get("status") for i in cov_items}
    missing_deferred, missing_undeferred = [], []
    for i in cov_items:
        if i.get("status") != "MISSING" or i.get("requirement_level") != "mandatory":
            continue
        entry = {"feature_id": i.get("feature_id"), "name": i.get("name")}
        if i.get("deferred_reason"):
            missing_deferred.append({**entry, "deferred_reason": i["deferred_reason"]})
        else:
            missing_undeferred.append(entry)
    summary = cov.get("coverage_summary") or {}
    context = {
        "total_features": summary.get("total"),
        "implemented": summary.get("implemented"),
        "missing_with_deferral": missing_deferred,
        "missing_without_deferral": missing_undeferred,
    }

    out: list[dict] = []
    suppressed: list[dict] = []
    for c in unstarted:
        cap_id = c.get("capability_id")
        gate = _gate_capability(section, cap_id, cov_status)
        if gate["decision"] == "SUPPRESS":
            suppressed.append({
                "capability_id": cap_id,
                "level": c.get("level"),
                "category": c.get("category"),
                "reason": gate["xref_gate"],
                "mapped_coverage_items": gate["mapped_coverage_items"],
                "interpretation": gate["interpretation"],
            })
            continue
        out.append({
            "format": fmt,
            "rule": "A",
            "severity": "WARN",
            "capability_id": cap_id,
            "level": c.get("level"),
            "category": c.get("category"),
            "observed_status": c.get("observed_status"),
            "gate_9_eligible": True,
            "coverage_context": context,
            "xref_gate": gate["xref_gate"],
            "mapped_coverage_items": gate["mapped_coverage_items"],
            "interpretation": gate["interpretation"],
        })

    if suppressed:
        counts: dict[str, int] = {}
        for s in suppressed:
            counts[s["reason"]] = counts.get(s["reason"], 0) + 1
        out.append({
            "format": fmt,
            "rule": "A-suppressed",
            "severity": "INFO",
            "detail": (
                f"{len(suppressed)} unstarted MUST capabilities are NOT coherence "
                "contradictions: no Gate 9 claim bears on them"
            ),
            "counts": counts,
            "suppressed": suppressed,
        })
    return out


def _rule_b(fmt: str, cov: dict, rec: dict) -> list[dict]:
    """Reconciliation fully TESTED but mandatory coverage MISSING undeferred (WARN)."""
    musts = [c for c in (rec.get("capabilities") or []) if c.get("level") == "MUST"]
    if not musts or not all(c.get("observed_status") in _DONE_STATUSES for c in musts):
        return []
    undeferred = [
        {"feature_id": i.get("feature_id"), "name": i.get("name"),
         "requirement_level": i.get("requirement_level"), "status": i.get("status")}
        for i in (cov.get("items") or [])
        if i.get("status") == "MISSING"
        and i.get("requirement_level") == "mandatory"
        and not i.get("deferred_reason")
    ]
    if not undeferred:
        return []
    return [{
        "format": fmt,
        "rule": "B",
        "severity": "WARN",
        "undeferred_missing": undeferred,
        "reconciliation_summary": (rec.get("summary") or {}).get("by_status", {}),
    }]


def _rule_c(repo: Path, fmt: str, cov: dict) -> list[dict]:
    """Coverage manifest refreshed after the last reconciliation run (INFO).

    Deviation from the plan text, which proposed comparing the reconciliation's
    contract_input_digests against the coverage report's manifest_hash. Those are
    disjoint hash spaces — contract_input_digests are SHA-256s of the SAL fact /
    family-pack / QName / research / shared-contract stores, while manifest_hash
    digests the feature manifest — so equality is not merely false, it is
    undefined, and the check would fire on every format forever. This implements
    the plan's verification item 8 instead ("coverage manifest modification time >
    reconciliation modification time"), which is the coherent statement of the same
    intent: the reconciliation may predate current spec-feature expectations.

    Known limit: mtime is checkout-relative, so a fresh clone rewrites all mtimes
    to clone time and this rule silently stops firing. It is INFO precisely because
    the signal is weak; it never affects the validator verdict.
    """
    man = repo / "reports" / "spec-coverage" / "manifests" / f"{fmt}-feature-manifest.json"
    rec_path = repo / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json"
    if not man.is_file() or not rec_path.is_file():
        return []
    man_mtime, rec_mtime = man.stat().st_mtime, rec_path.stat().st_mtime
    if man_mtime <= rec_mtime:
        return []
    return [{
        "format": fmt,
        "rule": "C",
        "severity": "INFO",
        "detail": "Coverage manifest updated since last reconciliation",
        "manifest_hash": cov.get("manifest_hash"),
        "reconciliation_age_days": int((time.time() - rec_mtime) // 86400),
    }]


@validator(rule_id="V247", domain="format_contract",
           description="Format-level coverage/contract coherence with per-item diagnostics",
           skill_ids=["reconcile-contract-capabilities"])
def validate_format_coherence(declaration: dict, repo_root: Path) -> dict:
    """Correlate Gate 9 coverage status with contract reconciliation status.

    WARN-only by design: the two systems decompose a format along different axes
    (spec construct vs. architectural concern), so a disagreement is a diagnostic
    signal for an operator, not proof of a defect. Formats without both views are
    skipped, so retiring either system degrades this to PASS rather than breaking it.

    Rule A is gated on curated xref evidence, and the gate is the rule. Measured on
    2026-07-17, the unguarded premise (gate_9_eligible AND a MUST capability at
    NOT_STARTED) fired on 6/6 dual-system formats — 20 items, of which 17 (85%) were
    vacuous (no coverage feature maps to the capability at all, so Gate 9 never made
    a claim about it) and 1 (5%) was logically inverted (the mapped feature was
    MISSING and the capability NOT_STARTED, i.e. the two systems AGREED, reported as
    a contradiction). A rule that fires on every format has no discriminating power,
    and the plan that specified this validator rejected its own substring-matching
    alternative for exactly that reason: "more noise than signal — worse than having
    no bridge at all, because it creates false confidence".

    So Rule A fires only when Gate 9 actually claims something the capability
    contradicts: >=1 coverage feature maps to the capability AND >=1 of those is
    IMPLEMENTED. Suppressed capabilities are not discarded — they are reported as an
    INFO "A-suppressed" item per format, with per-capability reasons, so the
    suppression is auditable.

    Degradation is one-directional: when the xref cannot answer (absent for the
    format, or the capability is orphaned from it), Rule A falls back to firing
    unguarded and stamps xref_gate so the item is recognisable. A missing file must
    never silence a real gap.
    """
    repo = Path(repo_root)
    xref = _load_xref(repo)
    items: list[dict] = []
    checked = 0
    for fmt in _dual_system_formats(repo):
        cov, rec = _coverage_report(repo, fmt), _reconciliation(repo, fmt)
        if not cov or not rec:
            continue
        checked += 1
        section = _xref_for(xref, fmt)
        items.extend(_rule_a(fmt, cov, rec, section))
        items.extend(_rule_b(fmt, cov, rec))
        items.extend(_rule_c(repo, fmt, cov))

    if not checked:
        return _result("validate_format_coherence", "PASS", [],
                       "no formats carry both a coverage report and a reconciliation", False)
    actionable = [i for i in items if i.get("severity") == "WARN"]
    info = [i for i in items if i.get("severity") == "INFO"]
    # INFO items never change the verdict — the runner only counts PASS/WARN/FAIL,
    # so an "INFO" result string would vanish from every count.
    result = "WARN" if actionable else "PASS"
    by_rule = {r: sum(1 for i in items if i.get("rule") == r) for r in ("A", "B", "C")}
    degraded = sum(1 for i in actionable
                   if i.get("xref_gate") in (_GATE_FIRE_XREF_UNAVAILABLE,
                                             _GATE_FIRE_CAP_NOT_IN_XREF))
    suppressed = sum(len(i.get("suppressed", [])) for i in items
                     if i.get("rule") == "A-suppressed")
    return _result(
        "validate_format_coherence", result, items,
        f"coherence over {checked} dual-system formats: "
        f"{len(actionable)} WARN + {len(info)} INFO "
        f"(rule A={by_rule['A']}, B={by_rule['B']}, C={by_rule['C']}; "
        f"{suppressed} rule-A capabilities suppressed as non-contradictions, "
        f"{degraded} fired ungated due to missing xref evidence)",
        False,
    )


def _xref_format_items(repo: Path, fmt: str, section: dict) -> tuple[list[dict], list[dict]]:
    """Referential (FAIL) and completeness (WARN) findings for one xref section."""
    fails: list[dict] = []
    warns: list[dict] = []
    man = _feature_manifest(repo, fmt)
    contract_path = repo / "shared" / "format-contracts" / f"{fmt}.yaml"
    if not man or not contract_path.is_file():
        fails.append({
            "format": fmt, "kind": "referential",
            "issue": "xref names a format without both a feature manifest and a contract "
                     f"(manifest={'yes' if man else 'no'}, "
                     f"contract={'yes' if contract_path.is_file() else 'no'})",
        })
        return fails, warns

    from canonical_io import load_yaml
    features = {f.get("feature_id") for f in (man.get("features") or [])}
    contract = load_yaml(contract_path) or {}
    caps = {c.get("capability_id") for c in (contract.get("capabilities") or [])}

    mappings = section.get("mappings") or []
    unmapped_cov = list(section.get("unmapped_coverage") or [])
    unmapped_cap = list(section.get("unmapped_capabilities") or [])
    mapped_cov = [m.get("coverage_id") for m in mappings]
    mapped_cap = [c for m in mappings for c in (m.get("capability_ids") or [])]

    for cid in mapped_cov + unmapped_cov:
        if cid not in features:
            fails.append({"format": fmt, "kind": "referential",
                          "issue": f"coverage_id not found in feature manifest: {cid}"})
    for cid in mapped_cap + unmapped_cap:
        if cid not in caps:
            fails.append({"format": fmt, "kind": "referential",
                          "issue": f"capability_id not found in compiled contract: {cid}"})
    for m in mappings:
        if not (m.get("rationale") or "").strip():
            fails.append({"format": fmt, "kind": "referential",
                          "issue": f"mapping {m.get('coverage_id')} has no rationale "
                                   "(the xref's only defence against a wrong mapping)"})

    for cid in sorted(features - set(mapped_cov) - set(unmapped_cov)):
        warns.append({"format": fmt, "kind": "completeness",
                      "issue": f"orphaned coverage item — add to mappings or unmapped_coverage: {cid}"})
    for cid in sorted(caps - set(mapped_cap) - set(unmapped_cap)):
        warns.append({"format": fmt, "kind": "completeness",
                      "issue": f"orphaned capability — add to a mapping or unmapped_capabilities: {cid}"})
    for cid in sorted(set(mapped_cov) & set(unmapped_cov)):
        warns.append({"format": fmt, "kind": "completeness",
                      "issue": f"coverage item is both mapped and declared unmapped: {cid}"})
    for cid in sorted(set(mapped_cap) & set(unmapped_cap)):
        warns.append({"format": fmt, "kind": "completeness",
                      "issue": f"capability is both mapped and declared unmapped: {cid}"})
    return fails, warns


@validator(rule_id="V248", domain="format_contract",
           description="Coverage-capability cross-reference integrity (referential + completeness)",
           skill_ids=["reconcile-contract-capabilities"])
def validate_coverage_xref_integrity(declaration: dict, repo_root: Path) -> dict:
    """Keep the hand-curated xref honest as coverage items and capabilities change.

    FAIL on referential violations (an ID that resolves to nothing, or a mapping with
    no rationale). WARN on completeness violations (an item in neither the mappings
    nor the unmapped list). The plan states both "FAILs until the xref is updated" for
    new items and "WARN for completeness violations"; a newly added item IS a
    completeness violation, so the narrower rule wins and new items WARN.

    V248 cannot detect a semantically wrong mapping — only a structurally broken one.
    The rationale field exists so that a human review can catch the rest.
    """
    repo = Path(repo_root)
    dual = _dual_system_formats(repo)
    if not dual:
        return _result("validate_coverage_xref_integrity", "PASS", [],
                       "no dual-system formats — xref not required", False)
    xref = _load_xref(repo)
    if xref is None:
        return _result("validate_coverage_xref_integrity", "WARN",
                       [{"issue": f"missing or unreadable: {_XREF_RELPATH}",
                         "dual_system_formats": dual}],
                       f"xref absent while {len(dual)} dual-system formats exist", False)

    sections = xref.get("formats") or {}
    fails: list[dict] = []
    warns: list[dict] = []
    for fmt, section in sorted(sections.items()):
        f, w = _xref_format_items(repo, fmt, section or {})
        fails.extend(f)
        warns.extend(w)
    for fmt in dual:
        if fmt not in sections:
            warns.append({"format": fmt, "kind": "completeness",
                          "issue": "dual-system format missing from the xref"})

    items = fails + warns
    result = "FAIL" if fails else ("WARN" if warns else "PASS")
    return _result(
        "validate_coverage_xref_integrity", result, items,
        f"xref integrity over {len(sections)} mapped formats "
        f"({len(dual)} dual-system): {len(fails)} referential, {len(warns)} completeness",
        True,
    )
