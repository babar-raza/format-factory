"""Regression tests for the skill gates (TC-PA-009, TC-PA-010).

Plan: plans/.claude/primary-purpose-the-python-starry-cupcake.md
Mission: PORTFOLIO-AUDIT-2026-07-16

The load-bearing tests here are the FALSE-CLEAN tests: a detector that misses the
aliased form of a defect is worse than no detector, because it certifies the
defect as absent (plan finding PA-F4). `test_alias_*` exist to fail loudly if
anyone "simplifies" the AST walk back to a naive Name.id == "sys" match.
"""
from __future__ import annotations

import ast
import re
import textwrap
from pathlib import Path

import pytest

from tools.governance.skill_gates import (converter_compat, dogfood_export_gate,
                                          format_name_gate, import_hygiene,
                                          namespace_collision)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _src(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


# --------------------------------------------------------------------------
# import_hygiene — the alias-evasion class (PA-F4)
# --------------------------------------------------------------------------

def test_plain_syspath_insert_detected():
    findings = import_hygiene.check_source(_src("""
        import sys
        sys.path.insert(0, "/x")
    """))
    assert len(findings) == 1
    assert findings[0].kind == "SYSPATH_MUTATION"


def test_alias_import_sys_as_underscore_detected():
    """`import sys as _sys` — the form found at src/python/dif/interchange_document.py:24-29."""
    findings = import_hygiene.check_source(_src("""
        import sys as _sys
        _sys.path.insert(0, "/x")
    """))
    assert len(findings) == 1, "aliased sys.path.insert must not read as clean"


def test_alias_defeats_naive_matchers_but_not_ours():
    """Proves the evasion is real, so this detector's complexity is justified."""
    sample = _src("""
        import sys as _sys
        _sys.path.insert(0, "/x")
    """)
    # A word-boundary regex misses it (\b does not match between "_" and "s").
    assert re.search(r"\bsys\.path", sample) is None
    # A naive AST match on Name.id == "sys" misses it.
    naive = [
        n for n in ast.walk(ast.parse(sample))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "insert"
        and isinstance(n.func.value, ast.Attribute)
        and n.func.value.attr == "path"
        and isinstance(n.func.value.value, ast.Name)
        and n.func.value.value.id == "sys"
    ]
    assert naive == []
    # Ours catches it.
    assert len(import_hygiene.check_source(sample)) == 1


def test_from_sys_import_path_as_alias_detected():
    findings = import_hygiene.check_source(_src("""
        from sys import path as _p
        _p.insert(0, "/x")
    """))
    assert len(findings) == 1


def test_assignment_rebinding_detected():
    findings = import_hygiene.check_source(_src("""
        import sys
        _p = sys.path
        _p.append("/x")
    """))
    assert len(findings) == 1


def test_chained_rebinding_detected():
    findings = import_hygiene.check_source(_src("""
        import sys as s
        p = s.path
        p2 = p
        p2.insert(0, "/x")
    """))
    assert len(findings) == 1


def test_augassign_and_slice_assign_detected():
    findings = import_hygiene.check_source(_src("""
        import sys
        sys.path += ["/a"]
        sys.path[0:0] = ["/b"]
        sys.path = ["/c"]
    """))
    kinds = {f.kind for f in findings}
    assert kinds == {"SYSPATH_AUGASSIGN", "SYSPATH_SLICE_ASSIGN", "SYSPATH_REBIND"}


def test_clean_source_reports_nothing():
    findings = import_hygiene.check_source(_src("""
        from dif.interchange_document import load
        import json

        def go(p):
            return json.dumps(load(p))
    """))
    assert findings == []


def test_unrelated_path_insert_is_not_flagged():
    """os.path / a local list named `path` must not produce false positives."""
    findings = import_hygiene.check_source(_src("""
        import os
        parts = []
        parts.insert(0, os.path.join("a", "b"))
    """))
    assert findings == []


def test_syntax_error_is_reported_not_silently_clean():
    findings = import_hygiene.check_source("def broken(:\n")
    assert len(findings) == 1
    assert findings[0].kind == "PARSE_ERROR"


# --------------------------------------------------------------------------
# import_hygiene — self-application (PA-F3: an enforcer that commits the
# offence it polices is not credible; V149 does exactly that)
# --------------------------------------------------------------------------

def test_skill_gate_modules_are_themselves_syspath_clean():
    gate_dir = REPO_ROOT / "tools" / "governance" / "skill_gates"
    findings = import_hygiene.check_paths([gate_dir])
    assert findings == [], (
        "skill gate modules must not mutate sys.path — an import-hygiene gate "
        "that bootstraps itself with sys.path.insert has no standing: "
        + "; ".join(f.format() for f in findings))


# --------------------------------------------------------------------------
# namespace_collision (TC-PA-010)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["csv", "json", "xml", "io", "types"])
def test_stdlib_colliding_names_blocked(name):
    """Stdlib collisions always block (MODE_1/MODE_2 have no safe outcome)."""
    assert namespace_collision.check_name(name).blocked


@pytest.mark.parametrize("name", ["toml", "yaml", "numpy"])
def test_popular_package_colliding_names_warn_not_blocked(name):
    """Popular-PyPI collisions WARN, not BLOCK (2026-07-20 policy fix, TC-PA-039
    review): the collision is contingent on that distribution actually being
    installed alongside ours, unlike a stdlib collision which is unconditional.
    """
    res = namespace_collision.check_name(name)
    assert res.verdict == namespace_collision.VERDICT_POPULAR
    assert not res.blocked, res.detail


@pytest.mark.parametrize("name", ["sylk", "fods", "fodt", "ndjson", "qoi", "ff_csv"])
def test_free_names_allowed(name):
    res = namespace_collision.check_name(name)
    assert not res.blocked, res.detail


def test_csv_verdict_is_stdlib_collision():
    assert namespace_collision.check_name("csv").verdict == "STDLIB_COLLISION"


def test_toml_is_popular_package_not_stdlib():
    """PA-F8: `toml` is NOT stdlib (`tomllib` is). Classify it correctly."""
    assert "toml" not in namespace_collision.stdlib_names()
    assert "tomllib" in namespace_collision.stdlib_names()
    assert namespace_collision.check_name("toml").verdict == "POPULAR_PACKAGE_COLLISION"


def test_invalid_identifier_blocked():
    assert namespace_collision.check_name("9bad").verdict == "INVALID_IDENTIFIER"


def test_format_name_gate_exit_codes():
    assert format_name_gate.main(["--format-name", "csv"]) == 1
    assert format_name_gate.main(["--format-name", "sylk"]) == 0


def test_format_name_gate_popular_collision_warns_not_blocks():
    """toml is a popular-PyPI collision, not stdlib -- exit 0 (non-blocking WARN)."""
    result = format_name_gate.run("toml")
    assert result["verdict"] == "WARN"
    assert result["stop_condition"] is None
    assert format_name_gate.main(["--format-name", "toml"]) == 0


def test_format_name_gate_suggests_prefixed_alternative():
    assert format_name_gate.run("csv")["suggested_name"] == "ff_csv"


# --------------------------------------------------------------------------
# converter_compat (TC-PA-009 compatibility half)
# --------------------------------------------------------------------------

@pytest.fixture()
def matrix(tmp_path):
    """Fixture mirroring the REAL registry shape authored by TC-PA-008/V251:
    keyed by file path, `category` (not `classification`), loss recorded in
    `rationale`. See test_gate_resolves_against_the_real_registry."""
    p = tmp_path / "converter-compatibility-matrix.yaml"
    p.write_text(textwrap.dedent("""
        schema_version: 1.0
        format_domains:
          dif: TABULAR
          csv: TABULAR
          fods: TABULAR
          pbm: RASTER
          fodt: DOCUMENT
          ods: TABULAR
        converters:
          src/python/dif/dif_to_csv.py:
            pair: "dif->csv"
            source_domain: TABULAR
            target_domain: TABULAR
            category: COMPATIBLE
            rationale: "both tabular"
          src/python/fods/fods_to_pbm.py:
            pair: "fods->pbm"
            source_domain: TABULAR
            target_domain: RASTER
            category: INCOMPATIBLE
            rationale: "a cell grid has no pixel representation"
            disposition: PENDING
          src/python/fodt/fodt_to_csv.py:
            pair: "fodt->csv"
            source_domain: DOCUMENT
            target_domain: TABULAR
            category: PROJECTION
            rationale: "extracts table text only; styles dropped"
          src/python/ods/ods_to_csv.py:
            pair: "ods->csv"
            source_domain: TABULAR
            target_domain: TABULAR
            category: PROJECTION
    """), encoding="utf-8")
    return str(p)


def test_missing_matrix_fails_closed():
    """Absence must BLOCK. Allow-on-missing would never fire for a new pair."""
    res = converter_compat.check_pair("fods", "pbm", matrix_path="/nonexistent.yaml")
    assert res.verdict == converter_compat.VERDICT_CONFIG_ERROR
    assert res.blocked


def test_compatible_pair_allowed(matrix):
    assert converter_compat.check_pair("dif", "csv", matrix).verdict == "ALLOW"


def test_incompatible_pair_blocked(matrix):
    res = converter_compat.check_pair("fods", "pbm", matrix)
    assert res.verdict == "BLOCK"
    assert "INCOMPATIBLE" in res.reason


def test_unregistered_pair_blocked(matrix):
    """The core PF-002 rule: no converter without a registered assessment."""
    res = converter_compat.check_pair("toml", "ppm", matrix)
    assert res.verdict == "BLOCK"
    assert "no entry" in res.reason


def test_projection_with_loss_note_allowed(matrix):
    assert converter_compat.check_pair("fodt", "csv", matrix).verdict == "ALLOW"


def test_projection_without_documented_loss_blocked(matrix):
    """ods_to_csv is PROJECTION with neither rationale nor loss_note."""
    res = converter_compat.check_pair("ods", "csv", matrix)
    assert res.verdict == "BLOCK"
    assert "loss_note" in res.reason or "rationale" in res.reason


def test_same_format_pair_blocked(matrix):
    assert converter_compat.check_pair("csv", "csv", matrix).verdict == "BLOCK"


def test_pair_normalisation_accepts_every_key_shape():
    n = converter_compat._normalise_pair
    assert n("abw->csv") == "abw_to_csv"
    assert n("src/python/abw/abw_to_csv.py") == "abw_to_csv"
    assert n("src\\python\\abw\\abw_to_csv.py") == "abw_to_csv"
    assert n("abw_to_csv") == "abw_to_csv"


def test_renamed_class_field_does_not_read_as_allow(tmp_path):
    """If the registry renames `category`, the gate must CONFIG_ERROR, not ALLOW.

    Guards the failure mode where a schema change makes the class field read as
    blank and a blank silently passes.
    """
    p = tmp_path / "m.yaml"
    p.write_text(textwrap.dedent("""
        converters:
          src/python/dif/dif_to_csv.py:
            pair: "dif->csv"
            some_future_field: COMPATIBLE
    """), encoding="utf-8")
    res = converter_compat.check_pair("dif", "csv", str(p))
    assert res.verdict == converter_compat.VERDICT_CONFIG_ERROR
    assert res.blocked


# --------------------------------------------------------------------------
# Seam contract: the gate must stay reconciled with the REAL registry
# (TC-PA-008 / V251 owns the schema; this consumer follows it)
# --------------------------------------------------------------------------

def test_gate_resolves_against_the_real_registry():
    """The live registry must be readable and its pairs resolvable.

    This is the test that catches schema drift between TC-PA-008's registry and
    this consumer. Without it, a shape change reads as "no entry for <pair>" and
    the gate blocks every converter for a bogus reason — which is exactly what
    happened on 2026-07-17 when the registry landed keyed by file path with a
    `category` field while this module expected pair-id keys and `classification`.
    """
    real = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"
    if not real.exists():
        pytest.skip("registry/converter-compatibility-matrix.yaml not landed yet "
                    "(TC-PA-008); gate correctly fails closed until then")
    m = converter_compat.load_matrix(real)
    idx = converter_compat._index_by_pair(m)
    assert idx, "no pair resolved from the real registry — schema drift"

    totals = m.get("totals") or {}
    if totals.get("converters"):
        assert len(idx) == totals["converters"], (
            f"indexed {len(idx)} pairs but registry totals say "
            f"{totals['converters']} — lookup is missing entries")

    # Every registered pair must yield a definite verdict, never CONFIG_ERROR.
    # evaluate_pair() against the already-loaded matrix — check_pair() would
    # re-parse the 71KB registry once per pair.
    for pid in idx:
        if "_to_" not in pid:
            continue
        src, _, tgt = pid.partition("_to_")
        res = converter_compat.evaluate_pair(m, src, tgt)
        assert res.verdict in ("ALLOW", "BLOCK"), (
            f"{pid} -> {res.verdict}: {res.reason}")


def test_allowed_pairs_matches_registry_totals():
    """allowed_pairs() must equal COMPATIBLE + documented PROJECTION.

    Regression for a real drift bug (2026-07-17): generate_supervisor_packet's
    dogfood-lane helper read the `classification` field directly instead of asking
    the shared checker. When the registry landed using `category`, the helper
    returned [] against 183 allowable pairs — which looks exactly like "no dogfood
    work this sprint" and would have silently disabled the lane forever.
    """
    real = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"
    if not real.exists():
        pytest.skip("registry not landed yet (TC-PA-008)")
    m = converter_compat.load_matrix(real)
    allowed = converter_compat.allowed_pairs(m)
    totals = m.get("totals") or {}
    if totals:
        expected = totals.get("COMPATIBLE", 0) + totals.get("PROJECTION", 0)
        assert len(allowed) == expected, (
            f"allowed_pairs()={len(allowed)} but registry totals imply {expected} "
            f"(COMPATIBLE={totals.get('COMPATIBLE')} + "
            f"PROJECTION={totals.get('PROJECTION')}) — the gate and the registry "
            f"disagree about which converters are legal")
        assert len(allowed) > 0


def test_packet_generator_dogfood_lane_uses_shared_checker():
    """The sprint packet's lane helper must agree with the gate, and must
    distinguish 'no pairs' from 'gate broken' (status, not a bare [])."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_gsp", REPO_ROOT / "tools" / "supervisor" / "generate_supervisor_packet.py")
    if spec is None or spec.loader is None:
        pytest.skip("generate_supervisor_packet.py not importable standalone")
    import sys as _s
    _s.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))  # sibling atomic_io
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"cannot load packet generator standalone: {exc}")

    pairs, status = mod._available_dogfood_pairs()
    assert status in ("ok", "matrix_absent", "gate_unavailable")
    assert status != "gate_unavailable", (
        "the dogfood lane helper cannot import the compatibility gate — the lane "
        "would be silently skipped every sprint")
    real = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"
    if real.exists():
        assert status == "ok"
        expected = converter_compat.allowed_pairs(converter_compat.load_matrix(real))
        assert pairs == expected, "packet generator disagrees with the shared checker"


# --------------------------------------------------------------------------
# Duplicate-detector agreement (EP-3 anti-drift)
# --------------------------------------------------------------------------

def _load_supervisor_module(name: str):
    """Import a tools/supervisor module that uses bare sibling imports.

    These modules do `from atomic_io import ...`, so they only import with
    tools/supervisor on sys.path. That is a property of the module under test,
    not a pattern this suite endorses — see the no-sys.path rule the gates
    enforce for product source.
    """
    import importlib
    import sys as _sys
    sup = str(REPO_ROOT / "tools" / "supervisor")
    if sup not in _sys.path:
        _sys.path.insert(0, sup)
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


def test_skill_gate_and_v249_agree_on_product_source():
    """The skill gate and V249 must not disagree about what a violation is.

    TC-PA-009 asked for the skill gate to REUSE the validator's checker. It does
    not: V249 (`tools/supervisor/governance_validators_import_hygiene.py`, landed
    concurrently on 2026-07-17) re-implements AST alias resolution independently
    of `skill_gates/import_hygiene.py`. Two implementations of one rule WILL
    drift — they already differ in scope (V249's `_MUTATING_METHODS` is
    {insert, append, extend}; the gate's adds {remove, pop, clear} plus
    AugAssign / slice-assign / rebind).

    Merging them requires editing the validator module, which is outside this
    taskcard's scope. This test is the containment: it turns silent divergence
    into a red test. If it fails, do not "fix" it by loosening an assertion —
    reconcile the two detectors (preferably by having V249 import the gate's
    checker) and record it in docs/governance/skill-gate-validator-seam.md.
    """
    v249 = _load_supervisor_module("governance_validators_import_hygiene")
    if v249 is None:
        pytest.skip("V249 module not importable (not landed?)")

    src_python = REPO_ROOT / "src" / "python"
    if not src_python.exists():
        pytest.skip("src/python missing")

    theirs = v249.scan_syspath(src_python, REPO_ROOT)
    their_files = set(theirs)
    their_occ = sum(v["occurrences"] for v in theirs.values())

    my_findings = [f for f in import_hygiene.check_paths([src_python])
                   if f.kind not in ("PARSE_ERROR", "READ_ERROR")]
    root = str(REPO_ROOT).replace("\\", "/") + "/"
    my_files = {f.path.replace(root, "") for f in my_findings}

    assert my_files == their_files, (
        "skill gate and V249 disagree on WHICH files mutate sys.path.\n"
        f"  only V249: {sorted(their_files - my_files)[:5]}\n"
        f"  only gate: {sorted(my_files - their_files)[:5]}")
    assert len(my_findings) == their_occ, (
        f"skill gate counts {len(my_findings)} occurrences, V249 counts "
        f"{their_occ} — the two detectors have drifted")


def test_real_registry_blocks_known_meaningless_projections():
    """TC-PA-009 completion criterion: fods->pbm, abw->pbm, toml->ppm blocked."""
    real = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"
    if not real.exists():
        pytest.skip("registry not landed yet (TC-PA-008)")
    for src, tgt in (("fods", "pbm"), ("abw", "pbm"), ("toml", "ppm")):
        res = converter_compat.check_pair(src, tgt, real)
        assert res.verdict == "BLOCK", f"{src}->{tgt} should be blocked, got {res.verdict}"


# --------------------------------------------------------------------------
# dogfood_export_gate composition (TC-PA-009)
# --------------------------------------------------------------------------

def test_dogfood_gate_blocks_incompatible_pair(matrix):
    res = dogfood_export_gate.run("fods", "pbm", [], matrix)
    assert res["verdict"] == "BLOCKED"


def test_dogfood_gate_blocks_toml_to_ppm(matrix):
    """TC-PA-009 completion criterion: the TOML->PPM pair must be blocked."""
    assert dogfood_export_gate.run("toml", "ppm", [], matrix)["verdict"] == "BLOCKED"


def test_dogfood_gate_blocks_compatible_pair_with_dirty_target(tmp_path, matrix):
    """A semantically fine pair still fails if the generated file hacks sys.path."""
    f = tmp_path / "dif_to_csv.py"
    f.write_text(_src("""
        import sys as _sys
        _sys.path.insert(0, "/x")
    """), encoding="utf-8")
    res = dogfood_export_gate.run("dif", "csv", [str(f)], matrix)
    assert res["verdict"] == "BLOCKED"
    assert res["import_hygiene"]["verdict"] == "VIOLATIONS"


def test_dogfood_gate_allows_compatible_pair_with_clean_target(tmp_path, matrix):
    f = tmp_path / "dif_to_csv.py"
    f.write_text(_src("""
        from ff_csv.csv_writer import write_csv

        def dif_to_csv(model, dest):
            return write_csv(model, dest)
    """), encoding="utf-8")
    res = dogfood_export_gate.run("dif", "csv", [str(f)], matrix)
    assert res["verdict"] == "ALLOW", res["reasons"]


def test_dogfood_gate_cli_exit_code_blocked(matrix):
    rc = dogfood_export_gate.main([
        "--source-format", "fods", "--target-format", "pbm", "--matrix", matrix])
    assert rc == 1


# --------------------------------------------------------------------------
# Live-tree corroboration of the plan's measured facts
# --------------------------------------------------------------------------

def test_known_meaningless_projection_is_syspath_dirty():
    """fods_to_pbm.py is both an INCOMPATIBLE pair and sys.path-dirty at HEAD.

    Skipped rather than failed if TC-PA-014/TC-PA-015 have already cleaned it —
    this test corroborates a baseline, it does not demand the defect persist.
    """
    target = REPO_ROOT / "src" / "python" / "fods" / "fods_to_pbm.py"
    if not target.exists():
        pytest.skip("fods_to_pbm.py already removed by converter disposition")
    findings = import_hygiene.check_file(target)
    if not findings:
        pytest.skip("fods_to_pbm.py already cleaned by sys.path elimination")
    assert all(f.kind == "SYSPATH_MUTATION" for f in findings)
