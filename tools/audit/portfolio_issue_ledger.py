"""Occurrence-level issue ledger with root-cause chains (TC-PA-003).

Consumes the machine-readable inventory produced by
tools/audit/portfolio_forensic_inventory.py (TC-PA-002) and emits one row per
CONCRETE OCCURRENCE -- not per defect class, not a summary count. Every row
carries a four-level root-cause chain:

    symptom -> local -> machinery -> governance

This script IS the fix for finding PF-008 ("Phase 0 was read-only forensics but
forensic artifacts have no consumer -- they inform decisions but have no
automated binding to Phase 1; the forensics-to-fix pipeline was manual").
The binding is now mechanical: inventory.yaml -> ledger.yaml -> Phase 1/2 read
`prevention_validator` / `prevention_skill_fix` / `required_regression_test`
directly off each row, and `--assert-complete` fails the build if any row lacks
a machinery root cause or a prevention validator.

Usage:
    python tools/audit/portfolio_issue_ledger.py \
        --inventory .local/evidences/portfolio-audit-2026-07-16/full-inventory.yaml \
        --out       .local/evidences/portfolio-audit-2026-07-16/issue-ledger.yaml \
        --assert-complete

Exit codes: 0 ok; 2 completion-criteria violation (unpopulated required field).

Evidence discipline: every chain below is grounded in an artifact verified at
HEAD on 2026-07-17. Where a producing skill could not be traced from evidence,
the field records "UNTRACEABLE: <why>" rather than a guess.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]

# Validator IDs reallocated by the plan's PLAN HARDENING section (the plan's
# original V246/V247/V248/V249 all collide with validators already shipped).
V_SYSPATH = "V249"        # TC-PA-005 sys.path zero-tolerance (plan said V246 -> taken)
V_NAMESPACE = "V250"      # TC-PA-007 stdlib/popular-package collision (plan said V248 -> taken)
V_CONVERTER = "V251"      # TC-PA-008 converter information-model gate (plan said V249 -> taken)
V_STUB = "V149"           # existing validate_source_stubs
V_NESTED_DUP = "V246"     # existing validate_no_nested_duplicate_packages
V_MONOLITH = "V66/V77"    # existing monolith_detection_validator


def _sev_for_syspath(occ: dict, pkg: str) -> tuple[str, str]:
    """csv is the load-bearing case: without the insert the package is unreachable."""
    if pkg == "csv":
        return "HIGH", "load_bearing_due_to_stdlib_collision"
    return "MEDIUM", "cargo_cult_editable_install_already_on_path"


def build_rows(inv: dict) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seq: dict[str, int] = {}

    def nid(cat: str) -> str:
        seq[cat] = seq.get(cat, 0) + 1
        return f"ISS-{cat}-{seq[cat]:04d}"

    pkgs: dict[str, Any] = inv["packages"]
    syspath_formats = sorted(p for p, d in pkgs.items() if d["sys_path_file_count"] > 0)

    # ---------------- SYS_PATH: one row per occurrence (not per file) ----------
    for pkg, d in sorted(pkgs.items()):
        for occ in d["sys_path_occurrences"]:
            sev, why = _sev_for_syspath(occ, pkg)
            aliased = "sys." not in occ["snippet"]
            rows.append(
                {
                    "issue_id": nid("SYS_PATH"),
                    "format_id": pkg,
                    "category": "SYS_PATH",
                    "severity": sev,
                    "exact_path": occ["path"],
                    "line_or_locator": f"line {occ['line']} :: {occ['op']}",
                    "observed_behavior": (
                        f"Product module mutates the interpreter-global import path at runtime: "
                        f"`{occ['snippet']}`."
                    ),
                    "expected_behavior": (
                        "Product source resolves its own package via normal relative/absolute "
                        "imports; import-path construction is the installer's job, never the "
                        "library's."
                    ),
                    "root_cause_symptom": "sys.path mutation inside shipped library code.",
                    "root_cause_local": (
                        "Module cannot import its siblings under the name it is installed as, so it "
                        "prepends the source tree to sys.path as a fallback."
                        + (
                            " This occurrence uses an ALIASED form (`import sys as _sys`), which "
                            "evades naive `sys.path` text/AST matching."
                            if aliased
                            else ""
                        )
                    ),
                    "root_cause_machinery": (
                        "/add-dogfood-export and /new-format-kickstart emit modules with no "
                        "import-hygiene gate; the generated template treats sys.path.insert as the "
                        "sanctioned cross-package import mechanism. VERIFIED: the skills contain no "
                        "import-hygiene step (.claude/commands/add-dogfood-export.md, "
                        ".claude/commands/new-format-kickstart.md)."
                    ),
                    "root_cause_governance": (
                        f"No governance validator blocks sys.path mutation in src/python. "
                        f"{V_SYSPATH} is unimplemented (TC-PA-005). The gap persisted because the "
                        f"governance layer itself uses the same anti-pattern (120 occurrences across "
                        f"83 files in tools/supervisor/), so it could not credibly ban it."
                    ),
                    "producing_skill": "add-dogfood-export | new-format-kickstart",
                    "affected_formats": syspath_formats,
                    "prevention_validator": V_SYSPATH,
                    "prevention_skill_fix": (
                        "TC-PA-009/TC-PA-010: add an import-hygiene gate to /add-dogfood-export and "
                        "/new-format-kickstart that rejects emitted source containing sys.path "
                        "mutation (alias-resolved)."
                    ),
                    "required_regression_test": (
                        "tests/governance/test_no_syspath_in_product_source.py::"
                        "test_zero_syspath_occurrences_in_src_python"
                    ),
                    "status": "root_cause_confirmed",
                    "closure_evidence": "",
                    "notes": why + ("; aliased_sys_import" if aliased else ""),
                }
            )

    # ---------------- NAMESPACE --------------------------------------------
    # Empirically verified 2026-07-17 (see baseline-capture.yaml namespace_probe).
    rows.append(
        {
            "issue_id": nid("NAMESPACE"),
            "format_id": "csv",
            "category": "NAMESPACE",
            "severity": "CRITICAL",
            "exact_path": "src/python/csv/__init__.py",
            "line_or_locator": "package directory name `csv`",
            "observed_behavior": (
                "Package directory `src/python/csv/` claims the stdlib module name `csv`. MEASURED: "
                "with the editable install active, `import csv` from a neutral cwd resolves to "
                "C:\\Python313\\Lib\\csv.py -- stdlib WINS, because stdlib Lib sits at sys.path[3] "
                "while the .pth-injected src/python sits at sys.path[7]. The shipped format-factory "
                "csv package is therefore UNREACHABLE under its own name. Conversely, when a module "
                "forces resolution with sys.path.insert(0, src/python), `import csv` yields the "
                "format-factory package, whose 119 exports do NOT include the stdlib API "
                "(reader/writer/DictReader all absent) -- silently breaking stdlib csv for every "
                "other library in that process."
            ),
            "expected_behavior": (
                "A distributable package must not claim a stdlib module name. It should be importable "
                "under a non-colliding name (e.g. ff_csv) with no sys.path manipulation."
            ),
            "root_cause_symptom": (
                "Two mutually exclusive failure modes from one name: without a path hack the product "
                "is unreachable; with one, the stdlib is hijacked process-wide."
            ),
            "root_cause_local": "Package directory named `csv`, colliding with Python's stdlib csv module.",
            "root_cause_machinery": (
                "/new-format-kickstart derives the package directory name directly from format_id "
                "with no reserved-name check. VERIFIED: the skill has no stdlib/popular-package "
                "collision guard; its only stdlib-related field is `stdlib_module` (which stdlib "
                "module to USE for parsing -- the opposite concern) and its own documentation lists "
                "`csv` as an example value for that field."
            ),
            "root_cause_governance": (
                f"No validator checks package names against sys.stdlib_module_names or popular PyPI "
                f"distributions. {V_NAMESPACE} is unimplemented (TC-PA-007). Gap in "
                f"governance_validators_package_integrity.py (PF-005)."
            ),
            "producing_skill": "new-format-kickstart",
            "affected_formats": ["csv"],
            "prevention_validator": V_NAMESPACE,
            "prevention_skill_fix": (
                "TC-PA-010: add a reserved-name guard to /new-format-kickstart rejecting any "
                "package name in sys.stdlib_module_names or a curated popular-PyPI denylist."
            ),
            "required_regression_test": (
                "tests/governance/test_package_namespace_collisions.py::"
                "test_no_package_shadows_stdlib_or_popular_pypi"
            ),
            "status": "root_cause_confirmed",
            "closure_evidence": "",
            "notes": (
                "PLAN CORRECTION: the plan states the csv package 'shadows Python's stdlib'. "
                "Measurement shows the DEFAULT direction is the reverse -- stdlib shadows the "
                "product. Both directions are real but mutually exclusive per process. This also "
                "makes TC-PA-014 (sys.path elimination) DEPEND ON TC-PA-013 (csv rename): removing "
                "the inserts before renaming makes the csv package permanently unreachable. The "
                "plan does not declare that dependency."
            ),
        }
    )

    # ---------------- STUB ---------------------------------------------------
    for pkg, d in sorted(pkgs.items()):
        for s in d["stubs"]:
            rows.append(
                {
                    "issue_id": nid("STUB"),
                    "format_id": pkg,
                    "category": "STUB",
                    "severity": "LOW",
                    "exact_path": s["path"],
                    "line_or_locator": f"line {s['line']} :: {s['symbol']}",
                    "observed_behavior": (
                        f"`{s['symbol']}` exists solely to raise NotImplementedError "
                        f"({s['kind']}). It is NOT exported from __init__.py and NOT claimed in "
                        f"README.md; its docstring states FODP is read-only by design."
                    ),
                    "expected_behavior": (
                        "Either implement the capability or do not define the symbol. A function "
                        "whose only behaviour is to raise is an EP-1 violation regardless of intent."
                    ),
                    "root_cause_symptom": "NotImplementedError in non-abstract product function.",
                    "root_cause_local": (
                        "A deliberate read-only design decision was encoded as a raising stub "
                        "rather than as absence of the symbol."
                    ),
                    "root_cause_machinery": (
                        "The codec template emits a write_{fmt}() for every format regardless of "
                        "whether the format supports writing; read-only formats get a raising stub "
                        "to satisfy the template's symmetric read/write shape."
                    ),
                    "root_cause_governance": (
                        f"{V_STUB} (validate_source_stubs) delegates to tools/review/no_stub_scan.py "
                        f"whose allowlist tolerates this pattern. VERIFIED AGGRAVATOR: {V_STUB} "
                        f"FAILS OPEN -- if `from no_stub_scan import report` raises ImportError it "
                        f"returns result=PASS, blocks_sprint=False. Worse, it reaches that import via "
                        f"`import sys as _sys; _sys.path.insert(...)` "
                        f"(governance_validators_ext4.py:835-838), i.e. the stub validator depends on "
                        f"the very anti-pattern {V_SYSPATH} is meant to ban, in the ALIASED form that "
                        f"evades naive detection."
                    ),
                    "producing_skill": "UNTRACEABLE: no skill-execution receipt binds this file to a generator run",
                    "affected_formats": [pkg],
                    "prevention_validator": V_STUB,
                    "prevention_skill_fix": (
                        "Make V149 fail CLOSED on scanner-import failure, and remove its sys.path "
                        "dependency; teach the codec template to omit write_* for read-only formats."
                    ),
                    "required_regression_test": (
                        "tests/governance/test_source_stubs.py::test_v149_fails_closed_when_scanner_missing"
                    ),
                    "status": "root_cause_confirmed",
                    "closure_evidence": "",
                    "notes": (
                        "SEVERITY DOWNGRADE vs plan: TC-PA-012 treats this as a defect to remove. It "
                        "is an honest, documented sentinel -- not a false capability claim. The "
                        "governance finding (V149 fail-open + aliased sys.path dependency) is "
                        "materially more severe than the stub itself."
                    ),
                }
            )

    # ---------------- CONVERTER ---------------------------------------------
    for pkg, d in sorted(pkgs.items()):
        for c in d["converters"]:
            cls = c["classification"]
            if cls in ("FAITHFUL", "MEANINGFUL", "CONTAINER"):
                continue
            sev = "HIGH" if cls == "MEANINGLESS_PROJECTION" else "LOW"
            rows.append(
                {
                    "issue_id": nid("CONVERTER"),
                    "format_id": pkg,
                    "category": "CONVERTER",
                    "severity": sev,
                    "exact_path": c["path"],
                    "line_or_locator": f"module {c['module']} ({c['loc']} LOC)",
                    "observed_behavior": (
                        f"{c['source_format']} ({c['source_model']}) -> {c['target_format']} "
                        f"({c['target_model']}): {c['rationale']}."
                    ),
                    "expected_behavior": (
                        "A converter should exist only where a defensible information-model mapping "
                        "exists between source and target."
                    ),
                    "root_cause_symptom": f"Converter classified {cls} by information-model analysis.",
                    "root_cause_local": (
                        f"Module projects a {c['source_model']} document into a {c['target_model']} "
                        f"container; the target cannot represent the source's information model."
                    ),
                    "root_cause_machinery": (
                        "/add-dogfood-export generates {src}_to_{tgt} modules combinatorially with no "
                        "information-model compatibility check. VERIFIED: the skill emits "
                        "src/python/{fmt}/{fmt}_to_{tgt}.py (add-dogfood-export.md:98-101) and "
                        "contains no compatibility gate (PF-002)."
                    ),
                    "root_cause_governance": (
                        f"No validator gates converter creation on information-model compatibility. "
                        f"{V_CONVERTER} is unimplemented (TC-PA-008). Converter count was treated as "
                        f"a product-progress metric, which rewarded combinatorial generation."
                    ),
                    "producing_skill": "add-dogfood-export",
                    "affected_formats": [c["source_format"], c["target_format"]],
                    "prevention_validator": V_CONVERTER,
                    "prevention_skill_fix": (
                        "TC-PA-009: /add-dogfood-export must consult the information-model matrix and "
                        "refuse to emit MEANINGLESS_PROJECTION pairs."
                    ),
                    "required_regression_test": (
                        "tests/governance/test_converter_information_model.py::"
                        "test_no_meaningless_projection_converters"
                    ),
                    "status": "root_cause_confirmed",
                    "closure_evidence": "",
                    "notes": f"classification={cls}; disposition target TC-PA-015",
                }
            )

    # ---------------- MONOLITH ----------------------------------------------
    for pkg, d in sorted(pkgs.items()):
        for m in d["monolith_files"]:
            rows.append(
                {
                    "issue_id": nid("MONOLITH"),
                    "format_id": pkg,
                    "category": "MONOLITH",
                    "severity": "MEDIUM",
                    "exact_path": m["path"],
                    "line_or_locator": f"{m['loc']} LOC (threshold 800)",
                    "observed_behavior": f"Source file is {m['loc']} LOC, exceeding the 800 LOC threshold.",
                    "expected_behavior": "Single-responsibility modules under the 800 LOC structural cap.",
                    "root_cause_symptom": "Oversized multi-responsibility module.",
                    "root_cause_local": "Parsing, writing, analytics and model concerns co-located in one module.",
                    "root_cause_machinery": (
                        "The codec template concentrates all format logic in {fmt}_codec.py; no "
                        "generator step splits analytics out (see §8.1 Analytics Separation Protocol)."
                    ),
                    "root_cause_governance": (
                        f"{V_MONOLITH} detects monoliths but registry/source-structure-baseline.json "
                        f"grandfathers existing files via write-once baseline_loc_cap, so detection "
                        f"does not force healing."
                    ),
                    "producing_skill": "format-feature-expansion | product-source-task",
                    "affected_formats": [pkg],
                    "prevention_validator": V_MONOLITH,
                    "prevention_skill_fix": (
                        "Apply /extract-analytics-from-monolith; keep baseline_loc_cap write-once so "
                        "caps cannot inflate."
                    ),
                    "required_regression_test": (
                        "tests/governance/test_source_structure_baseline.py::test_no_new_monoliths"
                    ),
                    "status": "root_cause_confirmed",
                    "closure_evidence": "",
                    "notes": "disposition target TC-PA-017",
                }
            )

    # ---------------- SAL_SPARSE --------------------------------------------
    for pkg, d in sorted(pkgs.items()):
        sal = d.get("sal_facts") or {}
        n = sal.get("merged_spec_facts", sal.get("canonical_facts"))
        if n is None or n < 0 or n >= 20:
            continue
        rows.append(
            {
                "issue_id": nid("SAL_SPARSE"),
                "format_id": pkg,
                "category": "SAL_SPARSE",
                "severity": "HIGH" if n < 10 else "MEDIUM",
                "exact_path": f"shared/sal-facts/{pkg}.yaml",
                "line_or_locator": f"{n} facts (threshold 20)",
                "observed_behavior": (
                    f"Format {pkg} has only {n} SAL facts. Product features cannot be traced to "
                    f"specification obligations."
                ),
                "expected_behavior": "Sufficient SAL fact coverage to drive spec-parity feature work.",
                "root_cause_symptom": f"Sparse specification fact base ({n} facts).",
                "root_cause_local": "Facts were manually seeded rather than ingested from a specification.",
                "root_cause_machinery": (
                    "/ingest-spec-sal was never run against a real specification document for this "
                    "format; /new-format-kickstart admits a format to the portfolio without a "
                    "minimum-fact precondition, so acquisition outran specification research."
                ),
                "root_cause_governance": (
                    "No gate blocks product deepening on formats with sparse SAL coverage. EP-4 "
                    "('machinery readiness before product work') requires SAL fact count > 0, which "
                    "2 facts technically satisfies -- the threshold is too weak to be meaningful."
                ),
                "producing_skill": "new-format-kickstart",
                "affected_formats": [pkg],
                "prevention_validator": "EP-4 machinery-readiness gate (threshold needs raising from >0 to >=20)",
                "prevention_skill_fix": (
                    "TC-PA-019: run /ingest-spec-sal against the authoritative spec; add a "
                    "minimum-fact precondition to /new-format-kickstart."
                ),
                "required_regression_test": (
                    "tests/governance/test_sal_coverage.py::test_all_product_formats_meet_min_facts"
                ),
                "status": "root_cause_confirmed",
                "closure_evidence": "",
                "notes": f"merged_spec_facts={n}; disposition target TC-PA-019",
            }
        )

    # ---------------- TEST_GAP ----------------------------------------------
    rows.append(
        {
            "issue_id": nid("TEST_GAP"),
            "format_id": "toml",
            "category": "TEST_GAP",
            "severity": "HIGH",
            "exact_path": "tests/python/dogfood/test_dogfood_toml_roundtrip_write_ndjson_export.py",
            "line_or_locator": "lines 17-22 (importlib workaround) -> src/python/toml/toml_codec.py:25",
            "observed_behavior": (
                "The ONLY collection error in the suite (1 of 39,284 collected tests). The module "
                "loads toml_codec.py via importlib.spec_from_file_location('toml_codec', ...), which "
                "creates a module with no package context, so toml_codec.py:25 "
                "`from .exceptions import ...` raises "
                "'ImportError: attempted relative import with no known parent package'. REPRODUCED "
                "2026-07-17."
            ),
            "expected_behavior": "The test imports the package normally and collects cleanly.",
            "root_cause_symptom": "1 test module uncollectable; its tests never run.",
            "root_cause_local": (
                "spec_from_file_location loads a package submodule as a top-level module, breaking "
                "its relative imports."
            ),
            "root_cause_machinery": (
                "The workaround is premised on a comment reading \"stdlib 'toml' conflict\" -- which "
                "is FALSE. `toml` is not stdlib (`tomllib` is), and no third-party toml is installed. "
                "MEASURED COUNTERFACTUAL: `from toml.toml_codec import load_toml, write_toml, "
                "roundtrip` succeeds. The test generator applied a csv-shaped collision workaround to "
                "a format that has no collision, and no gate caught that the workaround was both "
                "unnecessary and broken."
            ),
            "root_cause_governance": (
                "No validator asserts that tests/python collects without error, so a permanently "
                "dead test module has survived undetected. Collection health is not a gate."
            ),
            "producing_skill": "add-dogfood-export",
            "affected_formats": ["toml", "ndjson"],
            "prevention_validator": f"{V_NAMESPACE} (collision truth source) + new collection-health gate",
            "prevention_skill_fix": (
                "/add-dogfood-export must emit normal package imports and must derive any collision "
                "workaround from a verified collision list, not from a hand-written comment."
            ),
            "required_regression_test": (
                "tests/governance/test_collection_health.py::test_tests_python_collects_without_errors"
            ),
            "status": "reproduced",
            "closure_evidence": "",
            "notes": (
                "PLAN GAP: the plan has no taskcard for this. It is the single hardest evidence that "
                "the namespace/sys.path defect class causes real, silent test loss."
            ),
        }
    )

    # ---------------- CLAIM_MISMATCH ----------------------------------------
    for pkg, d in sorted(pkgs.items()):
        for sym in d["readme"].get("claimed_but_not_public") or []:
            rows.append(
                {
                    "issue_id": nid("CLAIM_MISMATCH"),
                    "format_id": pkg,
                    "category": "CLAIM_MISMATCH",
                    "severity": "MEDIUM",
                    "exact_path": f"src/python/{pkg}/README.md",
                    "line_or_locator": f"claimed symbol `{sym}()`",
                    "observed_behavior": (
                        f"README.md documents `{sym}()` but it is not a public symbol of the package."
                    ),
                    "expected_behavior": "Documented API matches the package's actual public surface.",
                    "root_cause_symptom": "README claims a symbol the package does not export.",
                    "root_cause_local": "README drifted from the implementation, or documents an aspirational API.",
                    "root_cause_machinery": (
                        "README generation is not bound to the AST-derived public surface; no "
                        "generator reconciles the two."
                    ),
                    "root_cause_governance": (
                        "No validator diffs README claims against __all__/public symbols, so doc "
                        "drift is invisible to the sprint gate."
                    ),
                    "producing_skill": "UNTRACEABLE: README authored across multiple sprints without receipts",
                    "affected_formats": [pkg],
                    "prevention_validator": "V252 (proposed): README-claim vs public-API reconciliation",
                    "prevention_skill_fix": "Bind README generation to the inventory's public symbol list.",
                    "required_regression_test": (
                        "tests/governance/test_readme_claims.py::test_readme_claims_are_public_symbols"
                    ),
                    "status": "discovered",
                    "closure_evidence": "",
                    "notes": "low-confidence extractor: matches `identifier(` code spans in README",
                }
            )

    # ---------------- HYGIENE ------------------------------------------------
    for pkg, d in sorted(pkgs.items()):
        if d["pycache_file_count"] <= 0:
            continue
        rows.append(
            {
                "issue_id": nid("HYGIENE"),
                "format_id": pkg,
                "category": "HYGIENE",
                "severity": "LOW",
                "exact_path": f"src/python/{pkg}/**/__pycache__",
                "line_or_locator": f"{d['pycache_file_count']} .pyc files",
                "observed_behavior": f"{d['pycache_file_count']} compiled .pyc artifacts present in the source tree.",
                "expected_behavior": "No build artifacts in the source tree.",
                "root_cause_symptom": "__pycache__ directories inside src/python.",
                "root_cause_local": "Interpreter byte-compiles modules in place when imported from the source tree.",
                "root_cause_machinery": (
                    "Because product code is imported via sys.path.insert into the SOURCE tree "
                    "rather than from an installed location, every test run byte-compiles into "
                    "src/. This is a direct downstream consequence of the SYS_PATH defect class."
                ),
                "root_cause_governance": (
                    "No validator asserts src/ is free of build artifacts; .gitignore completeness "
                    "is unverified (PF-010)."
                ),
                "producing_skill": "N/A: interpreter side-effect, not skill-generated",
                "affected_formats": sorted(p for p, x in pkgs.items() if x["pycache_file_count"] > 0),
                "prevention_validator": "V253 (proposed): src build-artifact cleanliness",
                "prevention_skill_fix": "TC-PA-018: harden .gitignore; eliminate source-tree imports (TC-PA-014).",
                "required_regression_test": "tests/governance/test_source_hygiene.py::test_no_pycache_in_src",
                "status": "discovered",
                "closure_evidence": "",
                "notes": "downstream of SYS_PATH; fixing imports removes the cause, not just the files",
            }
        )

    return rows


REQUIRED = (
    "issue_id", "format_id", "category", "severity", "exact_path", "line_or_locator",
    "observed_behavior", "expected_behavior", "root_cause_symptom", "root_cause_local",
    "root_cause_machinery", "root_cause_governance", "producing_skill", "affected_formats",
    "prevention_validator", "prevention_skill_fix", "required_regression_test", "status",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Occurrence-level issue ledger with root-cause chains (TC-PA-003).")
    ap.add_argument("--inventory", default=".local/evidences/portfolio-audit-2026-07-16/full-inventory.yaml")
    ap.add_argument("--out", default=".local/evidences/portfolio-audit-2026-07-16/issue-ledger.yaml")
    ap.add_argument("--assert-complete", action="store_true", help="exit 2 if any row misses a required field")
    args = ap.parse_args()

    inv_path = Path(args.inventory)
    if not inv_path.is_absolute():
        inv_path = REPO / inv_path
    inv = yaml.safe_load(inv_path.read_text(encoding="utf-8"))

    rows = build_rows(inv)

    by_cat: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
        by_sev[r["severity"]] = by_sev.get(r["severity"], 0) + 1

    # Completion criteria (TC-PA-003): every issue must have root_cause_machinery
    # and prevention_validator populated. Enforced mechanically, not by assertion.
    violations: list[str] = []
    for r in rows:
        for f in REQUIRED:
            v = r.get(f)
            if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not v):
                violations.append(f"{r['issue_id']}: empty required field `{f}`")

    # TC-PA-003 completion criteria says "Ledger covers all defect classes."
    # A class with zero rows must therefore carry an explicit, honest verdict --
    # silently omitting it would be indistinguishable from never having looked.
    schema_classes = [
        "SYS_PATH", "DUPLICATE", "NAMESPACE", "STUB", "CONVERTER",
        "MONOLITH", "SAL_SPARSE", "TEST_GAP", "CLAIM_MISMATCH", "HYGIENE",
    ]
    empty_verdicts = {
        "DUPLICATE": {
            "verdict": "CHECKED_EMPTY",
            "confidence": "HIGH",
            "basis": (
                "No pkg/pkg nested duplicate directory exists anywhere under src/python "
                "(verified 2026-07-17). src/python/fods/fods was deleted in commit 9a9ff060. "
                "V246 validate_no_nested_duplicate_packages now detects this class. "
                "Plan taskcards TC-PA-006 and TC-PA-011 are therefore OBSOLETE."
            ),
        },
        "CLAIM_MISMATCH": {
            "verdict": "UNPROVEN_LOW_CONFIDENCE",
            "confidence": "LOW",
            "basis": (
                "The README claim extractor matches only `identifier(` code spans and found just "
                "3 claimed symbols across 26 READMEs (csv=2, ubl=1), none of which mismatched. "
                "Zero rows here means THE EXTRACTOR IS TOO NAIVE TO CONCLUDE, not that doc drift "
                "is absent. Sharper finding for follow-up: 24 of 26 package READMEs document no "
                "API symbol in call syntax at all, so claim-vs-reality cannot be assessed by this "
                "method. Requires a prose-level extractor before any 'no drift' claim is made."
            ),
        },
    }
    coverage = {}
    for c in schema_classes:
        if by_cat.get(c):
            coverage[c] = {"verdict": "POPULATED", "confidence": "HIGH", "rows": by_cat[c]}
        else:
            coverage[c] = {"rows": 0, **empty_verdicts.get(c, {"verdict": "CHECKED_EMPTY", "confidence": "MEDIUM", "basis": "no occurrences detected"})}

    doc = {
        "schema_version": "1.0",
        "taskcard": "TC-PA-003",
        "mission_id": "PORTFOLIO-AUDIT-2026-07-16",
        "generator": "tools/audit/portfolio_issue_ledger.py",
        "consumes": {
            "inventory": inv_path.relative_to(REPO).as_posix(),
            "inventory_digest": inv.get("inventory_digest"),
        },
        "granularity": "occurrence-level (one row per concrete instance, not per defect class)",
        "totals": {
            "issues": len(rows),
            "by_category": dict(sorted(by_cat.items())),
            "by_severity": dict(sorted(by_sev.items())),
        },
        "defect_class_coverage": coverage,
        "completion_criteria": {
            "every_issue_has_root_cause_machinery": all(r.get("root_cause_machinery") for r in rows),
            "every_issue_has_prevention_validator": all(r.get("prevention_validator") for r in rows),
            "required_field_violations": violations,
        },
        "issues": rows,
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True)
    out.write_text(payload, encoding="utf-8")

    print(f"wrote {out}")
    print(f"  issues: {len(rows)}")
    print("  by category:")
    for k, v in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")
    print("  by severity:")
    for k, v in sorted(by_sev.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")
    print(f"  ledger_sha256: {hashlib.sha256(payload.encode()).hexdigest()}")

    if violations:
        print(f"COMPLETION CRITERIA VIOLATION: {len(violations)} unpopulated required fields")
        for v in violations[:10]:
            print("   ", v)
        if args.assert_complete:
            return 2
    else:
        print("COMPLETION CRITERIA: PASS (all rows carry a machinery root cause + prevention validator)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
