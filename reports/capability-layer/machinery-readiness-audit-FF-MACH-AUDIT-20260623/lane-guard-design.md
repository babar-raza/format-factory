# Lane Guard Design — check_lane_conflict()
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-H | **Requirement:** REQ-LANE-H

## Injection Point
- **File:** tools/supervisor/autonomous_cycle.py
- **Location:** Step 1b (after declaration loading, BEFORE evidence inspection and grading)
- **Rationale:** Catches lane violations BEFORE any work is graded, preventing wasted computation

## Function Design

```python
def check_lane_conflict(declaration: dict, repo_root: Path) -> dict:
    """Preventive lane guard — detects mixed-lane work before grading.

    Returns:
        {"status": "PASS"} or {"status": "FAIL", "reason": str, "violations": list}
    """
    declared_lane = declaration.get("declared_scope", {}).get("lane", "UNKNOWN")
    changed_files = declaration.get("changed_files", [])

    violations = []

    if declared_lane == "MACHINERY":
        # MACHINERY sprints must NOT touch product source
        for f in changed_files:
            if f.startswith("src/python/") or f.startswith("src/net/"):
                violations.append(f"MACHINERY sprint touched product source: {f}")

    elif declared_lane == "PRODUCT":
        # PRODUCT sprints must NOT touch supervisor machinery
        for f in changed_files:
            if f.startswith("tools/supervisor/") and not f.endswith("_test.py"):
                violations.append(f"PRODUCT sprint touched machinery: {f}")

    if violations:
        return {
            "status": "FAIL",
            "reason": "LANE_CONFLICT_DETECTED",
            "violations": violations,
            "declared_lane": declared_lane
        }

    return {"status": "PASS", "declared_lane": declared_lane}
```

## Integration

```python
# In autonomous_cycle.py, after Step 1b declaration loading:
lane_result = check_lane_conflict(declaration, repo_root)
if lane_result["status"] == "FAIL":
    grace_until = policies.get("lanes_grace_period_until", "")
    if grace_until and datetime.now().isoformat() < grace_until:
        print(f"WARNING: Lane conflict (grace period active): {lane_result['reason']}")
    else:
        hard_stops.append(f"LANE_CONFLICT: {lane_result['reason']}")
        # Exit 3 — rework required
```

## Grace Period
- **Config:** .supervisor/policies.yaml → `lanes_grace_period_until: "2026-07-15"`
- **Behavior:** During grace period, lane conflicts are warnings only (not hard stops)
- **After grace period:** Lane conflicts are hard stops that prevent autonomous continuation

## Exit Behavior
- **Exit 3:** Lane conflict detected after grace period → rework required
- **Warning only:** Lane conflict detected during grace period → logged, continue

## Tests Required
1. MACHINERY declaration + src/python/ file → FAIL
2. MACHINERY declaration + tools/supervisor/ file → PASS
3. PRODUCT declaration + tools/supervisor/ file → FAIL
4. PRODUCT declaration + src/python/ file → PASS
5. Grace period active + conflict → warning only (not FAIL)
