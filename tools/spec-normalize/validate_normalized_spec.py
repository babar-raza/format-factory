"""
validate_normalized_spec.py — Normalized Spec Validator
format-factory / tools/spec-normalize/

Purpose:
    Validate that a normalized spec directory is complete, consistent,
    and suitable for use in gate-gated work (Gate 4+).

Checks performed:
    1. source-manifest.yaml present and shows SHA-256 MATCH
    2. extraction-report.md present
    3. text.txt or pages.jsonl present (text extraction complete)
    4. sections.jsonl present if normalization claimed FULL status
    5. page-map.yaml present if sections.jsonl present
    6. citations.yaml present (citation map built)
    7. parser-requirements.yaml present (Gate 4 readiness check)
    8. verified-facts.yaml present (Gate 5 readiness check)
    9. No stale artifacts (source hash still matches)
    10. All artifact sizes are non-zero

Policy:
    - Reads ONLY from local normalized artifacts (never downloads).
    - Does NOT call network endpoints.
    - Does NOT call LLM endpoints.
    - Does NOT modify any artifact.
    - Exits 0 if all required checks pass, 1 if any required check fails.

See also:
    docs/python-foss/specification-normalization.md — full policy
    tools/spec-normalize/_readme.md    — directory orientation
"""

import argparse
import hashlib
import pathlib
import sys
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------

CHECK_PASS = "PASS"
CHECK_FAIL = "FAIL"
CHECK_WARN = "WARN"
CHECK_SKIP = "SKIP"


def check(label: str, result: str, detail: str = "") -> dict:
    symbol = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}.get(result, "[????]")
    print(f"  {symbol} {label}" + (f": {detail}" if detail else ""))
    return {"label": label, "result": result, "detail": detail}


