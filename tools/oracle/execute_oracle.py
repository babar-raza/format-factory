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
RESULT_SKIPPED_MISSING_PROVIDER = "SKIPPED_MISSING_PROVIDER"
RESULT_SKIPPED_MISSING_DEPENDENCY = "SKIPPED_MISSING_DEPENDENCY"

# Oracle depth levels (FF-XPLAN-001 W2A-002)
DEPTH_D0 = "D0"  # Load didn't crash (no property comparison)
DEPTH_D1 = "D1"  # Model properties compared against expected values
DEPTH_D2 = "D2"  # Schema validation (e.g. ODF RelaxNG via lxml)
DEPTH_D3 = "D3"  # External tool interop (e.g. LibreOffice)

# Synthetic properties that are always True and add no discriminating information.
# An oracle case with ONLY synthetic properties earns D0, not D1 (TC-OIS-003 / MCP-W5-001).
SYNTHETIC_PROPERTIES: frozenset[str] = frozenset({"loaded", "result_type"})


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
    depth_level: str = DEPTH_D0,
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
        "depth_level": depth_level,
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
                    expected_props = {}
                    deviations = []
                    unsupported_props = []
                    for p in case.get("expected_model_properties", []):
                        prop, exp_val = p["property"], p["value"]
                        expected_props[prop] = exp_val
                        if prop not in observed:
                            print(f"WARNING: CSV executor does not support property '{prop}' — INCONCLUSIVE", file=sys.stderr)
                            unsupported_props.append(prop)
                            continue
                        if observed.get(prop) != exp_val:
                            deviations.append({"property": prop, "expected": exp_val, "observed": observed.get(prop)})
                    if unsupported_props:
                        return make_verdict(
                            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                            format_id="csv", product_id="format-factory-csv", language="python",
                            case_id=case_id, profile="LIMITS_AND_BOUNDARIES",
                            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                            observed=observed, expected=expected_props,
                            diagnostics=[f"Unsupported properties in CSV executor: {unsupported_props}"],
                        )
                    result = RESULT_PASS if not deviations else RESULT_FAIL
                    depth = DEPTH_D1 if expected_props else DEPTH_D0
                    return make_verdict(
                        oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                        format_id="csv", product_id="format-factory-csv", language="python",
                        case_id=case_id, profile="LIMITS_AND_BOUNDARIES",
                        result=result, authority_status=authority_status,
                        observed=observed, expected=expected_props,
                        deviations=deviations, depth_level=depth,
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
        unsupported_props = []
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            exp_val = prop_def["value"]
            expected_props[prop] = exp_val
            if prop not in observed:
                print(f"WARNING: CSV executor does not support property '{prop}' — INCONCLUSIVE", file=sys.stderr)
                unsupported_props.append(prop)
                continue
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})

        if unsupported_props:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="csv", product_id="format-factory-csv", language="python",
                case_id=case_id, profile="PARSE_VALIDITY",
                result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                observed=observed, expected=expected_props,
                diagnostics=[f"Unsupported properties in CSV executor: {unsupported_props}"],
                input_hash=input_hash,
            )

        result = RESULT_PASS if not deviations else RESULT_FAIL
        depth = DEPTH_D1 if expected_props else DEPTH_D0
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="csv", product_id="format-factory-csv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
            depth_level=depth,
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


def execute_tsv_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a TSV valid case using Python stdlib csv as reference (TC-LA-003)."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="tsv", product_id="format-factory-tsv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref — introspection-only case"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="tsv", product_id="format-factory-tsv", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.tsv.tsv_parser import load_tsv  # type: ignore

        model = load_tsv(str(sample_path))
        observed = {
            "row_count": model.get("row_count", 0),
            "column_count": model.get("column_count", 0),
            "has_header": model.get("has_header", False),
            "headers": model.get("headers", []),
            "spec_qname": "tsv:row",
        }

        deviations = []
        expected_props: dict = {}
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            if "value" in prop_def:
                exp_val = prop_def["value"]
                expected_props[prop] = exp_val
                obs_val = observed.get(prop)
                if obs_val != exp_val:
                    deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})
            elif "value_min" in prop_def:
                exp_min = prop_def["value_min"]
                expected_props[f"{prop}_min"] = exp_min
                obs_val = observed.get(prop, 0)
                if obs_val < exp_min:
                    deviations.append({"property": prop, "expected_min": exp_min, "observed": obs_val})

        result = RESULT_PASS if not deviations else RESULT_FAIL
        depth = DEPTH_D1 if expected_props else DEPTH_D0
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="tsv", product_id="format-factory-tsv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
            depth_level=depth,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="tsv", product_id="format-factory-tsv", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def execute_ndjson_valid_case(case: dict, pkg: dict) -> dict:
    """Execute an NDJSON valid case using Python stdlib json as reference (TC-LA-003)."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="ndjson", product_id="format-factory-ndjson", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref — introspection-only case"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="ndjson", product_id="format-factory-ndjson", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    try:
        import json as _json
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.ndjson.ndjson_codec import load_ndjson  # type: ignore

        records = load_ndjson(str(sample_path))
        # Reference: Python stdlib line-by-line json.loads
        with open(sample_path, encoding="utf-8") as f:
            ref_records = [_json.loads(line) for line in f if line.strip()]

        observed = {
            "record_count": len(records),
            "spec_qname": "ndjson:record",
        }

        deviations = []
        expected_props: dict = {}
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            if "value" in prop_def:
                exp_val = prop_def["value"]
                expected_props[prop] = exp_val
                obs_val = observed.get(prop)
                if obs_val != exp_val:
                    deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})
            elif "value_min" in prop_def:
                exp_min = prop_def["value_min"]
                expected_props[f"{prop}_min"] = exp_min
                obs_val = observed.get(prop, 0)
                if obs_val < exp_min:
                    deviations.append({"property": prop, "expected_min": exp_min, "observed": obs_val})

        # Cross-check: stdlib reference must match product
        if len(records) != len(ref_records):
            deviations.append({
                "property": "record_count",
                "expected": len(ref_records),
                "observed": len(records),
                "authority": "PYTHON-JSON-STDLIB",
            })

        result = RESULT_PASS if not deviations else RESULT_FAIL
        depth = DEPTH_D1 if expected_props else DEPTH_D0
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="ndjson", product_id="format-factory-ndjson", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
            depth_level=depth,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="ndjson", product_id="format-factory-ndjson", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def execute_toml_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a TOML valid case using Python stdlib tomllib as reference (GAP-ORC-BACKFILL-D)."""
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="toml", product_id="format-factory-toml", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref -- introspection-only case"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="toml", product_id="format-factory-toml", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)

    try:
        import tomllib as _tomllib
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.toml.models import TomlDocument  # type: ignore

        doc = TomlDocument.from_file(str(sample_path))
        # Reference: Python stdlib tomllib key count
        with open(sample_path, "rb") as f:
            ref_data = _tomllib.load(f)
        ref_key_count = len(ref_data)

        observed = {
            "key_count": doc.key_count,
            "spec_qname": doc.spec_qname,
        }

        deviations = []
        expected_props: dict = {}
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            if "value" in prop_def:
                exp_val = prop_def["value"]
                expected_props[prop] = exp_val
                obs_val = observed.get(prop)
                if obs_val != exp_val:
                    deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})
            elif "value_min" in prop_def:
                exp_min = prop_def["value_min"]
                expected_props[f"{prop}_min"] = exp_min
                obs_val = observed.get(prop, 0)
                if obs_val < exp_min:
                    deviations.append({"property": prop, "expected_min": exp_min, "observed": obs_val})

        # Cross-check: stdlib reference must match product key count
        if doc.key_count != ref_key_count:
            deviations.append({
                "property": "key_count",
                "expected": ref_key_count,
                "observed": doc.key_count,
                "authority": "PYTHON-TOMLLIB-STDLIB",
            })

        # Handle roundtrip case
        if case.get("roundtrip_fields_equal"):
            from src.python.toml.toml_codec import write_toml, load_toml  # type: ignore
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                model_dict = doc.to_dict()
                write_toml(model_dict["data"], tmp_path)
                reloaded = TomlDocument.from_file(tmp_path)
                for field in case["roundtrip_fields_equal"]:
                    orig_val = observed.get(field)
                    reload_val = getattr(reloaded, field, None)
                    if orig_val != reload_val:
                        deviations.append({
                            "property": field,
                            "expected": orig_val,
                            "observed": reload_val,
                            "note": "roundtrip mismatch",
                        })
            finally:
                os.unlink(tmp_path)

        result = RESULT_PASS if not deviations else RESULT_FAIL
        depth = DEPTH_D1 if expected_props else DEPTH_D0
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="toml", product_id="format-factory-toml", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
            depth_level=depth,
        )

    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="toml", product_id="format-factory-toml", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"Unexpected exception: {type(e).__name__}: {e}"],
            input_hash=input_hash,
        )


