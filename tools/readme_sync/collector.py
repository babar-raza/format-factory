"""Collect README-relevant format state from repository metadata."""

from __future__ import annotations

import ast
import re
import sys
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}


def _read_format_registry(format_id: str) -> dict | None:
    data = _read_yaml(REPO_ROOT / "registry" / "format-registry.yaml")
    for entry in data.get("formats", []):
        if entry.get("format_id") == format_id:
            gates = entry.get("gates", {}) or {}
            return {
                "display_name": entry.get("display_name"),
                "family": entry.get("family"),
                "extensions": entry.get("extensions") or [],
                "mime_type": entry.get("mime_type"),
                "spec_body": entry.get("spec_body"),
                "spec_version": entry.get("spec_version"),
                "spec_url": entry.get("spec_url"),
                "gate_1_status": (gates.get("gate_1") or {}).get("status"),
                "gate_11_status": (gates.get("gate_11") or {}).get("status") or entry.get("gate_11_status"),
            }
    return None


def _read_pyproject(format_id: str) -> dict | None:
    path = REPO_ROOT / "src" / "python" / format_id / "pyproject.toml"
    if not path.exists():
        return None
    with path.open("rb") as handle:
        project = (tomllib.load(handle) or {}).get("project", {})
    license_value = project.get("license")
    if isinstance(license_value, dict):
        license_text = license_value.get("text") or license_value.get("file")
    else:
        license_text = license_value
    return {
        "package_name": project.get("name"),
        "version": project.get("version"),
        "description": project.get("description"),
        "license": license_text,
        "requires_python": project.get("requires-python"),
        "dependencies": project.get("dependencies") or [],
    }


def _strip_xml_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _read_csproj(format_id: str) -> dict | None:
    files = sorted((REPO_ROOT / "src" / "net" / format_id).glob("*.csproj"))
    if not files:
        return None
    root = ET.parse(files[0]).getroot()
    props: dict[str, str] = {}
    deps: list[str] = []
    for elem in root.iter():
        name = _strip_xml_namespace(elem.tag)
        if name in {"Version", "AssemblyName", "TargetFramework", "Description", "PackageId"} and elem.text:
            props[name] = elem.text.strip()
        if name == "PackageReference":
            inc = elem.attrib.get("Include")
            ver = elem.attrib.get("Version")
            deps.append(f"{inc} {ver}".strip() if ver else inc or "")
    return {
        "package_name": props.get("PackageId") or props.get("AssemblyName") or files[0].stem,
        "version": props.get("Version"),
        "description": props.get("Description"),
        "target_framework": props.get("TargetFramework"),
        "dependencies": [d for d in deps if d],
    }


def _read_qname_registry(format_id: str) -> dict:
    data = _read_yaml(REPO_ROOT / "shared" / "qname-registry" / f"{format_id}.yaml")
    if isinstance(data, list):
        entries = data
    else:
        entries = data.get("entries") or data.get("qnames") or []
    if isinstance(entries, dict):
        entries = list(entries.values())
    implemented = sum(1 for item in entries if isinstance(item, dict) and item.get("status") == "implemented")
    return {"qname_count": len(entries), "qname_implemented_count": implemented}


def _count_source_files(format_id: str, track: str) -> int:
    suffix = ".py" if track == "python" else ".cs"
    base = REPO_ROOT / "src" / ("python" if track == "python" else "net") / format_id
    if not base.exists():
        return 0
    skipped = {"__pycache__", "build", "bin", "obj"}
    return sum(1 for p in base.rglob(f"*{suffix}") if not any(part in skipped or part.endswith(".egg-info") for part in p.parts))


def _count_test_files(format_id: str, track: str) -> int:
    base = REPO_ROOT / "tests" / ("python" if track == "python" else "net") / format_id
    if not base.exists():
        return 0
    pattern = "test_*.py" if track == "python" else "*Tests.cs"
    return sum(1 for _ in base.rglob(pattern))


def _read_python_exports(format_id: str) -> tuple[list[str], dict]:
    path = REPO_ROOT / "src" / "python" / format_id / "__init__.py"
    if not path.exists():
        return [], {}
    text = path.read_text(encoding="utf-8", errors="replace")
    meta: dict[str, str] = {}
    for name in ("__version__", "__track__", "__commercial_ready__", "__capability_level__"):
        match = re.search(rf"^{name}\s*=\s*(.+)$", text, flags=re.M)
        if match:
            meta[name.strip("_")] = match.group(1).strip().strip("\"'")
    all_match = re.search(r"^__all__\s*=\s*(.+?)(?:\n\S|\Z)", text, flags=re.M | re.S)
    if not all_match:
        return [], meta
    try:
        value = ast.literal_eval(all_match.group(1).strip())
    except Exception:
        return ["(dynamic)"], meta
    return [str(v) for v in value] if isinstance(value, list) else ["(dynamic)"], meta


def collect_format_state(format_id: str, track: str) -> dict:
    trk = track.lower()
    registry = _read_format_registry(format_id) or {}
    package = _read_pyproject(format_id) if trk == "python" else _read_csproj(format_id)
    package = package or {}
    exports, py_meta = _read_python_exports(format_id) if trk == "python" else ([], {})
    return {
        "format_id": format_id,
        "track": trk,
        "display_name": registry.get("display_name") or format_id.upper(),
        "family": registry.get("family"),
        "extensions": registry.get("extensions") or [],
        "mime_type": registry.get("mime_type"),
        "spec_body": registry.get("spec_body"),
        "spec_version": registry.get("spec_version"),
        "spec_url": registry.get("spec_url"),
        "gate_1_status": registry.get("gate_1_status"),
        "gate_11_status": registry.get("gate_11_status"),
        "package_name": package.get("package_name"),
        "version": package.get("version"),
        "description": package.get("description"),
        "license": package.get("license"),
        "requires_python": package.get("requires_python"),
        "target_framework": package.get("target_framework"),
        "dependencies": package.get("dependencies") or [],
        **_read_qname_registry(format_id),
        "source_file_count": _count_source_files(format_id, trk),
        "test_file_count": _count_test_files(format_id, trk),
        "public_api_exports": exports,
        "python_version_meta": py_meta.get("version"),
        "python_track_meta": py_meta.get("track"),
        "python_commercial_ready": py_meta.get("commercial_ready"),
    }


def collect_all_formats() -> list[dict]:
    states: list[dict] = []
    for track, root in (("python", REPO_ROOT / "src" / "python"), ("dotnet", REPO_ROOT / "src" / "net")):
        for readme in sorted(root.glob("*/README.md")):
            if readme.parent.name.startswith("format_factory_") or readme.parent.name == "_shared":
                continue
            states.append(collect_format_state(readme.parent.name, track))
    return states


if __name__ == "__main__":
    import json

    json.dump(collect_all_formats(), sys.stdout, indent=2)
    print()
