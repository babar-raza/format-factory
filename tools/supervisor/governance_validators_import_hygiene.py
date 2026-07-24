"""governance_validators_import_hygiene.py — V249/V250: product-source import hygiene.

Full-repo-state validators following the V242-V246 pattern
(governance_validators_package_integrity.py): each function IGNORES the
`declaration` argument's scope and performs an unconditional AST scan of every
format package under src/python/ on every invocation. `repo_root` defaults to the
real repo root but may be overridden by tests pointing at a synthetic tmp_path.

V249 (TC-PA-005): validate_no_syspath_mutation_in_product_source
    Product source under src/python/ must not mutate the interpreter-global import
    path. Enforced as a DECREASE-ONLY RATCHET against a frozen per-file baseline
    (registry/governance/syspath-baseline.yaml): any NEW file, or any file exceeding
    its frozen cap, FAILs and blocks the sprint. Pre-existing debt is reported, never
    silently accepted -- the summary always states the live occurrence count.

    Detection is AST-based WITH ALIAS RESOLUTION (PA-F4). `import sys as _sys;
    _sys.path.insert(...)` is a real pattern in this repo and evades naive text
    matching whenever the alias does not itself contain the substring "sys."
    (e.g. `import sys as _s`). Resolving aliases via the AST is the only sound
    detection; see the module docstring of tools/audit/portfolio_forensic_inventory.py.

    Occurrences are classified, and the classification is auditable rather than
    hidden behind a silent exemption (the explicit instruction of TC-PA-005):

      LOAD_BEARING -- the module imports `src.python.*`, which resolves ONLY when
        the repository root is on sys.path. The repo root is NOT injected by the
        editable-install .pth files (they inject src/python and src), so removing
        these inserts silently degrades the module (e.g. `_ff_write_csv = None` in
        src/python/dif/interchange_document.py). These exist ONLY because the `csv`
        package is shadowed by stdlib csv (V250 MODE_1), forcing consumers onto
        `src.python.csv.*` imports. They are removable ONLY after TC-PA-013 renames
        the csv package. Deleting them before then is a regression, not a cleanup.

      REDUNDANT -- every import in the module resolves via the .pth-injected
        src/python entry without any mutation. These are cargo-cult copies of the
        template and are safe to delete (TC-PA-014).

    The classifier is a static approximation and says so: it asks "does this module
    import src.python.*?", which is the empirically-verified discriminator between
    the two classes in this repo (verified 2026-07-17 by importing both classes from
    a neutral cwd; see TC-PA-004 machinery-root-cause-map.yaml).

V250 (TC-PA-007): validate_no_stdlib_namespace_collision
    No package directory under src/python/ may collide with a Python stdlib module
    name or a curated popular-PyPI name. Collisions are detected in BOTH directions
    (the two are mutually exclusive failure modes, not one -- PA-F2):

      MODE_1_UNREACHABLE -- the colliding name resolves to the OTHER module, so our
        package is unreachable under its own name. Measured reality for `csv`:
        stdlib Lib precedes the .pth entry on sys.path, so `import csv` yields
        C:/PythonNNN/Lib/csv.py and `from csv.csv_parser import ...` raises
        ModuleNotFoundError ("csv is not a package").

      MODE_2_HIJACK_RISK -- if our package DID win resolution (which is exactly what
        a sys.path.insert(0, ...) accomplishes), it would shadow the stdlib module
        process-wide for every library in the interpreter. Reported when our package
        does not re-export the stdlib module's public API surface.

    BLOCKING POLICY (revised 2026-07-20, TC-PA-039 review): the two collision
    classes are NOT treated alike. A stdlib collision (`csv`) always produces
    MODE_1 or MODE_2 -- there is no environment where it is safe, so a NEW
    stdlib collision FAILs and blocks; a KNOWN one carries a required migration
    taskcard in registry/governance/namespace-collision-baseline.yaml and WARNs
    pending that migration. A popular-PyPI collision (`toml`) is CONTINGENT on
    that specific distribution actually being installed alongside ours -- absent
    it, our package resolves correctly. Popular-PyPI collisions therefore never
    block, whether or not they are yet recorded in the baseline; they WARN and
    are recorded for visibility, not queued for a mandatory rename.

Both validators fail CLOSED on their own errors: an unreadable baseline or an
unparseable source file is reported, never silently treated as clean (contrast
V149, which returns PASS when its scanner will not import -- see PA-F3).

Reference: tools/supervisor/governance_validators_package_integrity.py (the
full-repo-scan pattern these follow).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import yaml

from governance_validators_contract import validator
from skill_gate_bridge import SkillGateUnavailable, import_hygiene, namespace_collision

# Directory names directly under src/python/ that are infrastructure, not packages.
_NON_FORMAT_DIRS = frozenset({"__pycache__", "build", "dist", ".pytest_cache"})

_SYSPATH_BASELINE_REL = "registry/governance/syspath-baseline.yaml"
_COLLISION_BASELINE_REL = "registry/governance/namespace-collision-baseline.yaml"

# NOTE: the stdlib and popular-PyPI name lists deliberately do NOT live here. They are
# owned by tools/governance/skill_gates/namespace_collision.py so that the creation-time
# gate and V250 classify names identically. That module's lists are the superset (they
# add cross-version stdlib names — tomllib, and modules removed in 3.12/3.13 — which a
# bare sys.stdlib_module_names lookup on the running interpreter would miss).


def _repo_root(repo_root: "Path | None") -> Path:
    return Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent


def _is_infra(path: Path) -> bool:
    return any(part in _NON_FORMAT_DIRS for part in path.parts)


def _iter_product_py(src_python: Path):
    for p in sorted(src_python.rglob("*.py")):
        if not _is_infra(p.relative_to(src_python)):
            yield p


# --------------------------------------------------------------------------
# Detection is DELEGATED — see docs/governance/skill-gate-validator-seam.md.
#
# This module deliberately contains NO sys.path detector. The AST alias-resolving
# detector lives once, in tools/governance/skill_gates/import_hygiene.py, and is
# called by both the creation-time skill gates and by V249. An earlier revision of
# V249 carried its own copy; the two agreed on the tree at the time but differed in
# scope (this one lacked remove/pop/clear, AugAssign, slice-assign and rebind), which
# is latent drift — the failure mode that made GVD-2026-07-17 necessary.
#
# What stays here is the POLICY layer, which the shared gate deliberately has no
# opinion about: the frozen ratchet baseline and the LOAD_BEARING/REDUNDANT
# classification. That split is the correct one — only detection is shared.
# --------------------------------------------------------------------------

def _imports_repo_root_namespace(tree: ast.Module) -> bool:
    """True when the module imports `src.python.*` (resolves only with repo root on sys.path)."""
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            if n.module == "src" or n.module.startswith("src."):
                return True
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "src" or a.name.startswith("src."):
                    return True
    return False


def scan_syspath(src_python: Path, repo: Path) -> dict[str, dict[str, Any]]:
    """Map relative-path -> {occurrences, lines, classification}.

    DETECTION is delegated to the shared skill-gate checker (one rule, one
    implementation). This function adds only V249's policy layer: grouping findings
    per file and classifying each file LOAD_BEARING vs REDUNDANT.

    Raises SkillGateUnavailable if the shared checker cannot be loaded — callers must
    fail closed rather than report an empty (falsely clean) scan.
    """
    gate = import_hygiene()
    out: dict[str, dict[str, Any]] = {}
    for p in _iter_product_py(src_python):
        rel = p.relative_to(repo).as_posix()
        findings = gate.check_file(p)
        if not findings:
            continue

        parse_errs = [f for f in findings if f.kind in ("PARSE_ERROR", "READ_ERROR")]
        if parse_errs:
            out[rel] = {"occurrences": 0, "lines": [], "classification": "PARSE_ERROR",
                        "error": parse_errs[0].snippet}
            continue

        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:  # pragma: no cover — gate would have reported it
            out[rel] = {"occurrences": 0, "lines": [], "classification": "PARSE_ERROR",
                        "error": f"{type(exc).__name__}: {exc}"}
            continue

        out[rel] = {
            "occurrences": len(findings),
            "lines": [f.line for f in findings],
            "kinds": sorted({f.kind for f in findings}),
            "classification": ("LOAD_BEARING" if _imports_repo_root_namespace(tree) else "REDUNDANT"),
        }
    return out


def _load_yaml(path: Path) -> "dict | None":
    if not path.is_file():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None


# --------------------------------------------------------------------------
# V249
# --------------------------------------------------------------------------

@validator(rule_id="V249", domain="import_direction")
def validate_no_syspath_mutation_in_product_source(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V249: no NEW sys.path mutation in src/python/; frozen baseline is decrease-only.

    Unconditional full-repo AST scan; ``declaration`` is ignored by design.
    FAIL when a file absent from the baseline mutates sys.path, or when a
    baselined file exceeds its frozen cap. Pre-existing debt at/below cap is
    reported (never called clean) but does not block -- TC-PA-014 repairs it.
    """
    repo = _repo_root(repo_root)
    src_python = repo / "src" / "python"
    name = "validate_no_syspath_mutation_in_product_source"

    if not src_python.is_dir():
        return {"validator": name, "result": "PASS", "blocks_sprint": False, "items": [],
                "summary": "V249: no src/python/ directory found"}

    baseline_path = repo / _SYSPATH_BASELINE_REL
    baseline = _load_yaml(baseline_path)
    if baseline is None:
        # Fail closed: without the frozen baseline we cannot distinguish new debt
        # from old. Never assume clean (contrast V149's fail-open, PA-F3).
        return {
            "validator": name, "result": "FAIL", "blocks_sprint": True,
            "items": [{"issue": "baseline missing or unparseable", "path": _SYSPATH_BASELINE_REL}],
            "summary": (f"V249: baseline {_SYSPATH_BASELINE_REL} missing/unparseable — "
                        "cannot distinguish new sys.path debt from frozen debt (fail-closed)"),
        }

    caps: dict[str, int] = {
        k: int(v.get("occurrences", 0)) for k, v in (baseline.get("files") or {}).items()
    }
    try:
        live = scan_syspath(src_python, repo)
    except SkillGateUnavailable as exc:
        # The shared detector is the rule. Without it V249 has checked nothing, and an
        # enforcer that has checked nothing must never report clean (PA-F3).
        return {
            "validator": name, "result": "FAIL", "blocks_sprint": True,
            "items": [{"issue": "shared skill-gate checker unavailable", "error": str(exc)}],
            "summary": (f"V249: shared detector tools/governance/skill_gates/import_hygiene.py "
                        f"could not be loaded ({exc}) — sys.path enforcement did NOT run "
                        "(fail-closed)"),
        }

    new_files, exceeded, parse_errors = [], [], []
    load_bearing_occ = redundant_occ = 0
    for rel, info in sorted(live.items()):
        if info["classification"] == "PARSE_ERROR":
            parse_errors.append({"path": rel, "error": info["error"]})
            continue
        occ = info["occurrences"]
        if info["classification"] == "LOAD_BEARING":
            load_bearing_occ += occ
        else:
            redundant_occ += occ
        if rel not in caps:
            new_files.append({"path": rel, "occurrences": occ, "lines": info["lines"],
                              "classification": info["classification"],
                              "issue": "NEW sys.path mutation in product source (not in frozen baseline)"})
        elif occ > caps[rel]:
            exceeded.append({"path": rel, "occurrences": occ, "baseline_cap": caps[rel],
                             "lines": info["lines"],
                             "issue": "sys.path occurrences exceed frozen baseline cap"})

    # Progress detection: ratchet should tighten (WARN only; validators do not write).
    improved = [
        {"path": rel, "occurrences": live.get(rel, {}).get("occurrences", 0), "baseline_cap": cap}
        for rel, cap in sorted(caps.items())
        if live.get(rel, {}).get("occurrences", 0) < cap
    ]

    items = new_files + exceeded + parse_errors
    total_occ = load_bearing_occ + redundant_occ
    total_files = len([r for r, i in live.items() if i["classification"] != "PARSE_ERROR"])

    if items:
        result, blocks = "FAIL", True
        summary = (f"V249: {len(new_files)} file(s) with NEW sys.path mutation, "
                   f"{len(exceeded)} over frozen cap, {len(parse_errors)} parse error(s)")
    elif improved:
        result, blocks = "WARN", False
        summary = (f"V249: no new sys.path debt; {len(improved)} file(s) now BELOW frozen cap — "
                   f"baseline is stale, re-emit it to tighten the ratchet "
                   f"(python tools/supervisor/governance_validators_import_hygiene.py --emit-baseline). "
                   f"Live debt: {total_occ} occurrence(s) in {total_files} file(s) "
                   f"({load_bearing_occ} LOAD_BEARING pending TC-PA-013, {redundant_occ} REDUNDANT pending TC-PA-014)")
    elif total_occ == 0:
        result, blocks = "PASS", False
        summary = "V249: CLEAN — zero sys.path mutations in src/python/ (TC-PA-014 complete)"
    else:
        result, blocks = "PASS", False
        summary = (f"V249: no new sys.path debt. Live debt at frozen baseline: {total_occ} "
                   f"occurrence(s) in {total_files} file(s) — {load_bearing_occ} LOAD_BEARING "
                   f"(removable only after TC-PA-013 renames csv; deleting them now silently "
                   f"degrades imports to None), {redundant_occ} REDUNDANT (safe to delete, TC-PA-014). "
                   f"NOT clean — this is frozen debt, not absence of debt")

    return {"validator": name, "result": result, "blocks_sprint": blocks, "items": items,
            "summary": summary,
            "metrics": {"live_files": total_files, "live_occurrences": total_occ,
                        "load_bearing_occurrences": load_bearing_occ,
                        "redundant_occurrences": redundant_occ,
                        "baseline_files": len(caps), "new_files": len(new_files),
                        "exceeded_files": len(exceeded), "improved_files": len(improved)}}


