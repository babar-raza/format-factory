"""Derived-property oracle execution for model-based formats.

generated_by: codex
"""

import importlib
import sys


ENRICHED_LOADERS = {
    "ipynb": ("ipynb.ipynb_codec", "load_ipynb"),
    "mtlx": ("mtlx.mtlx_codec", "load_mtlx"),
    "nrrd": ("nrrd.nrrd_codec", "load_nrrd"),
    "safetensors": ("safetensors.safetensors_codec", "load_safetensors"),
    "ubl": ("ubl.ubl_codec", "load_ubl"),
    "xliff": ("xliff.xliff_codec", "load_xliff"),
}


def _enrich_model(result_val: dict, format_id: str) -> dict:
    """Add derived properties used by expected_model_properties."""
    if not isinstance(result_val, dict):
        return result_val
    enriched = dict(result_val)
    if format_id == "safetensors":
        tensors = result_val.get("tensors", {})
        enriched["tensor_count"] = len(tensors) if isinstance(tensors, dict) else 0
        enriched["tensor_names"] = sorted(tensors) if isinstance(tensors, dict) else []
    elif format_id == "ipynb":
        cells = result_val.get("cells", [])
        enriched["cell_count"] = len(cells) if isinstance(cells, list) else 0
    elif format_id == "mtlx":
        materials = result_val.get("materials", [])
        enriched["material_count"] = len(materials) if isinstance(materials, list) else 0
    elif format_id == "nrrd":
        shape = result_val.get("array_shape", result_val.get("header", {}).get("sizes", []))
        enriched["dimension"] = len(shape) if isinstance(shape, list) else 0
    elif format_id == "ubl":
        lines = result_val.get("lines", [])
        enriched["line_count"] = len(lines) if isinstance(lines, list) else 0
    elif format_id == "xliff":
        files = result_val.get("files", [])
        enriched["unit_count"] = sum(
            len(item.get("units", item.get("trans_units", [])))
            for item in files if isinstance(item, dict)
        ) if isinstance(files, list) else 0
    return enriched


def execute_enriched_generic(core, case, pkg, format_id, module, callable_name):
    """Execute a generic loader and compare enriched model properties."""
    case_id = case["case_id"]
    sample_ref = case.get("input_ref") or case.get("sample_ref")
    _, authority_status = core.check_authority(case, True)
    common = {
        "oracle_id": pkg["oracle_id"],
        "oracle_version": pkg["oracle_version"],
        "format_id": format_id,
        "product_id": f"format-factory-{format_id}",
        "language": "python",
        "case_id": case_id,
        "profile": "PARSE_VALIDITY",
        "authority_status": authority_status,
    }
    if not sample_ref:
        return core.make_verdict(
            **common, result=core.RESULT_NOT_APPLICABLE, diagnostics=["No sample_ref"]
        )
    sample_path = core.REPO_ROOT / sample_ref
    if not sample_path.exists():
        return core.make_verdict(
            **common,
            result=core.RESULT_BLOCKED_MISSING_SAMPLE,
            diagnostics=[f"Sample not found: {sample_path}"],
        )
    input_hash = core.sha256_file(sample_path)
    try:
        sys.path.insert(0, str(core.REPO_ROOT))
        fn = getattr(importlib.import_module(f"src.python.{module}"), callable_name)
        result_val = _enrich_model(fn(str(sample_path)), format_id)
        expected = case.get("expected_model_properties", [])
        observed, deviations, depth, diagnostics = core._compare_model_properties(
            result_val, expected
        )
        return core.make_verdict(
            **common,
            result=core.RESULT_FAIL if deviations else core.RESULT_PASS,
            observed=observed,
            deviations=deviations,
            input_hash=input_hash,
            depth_level=depth,
            diagnostics=diagnostics,
        )
    except Exception as exc:
        return core.make_verdict(
            **common,
            result=core.RESULT_FAIL,
            diagnostics=[f"{type(exc).__name__}: {exc}"],
            input_hash=input_hash,
            depth_level=core.DEPTH_D0,
        )
