"""
validate_requirement_pack.py — Validate provenance completeness of a requirement pack.

format-factory project — Spec Workbench v1
Created: run030 (2026-05-06)

Validates that a requirement pack produced by build_requirement_pack.py:
1. Has a requirement_id for every requirement
2. Has source_sha256 provenance for every requirement
3. Has spec_section or spec_page for every requirement
4. Has verification_status for every requirement
5. Has confidence for every requirement
6. Contains no full spec text excerpts

Usage:
    python validate_requirement_pack.py --pack .local/spec-cache/fods/1.3/workbench/requirement-packs/parser-requirements.yaml
    python validate_requirement_pack.py --format-id fods --version 1.3 --packet parser

License: Apache-2.0 (project-owned, format-factory)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _workbench_dir(fmt: str, ver: str) -> Path:
    return _repo_root() / ".local" / "spec-cache" / fmt / ver / "workbench"


REQUIRED_PROVENANCE_FIELDS = [
    "source_sha256",
    "spec_section",
    "verification_status",
    "confidence",
]

# Minimum required fields per requirement
REQUIRED_FIELDS = ["requirement_id", "claim"] + REQUIRED_PROVENANCE_FIELDS


def validate_pack(pack_path: Path) -> dict[str, Any]:
    """Validate a requirement pack file. Returns a validation report."""
    report: dict[str, Any] = {
        "pack_path": str(pack_path),
        "checks": [],
        "overall": "PASS",
    }

    def check(name: str, passed: bool, detail: str = "") -> None:
        report["checks"].append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            report["overall"] = "FAIL"

    # File existence
    if not pack_path.exists():
        check("file_exists", False, f"File not found: {pack_path}")
        return report

    check("file_exists", True)

    # JSON parse
    try:
        data = json.loads(pack_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        check("json_valid", False, str(e))
        return report

    check("json_valid", True)

    # Required top-level fields
    for field in ["format_id", "spec_version", "requirements"]:
        check(f"has_{field}", field in data, f"data={list(data.keys())}")

    if "requirements" not in data:
        return report

    reqs = data["requirements"]
    check("requirements_non_empty", len(reqs) > 0, f"count={len(reqs)}")

    # Per-requirement checks
    for i, req in enumerate(reqs):
        rid = req.get("requirement_id", f"idx-{i}")
        prefix = f"req[{rid}]"

        check(f"{prefix}.has_requirement_id", "requirement_id" in req, f"keys={list(req.keys())}")
        check(f"{prefix}.has_claim", "claim" in req, "")

        for field in REQUIRED_PROVENANCE_FIELDS:
            check(
                f"{prefix}.has_{field}",
                field in req,
                f"missing provenance field {field!r}",
            )

        # Spec reference: must have section OR page
        has_section = bool(req.get("spec_section"))
        has_page = req.get("spec_page") is not None
        check(
            f"{prefix}.has_spec_location",
            has_section or has_page,
            "must have spec_section or spec_page",
        )

        # source_sha256 must not be empty
        sha = req.get("source_sha256", "")
        check(
            f"{prefix}.sha256_non_empty",
            bool(sha) and sha != "unknown",
            f"sha256={sha!r}",
        )

        # No raw spec text should appear in a requirement (very long claim is suspicious)
        claim_len = len(req.get("claim", ""))
        check(
            f"{prefix}.claim_not_full_text",
            claim_len < 500,
            f"claim length={claim_len} (>=500 may contain raw spec text)",
        )

        # verification_status must be valid
        vs = req.get("verification_status", "")
        check(
            f"{prefix}.valid_verification_status",
            vs in ("draft", "verified", "disputed"),
            f"status={vs!r}",
        )

        # confidence must be valid
        conf = req.get("confidence", "")
        check(
            f"{prefix}.valid_confidence",
            conf in ("high", "medium", "low"),
            f"confidence={conf!r}",
        )

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate provenance completeness of a requirement pack."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pack", help="Path to requirement pack JSON/YAML file")
    group.add_argument("--format-id", help="Format ID (use with --version and --packet)")
    parser.add_argument("--version", help="Spec version (required with --format-id)")
    parser.add_argument(
        "--packet",
        choices=["sample", "parser", "model", "all"],
        help="Packet type to validate (required with --format-id)",
    )
    args = parser.parse_args()

    if args.pack:
        pack_paths = [Path(args.pack)]
    else:
        if not args.version or not args.packet:
            print("--version and --packet required when using --format-id", file=sys.stderr)
            sys.exit(1)
        wb_dir = _workbench_dir(args.format_id.lower(), args.version)
        pack_dir = wb_dir / "requirement-packs"
        if args.packet == "all":
            pack_paths = list(pack_dir.glob("*.yaml")) + list(pack_dir.glob("*.json"))
        else:
            name_map = {
                "parser": "parser-requirements.yaml",
                "sample": "sample-requirements.yaml",
                "model": "model-requirements-draft.yaml",
            }
            pack_paths = [pack_dir / name_map[args.packet]]

    all_pass = True
    for pack_path in pack_paths:
        report = validate_pack(pack_path)
        passed = sum(1 for c in report["checks"] if c["passed"])
        total = len(report["checks"])
        print(f"\n--- {pack_path.name} ---")
        print(f"Overall: {report['overall']}  ({passed}/{total} checks pass)")

        for chk in report["checks"]:
            status = "PASS" if chk["passed"] else "FAIL"
            detail = f" — {chk['detail']}" if chk.get("detail") else ""
            if not chk["passed"]:
                print(f"  [{status}] {chk['check']}{detail}")

        if report["overall"] != "PASS":
            all_pass = False

    print()
    if all_pass:
        print("=== Validation: PASS ===")
    else:
        print("=== Validation: FAIL — review above ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
