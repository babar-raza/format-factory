"""scaffold_oracle_obligation.py — Oracle obligation scaffold tool (TC-W2-001).

Generates minimum-floor oracle package YAML for newly registered formats.
Integrates with V145 governance validator.

Usage:
    python tools/oracle/scaffold_oracle_obligation.py --format <format_id> --dry-run
    python tools/oracle/scaffold_oracle_obligation.py --format <format_id>
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ORACLE_ROOT = REPO_ROOT / "oracle" / "formats"


MINIMUM_FLOOR_TEMPLATE = {
    "oracle_id": None,  # filled at runtime
    "format_id": None,
    "oracle_version": 1,
    "status": "OBLIGATION_CREATED",
    "generated_at": None,
    "generator_skill": "scaffold_oracle_obligation",
    "authority": {
        "specification_refs": [
            {
                "id": "SPEC-PLACEHOLDER",
                "title": "PLACEHOLDER — fill with authoritative spec",
                "authority_class": "SPEC_INFORMATIVE",
                "note": "Replace with real specification reference before promoting to CASES_DEFINED.",
            }
        ],
        "authority_summary": "PLACEHOLDER — replace with real authority summary.",
    },
    "profiles": ["STRUCTURAL_VALIDITY", "PARSE_VALIDITY"],
    "valid_cases": [
        {
            "case_id": None,  # filled at runtime
            "purpose": "PLACEHOLDER — replace with real parse-and-verify test",
            "authority_class": "SPEC_INFORMATIVE",
            "sample_ref": None,
            "expected_parse_result": "SUCCESS",
            "expected_model_properties": [
                {
                    "property": "format_id",
                    "value": None,  # filled at runtime
                    "data_source": "parsed",
                    "authority": "PLACEHOLDER",
                }
            ],
            "applicable_profiles": ["STRUCTURAL_VALIDITY", "PARSE_VALIDITY"],
            "status": "PLACEHOLDER_REQUIRED",
        }
    ],
    "invalid_cases": [
        {
            "case_id": None,  # filled at runtime
            "purpose": "PLACEHOLDER — replace with real invalid input rejection test",
            "defect_class": "wrong-format",
            "authority_class": "SPEC_INFORMATIVE",
            "sample_ref": None,
            "expected_failure_stage": "PARSE",
            "expected_error_type": "Exception or error indicator",
            "partial_recovery_allowed": True,
            "security_relevance": False,
            "status": "PLACEHOLDER_REQUIRED",
        }
    ],
    "canonicalization": {
        "method": "PLACEHOLDER",
        "encoding_policy": "UTF-8",
    },
    "tolerance_policy": {
        "policy_summary": "PLACEHOLDER — fill with format-specific tolerance rules",
    },
    "comparators": ["model-property-comparator"],
}


def build_scaffold(format_id: str) -> dict:
    """Build a minimum-floor oracle obligation scaffold for the given format."""
    now = datetime.now(timezone.utc).isoformat()
    scaffold = {
        "oracle_id": f"oracle-{format_id}-v1",
        "format_id": format_id,
        "oracle_version": 1,
        "status": "OBLIGATION_CREATED",
        "generated_at": now,
        "generator_skill": "scaffold_oracle_obligation",
        "authority": MINIMUM_FLOOR_TEMPLATE["authority"].copy(),
        "profiles": list(MINIMUM_FLOOR_TEMPLATE["profiles"]),
        "valid_cases": [
            {
                "case_id": f"{format_id}-valid-001",
                "purpose": f"PLACEHOLDER — {format_id} parse test",
                "authority_class": "SPEC_INFORMATIVE",
                "sample_ref": f"samples/by-format/{format_id}/",
                "expected_parse_result": "SUCCESS",
                "expected_model_properties": [
                    {
                        "property": "format_id",
                        "value": format_id,
                        "data_source": "parsed",
                        "authority": "PLACEHOLDER",
                    }
                ],
                "applicable_profiles": ["STRUCTURAL_VALIDITY", "PARSE_VALIDITY"],
                "status": "PLACEHOLDER_REQUIRED",
            }
        ],
        "invalid_cases": [
            {
                "case_id": f"{format_id}-invalid-001",
                "purpose": f"PLACEHOLDER — {format_id} invalid input rejection",
                "defect_class": "wrong-format",
                "authority_class": "SPEC_INFORMATIVE",
                "sample_ref": None,
                "expected_failure_stage": "PARSE",
                "expected_error_type": "Exception or error indicator",
                "partial_recovery_allowed": True,
                "security_relevance": False,
                "status": "PLACEHOLDER_REQUIRED",
            }
        ],
        "canonicalization": MINIMUM_FLOOR_TEMPLATE["canonicalization"].copy(),
        "tolerance_policy": MINIMUM_FLOOR_TEMPLATE["tolerance_policy"].copy(),
        "comparators": list(MINIMUM_FLOOR_TEMPLATE["comparators"]),
    }
    return scaffold


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold oracle obligation for a format.")
    parser.add_argument("--format", dest="format_id", required=True, help="Format ID (e.g. 'myformat')")
    parser.add_argument("--dry-run", action="store_true", help="Print scaffold YAML without writing files")
    args = parser.parse_args()

    format_id = args.format_id.lower().strip()
    scaffold = build_scaffold(format_id)
    yaml_text = yaml.dump(scaffold, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if args.dry_run:
        print(yaml_text)
        print(f"# Dry-run complete for format '{format_id}'. No files written.", file=sys.stderr)
        return 0

    # Write to oracle/formats/{format_id}/oracle-package.yaml
    out_dir = ORACLE_ROOT / format_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "oracle-package.yaml"

    if out_path.exists():
        print(f"ERROR: {out_path} already exists. Remove it first or use --dry-run.", file=sys.stderr)
        return 1

    out_path.write_text(yaml_text, encoding="utf-8")
    print(f"Written: {out_path}", file=sys.stderr)
    print(f"NEXT STEPS: Fill in PLACEHOLDER fields before running execute_oracle.py.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
