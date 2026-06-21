"""ingest_review_findings.py — Parse reviews/src/ findings into taskcard templates and gap-ledger entries.

Reads reviews/src/next_agent_handoff.md (TC-001 through TC-008 entries) and
outputs taskcard file templates and gap-ledger JSON entries to stdout.

Usage:
  python tools/spec/ingest_review_findings.py --output-taskcards
  python tools/spec/ingest_review_findings.py --output-gap-ledger
  python tools/spec/ingest_review_findings.py --output-taskcards --output-gap-ledger
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
REVIEWS_DIR = REPO_ROOT / "reviews" / "src"
HANDOFF_FILE = REVIEWS_DIR / "next_agent_handoff.md"

# Template for gap-ledger entries
_GAP_ENTRY_TEMPLATE = {
    "format": "FODT",
    "product_type": "foss",
    "capability_name": "QNameRegistry",
    "current_state": "not_started",
    "gap_type": "missing_spec_model_layer",
    "status": "open",
    "blocks_poc": False,
    "blocks_readiness": True,
    "commercial_impact": "HIGH",
    "foss_impact": "HIGH",
    "priority": "P1",
    "owning_lane": "SRC-REVIEW",
    "blockers": [],
    "notes": "Ingested from reviews/src/next_agent_handoff.md",
    "spec_facts": ["FACT-FODT-001"],
}


def _parse_tc_sections(content: str) -> list[dict]:
    """Parse TC-001 through TC-008 sections from handoff document."""
    # Find lines starting with ## TC- or ### TC-
    sections: list[dict] = []
    current: dict | None = None
    lines = content.splitlines()

    for line in lines:
        m = re.match(r"^#{1,3}\s+(TC-\d+[:\s].+)$", line)
        if m:
            if current:
                sections.append(current)
            title = m.group(1).strip()
            tc_num = re.match(r"TC-(\d+)", title)
            current = {
                "tc_id": f"TC-{tc_num.group(1)}" if tc_num else "TC-XXX",
                "title": title,
                "body_lines": [],
            }
        elif current is not None:
            current["body_lines"].append(line)

    if current:
        sections.append(current)

    return sections


def _make_taskcard_content(section: dict, idx: int) -> str:
    """Generate taskcard markdown content for a TC section."""
    tc_id = section["tc_id"]
    title = section["title"]
    body = "\n".join(section["body_lines"]).strip()
    gap_id = f"GAP-QNAME-FODT-{idx + 1:03d}"

    return f"""# TC-SRC-REVIEW-{idx + 1:03d}: {title}

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: none
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: {gap_id}

## Source

Ingested from `reviews/src/next_agent_handoff.md` — {tc_id}

## Original Content

{body}

## Completion Criteria

All steps in the original TC completed and verified.
"""


def _make_gap_entry(section: dict, idx: int) -> dict:
    """Generate a gap-ledger entry for a TC section."""
    gap_id = f"GAP-QNAME-FODT-{idx + 1:03d}"
    tc_src = f"TC-SRC-REVIEW-{idx + 1:03d}"
    entry = dict(_GAP_ENTRY_TEMPLATE)
    entry["gap_id"] = gap_id
    entry["suggested_taskcard"] = tc_src
    entry["suggested_pilot"] = f"CAP-PILOT-QNAME-FODT-{idx + 1}"
    entry["suggested_verification"] = f"python tools/spec/validate_spec_registry.py shared/qname-registry/fodt.yaml"
    entry["recurrence_prevention"] = "V43 enforces registry entry before any Spec/ class committed"
    entry["related_capability_id"] = f"FODT-SPEC-PARITY-{idx + 1:03d}"
    entry["notes"] = f"Ingested from reviews/src/next_agent_handoff.md — {section['tc_id']}"
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest reviews/src/next_agent_handoff.md into taskcard templates and gap-ledger entries"
    )
    parser.add_argument("--output-taskcards", action="store_true", help="Print taskcard markdown templates to stdout")
    parser.add_argument("--output-gap-ledger", action="store_true", help="Print gap-ledger JSON entries to stdout")
    parser.add_argument("--handoff-file", default=None, help="Override handoff file path")
    args = parser.parse_args(argv)

    if not args.output_taskcards and not args.output_gap_ledger:
        parser.print_help()
        return 1

    handoff = Path(args.handoff_file) if args.handoff_file else HANDOFF_FILE

    if not handoff.exists():
        print(f"ERROR: Handoff file not found: {handoff}", file=sys.stderr)
        return 2

    content = handoff.read_text(encoding="utf-8")
    sections = _parse_tc_sections(content)

    if not sections:
        print("WARN: No TC-* sections found in handoff file", file=sys.stderr)
        return 1

    if args.output_taskcards:
        for idx, section in enumerate(sections):
            print(f"\n--- TASKCARD: TC-SRC-REVIEW-{idx + 1:03d} ---")
            print(_make_taskcard_content(section, idx))

    if args.output_gap_ledger:
        entries = [_make_gap_entry(section, idx) for idx, section in enumerate(sections)]
        print(json.dumps(entries, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
