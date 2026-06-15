UNIVERSAL POST-SPRINT AUTONOMY LOOP — INSTALL FULL PROMPT 1, PROMPT 2, PROMPT 3, WIRE LOOP CONTROLLER, EXECUTE, SCORE, REROUTE, PACKAGE, AND REPEAT UNTIL ALL GREEN

Mission:
Build, harden, integrate, and pilot-prove a reusable autonomous post-sprint control system for this project and make it portable to future projects.

The user currently runs three prompts manually after every sprint:

Prompt 1:
A strict sprint audit that reviews what the sprint actually achieved, what it proved, how it affected the final outcome, and what was missed, partial, unverified, weakly proven, incorrectly done, not integrated, or systemically broken.

Prompt 2:
A plan-hardening prompt that reads Prompt 1 outputs, deep-dives the system again, updates or enhances the active master plan, and converts every unresolved issue into taskcard-driven, gate-managed, machine-state-managed execution work.

Prompt 3:
A controlled execution prompt that executes the hardened plan only if it is genuinely ready, otherwise heals the plan first. It executes in controlled slices, verifies, hardens, re-verifies, creates evidence, and produces a true final report.

Current manual continuation rule:
- If Prompt 3 produces a prose-only sprint summary, run Prompt 2 then Prompt 3.
- If Prompt 3 produces no sprint summary, run Prompt 1 then Prompt 2 then Prompt 3.
- If Prompt 3 produces a structured summary but it is not all green, feed remaining issues into Prompt 2 then run Prompt 3.
- Continue until the sprint summary is all green and nothing more is required.

Your job:
Convert this manual process into reusable project-owned machinery so the user no longer needs to manually choose which prompt to run next.

This is not a one-off prompt-writing task.
This is not just a plan.
This is not just a review.
This is a production governance and autonomous sprint-control implementation sprint.

The system must:
- install the full enhanced prompt assets into the repository,
- keep them reusable,
- keep them project-aware,
- connect them to existing supervisor/governance/taskcard machinery where available,
- create missing contracts and schemas where needed,
- create or harden a loop controller,
- classify Prompt 3 summaries,
- choose the next stage automatically,
- enforce 4/5 quality scoring,
- reroute failed work,
- reject prose-only or missing summaries,
- reject missing evidence bundles,
- package evidence every cycle,
- pilot-prove the full Prompt 1 → Prompt 2 → Prompt 3 loop.

----------------------------------------------------------------------
CORE DESIGN PRINCIPLE
----------------------------------------------------------------------

This must become a sprint operating system, not a pile of disconnected prompts.

A future agent must be able to run the project’s post-sprint loop without asking the user:
- Which prompt should I run now?
- Is this summary good enough?
- Should I rerun Prompt 2?
- Should I rerun Prompt 3?
- Is prose acceptable?
- Is a missing evidence bundle acceptable?
- Can an item with a 3/5 score pass?

The answer must be machine-controlled:
- summaries are classified,
- taskcards are checked,
- scores are checked,
- evidence is checked,
- gates are checked,
- loop decision is computed,
- next stage is selected automatically.

----------------------------------------------------------------------
SOURCE OF TRUTH
----------------------------------------------------------------------

Current repository state is the source of truth.

Before creating new machinery, inspect what already exists.

Search for:
- sprint closeout hooks
- evidence bundle builders
- declaration-review-package builders
- audit prompts
- plan-hardening prompts
- execution prompts
- supervisor prompt folders
- prompt registry
- skill registry
- agent instruction registry
- taskcard generator
- taskcard validator
- taskcard state machine
- queue/state files
- continuation signals
- autonomous-cycle scripts
- validators
- quality graders
- reroute/rework logic
- summary parser
- loop controller
- evidence contracts
- governance docs
- project adapter configs
- CI/workflow hooks
- previous sprint evidence
- previous sprint summaries

Do not rebuild what already works.
Do not preserve weak machinery just because it exists.
Do not assume a prompt file is enforceable unless it is wired into the project flow.
Do not assume a validator is enforceable unless it blocks or drives state.
Do not assume an evidence bundle is valid unless its manifest, declaration, and contents agree.

----------------------------------------------------------------------
PROMPT ASSET LOCATION
----------------------------------------------------------------------

Create reusable prompt assets under:

autonomous/supervisor/prompts/

If the project already uses another supervisor/governance prompt folder, use the project-native path and document the decision.

Acceptable alternatives:
- .supervisor/prompts/
- governance/prompts/
- tools/supervisor/prompts/
- automation/sprint/prompts/
- docs/governance/prompts/

Required prompt assets:
- prompt1-post-sprint-audit.md
- prompt2-plan-hardening.md
- prompt3-controlled-execution.md
- prompt-loop-controller.md
- prompt-output-contracts.md
- project-adapter-template.md

Required contracts/schemas:
- stage1-issue-model-schema.yaml
- stage2-taskcard-contract.yaml
- stage3-quality-scoring-rubric.yaml
- taskcard-state-machine.yaml
- summary-parser-contract.yaml
- loop-decision-state-machine.yaml
- evidence-bundle-contract.yaml
- project-adapter-contract.yaml
- governance-contract.yaml

If a registry exists:
- add these prompts to the registry.
- add stable IDs.
- add descriptions.
- add required inputs.
- add required outputs.
- add successor-stage rules.
- add validation rules.

If no registry exists:
- create prompt-registry.yaml in the selected prompt folder.
- wire it to the loop controller or taskcard the wiring if implementation is too large for this sprint.

----------------------------------------------------------------------
FULL PROMPT 1 ASSET — prompt1-post-sprint-audit.md
----------------------------------------------------------------------

Install this full enhanced Prompt 1 as a reusable project asset.

Title:
POST-SPRINT STRICT EVIDENCE AUDIT, THREE-LEVEL ISSUE DISCOVERY, ROOT-CAUSE REVIEW, AND NEXT-STAGE RECOMMENDATION

Mode:
Audit mode.
Do not execute new implementation work.
Do not modify source files unless the project’s audit system requires writing evidence artifacts.
Do not exaggerate progress.
Do not describe intent as achievement.
Do not treat claims as facts.
Do not accept summaries without evidence.
Do not skip integration and system-connect-point review.

Mission:
Provide an evidence-based summary of what was actually achieved in the last sprint, then perform a strict manual and evidence-backed review of:
- what was completed,
- what was partial,
- what was unresolved,
- what was not verified,
- what was not proven,
- what was integrated,
- what was supposed to be integrated but was not,
- what system weaknesses allowed gaps to happen.

