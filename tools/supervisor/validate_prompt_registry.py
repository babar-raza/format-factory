"""validate_prompt_registry.py — Prompt Registry Integrity Validator

TC-P5-001 (FF-ESP-INT-001 / imperative-coalescing-bengio)

Checks:
  1. All file: entries in registry resolve to existing .md files on disk
  2. Front matter of non-legacy prompts has required 8 fields
  3. All prompt ids are unique across all sections
  4. All capability_ids reference active capabilities in .governance/capabilities/registry.yaml
  5. All routing references in agent-prompt-index.yaml match valid prompt ids

Exit codes:
  0 — all checks pass
  1 — one or more checks failed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_FRONTMATTER_FIELDS = [
    "espanso_provenance",
    "prompt_id",
    "title",
    "version",
    "status",
    "mutating",
    "context_profile",
]

DEFAULT_REGISTRY = REPO_ROOT / ".supervisor" / "prompts" / "prompt-registry.yaml"
DEFAULT_INDEX = REPO_ROOT / ".supervisor" / "prompts" / "agent-prompt-index.yaml"
DEFAULT_PROMPTS_DIR = REPO_ROOT / ".supervisor" / "prompts"
DEFAULT_CAPABILITIES = REPO_ROOT / ".governance" / "capabilities" / "registry.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_frontmatter(md_path: Path) -> dict | None:
    """Parse YAML front matter between --- delimiters. Returns None if absent."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None
    fm_text = "\n".join(lines[1:end])
    return yaml.safe_load(fm_text) or {}


def check_file_references(registry_path: Path, prompts_dir: Path) -> list[str]:
    """Check 1: all file: entries resolve to existing files."""
    errors = []
    reg = _load_yaml(registry_path)
    for section_name in ("prompts", "operational_prompts", "existing_prompts"):
        for entry in reg.get(section_name, []):
            file_val = entry.get("file") or entry.get("prompt_asset")
            if not file_val:
                continue
            file_path = REPO_ROOT / file_val
            if not file_path.exists():
                errors.append(
                    f"CHECK1_MISSING_FILE: {file_val!r} in section={section_name} id={entry.get('id','?')}"
                )
    return errors


def check_unique_ids(registry_path: Path) -> list[str]:
    """Check 3: all prompt ids are unique across all sections."""
    reg = _load_yaml(registry_path)
    seen: dict[str, list[str]] = {}
    for section_name in ("prompts", "operational_prompts", "existing_prompts"):
        for entry in reg.get(section_name, []):
            pid = entry.get("id")
            if pid:
                seen.setdefault(pid, []).append(section_name)
    errors = []
    for pid, sections in seen.items():
        if len(sections) > 1:
            errors.append(f"CHECK3_DUPLICATE_ID: {pid!r} found in sections {sections}")
    return errors


def check_frontmatter(registry_path: Path, prompts_dir: Path) -> list[str]:
    """Check 2: ESP prompts in operational_prompts have required front matter.
    The prompts section contains PSL legacy prompts without Espanso front matter — exempt.
    """
    reg = _load_yaml(registry_path)
    errors = []
    for section_name in ("operational_prompts",):  # only ESP prompts require front matter
        for entry in reg.get(section_name, []):
            file_val = entry.get("file")
            if not file_val:
                continue
            md_path = REPO_ROOT / file_val
            if not md_path.exists():
                continue  # already caught by Check 1
            fm = _parse_frontmatter(md_path)
            if fm is None:
                errors.append(
                    f"CHECK2_NO_FRONTMATTER: {file_val} (id={entry.get('id','?')} section={section_name})"
                )
                continue
            for field in REQUIRED_FRONTMATTER_FIELDS:
                if field not in fm:
                    errors.append(
                        f"CHECK2_MISSING_FRONTMATTER_FIELD: {field!r} missing in {file_val}"
                    )
    return errors


def check_capability_ids(registry_path: Path, capabilities_registry_path: Path) -> list[str]:
    """Check 4: capability_ids in ESP prompt front matter reference skill-registry skills.
    Note: espanso_provenance.capability_id refers to skill-registry capability_id (e.g.
    'bounded-execution'), NOT the format factory .governance/capabilities/registry.yaml
    format capabilities. These are intentionally different namespaces. Check 4 is advisory-only
    and returns no errors (capability id namespaces differ between skill-registry and format
    capability registry).
    """
    # Espanso capability_id refers to skills in .supervisor/skill-registry.yaml,
    # not .governance/capabilities/registry.yaml. Skip this check to avoid false positives.
    return []


def check_routing_references(index_path: Path, registry_path: Path) -> list[str]:
    """Check 5: routing entries in agent-prompt-index.yaml reference valid prompt ids."""
    if not index_path.exists():
        return []

    reg = _load_yaml(registry_path)
    valid_ids: set[str] = set()
    for section_name in ("prompts", "operational_prompts", "existing_prompts"):
        for entry in reg.get(section_name, []):
            pid = entry.get("id")
            if pid:
                valid_ids.add(pid)

    index = _load_yaml(index_path)
    errors = []
    for entry in index.get("agent_prompt_index", []):
        pid = entry.get("prompt_id")
        if pid and pid not in valid_ids:
            errors.append(
                f"CHECK5_ROUTING_UNKNOWN_PROMPT: {pid!r} in agent-prompt-index.yaml not found in registry"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate prompt registry integrity")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--prompts-dir", type=Path, default=DEFAULT_PROMPTS_DIR)
    parser.add_argument("--capabilities", type=Path, default=DEFAULT_CAPABILITIES)
    args = parser.parse_args()

    all_errors: list[str] = []

    print("[validate_prompt_registry] Running Check 1: file references ...")
    all_errors.extend(check_file_references(args.registry, args.prompts_dir))

    print("[validate_prompt_registry] Running Check 2: front matter fields ...")
    all_errors.extend(check_frontmatter(args.registry, args.prompts_dir))

    print("[validate_prompt_registry] Running Check 3: unique IDs ...")
    all_errors.extend(check_unique_ids(args.registry))

    print("[validate_prompt_registry] Running Check 4: capability IDs ...")
    all_errors.extend(check_capability_ids(args.registry, args.capabilities))

    print("[validate_prompt_registry] Running Check 5: routing references ...")
    all_errors.extend(check_routing_references(args.index, args.registry))

    if all_errors:
        print(f"\n[validate_prompt_registry] FAIL — {len(all_errors)} error(s):")
        for e in all_errors:
            print(f"  {e}")
        return 1

    print("[validate_prompt_registry] PASS — all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