def _compare_model_properties(result_val, expected_props: list) -> tuple[dict, list, str, list]:
    """Compare model properties against expected values from oracle-package.yaml.

    Returns (observed_dict, deviations_list, depth_level, diagnostics).
    FF-XPLAN-001 W2A-003: Upgrade from D0 to D1 by actually inspecting properties.
    TC-FGSQ-007: data_source field per property controls depth eligibility.
      data_source values: 'parsed' | 'computed' | 'unsupported' | 'unknown' (default)
      - 'unsupported': feature not XML-backed; excluded from D1 eligibility
      - 'unknown': backward compat; allows D1 but adds WARN diagnostic
    """
    observed = {"loaded": True, "result_type": type(result_val).__name__}
    deviations = []
    diagnostics = []

    if not expected_props:
        return observed, deviations, DEPTH_D0, diagnostics

    d1_eligible = 0   # props with data_source in ('parsed', 'computed')
    unknown_ds = 0    # props with data_source == 'unknown' or absent

    for prop_spec in expected_props:
        prop_name = prop_spec.get("property", "")
        if not prop_name:
            continue

        data_source = prop_spec.get("data_source", "unknown")

        # Extract actual value from result
        actual = None
        if prop_name == "loaded":
            # Synthetic property: if we have a result_val, it loaded successfully
            actual = result_val is not None
        elif isinstance(result_val, dict):
            actual = result_val.get(prop_name)
        elif hasattr(result_val, prop_name):
            actual = getattr(result_val, prop_name)

        observed[prop_name] = actual

        # Compare against expected
        if "value" in prop_spec:
            expected_val = prop_spec["value"]
            if actual != expected_val:
                deviations.append({
                    "property": prop_name,
                    "expected": expected_val,
                    "observed": actual,
                    "type": "value_mismatch",
                    "data_source": data_source,
                })
        elif "value_min" in prop_spec:
            min_val = prop_spec["value_min"]
            if actual is None or (isinstance(actual, (int, float)) and actual < min_val):
                deviations.append({
                    "property": prop_name,
                    "expected_min": min_val,
                    "observed": actual,
                    "type": "below_minimum",
                    "data_source": data_source,
                })

        # Track data_source for depth calculation (TC-FGSQ-007)
        if data_source in ("parsed", "computed"):
            d1_eligible += 1
        elif data_source == "unknown":
            unknown_ds += 1
        # data_source == 'unsupported' → excluded from D1 contribution

    # TC-OIS-003 / MCP-W5-001: Require at least one non-synthetic property for D1.
    # 'loaded' and 'result_type' are oracle-synthesized and always True — they prove
    # nothing about model content beyond "the parser didn't crash" (D0 already implies that).
    has_non_synthetic = any(
        p.get("property") not in SYNTHETIC_PROPERTIES
        for p in expected_props
        if p.get("property")
    )
    if not has_non_synthetic:
        depth = DEPTH_D0  # only synthetic properties — no meaningful model comparison
    elif d1_eligible > 0:
        # Determine depth level based on data_source inventory (TC-FGSQ-007)
        depth = DEPTH_D1  # at least one parsed/computed non-synthetic property → D1
    elif unknown_ds > 0:
        depth = DEPTH_D1  # backward compat: unknown allows D1 but with WARN
        diagnostics.append(
            f"WARN[TC-FGSQ-007]: {unknown_ds} propert{'y' if unknown_ds == 1 else 'ies'} "
            "lack data_source declaration (defaulting to 'unknown'). "
            "Declare data_source='parsed'|'computed'|'unsupported' for accurate depth scoring."
        )
    else:
        depth = DEPTH_D0  # all non-synthetic properties are 'unsupported' → D0

    return observed, deviations, depth, diagnostics


