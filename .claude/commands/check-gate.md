# /check-gate

Verify whether a format has met the criteria for a given acquisition gate.

## Usage

```
/check-gate <format_id> <gate_number>
```

Examples:
- `/check-gate fods 11` — Check FODS Gate 11 readiness
- `/check-gate zst 4` — Check ZST Gate 4 criteria

## What This Command Does

1. **Load gate criteria** — Read `registry/gate11-criteria.yaml` (or per-gate file)
2. **Load format state** — Read `product-capability-matrix/poc-targets.yaml` for the format
3. **Check each criterion** — Evaluate PASS/FAIL/PENDING for each gate requirement
4. **Compute readiness score** — Count passed criteria vs total
5. **Output readiness packet** — Write to `reports/gate<N>/<format_id>-gate<N>-readiness-packet.md`

## Required Inputs

- `format_id` — Format identifier (e.g., `fods`, `fodt`, `zst`)
- `gate_number` — Gate number (1-11; most commonly 4, 8, or 11)

## Gate Criteria Sources

| Gate | Criteria File | Description |
|------|--------------|-------------|
| 1-4 | AGENTS.md §AG4 | POC baseline gates |
| 8 | registry/gate8-criteria.yaml | Commercial readiness |
| 11 | registry/gate11-criteria.yaml | Full commercial release |

## Steps

```
1. Read registry/gate<N>-criteria.yaml
2. Read product-capability-matrix/poc-targets.yaml → find <format_id> section
3. Read reports/gate<N>/<format_id>-gate<N>-readiness-packet.md (if exists)
4. For each criterion:
   a. Check evidence in poc-targets.yaml, evidence bundles, test results
   b. Classify: PASS | FAIL | PENDING | NOT_APPLICABLE
5. Compute: passed_count / total_required_count
6. Classify overall: READY | CONDITIONALLY_READY | NOT_READY
7. Write readiness packet to reports/gate<N>/<format_id>-gate<N>-readiness-packet.md
```

## Output Format

```
# Gate <N> Readiness: <FORMAT_ID>
**Overall:** READY / CONDITIONALLY_READY / NOT_READY
**Score:** X/Y criteria passed

## Criteria Checklist
- [x] C1: Python FOSS package installable from wheel
- [x] C2: All FOSS tests pass (0 failures)
- [ ] C5: .NET commercial package builds clean
...

## Blocking Items
...

## Next Actions
...
```

## Validation

Complete when:
- `reports/gate<N>/<format_id>-gate<N>-readiness-packet.md` exists
- All criteria evaluated (not UNKNOWN)
- Blocking items listed if NOT_READY

## Allowed Paths

- `registry/ — format registry (read-only unless updating registry)`
- `reports/ — acquisition reports (write)`
- `plans/ — acquisition plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation during acquisition
- `src/python/**` — no product source mutation during acquisition
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if all gate criteria cannot be evaluated
- Stop if the approval would be self-signed by the same agent
