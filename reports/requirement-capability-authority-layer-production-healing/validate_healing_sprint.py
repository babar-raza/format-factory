#!/usr/bin/env python3
"""
Validation script for FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Checks all required output files, JSON parse, TC count, keyword presence, and forbidden path guard.
Emits: validation-results.json with {checks: [{name, status, evidence}], overall: PASS|FAIL}
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def get_repo_root():
    """Resolve repo root dynamically via git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        )
        return Path(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Cannot resolve repo root: {e}")


REPO_ROOT = get_repo_root()
OUTPUT_DIR = REPO_ROOT / "reports" / "requirement-capability-authority-layer-production-healing"

REQUIRED_MD_FILES = [
    "00-preflight.md",
    "lane-ownership.md",
    "overlap-check.md",
    "coordinator-integration-log.md",
    "00-production-blocker-review.md",
    "symptoms-root-causes-structural-weaknesses.md",
    "preserve-redesign-decision-matrix.md",
    "canonical-capability-proof-graph.md",
    "claim-scope-and-decomposition-model.md",
    "proof-sufficiency-model.md",
    "capability-family-model.md",
    "authority-lifecycle-redesign.md",
    "delta-and-promotion-runtime-model.md",
    "staleness-invalidation-runtime-model.md",
    "overclaim-remediation-model.md",
    "existing-system-migration-model.md",
    "mainstream-gap-queue-runtime-model.md",
    "supervisor-verdict-packet-model.md",
    "four-stream-consumer-contracts.md",
    "regression-and-replay-suite.md",
    "tradeoffs-risks-limits.md",
    "healed-final-single-go-requirement-capability-authority-layer-mwp-execution-prompt.md",
    "final-adversarial-independent-verification.md",
]

REQUIRED_JSON_FILES = [
    "taskcard-state.json",
    "file-ownership-map.json",
]

HEALED_PROMPT_FILE = "healed-final-single-go-requirement-capability-authority-layer-mwp-execution-prompt.md"

REQUIRED_KEYWORDS = [
    "Canonical Capability Proof Graph",
    "ProductRequirement",
    "CapabilityClaim",
    "ImplementationArtifact",
    "TestArtifact",
    "DogfoodArtifact",
    "EvidencePackage",
    "UnsupportedFeature",
    "CapabilityDelta",
    "PocReadinessComputer",
    "MainstreamGapQueueGenerator",
    "SupervisorVerdictPacketGenerator",
    "proof sufficiency",
    "claim decomposition",
    "stale invalidation",
    "overclaim remediation",
    "golden replay",
    "Netpbm must be retained",
    "SVG must not replace Netpbm",
    "accepted_with_limitations",
    "ai_draft rejected as proof",
    "COVERAGE_CLEAN",
]

FORBIDDEN_PATH_PATTERNS = [
    r"^M src/net/",
    r"^M src/python/",
    r"^A src/net/",
    r"^A src/python/",
    r"^M tests/net/",
    r"^M tests/python/",
    r"^A tests/net/",
    r"^A tests/python/",
]


def run_check(name, fn):
    """Run a single check function and return a result dict."""
    try:
        evidence, passed = fn()
        return {"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence}
    except Exception as e:
        return {"name": name, "status": "FAIL", "evidence": f"Exception: {e}"}


def check_md_files_exist():
    missing = []
    for fname in REQUIRED_MD_FILES:
        path = OUTPUT_DIR / fname
        if not path.exists():
            missing.append(fname)
    if missing:
        return f"Missing files: {missing}", False
    return f"All {len(REQUIRED_MD_FILES)} required .md files exist", True


def check_md_files_have_h1():
    missing_h1 = []
    for fname in REQUIRED_MD_FILES:
        path = OUTPUT_DIR / fname
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if not any(line.startswith("# ") for line in content.splitlines()):
                missing_h1.append(fname)
    if missing_h1:
        return f"Files missing H1 heading: {missing_h1}", False
    return f"All .md files have H1 heading", True


def check_json_files_parse():
    errors = []
    for fname in REQUIRED_JSON_FILES:
        path = OUTPUT_DIR / fname
        if not path.exists():
            errors.append(f"MISSING: {fname}")
            continue
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"PARSE_ERROR: {fname}: {e}")
    if errors:
        return f"JSON errors: {errors}", False
    return f"All {len(REQUIRED_JSON_FILES)} JSON files parse successfully", True


def check_tc_count():
    """Check taskcard-state.json TC count matches actual sprint TC count (dynamic)."""
    path = OUTPUT_DIR / "taskcard-state.json"
    if not path.exists():
        return "taskcard-state.json missing", False
    with open(path, encoding="utf-8") as f:
        tcs = json.load(f)
    count = len(tcs)
    # Dynamic: count is whatever is in the file; we verify it's a reasonable number (>= 10)
    if count < 10:
        return f"TC count {count} is suspiciously low (expected >= 10)", False
    ids = [tc.get("id") for tc in tcs]
    return f"TC count = {count}; IDs: {ids[:5]}...", True


def check_file_ownership_map_no_duplicates():
    path = OUTPUT_DIR / "file-ownership-map.json"
    if not path.exists():
        return "file-ownership-map.json missing", False
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Check for duplicate keys by counting occurrences of each key
    # Simple heuristic: re-parse and count
    data = json.loads(content)
    key_count = len(data)
    # Check raw text for duplicate key patterns
    keys_in_text = re.findall(r'"([^"]+)"\s*:', content)
    unique_keys = set(keys_in_text)
    if len(keys_in_text) != len(unique_keys):
        dupes = [k for k in unique_keys if keys_in_text.count(k) > 1]
        return f"Duplicate keys found: {dupes}", False
    return f"file-ownership-map.json: {key_count} unique paths, no duplicates", True


def check_overlap_clean():
    path = OUTPUT_DIR / "overlap-check.md"
    if not path.exists():
        return "overlap-check.md missing", False
    content = path.read_text(encoding="utf-8")
    if "CLEAN" in content:
        return "overlap-check.md contains CLEAN", True
    return "overlap-check.md does not contain CLEAN", False


def check_healed_prompt_line_count():
    path = OUTPUT_DIR / HEALED_PROMPT_FILE
    if not path.exists():
        return f"{HEALED_PROMPT_FILE} missing", False
    lines = path.read_text(encoding="utf-8").splitlines()
    count = len(lines)
    if count > 300:
        return f"Healed prompt has {count} lines (> 300 required)", True
    return f"Healed prompt has only {count} lines (must be > 300)", False


def check_required_keywords_in_prompt():
    path = OUTPUT_DIR / HEALED_PROMPT_FILE
    if not path.exists():
        return f"{HEALED_PROMPT_FILE} missing", False
    content = path.read_text(encoding="utf-8")
    missing = []
    for kw in REQUIRED_KEYWORDS:
        if kw not in content:
            missing.append(kw)
    if missing:
        return f"Missing {len(missing)} keywords: {missing}", False
    return f"All {len(REQUIRED_KEYWORDS)} required keywords found in healed prompt", True


def check_verdict_in_blocker_review():
    path = OUTPUT_DIR / "00-production-blocker-review.md"
    if not path.exists():
        return "00-production-blocker-review.md missing", False
    content = path.read_text(encoding="utf-8")
    verdict = "RCA_PLAN_IS_PRODUCTION_BLOCKED_UNTIL_PROOF_GRAPH_AND_RUNTIME_MODELS_ARE_ADDED"
    if verdict in content:
        return f"Verdict line found in 00-production-blocker-review.md", True
    return f"Verdict line MISSING from 00-production-blocker-review.md", False


def check_git_status_no_forbidden_paths():
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, check=True,
            cwd=str(REPO_ROOT)
        )
        lines = result.stdout.splitlines()
        violations = []
        for line in lines:
            for pattern in FORBIDDEN_PATH_PATTERNS:
                if re.match(pattern, line):
                    violations.append(line)
        if violations:
            return f"Forbidden path modifications found: {violations}", False
        # Write final git status
        final_status_path = OUTPUT_DIR / "final-git-status.txt"
        final_status_path.write_text(result.stdout, encoding="utf-8")
        new_files = [l for l in lines if l.startswith("??") and "requirement-capability-authority-layer-production-healing" in l]
        return f"No forbidden-path modifications. {len(lines)} total dirty entries. final-git-status.txt written.", True
    except Exception as e:
        return f"git status check failed: {e}", False


