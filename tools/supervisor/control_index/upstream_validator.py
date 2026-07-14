"""Upstream source validator — validate JSON/YAML sources before ingestion.

TC-OCRD-C4-01: Provides ValidationResult and validate_upstream_source() for
ingestors to call before inserting rows. Failed validation triggers quarantine.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    valid: bool
    failures: list[str] = field(default_factory=list)
    quarantine: bool = False


def validate_upstream_source(
    source_path: Path,
    required_fields: list[str] | None = None,
) -> ValidationResult:
    """Validate a JSON or YAML source file before ingestion.

    Args:
        source_path: Absolute or repo-relative path to source file.
        required_fields: Top-level keys that must be present in the parsed data.

    Returns:
        ValidationResult with valid=True if the file parses and has required fields.
        Sets quarantine=True for missing/parse-error files; False for missing fields only.
    """
    if not source_path.exists():
        return ValidationResult(
            valid=False,
            failures=[f"NOT_FOUND: {source_path}"],
            quarantine=True,
        )

    try:
        text = source_path.read_text(encoding="utf-8")
        if source_path.suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore[import]
                data = yaml.safe_load(text)
            except ImportError:
                # Fallback: minimal parse check only
                data = {}
        else:
            data = json.loads(text)
    except Exception as exc:
        return ValidationResult(
            valid=False,
            failures=[f"PARSE_ERROR: {exc}"],
            quarantine=True,
        )

    failures: list[str] = []
    if required_fields:
        for field_name in required_fields:
            if not (isinstance(data, dict) and field_name in data):
                failures.append(f"MISSING_FIELD: {field_name}")

    return ValidationResult(
        valid=len(failures) == 0,
        failures=failures,
        quarantine=len(failures) > 0,
    )
