"""
spec_parser.py — Parse specification content from vault snapshots.

Produces a structured ParsedSpec with sections, headings, and raw text.
Supports: plain text, Markdown-like sections, and simple key-value formats.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SpecSection:
    section_id: str
    heading: str
    level: int
    content: str
    line_start: int
    line_end: int
    parent_section_id: Optional[str] = None


@dataclass
class ParsedSpec:
    source_id: str
    sha256: str
    format_id: str
    sections: List[SpecSection] = field(default_factory=list)
    raw_text: str = ""
    total_lines: int = 0
    parse_method: str = "auto"
    warnings: List[str] = field(default_factory=list)

    def find_sections_matching(self, keyword: str) -> List[SpecSection]:
        kw = keyword.lower()
        return [s for s in self.sections if kw in s.heading.lower() or kw in s.content.lower()]


def _parse_markdown_sections(lines: List[str], source_id: str) -> List[SpecSection]:
    """Parse Markdown-style headings (# ## ###) into SpecSection objects."""
    sections: List[SpecSection] = []
    current: Optional[Dict[str, Any]] = None
    current_lines: List[str] = []
    section_counter = 0

    def flush(end_line: int) -> None:
        nonlocal current
        if current is not None:
            current["content"] = "\n".join(current_lines).strip()
            current["line_end"] = end_line
            sections.append(SpecSection(**current))
        current = None
        current_lines.clear()

    for i, line in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush(i - 1)
            level = len(m.group(1))
            heading = m.group(2).strip()
            section_counter += 1
            parent_id: Optional[str] = None
            for s in reversed(sections):
                if s.level < level:
                    parent_id = s.section_id
                    break
            current = {
                "section_id": f"{source_id}-s{section_counter:04d}",
                "heading": heading,
                "level": level,
                "content": "",
                "line_start": i,
                "line_end": i,
                "parent_section_id": parent_id,
            }
        else:
            current_lines.append(line)

    flush(len(lines) - 1)
    return sections


def _parse_plain_text_sections(lines: List[str], source_id: str) -> List[SpecSection]:
    """
    Fallback: treat each non-empty block as a section.
    Groups consecutive non-empty lines into paragraphs.
    """
    sections: List[SpecSection] = []
    current_block: List[str] = []
    block_start = 0
    section_counter = 0

    def flush(end_line: int) -> None:
        nonlocal section_counter
        if current_block:
            section_counter += 1
            content = "\n".join(current_block).strip()
            heading = content[:60].split("\n")[0].strip()
            sections.append(SpecSection(
                section_id=f"{source_id}-s{section_counter:04d}",
                heading=heading,
                level=1,
                content=content,
                line_start=block_start,
                line_end=end_line,
            ))
        current_block.clear()

    for i, line in enumerate(lines):
        if line.strip():
            if not current_block:
                block_start = i
            current_block.append(line)
        else:
            flush(i - 1)

    flush(len(lines) - 1)
    return sections


def parse_spec(
    source_id: str,
    sha256: str,
    format_id: str,
    vault_path: str,
) -> ParsedSpec:
    """
    Parse a specification snapshot from the vault.
    Auto-detects content format.
    """
    path = Path(vault_path)
    if not path.exists():
        return ParsedSpec(
            source_id=source_id,
            sha256=sha256,
            format_id=format_id,
            warnings=[f"Vault file not found: {vault_path}"],
            parse_method="failed",
        )

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return ParsedSpec(
            source_id=source_id,
            sha256=sha256,
            format_id=format_id,
            warnings=[f"Read error: {e}"],
            parse_method="failed",
        )

    lines = raw_text.splitlines()
    # Detect format
    heading_lines = sum(1 for l in lines if re.match(r'^#{1,6}\s+', l))
    if heading_lines >= 1:
        sections = _parse_markdown_sections(lines, source_id)
        method = "markdown"
    else:
        sections = _parse_plain_text_sections(lines, source_id)
        method = "plain_text"

    return ParsedSpec(
        source_id=source_id,
        sha256=sha256,
        format_id=format_id,
        sections=sections,
        raw_text=raw_text,
        total_lines=len(lines),
        parse_method=method,
    )


def parse_spec_from_text(
    source_id: str,
    sha256: str,
    format_id: str,
    content: str,
) -> ParsedSpec:
    """Parse specification directly from a text string (e.g., fixture content)."""
    lines = content.splitlines()
    heading_lines = sum(1 for l in lines if re.match(r'^#{1,6}\s+', l))
    if heading_lines >= 1:
        sections = _parse_markdown_sections(lines, source_id)
        method = "markdown"
    else:
        sections = _parse_plain_text_sections(lines, source_id)
        method = "plain_text"

    return ParsedSpec(
        source_id=source_id,
        sha256=sha256,
        format_id=format_id,
        sections=sections,
        raw_text=content,
        total_lines=len(lines),
        parse_method=method,
    )
