"""Validate and canonicalize a spec feature manifest for a format.

Enumerating a specification's full feature set is a comprehension task, not a
mechanical one — this tool does not itself read specifications. An agent (or
human) reads the real spec, drafts a manifest matching
schemas/spec-coverage/feature-manifest-schema.json, and this tool validates
the draft, enforces feature_id numbering/uniqueness conventions, and writes
the canonical copy to reports/spec-coverage/manifests/<format_id>-feature-manifest.json.

This closes the gap found in the Select-6 feature-completeness audit: SAL
fact extraction (sal_master_runner.py) is template-based and produces only
2-3 bootstrap structural facts per format, portfolio-wide. No prior artifact
represents "the full feature list a spec defines, with implementation status
per item." This tool is the canonical, schema-enforced home for that list.

Usage:
    python tools/specification-authority-layer/enumerate_spec_features.py \\
        --format safetensors --draft path/to/draft.json [--authored-by <name>]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "spec-coverage" / "feature-manifest-schema.json"
MANIFEST_DIR = REPO_ROOT / "reports" / "spec-coverage" / "manifests"

FEATURE_ID_RE = re.compile(r"^FACT-[A-Z0-9]+-1[0-9]{2}$")
VALID_CATEGORIES = {
    "document_type", "encoding", "element", "field", "data_access",
    "safety_validation", "dtype", "api_capability", "mutation_capability",
}
VALID_REQUIREMENT_LEVELS = {"mandatory", "recommended", "optional"}


class ManifestValidationError(Exception):
    """Raised when a draft manifest fails schema/convention checks."""


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return a list of validation errors; empty list means valid."""
    errors: list[str] = []

    for required_key in ("format_id", "generated_at", "spec_source", "features"):
        if required_key not in manifest:
            errors.append(f"missing required top-level key: {required_key}")
    if errors:
        return errors

    format_id = manifest["format_id"]
    expected_prefix = f"FACT-{format_id.upper()}-1"

    spec_source = manifest.get("spec_source", {})
    if not spec_source.get("url"):
        errors.append("spec_source.url is required")
    if not spec_source.get("title"):
        errors.append("spec_source.title is required")

    features = manifest.get("features", [])
    if not features:
        errors.append("features must be a non-empty list")

    seen_ids: set[str] = set()
    for i, feature in enumerate(features):
        loc = f"features[{i}]"
        for required_key in ("feature_id", "category", "name", "requirement_level", "description", "evidence_keywords"):
            if required_key not in feature:
                errors.append(f"{loc}: missing required key: {required_key}")
        feature_id = feature.get("feature_id", "")
        if not FEATURE_ID_RE.match(feature_id):
            errors.append(f"{loc}: feature_id '{feature_id}' does not match pattern FACT-<FMT>-1NN")
        elif not feature_id.startswith(expected_prefix):
            errors.append(f"{loc}: feature_id '{feature_id}' does not match format_id '{format_id}' (expected prefix {expected_prefix})")
        if feature_id in seen_ids:
            errors.append(f"{loc}: duplicate feature_id '{feature_id}'")
        seen_ids.add(feature_id)

        category = feature.get("category")
        if category not in VALID_CATEGORIES:
            errors.append(f"{loc}: category '{category}' not in {sorted(VALID_CATEGORIES)}")

        req_level = feature.get("requirement_level")
        if req_level not in VALID_REQUIREMENT_LEVELS:
            errors.append(f"{loc}: requirement_level '{req_level}' not in {sorted(VALID_REQUIREMENT_LEVELS)}")

        evidence_keywords = feature.get("evidence_keywords")
        if not isinstance(evidence_keywords, list) or not evidence_keywords:
            errors.append(f"{loc}: evidence_keywords must be a non-empty list")

    return errors


def canonicalize(manifest: dict[str, Any], generator: str, authored_by: str | None) -> dict[str, Any]:
    """Return the manifest with generator metadata attached and features sorted by feature_id."""
    result = dict(manifest)
    result["generator"] = generator
    if authored_by:
        result["authored_by"] = authored_by
    result["features"] = sorted(manifest["features"], key=lambda f: f["feature_id"])
    # Enforce declared key order for readability.
    ordered_keys = ["format_id", "generated_at", "generator", "authored_by", "spec_source", "features"]
    return {k: result[k] for k in ordered_keys if k in result}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--draft", required=True, type=Path, help="Path to a draft manifest JSON file")
    parser.add_argument("--authored-by", default=None)
    args = parser.parse_args()

    if not args.draft.exists():
        print(f"ERROR: draft file not found: {args.draft}", file=sys.stderr)
        return 1

    draft = json.loads(args.draft.read_text(encoding="utf-8"))

    if draft.get("format_id") != args.format_id:
        print(
            f"ERROR: draft format_id '{draft.get('format_id')}' does not match "
            f"--format '{args.format_id}'",
            file=sys.stderr,
        )
        return 1

    errors = validate_manifest(draft)
    if errors:
        print(f"VALIDATION FAILED for {args.format_id} ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    canonical = canonicalize(draft, generator="enumerate_spec_features.py v1", authored_by=args.authored_by)

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MANIFEST_DIR / f"{args.format_id}-feature-manifest.json"
    out_path.write_text(json.dumps(canonical, indent=2) + "\n", encoding="utf-8")

    print(f"OK: {len(canonical['features'])} features validated and written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