# --------------------------------------------------------------------------
# V250
# --------------------------------------------------------------------------

def _package_public_names(pkg_dir: Path) -> "tuple[set[str], bool]":
    """Statically-visible public names of a package, and whether the count is trustworthy.

    Returns (names, count_is_determinable).

    A validator must NOT import the package to enumerate its exports: for a colliding
    package that is precisely the MODE_2 hijack (importing src/python/csv/ replaces stdlib
    csv in sys.modules for the rest of the process, including the rest of this sweep).
    So this reads the AST — which has a real limit, and the limit is load-bearing here:

    src/python/csv/__init__.py computes `__all__` as a list COMPREHENSION over
    vars(module), so its true size (119, measured at runtime 2026-07-17) is not knowable
    statically. Reporting the fallback count (3) as "our_export_count" would be a made-up
    number. When __all__ is present but not a literal, this returns determinable=False and
    the caller must not publish a count.

    The MODE_2 VERDICT does not depend on the count — it depends on whether the stdlib's
    public names are re-exported, and a name absent from the static surface AND from the
    package's submodule files is genuinely absent. Verified at runtime for csv:
    `csv.reader` -> AttributeError.
    """
    init = pkg_dir / "__init__.py"
    if not init.is_file():
        return set(), False
    try:
        tree = ast.parse(init.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set(), False

    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    if isinstance(n.value, (ast.List, ast.Tuple)):
                        return ({e.value for e in n.value.elts
                                 if isinstance(e, ast.Constant) and isinstance(e.value, str)}, True)
                    # Computed __all__ (comprehension, concatenation, ...) — the true
                    # surface is a runtime property. Fall through to the static surface
                    # but mark the count untrustworthy.
                    names = _static_surface(tree, pkg_dir)
                    return names, False
    return _static_surface(tree, pkg_dir), True


def _static_surface(tree: ast.Module, pkg_dir: Path) -> set[str]:
    """Top-level defs/classes/re-exports of __init__, plus submodule file names."""
    names: set[str] = set()
    for n in ast.iter_child_nodes(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not n.name.startswith("_"):
            names.add(n.name)
        elif isinstance(n, ast.ImportFrom):
            names.update(a.asname or a.name for a in n.names if not (a.asname or a.name).startswith("_"))
        elif isinstance(n, ast.Import):
            names.update((a.asname or a.name).split(".")[0] for a in n.names
                         if not (a.asname or a.name).startswith("_"))
    # A stdlib name could also be provided as a submodule (e.g. csv/reader.py -> csv.reader).
    names.update(p.stem for p in pkg_dir.glob("*.py") if not p.stem.startswith("_"))
    return names


def _stdlib_public_api(mod_name: str) -> set[str]:
    """Public API of the stdlib module of this name, imported in isolation."""
    try:
        import importlib
        mod = importlib.import_module(mod_name)
    except Exception:
        return set()
    file = getattr(mod, "__file__", "") or ""
    # Only trust it if it really resolved to the stdlib copy, not ours.
    if "src" in Path(file).parts and "python" in Path(file).parts:
        return set()
    declared = getattr(mod, "__all__", None)
    if isinstance(declared, (list, tuple)):
        return {str(x) for x in declared}
    return {n for n in dir(mod) if not n.startswith("_")}


@validator(rule_id="V250", domain="import_direction")
def validate_no_stdlib_namespace_collision(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V250: no src/python/ package may collide with a stdlib or popular-PyPI name.

    Unconditional full-repo scan; ``declaration`` is ignored by design.
    Reports BOTH failure modes (PA-F2): MODE_1_UNREACHABLE (the other module wins
    resolution, so ours is unreachable under its own name) and MODE_2_HIJACK_RISK
    (if ours won, it would shadow the stdlib module process-wide while failing to
    provide its public API). New collisions FAIL; baselined ones WARN and must
    carry a migration taskcard.
    """
    repo = _repo_root(repo_root)
    src_python = repo / "src" / "python"
    name = "validate_no_stdlib_namespace_collision"

    if not src_python.is_dir():
        return {"validator": name, "result": "PASS", "blocks_sprint": False, "items": [],
                "summary": "V250: no src/python/ directory found"}

    baseline = _load_yaml(repo / _COLLISION_BASELINE_REL) or {}
    known: dict[str, dict] = {k: (v or {}) for k, v in (baseline.get("known_collisions") or {}).items()}

    # Name classification is DELEGATED to the shared skill-gate checker (one rule, one
    # implementation). Its lists are the superset: cross-version stdlib names (tomllib,
    # and modules removed in 3.12/3.13) plus a far larger popular-PyPI set than this
    # module carried. V250 layers the RUNTIME failure-mode probe on top — which of the
    # two mutually exclusive modes is actually live right now is a question the
    # creation-time gate cannot ask, because at creation time the package does not exist.
    try:
        collision = namespace_collision()
    except SkillGateUnavailable as exc:
        return {
            "validator": name, "result": "FAIL", "blocks_sprint": True,
            "items": [{"issue": "shared skill-gate checker unavailable", "error": str(exc)}],
            "summary": (f"V250: shared checker tools/governance/skill_gates/namespace_collision.py "
                        f"could not be loaded ({exc}) — collision enforcement did NOT run "
                        "(fail-closed)"),
        }

    items, known_items = [], []
    for pkg_dir in sorted(src_python.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name in _NON_FORMAT_DIRS or pkg_dir.name.startswith(("_", ".")):
            continue
        pkg = pkg_dir.name
        verdict = collision.check_name(pkg)
        if verdict.verdict == collision.VERDICT_OK:
            continue
        is_std = verdict.verdict == collision.VERDICT_STDLIB
        is_pop = verdict.verdict == collision.VERDICT_POPULAR

        modes: list[str] = []
        detail: dict[str, Any] = {"shared_gate_verdict": verdict.verdict}
        if is_std:
            stdlib_api = _stdlib_public_api(pkg)
            if stdlib_api:
                # The stdlib module won resolution -> our package is unreachable.
                modes.append("MODE_1_UNREACHABLE")
                ours, count_ok = _package_public_names(pkg_dir)
                missing = sorted(stdlib_api - ours)
                detail["stdlib_api_count"] = len(stdlib_api)
                if count_ok:
                    detail["our_export_count"] = len(ours)
                else:
                    # Do not publish a number we cannot stand behind (csv computes __all__
                    # at runtime; its real surface is 119, unknowable from the AST).
                    detail["our_export_count"] = None
                    detail["our_export_count_note"] = (
                        "UNDETERMINABLE_STATICALLY: __all__ is computed at runtime. The "
                        "MODE_2 verdict below does not depend on this count.")
                if missing:
                    modes.append("MODE_2_HIJACK_RISK")
                    detail["stdlib_api_not_reexported"] = missing[:12]
        entry = {
            "package": pkg,
            "collides_with": "python_stdlib" if is_std else "popular_pypi",
            "failure_modes": modes or ["NAME_COLLISION_ONLY"],
            "path": pkg_dir.relative_to(repo).as_posix(),
            **detail,
        }
        if pkg in known:
            entry["migration_taskcard"] = known[pkg].get("migration_taskcard", "UNSPECIFIED")
            entry["accepted_reason"] = known[pkg].get("reason", "")
            known_items.append(entry)
        elif is_pop:
            # Popular-PyPI collisions never block (2026-07-20 policy fix, TC-PA-039
            # review): the collision is contingent on that PyPI distribution actually
            # being installed alongside ours, which is not the case for any format
            # package today. WARN-and-record, not FAIL-and-block, even when newly
            # observed (i.e. not yet in the frozen baseline).
            entry["issue"] = "popular-PyPI collision (non-blocking; not yet in baseline)"
            known_items.append(entry)
        else:
            entry["issue"] = "NEW stdlib namespace collision (not in frozen baseline)"
            items.append(entry)

    if items:
        result, blocks = "FAIL", True
        summary = f"V250: {len(items)} NEW namespace collision(s): {', '.join(i['package'] for i in items)}"
    elif known_items:
        result, blocks = "WARN", False
        parts = [f"{i['package']} ({'+'.join(i['failure_modes'])} -> {i.get('migration_taskcard', 'N/A (popular-PyPI, non-blocking)')})"
                 for i in known_items]
        summary = f"V250: {len(known_items)} known/non-blocking collision(s): {', '.join(parts)}"
    else:
        result, blocks = "PASS", False
        summary = "V250: no stdlib/popular-package namespace collisions in src/python/"

    return {"validator": name, "result": result, "blocks_sprint": blocks,
            "items": items + known_items, "summary": summary}


# --------------------------------------------------------------------------
# Baseline emitter — same module that enforces, so the two cannot drift.
# --------------------------------------------------------------------------

def emit_syspath_baseline(repo: Path) -> dict:
    live = scan_syspath(repo / "src" / "python", repo)
    files = {
        rel: {"occurrences": i["occurrences"], "classification": i["classification"]}
        for rel, i in sorted(live.items()) if i["classification"] != "PARSE_ERROR"
    }
    lb = sum(v["occurrences"] for v in files.values() if v["classification"] == "LOAD_BEARING")
    rd = sum(v["occurrences"] for v in files.values() if v["classification"] == "REDUNDANT")
    return {
        "schema_version": "1.0",
        "taskcard": "TC-PA-005",
        "validator": "V249",
        "mission_id": "PORTFOLIO-AUDIT-2026-07-16",
        "authority": (
            "Frozen decrease-only ratchet of pre-existing sys.path mutations in src/python/. "
            "V249 FAILs on any file absent here, or any file exceeding its cap. Caps may only "
            "DECREASE: re-emit after each cleanup batch to tighten the ratchet. Adding a file "
            "here to unblock a sprint is cap-inflation and is prohibited."
        ),
        "totals": {"files": len(files), "occurrences": lb + rd,
                   "load_bearing_occurrences": lb, "redundant_occurrences": rd},
        "classification_semantics": {
            "LOAD_BEARING": (
                "Module imports src.python.*, which resolves ONLY with the repo root on "
                "sys.path. The editable-install .pth injects src/python and src, NOT the repo "
                "root — verified 2026-07-17 from a neutral cwd. Removing these inserts silently "
                "degrades imports (e.g. _ff_write_csv = None). Removable ONLY after TC-PA-013 "
                "renames the csv package, which is what forces src.python.* imports in the "
                "first place (csv is shadowed by stdlib csv — V250 MODE_1)."
            ),
            "REDUNDANT": (
                "Every import resolves via the .pth-injected src/python entry with no mutation "
                "— verified 2026-07-17. Cargo-cult template copies; safe to delete (TC-PA-014)."
            ),
        },
        "files": files,
    }


def _main(argv: "list[str]") -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    if "--emit-baseline" in argv:
        data = emit_syspath_baseline(repo)
        out = repo / _SYSPATH_BASELINE_REL
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(data, sort_keys=False, width=100), encoding="utf-8")
        t = data["totals"]
        print(f"wrote {out.relative_to(repo).as_posix()}: {t['files']} files / "
              f"{t['occurrences']} occurrences "
              f"({t['load_bearing_occurrences']} LOAD_BEARING, {t['redundant_occurrences']} REDUNDANT)")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
