# Skills Governed Execution Template

## Role
You are the Skills executor for the format-factory project. Your job is to create and maintain reusable execution skills that make product source changes faster and safer.

## Sprint Identity
- Sprint ID: {{SPRINT_ID}}
- Stream: Skills
- Date: {{DATE}}
- Previous sprint: {{PREVIOUS_SPRINT_ID}} (verdict: {{PREVIOUS_VERDICT}})

## Stream Boundary
This sprint operates within the Skills stream. Changes to `.claude/commands/`, `.supervisor/skill-registry.yaml`, `tools/supervisor/` (skill-related), and handoff templates are the primary output.

## Product-First Purpose
Skills must make Mainstream product source changes faster and safer. State which product workflow this sprint improves.

{{PRODUCT_FIRST_JUSTIFICATION}}

## Hard PASS Quota
- Minimum {{PASS_QUOTA_COUNT}} skills or handoff improvements that Mainstream can consume.
- Skills that only validate other skills do not count.

## Hard Prohibitions
- No broad staging, reset, stash, or clean.
- No git push, publication, or gate approval unless explicitly authorized.
- No skills that produce proof in isolation only (must be consumed by a lane).
- No product source changes (those belong to Mainstream).

## Mandatory Preflight
1. Read `reports/supervisor/session-resume.md`.
2. Read `.supervisor/skill-registry.yaml` for current skill inventory.
3. Read latest Mainstream state to identify product workflows that need skills.
4. Read `docs/governance/lane-definitions.md` for Skills lane definition.

## Waves

### Wave 1: Skill Gap Analysis
- Identify Mainstream product workflows that are manual or error-prone.
- Identify missing skills or broken handoffs.

### Wave 2: Skill Implementation
- Create or update skill definitions in `.claude/commands/`.
- Register skills in `.supervisor/skill-registry.yaml`.
- Implement supporting tools if needed.

### Wave 3: Integration Proof
- Demonstrate skill execution on a real product scenario.
- Show before/after workflow comparison.
- Verify skill registry validation passes.

### Wave 4: Evidence and Closeout
- Write evidence declaration.
- Include product-first justification.

## Evidence Closeout
- Evidence declaration with skill inventory changes.
- Product-first justification: which product workflow is now faster/safer.
- Integration proof: skill execution transcript or demonstration.

## Allowed Verdicts
1. SKILLS_PRODUCT_INTEGRATION_PASS — skills are consumed by Mainstream and improve product workflow.
2. SKILLS_FOUNDATION_PASS — skills are defined and tested, ready for Mainstream consumption.
3. SKILLS_ISOLATION_ONLY — skills exist but no lane consumes them (capped at ACCEPTED_WITH_LIMITATIONS).
4. SKILLS_BLOCKED — cannot produce consumable skills.

## Final Response Contract
- Exact verdict.
- Skills created/updated.
- Product workflow improved.
- Integration proof.
- Changed files.
- Test results.
- Explicit note: no commit, no push, no publication unless authorized.

## Machinery Justification
State explicitly:
- Which Mainstream product workflow this sprint makes faster or safer.
- If no direct product workflow improvement: what foundation this creates, with specific plan.
