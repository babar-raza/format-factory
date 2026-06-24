---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same inputs produce same output; read-only except output file"
loc_budget: "<80 lines"
test_path: "tests/supervisor/test_build_capability_routes.py"
---

# /build-capability-routes

Read `.supervisor/capability-routing-registry.yaml`, verify each route's `preferred_skill_ids`
resolve to registered active skills; flag unresolved routes as MISSING_SKILL_CAPABILITY.

## Purpose

Validate that all routes in the capability routing registry have resolvable skill references.
Broken references indicate registry drift that must be repaired before routing is reliable.

## Steps

1. Read `.supervisor/skill-registry.yaml` — collect all active skill IDs
2. Read `.supervisor/capability-routing-registry.yaml` — iterate routes
3. For each route:
   - If `current_status: MISSING_SKILL_CAPABILITY` → verdict: MISSING_SKILL_CAPABILITY (expected)
   - If any `preferred_skill_ids` not in active skills → verdict: BROKEN_REFERENCE
   - Otherwise → verdict: ROUTE_ACTIVE
4. Write results to `.supervisor/capability-routing-results.yaml`

```bash
python tools/supervisor/build_capability_routes.py
```

## Output

`.supervisor/capability-routing-results.yaml` with:
- `overall_verdict`: PASS | PARTIAL | FAIL
- `total_routes`, `active_routes`, `missing_skill_routes`, `broken_reference_routes`
- `routes[]`: per-route verdict

## Pass Criteria

Zero BROKEN_REFERENCE entries. MISSING_SKILL_CAPABILITY entries are expected (gap tracking).

## Allowed Paths

- `.supervisor/capability-routing-results.yaml` (write)
- `.supervisor/skill-registry.yaml` (read)
- `.supervisor/capability-routing-registry.yaml` (read)

## Forbidden Paths

- `src/**`
- Modifying registries

## Constraints

- Read-only except for output file

## Idempotency Contract

Same registry inputs produce same output. Deterministic — no LLM involvement.

## Error Handling

On registry parse failure: exit non-zero; log to stderr.

## Usage

```
/build-capability-routes
```
