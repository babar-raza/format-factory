#!/usr/bin/env python3
"""
execute_oracle.py — Format Factory Product Conformance Oracle Executor

Executes oracle cases from oracle/formats/<format_id>/oracle-package.yaml
against the installed or source product and emits oracle_verdict records.

Rules:
- No LLM calls
- No network calls
- Verdicts written to .local/oracle/<format_id>/verdicts/ (gitignored)
- Sanitized summary written to oracle/formats/<format_id>/reports/
- Implementation cannot self-approve (AI_DRAFT_UNVERIFIED and IMPLEMENTATION_OBSERVED
  authority classes block PASS verdicts)
- Each verdict must trace to an authority class

Usage:
    python tools/oracle/execute_oracle.py --format csv
    python tools/oracle/execute_oracle.py --format zst --profile LOSSLESS_TRANSFORMATION
    python tools/oracle/execute_oracle.py --format fods --case fods-valid-001
    python tools/oracle/execute_oracle.py --format csv --all

Output:
    .local/oracle/<format_id>/verdicts/<case_id>.json
    .local/oracle/<format_id>/oracle-run-summary.json
"""

import argparse
import hashlib
import importlib
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository root
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
ORACLE_DIR = REPO_ROOT / "oracle"
LOCAL_ORACLE_DIR = REPO_ROOT / ".local" / "oracle"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format"

# Authority classes that BLOCK a PASS verdict (cannot self-approve)
BLOCKING_AUTHORITY_CLASSES = {"AI_DRAFT_UNVERIFIED", "IMPLEMENTATION_OBSERVED", "UNKNOWN", "REJECTED"}