def file_exists_nonempty(path: pathlib.Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def load_yaml_safe(path: pathlib.Path) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def compute_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


# ---------------------------------------------------------------------------
# Validation suites
# ---------------------------------------------------------------------------

def validate_source_manifest(normalized_dir: pathlib.Path) -> tuple[list[dict], bool, str]:
    """Returns (checks, hash_match, spec_dir_path)."""
    results = []
    manifest_path = normalized_dir / "source-manifest.yaml"

    if not file_exists_nonempty(manifest_path):
        results.append(check("source-manifest.yaml present", CHECK_FAIL,
                              "File missing — run normalize_pdf.py first"))
        return results, False, ""

    results.append(check("source-manifest.yaml present", CHECK_PASS))

    data = load_yaml_safe(manifest_path)
    if data is None:
        results.append(check("source-manifest.yaml readable", CHECK_FAIL, "YAML parse error"))
        return results, False, ""

    sm = data.get("source_manifest", data)
    hash_match = sm.get("sha256_match", False)
    source_path = sm.get("source_local_path", "")

    if hash_match:
        results.append(check("SHA-256 hash match", CHECK_PASS, sm.get("sha256_computed", "")))
    else:
        results.append(check("SHA-256 hash match", CHECK_FAIL,
                              f"Expected: {sm.get('sha256_expected', '?')} | Computed: {sm.get('sha256_computed', '?')}"))

    # Verify source file still exists and hash is still current
    if source_path and pathlib.Path(source_path).exists():
        current_hash = compute_sha256(pathlib.Path(source_path))
        expected = sm.get("sha256_computed", "")
        if current_hash == expected:
            results.append(check("Source file still matches recorded hash", CHECK_PASS))
        else:
            results.append(check("Source file still matches recorded hash", CHECK_FAIL,
                                  "Source file changed since manifest was written — regenerate normalized artifacts"))
            hash_match = False
    else:
        results.append(check("Source file accessible", CHECK_WARN,
                              f"Cannot re-verify: {source_path}"))

    return results, hash_match, source_path


def validate_text_artifacts(normalized_dir: pathlib.Path) -> list[dict]:
    results = []

    text_path = normalized_dir / "text.txt"
    pages_path = normalized_dir / "pages.jsonl"

    has_text = file_exists_nonempty(text_path)
    has_pages = file_exists_nonempty(pages_path)

    if has_text:
        size = text_path.stat().st_size
        results.append(check("text.txt present and non-empty", CHECK_PASS, f"{size:,} bytes"))
    else:
        results.append(check("text.txt present and non-empty", CHECK_WARN,
                              "Not present — normalization may be metadata-only"))

    if has_pages:
        try:
            with open(pages_path, "r", encoding="utf-8") as f:
                page_count = sum(1 for line in f if line.strip())
            results.append(check("pages.jsonl present and non-empty", CHECK_PASS,
                                  f"{page_count} pages"))
        except Exception as e:
            results.append(check("pages.jsonl readable", CHECK_FAIL, str(e)))
    else:
        results.append(check("pages.jsonl present and non-empty", CHECK_WARN,
                              "Not present — normalization may be metadata-only"))

    if not has_text and not has_pages:
        results.append(check("Text extraction complete", CHECK_FAIL,
                              "Neither text.txt nor pages.jsonl found — install pdfminer.six and re-run"))

    return results


def validate_structure_artifacts(normalized_dir: pathlib.Path) -> list[dict]:
    results = []

    sections_path = normalized_dir / "sections.jsonl"
    page_map_path = normalized_dir / "page-map.yaml"

    if file_exists_nonempty(sections_path):
        try:
            with open(sections_path, "r", encoding="utf-8") as f:
                count = sum(1 for line in f if line.strip())
            results.append(check("sections.jsonl present", CHECK_PASS, f"{count} sections"))
        except Exception as e:
            results.append(check("sections.jsonl readable", CHECK_FAIL, str(e)))

        if file_exists_nonempty(page_map_path):
            results.append(check("page-map.yaml present", CHECK_PASS))
        else:
            results.append(check("page-map.yaml present", CHECK_WARN,
                                  "sections.jsonl exists but page-map.yaml missing"))
    else:
        results.append(check("sections.jsonl present", CHECK_SKIP,
                              "Not yet produced (section detection not run)"))
        results.append(check("page-map.yaml present", CHECK_SKIP,
                              "Depends on sections.jsonl"))

    return results


def validate_citation_artifacts(normalized_dir: pathlib.Path) -> list[dict]:
    results = []
    citations_path = normalized_dir / "citations.yaml"

    if file_exists_nonempty(citations_path):
        data = load_yaml_safe(citations_path)
        if data:
            cm = data.get("citation_map", {})
            s_count = cm.get("section_references", {}).get("total_unique", "?")
            e_count = cm.get("external_references", {}).get("total_unique", "?")
            results.append(check("citations.yaml present", CHECK_PASS,
                                  f"{s_count} section refs, {e_count} external refs"))
        else:
            results.append(check("citations.yaml readable", CHECK_FAIL, "YAML parse error"))
    else:
        results.append(check("citations.yaml present", CHECK_SKIP,
                              "Not yet produced — run build_citation_map.py"))

    return results


def validate_gate_readiness(normalized_dir: pathlib.Path) -> list[dict]:
    """Gate 4 and Gate 5 readiness checks."""
    results = []

    # Gate 4: parser-requirements.yaml
    pr_path = normalized_dir / "parser-requirements.yaml"
    if file_exists_nonempty(pr_path):
        data = load_yaml_safe(pr_path)
        if data:
            req_count = len(data.get("parser_requirements", data.get("requirements", [])))
            results.append(check("parser-requirements.yaml present [Gate 4]", CHECK_PASS,
                                  f"{req_count} requirements"))
        else:
            results.append(check("parser-requirements.yaml readable [Gate 4]", CHECK_FAIL,
                                  "YAML parse error"))
    else:
        results.append(check("parser-requirements.yaml present [Gate 4]", CHECK_WARN,
                              "Not yet produced — required before Gate 4 may begin"))

    # Gate 5: verified-facts.yaml
    vf_path = normalized_dir / "verified-facts.yaml"
    if file_exists_nonempty(vf_path):
        data = load_yaml_safe(vf_path)
        if data:
            fact_count = len(data.get("verified_facts", data.get("facts", [])))
            results.append(check("verified-facts.yaml present [Gate 5]", CHECK_PASS,
                                  f"{fact_count} facts"))
        else:
            results.append(check("verified-facts.yaml readable [Gate 5]", CHECK_FAIL,
                                  "YAML parse error"))
    else:
        results.append(check("verified-facts.yaml present [Gate 5]", CHECK_SKIP,
                              "Not yet produced — useful for Gate 5 neutral model design"))

    return results


def validate_extraction_report(normalized_dir: pathlib.Path) -> list[dict]:
    results = []
    report_path = normalized_dir / "extraction-report.md"
    if file_exists_nonempty(report_path):
        results.append(check("extraction-report.md present", CHECK_PASS))
    else:
        results.append(check("extraction-report.md present", CHECK_WARN,
                              "Not present — run normalize_pdf.py to generate"))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate normalized spec artifacts for gate readiness."
    )
    parser.add_argument("--normalized-dir", required=True,
                        help="Path to .local/spec-cache/{format-id}/{version}/normalized/")
    parser.add_argument("--format-id", required=True,
                        help="Format ID (e.g., fods)")
    parser.add_argument("--gate", type=int, choices=[2, 3, 4, 5, 6, 7],
                        help="Check readiness for a specific gate (optional)")
    args = parser.parse_args()

    normalized_dir = pathlib.Path(args.normalized_dir)
    if not normalized_dir.exists():
        print(f"ERROR: normalized directory not found: {normalized_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\nvalidate_normalized_spec.py — format: {args.format_id}")
    print(f"  Normalized dir: {normalized_dir}")
    if args.gate:
        print(f"  Gate target: {args.gate}")
    print()

    all_checks = []
    fail_count = 0
    warn_count = 0

    # Run all validation suites
    print("--- Source manifest ---")
    manifest_checks, hash_match, _ = validate_source_manifest(normalized_dir)
    all_checks.extend(manifest_checks)

    print("\n--- Text artifacts ---")
    all_checks.extend(validate_text_artifacts(normalized_dir))

    print("\n--- Structure artifacts ---")
    all_checks.extend(validate_structure_artifacts(normalized_dir))

    print("\n--- Citation artifacts ---")
    all_checks.extend(validate_citation_artifacts(normalized_dir))

    print("\n--- Extraction report ---")
    all_checks.extend(validate_extraction_report(normalized_dir))

    print("\n--- Gate readiness ---")
    all_checks.extend(validate_gate_readiness(normalized_dir))

    # Tally
    for c in all_checks:
        if c["result"] == CHECK_FAIL:
            fail_count += 1
        elif c["result"] == CHECK_WARN:
            warn_count += 1

    # Summary
    pass_count = sum(1 for c in all_checks if c["result"] == CHECK_PASS)
    skip_count = sum(1 for c in all_checks if c["result"] == CHECK_SKIP)
    total = len(all_checks)

    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY — {args.format_id}")
    print(f"{'='*60}")
    print(f"  Total checks:  {total}")
    print(f"  PASS:          {pass_count}")
    print(f"  WARN:          {warn_count}")
    print(f"  FAIL:          {fail_count}")
    print(f"  SKIP:          {skip_count}")
    print()

    if fail_count == 0 and warn_count == 0:
        print("Overall: FULLY VALID — all checks pass, no warnings.")
    elif fail_count == 0:
        print(f"Overall: VALID WITH WARNINGS — {warn_count} warning(s). Review before gate use.")
    else:
        print(f"Overall: INVALID — {fail_count} failure(s). Fix before using normalized artifacts.")

    if args.gate:
        gate_warn = ""
        if args.gate >= 4 and not (normalized_dir / "parser-requirements.yaml").exists():
            gate_warn = f"  Gate {args.gate} BLOCKED: parser-requirements.yaml missing."
        if args.gate >= 5 and not (normalized_dir / "verified-facts.yaml").exists():
            gate_warn += f"  Gate {args.gate} NOTE: verified-facts.yaml not yet produced."
        if gate_warn:
            print(gate_warn)

    print()
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