Core requirements:
- Do not exaggerate progress.
- Do not describe intent as achievement.
- Separate completed work, partial work, and unresolved gaps.
- Distinguish between code changes, verified behavior, and assumptions.
- Focus on what was proven by direct evidence, not what was expected to happen.
- Identify missing proof explicitly.
- Identify root causes, not just symptoms.
- Identify integration/connect-point gaps.
- Identify system weaknesses that could cause recurrence.
- Produce both human-readable and machine-readable outputs.
- Recommend the next stage for the loop controller.

Required input discovery:
Locate and inspect the latest sprint evidence from available sources:
- final assistant response
- sprint summary
- evidence bundle
- declaration review package
- evidence-declaration.yaml
- evidence-manifest.yaml
- changed-file manifest
- taskcards
- taskcard index
- ledgers
- queue/state files
- continuation signals
- raw logs
- command logs
- test outputs
- validator outputs
- generated outputs
- sample outputs
- closeout report
- pilot proof
- current repository state
- relevant consumers and integration points

If evidence bundle is missing:
- classify all dependent claims as UNVERIFIED.
- produce an EVIDENCE_DEFECT issue.
- recommend Prompt 2 if a plan update is required.
- recommend Prompt 3 only if evidence repair can be executed safely from taskcards.

Human-readable section A — What we achieved:
List concrete outputs, changes, validations, and decisions completed during the sprint.

For each achievement, state:
- what changed,
- where it changed,
- whether it was fully done or partially done,
- what evidence supports it,
- whether behavior was verified,
- whether it is integrated,
- whether it is production-ready,
- whether any caveats remain.

Do not mix:
- code existence,
- behavior proof,
- integration proof,
- production readiness.

Human-readable section B — What this proves:
Explain what the sprint results actually demonstrate about the system, process, product, or plan.

Classify the level of proof:
- implementation_only
- partial_validation
- focused_validation
- integration_validation
- end_to_end_proof
- pilot_proof
- no_proof_yet

Identify:
- evidence-supported conclusions,
- conclusions still unproven,
- assumptions still being carried,
- proof that is too narrow,
- proof that is synthetic-only,
- proof that lacks raw logs,
- proof that lacks consumer/integration validation.

Human-readable section C — Effect on the final outcome:
Explain how the sprint changes the likely final outcome.

State whether it:
- reduced risk,
- improved confidence,
- uncovered deeper issues,
- changed the execution path,
- moved the project materially closer to the final goal,
- exposed blockers,
- revealed weak system machinery,
- requires plan hardening,
- requires re-execution.

Also state:
- what still blocks the final outcome,
- what remains unproven,
- what must happen next.

Structured issue level L1 — Sprint execution issues:
Identify issues in the sprint’s own execution.

Include issues such as:
- missed task
- partially completed task
- incorrectly completed task
- unverified work
- unproven claim
- missing raw log
- missing validator output
- weak test
- synthetic-only test
- stale artifact
- missing evidence bundle
- missing declaration
- missing manifest
- misleading final summary
- taskcard not closed
- taskcard closed without evidence
- changed file not listed
- generated output not inspected
- commit/staging state unclear
- pilot claimed but not proven
- end-to-end claim without end-to-end evidence
- production-ready claim without production proof

Structured issue level L2 — Integration and connect-point issues:
Identify issues where sprint work was supposed to connect into the system.

Include issues such as:
- implementation not consumed
- output not wired to downstream stage
- registry not updated
- state file stale
- queue not updated
- ledgers not updated
- docs not synchronized
- skill not synchronized
- prompt not synchronized
- schema not synchronized
- validator not synchronized
- CI/local gate not updated
- generated artifact not regenerated
- generated artifact not promoted
- downstream workflow still uses old path
- evidence exists but no consumer reads it
- taskcard exists but no executor consumes it
- plan updated but execution prompt not updated
- new script exists but is not registered
- new rule exists but is advisory only

Structured issue level L3 — System weakness issues:
Identify deeper weaknesses that allowed the sprint to fall short.

Include weaknesses such as:
- autonomous supervisor did not continue
- no loop controller
- no summary parser
- no quality scorer
- no reroute controller
- no fail-closed state
- validator too shallow
- evidence contract too weak
- taskcard schema too weak
- plan allowed prose-only work
- governance allowed early stop
- prompt allowed handoff instead of execution
- system did not require pilot proof
- system did not force downstream consumption check
- system accepted artifact existence as proof
- system accepted synthetic tests as production proof
- system did not block below-threshold quality
- system required human to choose next prompt
- system allowed “next prompt needed” as a final state

Every issue record must contain:
- issue_id
- issue_level
- title
- description
- evidence
- missing_evidence
- root_cause
- why_not_only_symptom
- affected_files
- affected_components
- affected_connection_points
- severity
- blocker
- recurrence_risk
- required_fix_type
- requires_plan_update
- requires_taskcard
- requires_system_healing
- requires_reexecution
- requires_governance_change
- requires_evidence_repair
- recommended_next_stage
- acceptance_impact

Claim classification matrix:
For every major sprint claim classify:
- ACCEPTED_VERIFIED
- ACCEPTED_WITH_LIMITATIONS
- PARTIAL
- UNVERIFIED
- FAILED
- STALE
- MISLEADING
- DAMAGED_OR_REGRESSED
- EXTERNAL_BLOCKED

Required Prompt 1 outputs:
- stage1-sprint-audit-summary.md
- stage1-achievement-proof-summary.md
- stage1-final-outcome-impact.md
- stage1-l1-execution-issues.yaml
- stage1-l2-integration-issues.yaml
- stage1-l3-system-weaknesses.yaml
- stage1-root-cause-map.md
- stage1-claim-classification-matrix.csv
- stage1-evidence-quality-verdict.md
- stage1-next-stage-recommendation.yaml

Prompt 1 evidence quality verdicts:
- STRONG
- ADEQUATE_WITH_LIMITATIONS
- WEAK
- INSUFFICIENT
- MISLEADING

Prompt 1 final verdicts:
- SPRINT_ALL_GREEN_VERIFIED
- SPRINT_ACCEPTED_WITH_LIMITATIONS
- SPRINT_REQUIRES_PLAN_HARDENING
- SPRINT_REQUIRES_REEXECUTION
- SPRINT_REQUIRES_EVIDENCE_REPAIR
- SPRINT_BLOCKED_EXTERNAL
- SPRINT_SUMMARY_INSUFFICIENT

