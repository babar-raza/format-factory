**Document type:** Directory Orientation
**Last reviewed:** 2026-07-01

# Sprint Task Templates (Playbooks directory)

## Purpose

Sprint task templates for format acquisition and feature expansion workflows.
These files are **Sprint Task Templates** (Layer A) — not YAML acquisition playbooks.

## Authority Model (Model C — Separate Scoped Layers)

This directory contains **Sprint Task Templates** (Markdown).
The YAML acquisition playbook system lives in `schemas/playbook/` and `tools/playbook/`.

| Layer | What | Where |
|-------|------|-------|
| Layer A — Sprint Task Templates | Markdown guides for bounded sprint tasks | `playbooks/format-factory/` (this directory) |
| Layer B — Acquisition Playbooks | YAML documents tracking gate operations | `schemas/playbook/`, `tools/playbook/`, `acquisition-packs/` |

The word "playbook" in filenames here refers to sprint task templates only.
"Playbook" as a governed YAML system refers exclusively to Layer B.

## Contents

- **`format-factory/`** — Sprint task templates: format-feature-expansion, new-format-kickstart, product-source-task, package-release-readiness, pipeline-incident-response, audit-healing-sprint
- **`playbook-registry.yaml`** — Machine-readable index of all sprint task templates and tools

## Governance

- **Classification:** DOCUMENTATION
- **Authority:** TASK_TEMPLATE only — not gate approval, not evidence contract replacement
- **Producers:** developers
- **Consumers:** developers, agents
- **Manual editing:** Yes — authored operational guides
- **Registry:** `playbooks/playbook-registry.yaml`

## Relationships

- Registry entry: `registry/repository-root-folders.yaml`
- Skill registrations: `.supervisor/skill-registry.yaml`
- Pilots: `.local/evidences/playbook-pilots-20260701/`
