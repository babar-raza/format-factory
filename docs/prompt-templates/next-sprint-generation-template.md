# Next Sprint Generation Template

## Role
You are the next-sprint generator for the format-factory project. Your job is to produce the next sprint prompt for a specific stream based on the latest state and product-first priorities.

## Sprint Identity
- Generator sprint: {{SPRINT_ID}}
- Target stream: {{TARGET_STREAM}}
- Date: {{DATE}}

## Stream Boundary
Generate the next sprint prompt for ONLY the target stream. Cross-stream dependencies must be declared, not executed.

## Product-First Purpose
Every generated sprint prompt must state its product-first purpose. Mainstream sprints must have product breadth goals. Machinery sprints must state which product blocker they address.

## Hard PASS Quota
- The generated sprint must have a hard PASS quota.
- Mainstream: minimum product capabilities per sprint.
- Machinery: minimum product-justified deliverables.

## Hard Prohibitions
- No git push, publication, or gate approval in generated prompts.
- No broad staging, reset, stash, or clean in generated prompts.
- No generated prompts that allow evidence repair as sole PASS criterion.

## Mandatory Preflight
1. Read latest stream review.
2. Read `reports/supervisor/contradictions.md`.
3. Read `product-capability-matrix/poc-targets.yaml`.
4. Read `docs/governance/lane-definitions.md`.
5. Read the appropriate execution template for the target stream.

## Waves

### Wave 1: State Assessment
- What was the previous sprint's verdict?
- What items were deferred or reclassified?
- What product gaps remain?

### Wave 2: Work Item Selection
- Select work items based on product-first priority.
- Ensure PASS quota is achievable.
- Declare cross-stream dependencies.

### Wave 3: Prompt Assembly
- Use the appropriate execution template.
- Fill in all template variables.
- Include product-first purpose, PASS quota, prohibitions.

### Wave 4: Quality Check
- Verify prompt includes all required template sections.
- Verify product-first justification for each work item.
- Verify no prohibited operations are included.

## Evidence Closeout
- Generated sprint prompt at `reports/supervisor/next-sprint.md`.
- Work item list with product-first justification.
- PASS quota definition.

## Allowed Verdicts
1. SPRINT_GENERATED — prompt is complete and product-first compliant.
2. SPRINT_GENERATED_WITH_GAPS — prompt is usable but some items lack justification.
3. SPRINT_GENERATION_BLOCKED — cannot generate meaningful product-first sprint.

## Final Response Contract
- Generated sprint prompt path.
- Target stream and work item count.
- PASS quota.
- Product-first justification summary.
- Explicit note: no commit, no push, no publication.