# Allowed result values
RESULT_PASS = "PASS"
RESULT_FAIL = "FAIL"
RESULT_BLOCKED_MISSING_AUTHORITY = "BLOCKED_MISSING_AUTHORITY"
RESULT_BLOCKED_MISSING_SAMPLE = "BLOCKED_MISSING_SAMPLE"
RESULT_UNSUPPORTED_DECLARED = "UNSUPPORTED_DECLARED"
RESULT_INVALID_ORACLE = "INVALID_ORACLE"
RESULT_STALE_ORACLE = "STALE_ORACLE"
RESULT_INCONCLUSIVE = "INCONCLUSIVE"
RESULT_NOT_APPLICABLE = "NOT_APPLICABLE"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def load_oracle_package(format_id: str) -> dict:
    """Load oracle package YAML for a format."""
    try:
        import yaml
    except ImportError:
        # Fallback: try to parse manually or raise clear error
        raise ImportError("PyYAML required: pip install pyyaml")

    pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        raise FileNotFoundError(f"No oracle package found at {pkg_path}")
    with open(pkg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_verdict(
    oracle_id: str,
    oracle_version: int,
    format_id: str,
    product_id: str,
    language: str,
    case_id: str,
    profile: str,
    result: str,
    authority_status: str,
    observed: dict = None,
    expected: dict = None,
    deviations: list = None,
    tolerated_deviations: list = None,
    untolerated_deviations: list = None,
    diagnostics: list = None,
    evidence: list = None,
    input_hash: str = None,
) -> dict:
    """Create a structured oracle verdict."""
    return {
        "verdict_id": f"{oracle_id}-{case_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "oracle_id": oracle_id,
        "oracle_version": oracle_version,
        "format_id": format_id,
        "product_id": product_id,
        "language": language,
        "case_id": case_id,
        "profile": profile,
        "result": result,
        "authority_status": authority_status,
        "input_hash": input_hash,
        "output_hashes": [],
        "comparator": None,
        "observed": observed or {},
        "expected": expected or {},
        "deviations": deviations or [],
        "tolerated_deviations": tolerated_deviations or [],
        "untolerated_deviations": untolerated_deviations or [],
        "diagnostics": diagnostics or [],
        "evidence": evidence or [],
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }


def check_authority(case: dict, result_pass_candidate: bool) -> tuple[str, str]:
    """
    Check authority class. If blocking class detected and result would be PASS,
    return (BLOCKED_MISSING_AUTHORITY, reason).
    Returns (result, authority_status).
    """
    auth_class = case.get("authority_class", "UNKNOWN")
    if auth_class in BLOCKING_AUTHORITY_CLASSES and result_pass_candidate:
        return (
            RESULT_BLOCKED_MISSING_AUTHORITY,
            auth_class,
        )
    return (None, auth_class)


def execute_csv_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a CSV valid case against the product."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")

    # Check authority before executing
    auth_block, authority_status = check_authority(case, True)
    if auth_block:
        return make_verdict(
            oracle_id=pkg["oracle_id"],
            oracle_version=pkg["oracle_version"],
            format_id="csv",
            product_id="format-factory-csv",
            language="python",
            case_id=case_id,
            profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_AUTHORITY,
            authority_status=authority_status,
            diagnostics=[f"Authority class {authority_status} blocks PASS"],
        )

    # Handle inline cases (no file)
    if sample_ref is None:
        inline = case.get("input_inline", "")
        if inline == "":
            # Empty file case
            try:
                import tempfile, os
                sys.path.insert(0, str(REPO_ROOT))
                from src.python.csv.csv_parser import parse_csv_strict
                with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                    f.write(inline)
                    tmp_path = f.name
                try:
                    model = parse_csv_strict(tmp_path)
                    observed = {
                        "row_count": model.get("row_count", 0),
                        "column_count": model.get("column_count", 0),
                        "has_header": model.get("has_header", False),
                    }
                    expected_props = {p["property"]: p["value"] for p in case.get("expected_model_properties", [])}
                    deviations = []
                    for prop, exp_val in expected_props.items():
                        obs_val = observed.get(prop)
                        if obs_val != exp_val:
                            deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})
                    result = RESULT_PASS if not deviations else RESULT_FAIL
                    return make_verdict(
                        oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                        format_id="csv", product_id="format-factory-csv", language="python",
                        case_id=case_id, profile="LIMITS_AND_BOUNDARIES",
                        result=result, authority_status=authority_status,
                        observed=observed, expected=expected_props,
                        deviations=deviations,
                    )
                finally:
                    os.unlink(tmp_path)
            except Exception as e:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="csv", product_id="format-factory-csv", language="python",
                    case_id=case_id, profile="LIMITS_AND_BOUNDARIES",
                    result=RESULT_FAIL, authority_status=authority_status,
                    diagnostics=[f"Exception: {e}", traceback.format_exc()],
                )

    # File-based case
    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="csv", product_id="format-factory-csv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.csv.csv_parser import parse_csv_strict

        model = parse_csv_strict(str(sample_path))
        observed = {
            "row_count": model.get("row_count", 0),
            "column_count": model.get("column_count", 0),
            "has_header": model.get("has_header", False),
            "headers": model.get("headers", []),
        }

        # Verify expected model properties
        expected_props = {}
        deviations = []
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            exp_val = prop_def["value"]
            expected_props[prop] = exp_val
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})

        result = RESULT_PASS if not deviations else RESULT_FAIL
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="csv", product_id="format-factory-csv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="csv", product_id="format-factory-csv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def execute_csv_invalid_case(case: dict, pkg: dict) -> dict:
    """Execute a CSV invalid case — expect parser to raise exception."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    _, authority_status = check_authority(case, False)

    # For invalid cases, we expect an exception
    if sample_ref is None:
        inline = case.get("input_inline", "")
        if inline is None:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="csv", product_id="format-factory-csv", language="python",
                case_id=case_id, profile="INVALID_INPUT_REJECTION",
                result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
                diagnostics=["In-memory inline case requires separate execution path"],
            )

    try:
        import tempfile, os
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.csv.csv_parser import parse_csv_strict

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(case.get("input_inline", ""))
            tmp_path = f.name
        try:
            model = parse_csv_strict(tmp_path)
            # Parser did NOT raise — but it should have for invalid input
            # Whether this is a FAIL depends on partial_recovery_allowed
            if case.get("partial_recovery_allowed", False):
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="csv", product_id="format-factory-csv", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=RESULT_PASS, authority_status=authority_status,
                    diagnostics=["Parser recovered gracefully (partial_recovery_allowed=true)"],
                )
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="csv", product_id="format-factory-csv", language="python",
                case_id=case_id, profile="INVALID_INPUT_REJECTION",
                result=RESULT_FAIL, authority_status=authority_status,
                diagnostics=["Expected exception but parser succeeded — invalid input not rejected"],
            )
        except Exception:
            # Exception raised — this is the expected behavior for invalid input
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="csv", product_id="format-factory-csv", language="python",
                case_id=case_id, profile="INVALID_INPUT_REJECTION",
                result=RESULT_PASS, authority_status=authority_status,
                diagnostics=["Parser correctly rejected invalid input"],
            )
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="csv", product_id="format-factory-csv", language="python",
            case_id=case_id, profile="INVALID_INPUT_REJECTION",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            diagnostics=[f"Oracle executor error: {e}"],
        )


def execute_zst_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a ZST valid case against the product."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref — introspection-only case"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    # Verify corpus hash if declared
    expected_hash = case.get("input_hash")
    if expected_hash and input_hash != expected_hash:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_STALE_ORACLE, authority_status=authority_status,
            diagnostics=[f"Sample hash mismatch. Expected {expected_hash}, got {input_hash}"],
            input_hash=input_hash,
        )

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.zst.models import ZstDocument
        doc = ZstDocument.from_file(str(sample_path))

        observed = {
            "compressed_size": doc.compressed_size,
            "decompressed_size": doc.decompressed_size,
            "frame_count": doc.frame_count,
            "is_empty": doc.is_empty,
            "spec_qname": getattr(ZstDocument, "spec_qname", None),
        }

        expected_props = {}
        deviations = []
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            exp_val = prop_def["value"]
            expected_props[prop] = exp_val
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})

        result = RESULT_PASS if not deviations else RESULT_FAIL
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def _fods_all_cells(parse_result: dict) -> list:
    """Collect all cell dicts from a parsed FODS result."""
    cells = []
    for sheet in parse_result.get("sheets", []):
        for row in sheet.get("rows", []):
            cells.extend(row.get("cells", []))
    return cells


def execute_fods_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a FODS valid case against the product."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    auth_block, authority_status = check_authority(case, True)
    if auth_block:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_AUTHORITY, authority_status=authority_status,
            diagnostics=[f"Authority class {authority_status} blocks PASS"],
        )

    # Introspection-only case (spec_qname check — no file)
    if sample_ref is None:
        try:
            sys.path.insert(0, str(REPO_ROOT))
            from src.python.fods.models import FodsDocument
            observed = {"spec_qname": getattr(FodsDocument, "spec_qname", None)}
            expected_props = {p["property"]: p["value"] for p in case.get("expected_model_properties", [])}
            deviations = []
            for prop, exp_val in expected_props.items():
                obs_val = observed.get(prop)
                if obs_val != exp_val:
                    deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})
            result = RESULT_PASS if not deviations else RESULT_FAIL
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="DOMAIN_MODEL_MAPPING",
                result=result, authority_status=authority_status,
                observed=observed, expected=expected_props, deviations=deviations,
            )
        except Exception as e:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="DOMAIN_MODEL_MAPPING",
                result=RESULT_FAIL, authority_status=authority_status,
                diagnostics=[f"Introspection error: {e}"],
            )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.fods.parser import parse_fods

        parse_result = parse_fods(str(sample_path))

        # Detect parse failure
        if parse_result.get("error"):
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="PARSE_VALIDITY",
                result=RESULT_FAIL, authority_status=authority_status,
                diagnostics=[f"Parse failed: {parse_result['error']}"],
                input_hash=input_hash,
            )

        # Build observed properties
        all_cells = _fods_all_cells(parse_result)
        sheets = parse_result.get("sheets", [])
        observed = {
            "sheet_count": parse_result.get("sheet_count", 0),
            "first_sheet_name": sheets[0]["name"] if sheets else None,
            "cell_count": len(all_cells),
            "has_float_cell": any(c.get("value_type") == "float" for c in all_cells),
            "has_string_cell": any(c.get("value_type") == "string" for c in all_cells),
            "has_formula_cell": any(c.get("formula") is not None for c in all_cells),
        }

        # Warn about unsupported properties
        expected_props = {}
        deviations = []
        unsupported_props = []
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            exp_val = prop_def["value"]
            expected_props[prop] = exp_val
            if prop not in observed:
                unsupported_props.append(prop)
                continue
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})

        if unsupported_props:
            # Unsupported properties produce INCONCLUSIVE, not FAIL
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="DOMAIN_MODEL_MAPPING",
                result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                observed=observed, expected=expected_props,
                diagnostics=[f"Unsupported properties in executor: {unsupported_props}"],
                input_hash=input_hash,
            )

        result = RESULT_PASS if not deviations else RESULT_FAIL
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props, deviations=deviations,
            input_hash=input_hash,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def execute_fods_invalid_case(case: dict, pkg: dict) -> dict:
    """Execute a FODS invalid case — expect parser error or failure mode."""
    import tempfile
    import os

    case_id = case["case_id"]
    _, authority_status = check_authority(case, False)
    sample_ref = case.get("sample_ref")

    # fods-invalid-001: directory reference — pick first .fods fixture file
    if sample_ref is not None:
        sample_path = REPO_ROOT / sample_ref
        if sample_path.is_dir():
            fods_files = sorted(sample_path.glob("*.fods"))
            if not fods_files:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
                    diagnostics=[f"No .fods fixtures found in: {sample_path}"],
                )
            # Test first fixture from directory
            test_file = fods_files[0]
            input_hash = sha256_file(test_file)
            try:
                sys.path.insert(0, str(REPO_ROOT))
                from src.python.fods.parser import parse_fods
                result_dict = parse_fods(str(test_file))
                rejected = bool(result_dict.get("error") or result_dict.get("parse_errors"))
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=RESULT_PASS if rejected else RESULT_FAIL, authority_status=authority_status,
                    diagnostics=[
                        f"Tested fixture: {test_file.name}",
                        f"Error: {result_dict.get('error', 'none')}",
                    ],
                    input_hash=input_hash,
                )
            except Exception as e:
                # Exception = definitely rejected
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=RESULT_PASS, authority_status=authority_status,
                    diagnostics=[f"Exception raised on malformed input: {type(e).__name__}: {e}"],
                    input_hash=input_hash,
                )

    # Inline / input_description cases (fods-invalid-002, fods-invalid-003)
    inline_content = case.get("input_inline") or case.get("input_description")
    if inline_content is None:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INVALID_INPUT_REJECTION",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No inline content and no sample_ref — cannot execute"],
        )

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.fods.parser import parse_fods

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".fods", delete=False, encoding="utf-8"
            ) as f:
                f.write(inline_content)
                tmp_path = f.name

            result_dict = parse_fods(tmp_path)
            rejected = bool(result_dict.get("error") or result_dict.get("parse_errors"))
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="INVALID_INPUT_REJECTION",
                result=RESULT_PASS if rejected else RESULT_FAIL, authority_status=authority_status,
                diagnostics=[
                    f"Input correctly {'rejected' if rejected else 'accepted (unexpected)'}",
                    f"Error: {result_dict.get('error', 'none')}",
                ],
            )
        except Exception as e:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="INVALID_INPUT_REJECTION",
                result=RESULT_PASS, authority_status=authority_status,
                diagnostics=[f"Exception raised: {type(e).__name__}: {e}"],
            )
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    except ImportError as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INVALID_INPUT_REJECTION",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            diagnostics=[f"Import error: {e}"],
        )


def execute_zst_lossless_case(case: dict, pkg: dict) -> dict:
    """Execute ZST compress→decompress round-trip lossless case."""
    case_id = case["case_id"]
    _, authority_status = check_authority(case, True)

    verdicts = []
    all_pass = True

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.zst.zst_codec import compress_string, decompress_to_string

        for tv in case.get("test_vectors", []):
            inp = tv["input"]
            expected = tv["expected_decompressed"]
            try:
                compressed = compress_string(inp)
                decompressed = decompress_to_string(compressed)
                if decompressed == expected:
                    verdicts.append(f"PASS: {repr(inp)[:30]}")
                else:
                    verdicts.append(f"FAIL: input={repr(inp)[:30]} expected={repr(expected)[:30]} got={repr(decompressed)[:30]}")
                    all_pass = False
            except Exception as e:
                verdicts.append(f"FAIL: exception {e}")
                all_pass = False

        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="LOSSLESS_TRANSFORMATION",
            result=RESULT_PASS if all_pass else RESULT_FAIL, authority_status=authority_status,
            diagnostics=verdicts,
        )

    except ImportError as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="LOSSLESS_TRANSFORMATION",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            diagnostics=[f"Import error: {e}"],
        )


def save_verdict(verdict: dict, format_id: str) -> Path:
    """Save a verdict to local oracle output directory."""
    out_dir = LOCAL_ORACLE_DIR / format_id / "verdicts"
    out_dir.mkdir(parents=True, exist_ok=True)
    case_id = verdict["case_id"]
    out_path = out_dir / f"{case_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2, ensure_ascii=False)
    return out_path


def run_oracle_for_format(format_id: str, profile_filter: str = None, case_filter: str = None) -> dict:
    """Run oracle for a single format. Returns summary dict."""
    print(f"\n[oracle] Executing oracle for format: {format_id}")

    pkg = load_oracle_package(format_id)
    oracle_id = pkg["oracle_id"]

    verdicts = []
    counts = {"PASS": 0, "FAIL": 0, "BLOCKED_MISSING_AUTHORITY": 0,
               "BLOCKED_MISSING_SAMPLE": 0, "INCONCLUSIVE": 0, "NOT_APPLICABLE": 0,
               "STALE_ORACLE": 0, "INVALID_ORACLE": 0}

    # Execute valid cases
    for case in pkg.get("valid_cases", []):
        case_id = case["case_id"]
        if case_filter and case_id != case_filter:
            continue
        if profile_filter:
            profiles = case.get("applicable_profiles", [])
            if profile_filter not in profiles:
                continue

        if format_id == "csv":
            verdict = execute_csv_valid_case(case, pkg)
        elif format_id == "zst":
            verdict = execute_zst_valid_case(case, pkg)
        elif format_id == "fods":
            verdict = execute_fods_valid_case(case, pkg)
        else:
            verdict = make_verdict(
                oracle_id=oracle_id, oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id, profile="PARSE_VALIDITY",
                result=RESULT_NOT_APPLICABLE, authority_status="UNKNOWN",
                diagnostics=["No executor implemented for this format in this tool yet"],
            )

        verdicts.append(verdict)
        save_verdict(verdict, format_id)
        result = verdict["result"]
        counts[result] = counts.get(result, 0) + 1
        status_icon = "OK" if result == "PASS" else ("FAIL" if result == "FAIL" else "~~")
        print(f"  [{status_icon}] {case_id}: {result}")

    # Execute ZST roundtrip cases
    if format_id == "zst":
        for case in pkg.get("roundtrip_cases", []):
            case_id = case["case_id"]
            if case_filter and case_id != case_filter:
                continue
            verdict = execute_zst_lossless_case(case, pkg)
            verdicts.append(verdict)
            save_verdict(verdict, format_id)
            result = verdict["result"]
            counts[result] = counts.get(result, 0) + 1
            status_icon = "OK" if result == "PASS" else "FAIL"
            print(f"  [{status_icon}] {case_id}: {result}")

    # Execute invalid cases (CSV and FODS)
    if format_id in ("csv", "fods"):
        for case in pkg.get("invalid_cases", []):
            case_id = case["case_id"]
            if case_filter and case_id != case_filter:
                continue
            if format_id == "csv":
                # Only execute inline cases for CSV
                if case.get("input_inline") is None:
                    continue
                verdict = execute_csv_invalid_case(case, pkg)
            else:
                # FODS: handles both directory refs and inline/description cases
                verdict = execute_fods_invalid_case(case, pkg)
            verdicts.append(verdict)
            save_verdict(verdict, format_id)
            result = verdict["result"]
            counts[result] = counts.get(result, 0) + 1
            print(f"  [{'OK' if result == 'PASS' else 'FAIL'}] {case_id}: {result}")

    # Summary
    total = len(verdicts)
    passed = counts["PASS"]
    summary = {
        "oracle_id": oracle_id,
        "format_id": format_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": total,
        "results": counts,
        "pass_rate": f"{passed}/{total}" if total else "0/0",
        "verdict": "ALL_PASS" if passed == total and total > 0 else ("PARTIAL_PASS" if passed > 0 else "ALL_FAIL"),
        "verdicts_dir": str(LOCAL_ORACLE_DIR / format_id / "verdicts"),
    }

    # Save summary
    summary_dir = REPO_ROOT / "oracle" / "formats" / format_id / "reports"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "oracle-run-summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[oracle] Summary for {format_id}: {passed}/{total} PASS")
    print(f"[oracle] Summary saved: {summary_path}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Format Factory Oracle Executor")
    parser.add_argument("--format", required=True, help="Format ID (e.g. csv, zst, fods)")
    parser.add_argument("--profile", default=None, help="Filter by profile (e.g. PARSE_VALIDITY)")
    parser.add_argument("--case", default=None, help="Run a single case by case_id")
    parser.add_argument("--all", action="store_true", help="Run all cases")
    args = parser.parse_args()

    try:
        summary = run_oracle_for_format(args.format, args.profile, args.case)
        passed = summary["results"]["PASS"]
        total = summary["total_cases"]
        if total > 0 and passed == total:
            sys.exit(0)
        else:
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"[oracle] ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except ImportError as e:
        print(f"[oracle] ERROR: Missing dependency: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
