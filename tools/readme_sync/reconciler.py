"""Parse, classify, and reconcile README sections without losing maintained text."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tools.readme_sync.section_schema import SectionDef, match_heading

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = REPO_ROOT / ".local" / "archive"
BEGIN_RE = re.compile(r"<!-- BEGIN:README-([A-Z0-9_-]+)\b")
END_RE = re.compile(r"<!-- END:README-([A-Z0-9_-]+) -->")
HEADING_RE = re.compile(r"^#{1,3}\s+")


@dataclass
class Section:
    heading: str
    body: str
    line_start: int
    line_end: int


@dataclass
class ClassifiedSection(Section):
    section_id: str
    classification: str
    matched_def: SectionDef | None
    has_markers: bool


def _frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return idx + 1
    return 0


def parse_readme(content: str) -> list[Section]:
    if content == "":
        return [Section("", "", 1, 1)]
    lines = content.splitlines(keepends=True)
    start_scan = _frontmatter_end(lines)
    heading_indexes = [idx for idx, line in enumerate(lines[start_scan:], start=start_scan) if HEADING_RE.match(line)]
    if not heading_indexes:
        return [Section("", content, 1, len(lines))]
    sections: list[Section] = []
    if heading_indexes[0] > 0:
        sections.append(Section("", "".join(lines[: heading_indexes[0]]), 1, heading_indexes[0]))
    else:
        sections.append(Section("", "", 1, 1))
    for pos, idx in enumerate(heading_indexes):
        end = heading_indexes[pos + 1] if pos + 1 < len(heading_indexes) else len(lines)
        sections.append(Section(lines[idx].rstrip("\r\n"), "".join(lines[idx + 1 : end]), idx + 1, end))
    return sections


def classify_sections(sections: list[Section], schema: list[SectionDef]) -> list[ClassifiedSection]:
    classified: list[ClassifiedSection] = []
    for section in sections:
        if not section.heading:
            classified.append(ClassifiedSection(**section.__dict__, section_id="preamble", classification="MAINTAINED", matched_def=None, has_markers=False))
            continue
        matched = match_heading(section.heading, schema)
        has_markers = bool(BEGIN_RE.search(section.body) and END_RE.search(section.body))
        if matched:
            classification = "GENERATED" if has_markers else matched.classification
            section_id = matched.section_id
        else:
            classification = "UNKNOWN"
            section_id = re.sub(r"[^a-z0-9]+", "_", section.heading.lower()).strip("_") or "unknown"
        classified.append(ClassifiedSection(**section.__dict__, section_id=section_id, classification=classification, matched_def=matched, has_markers=has_markers))
    return classified


def generated_marker(section_id: str) -> tuple[str, str]:
    marker_id = section_id.upper().replace("-", "_")
    return f"<!-- BEGIN:README-{marker_id}", f"<!-- END:README-{marker_id} -->"


def strip_timestamps(text: str) -> str:
    return re.sub(r"generated=[^\s>]+", "generated=STRIPPED", text)


def splice_generated_block(content: str, section_id: str, block: str) -> str:
    begin_prefix, end_marker = generated_marker(section_id)
    lines = content.splitlines(keepends=True)
    begin_idx = end_idx = None
    for idx, line in enumerate(lines):
        if begin_prefix in line:
            begin_idx = idx
        elif end_marker in line and begin_idx is not None:
            end_idx = idx
            break
    if begin_idx is None or end_idx is None:
        return content
    return "".join(lines[:begin_idx]) + block.rstrip() + "\n" + "".join(lines[end_idx + 1 :])


def render_existing_with_generated(content: str, generated_blocks: dict[str, str]) -> str:
    from tools.readme_sync.section_schema import PYTHON_FOSS_SECTIONS, match_heading

    # Use a broad schema for in-place generated section conversion. Unknown and
    # maintained sections are copied byte-for-byte.
    sections = parse_readme(content)
    consumed: set[str] = set()
    output: list[str] = []
    for index, section in enumerate(sections):
        if index == 0 and not section.heading:
            output.append(section.body)
            continue
        matched = match_heading(section.heading, PYTHON_FOSS_SECTIONS)
        section_id = matched.section_id if matched else None
        if section_id in generated_blocks:
            if section_id in consumed:
                continue
            output.append(f"{section.heading}\n\n{generated_blocks[section_id].rstrip()}\n\n")
            consumed.add(section_id)
        else:
            output.append(f"{section.heading}\n{section.body}")
    for section_id, block in generated_blocks.items():
        if section_id in consumed:
            continue
        heading = {
            "installation": "Installation",
            "public_api": "Public API",
            "package_info": "Package Info",
            "license": "License",
        }.get(section_id, section_id.replace("_", " ").title())
        prefix = "" if not output or "".join(output).endswith("\n") else "\n"
        output.append(f"{prefix}\n## {heading}\n\n{block.rstrip()}\n")
    return "".join(output).rstrip() + "\n"


def maintained_fragments(content: str, schema: list[SectionDef]) -> list[str]:
    fragments: list[str] = []
    for section in classify_sections(parse_readme(content), schema):
        if section.classification in {"MAINTAINED", "UNKNOWN", "HYBRID"} and not section.has_markers:
            text = (section.heading + "\n" + section.body).strip() if section.heading else section.body.strip()
            if text:
                fragments.append(text)
    return fragments


def verify_preservation(original: str, rendered: str, schema: list[SectionDef]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for fragment in maintained_fragments(original, schema):
        if fragment not in rendered:
            missing.append(fragment.splitlines()[0][:120])
    return not missing, missing


def backup_readme(path: Path, format_id: str, track: str) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup = BACKUP_DIR / f"readme-{format_id}-{track}-pre-sync-{ts}.md"
    counter = 1
    while backup.exists():
        backup = BACKUP_DIR / f"readme-{format_id}-{track}-pre-sync-{ts}-{counter}.md"
        counter += 1
    shutil.copyfile(path, backup)
    return backup
