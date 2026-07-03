"""governance_validators_ext3.py — V100-V109: Product Code Quality Validators (TC-PQLM-012)

Added 2026-07-03 as part of PQLM-001 product library code-writing and architecture healing.

V100 (TC-PQLM-012): validate_suspicious_filenames
    RULE-PQLM-001 — Block *ExtendedApis*, *MissingMethods*, *Misc*, *Helpers*, *Stubs* in product src.
    blocks_sprint=True.

V101 (TC-PQLM-012): validate_history_identifiers_in_source
    RULE-PQLM-002 — Scan product .py/.cs for free-form sprint/wave/train/run IDs in comments.
    blocks_sprint=False (WARN — requires manual review due to false positive risk).

V102 (TC-PQLM-012): validate_undocumented_public_python_apis
    RULE-PQLM-003 — Block public def in product .py without docstring.
    blocks_sprint=True for NEW files; WARN for existing known_violations.

V103 (TC-PQLM-012): validate_ungoverned_todo_markers
    RULE-PQLM-004 — Block TODO/FIXME/HACK in product source without GAP-*/TC-* reference.
    blocks_sprint=False (WARN — high false positive risk on legacy code).

V104 (TC-PQLM-012): validate_constant_return_public_methods
    RULE-PQLM-005 — Detect public Python functions that always return a literal constant.
    blocks_sprint=True for NEW files only.

V105 (TC-PQLM-012): validate_getter_without_parser_source
    RULE-PQLM-006 — Detect .cs public getters reading from private _dict fields.
    blocks_sprint=True.

V106 (TC-PQLM-012): validate_setter_without_writer_path
    RULE-PQLM-007 — Detect .cs public setters writing only to private _dict fields.
    blocks_sprint=True.

V107 (TC-PQLM-012): validate_test_only_public_apis
    RULE-PQLM-008 — Detect public Python/C# APIs referenced only in test files.
    blocks_sprint=False (WARN — expensive scan).

V108 (TC-PQLM-012): validate_detached_persistent_state
    RULE-PQLM-009 — Detect Dictionary<string, X?> _field = new() patterns in .cs product source.
    blocks_sprint=True for NEW violations.

V109 (TC-PQLM-012): validate_files_outside_approved_layout
    RULE-PQLM-010 — Check product source file paths against product-file-layout-contract.yaml.
    blocks_sprint=True for NEW files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


_PRODUCT_SRC_ROOTS = ("src/python", "src/net")

_SUSPICIOUS_PATTERNS = [
    # Case-insensitive substring patterns for dumping-ground filename stems
    "extendedapis", "missingmethods", "misc", "helpers", "stubs",
    "utils", "extra",
]
_SUSPICIOUS_FILENAME_PATTERNS = [
    # Regex patterns for sprint/wave/train/gate/R-number identifiers in filenames
    re.compile(r"sprint\d+", re.IGNORECASE),
    re.compile(r"wave\d+", re.IGNORECASE),
    re.compile(r"train[a-z]", re.IGNORECASE),
    re.compile(r"gate\d+", re.IGNORECASE),
    re.compile(r"r\d{3}", re.IGNORECASE),
]
_SPRINT_ID_PATTERNS = [
    re.compile(r"\bSprint\s*\d+\b", re.IGNORECASE),
    re.compile(r"\bWave\s*\d+\b", re.IGNORECASE),
    re.compile(r"\bTrain\s+[A-Z]\b"),
    re.compile(r"\bGI-[A-Z]+-[A-Z]+-[0-9]+\s+Phase\b"),
    re.compile(r"\bR[0-9]{3}\s+Train\b"),
    re.compile(r"\bPhase\s+\d+[a-z]?\b", re.IGNORECASE),
    re.compile(r"\bR\d{3}\s+sprint\b", re.IGNORECASE),
]
_GOVERNED_TODO_PATTERN = re.compile(r"(?:TODO|FIXME|HACK)\s*\(\s*(?:GAP-|PCG-|TC-)", re.IGNORECASE)
_RAW_TODO_PATTERN = re.compile(r"(?:#|//)\s*(?:TODO|FIXME|HACK)\b", re.IGNORECASE)
_DICT_GETTER_PATTERN = re.compile(
    r"_[a-z][a-zA-Z0-9]+\.(?:TryGetValue|ContainsKey|get\b|\[)",
)
_DICT_SETTER_PATTERN = re.compile(
    r"_[a-z][a-zA-Z0-9]+\s*\[",
)
_DICT_FIELD_PATTERN = re.compile(
    r"private\s+(?:readonly\s+)?Dictionary<[^>]+>\s+_[a-z][a-zA-Z0-9]+\s*=\s*new\s*\(\s*\)\s*;",
)


def _is_product_source(path: Path, repo_root: Path) -> bool:
    """Return True if the path is inside a product source root."""
    try:
        rel = path.relative_to(repo_root)
        return any(str(rel).startswith(root) for root in _PRODUCT_SRC_ROOTS)
    except ValueError:
        return False


def _load_baseline(repo_root: Path) -> dict:
    import json
    bp = repo_root / "registry" / "source-structure-baseline.json"
    if not bp.exists():
        return {"known_violations": {}}
    try:
        import re as _re
        txt = bp.read_text(encoding="utf-8", errors="replace")
        txt = _re.sub(r",\s*([}\]])", r"\1", txt)
        return json.loads(txt)
    except Exception:
        return {"known_violations": {}}


def validate_suspicious_filenames(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V100: Product source files must not have dumping-ground filename patterns.

    Blocks *ExtendedApis*, *MissingMethods*, *Misc*, *Helpers*, *Stubs*, *Utils*, *Extra*.
    blocks_sprint=True.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    violations = []

    for root in _PRODUCT_SRC_ROOTS:
        src_dir = _r / root
        if not src_dir.exists():
            continue
        for f in src_dir.rglob("*"):
            if f.suffix not in (".py", ".cs"):
                continue
            name_lower = f.stem.lower()
            # Check dumping-ground substring patterns (case-insensitive)
            if any(pat in name_lower for pat in _SUSPICIOUS_PATTERNS):
                violations.append(f.relative_to(_r).as_posix())
                continue
            # Check sprint/wave/train/gate/R-number filename regex patterns
            if any(rx.search(f.stem) for rx in _SUSPICIOUS_FILENAME_PATTERNS):
                violations.append(f.relative_to(_r).as_posix())

    if violations:
        return {
            "validator_id": "V100",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations,
            "summary": (
                f"V100: {len(violations)} product source file(s) have prohibited dumping-ground "
                f"filename patterns ({', '.join(_SUSPICIOUS_PATTERNS)}): {violations[:5]}"
            ),
        }
    return {
        "validator_id": "V100",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V100: No suspicious filename patterns found in product source",
    }


def validate_history_identifiers_in_source(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V101: Product source must not contain sprint/wave/train history identifiers in comments.

    WARN only (not blocking) due to false positive risk on legitimate references.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    violations = []

    for root in _PRODUCT_SRC_ROOTS:
        src_dir = _r / root
        if not src_dir.exists():
            continue
        for f in src_dir.rglob("*"):
            if f.suffix not in (".py", ".cs"):
                continue
            if "test" in f.name.lower() or "spec" in f.name.lower():
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                for pat in _SPRINT_ID_PATTERNS:
                    if pat.search(content):
                        violations.append(f.relative_to(_r).as_posix())
                        break
            except Exception:
                continue

    if violations:
        return {
            "validator_id": "V101",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations,
            "summary": (
                f"V101: {len(violations)} product source file(s) contain sprint/wave/train "
                f"history identifiers. Review and replace with governed GAP-* references."
            ),
        }
    return {
        "validator_id": "V101",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V101: No sprint/wave/train history identifiers found in product source",
    }


def validate_undocumented_public_python_apis(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V102: Public Python functions in product source must have docstrings.

    FAIL for new files; WARN for existing known_violations (grandfathered).
    blocks_sprint=True for new files.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    baseline = _load_baseline(_r)
    known = set(baseline.get("known_violations", {}).keys())
    violations_new = []
    violations_existing = []

    src_dir = _r / "src" / "python"
    if not src_dir.exists():
        return {
            "validator_id": "V102",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V102: No src/python directory found",
        }

    for f in src_dir.rglob("*.py"):
        if "test" in f.parts or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(_r).as_posix()
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue  # private
            if not (isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                entry = f"{rel}:{node.lineno}:{node.name}"
                if rel in known:
                    violations_existing.append(entry)
                else:
                    violations_new.append(entry)

    if violations_new:
        return {
            "validator_id": "V102",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations_new": violations_new[:20],
            "violations_grandfathered": len(violations_existing),
            "summary": (
                f"V102: {len(violations_new)} new public Python function(s) missing docstrings "
                f"(+ {len(violations_existing)} grandfathered). New files must have docstrings."
            ),
        }
    if violations_existing:
        return {
            "validator_id": "V102",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations_existing[:10],
            "summary": (
                f"V102: {len(violations_existing)} grandfathered public Python function(s) "
                f"missing docstrings. Address when files are next modified."
            ),
        }
    return {
        "validator_id": "V102",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V102: All public Python functions in product source have docstrings",
    }


def validate_ungoverned_todo_markers(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V103: TODO/FIXME/HACK markers must include a GAP-* or TC-* reference.

    WARN only (not blocking) due to high legacy count.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    violations = []

    for root in _PRODUCT_SRC_ROOTS:
        src_dir = _r / root
        if not src_dir.exists():
            continue
        for f in src_dir.rglob("*"):
            if f.suffix not in (".py", ".cs"):
                continue
            if "test" in f.name.lower():
                continue
            try:
                for i, line in enumerate(
                    f.read_text(encoding="utf-8", errors="replace").splitlines(), 1
                ):
                    if _RAW_TODO_PATTERN.search(line):
                        if not _GOVERNED_TODO_PATTERN.search(line):
                            violations.append(f"{f.relative_to(_r).as_posix()}:{i}")
            except Exception:
                continue

    if violations:
        return {
            "validator_id": "V103",
            "status": "WARN",
            "blocks_sprint": False,
            "violation_count": len(violations),
            "violations_sample": violations[:10],
            "summary": (
                f"V103: {len(violations)} ungoverned TODO/FIXME/HACK markers found "
                f"(missing GAP-*/TC-* reference). Use // TODO(GAP-PCG-NNN): format."
            ),
        }
    return {
        "validator_id": "V103",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V103: All TODO/FIXME/HACK markers have governed references",
    }


def validate_constant_return_public_methods(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V104: Public Python functions that return only a literal constant are semantic stubs.

    FAIL for new files; WARN for known_violations grandfathered files.
    blocks_sprint=True for new files.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    baseline = _load_baseline(_r)
    known = set(baseline.get("known_violations", {}).keys())
    violations_new = []
    violations_existing = []

    src_dir = _r / "src" / "python"
    if not src_dir.exists():
        return {
            "validator_id": "V104",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V104: No src/python directory",
        }

    for f in src_dir.rglob("*.py"):
        if "test" in f.parts or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(_r).as_posix()
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            # Find functions whose body is just: [possibly docstring,] return <literal>
            body = node.body
            if len(body) == 1 and isinstance(body[0], ast.Return):
                val = body[0].value
                if isinstance(val, (ast.Constant, ast.List, ast.Dict, ast.Tuple)) and (
                    not isinstance(val, ast.List) or len(val.elts) == 0
                ):
                    entry = f"{rel}:{node.lineno}:{node.name}"
                    if rel in known:
                        violations_existing.append(entry)
                    else:
                        violations_new.append(entry)
            elif len(body) == 2 and isinstance(body[0], ast.Expr) and isinstance(body[1], ast.Return):
                val = body[1].value
                if isinstance(val, (ast.Constant,)) or (
                    isinstance(val, ast.List) and len(val.elts) == 0
                ):
                    entry = f"{rel}:{node.lineno}:{node.name}"
                    if rel in known:
                        violations_existing.append(entry)
                    else:
                        violations_new.append(entry)

    if violations_new:
        return {
            "validator_id": "V104",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations_new": violations_new[:20],
            "violations_grandfathered": len(violations_existing),
            "summary": (
                f"V104: {len(violations_new)} new public Python function(s) return only a "
                f"literal constant (semantic stub). Implement or remove."
            ),
        }
    if violations_existing:
        return {
            "validator_id": "V104",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations_existing[:10],
            "summary": (
                f"V104: {len(violations_existing)} grandfathered semantic stub function(s) "
                f"found. Address when files are next modified."
            ),
        }
    return {
        "validator_id": "V104",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V104: No constant-return public methods found",
    }


def validate_getter_without_parser_source(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V105: .cs public getters that read from private dict fields (not XML) are detached state.

    Detects the pattern: public X? GetY(...) => _dict[...] or _dict.TryGetValue(...).
    blocks_sprint=True for NEW .cs files; WARN for existing.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    baseline = _load_baseline(_r)
    known = set(baseline.get("known_violations", {}).keys())
    violations_new = []
    violations_existing = []

    src_dir = _r / "src" / "net"
    if not src_dir.exists():
        return {
            "validator_id": "V105",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V105: No src/net directory",
        }

    # Regex to detect: public [type] GetXxx(...) => _field.TryGetValue or _field[
    _pub_getter = re.compile(
        r"public\s+\S+\s+Get[A-Z]\w*\s*\([^)]*\)\s*(?:=>|{)[^}]*"
        r"_[a-z]\w+\.(?:TryGetValue|ContainsKey)|"
        r"_[a-z]\w+\s*\[",
        re.DOTALL,
    )
    for f in src_dir.rglob("*.cs"):
        if "test" in f.name.lower() or "Test" in f.name:
            continue
        rel = f.relative_to(_r).as_posix()
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Find public GetXxx methods
        matches = re.finditer(
            r"public\s+[\w\?<>]+\???\s+(Get[A-Z]\w*)\s*\([^)]*\)",
            content,
        )
        for m in matches:
            method_name = m.group(1)
            # Get the next 5 lines after the method signature
            start = m.end()
            snippet = content[start:start + 300]
            if _DICT_GETTER_PATTERN.search(snippet):
                entry = f"{rel}:{method_name}"
                if rel in known:
                    violations_existing.append(entry)
                else:
                    violations_new.append(entry)

    if violations_new:
        return {
            "validator_id": "V105",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations_new[:20],
            "summary": (
                f"V105: {len(violations_new)} public .cs getter(s) read from private dict fields "
                f"instead of XML — detached state. Implement XML read path or remove."
            ),
        }
    if violations_existing:
        return {
            "validator_id": "V105",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations_existing[:10],
            "summary": (
                f"V105: {len(violations_existing)} grandfathered .cs getter(s) with detached dict reads. "
                f"Address in TC-PQLM-015 FODS rebuild."
            ),
        }
    return {
        "validator_id": "V105",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V105: No detached-state getters found in .cs product source",
    }


def validate_setter_without_writer_path(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V106: .cs public setters that write only to private dict fields have no XML writer path.

    Detects: public void SetXxx(...) { _dict[...] = ... } with no SetAttributeValue call.
    blocks_sprint=True for NEW .cs files; WARN for existing.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    baseline = _load_baseline(_r)
    known = set(baseline.get("known_violations", {}).keys())
    violations_new = []
    violations_existing = []

    src_dir = _r / "src" / "net"
    if not src_dir.exists():
        return {
            "validator_id": "V106",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V106: No src/net directory",
        }

    _xml_write_patterns = re.compile(r"SetAttributeValue|XElement|\.Add\(|\.Value\s*=")

    for f in src_dir.rglob("*.cs"):
        if "test" in f.name.lower() or "Test" in f.name:
            continue
        rel = f.relative_to(_r).as_posix()
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for m in re.finditer(
            r"public\s+void\s+(Set[A-Z]\w*)\s*\([^)]*\)",
            content,
        ):
            method_name = m.group(1)
            start = m.end()
            snippet = content[start:start + 400]
            if _DICT_SETTER_PATTERN.search(snippet) and not _xml_write_patterns.search(snippet):
                entry = f"{rel}:{method_name}"
                if rel in known:
                    violations_existing.append(entry)
                else:
                    violations_new.append(entry)

    if violations_new:
        return {
            "validator_id": "V106",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations_new[:20],
            "summary": (
                f"V106: {len(violations_new)} public .cs setter(s) write to dict only (no XML path) "
                f"— semantic stubs. Implement XML write path or remove."
            ),
        }
    if violations_existing:
        return {
            "validator_id": "V106",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations_existing[:10],
            "summary": (
                f"V106: {len(violations_existing)} grandfathered setter(s) with no XML write path. "
                f"Address in TC-PQLM-015 FODS rebuild."
            ),
        }
    return {
        "validator_id": "V106",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V106: No dict-only setter patterns found in .cs product source",
    }


def validate_test_only_public_apis(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V107: Public Python APIs referenced only in test files are test-shaped APIs (advisory).

    WARN only — requires cross-file analysis. blocks_sprint=False.
    """
    # This validator requires expensive cross-file grep analysis.
    # Implemented as a best-effort heuristic: functions in analytics/codec files that have
    # zero references in non-test source files.
    _r = repo_root or Path(__file__).parent.parent.parent
    src_dir = _r / "src" / "python"
    test_dir = _r / "tests" / "python"
    if not src_dir.exists():
        return {
            "validator_id": "V107",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V107: No src/python directory (skipped)",
        }

    # Collect all public function names defined in product source
    product_api_names: dict[str, str] = {}  # name -> source file
    for f in src_dir.rglob("*.py"):
        if "__pycache__" in f.parts or "test" in f.name.lower():
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                product_api_names[node.name] = f.relative_to(_r).as_posix()

    # Check which ones appear in non-test source (src/python only, not tests/)
    test_only = []
    non_test_src = set()
    for f in src_dir.rglob("*.py"):
        if "__pycache__" in f.parts or "test" in f.name.lower():
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for name in product_api_names:
                if name in content:
                    non_test_src.add(name)
        except Exception:
            continue

    # Collect test references
    test_referenced = set()
    if test_dir.exists():
        for f in test_dir.rglob("*.py"):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                for name in product_api_names:
                    if name in content:
                        test_referenced.add(name)
            except Exception:
                continue

    # Functions only in tests, not in non-test product source (excluding their own definition)
    for name, src_file in product_api_names.items():
        if name not in non_test_src and name in test_referenced:
            test_only.append(f"{src_file}:{name}")

    if len(test_only) > 50:
        # Too many — likely a false-positive-heavy scan; suppress
        return {
            "validator_id": "V107",
            "status": "WARN",
            "blocks_sprint": False,
            "summary": (
                f"V107: High-count scan ({len(test_only)} potential test-only APIs) — "
                f"likely includes false positives. Manual review recommended."
            ),
        }
    if test_only:
        return {
            "validator_id": "V107",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": test_only[:20],
            "summary": (
                f"V107: {len(test_only)} public Python function(s) appear only in test files. "
                f"Review — these may be test-shaped APIs."
            ),
        }
    return {
        "validator_id": "V107",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V107: No test-only public Python APIs detected",
    }