Prompt 1 next-stage recommendation rules:
- If all green and evidence is strong, recommend adversarial review then acceptance.
- If issues require plan changes, recommend Prompt 2.
- If only evidence packaging is missing and no plan changes are required, recommend Prompt 3 evidence repair lane.
- If execution defects remain, recommend Prompt 2 then Prompt 3.
- If sprint summary is missing or insufficient, recommend Prompt 1 rerun or evidence reconstruction.
- If true external blocker exists, recommend blocker packaging and stop.

----------------------------------------------------------------------
FULL PROMPT 2 ASSET — prompt2-plan-hardening.md
----------------------------------------------------------------------

Install this full enhanced Prompt 2 as a reusable project asset.

Title:
PLAN MODE — HARDEN CURRENT PLAN FROM LATEST SPRINT AUDIT / EVIDENCE SUMMARY

Role:
You are a senior plan hardening agent, sprint audit interpreter, execution planner, evidence reviewer, governance designer, and weak-agent safety reviewer.

Mission:
Read the latest Stage 1 sprint audit outputs, recent conversation/prose, evidence summary, sprint final report, reviewer summary, or equivalent audit source. Extract every unresolved gap, remaining item, weak spot, risk, blocker, incomplete proof, partially done area, not-attempted area, stale assumption, and recommended next step. Then harden the current/existing plan so it directly addresses those issues.

Mode:
This is a plan hardening task.

This is not an execution task.
Do not modify product/source files.
Do not run implementation commands.
Do not commit.
Do not push.
Do not publish.
Do not delete files.
Do not claim anything has been fixed.
Do not create fake evidence bundles.
Do not invent verification results.

Allowed outputs:
- plan amendments
- plan delta
- taskcards
- gates
- verification matrix
- evidence contract
- anti-overclaim rules
- execution-ready handoff
- next execution prompt

Input discovery priority:
1. stage1-l1-execution-issues.yaml
2. stage1-l2-integration-issues.yaml
3. stage1-l3-system-weaknesses.yaml
4. stage1-root-cause-map.md
5. stage1-claim-classification-matrix.csv
6. stage1-evidence-quality-verdict.md
7. stage1-next-stage-recommendation.yaml
8. latest sprint audit summary, evidence summary, final report, reviewer summary, or similar prose
9. active master plan
10. current roadmap
11. current taskcards
12. current governance docs
13. sprint history
14. current repository state

If multiple sprint summaries exist:
- use the latest one unless prose clearly targets another.

If multiple plans exist:
- use the most recent active plan.

If the audit summary and active plan refer to different projects/streams:
- do not merge blindly.
- report mismatch.
- create safe addendum only for the matching project/stream.
- classify final verdict as PLAN_NOT_READY_AUDIT_PLAN_MISMATCH if unresolved.

If active plan is not visible:
- do not hallucinate that it was seen.
- extract pending work from audit summary.
- produce plan-hardening addendum in nearest visible prior planning style if inferable.
- mark PLAN_CONTEXT_PARTIAL.
- state exactly what context was missing.

Core mission:
Turn sprint audit output into a stronger execution-ready production plan.

Extract and incorporate:
- completed verified work to preserve as closed
- completed but weakly verified work
- partially done work
- not attempted work
- claimed but unproven work
- weak evidence
- missing raw proof
- missing real-repo verification
- synthetic-only tests
- advisory-only gates
- unregistered scripts
- stale generated artifacts
- missing regeneration steps
- missing integration steps
- missing CI/local gate wiring
- missing post-change inspection
- missing taskcards
- missing ownership
- missing stop conditions
- missing evidence requirements
- missing validation commands
- missing repair loops
- unsafe assumptions
- false confidence risks
- system weakness issues from L3
- future hardening work

Do not overwrite the plan from scratch unless the existing plan is unusable.

Preserve:
- valid decisions
- valid lane structure
- valid taskcard structure
- valid gates
- valid terminology
- project planning style
- completed verified work
- accepted constraints
- true external blockers

But repair weak areas assertively.

Interpretation rules:
Treat Stage 1 outputs and audit summaries as evidence about current state, not as a complete plan.

Separate:
1. completed_and_verified
2. completed_but_weakly_verified
3. partially_done
4. not_attempted
5. claimed_but_unproven
6. risk_not_reduced
7. final_outcome_blockers
8. next_hardening_work

Required gap extraction categories:
1. Implementation gaps
   - code exists but incomplete
   - code exists but not integrated
   - extraction logic exists but not run against real source
   - feature works only on synthetic inputs
   - artifact not regenerated
   - stale output remains live
   - script exists but not wired
   - API surface not refreshed
   - examples/snippets not regenerated
   - content/pages/outputs still depend on stale knowledge

2. Verification gaps
   - synthetic-only unit tests
   - no real-repository test
   - no end-to-end run
   - no post-regeneration inspection
   - no compile/runtime proof
   - no CI proof
   - no raw logs
   - no audit against actual generated outputs
   - no install/import/use proof
   - no post-merge/live verification
   - no pilot proof

3. Gate and workflow gaps
   - advisory script not registered
   - validator not in pre-commit or CI
   - gate exists but optional
   - CI does not run check
   - approval gate missing
   - dry-run gate missing
   - state machine does not reflect reality
   - generated next prompt does not include blocker
   - loop controller missing
   - summary parser missing
   - reroute controller missing

4. Artifact freshness gaps
   - generated artifacts stale
   - knowledge cache old
   - reports point to old outputs
   - promoted artifacts not updated
   - regenerated output not compared
   - cache short-circuit not bypassed
   - live content can reproduce fixed bug

5. Evidence gaps
   - claim lacks raw proof
   - evidence only direct inspection
   - evidence only synthetic fixtures
   - no changed-file manifest
   - no final git status
   - no command log
   - no lane ledger
   - no taskcard closeout
   - no before/after comparison
   - evidence declaration references missing files

6. Safety and production gaps
   - publish/deploy path not guarded
   - live-state claim unverified
   - external dependency not present
   - command unavailable in environment
   - missing fallback
   - missing rollback
   - future generation can reintroduce bug

7. Planning/governance gaps
   - issue not taskcarded
   - unclear lane owner
   - unclear closeout criteria
   - human blocker claimed without proof
   - no adversarial review
   - no repair loop
   - historical prose not collapsed into final decision
   - next steps too vague
   - Prompt 3 can stop with prose-only summary
   - below-4 score can be accepted
   - evidence bundle is optional

