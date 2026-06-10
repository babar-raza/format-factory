# Supervisor Control Plane Boundary

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## What Supervisor IS

- Deterministic control plane: validates evidence with code-based rules
- Traffic controller: routes blockers to correct streams
- False-pass preventer: detects evidence-only sprints claiming product breadth
- False-stop preventer: routes prompt-quality issues away from product lanes
- Stream-local authority enforcer: each stream's evidence is evaluated locally

## What Supervisor IS NOT

- AI product brain (that's Acceleration stream)
- Just an evidence auditor (Supervisor also routes and governs)
- Authoritative AI output generator (AI advisory is non-authoritative)
- Gate approver (gates 1-11 require human approval)

## Authority Boundary

| Action | Authority |
|--------|-----------|
| Evidence validation | Deterministic (Supervisor) |
| Continuation state | Deterministic (autonomous_cycle.py) |
| Gate approval | Human only |
| AI advisory output | Non-authoritative (ai_draft) |
| Ruflo/tool coordination | Runtime advisory only |
| Product source edits | Skill/worker (never Supervisor) |
