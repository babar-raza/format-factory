"""ODF RelaxNG Schema Validator for Oracle D2 depth (FF-XPLAN-001 W2A-007).

Validates FODS/FODT/ODS XML against ODF 1.3 RelaxNG schema using lxml.
Returns structured validation results compatible with oracle verdicts.

Usage:
    from tools.oracle.schema_validator import validate_odf_schema
    result = validate_odf_schema(fods_path)
    # result = {"valid": True/False, "errors": [...], "schema_version": "1.3"}
"""
from __future__ import annotations

from pathlib import Path


SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "oracle" / "schemas" / "odf-1.3-relaxng"
SCHEMA_FILE = SCHEMA_DIR / "OpenDocument-v1.3-schema.rng"


def validate_odf_schema(xml_path: str | Path) -> dict:
    """Validate an ODF XML file against the ODF 1.3 RelaxNG schema.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "schema_version": str,
            "schema_path": str,
            "provider": "lxml",
        }
    """
    xml_path = Path(xml_path)

    if not xml_path.exists():
        return {
            "valid": False,
            "errors": [f"File not found: {xml_path}"],
            "schema_version": "1.3",
            "schema_path": str(SCHEMA_FILE),
            "provider": "lxml",
        }

    if not SCHEMA_FILE.exists():
        return {
            "valid": False,
            "errors": [f"Schema not found: {SCHEMA_FILE}. Run W2A-006 to download ODF 1.3 RelaxNG."],
            "schema_version": "1.3",
            "schema_path": str(SCHEMA_FILE),
            "provider": "lxml",
        }

    try:
        from lxml import etree
    except ImportError:
        return {
            "valid": False,
            "errors": ["lxml not installed. Install with: pip install lxml"],
            "schema_version": "1.3",
            "schema_path": str(SCHEMA_FILE),
            "provider": "MISSING_PROVIDER",
        }

    try:
        schema_doc = etree.parse(str(SCHEMA_FILE))
        relaxng = etree.RelaxNG(schema_doc)
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Schema parse error: {e}"],
            "schema_version": "1.3",
            "schema_path": str(SCHEMA_FILE),
            "provider": "lxml",
        }

    try:
        doc = etree.parse(str(xml_path))
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"XML parse error: {e}"],
            "schema_version": "1.3",
            "schema_path": str(SCHEMA_FILE),
            "provider": "lxml",
        }

    is_valid = relaxng.validate(doc)
    errors = [str(err) for err in relaxng.error_log] if not is_valid else []

    return {
        "valid": is_valid,
        "errors": errors[:20],  # Cap at 20 errors
        "schema_version": "1.3",
        "schema_path": str(SCHEMA_FILE),
        "provider": "lxml",
    }
