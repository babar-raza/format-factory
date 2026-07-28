"""governance_validators_package_integrity.py — V242/V243/V244: package integrity validators.

Full-repo-state validators modeled on governance_validators_gate9_drift.py's V230 pattern:
each function IGNORES the `declaration` argument's scope entirely and performs an
unconditional glob/scan of every format package under src/python/ on every invocation
(not sprint-scoped). `repo_root` defaults to the real repo root but may be overridden
(e.g. by tests pointing at a synthetic tmp_path fixture).

V242 (package-integrity hardening): validate_exception_class_single_source
    Each format package's exception classes (ClassDef nodes whose name matches
    `^[A-Z]\\w*Error$`) must be defined in exactly one file within that package.
    FAIL when a class of the same name is independently DEFINED (ClassDef, not merely
    imported) in more than one top-level .py file of the same format package -- this
    indicates parser/codec-local duplicate exception hierarchies that shadow the
    canonical definitions in exceptions.py. No grandfather/known-violations suppression:
    this validator reports the true current repo state, including pre-existing
    violations, by design.

V243 (package-integrity hardening): validate_exception_hierarchy_correctness
    Each format package's exceptions.py must define a root exception class (the class
    with no locally-defined base -- i.e. the top of that file's local Error hierarchy)
    that ultimately derives from FormatFactoryError. The documented
    `try: from _shared._shared_exceptions import FormatFactoryError / except ImportError:
    FormatFactoryError = Exception` fallback pattern is accepted as correct -- what
    matters is that the AST base node's name is literally `FormatFactoryError`,
    regardless of how that name is bound above it in the same file. FAIL when the root
    class's base resolves to anything else (e.g. ValueError, Exception) or when no
    root exception class / no exceptions.py can be found at all.

V244 (package-integrity hardening): validate_analytics_module_wiring
    Every `*_analytics*.py` file directly inside a format package directory must be
    imported (as an ImportFrom node) by that package's __init__.py. FAIL when an
    analytics module exists on disk but is never wired into the package's public
    surface (dead/unreachable analytics code).

Reference: tools/supervisor/governance_validators_ext2.py (V76, declaration-scoped shallow
validator pattern -- NOT what these follow) and
tools/supervisor/governance_validators_gate9_drift.py (V230, the full-repo-scan pattern
these DO follow).
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from governance_validators_contract import validator

_ERROR_CLASS_RE = re.compile(r"^[A-Z]\w*Error$")

# Directory names directly under src/python/ that are infrastructure, not format packages.
_NON_FORMAT_DIRS = frozenset({"__pycache__", "build"})


def _repo_root(repo_root: "Path | None") -> Path:
    return Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent


def _is_infra_dir(path: Path) -> bool:
    """True if the path passes through __pycache__ or build directories."""
    return any(p in _NON_FORMAT_DIRS for p in path.parts)


def _iter_format_packages(repo: Path):
    """Yield (pkg_name, pkg_dir) for every real format package under src/python/.

    Skips: __pycache__, build, and directories starting with "_" (e.g. the _shared
    base-exception infra package, which is not itself a format package).
    """
    src_python = repo / "src" / "python"
    if not src_python.is_dir():
        return
    for child in sorted(src_python.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith("_") or name in _NON_FORMAT_DIRS:
            continue
        if _is_infra_dir(child):
            continue
        yield name, child


def _iter_top_level_py_files(pkg_dir: Path):
    """Yield top-level .py files directly inside pkg_dir.

    Non-recursive by construction: pathlib's single-level glob("*.py") never descends
    into subdirectories, so Compat/, spec/, and __pycache__/ are all excluded.
    """
    for f in sorted(pkg_dir.glob("*.py")):
        if f.is_file() and not _is_infra_dir(f):
            yield f


def _iter_analytics_files(pkg_dir: Path):
    for f in sorted(pkg_dir.glob("*_analytics*.py")):
        if f.is_file() and not _is_infra_dir(f):
            yield f


def _parse(path: Path) -> "ast.Module | None":
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _base_name(base: "ast.expr | None") -> "str | None":
    if base is None:
        return None
    try:
        return ast.unparse(base)
    except Exception:
        if isinstance(base, ast.Name):
            return base.id
        if isinstance(base, ast.Attribute):
            return base.attr
        return "<unresolved>"


def _find_root_error_class(tree: "ast.Module", pkg_name: str):
    """Return (class_name, base_name) for the root of the file's local Error hierarchy.

    The "root" is the Error-suffixed class whose base is NOT itself one of the other
    Error-suffixed classes defined in this same file -- i.e. the top of the local
    hierarchy, the class whose base is an external name like FormatFactoryError,
    ValueError, or Exception. Returns None if the file defines no Error-suffixed class.
    """
    classes: dict[str, "str | None"] = {}
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and _ERROR_CLASS_RE.match(node.name)):
            continue
        if node.name == "FormatFactoryError":
            # The universal base class itself is never the subject of this check --
            # some packages redundantly re-declare it locally (instead of importing/
            # aliasing it via the documented try/except pattern); it must not be
            # mistaken for THIS package's own root error class.
            continue
        classes[node.name] = _base_name(node.bases[0]) if node.bases else None
    if not classes:
        return None
    local_names = set(classes)
    roots = [name for name, base in classes.items() if base not in local_names]
    if not roots:
        # Every Error class bases on another local Error class (a cycle or otherwise
        # malformed hierarchy) -- fall back to the first defined class so this is still
        # reported rather than silently skipped.
        first = next(iter(classes))
        return first, classes[first]
    expected_name = pkg_name[:1].upper() + pkg_name[1:].lower() + "Error"
    if expected_name in roots:
        return expected_name, classes[expected_name]
    return roots[0], classes[roots[0]]


@validator(rule_id="V242", domain="governance")
def validate_exception_class_single_source(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V242: each exception class name must be DEFINED in only one file per format package.

    Unconditional full-repo scan; `declaration` is ignored by design (see module docstring).
    FAIL (no WARN tier, no grandfather list) when a ClassDef matching `^[A-Z]\\w*Error$` is
    defined more than once, in different top-level .py files, within the same package --
    e.g. a parser module re-declaring `PbmError` instead of importing it from exceptions.py.
    """
    repo = _repo_root(repo_root)
    items: list[dict] = []
    for pkg_name, pkg_dir in _iter_format_packages(repo):
        definitions: dict[str, list[str]] = {}
        for py_file in _iter_top_level_py_files(pkg_dir):
            tree = _parse(py_file)
            if tree is None:
                continue
            try:
                rel = str(py_file.relative_to(repo).as_posix())
            except ValueError:
                rel = str(py_file.as_posix())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and _ERROR_CLASS_RE.match(node.name):
                    definitions.setdefault(node.name, []).append(rel)
        for class_name, files in sorted(definitions.items()):
            if len(files) > 1:
                items.append({
                    "package": pkg_name,
                    "class_name": class_name,
                    "defined_in": files,
                })

    result = "FAIL" if items else "PASS"
    return {
        "validator": "validate_exception_class_single_source",
        "result": result,
        "blocks_sprint": bool(items),
        "items": items,
        "summary": (
            f"V242: {len(items)} exception class(es) independently defined in more than "
            "one file within their format package"
            if items else
            "V242: every exception class has a single definition source within its package"
        ),
    }


