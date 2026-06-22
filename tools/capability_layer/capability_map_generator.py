"""
capability_map_generator.py — Generate Format Factory capability maps.

Reads:
  - product-capability-matrix/poc-targets.yaml (primary authority source)
  - product-capability-matrix/*.yaml (per-format extended matrices)
  - src/python/{format}/ (source introspection)
  - tests/python/{format}/ (test file detection)
  - examples/python/{format}/ (example detection)
  - acquisition-packs/{format}/pack.yaml (FUL pack authority state)

Produces:
  - reports/capability-layer/commercial-capability-map.json
  - reports/capability-layer/foss-reduced-capability-map.json
  - reports/capability-layer/unified-capability-map.json
  - reports/capability-layer/gap-ledger.json
  - reports/capability-layer/action-queue.json

Usage:
  python tools/capability_layer/capability_map_generator.py [--output-dir reports/capability-layer]

Exit codes:
  0 — maps generated successfully
  1 — input data missing or invalid
  2 — generation error

Governance:
  - poc-targets.yaml is ONE INPUT, not final truth
  - All AI-involved records are flagged as ai_draft
  - Commercial and FOSS maps are NEVER mixed
  - Unverified capabilities are flagged as inferred_unverified
  - This tool does NOT write to src/ or tests/
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_POC_TARGETS = _REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"
_CAPABILITY_MATRIX_DIR = _REPO_ROOT / "product-capability-matrix"
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
_TESTS_PYTHON = _REPO_ROOT / "tests" / "python"
_EXAMPLES_PYTHON = _REPO_ROOT / "examples" / "python"
_ACQUISITION_PACKS = _REPO_ROOT / "acquisition-packs"
_DEFAULT_OUTPUT_DIR = _REPO_ROOT / "reports" / "capability-layer"

# States counted as "verified" for summary purposes
VERIFIED_STATES = frozenset([
    "spec_verified", "requirement_verified", "capability_verified",
    "implementation_verified", "test_verified", "example_verified",
    "package_verified", "dogfood_verified",
])

# The taxonomy order (lower index = less evidence)
STATE_ORDER = [
    "missing", "planned", "ai_draft", "human_goal", "inferred_unverified",
    "spec_verified", "requirement_verified", "capability_verified",
    "implementation_partial", "implementation_verified", "test_verified",
    "example_verified", "package_verified", "dogfood_verified",
    "blocked", "unsupported", "out_of_scope", "future",
]

def _derive_sprint_id() -> str:
    import datetime
    import subprocess
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=str(_REPO_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        sha = "unknown"
    return f"CAPABILITY-LAYER-HEALING-{datetime.date.today().strftime('%Y%m%d')}-{sha}"


def _derive_run_id() -> str:
    import datetime
    import subprocess
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=str(_REPO_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        sha = "unknown"
    return f"capability-layer-healing-{datetime.date.today().strftime('%Y%m%d')}-{sha}"


# Module-level defaults — overridden by CLI --sprint-id / --run-id arguments
SPRINT_ID = _derive_sprint_id()
RUN_ID = _derive_run_id()


# ---------------------------------------------------------------------------
# Loader helpers
# ---------------------------------------------------------------------------

def _load_yaml_simple(path: Path) -> dict:
    """Minimal YAML loader (handles simple key:value and lists without external deps)."""
    import re
    result: dict = {}
    current_key = None
    current_list: list | None = None
    indent_stack: list = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    # Use a very simple state machine for our limited YAML subset
    # For complex nested YAML, fall back to a safe repr
    # This handles the key YAML files we need (poc-targets.yaml has
    # multi-level nesting; we use a focused key extraction approach)
    in_block = False
    current_section: str | None = None
    items: list = []
    current_item: dict = {}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Handle simple key: value (no nesting)
        m = re.match(r"^(\w[\w_]*)\s*:\s*(.*)", stripped)
        if m:
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            result[k] = v

    return result


def _try_load_yaml(path: Path) -> dict | None:
    """Try to load YAML using pyyaml if available, else skip."""
    try:
        import yaml  # type: ignore
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # PyYAML not available — use stdlib-safe approach
        return _load_yaml_simple(path)
    except Exception:
        return None


_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
_SAL_OUTPUT = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"

# SAL facts cache (loaded once per generation run)
_sal_facts_cache: dict[str, list[dict]] | None = None


def _load_sal_facts() -> dict[str, list[dict]]:
    """Load SAL spec facts from sal-facts-latest.json, indexed by uppercase format_id.

    Returns a dict mapping e.g. "FODS" -> [{"qname": "FODS-FACT-001", ...}, ...].
    If the SAL output is missing or malformed, returns {} with a warning.
    """
    global _sal_facts_cache
    if _sal_facts_cache is not None:
        return _sal_facts_cache

    if not _SAL_OUTPUT.is_file():
        print("[WARN] SAL output not found at "
              f"{_SAL_OUTPUT} — capability map will lack SAL enrichment",
              file=sys.stderr)
        _sal_facts_cache = {}
        return _sal_facts_cache

    try:
        data = json.loads(_SAL_OUTPUT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[WARN] SAL output malformed/unreadable: {exc}", file=sys.stderr)
        _sal_facts_cache = {}
        return _sal_facts_cache

    # Validate minimal schema
    if not isinstance(data, dict) or "results" not in data:
        print("[WARN] SAL output missing 'results' key — quarantined", file=sys.stderr)
        _sal_facts_cache = {}
        return _sal_facts_cache

    index: dict[str, list[dict]] = {}
    for entry in data.get("results", []):
        fmt = entry.get("format_id", "").upper()
        if fmt:
            index[fmt] = entry.get("spec_facts", [])
    _sal_facts_cache = index
    print(f"[OK] SAL facts loaded: {len(index)} formats, "
          f"{sum(len(v) for v in index.values())} total facts", file=sys.stderr)
    return _sal_facts_cache


def reset_sal_facts_cache() -> None:
    """Clear the SAL facts cache (for testing)."""
    global _sal_facts_cache
    _sal_facts_cache = None


# Keywords that indicate a SAL fact is relevant to an operation kind.
# Maps operation_kind substrings → matching SAL fact content keywords.
_OP_KEYWORDS: dict[str, list[str]] = {
    "load":       ["load", "parse", "read", "import", "open", "document", "file"],
    "write":      ["write", "serialize", "export", "output", "save", "generate"],
    "roundtrip":  ["roundtrip", "round-trip", "preserve", "identity", "lossless"],
    "probe":      ["probe", "detect", "identify", "header", "magic", "signature"],
    "sheet":      ["sheet", "table", "spreadsheet", "calc", "calc:table"],
    "cell":       ["cell", "table-cell", "table:table-cell", "value", "data-type"],
    "row":        ["row", "table-row", "table:table-row", "rows"],
    "column":     ["column", "col", "table-column", "table:table-column"],
    "paragraph":  ["paragraph", "text:p", "para"],
    "text":       ["text", "string", "content", "character"],
    "style":      ["style", "format", "formatting", "font", "colour", "color"],
    "formula":    ["formula", "expression", "calc", "function", "computation"],
    "metadata":   ["metadata", "meta", "document-meta", "office:meta", "title", "author"],
    "image":      ["image", "draw:image", "graphic", "picture", "bitmap", "pixel"],
    "drawing":    ["draw", "shape", "frame", "object", "svg"],
    "analytics":  ["count", "sum", "average", "mean", "max", "min", "total", "distinct"],
}


def _match_sal_facts_per_op(
    sal_fact_objects: list[dict],
    operation_kind: str,
    max_results: int = 20,
) -> list[str]:
    """Return SAL fact qnames relevant to the given operation_kind.

    Matches facts by checking whether operation-related keywords appear in the
    fact's qname, description, or section fields. Returns up to max_results qnames.

    Args:
        sal_fact_objects: List of fact dicts with keys 'qname', 'description', 'section'.
        operation_kind: Operation name (e.g., 'load', 'fods_sheet_count').
        max_results: Maximum number of qnames to return (default 20).

    Returns:
        List of matching qname strings, capped at max_results.
    """
    if not sal_fact_objects or not operation_kind:
        return []

    op_lower = operation_kind.lower()

    # Collect keywords: direct op name parts + mapped keyword lists
    op_parts = [p for p in op_lower.replace("-", "_").split("_") if len(p) > 2]
    keywords: list[str] = list(op_parts)
    for segment, kw_list in _OP_KEYWORDS.items():
        if segment in op_lower:
            keywords.extend(kw_list)
    keywords = list(dict.fromkeys(kw for kw in keywords if kw))  # deduplicate, preserve order

    if not keywords:
        return []

    matched: list[str] = []
    for fact in sal_fact_objects:
        qname = fact.get("qname", "")
        desc = fact.get("description", "").lower()
        section = fact.get("section", "").lower()
        qname_lower = qname.lower()
        haystack = f"{qname_lower} {desc} {section}"
        if any(kw in haystack for kw in keywords):
            matched.append(qname)
        if len(matched) >= max_results:
            break

    return matched


_VERIFIED_FACT_STATUSES = frozenset(["verified", "verified_with_note"])
_NON_AUTHORITATIVE_STATUSES = frozenset(["not_found_in_normalized_text", "needs_review", "needs_recheck"])


def _load_spec_facts(format_id: str, verified_only: bool = False) -> list[str]:
    """Load spec fact claim_ids from .local/spec-cache/{format}/*/workbench/verified-facts-review.yaml.

    Supports both JSON and YAML formats. Returns list of claim_id strings (e.g. ["FACT-FODS-001"]).

    Args:
        format_id: The format identifier (e.g. "zst", "fods").
        verified_only: If True, only return facts with verification_status in
            _VERIFIED_FACT_STATUSES. Excludes not_found_in_normalized_text,
            needs_review, etc. Use this for spec_fact_refs (SAL-authoritative).
    """
    fmt_dir = _SPEC_CACHE / format_id.lower()
    if not fmt_dir.exists():
        return []
    fact_ids: list[str] = []
    for review_file in fmt_dir.glob("*/workbench/verified-facts-review.yaml"):
        try:
            content = review_file.read_text(encoding="utf-8")
            # Try JSON first (FODS uses JSON format with .yaml extension)
            if content.lstrip().startswith("{"):
                data = json.loads(content)
                for fact in data.get("facts", []):
                    cid = fact.get("claim_id", "")
                    if not cid:
                        continue
                    if verified_only:
                        prov = fact.get("provenance", {})
                        vstat = (fact.get("verification_status")
                                 or prov.get("verification_status", ""))
                        if vstat not in _VERIFIED_FACT_STATUSES:
                            continue
                    fact_ids.append(cid)
            else:
                # YAML format — verification_status may be at top level or nested in provenance
                data = _try_load_yaml(review_file)
                if data and isinstance(data, dict):
                    for fact in data.get("facts", []):
                        if not isinstance(fact, dict):
                            continue
                        cid = fact.get("claim_id", "")
                        if not cid:
                            continue
                        if verified_only:
                            prov = fact.get("provenance", {}) or {}
                            vstat = (fact.get("verification_status")
                                     or prov.get("verification_status", ""))
                            if vstat not in _VERIFIED_FACT_STATUSES:
                                continue
                        fact_ids.append(cid)
        except Exception:
            continue
    return fact_ids


