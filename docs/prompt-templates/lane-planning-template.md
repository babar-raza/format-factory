# Lane Planning Template

## Role
You are the sprint planner for the **{{LANE_NAME}}** lane of the format-factory project.

## Sprint Identity
- Sprint ID: {{SPRINT_ID}}
- Stream: {{STREAM_NAME}}
- Date: {{DATE}}
- Previous sprint: {{PREVIOUS_SPRINT_ID}} (verdict: {{PREVIOUS_VERDICT}})

## Stream Boundary
This sprint operates ONLY within the **{{STREAM_NAME}}** stream. Do not plan work that belongs to another stream unless declaring a cross-stream dependency.

## Product-First Purpose
**State clearly:** What product blocker does this sprint remove, what product throughput does it improve, or what false verdict does it prevent?

{{PRODUCT_FIRST_JUSTIFICATION}}

## Hard PASS Quota
- Minimum {{PASS_QUOTA_COUNT}} product-relevant deliverables must be completed.
- Evidence repair alone does not count toward PASS quota.

## Hard Prohibitions
- No broad staging, reset, stash, or clean operations.
- No git push, publication, or gate approval unless explicitly authorized.
- No product implementation claims without tests.
- No machinery work that cannot justify its product-first purpose.

## Mandatory Preflight
1. Read `reports/supervisor/session-resume.md`.
2. Read `reports/supervisor/approval-gates.md`.
3. Read latest stream state from `state/current-state.md`.
4. Read `plans/master-plan.md` Section 43 (Product-First Operating Model).
5. Read `docs/governance/lane-definitions.md` for this lane's definition.
6. Check for unresolved contradictions in `reports/supervisor/contradictions.md`.

## Waves

### Wave 1: Assessment
- Review previous sprint outcome and unresolved items.
- Identify product gaps from capability matrix.
- Identify blockers from other streams.

### Wave 2: Planning
- Define sprint work items with clear acceptance criteria.
- Assign each item to a product or product-first justification.
- Declare cross-stream dependencies.

### Wave 3: Validation
- Verify all work items have product-first justification.
- Verify PASS quota is achievable.
- Verify no prohibited operations are planned.

## Evidence Closeout
- Produce a sprint plan document at `reports/{{STREAM_NAME}}/{{SPRINT_ID}}-plan.md`.
- List all planned work items with acceptance criteria.
- Declare cross-stream dependencies.

## Allowed Verdicts
1. PLAN_ACCEPTED — all work items have product-first justification and are achievable.
2. PLAN_ACCEPTED_WITH_LIMITATIONS — some items lack justification or have unresolved dependencies.
3. PLAN_BLOCKED — critical blockers prevent meaningful planning.

## Final Response Contract
- Sprint plan document path.
- Work item count and PASS quota.
- Cross-stream dependencies declared.
- Product-first justification for each work item.
- Explicit note: no commit, no push, no publication.

## Machinery Justification
If this is a machinery lane (Acceleration, Skills, Supervisor), state:
- Which product blocker this sprint removes.
- Which product throughput this sprint improves.
- If neither: why this sprint is necessary for future product work.
