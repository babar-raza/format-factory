"""
update_claude_instructions.py — Capability Sync Tool 4/7

Splice the generated capability index into CLAUDE.md between stable BEGIN/END markers.
First run: appends section at end of file.
Subsequent runs: replaces content between markers.
Idempotent: no write if content unchanged.
Backs up CLAUDE.md before first modification.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_CLAUDE_MD = _REPO / "CLAUDE.md"
_REGISTRY = _REPO / ".governance" / "capabilities" / "registry.yaml"
_BACKUP_DIR = _REPO / ".local" / "archive"

BEGIN_PREFIX = "<!-- BEGIN:CAPABILITY-INDEX"
END_MARKER = "<!-- END:CAPABILITY-INDEX -->"


def find_marker_bounds(lines: list[str]) -> tuple[int, int] | None:
    """Return (begin_line_idx, end_line_idx) or None if markers absent."""
    begin_idx = end_idx = None
    for i, line in enumerate(lines):
        if BEGIN_PREFIX in line:
            begin_idx = i
        elif END_MARKER in line and begin_idx is not None:
            end_idx = i
            return begin_idx, end_idx
    return None


def splice_section(content: str, new_block: str) -> str:
    """Replace content between markers, or append if markers absent."""
    lines = content.splitlines(keepends=True)
    bounds = find_marker_bounds([l.rstrip('\n').rstrip('\r') for l in lines])
    if bounds is not None:
        begin_idx, end_idx = bounds
        new_lines = lines[: begin_idx] + [new_block + "\n"] + lines[end_idx + 1:]
        return "".join(new_lines)
    else:
        # First run: append at end
        sep = "\n" if content.endswith("\n") else "\n\n"
        return content + sep + new_block + "\n"


def _strip_timestamps(text: str) -> str:
    import re
    return re.sub(r'generated=[^\s>]+', 'generated=STRIPPED', text)


def write_with_backup(path: Path, new_content: str, original_content: str) -> bool:
    """Write new_content to path with backup. Returns True if file was changed."""
    if _strip_timestamps(new_content) == _strip_timestamps(original_content):
        print("NO CHANGE — CLAUDE.md already up to date")
        return False
    # Write backup
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup = _BACKUP_DIR / f"claude-md-pre-sync-{ts}.md"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(original_content, encoding="utf-8")
    path.write_text(new_content, encoding="utf-8")
    print(f"Wrote backup to {backup}; Updated {path.name}")
    return True


def main() -> int:
    import sys as _sys
    if str(_REPO) not in _sys.path:
        _sys.path.insert(0, str(_REPO))

    if not _REGISTRY.exists():
        print("ERROR: Registry not found. Run inventory_capabilities.py first.")
        return 1
    if not _CLAUDE_MD.exists():
        print(f"ERROR: {_CLAUDE_MD} not found.")
        return 1

    registry = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8")) or {}
    from tools.capability_sync.generate_discovery_indexes import generate_claude_index
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_block = generate_claude_index(registry, timestamp)

    original = _CLAUDE_MD.read_text(encoding="utf-8")
    new_content = splice_section(original, new_block)
    write_with_backup(_CLAUDE_MD, new_content, original)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
