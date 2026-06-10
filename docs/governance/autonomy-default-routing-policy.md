# Autonomy Default Routing Policy

## Core Principle

Autonomy is acceleration, not authority. Evidence, tests, route decisions, taskcards, and supervisor verdicts are authority.

## Routes

| Route | Description |
|-------|-------------|
| AUTONOMOUS_ACCELERATED_DEFAULT | Safe product work qualified by category, tests, evidence, allowed paths |
| AGENT_GOVERNED_ROUTE_DECISION_REQUIRED | Machinery or unqualified work awaiting governed decision |
| GOVERNED_DIRECT_EXECUTION | Machinery with valid governed route decision on allowed paths |
| HUMAN_APPROVAL_REQUIRED | High-risk or gate-requiring work needing human authorization |
| BLOCKED_UNSAFE_OR_UNCLASSIFIED | Unknown, ambiguous, or unsafe work — fail closed |

## Task Categories

### Product Categories (may default to autonomous when qualified)
- PRODUCT_IMPLEMENTATION
- PRODUCT_TESTING
- PRODUCT_CAPABILITY_EXPANSION
- PRODUCT_EXPORT_OR_DOGFOOD

### Machinery Categories (require governed route decision)
- SPEC_AUTHORITY_MACHINERY
- REQUIREMENT_CAPABILITY_MACHINERY
- ACTION_QUEUE_MACHINERY
- AUTONOMY_ORCHESTRATOR_MACHINERY
- SUPERVISOR_VERDICT_MACHINERY
- VALIDATOR_OR_EVIDENCE_MACHINERY
- PROMPT_GENERATION_MACHINERY
- GOVERNED_SKILL_OR_GENERATOR_MACHINERY

### Blocked Category
- UNKNOWN_OR_AMBIGUOUS — always fails closed

## Fail-Closed Rules

1. Unknown or missing task category on current-run items blocks.
2. Legacy/backfill items without category may warn only when non-source-mutating.
3. Machinery without valid route_decision_id blocks.
4. Route decision must match task_id/category and not be blocked.
5. Product work routes to autonomous only with non-empty tests, evidence, and allowed_paths.
6. Generated prompts with unauthorized commit/push/publish instructions are quarantined.
7. Every route decision is written to the route ledger.

## Qualification for Autonomous Default

Product work qualifies for AUTONOMOUS_ACCELERATED_DEFAULT when:
- task_category is a product category
- required_tests is non-empty
- required_evidence is non-empty
- allowed_paths is non-empty
- no forbidden machinery mutation
- risk_level is LOW or MEDIUM
- no human_approval_required flag
