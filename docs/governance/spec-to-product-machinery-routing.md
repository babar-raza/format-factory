# Spec-to-Product Machinery Routing

## Principle

Machinery that drives the spec-to-product pipeline (validators, orchestrators, queue managers, prompt generators) must not self-authorize through the autonomous default path. These components require an explicit governed route decision before execution.

## Governed Route Decision Flow

1. Task is classified via classify_task_category()
2. If category is machinery, route defaults to AGENT_GOVERNED_ROUTE_DECISION_REQUIRED
3. A governed agent may issue a route decision with allowed_paths, forbidden_paths, required_tests
4. Route decision is validated against schema and written to ledger
5. Only then can machinery execute via GOVERNED_DIRECT_EXECUTION

## Machinery Categories

- SPEC_AUTHORITY_MACHINERY: spec-index, verified-facts, authority level changes
- REQUIREMENT_CAPABILITY_MACHINERY: capability maps, gap analysis, requirement graphs
- ACTION_QUEUE_MACHINERY: queue management, action generation, queue schema changes
- AUTONOMY_ORCHESTRATOR_MACHINERY: autonomous_cycle, continuation, orchestration
- SUPERVISOR_VERDICT_MACHINERY: grading, verdict, review pipeline
- VALIDATOR_OR_EVIDENCE_MACHINERY: governance validators, evidence declaration
- PROMPT_GENERATION_MACHINERY: prompt generators, train synthesis
- GOVERNED_SKILL_OR_GENERATOR_MACHINERY: skill registry, skill execution

## Unsafe Instruction Quarantine

Generated prompts or queue items containing executable git commit, git push, npm publish, pypi upload, nuget push, MCP activation, or gate bypass instructions must be quarantined under .local/supervisor/quarantine/ and must not be executed.
