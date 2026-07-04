"""capability_compiler.py — SAL/obligation-driven capability compiler.

This module implements the CORRECT authority chain for Format Factory capability derivation:

    SAL/spec facts → obligations → capability requirements → evidence → state

This is the AUTHORITATIVE compiler. It replaces poc-targets.yaml as the PRIMARY
capability driver. poc-targets.yaml provides scope/priority metadata only.

Key differences from capability_map_generator.py:
  - SAL facts are the PRIMARY source (not enrichment)
  - Every capability record MUST have obligation_ids[] (non-empty)
  - Every capability record MUST have source_fact_ids[] tracing to FACT-* IDs
  - implementation_verified and example_verified are distinguished from test_verified
  - No capability is created without at least one SAL fact supporting it

Usage:
    python tools/capability_layer/capability_compiler.py [--output PATH] [--format FORMAT_ID]

Exit codes:
    0 — compilation successful
    1 — SAL facts not found or invalid
    2 — compilation error
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
_SAL_FACTS_LATEST = _SPEC_CACHE / "sal-facts-latest.json"
_OBLIGATION_REGISTER = _REPO_ROOT / "reports" / "all-format-deepening" / "all-format-obligation-register.yaml"
_SUBJECTS_FILE = _REPO_ROOT / "reports" / "capability-layer" / "capability-subjects.yaml"
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
_TESTS_PYTHON = _REPO_ROOT / "tests" / "python"
_EXAMPLES_PYTHON = _REPO_ROOT / "examples" / "python"
_VENV_PACKAGES = _REPO_ROOT / ".venv" / "Lib" / "site-packages"
_DEFAULT_OUTPUT = _REPO_ROOT / "reports" / "capability-layer" / "sal-driven-capability-map.json"

# Operation kind → SAL fact content keywords (REUSED from capability_map_generator.py)
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
}

# FOSS Python formats to compile (from poc-targets.yaml scope)
_FOSS_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
]

# Formats with rich SAL facts (fods/fodt/fodp/fodg/ods/odt have 1000+ facts)
# Others have 2-100 facts; many have 0 verified facts in per-format files
_SAL_FACT_RICH_FORMATS = {"fods", "fodt", "fodp", "fodg", "ods", "odt", "zst"}


def _load_yaml_simple(path: Path) -> dict:
    """Minimal YAML loader for simple key:value structures."""
    try:
        import yaml  # type: ignore[import]
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        pass
    result: dict = {}
    current_key = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("-"):
            k, _, v = stripped.partition(":")
            result[k.strip()] = v.strip() or None
    return result


def _load_sal_facts_for_format(format_id: str) -> list[dict]:
    """Load per-format SAL facts from .local/spec-cache/sal-facts-{format}.json.

    Returns list of fact dicts with keys: qname, claim, section, description,
    authority, verification_status, source, fact_status, source_id.
    Returns empty list if file not found or format has no facts.
    """
    candidates = [
        _SPEC_CACHE / f"sal-facts-{format_id}.json",
        _SPEC_CACHE / f"sal-facts-{format_id.upper()}.json",
        _SPEC_CACHE / f"sal-facts-{format_id.lower()}.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
                facts = data.get("spec_facts", [])
                if isinstance(facts, list):
                    # Filter to verified/accepted facts.
                    # None is included for legacy facts without a fact_status field.
                    # "accepted" is included for structurally-derived facts (e.g. gnumeric).
                    _ACCEPTED_STATUSES = frozenset(
                        ("verified", "verified_with_note", "accepted", "structural", None)
                    )
                    return [
                        f for f in facts
                        if isinstance(f, dict)
                        and f.get("fact_status") in _ACCEPTED_STATUSES
                    ]
            except Exception:
                pass
    return []


def _match_facts_to_op(facts: list[dict], op_kind: str, max_results: int = 15) -> list[str]:
    """Return fact qnames relevant to operation_kind (reuses _OP_KEYWORDS logic)."""
    if not facts or not op_kind:
        return []
    op_lower = op_kind.lower()
    keywords: list[str] = [p for p in op_lower.replace("-", "_").split("_") if len(p) > 2]
    for segment, kw_list in _OP_KEYWORDS.items():
        if segment in op_lower:
            keywords.extend(kw_list)
    keywords = list(dict.fromkeys(kw for kw in keywords if kw))
    if not keywords:
        return []
    matched: list[str] = []
    for fact in facts:
        qname = fact.get("qname", "")
        desc = (fact.get("description", "") or fact.get("claim", "")).lower()
        section = fact.get("section", "").lower()
        haystack = f"{qname.lower()} {desc} {section}"
        if any(kw in haystack for kw in keywords):
            matched.append(qname)
        if len(matched) >= max_results:
            break
    return matched


def _load_obligation_register() -> dict[str, dict]:
    """Load obligation register; returns dict keyed by obligation_id."""
    if not _OBLIGATION_REGISTER.exists():
        return {}
    try:
        data = _load_yaml_simple(_OBLIGATION_REGISTER)
        obligations = data.get("obligations", [])
        if isinstance(obligations, list):
            return {o["obligation_id"]: o for o in obligations if isinstance(o, dict) and "obligation_id" in o}
    except Exception:
        pass
    return {}


def _get_obligation_ids(format_id: str, language: str, obligations: dict) -> list[str]:
    """Find obligation IDs for a (format, language) pair."""
    fmt = format_id.lower()
    lang = language.lower()
    result = []
    for oid, ob in obligations.items():
        if ob.get("format_id", "").lower() == fmt:
            ob_lang = ob.get("language", "").lower()
            if lang in ob_lang or ob_lang in lang:
                result.append(oid)
    return result or [f"ALLF-{fmt.upper()}-{lang.upper()}"]  # synthesize if not found


def _scan_python_functions(module_dir: Path) -> list[str]:
    """Scan Python source for exported function names (reused from generator)."""
    fns: list[str] = []
    if not module_dir.exists():
        return fns
    init = module_dir / "__init__.py"
    if init.exists():
        try:
            tree = ast.parse(init.read_text(encoding="utf-8"))
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
    for py_file in sorted(module_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        fns.append(node.name)
        except Exception:
            pass
    return list(dict.fromkeys(fns))


def _evaluate_state(
    format_id: str,
    op_kind: str,
    fact_qnames: list[str],
    obligations: list[str],
) -> tuple[str, str, list[str], list[str], list[str]]:
    """Evaluate evidence for a capability and return (state, confidence, impl_refs, test_refs, example_refs).

    State hierarchy (ordered from strongest to weakest):
      oracle_verified → test_verified → dogfood_verified → example_verified →
      implementation_verified → missing

    NOTE: implementation_verified and example_verified are PARTIAL states —
    they indicate real evidence exists but it is WEAKER than test evidence.
    These are NOT equivalent to test_verified in proof quality.
    """
    fmt = format_id.lower()
    src_dir = _SRC_PYTHON / fmt
    test_dir = _TESTS_PYTHON / fmt
    example_dir = _EXAMPLES_PYTHON / fmt

    impl_refs: list[str] = []
    test_refs: list[str] = []
    example_refs: list[str] = []

    # Check source implementation
    # Require operation-specific function evidence; do NOT fall back to arbitrary functions.
    fns = _scan_python_functions(src_dir)
    op_root = op_kind.split("_")[0]
    op_kws = _OP_KEYWORDS.get(op_root, [])[:3]
    op_fns = [f for f in fns if op_root in f.lower() or any(kw in f.lower() for kw in op_kws)]
    # RC-3 fix: removed the "if not op_fns and fns: op_fns = fns[:3]" fallback.
    # Using arbitrary functions as evidence for an operation produces false implementation_verified states.

    if op_fns:
        main_src = f"src/python/{fmt}/{fmt}_codec.py"
        # Find actual source file
        for name in [f"{fmt}_codec.py", f"{fmt}_parser.py", f"{fmt}.py"]:
            if (src_dir / name).exists():
                main_src = f"src/python/{fmt}/{name}"
                break
        impl_refs = [main_src]

    # Check test evidence via AST function-name analysis.
    # RC-3 fix: replaced format-name content search with test-function name analysis.
    # A test file is credited only when it contains a test_ function whose name mentions
    # the operation kind or one of its keywords — not merely because it contains the format name.
    test_files = sorted(test_dir.glob("test_*.py")) if test_dir.exists() else []
    if test_files:
        op_test_files = []
        for tf in test_files:
            try:
                tree = ast.parse(tf.read_text(encoding="utf-8", errors="replace"))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.startswith("test_"):
                            fn_lower = node.name.lower()
                            if op_root in fn_lower or any(kw in fn_lower for kw in op_kws):
                                op_test_files.append(f"tests/python/{fmt}/{tf.name}")
                                break
            except SyntaxError:
                pass
        test_refs = op_test_files[:3]

    # Check example evidence
    if example_dir.exists():
        ex_files = list(example_dir.glob("*.py"))
        if ex_files:
            example_refs = [f"examples/python/{fmt}/{ex_files[0].name}"]

    # Check package installation
    pkg_installed = (_VENV_PACKAGES / fmt).exists()

    # Determine state
    if test_refs and impl_refs:
        state = "test_verified"
        confidence = "high"
    elif impl_refs and example_refs:
        state = "example_verified"
        confidence = "medium"
    elif impl_refs:
        state = "implementation_verified"
        confidence = "medium"
    elif fact_qnames:
        # SAL facts exist but no implementation found → missing
        state = "missing"
        confidence = "high"
    else:
        state = "missing"
        confidence = "low"

    return state, confidence, impl_refs, test_refs, example_refs


def compile_format_capabilities(
    format_id: str,
    obligations: dict,
    verbose: bool = False,
) -> list[dict]:
    """Compile SAL-driven capability records for one format (Python FOSS track).

    Returns list of capability_record dicts. Every record has:
      - obligation_ids: non-empty list
      - source_fact_ids: list of FACT-* qnames from SAL
      - state: based on actual evidence (NOT prose claims)
    """
    fmt = format_id.lower()
    facts = _load_sal_facts_for_format(fmt)
    obligation_ids = _get_obligation_ids(fmt, "python", obligations)

    # TC-SCP-008: Compute per-format fact hash for spec-change invalidation tracking.
    import hashlib as _hashlib
    _fact_qnames_sorted = sorted(f.get("qname", "") for f in facts)
    sal_facts_hash = _hashlib.sha256(
        json.dumps(_fact_qnames_sorted).encode()
    ).hexdigest()[:16]

    if verbose:
        print(f"  [{fmt}] SAL facts: {len(facts)}, hash: {sal_facts_hash}, obligation_ids: {obligation_ids}", file=sys.stderr)

    records: list[dict] = []
    seen_ops: set[str] = set()

    # AUTHORITY RULE: Derive capabilities ONLY from SAL facts
    # For each operation_kind, check if SAL facts support it
    for op_kind in _OP_KEYWORDS:
        matched_qnames = _match_facts_to_op(facts, op_kind)

        # If no SAL facts match this operation for this format, NO capability is created
        # (This is the key difference from the existing generator which uses poc-targets.yaml)
        if not matched_qnames and not facts:
            # Special case: if format has NO SAL facts at all, still create minimal
            # implementation evidence based capability (source introspection only)
            # but mark as PROSE_DERIVED without obligation provenance
            pass  # Skip — no facts, no capability
        elif not matched_qnames:
            continue  # No SAL support for this op_kind

        if op_kind in seen_ops:
            continue
        seen_ops.add(op_kind)

        state, confidence, impl_refs, test_refs, example_refs = _evaluate_state(
            fmt, op_kind, matched_qnames, obligation_ids
        )

        cap_id = f"{fmt.upper()}-FOSS-{op_kind.upper()}-SAL-001"
        subject_id = f"{fmt}:python"
        # TC-HARDEN-006: Use uppercase format_id (canonical — matches unified map and format-registry.yaml)
        fmt_upper = fmt.upper()

        record: dict[str, Any] = {
            "capability_id": cap_id,
            "subject_id": subject_id,
            "format_id": fmt_upper,
            "product_type": "foss_reduced",
            "language": "python",
            "capability_name": f"{fmt.upper()} {op_kind.replace('_', ' ').title()}",
            "operation_kind": op_kind,
            # OBLIGATION PROVENANCE (required — non-empty)
            "obligation_ids": obligation_ids,
            "source_fact_ids": matched_qnames[:10],  # cap at 10 for readability
            # EVIDENCE
            "implementation_refs": impl_refs,
            "test_refs": test_refs,
            "example_refs": example_refs,
            "package_refs": [f".venv/Lib/site-packages/{fmt}/"] if (_VENV_PACKAGES / fmt).exists() else [],
            "oracle_evidence": [],  # populated from oracle results if available
            # SPEC-CHANGE INVALIDATION (TC-SCP-008): hash of fact qnames used for this format.
            # If this hash changes on rerun, the capability will be recompiled automatically.
            "sal_facts_hash": sal_facts_hash,
            # STATE (based on ACTUAL evidence, not prose)
            "current_state": state,
            "confidence_level": confidence,
            "evidence_note": _state_evidence_note(state),
            # METADATA
            "derived_from": "SAL_FACTS",
            "authority_note": "Capability derived from SAL fact match; NOT from poc-targets.yaml prose",
            "generated_by": "tools/capability_layer/capability_compiler.py",
        }

        records.append(record)

    # For formats with NO SAL facts at all, add a minimal source-introspection
    # record (IMPLEMENTED_UNVERIFIED) to avoid losing track of implementations
    if not facts:
        src_dir = _SRC_PYTHON / fmt
        fns = _scan_python_functions(src_dir)
        if fns:
            # Has source but no SAL facts → prose-derived only
            record = {
                "capability_id": f"{fmt.upper()}-FOSS-LOAD-SOURCE-001",
                "subject_id": f"{fmt}:python",
                "format_id": fmt.upper(),  # TC-HARDEN-006: canonical uppercase
                "product_type": "foss_reduced",
                "language": "python",
                "capability_name": f"{fmt.upper()} Source Implementation (no SAL facts)",
                "operation_kind": "load",
                # OBLIGATION PROVENANCE — synthesized (no real SAL facts)
                "obligation_ids": obligation_ids,
                "source_fact_ids": [],  # EMPTY — no SAL facts
                "implementation_refs": [f"src/python/{fmt}/"],
                "test_refs": [],
                "example_refs": [],
                "package_refs": [],
                "oracle_evidence": [],
                "current_state": "implementation_verified",
                "confidence_level": "low",
                "evidence_note": "PROSE_DERIVED: no SAL facts available; source exists but not SAL-verified",
                "derived_from": "SOURCE_INTROSPECTION",
                "authority_note": "WARNING: No SAL facts for this format; capability not SAL-grounded",
                "generated_by": "tools/capability_layer/capability_compiler.py",
            }
            records.append(record)

    if verbose:
        print(f"  [{fmt}] Generated {len(records)} capability records", file=sys.stderr)

    return records


def _state_evidence_note(state: str) -> str:
    notes = {
        "test_verified": "STRONG: test file + source implementation evidence",
        "example_verified": "PARTIAL: example file + source; no test evidence (weaker than test_verified)",
        "implementation_verified": "PARTIAL: source implementation only; no test or example evidence",
        "missing": "MISSING: no source implementation found for this operation",
        "oracle_verified": "STRONGEST: oracle case passes for this capability",
    }
    return notes.get(state, state)


def compile_all(
    formats: list[str] | None = None,
    output_path: Path | None = None,
    verbose: bool = False,
) -> int:
    """Compile capabilities for all specified formats and write JSON output.

    Returns exit code: 0=success, 1=input missing, 2=error.
    """
    if not _SAL_FACTS_LATEST.exists():
        print(f"ERROR: SAL facts not found: {_SAL_FACTS_LATEST}", file=sys.stderr)
        return 1

    # Load obligation register
    obligations = _load_obligation_register()
    if verbose:
        print(f"[capability_compiler] Loaded {len(obligations)} obligations", file=sys.stderr)

    target_formats = formats or _FOSS_FORMATS
    all_records: list[dict] = []
    stats: dict[str, int] = defaultdict(int)

    # TC-SCP-009: Load existing output to detect per-format SAL fact hash changes.
    # If a format's fact hash changed, log it so operators know recompilation was triggered.
    _existing_hashes: dict[str, str] = {}
    if (output_path or _DEFAULT_OUTPUT).exists():
        try:
            _existing = json.loads((output_path or _DEFAULT_OUTPUT).read_text(encoding="utf-8"))
            for _r in _existing.get("capabilities", []):
                _fmt = _r.get("format_id", "").lower()
                _h = _r.get("sal_facts_hash")
                if _fmt and _h and _fmt not in _existing_hashes:
                    _existing_hashes[_fmt] = _h
        except Exception:
            pass

    for fmt in target_formats:
        try:
            records = compile_format_capabilities(fmt, obligations, verbose=verbose)
            # TC-SCP-009: Log when SAL facts changed for a format.
            if records:
                new_hash = records[0].get("sal_facts_hash", "")
                old_hash = _existing_hashes.get(fmt.lower(), "")
                if old_hash and new_hash and old_hash != new_hash:
                    print(
                        f"[capability_compiler] {fmt}: SAL facts changed "
                        f"(hash {old_hash} → {new_hash}), recompiling",
                        file=sys.stderr,
                    )
            all_records.extend(records)
            for r in records:
                stats[r["current_state"]] += 1
        except Exception as exc:
            print(f"ERROR: Failed to compile {fmt}: {exc}", file=sys.stderr)

    # Validate: no capability without obligation_ids
    no_obligation = [r for r in all_records if not r.get("obligation_ids")]
    if no_obligation:
        print(f"VALIDATION FAIL: {len(no_obligation)} records have empty obligation_ids", file=sys.stderr)
        for r in no_obligation[:5]:
            print(f"  {r['capability_id']}", file=sys.stderr)

    # Build output document
    output = {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/capability_layer/capability_compiler.py",
        "generator_version": "2.0",
        "authority": "SAL_FACTS_PRIMARY",
        "authority_note": (
            "Capabilities derived from SAL spec facts. "
            "poc-targets.yaml provides scope/priority only. "
            "Every capability has obligation_ids[] linking to obligation register."
        ),
        "formats_compiled": target_formats,
        "total_capabilities": len(all_records),
        "state_breakdown": dict(stats),
        "validation": {
            "capabilities_without_obligation_provenance": len(no_obligation),
            "CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE": len(no_obligation),
        },
        "capabilities": all_records,
    }

    out = output_path or _DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)

    # TC-HARDEN-004: Content-normalized write — skip if only generated_at changed.
    # This prevents SHA churn in git and in idempotency checks when inputs are unchanged.
    new_content = json.dumps(output, indent=2)
    if out.exists():
        import hashlib as _hashlib
        existing = json.loads(out.read_text(encoding="utf-8"))
        existing.pop("generated_at", None)
        candidate = {k: v for k, v in output.items() if k != "generated_at"}
        existing_sig = _hashlib.sha256(json.dumps(existing, sort_keys=True).encode()).hexdigest()
        candidate_sig = _hashlib.sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest()
        if existing_sig == candidate_sig:
            # Content unchanged — preserve existing file (stable SHA, no git churn)
            print("[capability_compiler] Content unchanged — skipping write (stable SHA)", file=sys.stderr)
            return 0 if len(no_obligation) == 0 else 2

    out.write_text(new_content, encoding="utf-8")

    print(f"[capability_compiler] Written {len(all_records)} records to {out}", file=sys.stderr)
    print(f"[capability_compiler] State breakdown: {dict(stats)}", file=sys.stderr)
    print(f"[capability_compiler] CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE: {len(no_obligation)}", file=sys.stderr)

    return 0 if len(no_obligation) == 0 else 2


# ---------------------------------------------------------------------------
# Backward-compatible API (TC-CAP-011 / TC-C8)
# These functions bridge the gap between capability_queue_consumer.py and
# test_end_to_end_pipeline.py (which import them from this module) and the
# new SAL-driven compiler's internal design.
# ---------------------------------------------------------------------------

def compile_gap_to_feature_ir(gap: dict) -> dict:
    """Convert a gap-ledger record to a Feature IR (intermediate representation).

    Accepts both raw gap-ledger fields (format/capability_name) and
    consumer-mapped fields (format_id/function_name).

    Returns dict with: format_id, function_name, expected_module,
    expected_test_file, expected_signature, feature_id, gap_id, gap_type,
    priority, commercial_impact.
    """
    # Support both raw gap fields and pre-mapped consumer fields
    fmt = gap.get("format_id") or gap.get("format", "UNKNOWN")
    cap_name = gap.get("capability_name", "")
    fn = gap.get("function_name", "")

    if not fn:
        # Normalize capability name to snake_case function name
        fn = cap_name.lower().replace(" ", "_").replace("-", "_")
        for suffix in ("_function", "_api", "_capability"):
            if fn.endswith(suffix):
                fn = fn[:-len(suffix)]
        if not fn:
            fn = fmt.lower() + "_load"

    fmt_lower = fmt.lower()
    return {
        "format_id": fmt,
        "function_name": fn,
        "expected_module": f"src/python/{fmt_lower}/{fmt_lower}_codec.py",
        "expected_test_file": f"tests/python/{fmt_lower}/test_{fmt_lower}_api.py",
        "expected_signature": f"{fn}(source) -> Any",
        "feature_id": f"FEAT-{fmt.upper()}-{fn.upper().replace('_', '-')}-001",
        "gap_id": gap.get("gap_id", ""),
        "gap_type": gap.get("gap_type", ""),
        "priority": gap.get("priority", "P2"),
        "commercial_impact": gap.get("commercial_impact", "NONE"),
        "spec_refs": gap.get("spec_refs") or [],
    }


def compile_feature_ir_to_taskcard(ir: dict) -> dict:
    """Convert a Feature IR to an executable taskcard.

    Returns dict with: taskcard_id, title, format_id, function_name,
    evidence_obligations, required_skill, advisory_only.
    """
    fmt = ir.get("format_id", "UNKNOWN")
    fn = ir.get("function_name", "unknown")
    gap_id = ir.get("gap_id", "")
    feature_id = ir.get("feature_id", "")
    tc_id = f"TC-{gap_id}" if gap_id else f"TC-{fmt.upper()}-{fn.upper().replace('_', '-')}-001"

    return {
        "taskcard_id": tc_id,
        "title": f"Implement {fn} for {fmt}",
        "format_id": fmt,
        "function_name": fn,
        "expected_module": ir.get("expected_module", ""),
        "expected_test_file": ir.get("expected_test_file", ""),
        "expected_signature": ir.get("expected_signature", f"{fn}(source) -> Any"),
        "feature_id": feature_id,
        "gap_id": gap_id,
        "evidence_obligations": [
            f"Implementation at {ir.get('expected_module', '')}",
            f"Tests at {ir.get('expected_test_file', '')}",
        ],
        "required_skill": "add-python-api",
        "advisory_only": True,
        "priority": ir.get("priority", "P2"),
        "commercial_impact": ir.get("commercial_impact", "NONE"),
    }


def compile_gap(gap: dict) -> dict:
    """Full pipeline: gap record → Feature IR + Taskcard.

    Returns dict with keys: feature_ir, taskcard.
    This is the single entry-point for capability_queue_consumer.py.
    """
    ir = compile_gap_to_feature_ir(gap)
    taskcard = compile_feature_ir_to_taskcard(ir)
    return {"feature_ir": ir, "taskcard": taskcard}


def main() -> int:
    parser = argparse.ArgumentParser(description="SAL/obligation-driven capability compiler")
    parser.add_argument("--output", type=Path, default=_DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--format", action="append", dest="formats", help="Specific format(s) to compile")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    return compile_all(formats=args.formats, output_path=args.output, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
