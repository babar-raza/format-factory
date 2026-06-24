"""Capability-to-feature compiler — executable implementation.

Compiles capability gap records into feature IRs and executable taskcards.
This is the executable version of the compiler pilot.

Usage:
    python tools/supervisor/capability_compiler.py \
        --gap-record '{"format_id": "FODP", "function_name": "fodp_slide_notes", ...}' \
        --output-dir .local/evidences/<run_id>/taskcards/generated/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAL_OUTPUT_PATH = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"

_sal_cache: dict[str, list[dict]] | None = None


def load_sal_facts(sal_path: Path | None = None) -> dict[str, list[dict]]:
    """Load SAL spec facts indexed by format_id (case-insensitive).

    Returns a dict mapping uppercase format_id -> list of fact dicts.
    Each fact has: qname, section, description, authority.
    """
    global _sal_cache
    if _sal_cache is not None:
        return _sal_cache

    path = sal_path or SAL_OUTPUT_PATH
    if not path.is_file():
        _sal_cache = {}
        return _sal_cache

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        _sal_cache = {}
        return _sal_cache

    index: dict[str, list[dict]] = {}
    for entry in data.get("results", []):
        fmt = entry.get("format_id", "").upper()
        if fmt:
            index[fmt] = entry.get("spec_facts", [])
    _sal_cache = index
    return _sal_cache


def reset_sal_cache() -> None:
    """Clear the SAL facts cache (for testing)."""
    global _sal_cache
    _sal_cache = None


# ---------------------------------------------------------------------------
# Format family metadata
# ---------------------------------------------------------------------------

FORMAT_FAMILIES = {
    "FODP": {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/fodp"},
    "FODS": {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/fods"},
    "FODT": {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/fodt"},
    "FODG": {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/fodg"},
    "ODS":  {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/ods"},
    "ODT":  {"family": "ODF", "spec": "ODF 1.3 Part 3", "module_base": "src/python/odt"},
    "CSV":  {"family": "Tabular", "spec": "RFC 4180", "module_base": "src/python/csv"},
    "TSV":  {"family": "Tabular", "spec": "IANA TSV", "module_base": "src/python/tsv"},
    "QOI":  {"family": "Image", "spec": "QOI Spec 1.0", "module_base": "src/python/qoi"},
    "XCF":  {"family": "Image", "spec": "GIMP XCF", "module_base": "src/python/xcf"},
    "ZST":  {"family": "Compression", "spec": "RFC 8878", "module_base": "src/python/zst"},
    "ABW":  {"family": "Document", "spec": "AbiWord XML", "module_base": "src/python/abw"},
    "TOML": {"family": "Config", "spec": "TOML v1.0", "module_base": "src/python/toml"},
    "DIF":  {"family": "Tabular", "spec": "DIF 1983", "module_base": "src/python/dif"},
    "SYLK": {"family": "Tabular", "spec": "SYLK Microsoft", "module_base": "src/python/sylk"},
    "Gnumeric": {"family": "Spreadsheet", "spec": "Gnumeric XML", "module_base": "src/python/gnumeric"},
    "PBM":  {"family": "Netpbm", "spec": "Netpbm PBM", "module_base": "src/python/pbm"},
    "PGM":  {"family": "Netpbm", "spec": "Netpbm PGM", "module_base": "src/python/pgm"},
    "PPM":  {"family": "Netpbm", "spec": "Netpbm PPM", "module_base": "src/python/ppm"},
    "NDJSON": {"family": "JSON", "spec": "NDJSON Spec", "module_base": "src/python/ndjson"},
}

# Module file naming convention
MODULE_FILE_MAP = {
    "FODP": "fodp_codec.py", "FODS": "fods_codec.py", "FODT": "fodt_codec.py",
    "FODG": "fodg_codec.py", "ODS": "ods_parser.py", "ODT": "odt_parser.py",
    "CSV": "csv_parser.py", "TSV": "tsv_parser.py", "QOI": "qoi_parser.py",
    "XCF": "xcf_parser.py", "ZST": "zst_codec.py", "ABW": "abw_codec.py",
    "TOML": "toml_codec.py", "DIF": "dif_parser.py", "SYLK": "sylk_parser.py",
    "Gnumeric": "gnumeric_codec.py", "PBM": "pbm_parser.py", "PGM": "pgm_parser.py",
    "PPM": "ppm_parser.py", "NDJSON": "ndjson_codec.py",
}


def _deterministic_id(prefix: str, *parts: str) -> str:
    """Generate a deterministic ID from parts (no timestamps)."""
    combined = "-".join(str(p) for p in parts)
    short_hash = hashlib.sha256(combined.encode()).hexdigest()[:8]
    return f"{prefix}-{short_hash}".upper()


QNAME_OUTPUT_DIR = REPO_ROOT / ".local" / "qname-output"


def validate_sal_input(gap: dict, sal_path: Path | None = None) -> dict:
    """Phase 0: Validate SAL/spec inputs before compilation.

    Checks that SAL output exists, is parseable, and contains facts for the
    target format. Returns a validation result dict.
    """
    fmt = gap.get("format_id", "UNKNOWN").upper()
    path = sal_path or SAL_OUTPUT_PATH

    result: dict[str, Any] = {
        "phase": 0,
        "phase_name": "sal_input_validation",
        "format_id": fmt,
        "sal_path": str(path),
        "sal_exists": path.is_file(),
        "sal_parseable": False,
        "format_facts_found": False,
        "facts_count": 0,
        "valid": False,
        "warnings": [],
    }

    if not path.is_file():
        result["warnings"].append("SAL output not found — compilation proceeds without spec enrichment")
        result["valid"] = True  # Valid to compile without SAL (degraded mode)
        return result

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        result["sal_parseable"] = True
    except (json.JSONDecodeError, OSError) as exc:
        result["warnings"].append(f"SAL output malformed: {exc}")
        result["valid"] = True  # Degraded mode
        return result

    if not isinstance(data, dict) or "results" not in data:
        result["warnings"].append("SAL output missing 'results' key — quarantined")
        result["valid"] = True
        return result

    sal_facts = load_sal_facts(sal_path)
    format_facts = sal_facts.get(fmt, [])
    result["format_facts_found"] = bool(format_facts)
    result["facts_count"] = len(format_facts)
    result["valid"] = True

    if not format_facts:
        result["warnings"].append(f"No SAL facts for format {fmt}")

    return result


def compile_gap_to_feature_graph(feature_ir: dict) -> dict:
    """Phase 3: Generate a feature graph node from a feature IR.

    Produces a graph node with dependencies and connections to spec concepts.
    """
    fmt = feature_ir["format_id"]
    func = feature_ir["function_name"]

    return {
        "node_id": feature_ir["feature_id"],
        "format_id": fmt,
        "function_name": func,
        "node_type": "feature",
        "spec_connections": feature_ir.get("spec_qnames", []),
        "depends_on": [],
        "enables": [],
        "module_path": feature_ir["expected_module"],
        "test_path": feature_ir["expected_test_file"],
        "spec_coverage": "covered" if feature_ir.get("spec_qnames") else "uncovered",
    }


def attach_qname_ontology(feature_ir: dict) -> dict:
    """Phase 3.5: Attach QName ontology reference to feature IR.

    Looks up the QName-to-code map for the format and enriches the feature IR
    with ontology references.
    """
    fmt = feature_ir["format_id"].upper()
    qname_dir = QNAME_OUTPUT_DIR / fmt
    qname_map_path = qname_dir / f"qname-to-code-map-{fmt.lower()}.json"

    ontology_ref: dict[str, Any] = {
        "qname_map_exists": qname_map_path.is_file(),
        "qname_map_path": str(qname_map_path) if qname_map_path.is_file() else None,
        "coverage_percent": None,
        "mapped_qnames": [],
    }

    if qname_map_path.is_file():
        try:
            qdata = json.loads(qname_map_path.read_text(encoding="utf-8"))
            coverage = qdata.get("coverage_summary", {})
            ontology_ref["coverage_percent"] = coverage.get("coverage_percent")
            ontology_ref["mapped_qnames"] = [
                m.get("qname", "")
                for m in qdata.get("mappings", [])
                if m.get("qname")
            ]
        except (json.JSONDecodeError, OSError):
            ontology_ref["qname_map_exists"] = False

    enriched = dict(feature_ir)
    enriched["qname_ontology"] = ontology_ref
    return enriched


def compile_test_obligation_matrix(feature_ir: dict) -> dict:
    """Phase 6: Generate a test obligation matrix entry.

    Maps feature requirements to required test types.
    """
    func = feature_ir["function_name"]
    fmt = feature_ir["format_id"]
    obligations = feature_ir.get("test_obligation_count", 10)

    return {
        "feature_id": feature_ir["feature_id"],
        "format_id": fmt,
        "function_name": func,
        "min_tests_required": obligations,
        "test_types": [
            {"type": "file_based_input", "required": True, "description": f"Test {func} with a real {fmt} file"},
            {"type": "string_input", "required": True, "description": f"Test {func} with string/bytes input"},
            {"type": "empty_input", "required": True, "description": f"Test {func} with empty/missing input"},
            {"type": "return_type_check", "required": True, "description": f"Assert return type of {func}"},
            {"type": "error_handling", "required": True, "description": f"Test {func} error paths"},
        ],
        "expected_test_file": feature_ir["expected_test_file"],
    }


def compile_evidence_obligation_matrix(feature_ir: dict) -> dict:
    """Phase 7: Generate an evidence obligation matrix entry.

    Maps feature to required evidence artifacts.
    """
    return {
        "feature_id": feature_ir["feature_id"],
        "format_id": feature_ir["format_id"],
        "function_name": feature_ir["function_name"],
        "evidence_obligations": [
            {"type": "source_diff", "required": True, "description": "Git diff showing source changes"},
            {"type": "test_log", "required": True, "description": "pytest output showing all tests pass"},
            {"type": "ledger_entry", "required": True, "description": "Entry in product-code-change-ledger.json"},
            {"type": "export_in_init", "required": True, "description": "Function exported in __init__.py __all__"},
        ],
    }


def compile_gate_readiness_projection(feature_ir: dict, taskcard: dict) -> dict:
    """Phase 8: Project gate readiness impact of completing this feature.

    Estimates how completing this taskcard affects gate readiness.
    """
    fmt = feature_ir["format_id"]
    has_spec = bool(feature_ir.get("spec_qnames"))

    return {
        "feature_id": feature_ir["feature_id"],
        "format_id": fmt,
        "function_name": feature_ir["function_name"],
        "taskcard_id": taskcard["taskcard_id"],
        "gate_impact": {
            "gate_4_prototype": "advances" if not has_spec else "already_passed",
            "gate_8_foss_readiness": "advances",
            "gate_11_commercial": "no_direct_impact",  # FOSS work doesn't directly advance Gate 11
        },
        "spec_coverage_after": "partial" if has_spec else "none",
        "blocks_gate_11": False,  # Gate 11 is externally gated by Babar Raza
    }


def compile_gap_to_feature_ir(gap: dict) -> dict:
    """Phase 1: Compile a gap record into a feature IR."""
    # Accept both consumer-mapped fields (format_id/function_name) and raw gap-ledger
    # fields (format/capability_name).  The queue consumer maps before calling, but
    # CLI callers pass raw gap-ledger records directly.
    fmt = gap.get("format_id") or gap.get("format", "UNKNOWN")
    if fmt != "UNKNOWN":
        fmt = fmt.upper()
    raw_name = gap.get("function_name") or gap.get("capability_name", "unknown_func")
    func = raw_name.lower().replace(" ", "_")
    if func != "unknown_func" and not func.startswith(fmt.lower() + "_"):
        func = f"{fmt.lower()}_{func}"
    sig = gap.get("expected_signature", f"{func}(source) -> Any")
    family = FORMAT_FAMILIES.get(fmt, {})
    module_base = family.get("module_base", f"src/python/{fmt.lower()}")
    module_file = MODULE_FILE_MAP.get(fmt, f"{fmt.lower()}_codec.py")

    feature_id = _deterministic_id("FEAT", fmt, func)

    # Look up SAL spec facts for this format
    sal_facts = load_sal_facts()
    format_facts = sal_facts.get(fmt.upper(), [])
    spec_qnames = [f.get("qname", "") for f in format_facts if f.get("qname")]

    return {
        "feature_id": feature_id,
        "format_id": fmt,
        "function_name": func,
        "expected_signature": sig,
        "expected_module": f"{module_base}/{module_file}",
        "expected_test_file": f"tests/python/{fmt.lower()}/test_rXXX_{func}.py",
        "format_family": family.get("family", "Unknown"),
        "spec_ref": family.get("spec", "no_public_spec_available"),
        "spec_qnames": spec_qnames,
        "spec_facts_count": len(format_facts),
        "test_obligation_count": 10,
        "evidence_obligations": [
            "source_diff",
            "test_log",
            "ledger_entry",
            "export_in_init",
        ],
    }


def compile_feature_ir_to_taskcard(feature_ir: dict) -> dict:
    """Phase 2: Compile a feature IR into an executable taskcard."""
    func = feature_ir["function_name"]
    fmt = feature_ir["format_id"]
    taskcard_id = _deterministic_id("TC", fmt, func)

    return {
        "taskcard_id": taskcard_id,
        "title": f"Implement {func} function",
        "generated_by": "capability_compiler",
        "lane_id": "lane-10-product",
        "wave_id": "wave-product",
        "format_id": fmt,
        "function_name": func,
        "expected_signature": feature_ir["expected_signature"],
        "expected_module": feature_ir["expected_module"],
        "expected_test_file": feature_ir["expected_test_file"],
        "governance_requirements": {
            "execution_method": "DIRECT_IMPLEMENTATION",
            "idempotency_key": f"{taskcard_id}-exec",
            "route_decision_id": f"CAPABILITY-BACKED-{fmt}-DEEPENING",
            "exception_classification": (
                "spec_authority_available"
                if feature_ir.get("spec_qnames")
                else "no_public_spec_available"
            ),
            "spec_qnames": feature_ir.get("spec_qnames", []),
            "spec_facts_count": feature_ir.get("spec_facts_count", 0),
            "source_diff_paths": [
                feature_ir["expected_module"],
                f"{'/'.join(feature_ir['expected_module'].split('/')[:-1])}/__init__.py",
            ],
        },
        "test_obligations": {
            "min_test_count": feature_ir["test_obligation_count"],
            "required_test_types": [
                "file_based_input",
                "string_input",
                "empty_input",
                "return_type_check",
                "error_handling",
            ],
        },
        "evidence_obligations": feature_ir["evidence_obligations"],
        "acceptance_criteria": (
            f"{func} returns correct output; "
            f"{feature_ir['test_obligation_count']}+ tests pass; "
            f"ledger entry added; exported in __init__.py"
        ),
        "status": "READY_TO_EXECUTE",
    }


def compile_gap(gap: dict, sal_path: Path | None = None) -> dict:
    """Full compilation: phases 0-8 (gap -> feature IR -> taskcard + all matrices).

    Phase 0: SAL input validation
    Phase 1: Gap -> Feature IR
    Phase 2: Feature IR -> Taskcard
    Phase 3: Feature graph node
    Phase 3.5: QName ontology attachment
    Phase 6: Test obligation matrix
    Phase 7: Evidence obligation matrix
    Phase 8: Gate readiness projection
    """
    # Phase 0: Validate SAL input
    sal_validation = validate_sal_input(gap, sal_path)

    # Phase 1: Feature IR
    feature_ir = compile_gap_to_feature_ir(gap)

    # Phase 2: Taskcard
    taskcard = compile_feature_ir_to_taskcard(feature_ir)

    # Phase 3: Feature graph
    feature_graph = compile_gap_to_feature_graph(feature_ir)

    # Phase 3.5: QName ontology
    enriched_ir = attach_qname_ontology(feature_ir)

    # Phase 6: Test obligation matrix
    test_obligations = compile_test_obligation_matrix(feature_ir)

    # Phase 7: Evidence obligation matrix
    evidence_obligations = compile_evidence_obligation_matrix(feature_ir)

    # Phase 8: Gate readiness projection
    gate_projection = compile_gate_readiness_projection(feature_ir, taskcard)

    return {
        "gap": gap,
        "sal_validation": sal_validation,
        "feature_ir": enriched_ir,
        "taskcard": taskcard,
        "feature_graph": feature_graph,
        "test_obligation_matrix": test_obligations,
        "evidence_obligation_matrix": evidence_obligations,
        "gate_readiness_projection": gate_projection,
        "phases_executed": [0, 1, 2, 3, 3.5, 6, 7, 8],
    }


def write_outputs(compilation: dict, output_dir: Path) -> dict:
    """Write all compilation outputs to files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, str] = {}

    ir_path = output_dir / "feature-ir.json"
    ir_path.write_text(json.dumps(compilation["feature_ir"], indent=2), encoding="utf-8")
    paths["feature_ir_path"] = str(ir_path)

    tc_path = output_dir / "taskcard.json"
    tc_path.write_text(json.dumps(compilation["taskcard"], indent=2), encoding="utf-8")
    paths["taskcard_path"] = str(tc_path)

    # Phase 0: SAL validation
    if "sal_validation" in compilation:
        sv_path = output_dir / "sal-validation.json"
        sv_path.write_text(json.dumps(compilation["sal_validation"], indent=2), encoding="utf-8")
        paths["sal_validation_path"] = str(sv_path)

    # Phase 3: Feature graph
    if "feature_graph" in compilation:
        fg_path = output_dir / "feature-graph.json"
        fg_path.write_text(json.dumps(compilation["feature_graph"], indent=2), encoding="utf-8")
        paths["feature_graph_path"] = str(fg_path)

    # Phase 6: Test obligation matrix
    if "test_obligation_matrix" in compilation:
        tom_path = output_dir / "test-obligation-matrix.json"
        tom_path.write_text(json.dumps(compilation["test_obligation_matrix"], indent=2), encoding="utf-8")
        paths["test_obligation_matrix_path"] = str(tom_path)

    # Phase 7: Evidence obligation matrix
    if "evidence_obligation_matrix" in compilation:
        eom_path = output_dir / "evidence-obligation-matrix.json"
        eom_path.write_text(json.dumps(compilation["evidence_obligation_matrix"], indent=2), encoding="utf-8")
        paths["evidence_obligation_matrix_path"] = str(eom_path)

    # Phase 8: Gate readiness
    if "gate_readiness_projection" in compilation:
        gr_path = output_dir / "gate-readiness-projection.json"
        gr_path.write_text(json.dumps(compilation["gate_readiness_projection"], indent=2), encoding="utf-8")
        paths["gate_readiness_projection_path"] = str(gr_path)

    return paths


