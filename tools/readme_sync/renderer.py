"""Render deterministic generated README blocks."""

from __future__ import annotations

from datetime import datetime, timezone


def _marker(section_id: str, source: str, timestamp: str | None = None) -> tuple[str, str]:
    ts = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    marker_id = section_id.upper().replace("-", "_")
    return (
        f"<!-- BEGIN:README-{marker_id} generated={ts} source={source} -->",
        f"<!-- END:README-{marker_id} -->",
    )


def _unknown(value) -> str:
    if value in (None, "", []):
        return "unknown"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "unknown"
    return str(value)


def gen_installation(state: dict, timestamp: str | None = None) -> str:
    begin, end = _marker("installation", "package-metadata", timestamp)
    package = state.get("package_name") or f"format-factory-{state['format_id']}"
    if state["track"] == "python":
        command = f"pip install {package}"
    else:
        command = f"dotnet add package {package}"
    return f"{begin}\n```bash\n{command}\n```\n{end}\n"


def gen_package_info(state: dict, timestamp: str | None = None) -> str:
    begin, end = _marker("package_info", "repository-metadata", timestamp)
    rows = [
        ("Format", _unknown(state.get("display_name"))),
        ("Track", _unknown(state.get("track"))),
        ("Package", _unknown(state.get("package_name"))),
        ("Version", _unknown(state.get("version"))),
        ("License", _unknown(state.get("license"))),
        ("Python", _unknown(state.get("requires_python"))),
        (".NET", _unknown(state.get("target_framework"))),
        ("Spec", _unknown(" ".join(str(v) for v in [state.get("spec_body"), state.get("spec_version")] if v))),
        ("QName coverage", f"{state.get('qname_implemented_count', 0)}/{state.get('qname_count', 0)} implemented"),
        ("Source files", _unknown(state.get("source_file_count"))),
        ("Test files", _unknown(state.get("test_file_count"))),
    ]
    table = ["| Field | Value |", "|---|---|"]
    table.extend(f"| {key} | {value} |" for key, value in rows)
    return f"{begin}\n" + "\n".join(table) + f"\n{end}\n"


def gen_public_api(state: dict, timestamp: str | None = None) -> str:
    begin, end = _marker("public_api", "src-python-init", timestamp)
    exports = state.get("public_api_exports") or []
    if not exports:
        body = "- No static public API export list found."
    else:
        body = "\n".join(f"- `{name}`" for name in exports[:80])
    return f"{begin}\n{body}\n{end}\n"


def gen_license(state: dict, timestamp: str | None = None) -> str:
    begin, end = _marker("license", "package-metadata", timestamp)
    return f"{begin}\n{_unknown(state.get('license'))}\n{end}\n"


def generate_blocks(state: dict, timestamp: str | None = None) -> dict[str, str]:
    blocks = {
        "installation": gen_installation(state, timestamp),
        "package_info": gen_package_info(state, timestamp),
    }
    if state.get("track") == "python":
        blocks["public_api"] = gen_public_api(state, timestamp)
    if state.get("license") or state.get("track") == "python":
        blocks["license"] = gen_license(state, timestamp)
    return blocks
