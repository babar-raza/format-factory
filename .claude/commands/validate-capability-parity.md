# /validate-capability-parity

Validate cross-agent capability parity by running P1 (fatal) and P2 (warn) checks against the compiled capability registry.

## What This Command Does

1. **Load registry** — Reads `.governance/capabilities/registry.yaml`.
2. **Run P1 checks (fatal)** — Failures cause exit 1 and block CI.
3. **Run P2 checks (warn)** — Failures are reported but non-fatal.
4. **Emit parity report** — Writes `.governance/capabilities/parity-report.yaml`.
5. **Exit** — 0 if PASS, 1 if FAIL (P1), 0 with WARN output if P2 only.

## When to Use

- To diagnose parity failures without running the full sync
- After manually editing source registries, to check consistency before committing
- When CI `capability-parity` job fails, to see details locally

## Command

```
python tools/capability_sync/run_sync.py --mode validate
```

Or directly:

```
python tools/capability_sync/validate_parity.py
```

## Check Definitions

### P1 Checks (fatal — exit 1 on any failure)

| Check | Description |
|-------|-------------|
| `skill_has_command_file` | Every active skill must have its `command_file` present on disk |
| `command_has_skill` | Every command `.md` file (excluding `_readme`, `command-registry`) must have a matching skill entry |

### P2 Checks (warn — exit 0, verdict WARN)

| Check | Description |
|-------|-------------|
| `command_in_registry` | Every active skill should appear in `command-registry.yaml` |
| `routing_coverage` | Every `preferred_skill_id` in capability-routing-registry must exist in the skill registry |

## Output

- Parity report: `.governance/capabilities/parity-report.yaml`
- Prints per-check PASS / WARN / FAIL lines to stdout
- Final line: `Parity report: PASS|WARN|FAIL (N capabilities)`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS or WARN (no P1 failures) |
| 1 | FAIL (one or more P1 failures) |

## Fixing Failures

- **P1 `skill_has_command_file`**: Create the missing `.claude/commands/<skill-id>.md` file, then re-run.
- **P1 `command_has_skill`**: Add the missing skill entry to `.supervisor/skill-registry.yaml`, then run `/sync-capabilities`.
- **P2 `command_in_registry`**: Run `/sync-skill-command-registry` to auto-repair `command-registry.yaml`.
- **P2 `routing_coverage`**: Fix the dangling `preferred_skill_id` in `.supervisor/capability-routing-registry.yaml`.

## skill_id

validate-capability-parity

## Required Inputs

- `capability_id` — capability identifier from the capability registry
- `target_language` — language target: `python` or `dotnet`

## Allowed Paths

- `tools/capability_sync/validate_parity.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the parity report cannot be produced
- Stop if the execution would modify any file under src/

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