def verify_idempotency(gap: dict) -> dict:
    """Run compilation twice and verify outputs are identical."""
    r1 = compile_gap(gap)
    r2 = compile_gap(gap)

    ir_match = json.dumps(r1["feature_ir"], sort_keys=True) == json.dumps(r2["feature_ir"], sort_keys=True)
    tc_match = json.dumps(r1["taskcard"], sort_keys=True) == json.dumps(r2["taskcard"], sort_keys=True)

    return {
        "idempotent": ir_match and tc_match,
        "feature_ir_match": ir_match,
        "taskcard_match": tc_match,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capability-to-feature compiler")
    parser.add_argument("--gap-record", required=True, help="Gap record as JSON string")
    parser.add_argument("--output-dir", required=True, help="Output directory for artifacts")
    parser.add_argument("--verify-idempotency", action="store_true")
    args = parser.parse_args()

    gap = json.loads(args.gap_record)
    compilation = compile_gap(gap)
    paths = write_outputs(compilation, Path(args.output_dir))

    print(f"Feature IR: {paths['feature_ir_path']}")
    print(f"Taskcard:   {paths['taskcard_path']}")

    if args.verify_idempotency:
        idem = verify_idempotency(gap)
        print(f"Idempotent: {idem['idempotent']}")
        if not idem["idempotent"]:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