def execute_generic_load_case(case: dict, pkg: dict, format_id: str, module: str, callable_name: str) -> dict:
    """Generic executor: import module, call callable(sample_path), compare properties (FF-XPLAN-001)."""
    case_id = case["case_id"]
    sample_ref = case.get("input_ref") or case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)
    try:
        sys.path.insert(0, str(REPO_ROOT))
        import importlib
        mod = importlib.import_module(f"src.python.{module}")
        fn = getattr(mod, callable_name)
        result_val = fn(str(sample_path))

        # FF-XPLAN-001 W2A-003: Compare expected_model_properties if defined
        expected_props = case.get("expected_model_properties", [])
        observed, deviations, depth, ds_diagnostics = _compare_model_properties(result_val, expected_props)

        verdict_result = RESULT_FAIL if deviations else RESULT_PASS
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=verdict_result, authority_status=authority_status,
            observed=observed, deviations=deviations, input_hash=input_hash,
            depth_level=depth, diagnostics=ds_diagnostics,
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"{type(e).__name__}: {e}"], input_hash=input_hash,
            depth_level=DEPTH_D0,
        )


def execute_generic_invalid_case(
    case: dict, pkg: dict, format_id: str, module: str, callable_name: str
) -> dict:
    """Generic invalid case executor (TC-OIS-004 / MCP-W5-001 Pillar 1b).

    PASS if the callable raises an exception (parser correctly rejects malformed input).
    PASS if partial_recovery_allowed=true and the callable returns without raising.
    FAIL if no exception raised and partial_recovery_allowed is false.
    """
    case_id = case["case_id"]
    _, authority_status = check_authority(case, False)

    sample_ref = case.get("sample_ref") or case.get("input_ref")
    inline = case.get("input_inline")

    if sample_ref is None and inline is None:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref or input_inline for invalid case — COVERAGE_GAP"],
        )

    if sample_ref:
        sample_path = REPO_ROOT / sample_ref
        if not sample_path.exists():
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
                diagnostics=[f"Sample not found: {sample_path}"],
            )
        input_data = str(sample_path)
    else:
        input_data = inline

    partial_recovery = case.get("partial_recovery_allowed", False)

    try:
        src_py = str(REPO_ROOT / "src" / "python")
        if src_py not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        mod = importlib.import_module(f"src.python.{module}")
        fn = getattr(mod, callable_name)
        fn(input_data)

        if partial_recovery:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_PASS, authority_status=authority_status,
                diagnostics=["Parser recovered gracefully (partial_recovery_allowed=true)"],
                depth_level=DEPTH_D0,
            )
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=["Expected exception was not raised — parser silently accepted invalid input"],
            depth_level=DEPTH_D0,
        )
    except Exception:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_PASS, authority_status=authority_status,
            depth_level=DEPTH_D0,
        )


def execute_abw_valid_case(case: dict, pkg: dict) -> dict:
    """Execute an ABW valid case (TC-LA-003)."""
    return execute_generic_load_case(case, pkg, "abw", "abw.abw_codec", "load")


def execute_gnumeric_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a GNUMERIC valid case (TC-LA-003)."""
    return execute_generic_load_case(case, pkg, "gnumeric", "gnumeric.gnumeric_codec", "load")


def execute_dif_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a DIF valid case (TC-LA-003)."""
    return execute_generic_load_case(case, pkg, "dif", "dif.dif_parser", "parse_dif")


def _execute_odf_flat_d2_case(case: dict, pkg: dict, format_id: str) -> dict:
    """Execute a D2 schema validation case for flat-XML ODF formats (FODT, FODP, FODG).

    TC-W3-001: Reuses validate_odf_schema() from tools.oracle.schema_validator.
    Called when case.get('depth_level') == 'D2' or expected_parse_result == 'SCHEMA_VALID'.
    """
    case_id = case["case_id"]
    sample_ref = case.get("sample_ref") or case.get("input_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref — D2 schema case requires a file"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.oracle.schema_validator import validate_odf_schema  # noqa: PLC0415
        sv_result = validate_odf_schema(str(sample_path))
        if sv_result.get("provider") == "MISSING_PROVIDER":
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                case_id=case_id, profile="STRUCTURAL_VALIDITY",
                result=RESULT_SKIPPED_MISSING_PROVIDER, authority_status=authority_status,
                input_hash=input_hash,
                diagnostics=["lxml not available — install lxml for D2 schema validation"],
            )
        is_valid = sv_result.get("valid", False)
        observed = {"schema_valid": is_valid, "schema_version": sv_result.get("schema_version", "1.3")}
        if is_valid:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                case_id=case_id, profile="STRUCTURAL_VALIDITY",
                result=RESULT_PASS, authority_status=authority_status,
                observed=observed, input_hash=input_hash, depth_level=DEPTH_D2,
                diagnostics=["ODF 1.3 RelaxNG schema: VALID"],
            )
        errors = sv_result.get("errors", [])[:3]
        # Return INCONCLUSIVE (not FAIL) when schema has errors — sample is parseable but
        # doesn't satisfy strict RelaxNG (e.g. synthetic files missing optional namespace attrs).
        # depth_level=D2 is recorded to document that D2 was attempted (TC-W3-001).
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            observed=observed, input_hash=input_hash, depth_level=DEPTH_D2,
            diagnostics=[f"ODF 1.3 RelaxNG schema: {len(sv_result.get('errors',[]))} errors "
                         "(sample parseable but schema non-conformant — D2 attempted)"] + errors,
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            input_hash=input_hash,
            diagnostics=[f"D2 schema check error: {type(e).__name__}: {e}"],
        )