@validator(rule_id="V243", domain="governance")
def validate_exception_hierarchy_correctness(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V243: each package's root exception class must derive from FormatFactoryError.

    Unconditional full-repo scan; `declaration` is ignored by design (see module docstring).
    FAIL when the root of exceptions.py's local Error hierarchy bases on anything other
    than FormatFactoryError (e.g. ValueError, Exception directly), or when exceptions.py
    is missing or defines no Error-suffixed class at all.
    """
    repo = _repo_root(repo_root)
    items: list[dict] = []
    for pkg_name, pkg_dir in _iter_format_packages(repo):
        exc_file = pkg_dir / "exceptions.py"
        try:
            rel = str(exc_file.relative_to(repo).as_posix())
        except ValueError:
            rel = str(exc_file.as_posix())
        if not exc_file.is_file():
            items.append({
                "package": pkg_name,
                "class_name": None,
                "actual_base": "<exceptions.py missing>",
                "expected_base": "FormatFactoryError",
                "file": rel,
            })
            continue
        tree = _parse(exc_file)
        if tree is None:
            items.append({
                "package": pkg_name,
                "class_name": None,
                "actual_base": "<exceptions.py unparsable>",
                "expected_base": "FormatFactoryError",
                "file": rel,
            })
            continue
        root = _find_root_error_class(tree, pkg_name)
        if root is None:
            items.append({
                "package": pkg_name,
                "class_name": None,
                "actual_base": "<no root exception class found>",
                "expected_base": "FormatFactoryError",
                "file": rel,
            })
            continue
        class_name, base_name = root
        if base_name != "FormatFactoryError":
            items.append({
                "package": pkg_name,
                "class_name": class_name,
                "actual_base": base_name if base_name is not None else "<no base>",
                "expected_base": "FormatFactoryError",
                "file": rel,
            })

    result = "FAIL" if items else "PASS"
    return {
        "validator": "validate_exception_hierarchy_correctness",
        "result": result,
        "blocks_sprint": bool(items),
        "items": items,
        "summary": (
            f"V243: {len(items)} format package(s) whose root exception class does not "
            "derive from FormatFactoryError"
            if items else
            "V243: every package's root exception class derives from FormatFactoryError"
        ),
    }


@validator(rule_id="V244", domain="governance")
def validate_analytics_module_wiring(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V244: every *_analytics*.py file must be imported by its package's __init__.py.

    Unconditional full-repo scan; `declaration` is ignored by design (see module docstring).
    FAIL when an analytics module exists on disk directly inside a format package but is
    never referenced by an ImportFrom node in that package's __init__.py (dead code that
    is never reachable via the package's public API).
    """
    repo = _repo_root(repo_root)
    items: list[dict] = []
    for pkg_name, pkg_dir in _iter_format_packages(repo):
        analytics_files = list(_iter_analytics_files(pkg_dir))
        if not analytics_files:
            continue

        init_file = pkg_dir / "__init__.py"
        imported_modules: set[str] = set()
        if init_file.is_file():
            tree = _parse(init_file)
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            # Match on the last dotted segment so both the relative
                            # style (`from .foo_analytics import *`, module="foo_analytics")
                            # and the absolute style used by newer packages
                            # (`from pkg.foo_analytics import x`, module="pkg.foo_analytics")
                            # resolve to the same module name.
                            imported_modules.add(node.module.rsplit(".", 1)[-1])
                        else:
                            for alias in node.names:
                                imported_modules.add(alias.name)

        for af in analytics_files:
            mod_name = af.stem
            if mod_name not in imported_modules:
                try:
                    rel = str(af.relative_to(repo).as_posix())
                except ValueError:
                    rel = str(af.as_posix())
                items.append({
                    "package": pkg_name,
                    "unwired_file": rel,
                })

    result = "FAIL" if items else "PASS"
    return {
        "validator": "validate_analytics_module_wiring",
        "result": result,
        "blocks_sprint": bool(items),
        "items": items,
        "summary": (
            f"V244: {len(items)} analytics module(s) not wired into their package's "
            "__init__.py"
            if items else
            "V244: every analytics module is wired into its package's __init__.py"
        ),
    }


# TC-PA-041: the oracle-package.yaml `status:` field was a DUPLICATE MIRROR of the
# registry's `product_oracle_status` with no producer — a static template literal
# (commit 1adfdc47's select-6 onboarding wrote `status: VERIFIED` into 6 packages
# whose oracles had actually run 1/5 PASS). TC-PA-031 guarded the drift; TC-PA-041
# ELIMINATED the source: the mirror field was removed from all packages and its only
# consumer (tools/oracle/calculate_oracle_coverage.py) now reads product_oracle_status
# from the registry. The DESIRED state is therefore no `status:` field at all.
#
# This validator now guards REINTRODUCTION: if a revert-to-HEAD or a re-onboard writes
# a `status:` back into a package and it contradicts the registry, that is drift ->
# FAIL. A reintroduced-but-matching value is tolerated (harmless); absence is the goal.
# The registry (`product_oracle_status`: VERIFIED, CASES_DEFINED, OBLIGATION_CREATED)
# remains the single source of truth. Only CASES_DEFINED/VERIFIED are comparable to a
# reintroduced package value; other pairs are reported, never silently passed.
_ORACLE_STATUS_SHARED_VOCAB = frozenset({"CASES_DEFINED", "VERIFIED"})


@validator(rule_id="V245", domain="oracle")
def validate_oracle_registry_reconciliation(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V245: oracle-package.yaml must reconcile with its registry entry.

    Checks:
      1. (original) on-disk oracle-package.yaml has a non-null registry entry -> WARN
      2. (TC-PA-031/TC-PA-041) the duplicate package `status:` mirror is eliminated.
         Absence is the reconciled state. If a package RE-INTRODUCES a `status:` that
         contradicts registry `product_oracle_status` (shared vocabulary) -> FAIL,
         blocks_sprint=True. A reintroduced-but-matching value is tolerated.

    Authority: `oracle/registry/format-oracle-registry.yaml` is the single source of
    truth for oracle status. It is declared so in oracle/reports/final-oracle-audit.md,
    it is the iteration root of /detect-stale-oracles, /generate-oracle-verdict-report
    and /calculate-oracle-coverage, and it is the only side read by a BLOCKING validator
    (V145 validate_future_format_oracle_onboarding). It alone carries the audit trail:
    depth_achieved, current_proof_level, blockers, terminal_state.

    The package `status:` WAS a DERIVED MIRROR with no producer. Nothing promoted it from
    evidence: scaffold_oracle_obligation.py writes a constant, and the select-6
    acquisition generator emitted `status: VERIFIED` as a template literal at authoring
    time. That is exactly how ipynb, mtlx, nrrd, safetensors, ubl and xliff came to claim
    VERIFIED on the day their oracles actually ran 1/5 PASS + 4 NOT_APPLICABLE, while the
    registry honestly recorded CASES_DEFINED at proof level 1 of 4. TC-PA-031 guarded that
    drift but the field kept reverting (the fix was never committed; HEAD still carried
    VERIFIED), so TC-PA-041 removed the SOURCE: the mirror field was deleted from every
    package and calculate_oracle_coverage.py repointed at the registry.

    With the field gone, the false-green surface no longer exists — `summary.verified_formats`
    derives from product_oracle_status directly. This check now exists only to catch a
    REINTRODUCTION of the mirror (revert-to-HEAD / re-onboard) that contradicts the registry.
    """
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent

    registry_path = repo / "oracle" / "registry" / "format-oracle-registry.yaml"
    if not registry_path.exists():
        return {
            "validator": "validate_oracle_registry_reconciliation",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V245: no oracle registry found — skipped",
        }

    try:
        import yaml
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "validator": "validate_oracle_registry_reconciliation",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V245: oracle registry unreadable: {exc}",
        }

    formats_dir = repo / "oracle" / "formats"
    if not formats_dir.is_dir():
        return {
            "validator": "validate_oracle_registry_reconciliation",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V245: no oracle/formats/ directory — skipped",
        }

    reg_entries = {}
    for entry in (registry.get("format_oracles") or []):
        fid = entry.get("format_id", "")
        reg_entries[fid] = entry

    mismatches = []
    status_drift = []
    checked = 0
    for fmt_dir in sorted(formats_dir.iterdir()):
        if not fmt_dir.is_dir():
            continue
        pkg_path = fmt_dir / "oracle-package.yaml"
        if not pkg_path.exists():
            continue
        fmt = fmt_dir.name
        reg = reg_entries.get(fmt)
        if reg is None:
            mismatches.append({"format": fmt, "issue": "on-disk oracle-package.yaml but no registry entry"})
            continue
        if not reg.get("oracle_package"):
            mismatches.append({"format": fmt, "issue": "oracle_package is null despite on-disk file"})

        # TC-PA-031: status must not contradict the authoritative registry.
        try:
            pkg_doc = yaml.safe_load(pkg_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            mismatches.append({"format": fmt, "issue": f"oracle-package.yaml unreadable: {exc}"})
            continue

        pkg_status = pkg_doc.get("status")
        reg_status = reg.get("product_oracle_status")
        checked += 1

        if pkg_status is None:
            # TC-PA-041 DESIRED STATE: the duplicate `status:` mirror has been eliminated
            # from oracle-package.yaml (its only consumer, calculate_oracle_coverage.py,
            # now reads product_oracle_status from the registry). Absence IS reconciliation
            # — there is no longer a package-authored value that can drift or go false-green.
            pass  # reconciled (mirror removed)
        elif pkg_status == reg_status:
            pass  # reconciled (mirror reintroduced but matching)
        elif pkg_status in _ORACLE_STATUS_SHARED_VOCAB and reg_status in _ORACLE_STATUS_SHARED_VOCAB:
            # REINTRODUCTION GUARD (TC-PA-041): the mirror field was removed, but a
            # revert-to-HEAD or a re-onboard has written a conflicting `status:` back in.
            # Both sides speak the shared vocabulary and disagree -> hard contradiction.
            status_drift.append({
                "format": fmt,
                "issue": "STATUS_DRIFT: oracle-package.yaml re-introduced a status that contradicts the authoritative registry",
                "package_status": pkg_status,
                "registry_product_oracle_status": reg_status,
                "authority": "oracle/registry/format-oracle-registry.yaml",
                "depth_achieved": reg.get("depth_achieved"),
                "current_proof_level": reg.get("current_proof_level"),
                "target_proof_level": reg.get("target_proof_level"),
                "blockers": reg.get("blockers") or [],
                "remedy": (
                    f"remove the re-introduced `status:` field from oracle/formats/{fmt}/oracle-package.yaml "
                    "(TC-PA-041 eliminated this mirror; the registry is authoritative and coverage reads "
                    "product_oracle_status directly — do NOT promote the registry to match the package)"
                ),
            })
        else:
            # One side uses a value the other vocabulary cannot express. Not silently OK.
            mismatches.append({
                "format": fmt,
                "issue": "UNCOMPARABLE_STATUS_VOCABULARY: reconcile manually",
                "package_status": pkg_status,
                "registry_product_oracle_status": reg_status,
            })

    if status_drift:
        drifting = ", ".join(f"{d['format']}({d['package_status']}!={d['registry_product_oracle_status']})"
                             for d in status_drift)
        return {
            "validator": "validate_oracle_registry_reconciliation",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": status_drift + mismatches,
            "summary": (
                f"V245 STATUS_DRIFT: {len(status_drift)} oracle package(s) re-introduced a "
                f"`status:` mirror that contradicts format-oracle-registry.yaml (authoritative): "
                f"{drifting}. TC-PA-041 removed this duplicate field; a revert-to-HEAD or a "
                "re-onboard has written it back. Remove the `status:` field from the package — "
                "the registry is the single source of truth."
            ),
        }

    result = "WARN" if mismatches else "PASS"
    return {
        "validator": "validate_oracle_registry_reconciliation",
        "result": result,
        "blocks_sprint": False,
        "items": mismatches,
        "summary": (
            f"V245: {len(mismatches)} format(s) have oracle-package.yaml on disk "
            "but stale/missing registry entries"
            if mismatches else
            f"V245: all {checked} on-disk oracle packages reconcile with the registry "
            "(status mirror removed per TC-PA-041, or — if reintroduced — matching "
            "product_oracle_status)"
        ),
    }


@validator(rule_id="V246", domain="governance")
def validate_no_nested_duplicate_packages(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V246: no format package directory may contain a same-named child directory.

    Unconditional full-repo scan; ``declaration`` is ignored by design.
    FAIL when any directory under src/python/ contains a child directory with the
    same name (e.g. src/python/fods/fods/). Such nested duplicates are structural
    violations that indicate stale copies, packaging artifacts, or migration remnants.

    This validator fails closed: it does NOT skip, exclude, or silently accept
    nested duplicates. Any such structure must be removed or formally resolved
    before the sprint can proceed.
    """
    repo = _repo_root(repo_root)
    src_python = repo / "src" / "python"
    items: list[dict] = []

    if not src_python.is_dir():
        return {
            "validator": "validate_no_nested_duplicate_packages",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V246: no src/python/ directory found",
        }

    for pkg_dir in sorted(src_python.iterdir()):
        if not pkg_dir.is_dir():
            continue
        name = pkg_dir.name
        if name.startswith("_") or name in _NON_FORMAT_DIRS:
            continue
        nested = pkg_dir / name
        if nested.is_dir():
            nested_files = [
                str(f.relative_to(repo).as_posix())
                for f in sorted(nested.rglob("*"))
                if f.is_file() and "__pycache__" not in f.parts
            ]
            items.append({
                "package": name,
                "nested_path": str(nested.relative_to(repo).as_posix()),
                "file_count": len(nested_files),
                "files": nested_files[:10],
            })

    result = "FAIL" if items else "PASS"
    return {
        "validator": "validate_no_nested_duplicate_packages",
        "result": result,
        "blocks_sprint": bool(items),
        "items": items,
        "summary": (
            f"V246: {len(items)} format package(s) contain nested duplicate directories"
            if items else
            "V246: no nested duplicate package directories found"
        ),
    }