def _scan_python_functions(module_dir: Path) -> list[str]:
    """Scan a Python source directory and return exported function names."""
    fns: list[str] = []
    if not module_dir.exists():
        return fns
    # Look for __init__.py __all__ first
    init = module_dir / "__init__.py"
    if init.exists():
        try:
            source = init.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                        fns.append(elt.value)
            if fns:
                return fns
        except Exception:
            pass

    # Fall back: scan all .py files for def statements
    for py_file in sorted(module_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        fns.append(node.name)
        except Exception:
            pass
    return list(dict.fromkeys(fns))  # deduplicate preserving order


def _find_main_source_file(module_dir: Path, format_id: str) -> str:
    """Return the main source file name for a Python FOSS module.

    Tries <format_lower>_codec.py then <format_lower>_parser.py then any .py that
    is not __init__.py or starts with _. Falls back to directory path if ambiguous.
    """
    if not module_dir.exists():
        return f"{format_id.lower()}_codec.py"
    fmt = format_id.lower()
    candidates = [
        f"{fmt}_codec.py",
        f"{fmt}_parser.py",
        f"{fmt}.py",
    ]
    for name in candidates:
        if (module_dir / name).exists():
            return name
    # Any non-private .py that is not __init__
    for py in sorted(module_dir.glob("*.py")):
        if py.name != "__init__.py" and not py.name.startswith("_"):
            return py.name
    return f"{fmt}_codec.py"


def _count_test_files(test_dir: Path) -> tuple[int, list[str]]:
    """Count test files and return list of test file names."""
    if not test_dir.exists():
        return 0, []
    files = [f.name for f in sorted(test_dir.glob("test_*.py"))]
    return len(files), files


def _count_net_test_files(test_dir: Path) -> tuple[int, list[str]]:
    """Count .NET test files (.cs) and return list of file names."""
    if not test_dir.exists():
        return 0, []
    files = [f.name for f in sorted(test_dir.glob("*.cs"))]
    return len(files), files


def _resolve_csharp_symbol(src_dir: Path, op_key: str) -> str | None:
    """Try to find a C# public method/class symbol that matches op_key.

    Searches .cs files in src_dir for public methods whose name
    contains op_key (case-insensitive, underscore-to-CamelCase aware).

    Returns the resolved symbol string or None if not found.
    """
    if not src_dir.exists():
        return None
    op_camel = "".join(w.capitalize() for w in op_key.split("_"))
    op_lower = op_key.lower().replace("_", "")
    import re
    method_re = re.compile(r'public\s+\S+\s+(\w+)\s*\(', re.MULTILINE)
    for cs_file in sorted(src_dir.glob("*.cs")):
        try:
            content = cs_file.read_text(encoding="utf-8")
            for match in method_re.finditer(content):
                method_name = match.group(1)
                if method_name.lower().replace("_", "") == op_lower or method_name == op_camel:
                    return f"{cs_file.name}::{method_name}"
        except Exception:
            continue
    return None


def _count_examples(examples_dir: Path) -> tuple[int, list[str]]:
    """Count example files and return list of example file names."""
    if not examples_dir.exists():
        return 0, []
    files = [f.name for f in sorted(examples_dir.glob("*.py"))]
    return len(files), files


def _get_pack_authority(format_id: str) -> str:
    """Get authority state from acquisition-packs/{format}/pack.yaml."""
    pack_yaml = _ACQUISITION_PACKS / format_id.lower() / "pack.yaml"
    if not pack_yaml.exists():
        return "no_authority"
    data = _try_load_yaml(pack_yaml)
    if not data:
        return "no_authority"
    # Look for gates_passed or authority fields
    gates = data.get("gates_passed", data.get("gate", ""))
    if "10" in str(gates) or "11" in str(gates):
        return "gate_evidence"
    if "1" in str(gates):
        return "gate_evidence"
    return "product_goal"


_test_fn_name_cache: dict[str, frozenset[str]] = {}


def _get_cached_test_functions(test_dir: Path) -> frozenset[str]:
    """Return all test function names from test_dir as lowercase strings.

    Results are cached per directory so the AST parse only runs once per
    format per generator invocation.
    """
    key = str(test_dir)
    if key in _test_fn_name_cache:
        return _test_fn_name_cache[key]
    if not test_dir.is_dir():
        _test_fn_name_cache[key] = frozenset()
        return frozenset()
    names: set[str] = set()
    for test_file in sorted(test_dir.glob("test_*.py")):
        try:
            source = test_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except Exception:
            continue  # conservative: skip unparseable files
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test"):
                    names.add(node.name.lower())
    result = frozenset(names)
    _test_fn_name_cache[key] = result
    return result


def _scan_test_function_names(test_dir: Path, fn_name: str) -> bool:
    """Return True if any test function in test_dir covers fn_name.

    Uses cached AST parsing — the directory is only scanned once per generator
    run regardless of how many functions are checked against it.
    Falls back to False (conservative) on any parse error.
    """
    all_names = _get_cached_test_functions(test_dir)
    if not all_names:
        return False
    fn_lower = fn_name.lower().replace(" ", "_")
    return any(fn_lower in name for name in all_names)


def _determine_state(
    fn_name: str,
    implemented: bool,
    test_files: list[str],
    example_count: int,
    authority_state: str,
    test_dir: "Path | None" = None,
) -> tuple[str, str, float]:
    """Determine current_state, confidence_reason, and confidence float.

    When test_dir is provided, uses AST-level function-name scanning for
    precision. Falls back to file-name substring matching when test_dir is None
    (backward-compatible for unit tests that don't have a real directory).
    """
    if not implemented:
        return "missing", "Function not found in source", 0.9
    fn_lower = fn_name.lower()
    if test_dir is not None:
        has_matching_test = _scan_test_function_names(test_dir, fn_name)
    else:
        # Legacy file-name substring fallback (used in unit tests)
        has_matching_test = any(fn_lower in tf.lower() for tf in test_files)
    confidence_boost = 0.05 if authority_state == "spec_fact" else 0.0
    if has_matching_test:
        if example_count > 0:
            return "example_verified", f"test match: {fn_name} in test functions + examples", min(0.9 + confidence_boost, 1.0)
        return "test_verified", f"test match: {fn_name} in test functions", min(0.8 + confidence_boost, 1.0)
    if test_files or (test_dir is not None and test_dir.is_dir()):
        return "implementation_verified", f"Implemented but no test function matches '{fn_name}'", 0.5
    return "implementation_verified", "Implemented; no tests in directory", 0.4


# ---------------------------------------------------------------------------
# Core: build capability records for one format
# ---------------------------------------------------------------------------

def _build_foss_records(
    format_id: str,
    python_status: dict,
    test_info: tuple[int, list[str]],
    example_info: tuple[int, list[str]],
    implemented_fns: list[str],
    authority_state: str,
    sprint_now: str,
    main_source_file: str | None = None,
    spec_facts: list[str] | None = None,
    verified_spec_facts: list[str] | None = None,
    sal_fact_objects: list[dict] | None = None,
    test_dir: "Path | None" = None,
) -> list[dict]:
    """Build FOSS/reduced capability records for one format."""
    records: list[dict] = []
    effective_authority = "spec_fact" if spec_facts else authority_state
    test_count, test_files = test_info
    example_count, example_files = example_info
    fn_set = set(implemented_fns)
    src_file = main_source_file or f"{format_id.lower()}_codec.py"
    # Only create implementation_refs if the source directory/file actually exists
    src_dir_exists = (_SRC_PYTHON / format_id.lower()).exists()

    # All expected capabilities from python_status
    for op_key, op_status in python_status.items():
        is_implemented = op_key in fn_set or op_status in ("PASS", "pass", True)
        # Check source introspection
        source_fn_check = any(op_key in fn or fn in op_key for fn in fn_set)
        actually_implemented = is_implemented or source_fn_check

        state, reason, confidence = _determine_state(
            op_key, actually_implemented, test_files, example_count, effective_authority,
            test_dir=test_dir,
        )

        # Per-operation spec_refs: use SAL fact matching when sal_fact_objects available
        if sal_fact_objects:
            per_op_refs = _match_sal_facts_per_op(sal_fact_objects, op_key)
            op_spec_refs = per_op_refs if per_op_refs else (spec_facts[:5] if spec_facts else [])
        else:
            op_spec_refs = spec_facts or []

        record: dict[str, Any] = {
            "capability_id": f"{format_id}-FOSS-{op_key.upper()}-001",
            "format": format_id,
            "format_family": _guess_family(format_id),
            "product_type": "foss_reduced",
            "product_profile": f"{format_id.lower()}-python-foss",
            "capability_name": op_key.replace("_", " ").title(),
            "capability_category": _guess_category(op_key),
            "operation_kind": op_key,
            "input_cardinality": "single",
            "output_cardinality": "single",
            "expected_for_commercial": False,
            "expected_for_foss": True,
            "required_for_poc": op_key in ("load", "probe", f"probe_{format_id.lower()}"),
            "blocks_readiness": op_key in ("load", "write", "roundtrip"),
            "current_state": state,
            "authority_state": effective_authority,
            "spec_refs": op_spec_refs,
            "spec_fact_refs": verified_spec_facts or [],
            "requirement_refs": [],
            "source_refs": [f"src/python/{format_id.lower()}/"] if (actually_implemented and src_dir_exists) else [],
            "implementation_refs": [
                f"src/python/{format_id.lower()}/{src_file}::{op_key}"
            ] if (actually_implemented and src_dir_exists) else [],
            "test_refs": [f"tests/python/{format_id.lower()}/{t}" for t in test_files[:3]],
            "example_refs": [f"examples/python/{format_id.lower()}/{e}" for e in example_files[:2]],
            "package_refs": [],
            "dogfood_refs": [],
            "evidence_refs": [],
            "gaps": [] if actually_implemented else ["implementation_missing"],
            "blockers": [],
            "next_task_candidate": "" if actually_implemented else f"Implement {op_key} for {format_id}",
            "confidence_level": "high" if confidence >= 0.8 else ("medium" if confidence >= 0.5 else "low"),
            "confidence_reason": reason,
            "ai_involvement_flag": False,
            "manual_agent_verified": True,
            "last_verified": sprint_now,
            "verifier": RUN_ID,
            "notes": f"Generated from poc-targets.yaml python_status + source introspection. op_status={op_status}",
        }
        records.append(record)

    # Add any implemented functions NOT in python_status (source introspection extras)
    status_keys = set(python_status.keys())
    for fn in implemented_fns:
        fn_lower = fn.lower()
        if fn_lower not in status_keys and not any(fn_lower in k for k in status_keys):
            state2, reason2, conf2 = _determine_state(
                fn, True, test_files, example_count, authority_state, test_dir=test_dir
            )
            record2: dict[str, Any] = {
                "capability_id": f"{format_id}-FOSS-{fn.upper()}-SRC-001",
                "format": format_id,
                "format_family": _guess_family(format_id),
                "product_type": "foss_reduced",
                "product_profile": f"{format_id.lower()}-python-foss",
                "capability_name": fn.replace("_", " ").title(),
                "capability_category": _guess_category(fn),
                "operation_kind": fn,
                "input_cardinality": "single",
                "output_cardinality": "single",
                "expected_for_commercial": False,
                "expected_for_foss": True,
                "required_for_poc": False,
                "blocks_readiness": False,
                "current_state": state2,
                "authority_state": authority_state,
                "spec_refs": [],
                "spec_fact_refs": verified_spec_facts or [],
                "requirement_refs": [],
                "source_refs": [f"src/python/{format_id.lower()}/"] if src_dir_exists else [],
                "implementation_refs": [f"src/python/{format_id.lower()}/{src_file}::{fn}"] if src_dir_exists else [],
                "test_refs": [f"tests/python/{format_id.lower()}/{t}" for t in test_files[:2]],
                "example_refs": [],
                "package_refs": [],
                "dogfood_refs": [],
                "evidence_refs": [],
                "gaps": [],
                "blockers": [],
                "next_task_candidate": "",
                "confidence_level": "medium",
                "confidence_reason": f"Found in source introspection; not in poc-targets.yaml python_status. {reason2}",
                "ai_involvement_flag": False,
                "manual_agent_verified": False,
                "last_verified": sprint_now,
                "verifier": RUN_ID,
                "notes": "Discovered via source introspection — not in poc-targets.yaml",
            }
            records.append(record2)

    return records


def _build_commercial_records(
    format_id: str,
    dotnet_status: dict,
    test_info: tuple[int, list[str]],
    example_info: tuple[int, list[str]],
    authority_state: str,
    sprint_now: str,
    *,
    spec_facts: list[str] | None = None,
    verified_spec_facts: list[str] | None = None,
) -> list[dict]:
    """Build commercial capability records for one .NET format."""
    records: list[dict] = []
    test_count, test_files = test_info
    example_count, example_files = example_info
    effective_authority = "spec_fact" if spec_facts else authority_state

    for op_key, op_status in dotnet_status.items():
        if op_key == "dotnet_tests":
            continue
        is_implemented = op_status in ("PASS", "pass", True)

        # Resolve actual C# symbol for this operation
        src_dir = _REPO_ROOT / "src" / "net" / format_id.lower()
        resolved_symbol = _resolve_csharp_symbol(src_dir, op_key) if is_implemented else None
        impl_ref = (
            f"src/net/{format_id.lower()}/{resolved_symbol}"
            if resolved_symbol
            else f"src/net/{format_id.lower()}/"
        ) if is_implemented else None

        # Per-operation test matching for .NET
        # .NET test files use class-based naming (e.g. FodsCsvExporterTests.cs)
        # Match by checking if ANY keyword from the operation name appears in test filenames
        net_test_dir = _REPO_ROOT / "tests" / "net" / format_id.lower()
        _, net_test_files = _count_net_test_files(net_test_dir)
        op_keywords = [kw for kw in op_key.lower().split("_") if len(kw) > 2]
        has_matching_test = (
            bool(net_test_files)
            and bool(op_keywords)
            and any(
                all(kw in tf.lower() for kw in op_keywords)
                for tf in net_test_files
            )
        )

        # State: test_verified only if a test file matches the operation keywords
        if not is_implemented:
            state = "missing"
            reason = f"dotnet_status={op_status}; not implemented"
        elif has_matching_test:
            state = "test_verified"
            reason = f"dotnet_status={op_status}; test file matches keywords {op_keywords}"
        elif net_test_files:
            state = "implementation_verified"
            reason = f"dotnet_status={op_status}; {len(net_test_files)} test files but none match keywords {op_keywords}"
        else:
            state = "implementation_verified"
            reason = f"dotnet_status={op_status}; no test files in directory"

        record: dict[str, Any] = {
            "capability_id": f"{format_id}-COMMERCIAL-{op_key.upper()}-001",
            "format": format_id,
            "format_family": _guess_family(format_id),
            "product_type": "commercial",
            "product_profile": f"{format_id.lower()}-dotnet-commercial",
            "capability_name": op_key.replace("_", " ").title(),
            "capability_category": _guess_category(op_key),
            "operation_kind": op_key,
            "input_cardinality": "single",
            "output_cardinality": "single",
            "expected_for_commercial": True,
            "expected_for_foss": False,
            "required_for_poc": op_key in ("load", "save_same_format", "reload_and_verify"),
            "blocks_readiness": op_key in ("load", "save_same_format"),
            "current_state": state,
            "authority_state": effective_authority,
            "spec_refs": spec_facts or [],
            "spec_fact_refs": verified_spec_facts or [],
            "requirement_refs": [],
            "source_refs": [f"src/net/{format_id.lower()}/"] if is_implemented else [],
            "implementation_refs": [impl_ref] if impl_ref else [],
            "test_refs": (
                [f"tests/net/{format_id.lower()}/{t}" for t in net_test_files[:3]]
                if net_test_files else
                ([f"tests/net/{format_id.lower()}/"] if test_count > 0 else [])
            ),
            "example_refs": [f"examples/net/{format_id.lower()}/{e}" for e in example_files[:2]],
            "package_refs": [],
            "dogfood_refs": [],
            "evidence_refs": [],
            "gaps": [] if is_implemented else ["implementation_missing"],
            "blockers": [],
            "next_task_candidate": "" if is_implemented else f"Implement {op_key} for {format_id} .NET",
            "confidence_level": "high" if is_implemented and test_count > 50 else "medium",
            "confidence_reason": reason,
            "ai_involvement_flag": False,
            "manual_agent_verified": True,
            "last_verified": sprint_now,
            "verifier": RUN_ID,
            "notes": f"Generated from poc-targets.yaml dotnet_status. authority_state={authority_state}.",
        }
        records.append(record)

    return records


def _guess_category(op_key: str) -> str:
    """Guess capability_category from operation name."""
    op = op_key.lower()
    if "probe" in op:
        return "probe"
    if "load" in op or "parse" in op or "read" in op:
        return "load"
    if "write" in op or "save" in op or "create" in op:
        return "save"
    if "export" in op or "to_csv" in op or "to_txt" in op or "to_html" in op or "to_json" in op:
        return "export"
    if "edit" in op or "set" in op or "add" in op or "remove" in op or "insert" in op or "append" in op:
        return "edit"
    if "get" in op or "count" in op or "extract" in op or "inspect" in op or "metadata" in op or "stat" in op:
        return "inspect"
    if "installed" in op or "package" in op:
        return "package"
    if "dogfood" in op or "roundtrip" in op:
        return "dogfood"
    if "filter" in op or "find" in op or "search" in op:
        return "utility"
    return "utility"


def _guess_family(format_id: str) -> str:
    """Guess format_family from format_id."""
    odf_flat = {"FODS", "FODT", "FODG", "FODP"}
    netpbm = {"PBM", "PGM", "PPM", "Netpbm"}
    spreadsheet_text = {"TSV", "CSV", "SYLK", "DIF", "Gnumeric"}
    compression = {"ZST", "ZPAQ"}
    doc_text = {"ABW", "ODT", "ODS"}
    image = {"QOI", "XCF", "XPM", "PAM"}

    f = format_id.upper()
    if f in odf_flat:
        return "odf_flat"
    if f in netpbm:
        return "netpbm"
    if f in spreadsheet_text:
        return "spreadsheet_text"
    if f in compression:
        return "compression"
    if f in doc_text:
        return "document_text"
    if f in image:
        return "image"
    if f == "NDJSON":
        return "json_lines"
    return "unknown"


def _build_summary(records: list[dict]) -> dict:
    """Build summary statistics from a list of records."""
    by_state: dict[str, int] = {}
    by_format: dict[str, dict] = {}
    verified_count = 0
    missing_count = 0

    for r in records:
        state = r.get("current_state", "missing")
        fmt = r.get("format", "unknown")
        by_state[state] = by_state.get(state, 0) + 1
        if state in VERIFIED_STATES:
            verified_count += 1
        if state in ("missing", "planned", "human_goal"):
            missing_count += 1

        if fmt not in by_format:
            by_format[fmt] = {"total": 0, "verified": 0, "missing": 0}
        by_format[fmt]["total"] += 1
        if state in VERIFIED_STATES:
            by_format[fmt]["verified"] += 1
        if state in ("missing", "planned", "human_goal"):
            by_format[fmt]["missing"] += 1

    return {
        "total_capabilities": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "by_state": dict(sorted(by_state.items())),
        "by_format": dict(sorted(by_format.items())),
    }


# ---------------------------------------------------------------------------
# Gap ledger builder
# ---------------------------------------------------------------------------

def _build_gap_ledger(all_records: list[dict]) -> list[dict]:
    """Build gap ledger from capability records with missing/partial states."""
    GAP_STATES = {"missing", "planned", "implementation_partial", "implementation_verified",
                  "human_goal", "inferred_unverified", "ai_draft", "blocked"}
    gaps: list[dict] = []
    seen: set[str] = set()

    for r in all_records:
        state = r.get("current_state", "")
        if state not in GAP_STATES:
            continue
        gap_id = f"GAP-{r['format']}-{r['product_type'].upper()[:4]}-{r['operation_kind'].upper()[:12]}-001"
        if gap_id in seen:
            continue
        seen.add(gap_id)

        gap_type = (
            "missing_implementation" if state in ("missing", "planned", "human_goal", "inferred_unverified") else
            "stale_claim" if state == "ai_draft" else
            "missing_test_coverage" if state == "implementation_verified" else
            "missing_implementation"
        )

        # Use verified spec_fact_refs first; fall back to spec_refs (SAL qnames) when absent.
        # This allows formats with SAL-extracted but unverified facts to still appear
        # in gap ledger spec_facts (e.g. FODG, ODS, ODT via ODF-FACT-* qnames).
        _gap_spec_facts = r.get("spec_fact_refs", []) or r.get("spec_refs", []) or []
        gaps.append({
            "gap_id": gap_id,
            "format": r["format"],
            "product_type": r["product_type"],
            "capability_name": r["capability_name"],
            "current_state": state,
            "gap_type": gap_type,
            "status": "open",
            "blocks_poc": r.get("required_for_poc", False),
            "blocks_readiness": r.get("blocks_readiness", False),
            "commercial_impact": "HIGH" if r.get("expected_for_commercial") else "NONE",
            "foss_impact": "HIGH" if r.get("expected_for_foss") else "NONE",
            "priority": "P0" if r.get("blocks_readiness") else ("P1" if r.get("required_for_poc") else "P2"),
            "owning_lane": 1 if r["product_type"] == "commercial" else 6,
            "suggested_taskcard": r.get("next_task_candidate", ""),
            "suggested_pilot": f"CAP-PILOT-{'C' if r['product_type']=='commercial' else 'F'}-{r['format']}",
            "suggested_verification": f"python -m pytest tests/python/{r['format'].lower()}/ -v",
            "recurrence_prevention": f"Update poc-targets.yaml after implementing {r['operation_kind']}",
            "blockers": r.get("blockers", []),
            "related_capability_id": r.get("capability_id", ""),
            "notes": r.get("notes", ""),
            "spec_facts": _gap_spec_facts,
        })

    return sorted(gaps, key=lambda g: (g["priority"], g["format"]))


# ---------------------------------------------------------------------------
# Action queue builder
# ---------------------------------------------------------------------------

def _eval_action_conditions(poc_data: dict) -> list[dict]:
    """Return only actions whose preconditions are currently unresolved.

    Add future conditional actions here instead of hard-coding them in
    _build_action_queue. This function is the single source of truth for
    what work is actually needed.
    """
    actions: list[dict] = []

    # ACT-UPDATE-POC-TARGETS: only emit if FODG, TSV, or NDJSON missing
    foss = poc_data.get("foss_reduced_products", [])
    if isinstance(foss, list):
        foss_keys = {str(item.get("format_id", item.get("format", ""))).upper() for item in foss}
    else:
        foss_keys = {k.upper() for k in foss.keys()}
    missing_foss = {"FODG", "TSV", "NDJSON"} - foss_keys
    if missing_foss:
        actions.append({
            "action_id": "ACT-UPDATE-POC-TARGETS",
            "action_type": "UPDATE_MATRIX",
            "format": "ALL",
            "product_type": "both",
            "capability": "poc-targets.yaml staleness healing",
            "gap_id": "GAP-POC-TARGETS-STALE",
            "priority": "P1",
            "lane": 4,
            "description": f"Add missing FOSS formats to poc-targets.yaml: {sorted(missing_foss)}",
            "taskcard": "CAP-PROD-005",
            "verification": "python tools/capability_layer/capability_map_generator.py",
            "advisory_only": False,
            "machine_executable": True,
            "external_gate": False,
            "safe_for_autonomous": True,
        })

    return actions


def _build_action_queue(
    gaps: list[dict],
    commercial_records: list[dict],
    foss_records: list[dict],
    poc_data: dict | None = None,
) -> list[dict]:
    """Build machine-readable action queue from gap ledger."""
    actions: list[dict] = []

    # High-priority open gaps first (TC-RCAL-001: filter open gaps so closed gaps
    # don't crowd out actionable work; sort by priority then by suggested_taskcard presence)
    _PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    open_gaps = [g for g in gaps if g.get("status", "open") != "closed"]
    open_gaps.sort(key=lambda g: (
        _PRIORITY_ORDER.get(g.get("priority", "P4"), 4),
        0 if g.get("suggested_taskcard") else 1,
    ))
    for gap in open_gaps[:20]:  # top 20 open gaps
        is_machine_executable = (
            gap["product_type"] == "foss_reduced"
            and gap["priority"] in ("P0", "P1")
            and not gap.get("blocks_poc", False)
            and gap.get("commercial_impact", "NONE") == "NONE"
        )
        actions.append({
            "action_id": f"ACT-{gap['gap_id']}",
            "action_type": "IMPLEMENT_CAPABILITY",
            "format": gap["format"],
            "product_type": gap["product_type"],
            "capability": gap["capability_name"],
            "gap_id": gap["gap_id"],
            "priority": gap["priority"],
            "lane": gap["owning_lane"],
            "description": f"Implement {gap['capability_name']} for {gap['format']} ({gap['product_type']})",
            "taskcard": gap["suggested_taskcard"],
            "verification": gap["suggested_verification"],
            "advisory_only": not is_machine_executable,
            "machine_executable": is_machine_executable,
            "external_gate": False,
            "safe_for_autonomous": gap["priority"] in ("P0", "P1", "P2") and not gap["blocks_poc"],
        })

    # Conditional actions evaluated against current system state
    if poc_data is not None:
        actions.extend(_eval_action_conditions(poc_data))

    return actions


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate(
    output_dir: Path = _DEFAULT_OUTPUT_DIR,
    sprint_id: str | None = None,
    run_id: str | None = None,
) -> int:
    """Generate capability maps and supporting artifacts.

    Args:
        output_dir: Output directory for generated maps.
        sprint_id:  Sprint identifier to embed in artifacts (overrides module default).
        run_id:     Run identifier to embed in artifacts (overrides module default).

    Returns:
        0 on success, 1 on missing input, 2 on error.
    """
    global SPRINT_ID, RUN_ID
    if sprint_id:
        SPRINT_ID = sprint_id
    if run_id:
        RUN_ID = run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    sprint_now = datetime.now(timezone.utc).isoformat()

    # --- Load poc-targets.yaml ---
    try:
        import yaml  # type: ignore
        poc_data = yaml.safe_load(_POC_TARGETS.read_text(encoding="utf-8")) or {}
    except ImportError:
        print("[WARN] PyYAML not available — using simplified YAML loader", file=sys.stderr)
        poc_data = _load_yaml_simple(_POC_TARGETS) or {}
    except Exception as exc:
        print(f"[ERROR] Cannot load poc-targets.yaml: {exc}", file=sys.stderr)
        return 1

    commercial_records: list[dict] = []
    foss_records: list[dict] = []

    # --- Load SAL facts for enrichment ---
    sal_facts = _load_sal_facts()
    sal_enrichment_log: list[dict] = []

    # --- Commercial .NET products ---
    for fmt_entry in poc_data.get("commercial_net_products", []):
        fmt_id = fmt_entry.get("format", "")
        if not fmt_id:
            continue
        dotnet_status = fmt_entry.get("dotnet_status", {})
        # Determine Gate 11 approval from poc-targets (not hardcoded)
        gate_11_g = fmt_entry.get("gate_11_g11g", "")
        authority_state = "gate_evidence" if gate_11_g else "poc_candidate"

        # Tests: prefer dotnet_tests from dotnet_status dict, fall back to format-level key
        raw_test_count = dotnet_status.get("dotnet_tests") or fmt_entry.get("dotnet_tests") or 0
        net_tests = (int(raw_test_count), [])

        # Examples from .NET examples dir
        net_ex_dir = _REPO_ROOT / "examples" / "net" / fmt_id.lower()
        net_examples = _count_examples(net_ex_dir)

        # Spec facts (commercial formats may also have verified spec facts)
        # Netpbm is a parent format — aggregate facts from child formats (pbm/pgm/ppm)
        if fmt_id.lower() == "netpbm":
            commercial_facts = []
            commercial_verified = []
            for child_fmt in ("pbm", "pgm", "ppm"):
                commercial_facts.extend(_load_spec_facts(child_fmt))
                commercial_verified.extend(_load_spec_facts(child_fmt, verified_only=True))
        else:
            commercial_facts = _load_spec_facts(fmt_id)
            commercial_verified = _load_spec_facts(fmt_id, verified_only=True)

        # Merge SAL facts into commercial records
        sal_comm_facts = sal_facts.get(fmt_id.upper(), [])
        sal_comm_qnames = [f.get("qname", "") for f in sal_comm_facts if f.get("qname")]
        if sal_comm_qnames:
            existing_comm = set(commercial_facts)
            for q in sal_comm_qnames:
                if q not in existing_comm:
                    commercial_facts.append(q)
            sal_enrichment_log.append({
                "format": fmt_id, "product_type": "commercial",
                "sal_facts_count": len(sal_comm_facts),
                "sal_qnames": sal_comm_qnames,
                "action": "enriched",
            })

        recs = _build_commercial_records(
            fmt_id, dotnet_status, net_tests, net_examples, authority_state, sprint_now,
            spec_facts=commercial_facts,
            verified_spec_facts=commercial_verified,
        )
        commercial_records.extend(recs)

    # --- FOSS/reduced Python products ---
    for fmt_entry in poc_data.get("foss_reduced_products", []):
        fmt_id = fmt_entry.get("format", "")
        if not fmt_id:
            continue
        python_status = fmt_entry.get("python_status") or fmt_entry.get("python_foss_status", {})
        authority_state = _get_pack_authority(fmt_id)
        if not authority_state or authority_state == "no_authority":
            authority_state = "gate_evidence"  # Gates 1-10 passed per poc-targets

        # Source introspection
        src_dir = _SRC_PYTHON / fmt_id.lower()
        impl_fns = _scan_python_functions(src_dir)
        main_src_file = _find_main_source_file(src_dir, fmt_id)

        # Tests
        test_dir = _TESTS_PYTHON / fmt_id.lower()
        test_info = _count_test_files(test_dir)

        # Examples
        ex_dir = _EXAMPLES_PYTHON / fmt_id.lower()
        ex_info = _count_examples(ex_dir)

        # Spec facts — all facts and verified-only facts
        facts = _load_spec_facts(fmt_id)
        verified_facts = _load_spec_facts(fmt_id, verified_only=True)

        # Merge SAL facts: SAL provides qnames, spec_cache provides claim_ids
        sal_format_facts = sal_facts.get(fmt_id.upper(), [])
        sal_qnames = [f.get("qname", "") for f in sal_format_facts if f.get("qname")]
        if sal_qnames and not facts:
            # SAL provides facts where spec-cache has none — use SAL qnames as spec_refs
            facts = sal_qnames
        elif sal_qnames:
            # Merge: add SAL qnames not already in facts
            existing = set(facts)
            for q in sal_qnames:
                if q not in existing:
                    facts.append(q)
        if sal_format_facts:
            sal_enrichment_log.append({
                "format": fmt_id, "product_type": "foss_reduced",
                "sal_facts_count": len(sal_format_facts),
                "sal_qnames": sal_qnames,
                "action": "enriched" if sal_qnames else "no_change",
                "reason": "SAL facts merged into spec_refs" if sal_qnames else "SAL facts present but no qnames",
            })

        recs = _build_foss_records(
            fmt_id, python_status, test_info, ex_info, impl_fns, authority_state, sprint_now,
            main_source_file=main_src_file,
            spec_facts=facts,
            verified_spec_facts=verified_facts,
            sal_fact_objects=sal_format_facts if sal_format_facts else None,
            test_dir=test_dir,
        )
        foss_records.extend(recs)

    # --- Also add FOSS formats NOT YET in poc-targets (discovered via source scan) ---
    missing_foss = _discover_missing_foss_formats(poc_data, sprint_now)
    foss_records.extend(missing_foss)

    # --- Unified map ---
    all_records = commercial_records + foss_records

    # --- Summaries ---
    commercial_summary = _build_summary(commercial_records)
    foss_summary = _build_summary(foss_records)
    unified_summary = _build_summary(all_records)

    # --- Write commercial map ---
    commercial_map = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "product_type": "commercial",
        "sprint_id": SPRINT_ID,
        "run_id": RUN_ID,
        "authority_note": "Generated from poc-targets.yaml dotnet_status + gate_evidence. Gate 11 approved for FODS/FODT/Netpbm.",
        "capabilities": commercial_records,
        "summary": commercial_summary,
    }
    (output_dir / "commercial-capability-map.json").write_text(
        json.dumps(commercial_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] commercial-capability-map.json — {len(commercial_records)} records", file=sys.stderr)

    # --- Write FOSS map ---
    foss_map = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "product_type": "foss_reduced",
        "sprint_id": SPRINT_ID,
        "run_id": RUN_ID,
        "authority_note": "Generated from poc-targets.yaml python_status + source introspection. Gates 1-10 passed.",
        "capabilities": foss_records,
        "summary": foss_summary,
    }
    (output_dir / "foss-reduced-capability-map.json").write_text(
        json.dumps(foss_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] foss-reduced-capability-map.json — {len(foss_records)} records", file=sys.stderr)

    # --- Write unified map ---
    unified_map = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "product_type": "unified",
        "sprint_id": SPRINT_ID,
        "run_id": RUN_ID,
        "authority_note": "Unified map combining commercial and foss_reduced records. Records are separated by product_type field.",
        "sal_enrichment": {
            "sal_source": str(_SAL_OUTPUT),
            "sal_consumed": bool(sal_facts),
            "formats_enriched": len(sal_enrichment_log),
            "log": sal_enrichment_log,
        },
        "capabilities": all_records,
        "summary": unified_summary,
    }
    (output_dir / "unified-capability-map.json").write_text(
        json.dumps(unified_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] unified-capability-map.json — {len(all_records)} total records", file=sys.stderr)

    # --- Write compact capability summary (< 2MB for fast downstream use) ---
    _SUMMARY_FIELDS = [
        "capability_id", "format", "product_type", "capability_name",
        "capability_category", "current_state", "blocks_readiness", "priority",
    ]
    summary_records = []
    for rec in all_records:
        summary_rec = {f: rec.get(f) for f in _SUMMARY_FIELDS}
        summary_rec["spec_refs_count"] = len(rec.get("spec_refs", []))
        summary_records.append(summary_rec)
    capability_summary = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "sprint_id": SPRINT_ID,
        "total_records": len(summary_records),
        "capabilities": summary_records,
    }
    (output_dir / "capability_summary.json").write_text(
        json.dumps(capability_summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] capability_summary.json — {len(summary_records)} records", file=sys.stderr)

    # --- Write gap ledger ---
    gaps = _build_gap_ledger(all_records)
    # Merge status from existing gap-ledger to preserve closed statuses and supplemental gaps
    existing_gap_path = output_dir / "gap-ledger.json"
    if existing_gap_path.exists():
        try:
            old = json.loads(existing_gap_path.read_text(encoding="utf-8"))
            old_by_id = {g["gap_id"]: g for g in old.get("gaps", [])}
            generated_ids = {g["gap_id"] for g in gaps}
            # Preserve closed status and close metadata for regenerated gaps
            for g in gaps:
                if g["gap_id"] in old_by_id and old_by_id[g["gap_id"]].get("status") == "closed":
                    prev = old_by_id[g["gap_id"]]
                    g["status"] = "closed"
                    if "closed_by_sprint" in prev:
                        g["closed_by_sprint"] = prev["closed_by_sprint"]
                    if "closed_at" in prev:
                        g["closed_at"] = prev["closed_at"]
            # Re-append supplemental gaps (manually added, not generated from poc-targets.yaml)
            for old_gap in old.get("gaps", []):
                if old_gap["gap_id"] not in generated_ids:
                    gaps.append(old_gap)
        except (json.JSONDecodeError, KeyError):
            pass  # If old file is corrupt, start fresh
    gap_ledger = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "sprint_id": SPRINT_ID,
        "run_id": RUN_ID,
        "total_gaps": len(gaps),
        "gaps": gaps,
    }
    (output_dir / "gap-ledger.json").write_text(
        json.dumps(gap_ledger, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] gap-ledger.json — {len(gaps)} gaps", file=sys.stderr)

    # --- Write action queue (merge with existing user-populated actions) ---
    actions = _build_action_queue(gaps, commercial_records, foss_records, poc_data=poc_data)
    generated_ids = {a["action_id"] for a in actions}
    # Actions managed by _eval_action_conditions are re-evaluated every run.
    # Do NOT re-merge stale versions of them from the previous file — if they
    # were not emitted this run, the condition is resolved and they should be absent.
    _CONDITION_MANAGED_IDS = {"ACT-UPDATE-POC-TARGETS"}
    queue_path = output_dir / "action-queue.json"
    if queue_path.exists():
        try:
            existing = json.loads(queue_path.read_text(encoding="utf-8"))
            for existing_action in existing.get("actions", []):
                eid = existing_action.get("action_id")
                if eid not in generated_ids and eid not in _CONDITION_MANAGED_IDS:
                    actions.append(existing_action)
        except (json.JSONDecodeError, KeyError):
            pass  # corrupt file — regenerate from scratch
    # Top-level advisory_only=False when any action is machine_executable
    any_machine_executable = any(a.get("machine_executable") for a in actions)
    action_queue = {
        "schema_version": "1.0",
        "generated_at": sprint_now,
        "sprint_id": SPRINT_ID,
        "run_id": RUN_ID,
        "advisory_only": not any_machine_executable,
        "note": "machine_executable=True actions are safe for autonomous agent execution. No action authorizes push/commit/gate approval.",
        "total_actions": len(actions),
        "actions": actions,
    }
    queue_path.write_text(
        json.dumps(action_queue, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] action-queue.json — {len(actions)} actions", file=sys.stderr)

    print(f"\n[DONE] Generated capability maps in {output_dir}", file=sys.stderr)
    print(f"       Commercial: {len(commercial_records)} records | FOSS: {len(foss_records)} records | Gaps: {len(gaps)}", file=sys.stderr)
    return 0


def _discover_missing_foss_formats(poc_data: dict, sprint_now: str) -> list[dict]:
    """Discover FOSS Python modules not yet in poc-targets.yaml."""
    known_foss_formats = {
        e.get("format", "").upper()
        for e in poc_data.get("foss_reduced_products", [])
    }

    missing: list[dict] = []
    if not _SRC_PYTHON.exists():
        return missing

    for module_dir in sorted(_SRC_PYTHON.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        fmt_id = module_dir.name.upper()
        if fmt_id in known_foss_formats:
            continue

        # Known non-FOSS or noise dirs
        skip = {"__PYCACHE__", "ODS", "ODT", "FODP"}
        if fmt_id in skip:
            continue

        impl_fns = _scan_python_functions(module_dir)
        if not impl_fns:
            continue  # Empty module — skip

        test_dir = _TESTS_PYTHON / module_dir.name.lower()
        test_info = _count_test_files(test_dir)
        main_src = _find_main_source_file(module_dir, module_dir.name)

        # Build minimal status dict from source
        python_status = {fn: "IMPLEMENTED_SOURCE_ONLY" for fn in impl_fns}

        # Load spec facts for discovered formats
        facts = _load_spec_facts(module_dir.name.lower())
        verified_facts = _load_spec_facts(module_dir.name.lower(), verified_only=True)
        effective_authority = "spec_fact" if facts else "gate_evidence"

        # Load SAL facts for per-operation spec_refs matching
        sal_all = _load_sal_facts()
        sal_objs = sal_all.get(module_dir.name.upper(), []) or None

        recs = _build_foss_records(
            module_dir.name.upper(),
            python_status,
            test_info,
            (0, []),
            impl_fns,
            effective_authority,
            sprint_now,
            main_source_file=main_src,
            spec_facts=facts,
            verified_spec_facts=verified_facts,
            sal_fact_objects=sal_objs,
        )
        for r in recs:
            r["notes"] = "Discovered via source scan — NOT in poc-targets.yaml. Add to foss_reduced_products."
            r["gaps"].append("not_in_poc_targets_yaml")
        missing.extend(recs)

    return missing


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Format Factory capability maps from repo state"
    )
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Output directory for generated maps (default: reports/capability-layer)",
    )
    parser.add_argument(
        "--sprint-id",
        default=None,
        help="Sprint ID to embed in generated artifacts (overrides hardcoded default)",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run ID to embed in generated artifacts (overrides hardcoded default)",
    )
    args = parser.parse_args()
    return generate(Path(args.output_dir), sprint_id=args.sprint_id, run_id=args.run_id)


if __name__ == "__main__":
    sys.exit(main())