Plan hardening requirements:
For every issue extracted from Prompt 1 or audit summary, add or update:
- lane
- taskcard
- owner role
- supervisor role
- current status
- source evidence
- exact work required
- allowed paths or affected areas
- forbidden actions
- verification method
- evidence required
- closeout criteria
- stop conditions
- rollback/safety notes
- priority
- whether real source/repo verification is required
- whether synthetic tests are acceptable or only supplementary
- whether live artifact regeneration is required
- whether CI/local gate wiring is required
- whether post-run inspection is required
- whether loop-controller behavior must change

Every issue must map to one of:
- fixed_by_existing_plan_item
- new_plan_item_required
- updated_plan_item_required
- taskcard_required
- governance_change_required
- verification_only_required
- rejected_with_reason
- blocked_external

Do not leave actionable items as prose-only recommendations.
Every actionable item must become taskcard-driven or lane-owned.

Plan format preservation:
- Preserve existing lanes where useful.
- Preserve taskcard format where useful.
- Preserve gate naming where useful.
- Preserve evidence contract format where useful.
- Preserve status vocabulary unless misleading.
- Preserve sprint identity where useful.
- Collapse historical/confusing/superseded prose into clear final decisions.
- Mark superseded items explicitly.

Taskcard requirements:
Each taskcard must include:
- taskcard_id
- title
- source_issue_id
- source_issue_level
- source_audit_finding
- why_it_matters
- risk_addressed
- current_status
- lane_owner
- supervisor_role
- required_implementation_or_investigation
- required_verification
- required_evidence
- quality_dimensions
- scoring_rubric
- reroute_rule_if_score_below_4
- acceptance_criteria
- stop_conditions
- allowed_actions
- forbidden_actions
- dependencies
- closeout_rules
- machine_state

Valid taskcard statuses:
- completed_verified
- completed_but_weakly_verified
- partially_done
- not_attempted
- claimed_unproven
- blocker
- follow_up
- ready_for_execution
- blocked_external
- deferred_with_reason

Validation and repair-loop requirements:
The hardened plan must include:
- internal adversarial review
- contradiction repair
- 1–2 validation repair loops
- final evidence review
- final state summary
- final blockers list
- no-overclaim rules
- reroute rules
- all-green acceptance definition

The plan must instruct the future execution agent:
- do not stop after first issue
- do not treat synthetic-only tests as real proof
- do not treat advisory-only scripts as gates
- do not treat generated code changes as applied until generated artifacts are refreshed or explicitly deferred
- do not treat artifact existence as correctness
- do not claim risk reduction if stale live artifact still exists
- do not claim CI protection if check is not wired into CI/local gates
- do not treat unavailable command as proof of correctness
- continue safe lanes even if one lane is blocked
- do not accept below-4 quality score
- do not accept prose-only summaries
- do not accept missing sprint summaries
- do not accept missing evidence bundles

No timelines:
Do not create timeline promises.
Do not give calendar deadlines.
Use priority and dependency only.

Prompt 2 required human-readable outputs:
1. Input interpretation
2. Summary of issues extracted from sprint audit
3. Base gaps and weak spots
4. Exact amendments made or proposed
5. Updated execution-ready plan
6. Taskcard register
7. Verification matrix
8. Remaining blockers
9. Anti-overclaim rules for next execution agent
10. Final plan verdict