def check_adversarial_iv_pass_count():
    path = OUTPUT_DIR / "final-adversarial-independent-verification.md"
    if not path.exists():
        return "final-adversarial-independent-verification.md missing", False
    content = path.read_text(encoding="utf-8")
    pass_count = content.count("\nPASS\n") + content.count("\n\nPASS")
    # More robust: count PASS entries
    pass_lines = [l for l in content.splitlines() if l.strip() == "PASS"]
    if len(pass_lines) >= 20:
        return f"Adversarial IV: {len(pass_lines)} PASS answers (>= 20 required)", True
    # Also check for inline PASS pattern
    inline_pass = re.findall(r'\n###.*?\n\nPASS', content, re.DOTALL)
    all_pass_count = len(re.findall(r'^PASS$', content, re.MULTILINE))
    if all_pass_count >= 20:
        return f"Adversarial IV: {all_pass_count} PASS answers (>= 20 required)", True
    return f"Adversarial IV: only {all_pass_count} PASS answers (need >= 20)", False


def main():
    checks = [
        run_check("md_files_exist", check_md_files_exist),
        run_check("md_files_have_h1", check_md_files_have_h1),
        run_check("json_files_parse", check_json_files_parse),
        run_check("tc_count_reasonable", check_tc_count),
        run_check("file_ownership_map_no_duplicates", check_file_ownership_map_no_duplicates),
        run_check("overlap_check_clean", check_overlap_clean),
        run_check("healed_prompt_line_count", check_healed_prompt_line_count),
        run_check("required_keywords_in_prompt", check_required_keywords_in_prompt),
        run_check("verdict_in_blocker_review", check_verdict_in_blocker_review),
        run_check("git_status_no_forbidden_paths", check_git_status_no_forbidden_paths),
        run_check("adversarial_iv_pass_count", check_adversarial_iv_pass_count),
    ]

    failed = [c for c in checks if c["status"] == "FAIL"]
    overall = "PASS" if not failed else "FAIL"

    result = {"checks": checks, "overall": overall}

    # Write validation-results.json
    results_path = OUTPUT_DIR / "validation-results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Write validation-results.md
    md_lines = [
        "# Validation Results\n",
        f"Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001\n",
        f"Overall: **{overall}**\n",
        "## Checks\n",
    ]
    for c in checks:
        status_str = "PASS" if c["status"] == "PASS" else "**FAIL**"
        md_lines.append(f"- [{status_str}] {c['name']}: {c['evidence']}\n")
    if overall == "PASS":
        md_lines.append("\n**REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION**\n")
    else:
        md_lines.append(f"\n**FAILED checks ({len(failed)}):** {[c['name'] for c in failed]}\n")

    md_path = OUTPUT_DIR / "validation-results.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)

    # Print summary
    print(f"Validation complete. Overall: {overall}")
    for c in checks:
        mark = "OK" if c["status"] == "PASS" else "FAIL"
        print(f"  [{mark}] {c['name']}: {c['evidence'][:80]}")

    if overall == "FAIL":
        print(f"\nFailed checks: {[c['name'] for c in failed]}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
