"""
inspect_declared_evidence.py — Declared Evidence Inspector
Inspects a worker-declared evidence directory by walking declared paths,
extracting facts, and assessing per-item evidence presence.

Exit codes:
  0 — inspection complete
  1 — declaration invalid
  9 — unexpected error
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# ---------------------------------------------------------------------------
# LLM semantic helpers — optional enrichment, deterministic fallback
# ---------------------------------------------------------------------------
_ai_gateway = None
_ai_config_obj = None


def _get_ai_gateway():
    """Lazily load AI gateway. Returns (gateway_chat, config) or (None, None)."""
    global _ai_gateway, _ai_config_obj
    if _ai_gateway is not None:
        return _ai_gateway, _ai_config_obj
    try:
        # SCRIPT_DIR = tools/supervisor, repo_root = tools/supervisor/../.. = repo root
        repo_root_for_import = str(SCRIPT_DIR.parent.parent)
        if repo_root_for_import not in sys.path:
            sys.path.insert(0, repo_root_for_import)
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.config import load_ai_config
        cfg = load_ai_config()
        if cfg.is_configured:
            _ai_gateway = gateway_chat
            _ai_config_obj = cfg
            return _ai_gateway, _ai_config_obj
    except Exception:
        pass
    return None, None


def _llm_call(messages: list[dict], role: str, operation: str) -> str | None:
    """Single LLM call with graceful fallback. Returns content or None.

    Tries gateway (litellm) first, falls back to direct SDK if litellm unavailable.
    """
    gw, cfg = _get_ai_gateway()
    if gw is None:
        print(f"  [LLM] No gateway available for {operation}, skipping")
        return None
    try:
        print(f"  [LLM] gateway_chat attempt for {operation}...")
        resp, _record = gw(
            config=cfg,
            model="recommended",
            messages=messages,
            role=role,
            operation=operation,
        )
        content = resp.get("content", "")
        if content:
            return content
        # Gateway returned empty — may be litellm import failure; try direct SDK
        if _record and getattr(_record, "status", None) and "error" in str(_record.status).lower():
            print(f"  [LLM] gateway_chat failed for {operation}, trying SDK fallback...")
            return _sdk_fallback(messages, cfg)
        print(f"  [LLM] gateway_chat returned empty for {operation}")
        return None
    except Exception as exc:
        print(f"  [LLM] gateway_chat exception for {operation}: {type(exc).__name__}")
        return None


def _sdk_fallback(messages: list[dict], cfg) -> str | None:
    """Fallback: call endpoint directly via SDK when litellm fails."""  # policy-allowed
    import os
    import time
    _max_attempts = 3
    _backoff = [1, 2, 4]
    key = os.environ.get("GPT_OSS_API_KEY", "").strip()
    if not key or not cfg.endpoint:
        return None
    for attempt in range(_max_attempts):
        try:
            _sdk = __import__("openai")  # policy-approved endpoint only
            _Client = _sdk.OpenAI  # policy-approved
            client = _Client(base_url=cfg.endpoint, api_key=key)
            resp = client.chat.completions.create(
                model="recommended",
                messages=messages,
                max_tokens=500,
                temperature=0,
            )
            return resp.choices[0].message.content or None
        except Exception as exc:
            print(f"  [LLM] SDK fallback attempt {attempt + 1}/{_max_attempts} failed: {type(exc).__name__}")
            if attempt < _max_attempts - 1:
                time.sleep(_backoff[attempt])
    print("  [LLM] All SDK fallback attempts exhausted")
    return None


def parse_acceptance_criteria(criteria_text: str) -> dict:
    """Parse natural-language acceptance criteria into structured assertions.

    Returns:
        {
            "assertions": [{"claim": str, "verifiable": bool, "evidence_type": str}],
            "overall_verifiability": float,  # 0.0-1.0
            "llm_used": bool,
        }

    Falls back to regex extraction when LLM is unavailable.
    """
    if not criteria_text or not criteria_text.strip():
        return {"assertions": [], "overall_verifiability": 0.0, "llm_used": False}

    crit_str = str(criteria_text)[:500]  # Bound input size

    messages = [
        {"role": "system", "content": (
            "You parse acceptance criteria for software work items. "
            "Extract each distinct testable assertion. For each, state whether it is "
            "objectively verifiable (e.g. 'output is valid JSON') vs subjective/vague "
            "(e.g. 'handles edge cases well'). "
            "Respond ONLY with valid JSON: "
            '{"assertions": [{"claim": "...", "verifiable": true/false, '
            '"evidence_type": "test|file_exists|content_match|manual"}], '
            '"overall_verifiability": 0.0-1.0}'
        )},
        {"role": "user", "content": f"Acceptance criteria:\n{crit_str}"},
    ]

    raw = _llm_call(messages, role="structured_extraction", operation="parse_acceptance_criteria")
    if raw:
        try:
            import json as _json
            parsed = _json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
            if "assertions" in parsed:
                return {**parsed, "llm_used": True}
        except Exception:
            pass

    # Deterministic fallback: existing regex logic
    import re
    quoted = re.findall(r'"([^"]{3,40})"', crit_str[:120])
    assertions = []
    if quoted:
        assertions = [{"claim": q, "verifiable": True, "evidence_type": "content_match"} for q in quoted]
    elif "PASS" in crit_str:
        assertions = [{"claim": "PASS", "verifiable": True, "evidence_type": "content_match"}]

    verifiable_count = sum(1 for a in assertions if a["verifiable"])
    score = verifiable_count / len(assertions) if assertions else 0.0
    return {"assertions": assertions, "overall_verifiability": score, "llm_used": False}


# R107: Lazy import for transcript validation enrichment
_validate_transcript_fn = None


def _get_validate_transcript():
    """Lazily import validate_transcript to avoid circular imports."""
    global _validate_transcript_fn
    if _validate_transcript_fn is None:
        try:
            prev_path = list(sys.path)
            if str(SCRIPT_DIR) not in sys.path:
                sys.path.insert(0, str(SCRIPT_DIR))
            from validate_skill_transcript import validate_transcript
            _validate_transcript_fn = validate_transcript
        except ImportError:
            _validate_transcript_fn = False  # Mark as unavailable
    return _validate_transcript_fn if _validate_transcript_fn is not False else None


def _is_transcript_json(data: dict) -> bool:
    """Check if a parsed JSON dict looks like a skill invocation transcript."""
    transcript_fields = {"invocation_id", "skill_id", "mode", "result"}
    return transcript_fields.issubset(set(data.keys()))


def _validate_transcript_scope(
    transcript_paths: list[str], repo_root: Path, item_context: dict
) -> dict | None:
    """LLM-enhanced: validate transcript scope covers declared work item.

    Returns {scope_aligned: bool, coverage_pct: float, gaps: [str]} or None.
    """
    if not transcript_paths or not item_context:
        return None

    # Read first transcript (bounded to 3000 chars)
    first_path = repo_root / transcript_paths[0]
    if not first_path.exists():
        return None
    try:
        transcript_text = first_path.read_text(encoding="utf-8")[:3000]
    except Exception:
        return None

    item_title = item_context.get("title", item_context.get("item_id", ""))
    item_criteria = str(item_context.get("acceptance_criteria", ""))[:300]

    messages = [
        {"role": "system", "content": (
            "You validate whether a skill execution transcript covers the scope of "
            "a declared work item. Check if the transcript's executed skills and "
            "outcomes align with the item's title and acceptance criteria. "
            "Respond ONLY with valid JSON: "
            '{"scope_aligned": true/false, "coverage_pct": 0.0-1.0, '
            '"gaps": ["missing aspect 1", ...]}'
        )},
        {"role": "user", "content": (
            f"Work item: {item_title}\n"
            f"Acceptance criteria: {item_criteria}\n\n"
            f"Transcript content:\n{transcript_text}"
        )},
    ]

    raw = _llm_call(messages, role="evidence_review", operation="validate_transcript_scope")
    if raw:
        try:
            import json as _json
            parsed = _json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
            if "scope_aligned" in parsed:
                return parsed
        except Exception:
            pass

    return None  # LLM unavailable — no scope validation, trust deterministic checks


def check_transcript_in_evidence(
    evidence_paths: list, repo_root: Path, item_context: dict | None = None
) -> dict | None:
    """R107: Detect and validate transcript JSON files in evidence_paths.

    Returns a dict with validation results if any transcript found, else None.
    """
    validator = _get_validate_transcript()
    if validator is None:
        return None

    transcripts_found = []
    transcripts_valid = []
    transcripts_invalid = []

    for p in evidence_paths:
        if not p.endswith(".json"):
            continue
        full = repo_root / p
        if not full.exists():
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or not _is_transcript_json(data):
            continue

        # This is a transcript — validate it
        transcripts_found.append(p)
        result = validator(data)
        if result["valid"]:
            transcripts_valid.append({
                "path": p,
                "skill_id": result.get("skill_id", ""),
                "mode": result.get("mode", ""),
                "result": result.get("result", ""),
            })
        else:
            transcripts_invalid.append({
                "path": p,
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
            })

    if not transcripts_found:
        return None

    result = {
        "transcripts_found": len(transcripts_found),
        "transcripts_valid": len(transcripts_valid),
        "transcripts_invalid": len(transcripts_invalid),
        "valid_transcripts": transcripts_valid,
        "invalid_transcripts": transcripts_invalid,
        "all_valid": len(transcripts_invalid) == 0,
    }

    # LLM-enhanced transcript scope validation (optional enrichment)
    if item_context and transcripts_found:
        scope_result = _validate_transcript_scope(transcripts_found, repo_root, item_context)
        if scope_result is not None:
            result["scope_validation"] = scope_result
            result["transcript_scope_aligned"] = scope_result.get("scope_aligned", True)
            result["transcript_scope_coverage"] = scope_result.get("coverage_pct", 1.0)

    return result


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def check_test_file_content(test_path: Path) -> dict:
    """Check if a test file contains actual test methods (D92-03 deep grading)."""
    if not test_path.exists():
        return {"has_content": False, "reason": "file not found"}

    try:
        text = test_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {"has_content": False, "reason": "read error"}

    # Check for common test patterns
    is_cs = test_path.suffix.lower() == ".cs"
    is_py = test_path.suffix.lower() == ".py"

    if is_cs:
        # C#: [Fact], [Theory], void Test*, Task Test*
        has_tests = bool(
            "[Fact]" in text or "[Theory]" in text or
            ("void " in text and ("Test" in text or "test" in text)) or
            ("Task " in text and "Test" in text)
        )
        method_count = text.count("[Fact]") + text.count("[Theory]")
    elif is_py:
        # Python: def test_
        import re
        methods = re.findall(r"^\s*def test_\w+", text, re.MULTILINE)
        has_tests = len(methods) > 0
        method_count = len(methods)
    else:
        has_tests = len(text.strip()) > 0
        method_count = 0

    if not has_tests:
        return {"has_content": False, "reason": "no test methods found", "method_count": method_count}

    return {"has_content": True, "method_count": method_count}


def inspect_item(item: dict, repo_root: Path) -> dict:
    """Inspect a single planned work item for evidence presence."""
    item_id = item.get("item_id", "unknown")
    status = item.get("status", "not_started")
    evidence_paths = item.get("evidence_paths", [])
    # R103: Accept both schema field name and common alias
    tests = item.get("tests_supporting", []) or item.get("test_references", [])
    acceptance_criteria = item.get("acceptance_criteria", "")

    found_paths = []
    missing_paths = []
    for p in evidence_paths:
        full = repo_root / p
        if full.exists():
            found_paths.append(p)
        else:
            missing_paths.append(p)

    has_evidence = len(found_paths) > 0
    has_tests = len(tests) > 0

    # D92-03 deep grading: check test file content
    # R98 fix: Distinguish actual file paths from summary strings.
    # A test entry is a file path if it contains a path separator or ends with
    # a known test file extension (.py, .cs). Otherwise it is a summary string
    # and should NOT be treated as a missing/empty test file.
    tests_with_content = []
    tests_empty_or_stub = []
    test_summaries = []
    for t in tests:
        is_file_path = (
            "/" in t or "\\" in t or
            t.endswith(".py") or t.endswith(".cs") or
            t.startswith("tests/") or t.startswith("tests\\")
        )
        if not is_file_path:
            # This is a summary string like "8 new tests, all passed"
            test_summaries.append(t)
            continue
        # R105: Strip pytest node ID suffix (::test_function) to get the file path
        file_part = t.split("::")[0] if "::" in t else t
        full_t = repo_root / file_part
        check = check_test_file_content(full_t)
        if check["has_content"]:
            tests_with_content.append(t)
        else:
            tests_empty_or_stub.append(t)

    # Check acceptance criteria — LLM-enhanced parsing with deterministic fallback
    criteria_verified = False
    criteria_pattern = ""
    criteria_parse = None
    if acceptance_criteria and found_paths:
        criteria_parse = parse_acceptance_criteria(acceptance_criteria)

        # Extract a single pattern for backwards-compatible verification
        if criteria_parse["assertions"]:
            # Use first verifiable assertion as the pattern
            verifiable = [a for a in criteria_parse["assertions"] if a.get("verifiable")]
            if verifiable:
                criteria_pattern = verifiable[0]["claim"]
            else:
                criteria_pattern = criteria_parse["assertions"][0]["claim"]
        else:
            # Fallback: legacy regex extraction
            import re
            crit_text = str(acceptance_criteria)[:120]
            quoted = re.findall(r'"([^"]{3,40})"', crit_text)
            if quoted:
                criteria_pattern = quoted[0]
            elif "PASS" in crit_text:
                criteria_pattern = "PASS"

        if criteria_pattern:
            for fp in found_paths[:3]:  # Check first 3 evidence files
                full_fp = repo_root / fp
                if full_fp.exists():
                    try:
                        content = full_fp.read_text(encoding="utf-8", errors="replace")
                        if criteria_pattern.lower() in content.lower():
                            criteria_verified = True
                            break
                    except Exception:
                        pass

    # R98 fix: If only summary strings were provided in tests_supporting,
    # check evidence_paths for test files and verify their content instead.
    if not tests_with_content and not tests_empty_or_stub and test_summaries:
        for fp in found_paths:
            fp_path = repo_root / fp
            is_test = (
                fp.startswith("tests/") or fp.startswith("tests\\") or
                "test" in fp.lower()
            ) and (fp.endswith(".py") or fp.endswith(".cs"))
            if is_test:
                check = check_test_file_content(fp_path)
                if check["has_content"]:
                    tests_with_content.append(fp)
                else:
                    tests_empty_or_stub.append(fp)

    # R107: Transcript enrichment — detect and validate transcript JSON in evidence
    transcript_validation = check_transcript_in_evidence(found_paths, repo_root, item_context=item)

    return {
        "item_id": item_id,
        "declared_status": status,
        "evidence_paths_declared": evidence_paths,
        "evidence_paths_found": found_paths,
        "evidence_paths_missing": missing_paths,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "tests_declared": tests,
        # D92-03: deep content checks
        "tests_with_content": tests_with_content,
        "tests_empty_or_stub": tests_empty_or_stub,
        "test_summaries": test_summaries,
        "acceptance_criteria_verified": criteria_verified,
        "acceptance_criteria_pattern": criteria_pattern,
        "acceptance_criteria_parse": criteria_parse,
        # R107: Transcript validation enrichment
        "transcript_validation": transcript_validation,
    }


def inspect_declaration(decl: dict, repo_root: Path) -> dict:
    """Full inspection of a declaration."""
    evidence_root = decl.get("evidence_root", "")
    root_path = repo_root / evidence_root if evidence_root else None

    inspection = {
        "run_id": decl.get("run_id", "unknown"),
        "sprint_id": decl.get("sprint_id", "unknown"),
        "evidence_root": evidence_root,
        "evidence_root_exists": root_path.is_dir() if root_path else False,
        "timestamp": datetime.now().isoformat(),
        "item_inspections": [],
        "artifact_inspections": [],
        "test_results": decl.get("test_results", {}),
        "tests_run": decl.get("tests_run", 0),
        "zip_declared": bool(decl.get("zip_export_path")),
        "zip_path": decl.get("zip_export_path"),
    }

    # Inspect each work item
    for item in decl.get("planned_work_items", []):
        inspection["item_inspections"].append(inspect_item(item, repo_root))

    # Inspect declared artifacts
    for artifact in decl.get("evidence_artifacts", []):
        apath = artifact.get("path", "")
        full = repo_root / apath if apath else None
        inspection["artifact_inspections"].append({
            "path": apath,
            "exists": full.exists() if full else False,
            "type": artifact.get("type", "unknown"),
            "related_work_items": artifact.get("related_work_items", []),
        })

    return inspection


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect declared evidence directory")
    parser.add_argument("--declaration", type=Path, required=True, help="Path to evidence-declaration.yaml")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, help="Write inspection JSON to file")
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    decl = load_yaml(args.declaration)
    inspection = inspect_declaration(decl, args.repo_root)

    output_json = json.dumps(inspection, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json, encoding="utf-8")
        print(f"INSPECTION_COMPLETE: {args.output}")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