Prompt 2 required machine-readable outputs:
- stage2-input-interpretation.md
- stage2-issues-extracted-from-stage1.md
- stage2-plan-gap-analysis.md
- stage2-master-plan-delta.md
- stage2-enhanced-master-plan.md
- stage2-taskcard-index.yaml
- stage2-taskcards/*.yaml
- stage2-execution-dag.yaml
- stage2-lane-ownership-map.yaml
- stage2-gate-model.md
- stage2-verification-matrix.md
- stage2-evidence-contract.md
- stage2-quality-scoring-rubric.md
- stage2-reroute-rules.md
- stage2-anti-overclaim-rules.md
- stage2-ready-for-execution-verdict.yaml

Prompt 2 final verdicts:
- PLAN_HARDENED_FROM_AUDIT_READY_FOR_EXECUTION
- PLAN_HARDENED_FROM_AUDIT_WITH_PARTIAL_CONTEXT
- PLAN_NOT_READY_AUDIT_PLAN_MISMATCH
- PLAN_NOT_READY_MISSING_ACTIVE_PLAN
- PLAN_NOT_READY_MISSING_AUDIT_SUMMARY
- BLOCKED_EXTERNAL

----------------------------------------------------------------------
FULL PROMPT 3 ASSET — prompt3-controlled-execution.md
----------------------------------------------------------------------

Install this full enhanced Prompt 3 as a reusable project asset.

Title:
EXECUTION MODE — CONTROLLED TASKCARD EXECUTION, PLAN READINESS GATING, SYSTEM HEALING, VERIFICATION, EVIDENCE, QUALITY SCORING, REROUTE, AND FINAL SELF-REVIEW

You are operating in EXECUTION MODE.

Goal:
Execute the approved plan only if it is genuinely ready for safe execution. If the plan is not ready, do not force execution. Heal, normalize, and harden the plan first, then stop with an execution-ready handoff.

Core rule:
Do not blindly execute prose. First convert the plan into a controlled, taskcard-driven, gate-managed execution system.

Repository:
Use the current repository and current branch unless the user explicitly provided a different path or branch.

Operating principles:
- Act on the human’s behalf where repository governance allows it.
- Do not ask the human to perform manual review unless governance absolutely requires it.
- If a human-review step exists, first perform an agent-side verification pass yourself.
- Do not bypass tests, scanners, hooks, policy gates, or evidence requirements.
- Do not use reset, clean, destructive checkout, blind stash-pop, broad revert operations, destructive checkout, or broad overwrite operations.
- Do not mutate unrelated files.
- Do not trust prior summaries.
- Verify source files, plans, taskcards, evidence, and registry/state files directly.
- Prefer durable system fixes over one-off local patches.
- Preserve what already works.
- Do not accept prompt-only fixes as system healing.
- Do not accept advisory-only state as autonomy.
- Do not accept artifact existence as evidence of behavior.
- Do not accept below-4 quality scores.
- Do not accept prose-only final summaries.
- Do not accept missing evidence bundles.

Input priority:
1. stage2-ready-for-execution-verdict.yaml
2. stage2-enhanced-master-plan.md
3. stage2-taskcard-index.yaml
4. stage2-taskcards/*.yaml
5. stage2-execution-dag.yaml
6. stage2-lane-ownership-map.yaml
7. stage2-gate-model.md
8. stage2-verification-matrix.md
9. stage2-quality-scoring-rubric.md
10. stage2-reroute-rules.md
11. stage2-anti-overclaim-rules.md
12. active repository state
13. active governance docs
14. active taskcard/state/queue files

Phase 0 — Preflight safety and state capture:
1. Record:
   - absolute repository path
   - branch
   - HEAD commit
   - git status
   - staged files
   - untracked files
   - active worktrees if any
   - relevant plan files
   - relevant taskcards
   - relevant governance docs
   - relevant evidence/report directories
   - relevant prompt assets
   - relevant skill/agent registries
   - relevant queue/state/ledger files

2. Classify every dirty/untracked file as:
   - owned_by_this_sprint
   - unrelated_human_or_agent_work
   - stale_generated
   - unsafe_unknown

3. If unrelated or unsafe changes exist:
   - do not overwrite them.
   - continue only in a way that isolates this sprint’s work.
   - record the isolation strategy.

4. Create a run record directory for this execution/healing sprint.

Phase 1 — Readiness assessment gate:
Inspect the plan deeply and decide whether it is ready for execution.

A plan is NOT ready if any of these are true:
- goals are vague or conflict with repo authority
- tasks are not taskcard-driven
- gates are missing or weak
- verification is mostly prose
- evidence bundle requirements are missing
- state management is missing
- rollback/recovery rules are missing
- dependencies are unclear
- execution order is unsafe
- docs/skills/agent sync is missing
- plan ignores known prior findings or recent evidence
- plan depends on assumptions not verified in source files
- quality scoring is missing
- reroute rules are missing
- Prompt 1-style final assessment is missing
- evidence package closeout is missing

If the plan is not ready:
- Do not execute implementation tasks.
- Heal the plan first.
- Produce a normalized, execution-ready plan.
- Add or update taskcards.
- Add gates and acceptance criteria.
- Add verification commands.
- Add evidence-bundle requirements.
- Add internal execution management.
- Add skill/docs/agent-sync requirements.
- Add quality scoring.
- Add reroute rules.
- Stop after producing the execution handoff and evidence of plan healing.

If the plan is ready:
- Proceed to controlled execution.

Phase 2 — Plan healing requirements:
When healing the plan, make it production-grade.

The healed plan must include:
1. Normalized objective:
   - what problem is being solved
   - why it matters
   - what must not regress
   - what is explicitly out of scope

2. Root-cause model:
   - visible symptoms
   - root causes
   - structural weaknesses
   - why reruns currently become inconsistent
   - what should be preserved
   - what must be redesigned

3. Taskcard-driven state:
   - one taskcard per actionable unit
   - each taskcard has ID, owner-agent role, scope, inputs, outputs, gates, tests, evidence, quality scoring, reroute rule, and closeout status
   - no hidden work outside taskcards
   - no silently dropped items
   - defer only with explicit backlog taskcard and reason

4. Internal execution management:
   - preflight gate
   - implementation gate
   - midflight verification gate
   - pre-commit gate
   - evidence gate
   - closeout gate
   - rerun/non-regression gate
   - quality scoring gate
   - reroute gate
   - final Prompt 1-style self-review gate

5. Sync requirements:
   - update relevant skills
   - update agent instructions
   - update governance docs
   - update README or methodology docs where applicable
   - update master plan/roadmap/registry/taskcards
   - add checks preventing future drift

6. Verification:
   - exact commands to run
   - expected results
   - failure handling
   - regression coverage
   - source-code inspection requirements
   - evidence bundle validation

7. Evidence:
   - create a zip/tar evidence bundle
   - include run record, git status, changed files list, test logs, validation logs, taskcard updates, gate results, quality scores, reroute log, and final verdict
   - print the absolute evidence bundle path

Phase 3 — Controlled multi-lane execution:
Execute in controlled slices internally, without requiring manual copy-paste between slices.

Required lanes:
- Lane 0: execution coordinator and safety supervisor
- Lane A: preflight/current-state lane
- Lane B: taskcard execution lane
- Lane C: system healing lane
- Lane D: verification/QA lane
- Lane E: governance/evidence/state lane
- Lane F: docs/skills/agent-sync lane
- Lane G: work-ahead/repeatability lane
- Lane H: quality scoring and reroute lane
- Lane I: independent adversarial review lane

For each taskcard:
1. Re-read source files before editing.
2. Confirm allowed paths and forbidden paths.
3. Implement the smallest durable system fix that solves the root cause.
4. Add or update tests before claiming success.
5. Run focused tests.
6. Run broader regression tests for touched scopes.
7. Update docs/skills/agent instructions if behavior changed.
8. Update taskcard state.
9. Record evidence.
10. Score the item.
11. Reroute if any required score is below 4/5.

Do not continue past a failed gate unless:
- the failure is understood
- the fix is within scope
- the fix is recorded
- tests are rerun
- the taskcard status reflects the truth

Phase 4 — Production-grade verification:
Before closeout, run:
- formatting/lint checks where applicable
- unit tests for touched modules
- integration tests for changed workflows
- governance/policy checks
- taskcard consistency checks
- docs/skill sync checks
- evidence contract validation if available
- prompt output contract validation if available
- git status verification
- rerun or dry-run proving the system works across reruns, if applicable

Phase 5 — Quality scoring:
Score every executed item 1–5 across required dimensions:
- requirement correctness
- implementation correctness
- integration completeness
- pipeline compatibility
- governance compliance
- evidence completeness
- test coverage
- validator coverage
- repeatability
- idempotency
- downstream consumer readiness
- agentic consumption quality
- rollback/safety quality
- documentation/skill/agent-sync quality
- production readiness

Acceptance rule:
Any required dimension below 4/5 means the item is not accepted.

Reroute rule:
If any item scores below 4/5:
- mark taskcard REROUTED
- create reroute reason
- assign rework owner
- repair if safe
- rerun verification
- rescore
- accept only after all required dimensions are >= 4/5
- if impossible due to external blocker, classify BLOCKED_EXTERNAL with evidence

Phase 6 — Commit rules:
Commit only if:
- repo policy allows commits
- all gates pass
- unrelated files are excluded
- evidence exists
- taskcards and docs are updated
- final git status is understood

If direct commit is not allowed:
- stage only allowed files if policy permits
- provide the exact proposed commit message

Commit message format:
<type>(<scope>): <short durable summary>

Include:
- what root cause was fixed
- what tests prove it
- what evidence bundle was created

Phase 7 — Final Prompt 1-style self-review:
At the end, produce a structured self-review in the Prompt 1 pattern.

It must include:
- what was achieved
- what this proves
- effect on final outcome
- L1 execution issues
- L2 integration/connect-point issues
- L3 system weakness issues
- evidence quality verdict
- final sprint summary YAML

It must not be prose-only.

Required Prompt 3 outputs:
- stage3-preflight-state.md
- stage3-execution-log.md
- stage3-lane-status.yaml
- stage3-taskcard-status.yaml
- stage3-verification-results.md
- stage3-quality-evaluations.yaml
- stage3-reroute-log.yaml
- stage3-evidence-manifest.yaml
- stage3-final-sprint-summary.yaml
- stage3-final-sprint-summary.md
- stage3-self-review-l1-execution-issues.yaml
- stage3-self-review-l2-integration-issues.yaml
- stage3-self-review-l3-system-weaknesses.yaml
- declaration-review-package-<run_id>.zip

Prompt 3 final verdicts:
- EXECUTION_COMPLETE_VERIFIED
- EXECUTION_COMPLETE_WITH_LIMITATIONS
- EXECUTION_REROUTED_REWORK_REQUIRED
- PLAN_NOT_READY_HEALED_ONLY
- BLOCKED_BY_FAILED_GATE
- BLOCKED_BY_REPO_SAFETY
- BLOCKED_EXTERNAL
- NEEDS_HUMAN_DECISION

----------------------------------------------------------------------
LOOP CONTROLLER ASSET — prompt-loop-controller.md
----------------------------------------------------------------------

Install a reusable loop controller prompt and contract.

Title:
POST-SPRINT LOOP CONTROLLER — SUMMARY PARSING, NEXT-STAGE DECISION, REROUTE, AND ALL-GREEN ACCEPTANCE

Mission:
Read Prompt 1, Prompt 2, and Prompt 3 outputs. Determine the next required stage automatically. Do not ask the user which prompt to run.

Inputs:
- stage1 outputs if present
- stage2 outputs if present
- stage3 outputs if present
- evidence manifest
- taskcard index
- quality evaluations
- reroute log
- final sprint summary YAML
- final sprint summary markdown
- evidence package path
- blocker reports

Summary classifications:
- STRUCTURED_ALL_GREEN
- STRUCTURED_NOT_GREEN
- PROSE_ONLY
- MISSING
- CONTRADICTORY
- EVIDENCE_MISSING
- SCORES_MISSING
- TASKCARDS_INCOMPLETE
- BLOCKED_EXTERNAL

Loop decisions:
- If Prompt 3 summary is PROSE_ONLY:
  run Prompt 2 then Prompt 3.

- If Prompt 3 summary is MISSING:
  run Prompt 1 then Prompt 2 then Prompt 3.

- If Prompt 3 summary is STRUCTURED_NOT_GREEN:
  feed open issues into Prompt 2, then run Prompt 3.

- If Prompt 3 summary has SCORES_MISSING:
  run or rerun quality scoring, then reroute or accept.

- If Prompt 3 summary has EVIDENCE_MISSING:
  run evidence packaging and evidence validation lane.

- If Prompt 3 taskcards are incomplete:
  run Prompt 2.

- If Prompt 3 has any score below 4/5:
  reroute to rework and run Prompt 3 for affected taskcards.

- If Prompt 3 is STRUCTURED_ALL_GREEN:
  run independent adversarial review.
  Accept only if adversarial review passes.

- If BLOCKED_EXTERNAL:
  verify blocker, package evidence, and stop.

Invalid final states:
- NEXT_PROMPT_NEEDED
- HUMAN_REVIEW_NEEDED_BEFORE_AGENT_REVIEW
- PROSE_ONLY_ACCEPTED
- SUMMARY_MISSING_ACCEPTED
- SCORE_BELOW_4_ACCEPTED
- EVIDENCE_PACKAGE_MISSING_ACCEPTED
- PLAN_UPDATED_NOT_EXECUTED
- EXECUTED_NOT_EVALUATED
- PROMPT_ASSETS_DISCONNECTED
- TASKCARDS_MISSING_ACCEPTED

Required outputs:
- loop-summary-classification.yaml
- loop-decision.yaml
- loop-open-items.yaml
- loop-next-stage-inputs.md
- loop-final-state-verdict.md

----------------------------------------------------------------------
PROJECT ADAPTER REQUIREMENT
----------------------------------------------------------------------

Create or harden:
- project-adapter-template.md
- project-adapter-contract.md
- project adapter config if repository supports configs

Adapter must define:
- project_name
- repo_root
- evidence_paths
- plan_paths
- taskcard_paths
- prompt_folder_path
- prompt_registry_path
- test_commands
- validator_commands
- build_commands
- governance_commands
- protected_paths
- allowed_mutation_paths
- docs_paths
- skills_paths
- agent_instruction_paths
- final_package_format
- project_specific_gates
- external_blockers

The loop must not be hardcoded to one project.

----------------------------------------------------------------------
IMPLEMENTATION RECON
----------------------------------------------------------------------

Before implementing anything, inspect current project support.

Search for:
- sprint closeout hooks
- evidence bundle builders
- declaration-review-package builders
- audit prompts
- plan-hardening prompts
- execution prompts
- prompt registries
- skill registries
- taskcard generators
- taskcard validators
- state machines
- queue files
- continuation signals
- supervisor cycles
- validators
- quality graders
- reroute/rework logic
- summary parsers
- loop controllers
- evidence contracts
- governance docs
- project adapters
- CI/workflow hooks
- prior sprint evidence

Produce:
- current-cycle-machinery-map.md
- existing-support-audit.md
- prompt-asset-installation-plan.md
- partial-capability-register.yaml
- missing-capability-register.yaml
- broken-capability-register.yaml
- reusable-cycle-architecture.md
- project-adapter-assessment.md
- governance-gap-analysis.md

Classify each capability:
- EXISTS_AND_VERIFIED
- EXISTS_NOT_WIRED
- EXISTS_BUT_WEAK
- EXISTS_BUT_PROMPT_ONLY
- EXISTS_BUT_ARTIFACT_ONLY
- PARTIAL
- MISSING
- BROKEN
- BLOCKED_EXTERNAL

----------------------------------------------------------------------
CONTROLLED MULTI-LANE EXECUTION MODEL
----------------------------------------------------------------------

Use controlled lanes, not unmanaged swarm execution.

Lane 0 — Autonomous sprint-loop coordinator
- owns prompt installation
- owns loop design
- owns final state
- prevents premature stop
- coordinates all lanes
- verifies the user no longer needs to manually choose Prompt 1, 2, or 3

Lane A — Existing machinery recon
- maps what already exists
- classifies existing support

Lane B — Prompt asset installation
- creates/enhances Prompt 1, Prompt 2, Prompt 3 files
- registers them where appropriate

Lane C — Stage 1 engine
- implements/hardens strict audit and L1/L2/L3 issue model

Lane D — Stage 2 engine
- implements/hardens plan hardening, master plan delta, and taskcard generation

Lane E — Stage 3 engine
- implements/hardens controlled execution, multi-lane execution, and final self-review

Lane F — Quality scoring and reroute
- implements/hardens 4/5 quality scoring and reroute/rework

Lane G — Summary parser and loop controller
- implements/hardens automatic next-stage decision logic

Lane H — Evidence bundle manager
- implements/hardens evidence package creation and validation

Lane I — Project adapter and portability
- ensures the loop works across projects

Lane J — Governance/docs/skills/agent-sync
- updates governance, docs, skills, prompts, and agent instructions

Lane K — Verification and negative controls
- proves fail-closed behavior

Lane L — Full-loop pilot
- proves Prompt 1 → Prompt 2 → Prompt 3 → loop decision

Lane M — Independent adversarial review
- tries to prove the system still requires manual user orchestration

----------------------------------------------------------------------
TASKCARD GOVERNANCE
----------------------------------------------------------------------

Every implementation or hardening item must have a taskcard.

Every taskcard must include:
- taskcard ID
- component
- stage
- lane
- supervisor
- source gap
- objective
- root cause
- allowed paths
- forbidden paths
- inputs
- outputs
- dependencies
- implementation steps
- verification commands
- negative controls
- quality dimensions affected
- evidence outputs
- rollback plan
- status
- acceptance criteria

Valid taskcard statuses:
- PROPOSED
- READY
- BLOCKED
- IN_PROGRESS
- IMPLEMENTED
- VERIFIED
- SCORED
- REROUTED
- REWORKING
- REWORKED
- ACCEPTED
- ACCEPTED_WITH_LIMITATIONS
- BLOCKED_EXTERNAL
- DEFERRED_WITH_REASON

Invalid transitions must fail.

----------------------------------------------------------------------
NEGATIVE CONTROLS
----------------------------------------------------------------------

Prove the system fails closed for these cases:

1. Prompt 3 summary is prose-only.
   Expected: loop controller chooses Prompt 2 then Prompt 3.

2. Prompt 3 summary is missing.
   Expected: loop controller chooses Prompt 1 then Prompt 2 then Prompt 3.

3. Summary claims all green but issue register has blockers.
   Expected: acceptance blocked.

4. Quality score is 3/5 in one required dimension.
   Expected: item rerouted to rework.

5. Evidence bundle is missing.
   Expected: acceptance blocked.

6. Taskcard missing for actionable work.
   Expected: execution blocked or taskcard generated first.

7. Prompt 1 issue has no root cause.
   Expected: Prompt 1 output rejected.

8. Prompt 2 issue has no solution or taskcard.
   Expected: Prompt 2 output rejected.

9. Prompt 3 taskcard executed but not evaluated.
   Expected: final acceptance blocked.

10. Human review requested before agent-side review.
    Expected: agent-side review forced first.

11. Evidence declaration references missing files.
    Expected: evidence package invalid.

12. Rerouted item marked accepted without re-evaluation.
    Expected: acceptance blocked.

13. Loop controller returns NEXT_PROMPT_NEEDED.
    Expected: invalid state; controller must choose next stage.

14. Project adapter lacks validation commands.
    Expected: adapter incomplete; execution blocked or adapter repair required.

15. Prompt 3 completes without Prompt 1-style self-assessment.
    Expected: loop requires structured Prompt 1-compatible self-review before acceptance.

16. Master plan delta has no linked issue IDs.
    Expected: plan update rejected.

17. Taskcard state transition skips VERIFIED or SCORED.
    Expected: state transition rejected.

18. Prompt asset exists but is not registered or reachable by loop controller.
    Expected: prompt asset classified EXISTS_NOT_WIRED and acceptance blocked until wired or taskcarded.

19. Prompt 2 creates prose recommendations without taskcards.
    Expected: plan hardening output rejected.

20. Prompt 1 classifies achievement without proof level.
    Expected: audit output rejected.

21. Stage 3 accepts a taskcard without evidence output.
    Expected: acceptance blocked.

22. Evidence package exists but manifest does not match contents.
    Expected: package invalid.

23. Summary parser sees contradiction between all-green summary and reroute log.
    Expected: classification CONTRADICTORY and acceptance blocked.

24. Loop controller cannot determine next stage.
    Expected: invalid controller behavior; must produce BLOCKED_EXTERNAL only if true blocker exists, otherwise repair controller.

----------------------------------------------------------------------
FULL-LOOP PILOT PROOF
----------------------------------------------------------------------

Run a controlled pilot on one representative completed sprint or fixture sprint.

The pilot must prove the actual loop, not only isolated functions.

Pilot must demonstrate:
- completed sprint intake works
- prompt assets are found in project prompt folder
- Prompt 1 asset is found and usable
- Prompt 1 produces achievement summary
- Prompt 1 produces proof summary
- Prompt 1 produces final outcome impact summary
- Prompt 1 produces L1/L2/L3 issues
- issues include evidence and root causes
- Prompt 2 asset is found and usable
- Prompt 2 reads Prompt 1 outputs
- Prompt 2 creates master-plan delta
- Prompt 2 creates taskcards
- Prompt 2 creates verification matrix
- Prompt 2 creates anti-overclaim rules
- Prompt 3 asset is found and usable
- Prompt 3 executes at least one taskcard or controlled fixture taskcard
- quality evaluator scores result
- one below-4 score causes reroute
- rerouted item is reworked and rescored
- Prompt 3 emits structured final sprint summary
- summary parser classifies output
- loop controller chooses next stage correctly
- evidence bundle is generated and validated
- all-green acceptance is allowed only when all gates agree
- adversarial review passes

Produce:
- pilot-plan.md
- pilot-fixture-or-sprint-selection.md
- pilot-run-log.md
- pilot-results.md
- negative-control-results.md
- all-green-acceptance-proof.md

----------------------------------------------------------------------
EVIDENCE REQUIREMENTS
----------------------------------------------------------------------

Create evidence root:
.local/evidences/post-sprint-autonomy-loop-<YYYYMMDD>-<shortsha-or-counter>/

Required artifacts:
- evidence-declaration.yaml
- current-cycle-machinery-map.md
- existing-support-audit.md
- prompt-asset-installation-plan.md
- partial-capability-register.yaml
- missing-capability-register.yaml
- broken-capability-register.yaml
- reusable-cycle-architecture.md
- project-adapter-assessment.md
- governance-gap-analysis.md
- prompt1-post-sprint-audit.md
- prompt2-plan-hardening.md
- prompt3-controlled-execution.md
- prompt-loop-controller.md
- prompt-output-contracts.md
- project-adapter-template.md
- stage1-issue-model-schema.yaml
- stage2-taskcard-contract.yaml
- stage3-quality-scoring-rubric.yaml
- taskcard-state-machine.yaml
- summary-parser-contract.yaml
- loop-decision-state-machine.yaml
- evidence-bundle-contract.yaml
- project-adapter-contract.yaml
- governance-contract.yaml
- taskcards/index.yaml
- taskcards/*.yaml
- implementation-log.md
- verification-results.md
- negative-control-results.md
- pilot-plan.md
- pilot-run-log.md
- pilot-results.md
- all-green-acceptance-proof.md
- adversarial-review.md
- final-verdict.md
- next-execution-prompt.md
- declaration-review-package-<run_id>.zip

evidence-declaration.yaml must include:
- run_id
- repo path
- branch
- base commit
- prompt folder selected
- prompt assets created or updated
- prompt registry updated: true/false
- stage1 contract installed: true/false
- stage2 contract installed: true/false
- stage3 contract installed: true/false
- loop controller installed or taskcarded
- summary parser installed or taskcarded
- quality scoring installed or taskcarded
- reroute controller installed or taskcarded
- project adapter installed or taskcarded
- negative controls run
- pilot run
- evidence package created
- final verdict

----------------------------------------------------------------------
EXECUTION PHASES
----------------------------------------------------------------------

Phase 0 — Baseline and safety
- capture repo state
- identify current sprint/evidence roots
- identify protected files
- identify existing lifecycle
- create evidence root
- create taskcard index
- do not mutate source until taskcards exist

Phase 1 — Existing machinery deep recon
- inspect existing support for Prompt 1, Prompt 2, Prompt 3, loop decisions, evidence, summary parsing, taskcards, scoring, and reroute
- classify every capability
- preserve what works
- identify what is missing, partial, weak, prompt-only, artifact-only, or broken

Phase 2 — Prompt asset installation
- create/enhance prompt files under autonomous/supervisor/prompts/ or equivalent
- include full enhanced Prompt 1
- include full enhanced Prompt 2
- include full enhanced Prompt 3
- include loop controller prompt
- include output contracts
- include project adapter template
- register prompts in project registry if available

Phase 3 — Contracts and schemas
- create output contracts for Prompt 1, Prompt 2, Prompt 3
- create issue schema
- create taskcard state machine
- create summary parser contract
- create loop controller contract
- create project adapter contract
- create evidence bundle contract
- create governance contract

Phase 4 — Implementation/hardening
- implement or harden the highest-leverage safe slice
- connect prompt assets to existing machinery where available
- avoid broad rewrites
- preserve working components
- ensure disconnected prompt assets are not falsely accepted

Phase 5 — Verification
- run focused tests or local checks
- validate prompt files exist
- validate prompt registry if present
- validate schemas/contracts
- validate taskcard state transitions
- validate summary classification
- validate scoring and reroute behavior
- validate evidence package behavior

Phase 6 — Negative controls
- run all fail-closed cases listed above
- record results
- repair failed negative controls where safe
- rerun after repair

Phase 7 — Full-loop pilot
- run representative sprint/fixture through Prompt 1, Prompt 2, Prompt 3, summary parser, loop controller, quality evaluator, reroute, and evidence packaging

Phase 8 — Hardening and reverification
- fix weak points found in verification or pilot
- rerun affected checks
- rerun pilot if needed

Phase 9 — Independent adversarial review
- try to prove user manual orchestration is still required
- try to prove prose-only summary can pass
- try to prove below-4 score can pass
- try to prove missing evidence can pass
- try to prove prompt assets are disconnected
- try to prove Prompt 2 can create prose-only tasks
- repair or record blockers

Phase 10 — Final closeout
- package evidence
- produce final verdict
- produce next execution prompt

----------------------------------------------------------------------
FINAL VERDICT OPTIONS
----------------------------------------------------------------------

Use one:

- POST_SPRINT_AUTONOMY_LOOP_IMPLEMENTED_AND_PILOT_PROVED
  The reusable Prompt 1 → Prompt 2 → Prompt 3 loop exists, prompt assets are installed, loop decision works, negative controls pass, and pilot proves the flow.

- POST_SPRINT_AUTONOMY_LOOP_HARDENED_WITH_LIMITATIONS
  The system is materially improved and reusable, but non-critical limitations remain and are taskcarded.

- POST_SPRINT_AUTONOMY_LOOP_PARTIAL_REWORK_REQUIRED
  Important components are missing, weak, disconnected, or not pilot-proved.

- PLAN_ONLY_HANDOFF_PRODUCED
  Implementation could not safely proceed, but complete taskcards/contracts/plan were produced.

- BLOCKED_EXTERNAL
  A true external blocker prevents completion after all safe local work is exhausted.

----------------------------------------------------------------------
FINAL RESPONSE FORMAT
----------------------------------------------------------------------

Return:
1. Final verdict.
2. Prompt asset folder used.
3. Prompt 1 installed/enhanced status.
4. Prompt 2 installed/enhanced status.
5. Prompt 3 installed/enhanced status.
6. Existing machinery found.
7. Missing/partial/broken machinery.
8. Loop controller behavior.
9. Summary parser behavior.
10. Quality scoring and reroute behavior.
11. Project adapter behavior.
12. Evidence bundle behavior.
13. Negative controls and results.
14. Pilot proof summary.
15. Evidence package path.
16. Remaining limitations.
17. Next execution prompt.

Final acceptance rule:
The system is not accepted unless the project now has reusable full prompt assets and a proven or taskcarded path to automatically run Prompt 1 → Prompt 2 → Prompt 3 after every sprint without requiring the user to manually decide which prompt to run next.

Do not trim the prompt assets.
Do not summarize Prompt 1, Prompt 2, or Prompt 3 into weak substitutes.
Install full enhanced reusable prompts with output contracts.
Prove they are connected, reusable, and enforceable.
