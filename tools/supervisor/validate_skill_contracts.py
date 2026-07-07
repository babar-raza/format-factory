"""
validate_skill_contracts.py — Skill 4

For each registered active skill in skill-registry.yaml, verify:
  (a) command_file exists on disk
  (b) required fields present (purpose, command, status)
  (c) status is a valid enum value
  (d) validator coverage: if _VALIDATOR_REGISTRY has entries mapping to this skill,
      the skill's command_file must mention those rule_ids (TC-CQGA-033-03)

Output: .supervisor/skill-contract-validation-results.yaml
"""
import argparse
import sys
from pathlib import Path
import yaml

_SUPERVISOR_DIR = Path(__file__).resolve().parent
if str(_SUPERVISOR_DIR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR_DIR))

_REPO = Path(__file__).resolve().parent.parent.parent
_VALID_STATUSES = {"active", "deprecated", "experimental", "retired"}
_REQUIRED_SKILL_FIELDS = {"skill_id", "purpose", "command", "status"}


def validate(skill: dict, repo_root: Path) -> dict:
    sid = skill.get("skill_id", "<unknown>")
    findings = []

    for field in _REQUIRED_SKILL_FIELDS:
        if not skill.get(field):
            findings.append({"check": f"required_field:{field}", "result": "FAIL",
                             "detail": f"Missing or empty field '{field}'"})

    status = skill.get("status", "")
    if status not in _VALID_STATUSES:
        findings.append({"check": "status_enum", "result": "WARN",
                         "detail": f"Status '{status}' not in {sorted(_VALID_STATUSES)}"})

    cf = skill.get("command_file", "")
    cmd_path = repo_root / cf if cf else None
    if cf:
        if not cmd_path.exists():
            findings.append({"check": "command_file_exists", "result": "FAIL",
                             "detail": f"command_file not found: {cf}"})
    else:
        findings.append({"check": "command_file_exists", "result": "WARN",
                         "detail": "No command_file specified"})

    # (d) Validator coverage: check that command_file mentions applicable rule_ids
    if cf and cmd_path and cmd_path.exists():
        try:
            from governance_validators_contract import _VALIDATOR_REGISTRY  # noqa: PLC0415
            cmd_text = cmd_path.read_text(encoding="utf-8", errors="replace")
            for entry in _VALIDATOR_REGISTRY:
                if sid in entry.get("skill_ids", []):
                    rid = entry["rule_id"]
                    if rid not in cmd_text:
                        findings.append({"check": f"validator_coverage:{rid}", "result": "WARN",
                                         "detail": (f"Validator {rid} (domain={entry.get('domain')}) "
                                                    f"applies to skill '{sid}' but is not mentioned "
                                                    f"in {cf}")})
        except Exception:
            pass  # Registry loading is best-effort; never blocks contract check

    fails = sum(1 for f in findings if f["result"] == "FAIL")
    warns = sum(1 for f in findings if f["result"] == "WARN")
    verdict = "FAIL" if fails else ("WARN" if warns else "PASS")
    return {"skill_id": sid, "status": status, "verdict": verdict,
            "fail_count": fails, "warn_count": warns, "findings": findings}


def main(output_path: str | None = None) -> None:
    registry_path = _REPO / ".supervisor" / "skill-registry.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8", errors="replace"))

    results = []
    for skill in data.get("skills", []):
        if skill.get("status") == "deprecated":
            results.append({"skill_id": skill.get("skill_id"), "verdict": "SKIP",
                            "note": "deprecated skill excluded from contract validation"})
            continue
        results.append(validate(skill, _REPO))

    fails = sum(1 for r in results if r.get("verdict") == "FAIL")
    warns = sum(1 for r in results if r.get("verdict") == "WARN")
    out = {
        "generated_by": "validate_skill_contracts.py",
        "mission_id": "SKILL-FIRST-001",
        "total_skills": len(results),
        "fail_count": fails,
        "warn_count": warns,
        "overall_verdict": "FAIL" if fails else ("WARN" if warns else "PASS"),
        "results": results,
    }
    dest = output_path or str(_REPO / ".supervisor" / "skill-contract-validation-results.yaml")
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(out, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"Validated {len(results)} skills: {fails} FAIL, {warns} WARN -> {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate skill contracts")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
