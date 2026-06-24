"""
build_capability_routes.py — Skill 6

Read capability-routing-registry.yaml, verify each route's preferred_skill_ids
resolve to registered active skills; flag unresolved routes as MISSING_SKILL_CAPABILITY.

Output: .supervisor/capability-routing-results.yaml
LOC budget: <80 lines
"""
import argparse
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


def load_registered_skills(registry_path: Path) -> set[str]:
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8", errors="replace"))
    return {s["skill_id"] for s in data.get("skills", []) if s.get("status") != "deprecated"}


def check_routes(routing_path: Path, registered: set[str]) -> list[dict]:
    data = yaml.safe_load(routing_path.read_text(encoding="utf-8", errors="replace"))
    results = []
    for route in data.get("routes", []):
        rid = route.get("route_id", "<unknown>")
        declared_status = route.get("current_status", "UNKNOWN")
        preferred = route.get("preferred_skill_ids", [])

        unresolved = [s for s in preferred if s not in registered]
        if declared_status == "MISSING_SKILL_CAPABILITY":
            verdict = "MISSING_SKILL_CAPABILITY"
        elif unresolved:
            verdict = "BROKEN_REFERENCE"
        else:
            verdict = "ROUTE_ACTIVE"

        results.append({
            "route_id": rid,
            "declared_status": declared_status,
            "verdict": verdict,
            "preferred_skill_ids": preferred,
            "unresolved_skill_ids": unresolved,
            "gap_id": route.get("gap_id"),
        })
    return results


def main(output_path: str | None = None) -> None:
    registry_path = _REPO / ".supervisor" / "skill-registry.yaml"
    routing_path = _REPO / ".supervisor" / "capability-routing-registry.yaml"

    registered = load_registered_skills(registry_path)
    results = check_routes(routing_path, registered)

    active = sum(1 for r in results if r["verdict"] == "ROUTE_ACTIVE")
    missing = sum(1 for r in results if r["verdict"] == "MISSING_SKILL_CAPABILITY")
    broken = sum(1 for r in results if r["verdict"] == "BROKEN_REFERENCE")

    out = {
        "generated_by": "build_capability_routes.py",
        "mission_id": "SKILL-FIRST-001",
        "total_routes": len(results),
        "active_routes": active,
        "missing_skill_routes": missing,
        "broken_reference_routes": broken,
        "overall_verdict": "FAIL" if broken else ("PARTIAL" if missing else "PASS"),
        "routes": results,
    }
    dest = output_path or str(_REPO / ".supervisor" / "capability-routing-results.yaml")
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(out, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"Checked {len(results)} routes: {active} ACTIVE, {missing} MISSING, {broken} BROKEN -> {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and verify capability routes")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
