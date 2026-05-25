# R63 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Purpose

Work-ahead trains reduce R64/R65 startup cost while R63 closure blockers are being verified.
They run in parallel with closure trains but are governed independently.

---

## Permitted Work-Ahead

1. **Readiness analysis** — ranking formats by package readiness (no gate mutations)
2. **Fixture inventory** — documenting missing/weak samples (no downloads)
3. **Test scaffolds** — xfail/skip-marked only; no new passing claims
4. **Validator gap analysis** — identify missing negative tests; implement low-risk ones
5. **Docs/taskcards** — create/update where current evidence supports
6. **Dry-run publication checklists** — no upload; all gates blocked

---

## Prohibited Work-Ahead

1. Gate approval (Gate 8, Gate 11) — human-only
2. Mutating acquisition-packs/ without coordinator approval
3. Mutating registry/format-registry.yaml without coordinator approval
4. Changing gate status without deterministic evidence
5. Publishing to PyPI or NuGet
6. Claiming commercial_product_ready = true
7. Downloading new specs or external samples without policy approval

---

## Anti-Blocker Rule

A blocker in a closure train must NOT stop work-ahead trains. Both categories run
independently. If all closure trains block, work-ahead trains continue and deliver.

---

## Coordinator Review Required Before

- Any work-ahead output that proposes gate status change
- Any work-ahead output that proposes registry mutation
- Any work-ahead output that claims publication readiness

WORK_AHEAD_POLICY: DOCUMENTED