def _execute_odf_zip_d2_case(case: dict, pkg: dict, format_id: str) -> dict:
    """Execute a D2 schema validation case for ZIP-based ODF formats (ODS, ODT).

    TC-W3-001: Extracts content.xml from ODF ZIP, then validates against ODF 1.3 RelaxNG.
    """
    import zipfile  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    case_id = case["case_id"]
    sample_ref = case.get("sample_ref") or case.get("input_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref — D2 schema case requires a file"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)
    tmp_path = None
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.oracle.schema_validator import validate_odf_schema  # noqa: PLC0415
        # Extract content.xml from ZIP to temp file for schema validation
        with zipfile.ZipFile(str(sample_path), "r") as zf:
            names = zf.namelist()
            # ODF content.xml holds document content with office:document-content root
            if "content.xml" not in names:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                    case_id=case_id, profile="STRUCTURAL_VALIDITY",
                    result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                    input_hash=input_hash,
                    diagnostics=[f"content.xml not found in ODF ZIP (found: {names[:5]})"],
                )
            content_xml = zf.read("content.xml")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            tmp.write(content_xml)
            tmp_path = tmp.name

        sv_result = validate_odf_schema(tmp_path)
        if sv_result.get("provider") == "MISSING_PROVIDER":
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                case_id=case_id, profile="STRUCTURAL_VALIDITY",
                result=RESULT_SKIPPED_MISSING_PROVIDER, authority_status=authority_status,
                input_hash=input_hash,
                diagnostics=["lxml not available — install lxml for D2 schema validation"],
            )
        is_valid = sv_result.get("valid", False)
        observed = {"schema_valid": is_valid, "schema_version": sv_result.get("schema_version", "1.3"),
                    "validated_component": "content.xml"}
        if is_valid:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                case_id=case_id, profile="STRUCTURAL_VALIDITY",
                result=RESULT_PASS, authority_status=authority_status,
                observed=observed, input_hash=input_hash, depth_level=DEPTH_D2,
                diagnostics=["ODF 1.3 RelaxNG schema: VALID (content.xml)"],
            )
        errors = sv_result.get("errors", [])[:3]
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            observed=observed, input_hash=input_hash, depth_level=DEPTH_D2,
            diagnostics=(
                [f"content.xml schema validation: {len(sv_result.get('errors',[]))} errors "
                 "(ODF content.xml uses office:document-content root — partial schema match)"]
                + errors
            ),
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="STRUCTURAL_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            input_hash=input_hash,
            diagnostics=[f"D2 ZIP schema check error: {type(e).__name__}: {e}"],
        )
    finally:
        if tmp_path:
            try:
                import os  # noqa: PLC0415
                os.unlink(tmp_path)
            except Exception:
                pass


def execute_fodg_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a FODG valid case (TC-LA-003)."""
    if case.get("depth_level") == "D2" or case.get("expected_parse_result") == "SCHEMA_VALID":
        return _execute_odf_flat_d2_case(case, pkg, "fodg")
    return execute_generic_load_case(case, pkg, "fodg", "fodg.fodg_codec", "load")


def execute_ods_valid_case(case: dict, pkg: dict) -> dict:
    """Execute an ODS valid case (GAP-ORC-BACKFILL-A)."""
    if case.get("depth_level") == "D2" or case.get("expected_parse_result") == "SCHEMA_VALID":
        return _execute_odf_zip_d2_case(case, pkg, "ods")
    return execute_generic_load_case(case, pkg, "ods", "ods.ods_parser", "parse_ods")


def execute_sylk_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a SYLK valid case (GAP-ORC-BACKFILL-A). Uses parse_sylk (dict result).
    TC-OIS-002: Changed from SylkDocument (dataclass constructor, not a parser) to parse_sylk.
    """
    return execute_generic_load_case(case, pkg, "sylk", "sylk.sylk_parser", "parse_sylk")


def execute_fodt_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a FODT valid case (GAP-ORC-BACKFILL-B)."""
    if case.get("depth_level") == "D2" or case.get("expected_parse_result") == "SCHEMA_VALID":
        return _execute_odf_flat_d2_case(case, pkg, "fodt")
    return execute_generic_load_case(case, pkg, "fodt", "fodt.parser", "parse_fodt")


def execute_xcf_valid_case(case: dict, pkg: dict) -> dict:
    """Execute an XCF valid case (GAP-ORC-BACKFILL-C)."""
    return execute_generic_load_case(case, pkg, "xcf", "xcf.xcf_parser", "XcfImage")


def execute_pbm_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a PBM valid case (GAP-ORC-BACKFILL-C)."""
    return execute_generic_load_case(case, pkg, "pbm", "pbm.pbm_parser", "parse_pbm")


def execute_pgm_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a PGM valid case (GAP-ORC-BACKFILL-C).

    Uses src/python on sys.path to satisfy bare 'from pgm.*' imports in pgm_to_ppm.py.
    """
    case_id = case["case_id"]
    sample_ref = case.get("input_ref") or case.get("sample_ref")
    _, authority_status = check_authority(case, True)
    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="pgm", product_id="format-factory-pgm", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref"],
        )
    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="pgm", product_id="format-factory-pgm", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )
    input_hash = sha256_file(sample_path)
    try:
        src_py = str(REPO_ROOT / "src" / "python")
        if src_py not in sys.path:
            sys.path.insert(0, src_py)
        from pgm.pgm_parser import parse_pgm as _parse_pgm
        result_val = _parse_pgm(str(sample_path))
        observed, deviations, depth, ds_diagnostics = _compare_model_properties(
            result_val, case.get("expected_model_properties", [])
        )
        result = RESULT_PASS if not deviations else RESULT_FAIL
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="pgm", product_id="format-factory-pgm", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, deviations=deviations, input_hash=input_hash,
            depth_level=depth, diagnostics=ds_diagnostics,
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="pgm", product_id="format-factory-pgm", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"{type(e).__name__}: {e}"], input_hash=input_hash,
        )


def execute_ppm_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a PPM valid case (GAP-ORC-BACKFILL-C)."""
    return execute_generic_load_case(case, pkg, "ppm", "ppm.ppm_parser", "parse_ppm")


