# Plans

Master plan, permanent layer plans, per-chat plans, and healing plans.

## Contents

- **`master-plan.md`** — Single operational authority for the project
- **`master-plan-memory.md`** — Ledger-only plan memory
- **`strategic/`** — High-authority strategic and governance plans (spec-to-feature, SAL forensics, etc.)
- **`healing/`** — Repair, hardening, and backfill plans
- **`secondary/`** — Historical, superseded, and archived plans
- **`layers/`** — Permanent layer plans (34+ layers) with index, task register, and dependency register
- **`.claude/`** — Per-chat plan files (created by plan mode)
- **`.governance/`** — Plan governance metadata (routing policy, migration maps)

## Governance

- **Classification:** GOVERNANCE_INFRA
- **Producers:** developers, plan tools, supervisor
- **Consumers:** supervisor, sprint executor, agents
- **Manual editing:** Yes — plans are authored content. Layer index is governed.
- **Registry:** `registry/repository-root-folders.yaml`

## Agent Navigation

**Purpose of this folder:** All planning documents — master plan, layer plans, per-chat
plans, and healing plans. Created by developers and plan-mode sessions.

**Where per-chat plans go:** `plans/.claude/<plan-name>.md`. When plan mode creates a plan
at `~/.claude/plans/<name>.md`, IMMEDIATELY copy it to `plans/.claude/<name>.md` and run:
`python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/<name>.md`

**Where strategic plans go:** `plans/strategic/` for spec-to-feature, SAL forensics, etc.
**Where layer plans go:** `plans/layers/<layer-slug>.md`
**Where healing plans go:** `plans/healing/`

**To check the active plan lock:** `python tools/supervisor/write_plan_lock.py --status`
**To check continuation signal:** `python tools/supervisor/check_continuation.py`

**Producer:** Developer-authored. Plan mode creates seeds in `plans/.claude/`. Supervisor
updates `plans/master-plan.md` sections via autonomous cycle.
