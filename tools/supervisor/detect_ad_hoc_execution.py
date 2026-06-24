"""
detect_ad_hoc_execution.py — Skill 3

Scan tools/supervisor/*.py for scripts not referenced in any skill-registry.yaml
entry's implementation_paths or command_file; classify as GOVERNED vs AD_HOC.

Output: .supervisor/ad-hoc-execution-inventory.yaml
LOC budget: <90 lines
"""
import argparse
import sys
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


def load_registry(registry_path: Path) -> tuple[set, set]:
    """Return (governed_paths, governed_command_files) from skill-registry.yaml."""
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8", errors="replace"))
    governed = set()
    commands = set()
    for skill in data.get("skills", []):
        for p in skill.get("implementation_paths", []):
            governed.add(Path(p).name)
        cf = skill.get("command_file", "")
        if cf:
            commands.add(Path(cf).name)
    return governed, commands


def scan(tools_root: Path, governed: set) -> list[dict]:
    results = []
    for py_file in sorted(tools_root.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        classification = "GOVERNED" if py_file.name in governed else "AD_HOC"
        results.append({
            "file": py_file.name,
            "path": f"tools/supervisor/{py_file.name}",
            "classification": classification,
        })
    return results


def main(output_path: str | None = None) -> None:
    registry_path = _REPO / ".supervisor" / "skill-registry.yaml"
    tools_root = _REPO / "tools" / "supervisor"

    try:
        governed, _ = load_registry(registry_path)
    except Exception as exc:
        out = {"status": "error", "error": str(exc), "entries": []}
        _write(output_path or str(_REPO / ".supervisor" / "ad-hoc-execution-inventory.yaml"), out)
        return

    entries = scan(tools_root, governed)
    ad_hoc = [e for e in entries if e["classification"] == "AD_HOC"]
    governed_count = len(entries) - len(ad_hoc)

    out = {
        "generated_by": "detect_ad_hoc_execution.py",
        "mission_id": "SKILL-FIRST-001",
        "status": "complete",
        "total_files": len(entries),
        "governed_count": governed_count,
        "ad_hoc_count": len(ad_hoc),
        "note": "GOVERNED = referenced in skill-registry.yaml; AD_HOC = not referenced",
        "entries": entries,
    }
    dest = output_path or str(_REPO / ".supervisor" / "ad-hoc-execution-inventory.yaml")
    _write(dest, out)
    print(f"Scanned {len(entries)} files: {governed_count} GOVERNED, {len(ad_hoc)} AD_HOC -> {dest}")


def _write(path: str, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect ad-hoc execution scripts")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
