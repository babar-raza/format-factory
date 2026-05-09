#!/usr/bin/env python3
"""
validate_format_understanding.py - Read-Only Format Understanding Package Validator

Validates a Format Understanding package (6 YAML files) against minimum standards.
This tool is STRICTLY READ-ONLY: reads files, writes nothing, makes no network calls.

Usage:
    python validate_format_understanding.py --format fods --pack acquisition-packs/fods
        --min-facts 20 --min-requirements 20

    python validate_format_understanding.py --format fodt --pack acquisition-packs/fodt
        --min-facts 15 --min-requirements 15 --allow-partial-product-readiness

Exit codes:
    0 = FORMAT_UNDERSTANDING_VALIDATION: PASS
    1 = FORMAT_UNDERSTANDING_VALIDATION: FAIL
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml as _yaml
    def _load_yaml(text):
        return _yaml.safe_load(text)
except ImportError:
    _yaml = None
    def _load_yaml(text):
        # Minimal YAML loader (key: value only, no nested)
        result = {}
        for line in text.splitlines():
            m = re.match(r'^(\w[\w_-]*):\s*(.*)', line.strip())
            if m:
                result[m.group(1)] = m.group(2).strip().strip('"\'')
        return result


FUL_FILES = [
    "format-profile.yaml",
    "verified-facts.yaml",
    "implementation-requirements.yaml",
    "parser-strategy.yaml",
    "security-surface.yaml",
    "product-readiness.yaml",
]

REQUIRED_FORMAT_PROFILE_FIELDS = [
    "format_id", "display_name", "physical_representation", "legal_category",
    "xml_namespace_root", "mime_type", "container_model",
]

REQUIRED_PRODUCT_READINESS_FIELDS = [
    "format_id", "product_source_state", "source_authorization_state",
]


def split_frontmatter(text):
    """Split ---\n...\n---\n body into (frontmatter_text, body_text)."""
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1].strip(), parts[2].strip()
    return "", text.strip()


def load_yaml_section(text, filename, errors):
    """Load YAML from text, appending errors on failure."""
    try:
        data = _load_yaml(text)
        if data is None:
            data = {}
        return data
    except Exception as e:
        errors.append(f"{filename}: YAML parse error: {e}")
        return None


def validate_package(format_id, pack_dir, min_facts, min_requirements,
                     allow_partial_product_readiness=False):
    errors = []
    warnings = []
    pack_path = Path(pack_dir)
    results = {}

    for fname in FUL_FILES:
        fpath = pack_path / fname
        if not fpath.exists():
            errors.append(f"Missing required file: {fname}")
            continue
        raw = fpath.read_text(encoding="utf-8")
        fm_text, body_text = split_frontmatter(raw)
        fm = load_yaml_section(fm_text, f"{fname} frontmatter", errors)
        body = load_yaml_section(body_text, f"{fname} body", errors)
        if body is None:
            continue  # Already reported YAML error

        # format-profile checks
        if fname == "format-profile.yaml":
            if body is not None:
                for field in REQUIRED_FORMAT_PROFILE_FIELDS:
                    if field not in body:
                        errors.append(f"format-profile.yaml: missing required field '{field}'")
                fid = body.get("format_id", "")
                if fid != format_id:
                    errors.append(f"format-profile.yaml: format_id mismatch: expected '{format_id}', got '{fid}'")
            results["format_profile"] = body

        # verified-facts checks
        elif fname == "verified-facts.yaml":
            if body is not None:
                facts = body.get("facts", [])
                if not isinstance(facts, list):
                    errors.append("verified-facts.yaml: 'facts' must be a list")
                else:
                    count = len(facts)
                    results["fact_count"] = count
                    if count < min_facts:
                        errors.append(
                            f"verified-facts.yaml: fact count {count} < minimum {min_facts}"
                        )
                    for i, fact in enumerate(facts):
                        if not isinstance(fact, dict):
                            errors.append(f"verified-facts.yaml: fact[{i}] is not a dict")
                            continue
                        if not fact.get("evidence_source"):
                            errors.append(
                                f"verified-facts.yaml: fact_id {fact.get('fact_id','?')} missing evidence_source"
                            )
                        if not fact.get("spec_citation"):
                            warnings.append(
                                f"verified-facts.yaml: fact_id {fact.get('fact_id','?')} missing spec_citation"
                            )

        # implementation-requirements checks
        elif fname == "implementation-requirements.yaml":
            if body is not None:
                reqs = body.get("requirements", [])
                if not isinstance(reqs, list):
                    errors.append("implementation-requirements.yaml: 'requirements' must be a list")
                else:
                    count = len(reqs)
                    results["req_count"] = count
                    if count < min_requirements:
                        errors.append(
                            f"implementation-requirements.yaml: req count {count} < minimum {min_requirements}"
                        )

        # product-readiness checks
        elif fname == "product-readiness.yaml":
            if body is not None:
                for field in REQUIRED_PRODUCT_READINESS_FIELDS:
                    if field not in body:
                        if not allow_partial_product_readiness:
                            errors.append(
                                f"product-readiness.yaml: missing required field '{field}'"
                            )
                        else:
                            warnings.append(
                                f"product-readiness.yaml: missing field '{field}' (allowed with --allow-partial)"
                            )
                pss = body.get("product_source_state", "")
                valid_pss = ("not_created", "partial", "created", "")
                if pss and pss not in valid_pss:
                    errors.append(
                        f"product-readiness.yaml: product_source_state must be one of {valid_pss}, got '{pss}'"
                    )
                sas = body.get("source_authorization_state", "")
                valid_sas = ("not_authorized", "authorized", "partial", "authorized_and_executed")
                if sas and sas not in valid_sas:
                    warnings.append(
                        f"product-readiness.yaml: unexpected source_authorization_state '{sas}'"
                    )
                if body.get("partial") and not allow_partial_product_readiness:
                    errors.append(
                        "product-readiness.yaml: partial=true but --allow-partial-product-readiness not set"
                    )
                results["product_readiness"] = body

    return errors, warnings, results


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Format Understanding package"
    )
    parser.add_argument("--format", required=True, help="format_id (e.g. fods, fodt)")
    parser.add_argument("--pack", required=True, help="path to acquisition pack directory")
    parser.add_argument("--min-facts", type=int, default=20)
    parser.add_argument("--min-requirements", type=int, default=20)
    parser.add_argument("--allow-partial-product-readiness", action="store_true")
    args = parser.parse_args()

    errors, warnings, results = validate_package(
        format_id=args.format,
        pack_dir=args.pack,
        min_facts=args.min_facts,
        min_requirements=args.min_requirements,
        allow_partial_product_readiness=args.allow_partial_product_readiness,
    )

    print(f"format_id: {args.format}")
    print(f"pack: {args.pack}")
    print(f"facts: {results.get('fact_count', 'N/A')}")
    print(f"requirements: {results.get('req_count', 'N/A')}")
    pr = results.get("product_readiness", {})
    if pr:
        print(f"product_source_state: {pr.get('product_source_state', 'N/A')}")

    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("FORMAT_UNDERSTANDING_VALIDATION: FAIL")
        print("errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("FORMAT_UNDERSTANDING_VALIDATION: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
