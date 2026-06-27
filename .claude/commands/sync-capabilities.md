# /sync-capabilities

Run the full capability sync pipeline: inventory source registries → validate parity → update CLAUDE.md and AGENTS.md → confirm no drift.

## What This Command Does

1. **Inventory** — Reads `.supervisor/skill-registry.yaml`, `.claude/commands/command-registry.yaml`, and `.supervisor/capability-routing-registry.yaml`; compiles `.governance/capabilities/registry.yaml`.
2. **Validate parity** — Runs P1 (fatal) and P2 (warn) parity checks; emits `.governance/capabilities/parity-report.yaml`.
3. **Update CLAUDE.md** — Splices a generated capability index between stable `<!-- BEGIN:CAPABILITY-INDEX -->` / `<!-- END:CAPABILITY-INDEX -->` markers.
4. **Update AGENTS.md** — Splices a generated capability discovery table between stable `<!-- BEGIN:CAPABILITY-DISCOVERY -->` / `<!-- END:CAPABILITY-DISCOVERY -->` markers.
5. **Drift check** — Confirms the committed registry and adapter sections match the freshly computed snapshot.

## When to Use

- After adding or modifying any skill in `.supervisor/skill-registry.yaml`
- After adding or modifying any command file in `.claude/commands/`
- After changing routing in `.supervisor/capability-routing-registry.yaml`
- At the start of any session that will modify the capability surface

## Command

```
python tools/capability_sync/run_sync.py --mode full
```

## What Changes

| File | What changes |
|------|-------------|
| `.governance/capabilities/registry.yaml` | Rebuilt from source registries |
| `.governance/capabilities/parity-report.yaml` | Updated parity check results |
| `CLAUDE.md` | Generated capability index section updated (human-authored content untouched) |
| `AGENTS.md` | Generated capability discovery section updated (human-authored content untouched) |
| `docs/governance/codex-adapter.md` | Registry reference added if absent (additive only) |

## What NEVER Changes (protected source registries)

- `.supervisor/skill-registry.yaml`
- `.claude/commands/command-registry.yaml`
- `.supervisor/capability-routing-registry.yaml`
- Any `.claude/commands/*.md` file content (only the discovery section in AGENTS.md changes)

## Idempotency Guarantee

Safe to run multiple times. A second run with no source changes produces no file modifications and exits 0.

## Other Modes

```
python tools/capability_sync/run_sync.py --mode inventory-only   # rebuild registry only
python tools/capability_sync/run_sync.py --mode validate          # parity check only
python tools/capability_sync/run_sync.py --mode drift-only        # drift detection only
```

## skill_id

sync-capabilities
