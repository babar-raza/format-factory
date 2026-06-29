# Supervisor Control Plane

Configuration, policies, schemas, prompts, skill registry, and project memory for the autonomous supervisor system.

## Contents

- **`config.yaml`** — Supervisor configuration
- **`policies.yaml`** — Autonomous execution policies
- **`skill-registry.yaml`** — Canonical skill registry (99+ capabilities)
- **`project-memory.md`** — Project memory snapshot
- **`prompts/`** — Supervisor prompt templates
- **`schemas/`** — Evidence declaration and validation schemas
- **`fixtures/`** — Test fixtures for supervisor
- **`state/`** — Runtime state (gitignored — not committed)

## Governance

- **Classification:** GOVERNANCE_INFRA
- **Layer:** L11 (Supervisor)
- **Producers:** supervisor tools, developers
- **Consumers:** supervisor loop, governance validators, sprint executor
- **Manual editing:** Config and policies are authored; state/ is generated
- **Note:** `.supervisor/state/` is gitignored (runtime-only). Committed content is configuration.
- **Registry:** `registry/repository-root-folders.yaml`
