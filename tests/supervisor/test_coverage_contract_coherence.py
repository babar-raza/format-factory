"""Tests for V247 (format coherence) and V248 (coverage/capability xref integrity).

Covers the verification plan of plans/.claude/investigate-and-plan-a-snuggly-grove.md
(Changes 2 and 3, items 6-14), plus two structural regressions the plan did not
anticipate:

  - test_xref_is_not_treated_as_a_contract: the xref lives in shared/format-contracts/,
    which _contracts() globs as *.yaml. Without an exclusion, V232/V238/V239/V240 would
    schema-check, recompile and byte-compare the xref as if it were a compiled contract
    for a format named "coverage-capability-xref", hard-FAILing and blocking sprints.
  - test_v247_v248_are_dispatched_by_the_runner: dispatch is explicit-only since
    TC-GVD-001 deleted the blind registry fallback, so a @validator decorator alone
    would leave these silently never executed.

Fixture strategy: synthetic repos under tmp_path for rule behaviour (hermetic, fast,
independent of portfolio drift), real repo data for the clean-state assertions.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from governance_validators_format_contract import (  # noqa: E402
    _contracts,
    validate_coverage_xref_integrity,
    validate_format_coherence,
)

XREF_PATH = REPO_ROOT / "shared" / "format-contracts" / "coverage-capability-xref.yaml"


# ---------------------------------------------------------------------------
# Synthetic repo builders
# ---------------------------------------------------------------------------

def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _mkrepo(
    tmp_path: Path,
    fmt: str = "zz",
    *,
    gate_9_eligible: bool = True,
    coverage_items: list | None = None,
    capabilities: list | None = None,
    xref: dict | None = None,
    with_coverage: bool = True,
) -> Path:
    """Build a minimal repo with the four files V247/V248 read."""
    repo = tmp_path
    caps = capabilities if capabilities is not None else [
        {"capability_id": f"{fmt.upper()}-PARSE-001", "level": "MUST", "category": "parse",
         "observed_status": "TESTED", "product_symbols": ["load"]},
    ]
    items = coverage_items if coverage_items is not None else [
        {"feature_id": f"FACT-{fmt.upper()}-101", "name": "Feature one",
         "requirement_level": "mandatory", "status": "IMPLEMENTED", "deferred_reason": None},
    ]

    # Compiled contract (capability_id/level/category are the fields V248 reads).
    _write(repo / "shared" / "format-contracts" / f"{fmt}.yaml", {
        "contract_metadata": {"contract_id": f"{fmt}-contract"},
        "capabilities": [
            {k: c[k] for k in ("capability_id", "level", "category") if k in c}
            for c in caps
        ],
    })
    # Reconciliation (observed_status lives here, not in the contract).
    _write(repo / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json", {
        "format_id": fmt,
        "capabilities": caps,
        "summary": {"total": len(caps), "by_status": {}},
    })
    if with_coverage:
        _write(repo / "reports" / "spec-coverage" / f"{fmt}-coverage-report.json", {
            "format_id": fmt,
            "gate_9_eligible": gate_9_eligible,
            "manifest_hash": "sha256:deadbeef",
            "coverage_summary": {
                "total": len(items),
                "implemented": sum(1 for i in items if i["status"] == "IMPLEMENTED"),
                "missing": sum(1 for i in items if i["status"] == "MISSING"),
            },
            "items": items,
        })
        _write(repo / "reports" / "spec-coverage" / "manifests" / f"{fmt}-feature-manifest.json", {
            "format_id": fmt,
            "features": [
                {"feature_id": i["feature_id"], "name": i["name"],
                 "requirement_level": i["requirement_level"]}
                for i in items
            ],
        })
    if xref is not None:
        _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)

    # Normalize mtimes to real pipeline order: the feature manifest is authored first,
    # the reconciliation is generated from the contract afterwards. Without this the
    # builder's own write order (manifest last) leaves the manifest a few milliseconds
    # newer and Rule C fires with reconciliation_age_days=0 in every fixture — an
    # artifact of the test, not a finding. Rule C tests set their own mtimes.
    if with_coverage:
        man = repo / "reports" / "spec-coverage" / "manifests" / f"{fmt}-feature-manifest.json"
        rec = repo / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json"
        now = time.time()
        os.utime(man, (now - 60, now - 60))
        os.utime(rec, (now, now))
    return repo


def _full_xref(fmt: str, mappings: list, unmapped_cov: list, unmapped_cap: list) -> dict:
    return {
        "schema_version": "1.0",
        "formats": {fmt: {
            "mappings": mappings,
            "unmapped_coverage": unmapped_cov,
            "unmapped_capabilities": unmapped_cap,
        }},
    }


# ---------------------------------------------------------------------------
# V247 — verification items 6-11
# ---------------------------------------------------------------------------

def test_rule_a_gate9_eligible_with_unstarted_must_capability(tmp_path):
    """Item 6: gate_9_eligible + MUST at NOT_STARTED -> WARN w/ deferral context.

    No xref here, so Rule A fires via the ungated fallback path.
    """
    repo = _mkrepo(
        tmp_path, "qq",
        capabilities=[
            {"capability_id": "QQ-PRESERVE-001", "level": "MUST", "category": "preserve",
             "observed_status": "NOT_STARTED", "product_symbols": []},
        ],
        coverage_items=[
            {"feature_id": "FACT-QQ-101", "name": "Decode", "requirement_level": "mandatory",
             "status": "IMPLEMENTED", "deferred_reason": None},
            {"feature_id": "FACT-QQ-104", "name": "Streaming decode",
             "requirement_level": "mandatory", "status": "MISSING",
             "deferred_reason": "Out of scope for this pass"},
        ],
    )
    res = validate_format_coherence({}, repo)
    assert res["result"] == "WARN"
    assert res["blocks_sprint"] is False, "V247 is diagnostic; it must never block a sprint"
    a = [i for i in res["items"] if i["rule"] == "A"]
    assert len(a) == 1
    item = a[0]
    assert item["capability_id"] == "QQ-PRESERVE-001"
    assert item["gate_9_eligible"] is True
    deferred = item["coverage_context"]["missing_with_deferral"]
    assert [d["feature_id"] for d in deferred] == ["FACT-QQ-104"]
    assert deferred[0]["deferred_reason"] == "Out of scope for this pass"
    assert item["coverage_context"]["missing_without_deferral"] == []


# ---------------------------------------------------------------------------
# Rule A xref-evidence gate
#
# The unguarded premise fired on 6/6 real formats (85% vacuous, 5% inverted), so
# the gate is what gives Rule A meaning. These pin each branch of it.
# ---------------------------------------------------------------------------

def _gate_repo(tmp_path, *, cap_id, cap_status="NOT_STARTED", feature_status="IMPLEMENTED",
               mapped=True, in_unmapped_caps=False, with_xref=True):
    caps = [{"capability_id": cap_id, "level": "MUST", "category": "transform",
             "observed_status": cap_status}]
    items = [{"feature_id": "FACT-GG-101", "name": "A feature",
              "requirement_level": "mandatory", "status": feature_status,
              "deferred_reason": "deferred" if feature_status == "MISSING" else None}]
    xref = None
    if with_xref:
        xref = _full_xref(
            "gg",
            mappings=([{"coverage_id": "FACT-GG-101", "capability_ids": [cap_id],
                        "rationale": "the feature is evidence for this capability"}]
                      if mapped else []),
            unmapped_cov=([] if mapped else ["FACT-GG-101"]),
            unmapped_cap=([cap_id] if in_unmapped_caps else []),
        )
    return _mkrepo(tmp_path, "gg", capabilities=caps, coverage_items=items, xref=xref)


def test_gate_fires_when_mapped_feature_is_implemented(tmp_path):
    """The real signal: Gate 9 claims the feature is IMPLEMENTED, capability is
    NOT_STARTED -> genuine depth gap."""
    repo = _gate_repo(tmp_path, cap_id="GG-CLEAN-001")
    res = validate_format_coherence({}, repo)
    a = [i for i in res["items"] if i["rule"] == "A"]
    assert len(a) == 1
    assert a[0]["xref_gate"] == "evidenced"
    assert "capability depth" in a[0]["interpretation"]
    assert res["result"] == "WARN"


def test_gate_suppresses_unmapped_capability(tmp_path):
    """Vacuous case (17/20 of real data): nothing maps to the capability, so Gate 9
    eligibility asserts nothing about it. Not a contradiction -> no WARN."""
    repo = _gate_repo(tmp_path, cap_id="GG-SEC-001", mapped=False, in_unmapped_caps=True)
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "A"] == []
    assert res["result"] == "PASS", "a vacuous finding must not produce a WARN verdict"


def test_gate_suppresses_agreement_when_mapped_feature_is_missing(tmp_path):
    """Inverted case (IPYNB-UPGRADE-001 on real data): mapped feature MISSING and
    capability NOT_STARTED means the systems AGREE. Agreement is not a contradiction."""
    repo = _gate_repo(tmp_path, cap_id="GG-UPGRADE-001", feature_status="MISSING")
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "A"] == []
    assert res["result"] == "PASS"


def test_suppressed_capabilities_are_reported_as_auditable_info(tmp_path):
    """Suppression must be visible, not silent."""
    repo = _gate_repo(tmp_path, cap_id="GG-SEC-001", mapped=False, in_unmapped_caps=True)
    res = validate_format_coherence({}, repo)
    sup = [i for i in res["items"] if i["rule"] == "A-suppressed"]
    assert len(sup) == 1
    assert sup[0]["severity"] == "INFO"
    assert sup[0]["counts"] == {"no_mapped_coverage": 1}
    entry = sup[0]["suppressed"][0]
    assert entry["capability_id"] == "GG-SEC-001"
    assert entry["reason"] == "no_mapped_coverage"
    assert "asserts nothing about it" in entry["interpretation"]


def test_gate_falls_back_to_firing_when_xref_absent(tmp_path):
    """Degradation is one-directional: a missing xref must never silence Rule A."""
    repo = _gate_repo(tmp_path, cap_id="GG-SEC-001", with_xref=False)
    res = validate_format_coherence({}, repo)
    a = [i for i in res["items"] if i["rule"] == "A"]
    assert len(a) == 1, "missing xref must fall back to unguarded firing, not go dark"
    assert a[0]["xref_gate"] == "xref_unavailable"
    assert "falling back to unguarded" in a[0]["interpretation"]


def test_gate_falls_back_to_firing_when_capability_orphaned_from_xref(tmp_path):
    """An xref that simply forgot the capability is unknown evidence, not absent
    evidence -> fire and flag (V248 separately WARNs to fix the xref)."""
    repo = _gate_repo(tmp_path, cap_id="GG-SEC-001", mapped=False, in_unmapped_caps=False)
    res = validate_format_coherence({}, repo)
    a = [i for i in res["items"] if i["rule"] == "A"]
    assert len(a) == 1
    assert a[0]["xref_gate"] == "capability_not_in_xref"


def test_gate_fires_on_partial_evidence(tmp_path):
    """>=1 mapped feature IMPLEMENTED is enough to constitute a Gate 9 claim."""
    caps = [{"capability_id": "GG-EDIT-001", "level": "MUST", "category": "edit",
             "observed_status": "NOT_STARTED"}]
    items = [
        {"feature_id": "FACT-GG-101", "name": "done", "requirement_level": "mandatory",
         "status": "IMPLEMENTED", "deferred_reason": None},
        {"feature_id": "FACT-GG-102", "name": "not done", "requirement_level": "optional",
         "status": "MISSING", "deferred_reason": "deferred"},
    ]
    xref = _full_xref(
        "gg",
        mappings=[{"coverage_id": "FACT-GG-101", "capability_ids": ["GG-EDIT-001"],
                   "rationale": "r1"},
                  {"coverage_id": "FACT-GG-102", "capability_ids": ["GG-EDIT-001"],
                   "rationale": "r2"}],
        unmapped_cov=[], unmapped_cap=[],
    )
    repo = _mkrepo(tmp_path, "gg", capabilities=caps, coverage_items=items, xref=xref)
    res = validate_format_coherence({}, repo)
    a = [i for i in res["items"] if i["rule"] == "A"]
    assert len(a) == 1
    assert a[0]["xref_gate"] == "evidenced"
    assert "does not reflect" in a[0]["interpretation"]


def test_rule_a_silent_when_not_gate9_eligible(tmp_path):
    """Rule A is conditioned on gate_9_eligible; an unstarted MUST alone is not a
    contradiction, it is just unfinished work."""
    repo = _mkrepo(
        tmp_path, "qq", gate_9_eligible=False,
        capabilities=[{"capability_id": "QQ-PRESERVE-001", "level": "MUST",
                       "category": "preserve", "observed_status": "NOT_STARTED"}],
    )
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "A"] == []
    assert res["result"] == "PASS"


def test_rule_a_ignores_should_level_capabilities(tmp_path):
    """Only MUST capabilities can contradict Gate 9 eligibility."""
    repo = _mkrepo(
        tmp_path, "qq",
        capabilities=[{"capability_id": "QQ-CONVERT-001", "level": "SHOULD",
                       "category": "transform", "observed_status": "NOT_STARTED"}],
    )
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "A"] == []


def test_rule_b_all_must_tested_but_mandatory_coverage_missing_undeferred(tmp_path):
    """Item 7: all MUST TESTED + mandatory MISSING w/o deferral -> WARN."""
    repo = _mkrepo(
        tmp_path, "bb", gate_9_eligible=False,
        capabilities=[
            {"capability_id": "BB-PARSE-001", "level": "MUST", "category": "parse",
             "observed_status": "TESTED"},
            {"capability_id": "BB-WRITE-001", "level": "MUST", "category": "write",
             "observed_status": "ORACLE_PROVEN"},
        ],
        coverage_items=[
            {"feature_id": "FACT-BB-104", "name": "Write-side party round-trip fix",
             "requirement_level": "mandatory", "status": "MISSING", "deferred_reason": None},
            {"feature_id": "FACT-BB-105", "name": "Deferred thing",
             "requirement_level": "mandatory", "status": "MISSING",
             "deferred_reason": "conscious exclusion"},
            {"feature_id": "FACT-BB-106", "name": "Optional missing",
             "requirement_level": "optional", "status": "MISSING", "deferred_reason": None},
        ],
    )
    res = validate_format_coherence({}, repo)
    assert res["result"] == "WARN"
    b = [i for i in res["items"] if i["rule"] == "B"]
    assert len(b) == 1
    # Only the mandatory, undeferred, missing item — not the deferred one, not the optional one.
    assert [m["feature_id"] for m in b[0]["undeferred_missing"]] == ["FACT-BB-104"]


def test_rule_b_silent_when_any_must_unstarted(tmp_path):
    repo = _mkrepo(
        tmp_path, "bb", gate_9_eligible=False,
        capabilities=[
            {"capability_id": "BB-PARSE-001", "level": "MUST", "category": "parse",
             "observed_status": "TESTED"},
            {"capability_id": "BB-SEC-001", "level": "MUST", "category": "security",
             "observed_status": "NOT_STARTED"},
        ],
        coverage_items=[
            {"feature_id": "FACT-BB-104", "name": "x", "requirement_level": "mandatory",
             "status": "MISSING", "deferred_reason": None},
        ],
    )
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "B"] == []


def test_rule_c_manifest_newer_than_reconciliation_is_info_only(tmp_path):
    """Item 8: manifest mtime > reconciliation mtime -> INFO w/ reconciliation_age_days.

    INFO must not change the verdict: the runner counts PASS/WARN/FAIL only, so an
    "INFO" result string would be invisible to every count.
    """
    repo = _mkrepo(tmp_path, "cc", gate_9_eligible=False)
    rec = repo / "reports" / "format-contract-layer" / "cc-reconciliation.json"
    man = repo / "reports" / "spec-coverage" / "manifests" / "cc-feature-manifest.json"
    old = time.time() - (5 * 86400)
    os.utime(rec, (old, old))
    os.utime(man, (time.time(), time.time()))

    res = validate_format_coherence({}, repo)
    c = [i for i in res["items"] if i["rule"] == "C"]
    assert len(c) == 1
    assert c[0]["severity"] == "INFO"
    assert c[0]["reconciliation_age_days"] >= 4
    assert c[0]["manifest_hash"] == "sha256:deadbeef"
    assert res["result"] == "PASS", "INFO-only findings must not produce a WARN verdict"


def test_rule_c_silent_when_reconciliation_is_newer(tmp_path):
    repo = _mkrepo(tmp_path, "cc", gate_9_eligible=False)
    man = repo / "reports" / "spec-coverage" / "manifests" / "cc-feature-manifest.json"
    old = time.time() - (5 * 86400)
    os.utime(man, (old, old))
    res = validate_format_coherence({}, repo)
    assert [i for i in res["items"] if i["rule"] == "C"] == []


def test_no_coverage_format_passes(tmp_path):
    """Item 9: a format with a contract but no coverage report is skipped -> PASS.

    This is the graceful-degradation guarantee: if the coverage system is ever
    retired, V247 goes quiet instead of failing.
    """
    repo = _mkrepo(tmp_path, "csv", with_coverage=False)
    res = validate_format_coherence({}, repo)
    assert res["result"] == "PASS"
    assert res["items"] == []
    assert "no formats carry both" in res["summary"]


def test_consistent_format_passes(tmp_path):
    """Item 10: both systems agree -> PASS with no items."""
    repo = _mkrepo(
        tmp_path, "ok",
        capabilities=[{"capability_id": "OK-PARSE-001", "level": "MUST",
                       "category": "parse", "observed_status": "TESTED"}],
        coverage_items=[{"feature_id": "FACT-OK-101", "name": "Decode",
                         "requirement_level": "mandatory", "status": "IMPLEMENTED",
                         "deferred_reason": None}],
    )
    res = validate_format_coherence({}, repo)
    assert res["result"] == "PASS"
    assert res["items"] == []


def test_xref_enrichment_and_gating_of_rule_a(tmp_path):
    """Item 11: the xref both enriches AND gates Rule A.

    XX-CLEAN-001 has an IMPLEMENTED mapped feature -> fires with the depth-gap reading.
    XX-SEC-001 has no mapped coverage at all -> suppressed as a non-contradiction and
    recorded in the auditable INFO item instead of emitting a vacuous WARN.
    """
    caps = [
        {"capability_id": "XX-CLEAN-001", "level": "MUST", "category": "transform",
         "observed_status": "NOT_STARTED"},
        {"capability_id": "XX-SEC-001", "level": "MUST", "category": "security",
         "observed_status": "NOT_STARTED"},
    ]
    items = [{"feature_id": "FACT-XX-104", "name": "Structural mutation API",
              "requirement_level": "mandatory", "status": "IMPLEMENTED",
              "deferred_reason": None}]
    xref = _full_xref(
        "xx",
        mappings=[{"coverage_id": "FACT-XX-104", "capability_ids": ["XX-CLEAN-001"],
                   "rationale": "clear_outputs is named in XX-CLEAN-001's behaviour"}],
        unmapped_cov=[],
        unmapped_cap=["XX-SEC-001"],
    )
    repo = _mkrepo(tmp_path, "xx", capabilities=caps, coverage_items=items, xref=xref)
    res = validate_format_coherence({}, repo)
    by_cap = {i["capability_id"]: i for i in res["items"] if i["rule"] == "A"}

    assert set(by_cap) == {"XX-CLEAN-001"}, "only the evidenced capability may WARN"
    clean = by_cap["XX-CLEAN-001"]
    assert clean["mapped_coverage_items"] == [
        {"feature_id": "FACT-XX-104", "status": "IMPLEMENTED"}
    ]
    assert "capability depth" in clean["interpretation"]

    sup = [i for i in res["items"] if i["rule"] == "A-suppressed"][0]
    assert [s["capability_id"] for s in sup["suppressed"]] == ["XX-SEC-001"]
    assert sup["suppressed"][0]["reason"] == "no_mapped_coverage"


# ---------------------------------------------------------------------------
# V248 — verification items 12-14
# ---------------------------------------------------------------------------

def _clean_xref_repo(tmp_path):
    caps = [{"capability_id": "QQ-PARSE-001", "level": "MUST", "category": "parse",
             "observed_status": "TESTED"},
            {"capability_id": "QQ-SEC-001", "level": "MUST", "category": "security",
             "observed_status": "NOT_STARTED"}]
    items = [{"feature_id": "FACT-QQ-101", "name": "Decode", "requirement_level": "mandatory",
              "status": "IMPLEMENTED", "deferred_reason": None},
             {"feature_id": "FACT-QQ-104", "name": "Streaming", "requirement_level": "optional",
              "status": "MISSING", "deferred_reason": "out of scope"}]
    xref = _full_xref(
        "qq",
        mappings=[{"coverage_id": "FACT-QQ-101", "capability_ids": ["QQ-PARSE-001"],
                   "rationale": "decode is the parse payload"}],
        unmapped_cov=["FACT-QQ-104"],
        unmapped_cap=["QQ-SEC-001"],
    )
    return _mkrepo(tmp_path, "qq", capabilities=caps, coverage_items=items, xref=xref), xref


def test_v248_clean_xref_passes(tmp_path):
    repo, _ = _clean_xref_repo(tmp_path)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "PASS"
    assert res["items"] == []


def test_v248_broken_coverage_id_fails(tmp_path):
    """Item 12: a coverage_id absent from the feature manifest is FAIL."""
    repo, xref = _clean_xref_repo(tmp_path)
    xref["formats"]["qq"]["mappings"][0]["coverage_id"] = "FACT-QQ-999"
    _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "FAIL"
    assert res["blocks_sprint"] is True
    assert any("coverage_id not found in feature manifest: FACT-QQ-999" in i["issue"]
               for i in res["items"])


def test_v248_broken_capability_id_fails(tmp_path):
    repo, xref = _clean_xref_repo(tmp_path)
    xref["formats"]["qq"]["mappings"][0]["capability_ids"] = ["QQ-NOPE-001"]
    _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "FAIL"
    assert any("capability_id not found in compiled contract: QQ-NOPE-001" in i["issue"]
               for i in res["items"])


def test_v248_mapping_without_rationale_fails(tmp_path):
    """The rationale is the xref's only defence against a semantically wrong mapping
    (V248 cannot check meaning), so an empty one is a referential failure."""
    repo, xref = _clean_xref_repo(tmp_path)
    xref["formats"]["qq"]["mappings"][0]["rationale"] = "   "
    _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "FAIL"
    assert any("no rationale" in i["issue"] for i in res["items"])


def test_v248_orphaned_coverage_item_warns(tmp_path):
    """Item 13: a new coverage item absent from the xref is a completeness WARN.

    The plan says both "FAILs until the xref is updated" and "WARN for completeness
    violations". A new item IS a completeness violation, so the narrower rule wins.
    """
    repo, xref = _clean_xref_repo(tmp_path)
    man_path = repo / "reports" / "spec-coverage" / "manifests" / "qq-feature-manifest.json"
    man = json.loads(man_path.read_text())
    man["features"].append({"feature_id": "FACT-QQ-105", "name": "New feature",
                            "requirement_level": "mandatory"})
    _write(man_path, man)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "WARN"
    assert res["blocks_sprint"] is False
    assert any("orphaned coverage item" in i["issue"] and "FACT-QQ-105" in i["issue"]
               for i in res["items"])


def test_v248_orphaned_capability_warns(tmp_path):
    repo, xref = _clean_xref_repo(tmp_path)
    con_path = repo / "shared" / "format-contracts" / "qq.yaml"
    con = yaml.safe_load(con_path.read_text())
    con["capabilities"].append({"capability_id": "QQ-EDIT-001", "level": "MUST",
                                "category": "edit"})
    _write(con_path, con)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "WARN"
    assert any("orphaned capability" in i["issue"] and "QQ-EDIT-001" in i["issue"]
               for i in res["items"])


def test_v248_dual_system_format_missing_from_xref_warns(tmp_path):
    """The forcing function for a format that newly acquires both systems."""
    repo, xref = _clean_xref_repo(tmp_path)
    del xref["formats"]["qq"]
    xref["formats"] = {}
    _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "WARN"
    assert any("missing from the xref" in i["issue"] for i in res["items"])


def test_v248_xref_naming_a_non_dual_system_format_fails(tmp_path):
    """An xref section for a format with no contract cannot be validated -> FAIL.

    This is the safetensors shape: coverage report present, contract absent.
    """
    repo, xref = _clean_xref_repo(tmp_path)
    xref["formats"]["safetensors"] = {"mappings": [], "unmapped_coverage": [],
                                      "unmapped_capabilities": []}
    _write(repo / "shared" / "format-contracts" / "coverage-capability-xref.yaml", xref)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "FAIL"
    assert any(i.get("format") == "safetensors" and "without both" in i["issue"]
               for i in res["items"])


def test_v248_missing_xref_warns_not_silently_passes(tmp_path):
    """A deleted xref must not silently disable the check."""
    repo = _mkrepo(tmp_path, "qq")  # no xref written
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "WARN"
    assert any("missing or unreadable" in i["issue"] for i in res["items"])


def test_v248_passes_when_no_dual_system_formats(tmp_path):
    repo = _mkrepo(tmp_path, "csv", with_coverage=False)
    res = validate_coverage_xref_integrity({}, repo)
    assert res["result"] == "PASS"
    assert "not required" in res["summary"]


# ---------------------------------------------------------------------------
# Real-repo state (item 14) and structural regressions
# ---------------------------------------------------------------------------

def test_real_xref_passes_v248():
    """Item 14: the authored xref is referentially intact and complete at HEAD."""
    res = validate_coverage_xref_integrity({}, REPO_ROOT)
    assert res["result"] == "PASS", f"xref integrity broken: {res['items']}"


def test_real_xref_covers_every_dual_system_format():
    """Every format with both a contract and a coverage report is mapped."""
    xref = yaml.safe_load(XREF_PATH.read_text(encoding="utf-8"))
    dual = {
        p.stem for p in _contracts(REPO_ROOT)
        if (REPO_ROOT / "reports" / "spec-coverage" / f"{p.stem}-coverage-report.json").is_file()
    }
    assert set(xref["formats"]) == dual


def test_safetensors_is_not_dual_system():
    """Pins the finding that safetensors has coverage but NO contract, so it is not
    dual-system and is deliberately absent from the xref. If a contract is ever added,
    this test fails and V248 starts WARNing — both point at the same required update."""
    assert (REPO_ROOT / "reports" / "spec-coverage" / "safetensors-coverage-report.json").is_file()
    assert not (REPO_ROOT / "shared" / "format-contracts" / "safetensors.yaml").is_file()
    xref = yaml.safe_load(XREF_PATH.read_text(encoding="utf-8"))
    assert "safetensors" not in xref["formats"]


def test_real_v247_never_blocks():
    """V247 is diagnostic. Whatever it finds in real data, it must not block a sprint."""
    res = validate_format_coherence({}, REPO_ROOT)
    assert res["result"] in {"PASS", "WARN"}
    assert res["blocks_sprint"] is False


def test_xref_is_not_treated_as_a_contract():
    """Structural regression: the xref sits in shared/format-contracts/ and would
    otherwise be globbed by _contracts() and fed to the L30 schema check, the
    recompiler and the hand-edit byte-comparison as a bogus "coverage-capability-xref"
    format."""
    assert XREF_PATH.is_file(), "xref fixture must exist for this regression to mean anything"
    names = [p.name for p in _contracts(REPO_ROOT)]
    assert "coverage-capability-xref.yaml" not in names
    assert all(n.endswith(".yaml") for n in names)
    assert "qoi.yaml" in names, "exclusion must not over-reach and drop real contracts"


def test_v247_v248_are_registered_with_explicit_dispatch():
    from governance_validators_contract import _VALIDATOR_REGISTRY

    reg = {e["rule_id"]: e for e in _VALIDATOR_REGISTRY}
    for rid, fn_name in (("V247", "validate_format_coherence"),
                         ("V248", "validate_coverage_xref_integrity")):
        assert rid in reg, f"{rid} not registered via @validator"
        assert reg[rid]["domain"] == "format_contract"
        assert reg[rid]["dispatch"] == "explicit"
        assert reg[rid]["fn"].__name__ == fn_name


def test_manifest_count_matches_module_sum():
    """The runner derives _EXPECTED_VALIDATOR_COUNT from the module counts; a
    mismatch makes the count check FAIL for reasons unrelated to any real defect."""
    manifest = yaml.safe_load(
        (REPO_ROOT / "tools" / "supervisor" / "validator-manifest.yaml").read_text(encoding="utf-8")
    )
    total = sum(m.get("count", 0) for m in manifest["modules"].values())
    assert total == manifest["expected_count"]
    fc = manifest["modules"]["format_contract"]
    assert fc["count"] == len(fc["validators"])
    assert {"V247", "V248"} <= set(fc["validators"])


def test_id_authority_mirrors_manifest_count():
    manifest = yaml.safe_load(
        (REPO_ROOT / "tools" / "supervisor" / "validator-manifest.yaml").read_text(encoding="utf-8")
    )
    authority = yaml.safe_load(
        (REPO_ROOT / "registry" / "governance" / "validator-id-authority.yaml").read_text(encoding="utf-8")
    )
    assert authority["runner_expected_count"] == manifest["expected_count"]
    entries = {e["rule_id"]: e for e in authority["registered_validators"]}
    for rid in ("V247", "V248"):
        assert rid in entries
        assert entries[rid]["source_file"] == (
            "tools/supervisor/governance_validators_format_contract.py"
        )


@pytest.mark.timeout(600)
def test_v247_v248_are_dispatched_by_the_runner():
    """Dispatch is explicit-only since TC-GVD-001 deleted the blind registry fallback,
    so the @validator decorator alone would leave these never executed. This drives the
    real runner and asserts both results actually appear."""
    from governance_validator_runner import run_all_governance_validators

    out = run_all_governance_validators({"work_items": []}, REPO_ROOT)
    names = {r.get("validator") for r in out["validators"]}
    rule_ids = {r.get("rule_id") for r in out["validators"] if r.get("rule_id")}
    assert "validate_format_coherence" in names
    assert "validate_coverage_xref_integrity" in names
    assert {"V247", "V248"} <= rule_ids, "_dispatch() must stamp the rule_id"