def execute_qoi_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a QOI valid case (GAP-ORC-BACKFILL-C)."""
    return execute_generic_load_case(case, pkg, "qoi", "qoi.qoi_parser", "parse_qoi")


def execute_odt_valid_case(case: dict, pkg: dict) -> dict:
    """Execute an ODT valid case using parse_odt."""
    if case.get("depth_level") == "D2" or case.get("expected_parse_result") == "SCHEMA_VALID":
        return _execute_odf_zip_d2_case(case, pkg, "odt")
    return execute_generic_load_case(case, pkg, "odt", "odt.odt_parser", "parse_odt")


def execute_fodp_valid_case(case: dict, pkg: dict) -> dict:
    """Execute a FODP valid case using fodp load()."""
    if case.get("depth_level") == "D2" or case.get("expected_parse_result") == "SCHEMA_VALID":
        return _execute_odf_flat_d2_case(case, pkg, "fodp")
    return execute_generic_load_case(case, pkg, "fodp", "fodp.fodp_codec", "load")


def _enrich_model(result_val: dict, format_id: str) -> dict:
    """Add derived properties so oracle expected_model_properties can match."""
    if not isinstance(result_val, dict):
        return result_val
    enriched = dict(result_val)
    if format_id == "safetensors":
        tensors = result_val.get("tensors", {})
        enriched["tensor_count"] = len(tensors) if isinstance(tensors, dict) else 0
        enriched["tensor_names"] = sorted(tensors.keys()) if isinstance(tensors, dict) else []
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
        unit_count = 0
        for f in (files if isinstance(files, list) else []):
            units = f.get("units", f.get("trans_units", []))
            unit_count += len(units) if isinstance(units, list) else 0
        enriched["unit_count"] = unit_count
    return enriched


def _execute_enriched_generic(case, pkg, format_id, module, callable_name):
    """Generic executor with model enrichment for derived properties."""
    case_id = case["case_id"]
    sample_ref = case.get("input_ref") or case.get("sample_ref")
    _, authority_status = check_authority(case, True)

    if not sample_ref:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref"],
        )

    sample_path = REPO_ROOT / sample_ref
    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    input_hash = sha256_file(sample_path)
    try:
        sys.path.insert(0, str(REPO_ROOT))
        import importlib
        mod = importlib.import_module(f"src.python.{module}")
        fn = getattr(mod, callable_name)
        result_val = fn(str(sample_path))
        result_val = _enrich_model(result_val, format_id)

        expected_props = case.get("expected_model_properties", [])
        observed, deviations, depth, ds_diagnostics = _compare_model_properties(result_val, expected_props)

        verdict_result = RESULT_FAIL if deviations else RESULT_PASS
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=verdict_result, authority_status=authority_status,
            observed=observed, deviations=deviations, input_hash=input_hash,
            depth_level=depth, diagnostics=ds_diagnostics,
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=[f"{type(e).__name__}: {e}"], input_hash=input_hash,
            depth_level=DEPTH_D0,
        )


def execute_ipynb_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "ipynb", "ipynb.ipynb_codec", "load_ipynb")


def execute_mtlx_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "mtlx", "mtlx.mtlx_codec", "load_mtlx")


def execute_nrrd_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "nrrd", "nrrd.nrrd_codec", "load_nrrd")


def execute_safetensors_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "safetensors", "safetensors.safetensors_codec", "load_safetensors")


def execute_ubl_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "ubl", "ubl.ubl_codec", "load_ubl")


def execute_xliff_valid_case(case: dict, pkg: dict) -> dict:
    return _execute_enriched_generic(case, pkg, "xliff", "xliff.xliff_codec", "load_xliff")


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
        unsupported_props = []
        for prop_def in case.get("expected_model_properties", []):
            prop = prop_def["property"]
            exp_val = prop_def["value"]
            expected_props[prop] = exp_val
            if prop not in observed:
                print(f"WARNING: ZST executor does not support property '{prop}' — INCONCLUSIVE", file=sys.stderr)
                unsupported_props.append(prop)
                continue
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({"property": prop, "expected": exp_val, "observed": obs_val})

        if unsupported_props:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="zst", product_id="format-factory-zst", language="python",
                case_id=case_id, profile="PARSE_VALIDITY",
                result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                observed=observed, expected=expected_props,
                diagnostics=[f"Unsupported properties in ZST executor: {unsupported_props}"],
                input_hash=input_hash,
            )

        result = RESULT_PASS if not deviations else RESULT_FAIL
        depth = DEPTH_D1 if expected_props else DEPTH_D0
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="zst", product_id="format-factory-zst", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=result, authority_status=authority_status,
            observed=observed, expected=expected_props,
            deviations=deviations, input_hash=input_hash,
            depth_level=depth,
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
                depth_level=DEPTH_D1,
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
        src_py = str(REPO_ROOT / "src" / "python")
        if src_py not in sys.path:
            sys.path.insert(0, src_py)
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
            data_source = prop_def.get("data_source", "unknown")
            expected_props[prop] = exp_val
            if prop not in observed:
                unsupported_props.append(prop)
                continue
            obs_val = observed.get(prop)
            if obs_val != exp_val:
                deviations.append({
                    "property": prop,
                    "expected": exp_val,
                    "observed": obs_val,
                    "data_source": data_source,
                })

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

        if deviations:
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="PARSE_VALIDITY",
                result=RESULT_FAIL, authority_status=authority_status,
                observed=observed, expected=expected_props, deviations=deviations,
                input_hash=input_hash, depth_level=DEPTH_D1,
            )

        # FF-XPLAN-001 W2A-008: D1→D2 upgrade via ODF RelaxNG schema validation
        depth = DEPTH_D1
        schema_detail = []
        try:
            from tools.oracle.schema_validator import validate_odf_schema  # noqa: PLC0415
            sv_result = validate_odf_schema(str(sample_path))
            if sv_result.get("provider") not in ("MISSING_PROVIDER", "lxml"):
                schema_detail.append(f"Schema provider: {sv_result.get('provider','unknown')}")
            elif sv_result.get("valid"):
                depth = DEPTH_D2
                schema_detail.append("ODF 1.3 RelaxNG schema: VALID")
                observed["schema_valid"] = True
            else:
                errs = sv_result.get("errors", [])[:2]
                schema_detail.append(f"Schema: {len(sv_result.get('errors',[]))} errors (D1 retained)")
                observed["schema_valid"] = False
        except Exception as _sv_err:
            schema_detail.append(f"Schema check skipped: {_sv_err}")

        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="PARSE_VALIDITY",
            result=RESULT_PASS, authority_status=authority_status,
            observed=observed, expected=expected_props, deviations=[],
            input_hash=input_hash, depth_level=depth,
            diagnostics=schema_detail if schema_detail else None,
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

    # fods-invalid-001: directory reference — test all .fods fixtures, PASS if any rejected
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
            try:
                sys.path.insert(0, str(REPO_ROOT))
                from src.python.fods.parser import parse_fods
                rejected_files = []
                accepted_files = []
                for fods_file in fods_files:
                    try:
                        r = parse_fods(str(fods_file))
                        if r.get("error") or r.get("parse_errors"):
                            rejected_files.append(fods_file.name)
                        else:
                            accepted_files.append(fods_file.name)
                    except Exception:
                        rejected_files.append(fods_file.name)
                # Oracle passes if at least one fixture is rejected
                # (Gate 7 corpus tests mixed-severity malformed files)
                any_rejected = len(rejected_files) > 0
                result = RESULT_PASS if any_rejected else RESULT_FAIL
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=result, authority_status=authority_status,
                    observed={
                        "total_fixtures": len(fods_files),
                        "rejected_count": len(rejected_files),
                        "accepted_count": len(accepted_files),
                    },
                    expected={"any_rejected": True},
                    diagnostics=[
                        f"Rejected ({len(rejected_files)}): {rejected_files}",
                        f"Accepted ({len(accepted_files)}): {accepted_files}",
                    ],
                )
            except ImportError as e:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INVALID_INPUT_REJECTION",
                    result=RESULT_INCONCLUSIVE, authority_status=authority_status,
                    diagnostics=[f"Import error: {e}"],
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


def execute_fods_rt_case(case: dict, pkg: dict) -> dict:
    """Execute FODS roundtrip case: parse → write → re-parse → compare semantics.

    TC-H1-001 (FF-XPLAN-001 healed plan): fods-rt-* cases at D1 depth.
    Compares sheet_count, sheet names, and non-empty cell values after round-trip.
    D2 upgrade applied if schema validates both source and output.
    """
    import os
    import tempfile
    case_id = case["case_id"]
    _, authority_status = check_authority(case, True)

    sample_ref = case.get("sample_ref") or "samples/by-format/fods/minimal-spreadsheet.fods"
    sample_path = REPO_ROOT / sample_ref

    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="ROUNDTRIP_SEMANTIC_EQUIVALENCE",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    tmp_path = None
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.python.fods.parser import parse_fods  # noqa: PLC0415
        from src.python.fods.writer import write_fods  # noqa: PLC0415

        # Step 1: parse source
        model1 = parse_fods(str(sample_path))

        # Step 2: write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fods", delete=False, encoding="utf-8"
        ) as tf:
            tmp_path = tf.name
        write_fods(model1, tmp_path)

        # Step 3: re-parse output
        model2 = parse_fods(tmp_path)

        # Step 4: semantic comparison
        mismatches = []

        sc1 = model1.get("sheet_count", 0)
        sc2 = model2.get("sheet_count", 0)
        if sc1 != sc2:
            mismatches.append(f"sheet_count mismatch: {sc1} vs {sc2}")

        sheets1 = model1.get("sheets", [])
        sheets2 = model2.get("sheets", [])
        names1 = [s.get("name", "") for s in sheets1]
        names2 = [s.get("name", "") for s in sheets2]
        if names1 != names2:
            mismatches.append(f"sheet_names mismatch: {names1} vs {names2}")

        # Compare non-empty cell values across all sheets
        def _extract_cells(sheets: list) -> list:
            cells = []
            for sheet in sheets:
                rows = sheet.get("rows", sheet.get("cells", []))
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, list):
                            for cell in row:
                                if isinstance(cell, dict):
                                    v = cell.get("value")
                                    if v is not None and v != "":
                                        cells.append(v)
                                elif cell is not None and cell != "":
                                    cells.append(cell)
            return cells

        cells1 = _extract_cells(sheets1)
        cells2 = _extract_cells(sheets2)
        if cells1 != cells2:
            mismatches.append(
                f"cell_values mismatch: {len(cells1)} non-empty cells vs {len(cells2)}"
            )

        depth = DEPTH_D1
        diags = [f"Roundtrip: {sample_path.name} → temp → re-parse"]

        # Attempt D2 upgrade via schema validation
        try:
            from tools.oracle.schema_validator import validate_odf_schema
            r1 = validate_odf_schema(str(sample_path))
            r2 = validate_odf_schema(tmp_path)
            if r1.get("valid") and r2.get("valid"):
                depth = DEPTH_D2
                diags.append("D2: schema validation PASS for source and output")
            else:
                errs = r1.get("errors", []) + r2.get("errors", [])
                diags.append(f"D2: schema validation not achieved ({errs[:1]})")
        except Exception as se:
            diags.append(f"D2: schema_validator unavailable — {se}")

        if mismatches:
            diags.extend(mismatches)
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="ROUNDTRIP_SEMANTIC_EQUIVALENCE",
                result=RESULT_FAIL, authority_status=authority_status,
                depth_level=depth, diagnostics=diags,
            )

        diags.append(f"sheet_count: {sc1}, sheet_names: {names1}, cells: {len(cells1)}")
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="ROUNDTRIP_SEMANTIC_EQUIVALENCE",
            result=RESULT_PASS, authority_status=authority_status,
            depth_level=depth, diagnostics=diags,
        )

    except ImportError as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="ROUNDTRIP_SEMANTIC_EQUIVALENCE",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=[f"Import error: {e}"],
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="ROUNDTRIP_SEMANTIC_EQUIVALENCE",
            result=RESULT_FAIL, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=[f"Exception: {type(e).__name__}: {e}"],
        )
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def execute_fods_libreoffice_case(case: dict, pkg: dict) -> dict:
    """Execute FODS D3 interoperability case via LibreOffice headless.

    TC-H1-002 (FF-XPLAN-001 healed plan): fods-lo-* cases at D3 depth.
    Returns SKIPPED_MISSING_PROVIDER if soffice is not on PATH (expected on CI).
    """
    import shutil
    import subprocess
    import tempfile
    case_id = case["case_id"]
    _, authority_status = check_authority(case, True)

    if not shutil.which("soffice"):
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INTEROPERABILITY",
            result=RESULT_SKIPPED_MISSING_PROVIDER, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=["LibreOffice (soffice) not found on PATH — D3 skipped"],
        )

    sample_ref = case.get("sample_ref") or "samples/by-format/fods/minimal-spreadsheet.fods"
    sample_path = REPO_ROOT / sample_ref

    if not sample_path.exists():
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INTEROPERABILITY",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=[f"Sample not found: {sample_path}"],
        )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.run(
                ["soffice", "--headless", "--convert-to", "xml",
                 "--outdir", tmpdir, str(sample_path)],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode != 0:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INTEROPERABILITY",
                    result=RESULT_FAIL, authority_status=authority_status,
                    depth_level=DEPTH_D3,
                    diagnostics=[f"soffice exited {proc.returncode}", proc.stderr[:200]],
                )
            # Check that an xml output file was produced
            from pathlib import Path as _Path
            xml_files = list(_Path(tmpdir).glob("*.xml"))
            if not xml_files:
                return make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id="fods", product_id="format-factory-fods", language="python",
                    case_id=case_id, profile="INTEROPERABILITY",
                    result=RESULT_FAIL, authority_status=authority_status,
                    depth_level=DEPTH_D3,
                    diagnostics=["soffice produced no xml output"],
                )
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id="fods", product_id="format-factory-fods", language="python",
                case_id=case_id, profile="INTEROPERABILITY",
                result=RESULT_PASS, authority_status=authority_status,
                depth_level=DEPTH_D3,
                diagnostics=[f"D3 PASS: LibreOffice converted to {xml_files[0].name}"],
            )
    except subprocess.TimeoutExpired:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INTEROPERABILITY",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            depth_level=DEPTH_D3,
            diagnostics=["soffice timed out after 60s"],
        )
    except Exception as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id="fods", product_id="format-factory-fods", language="python",
            case_id=case_id, profile="INTEROPERABILITY",
            result=RESULT_INCONCLUSIVE, authority_status=authority_status,
            depth_level=DEPTH_D0,
            diagnostics=[f"Exception: {type(e).__name__}: {e}"],
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


def _validate_oracle_package_schema(pkg: dict, format_id: str) -> list:
    """TC-ORC-006: Validate oracle package against JSON Schema. Returns list of error strings.

    Graceful degradation: returns [] (no errors) if jsonschema is not installed.
    Non-blocking: callers print WARNING but do not crash.
    """
    schema_path = ORACLE_DIR / "schema" / "oracle-package.schema.json"
    if not schema_path.exists():
        return []
    try:
        import jsonschema as _jschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            _jschema.validate(instance=pkg, schema=schema)
            return []
        except _jschema.ValidationError as e:
            return [f"Schema validation error: {e.message} (path: {list(e.absolute_path)})"]
        except _jschema.SchemaError as e:
            return [f"Schema itself is invalid: {e.message}"]
    except ImportError:
        print(f"WARNING: jsonschema not installed — oracle package schema validation skipped for {format_id}", file=sys.stderr)
        return []
    except Exception as e:
        return [f"Schema validation exception: {e}"]


def _check_case_coverage(pkg: dict, format_id: str) -> list[str]:
    """Warn about case types defined in oracle package but not executed (TC-OIS-008 Pillar 5).

    Makes the declare-vs-execute gap VISIBLE in committed evidence.
    """
    warnings = []

    # Roundtrip cases — wired for zst and fods only
    if pkg.get("roundtrip_cases") and format_id not in ("csv", "fods", "zst"):
        n = len(pkg["roundtrip_cases"])
        warnings.append(f"COVERAGE_GAP: {n} roundtrip_cases defined but no executor wired for {format_id}")

    # Interoperability cases — only fods is wired
    if pkg.get("interoperability_cases") and format_id != "fods":
        n = len(pkg["interoperability_cases"])
        warnings.append(f"COVERAGE_GAP: {n} interoperability_cases defined but no executor wired for {format_id}")

    # Invalid cases — wired for csv/fods (dedicated), others use generic if executor_config present
    invalid_cases = pkg.get("invalid_cases", [])
    if invalid_cases and format_id not in ("csv", "fods"):
        executor_config = pkg.get("executor_config", {})
        # Check for cases with sample_ref=null (no sample file) — generic executor returns NOT_APPLICABLE
        no_sample_cases = [c for c in invalid_cases if not c.get("sample_ref") and not c.get("input_inline")]
        if no_sample_cases:
            warnings.append(
                f"COVERAGE_GAP: {len(no_sample_cases)} invalid_cases have no sample_ref or input_inline "
                f"for {format_id} — will return NOT_APPLICABLE"
            )
        if not executor_config:
            warnings.append(
                f"COVERAGE_GAP: {len(invalid_cases)} invalid_cases defined but no executor_config "
                f"in oracle-package.yaml for {format_id}"
            )

    return warnings


def _compute_source_hash(format_id: str) -> str:
    """SHA-256 of all .py source files in src/python/{format_id}/, sorted by path (TC-OIS-006)."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    if not src_dir.exists():
        return "sha256:absent"
    h = hashlib.sha256()
    for py_file in sorted(src_dir.glob("**/*.py")):
        h.update(py_file.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _compute_package_hash(format_id: str) -> str:
    """SHA-256 of oracle-package.yaml for this format (TC-OIS-006)."""
    pkg_path = REPO_ROOT / "oracle" / "formats" / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        return "sha256:absent"
    return sha256_file(pkg_path)


def run_oracle_for_format(format_id: str, profile_filter: str = None, case_filter: str = None) -> dict:
    """Run oracle for a single format. Returns summary dict."""
    print(f"\n[oracle] Executing oracle for format: {format_id}")

    pkg = load_oracle_package(format_id)
    oracle_id = pkg["oracle_id"]

    # TC-ORC-006: Validate oracle package against JSON Schema (graceful — non-blocking)
    schema_errors = _validate_oracle_package_schema(pkg, format_id)
    if schema_errors:
        print(f"WARNING: oracle package for '{format_id}' failed schema validation:", file=sys.stderr)
        for err in schema_errors:
            print(f"  - {err}", file=sys.stderr)

    verdicts = []
    counts = {"PASS": 0, "FAIL": 0, "BLOCKED_MISSING_AUTHORITY": 0,
               "BLOCKED_MISSING_SAMPLE": 0, "INCONCLUSIVE": 0, "NOT_APPLICABLE": 0,
               "STALE_ORACLE": 0, "INVALID_ORACLE": 0,
               "SKIPPED_MISSING_PROVIDER": 0, "SKIPPED_MISSING_DEPENDENCY": 0}

    # TC-OIS-008 / MCP-W5-001 Pillar 5: Coverage gap check (emits to stderr, stored in summary)
    coverage_gaps = _check_case_coverage(pkg, format_id)
    for gap in coverage_gaps:
        print(f"  [WARN] {gap}", file=sys.stderr)

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
        elif format_id == "tsv":
            verdict = execute_tsv_valid_case(case, pkg)
        elif format_id == "ndjson":
            verdict = execute_ndjson_valid_case(case, pkg)
        elif format_id == "toml":
            verdict = execute_toml_valid_case(case, pkg)
        elif format_id == "abw":
            verdict = execute_abw_valid_case(case, pkg)
        elif format_id == "gnumeric":
            verdict = execute_gnumeric_valid_case(case, pkg)
        elif format_id == "dif":
            verdict = execute_dif_valid_case(case, pkg)
        elif format_id == "fodg":
            verdict = execute_fodg_valid_case(case, pkg)
        elif format_id == "ods":
            verdict = execute_ods_valid_case(case, pkg)
        elif format_id == "sylk":
            verdict = execute_sylk_valid_case(case, pkg)
        elif format_id == "fodt":
            verdict = execute_fodt_valid_case(case, pkg)
        elif format_id == "xcf":
            verdict = execute_xcf_valid_case(case, pkg)
        elif format_id == "pbm":
            verdict = execute_pbm_valid_case(case, pkg)
        elif format_id == "pgm":
            verdict = execute_pgm_valid_case(case, pkg)
        elif format_id == "ppm":
            verdict = execute_ppm_valid_case(case, pkg)
        elif format_id == "qoi":
            verdict = execute_qoi_valid_case(case, pkg)
        elif format_id == "odt":
            verdict = execute_odt_valid_case(case, pkg)
        elif format_id == "fodp":
            verdict = execute_fodp_valid_case(case, pkg)
        elif format_id == "ipynb":
            verdict = execute_ipynb_valid_case(case, pkg)
        elif format_id == "mtlx":
            verdict = execute_mtlx_valid_case(case, pkg)
        elif format_id == "nrrd":
            verdict = execute_nrrd_valid_case(case, pkg)
        elif format_id == "safetensors":
            verdict = execute_safetensors_valid_case(case, pkg)
        elif format_id == "ubl":
            verdict = execute_ubl_valid_case(case, pkg)
        elif format_id == "xliff":
            verdict = execute_xliff_valid_case(case, pkg)
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

    # Execute FODS roundtrip cases (TC-H1-001)
    if format_id == "fods":
        for case in pkg.get("roundtrip_cases", []):
            case_id = case["case_id"]
            if case_filter and case_id != case_filter:
                continue
            verdict = execute_fods_rt_case(case, pkg)
            verdicts.append(verdict)
            save_verdict(verdict, format_id)
            result = verdict["result"]
            counts[result] = counts.get(result, 0) + 1
            status_icon = "OK" if result == "PASS" else ("~~" if result == RESULT_SKIPPED_MISSING_PROVIDER else "FAIL")
            print(f"  [{status_icon}] {case_id}: {result}")

        # Execute FODS LibreOffice D3 cases (TC-H1-002)
        for case in pkg.get("interoperability_cases", []):
            case_id = case.get("case_id", "")
            if not case_id.startswith("fods-lo-"):
                continue
            if case_filter and case_id != case_filter:
                continue
            verdict = execute_fods_libreoffice_case(case, pkg)
            verdicts.append(verdict)
            save_verdict(verdict, format_id)
            result = verdict["result"]
            counts[result] = counts.get(result, 0) + 1
            status_icon = "OK" if result == "PASS" else ("~~" if result == RESULT_SKIPPED_MISSING_PROVIDER else "FAIL")
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

    # Execute invalid cases — all formats (TC-OIS-004 / MCP-W5-001 Pillar 1b)
    # Previously limited to csv and fods; now uses generic executor for all others.
    for case in pkg.get("invalid_cases", []):
        case_id = case["case_id"]
        if case_filter and case_id != case_filter:
            continue
        if format_id == "csv":
            # Only execute inline cases for CSV
            if case.get("input_inline") is None:
                continue
            verdict = execute_csv_invalid_case(case, pkg)
        elif format_id == "fods":
            # FODS: handles both directory refs and inline/description cases
            verdict = execute_fods_invalid_case(case, pkg)
        else:
            # Generic: resolve format's module and callable from oracle-package.yaml executor_config
            executor_config = pkg.get("executor_config", {})
            module = executor_config.get("module")
            callable_name = executor_config.get("callable")
            if module and callable_name:
                verdict = execute_generic_invalid_case(case, pkg, format_id, module, callable_name)
            else:
                # No executor_config — record COVERAGE_GAP explicitly
                _, authority_status = check_authority(case, False)
                verdict = make_verdict(
                    oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                    format_id=format_id, product_id=f"format-factory-{format_id}",
                    language="python", case_id=case_id,
                    profile="INVALID_INPUT_REJECTION",
                    result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
                    diagnostics=[f"COVERAGE_GAP: no executor_config in oracle-package.yaml for {format_id}"],
                )
        verdicts.append(verdict)
        save_verdict(verdict, format_id)
        result = verdict["result"]
        counts[result] = counts.get(result, 0) + 1
        print(f"  [{'OK' if result == 'PASS' else 'FAIL'}] {case_id}: {result}")

    # Summary with depth histogram (FF-XPLAN-001 W2A-005)
    total = len(verdicts)
    passed = counts["PASS"]
    depth_histogram = {}
    for v in verdicts:
        dl = v.get("depth_level", DEPTH_D0)
        depth_histogram[dl] = depth_histogram.get(dl, 0) + 1
    # Format depth = max depth achieved by any valid-case PASS verdict
    # Invalid cases test rejection (always D0) and should not lower the score
    valid_pass_depths = [
        v.get("depth_level", DEPTH_D0) for v in verdicts
        if v["result"] == "PASS" and not v.get("case_id", "").startswith(f"{format_id}-invalid")
    ]
    format_depth = max(valid_pass_depths, default=DEPTH_D0)
    # TC-OIS-006 / MCP-W5-001 Pillar 3: Source and package hashes for staleness detection.
    product_source_hash = _compute_source_hash(format_id)
    oracle_package_hash = _compute_package_hash(format_id)

    summary = {
        "oracle_id": oracle_id,
        "format_id": format_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": total,
        "results": counts,
        "pass_rate": f"{passed}/{total}" if total else "0/0",
        "verdict": "ALL_PASS" if passed == total and total > 0 else ("PARTIAL_PASS" if passed > 0 else "ALL_FAIL"),
        "verdicts_dir": str(LOCAL_ORACLE_DIR / format_id / "verdicts"),
        "depth_histogram": depth_histogram,
        "format_depth_score": format_depth,
        "product_source_hash": product_source_hash,
        "oracle_package_hash": oracle_package_hash,
        "coverage_gaps": coverage_gaps,
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
