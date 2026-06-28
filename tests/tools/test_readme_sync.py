import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.readme_sync.collector import REPO_ROOT, collect_all_formats, collect_format_state
from tools.readme_sync.reconciler import (
    classify_sections,
    maintained_fragments,
    parse_readme,
    render_existing_with_generated,
    strip_timestamps,
    verify_preservation,
)
from tools.readme_sync.renderer import gen_installation, gen_package_info, generate_blocks
from tools.readme_sync.section_schema import (
    DOTNET_COMMERCIAL_SECTIONS,
    DOTNET_MINIMAL_SECTIONS,
    PYTHON_FOSS_SECTIONS,
    get_schema_for_format,
    match_heading,
)
from tools.readme_sync.validator import validate_markers


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")


def test_schema_lookup_python():
    assert get_schema_for_format("fods", "python") is PYTHON_FOSS_SECTIONS


def test_schema_lookup_dotnet_minimal():
    assert get_schema_for_format("html", "dotnet") is DOTNET_MINIMAL_SECTIONS


def test_schema_lookup_dotnet_commercial():
    assert get_schema_for_format("fods", "dotnet") is DOTNET_COMMERCIAL_SECTIONS


def test_match_heading_alias():
    assert match_heading("## Quick Start", PYTHON_FOSS_SECTIONS).section_id == "quick_start"


def test_match_heading_wildcard():
    heading = "## Status: Gate 11 commercial_readiness_in_progress - NOT Release-Ready"
    assert match_heading(heading, DOTNET_COMMERCIAL_SECTIONS).section_id == "status"


def test_collector_fods_python():
    state = collect_format_state("fods", "python")
    assert state["display_name"] == "Flat OpenDocument Spreadsheet"
    assert state["package_name"]
    assert state["version"]
    assert state["qname_count"] >= 1
    assert state["source_file_count"] >= 6
    assert state["test_file_count"] >= 1


def test_collector_fods_dotnet():
    state = collect_format_state("fods", "dotnet")
    assert state["target_framework"] == "net10.0"
    assert "gate_11_status" in state


def test_collector_csv_python():
    state = collect_format_state("csv", "python")
    assert "csv" in state["package_name"].lower()


def test_collect_all_formats_finds_portfolio_readmes():
    assert len(collect_all_formats()) >= 30


def test_parse_frontmatter_preserved_in_preamble():
    sections = parse_readme(_read("src/python/fods/README.md"))
    assert sections[0].heading == ""
    assert sections[0].body.startswith("---")
    assert "artifact_id: fods-python-source-readme" in sections[0].body


def test_parse_csv_sections():
    sections = parse_readme(_read("src/python/csv/README.md"))
    headings = [s.heading for s in sections]
    assert "# Format Factory" in headings[1]
    assert "## Quick Start" in headings


def test_classify_unknown_as_maintained_by_preservation():
    sections = classify_sections(parse_readme("# X\n\n## Weird Local Notes\n\nKeep this.\n"), PYTHON_FOSS_SECTIONS)
    assert sections[-1].classification == "UNKNOWN"
    assert "Keep this." in maintained_fragments("# X\n\n## Weird Local Notes\n\nKeep this.\n", PYTHON_FOSS_SECTIONS)[-1]


def test_renderer_installation_python():
    state = collect_format_state("csv", "python")
    block = gen_installation(state, "STRIPPED")
    assert "pip install" in block
    assert "<!-- BEGIN:README-INSTALLATION" in block


def test_renderer_package_info_table():
    state = collect_format_state("fods", "python")
    block = gen_package_info(state, "STRIPPED")
    assert "| Field | Value |" in block
    assert state["package_name"] in block


def test_render_adds_markers():
    state = collect_format_state("csv", "python")
    rendered = render_existing_with_generated(_read("src/python/csv/README.md"), generate_blocks(state, "STRIPPED"))
    assert "<!-- BEGIN:README-PACKAGE_INFO" in rendered


def test_idempotency_timestamp_stripped():
    original = _read("src/python/fods/README.md")
    state = collect_format_state("fods", "python")
    first = render_existing_with_generated(original, generate_blocks(state, "2026-01-01T00:00:00+00:00"))
    second = render_existing_with_generated(first, generate_blocks(state, "2026-01-02T00:00:00+00:00"))
    assert strip_timestamps(first) == strip_timestamps(second)


def test_preservation_fods_python():
    original = _read("src/python/fods/README.md")
    rendered = render_existing_with_generated(original, generate_blocks(collect_format_state("fods", "python"), "STRIPPED"))
    ok, missing = verify_preservation(original, rendered, get_schema_for_format("fods", "python"))
    assert ok, missing
    assert "Security Notes" in rendered


def test_preservation_csv_python():
    original = _read("src/python/csv/README.md")
    rendered = render_existing_with_generated(original, generate_blocks(collect_format_state("csv", "python"), "STRIPPED"))
    ok, missing = verify_preservation(original, rendered, get_schema_for_format("csv", "python"))
    assert ok, missing
    assert "Class-based API" in rendered


def test_preservation_fods_dotnet():
    original = _read("src/net/fods/README.md")
    rendered = render_existing_with_generated(original, generate_blocks(collect_format_state("fods", "dotnet"), "STRIPPED"))
    ok, missing = verify_preservation(original, rendered, get_schema_for_format("fods", "dotnet"))
    assert ok, missing
    assert "Gate 11 has NOT been approved" in rendered


def test_negative_marker_mismatch_detected():
    result = validate_markers("<!-- BEGIN:README-X generated=now source=t -->\n")
    assert not result.ok
