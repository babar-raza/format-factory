"""Validate Claude command files (.claude/commands/*.md) for completeness.

Checks every command file for required sections:
- Purpose / description (title + intro paragraph)
- Required inputs / usage
- Steps / execution flow
- Allowed paths
- Forbidden paths
- Stop conditions / constraints
- Evidence / output format
- Validation section
- Rollback instructions
- Transcript requirement (explicit mention of transcript output)
- Sample invocation
- Stream boundary (must not cross product tracks)
- Changelog

Also cross-references the skill registry to detect orphan commands
and missing command files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
DEFAULT_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

# Files to skip (not governed skills)
SKIP_FILES = {"_readme.md"}

# Required sections and their detection patterns (heading text or content keywords)
REQUIRED_SECTIONS = {
    "purpose": {
        "description": "Purpose or description (title heading + intro)",
        "heading_patterns": [r"^#\s+/"],  # Title like "# /add-dotnet-api"
        "content_patterns": [],
        "severity": "error",
    },
    "inputs": {
        "description": "Required inputs or usage section",
        "heading_patterns": [
            r"(?i)##\s+required\s+inputs",
            r"(?i)##\s+usage",
            r"(?i)##\s+what\s+this\s+skill\s+does",
        ],
        "content_patterns": [],
        "severity": "error",
    },
    "steps": {
        "description": "Step-by-step execution flow",
        "heading_patterns": [
            r"(?i)##\s+steps",
            r"(?i)##\s+what\s+this\s+skill\s+does",
        ],
        "content_patterns": [r"^\d+\.\s"],  # Numbered list items
        "severity": "error",
    },
    "allowed_paths": {
        "description": "Allowed paths section",
        "heading_patterns": [r"(?i)##\s+allowed\s+paths"],
        "content_patterns": [],
        "severity": "error",
    },
    "forbidden_paths": {
        "description": "Forbidden paths section",
        "heading_patterns": [r"(?i)##\s+forbidden\s+paths"],
        "content_patterns": [],
        "severity": "error",
    },
    "stop_conditions": {
        "description": "Stop conditions or constraints",
        "heading_patterns": [
            r"(?i)##\s+stop\s+conditions",
            r"(?i)##\s+constraints",
        ],
        "content_patterns": [],
        "severity": "error",
    },
    "evidence_output": {
        "description": "Evidence or output format section",
        "heading_patterns": [
            r"(?i)##\s+evidence",
            r"(?i)##\s+output\s+format",
        ],
        "content_patterns": [],
        "severity": "error",
    },
    "validation": {
        "description": "Validation section",
        "heading_patterns": [r"(?i)##\s+validation"],
        "content_patterns": [],
        "severity": "warning",
    },
    "rollback": {
        "description": "Rollback instructions",
        "heading_patterns": [r"(?i)##\s+rollback"],
        "content_patterns": [],
        "severity": "warning",
    },
    "transcript_requirement": {
        "description": "Transcript output requirement (keyword mention)",
        "heading_patterns": [],
        "content_patterns": [r"(?i)transcript"],
        "severity": "warning",
    },
    "sample_invocation": {
        "description": "Sample invocation or usage block",
        "heading_patterns": [
            r"(?i)##\s+sample\s+invocation",
            r"(?i)##\s+usage",
        ],
        "content_patterns": [r"```"],  # Code block as fallback
        "severity": "warning",
    },
    "changelog": {
        "description": "Changelog section",
        "heading_patterns": [r"(?i)##\s+changelog"],
        "content_patterns": [],
        "severity": "warning",
    },
}

# Frontmatter fields
REQUIRED_FRONTMATTER = {"version", "last-updated"}
OPTIONAL_FRONTMATTER = {"phase-available", "gate-required", "generated_by", "visibility", "created-by"}


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()
    fm: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm, body


def validate_command_file(path: Path) -> dict:
    """Validate a single command file and return findings."""
    errors: list[str] = []
    warnings: list[str] = []
    sections_found: list[str] = []
    sections_missing: list[str] = []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        return {
            "file": path.name,
            "valid": False,
            "errors": [f"Cannot read: {exc}"],
            "warnings": [],
            "sections_found": [],
            "sections_missing": list(REQUIRED_SECTIONS.keys()),
            "frontmatter": {},
        }

    frontmatter, body = _parse_frontmatter(content)

    # Check frontmatter
    for field in REQUIRED_FRONTMATTER:
        if field not in frontmatter:
            warnings.append(f"Missing frontmatter field: {field}")

    # Check each required section
    for section_id, spec in REQUIRED_SECTIONS.items():
        found = False

        # Check heading patterns
        for pattern in spec["heading_patterns"]:
            if re.search(pattern, content, re.MULTILINE):
                found = True
                break

        # Check content patterns if heading not found
        if not found:
            for pattern in spec["content_patterns"]:
                if re.search(pattern, content, re.MULTILINE):
                    found = True
                    break

        if found:
            sections_found.append(section_id)
        else:
            sections_missing.append(section_id)
            msg = f"Missing section: {spec['description']}"
            if spec["severity"] == "error":
                errors.append(msg)
            else:
                warnings.append(msg)

    # Check that the file isn't trivially short
    line_count = len(body.splitlines())
    if line_count < 10:
        errors.append(f"Command file too short ({line_count} lines, min 10)")

    # Check for gate/registry authority claims (forbidden)
    if re.search(r"(?i)gate.*(approved|closed|passed)", body):
        warnings.append("Command file contains gate status claims (should be in registry)")

    return {
        "file": path.name,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "section_count": len(sections_found),
        "section_total": len(REQUIRED_SECTIONS),
        "frontmatter": frontmatter,
    }


def cross_reference_registry(
    command_results: dict[str, dict], registry_path: Path
) -> tuple[list[str], list[str]]:
    """Cross-reference command files against the skill registry."""
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        errors.append(f"Registry not found: {registry_path}")
        return errors, warnings

    try:
        text = registry_path.read_text(encoding="utf-8")
        if yaml is not None:
            data = yaml.safe_load(text)
        else:
            raise ImportError("PyYAML required")
    except Exception as exc:
        errors.append(f"Cannot load registry: {exc}")
        return errors, warnings

    skills = data.get("skills", [])
    registry_commands: dict[str, str] = {}  # command_file -> skill_id
    for skill in skills:
        cf = skill.get("command_file", "")
        sid = skill.get("skill_id", "")
        if cf:
            registry_commands[cf] = sid

    # Check for orphan commands (exist on disk but not in registry)
    for name, result in command_results.items():
        rel_path = f".claude/commands/{name}"
        if rel_path not in registry_commands:
            warnings.append(f"Orphan command (not in registry): {name}")

    # Check for missing commands (in registry but no file on disk)
    for cf, sid in registry_commands.items():
        filename = Path(cf).name
        if filename not in command_results:
            status_in_registry = None
            for s in skills:
                if s.get("skill_id") == sid:
                    status_in_registry = s.get("status")
                    break
            if status_in_registry in ("draft", "deprecated", "deferred"):
                warnings.append(f"Registry skill '{sid}' references missing command (acceptable for {status_in_registry}): {cf}")
            else:
                errors.append(f"Registry skill '{sid}' references missing command: {cf}")

    return errors, warnings


def validate_all(
    commands_dir: Path, registry_path: Path
) -> dict:
    """Validate all command files and cross-reference with registry."""
    all_errors: list[str] = []
    all_warnings: list[str] = []
    command_results: dict[str, dict] = {}

    if not commands_dir.exists():
        return {
            "valid": False,
            "errors": [f"Commands directory not found: {commands_dir}"],
            "warnings": [],
            "commands": {},
            "summary": {},
        }

    md_files = sorted(commands_dir.glob("*.md"))
    for md in md_files:
        if md.name in SKIP_FILES:
            continue
        result = validate_command_file(md)
        command_results[md.name] = result
        for err in result["errors"]:
            all_errors.append(f"[{md.name}] {err}")
        for warn in result["warnings"]:
            all_warnings.append(f"[{md.name}] {warn}")

    # Cross-reference with registry
    xref_errors, xref_warnings = cross_reference_registry(
        command_results, registry_path
    )
    all_errors.extend(xref_errors)
    all_warnings.extend(xref_warnings)

    # Summary
    total = len(command_results)
    passing = sum(1 for r in command_results.values() if r["valid"])
    fully_complete = sum(
        1
        for r in command_results.values()
        if r["valid"] and not r["sections_missing"]
    )

    return {
        "valid": not all_errors,
        "errors": all_errors,
        "warnings": all_warnings,
        "commands": command_results,
        "summary": {
            "total_commands": total,
            "passing": passing,
            "failing": total - passing,
            "fully_complete": fully_complete,
            "total_sections_possible": len(REQUIRED_SECTIONS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commands-dir", type=Path, default=COMMANDS_DIR,
        help="Directory containing .claude/commands/*.md files",
    )
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_REGISTRY,
        help="Path to skill-registry.yaml for cross-reference",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print JSON result",
    )
    parser.add_argument(
        "--file", type=Path, default=None,
        help="Validate a single command file instead of all",
    )
    args = parser.parse_args()

    if args.file:
        result = validate_command_file(args.file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            verdict = "PASS" if result["valid"] else "FAIL"
            print(f"COMMAND_FILE_VALIDATION: {verdict} — {result['file']}")
            print(f"  sections: {result['section_count']}/{result['section_total']}")
            if result["sections_missing"]:
                print(f"  missing: {', '.join(result['sections_missing'])}")
            for err in result["errors"]:
                print(f"  ERROR: {err}")
            for warn in result["warnings"]:
                print(f"  WARNING: {warn}")
        return 0 if result["valid"] else 1

    result = validate_all(args.commands_dir, args.registry)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        verdict = "PASS" if result["valid"] else "FAIL"
        summary = result["summary"]
        print(f"COMMAND_FILE_VALIDATION: {verdict}")
        print(
            f"  total={summary['total_commands']} "
            f"passing={summary['passing']} "
            f"failing={summary['failing']} "
            f"fully_complete={summary['fully_complete']}"
        )
        for err in result["errors"]:
            print(f"  ERROR: {err}")
        for warn in result["warnings"]:
            print(f"  WARNING: {warn}")

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