def validate_detached_persistent_state(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V108: Private Dictionary fields used as persistent state backing in .cs product files.

    Detects: private [readonly] Dictionary<string, X?> _name = new();
    blocks_sprint=True for NEW .cs files; WARN for existing grandfathered.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    baseline = _load_baseline(_r)
    known = set(baseline.get("known_violations", {}).keys())
    violations_new = []
    violations_existing = []

    src_dir = _r / "src" / "net"
    if not src_dir.exists():
        return {
            "validator_id": "V108",
            "status": "PASS",
            "blocks_sprint": False,
            "summary": "V108: No src/net directory",
        }

    # Known false-positive class names (caches are OK, persistent state is not)
    _CACHE_NAME_PATTERNS = re.compile(r"_[a-z]*[Cc]ache[a-z]*")

    for f in src_dir.rglob("*.cs"):
        if "test" in f.name.lower() or "Test" in f.name:
            continue
        rel = f.relative_to(_r).as_posix()
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for m in _DICT_FIELD_PATTERN.finditer(content):
            matched = m.group(0)
            # Skip cache fields (legitimate use)
            field_match = re.search(r"\s+(_[a-z][a-zA-Z0-9]+)\s*=", matched)
            if field_match and _CACHE_NAME_PATTERNS.match(field_match.group(1)):
                continue
            line_no = content[: m.start()].count("\n") + 1
            entry = f"{rel}:{line_no}:{matched.strip()[:60]}"
            if rel in known:
                violations_existing.append(entry)
            else:
                violations_new.append(entry)

    if violations_new:
        return {
            "validator_id": "V108",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations_new[:20],
            "summary": (
                f"V108: {len(violations_new)} new detached Dictionary field(s) found in .cs "
                f"product source — persistent state must be backed by XML."
            ),
        }
    if violations_existing:
        return {
            "validator_id": "V108",
            "status": "WARN",
            "blocks_sprint": False,
            "violation_count": len(violations_existing),
            "violations_sample": violations_existing[:5],
            "summary": (
                f"V108: {len(violations_existing)} grandfathered detached Dictionary field(s). "
                f"Address in TC-PQLM-015 FODS rebuild. Each requires XML persistence path."
            ),
        }
    return {
        "validator_id": "V108",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V108: No detached Dictionary persistent state fields found",
    }


def validate_files_outside_approved_layout(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V109: Product source files must appear in product-file-layout-contract.yaml.

    FAIL for NEW source files not in the approved layout.
    WARN for existing grandfathered files in files_requiring_migration_or_removal.
    blocks_sprint=True for new violations.
    """
    try:
        import yaml as _yaml  # type: ignore
    except ImportError:
        return {
            "validator_id": "V109",
            "status": "WARN",
            "blocks_sprint": False,
            "summary": "V109: PyYAML not available — layout contract check skipped",
        }

    _r = repo_root or Path(__file__).parent.parent.parent
    contract_path = _r / "docs" / "code-quality" / "product-file-layout-contract.yaml"
    if not contract_path.exists():
        return {
            "validator_id": "V109",
            "status": "WARN",
            "blocks_sprint": False,
            "summary": "V109: product-file-layout-contract.yaml not found — layout check skipped",
        }

    try:
        contract = _yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "validator_id": "V109",
            "status": "WARN",
            "blocks_sprint": False,
            "summary": f"V109: Failed to parse layout contract: {e}",
        }

    # Build set of approved files and migration/removal files per format+language
    approved: set[str] = set()
    migration_targets: set[str] = set()

    for fmt_block in contract.get("formats", []):
        for entry in fmt_block.get("approved_layout", []):
            approved.add(entry["file"])
        for entry in fmt_block.get("files_requiring_migration", []):
            migration_targets.add(entry["current"])
        for entry in fmt_block.get("files_requiring_removal_or_migration", []):
            migration_targets.add(entry["file"])

    # Governed format scopes
    governed_format_roots = {
        "src/python/fods/",
        "src/net/fods/",
    }

    # Determine which files to check: use changed_files from declaration
    # (only check files in this sprint's changes, not the whole repo).
    # This ensures V109 is a sprint-time gate, not a full-repo audit.
    changed_files: list[str] = []
    for wi in declaration.get("work_items", []):
        changed_files.extend(wi.get("changed_files", []))

    if not changed_files:
        # No changed files declared — fall back to full governed-scope scan
        # but only flag as WARN (not FAIL) since this is a proactive check.
        violations_new = []
        violations_migration = []
        for root_prefix in governed_format_roots:
            src_root = _r / root_prefix.rstrip("/")
            if not src_root.exists():
                continue
            for f in src_root.rglob("*"):
                if f.suffix not in (".py", ".cs"):
                    continue
                if "__pycache__" in f.parts:
                    continue
                rel = f.relative_to(_r).as_posix()
                if rel in approved:
                    continue
                if rel in migration_targets:
                    violations_migration.append(rel)
                # Do NOT add to violations_new in fallback mode
    else:
        violations_new = []
        violations_migration = []
        for cf in changed_files:
            # Normalize separators
            rel = cf.replace("\\", "/")
            # Only check files in governed format roots
            if not any(rel.startswith(root) for root in governed_format_roots):
                continue
            if not (rel.endswith(".py") or rel.endswith(".cs")):
                continue
            if "__pycache__" in rel:
                continue
            if rel in approved:
                continue
            if rel in migration_targets:
                violations_migration.append(rel)
            else:
                violations_new.append(rel)

    if violations_new:
        return {
            "validator_id": "V109",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations_new": violations_new,
            "violations_requiring_migration": violations_migration,
            "summary": (
                f"V109: {len(violations_new)} product source file(s) NOT in approved layout "
                f"(and not in migration list). Add to product-file-layout-contract.yaml or remove."
            ),
        }
    if violations_migration:
        return {
            "validator_id": "V109",
            "status": "WARN",
            "blocks_sprint": False,
            "violations": violations_migration,
            "summary": (
                f"V109: {len(violations_migration)} file(s) flagged for migration/removal "
                f"per layout contract. Address in TC-PQLM-015 FODS rebuild."
            ),
        }
    return {
        "validator_id": "V109",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "V109: All governed product source files conform to approved layout",
    }
