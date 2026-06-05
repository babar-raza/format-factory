# Plan Repair Order Reference

**Added:** 2026-06-04
**Authority:** local-memory-sync sprint 2026-06-04

## Context

All four stream plans (Supervisor, Skills, Acceleration, Mainstream) require one external-tool-aware repair pass before autonomous execution. This document defines the repair order and what each repair must accomplish.

## Repair Order

### 1. Supervisor Repair (First)
**Why first:** Supervisor establishes the governance framework all other plans depend on.

**Must add:**
- Ruflo runtime governance section (mode detection, approval flow)
- Superpowers plugin governance (normalization requirement)
- GhidraMCP compliance gate (DISABLED_BY_DEFAULT with activation conditions)
- External tool mode detection in session-resume
- Runtime mutation policy (what Supervisor approves vs. blocks)

### 2. Skills Repair (Second)
**Why second:** Skills normalizes external skill patterns before Mainstream can consume them.

**Must add:**
- Superpowers Marketplace intake section
- Local skill normalization checklist (5-step process)
- External skill wrapper template (allowed/forbidden paths, validation, rollback)
- Installation gate for each risk level
- Risk register for existing and proposed skills
- No-plugin-install proof requirement

### 3. Acceleration Repair (Third)
**Why third:** Acceleration clarifies AI cognitive model and tool intake rules.

**Must add:**
- External tool intake section (what AI tools Acceleration may call)
- Ruflo boundary (Acceleration uses Ruflo for learning/telemetry only, if approved)
- Superpowers boundary (brainstorm/ideation only unless normalized)
- GhidraMCP gate reference (DISABLED_BY_DEFAULT)
- Tool risk register (what AI tool calls are permitted per mode)
- External-tool authority validation (AI output from tools is ai_draft)

### 4. Mainstream Repair (Last)
**Why last:** Mainstream integrates all machinery handshakes into the POC mega-train loop.

**Must add:**
- Ruflo-aware orchestration model (FULL_LOOP if approved, local coordinator if absent)
- Ruflo fallback modes (never block on Ruflo absence)
- Continuation loop contract (17-step loop from mainstream-poc-mega-train.md)
- Machinery readiness handshake (how Mainstream checks Skills/Acceleration readiness)
- Skills/Superpowers handshake (how Mainstream consumes normalized skills)
- Acceleration feedback loop (what Mainstream reports back after each iteration)
- GhidraMCP default exclusion (never call GhidraMCP from Mainstream)

## Repair Pass Format (all plans)

Each repair pass:
- Produces an updated prompt template (or new version)
- Produces a `reports/supervisor/plan-repair-<stream>-<date>.md` with changes
- Does NOT change product source (src/net/, src/python/)
- Does NOT commit or push
- Does NOT approve any gate

## Reference Documents for Repair

- docs/governance/external-tool-architecture.md
- docs/governance/ruflo-runtime-governance.md
- docs/governance/superpowers-skill-intake.md
- docs/governance/ghidra-mcp-compliance-gate.md
- docs/governance/four-stream-operating-model.md
- docs/governance/ai-authority-boundary.md
- docs/governance/product-first-operating-model.md
- docs/governance/mainstream-poc-mega-train.md
