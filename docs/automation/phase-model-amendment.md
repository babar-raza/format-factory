# Phase Model Amendment — MODE 0-5

## Amendment Summary

The original plan used letter-based phases (A-E) with overly broad human gates.
This amendment replaces them with numbered MODE 0-5 and internal promotion rules,
reducing unnecessary human gates from 5 to 2 (MODE 4 and MODE 5 only).

## MODE 0: PLAN_HEALING

**Purpose:** Plan normalization only. No activation. No MCP. No TM. No Ruflo.

**Authorized by:** User (one-time, this sprint)

**What happens:**
- Plan status normalized to PLAN_HEALED_READY_FOR_SINGLE_GO_EXECUTION_HANDOFF
- TC-SUP-000 through TC-SUP-019 taskcard system defined
- C0-C10 lane swarm model with file ownership matrix
- Verification matrix V00-01 through V00-25

**Promotion:** If verification matrix passes → MODE 1 authorized (no human gate)

## MODE 1: LOCAL_SUPERVISOR_FOUNDATION_IMPLEMENTATION

**Purpose:** Implement working minimum supervisor loop. No stubs for core scripts.

**Authorized by:** MODE 0 verification matrix passing (no human gate)

**What is implemented:**
- All 6 supervisor scripts fully functional
- All 4 JSON schemas valid
- All 5 prompt templates with [INSERT_...] placeholder convention
- Bridge validators + tests (27 tests passing)
- .supervisor/ config, policies, memory, sprint-loop files

**Evidence tested against:** R77/R78 evidence bundle structure (validated during replay)

**Promotion:** If MODE 1 verification matrix passes → MODE 2 authorized (no human gate)

## MODE 2: LOCAL_SUPERVISOR_REPLAY_AND_HARDENING

**Purpose:** Replay supervisor against known prior evidence bundle. Prove idempotence.

**Authorized by:** MODE 1 evidence (no human gate)

**What is proven:**
- `supervisor_loop.py run-on-latest` exits 0 (or exits 1 if no bundle found — acceptable limitation)
- Evidence-review.json schema-validates
- Taskmaster export schema-validates
- Ruflo lanes export schema-validates
- Idempotent rerun produces identical output
- Contradiction detection handles 9 synthetic scenarios

**Limitation if no real bundle:** `SUPERVISOR_E2E_ACCEPTED_WITH_LIMITATIONS` verdict
(synthetic fixture bundles exercise all code paths; real bundle replay deferred to MODE 5)

**Promotion:** If MODE 2 verification passes → MODE 3 authorized (no human gate)

## MODE 3: TASKMASTER_RUFLO_LOCAL_DRY_RUN

**Purpose:** Version resolution, disposable Ruflo rehearsal, TM import dry run.

**Authorized by:** MODE 2 evidence (no human gate)

**What happens:**
- `npm show task-master-ai version` — version resolution without starting MCP server
- `claude-flow mcp tools` or `claude-flow mcp status` in temp directory
- TM task import format test (schema validation only — no active daemon)
- Ruflo lane ingestion test (schema validation only — no daemon)
- No .vscode/mcp.json created
- No .taskmaster/ in repo root
- Temp dir used and cleaned up after

**Promotion:** MODE 4 requires EXPLICIT human approval (first external gate)

## MODE 4: ACTIVE_MCP_ACTIVATION

**Purpose:** Register MCP servers. Validate rollback + process hygiene.

**Authorized by:** Explicit human approval (MCP is a system-level change)

**What happens:**
- .vscode/mcp.json created with claude-code-oauth or provider-key configuration
- Task Master AI registered as MCP server
- Ruflo registered as MCP server
- Process hygiene validated (daemon lifecycle, port cleanup)
- Rollback procedure tested and documented

**Promotion:** MODE 5 requires EXPLICIT human approval

## MODE 5: AUTONOMOUS_SPRINT_LOOP_RC

**Purpose:** One complete autonomous loop. Evidence-gated. Human sees final dashboard only.

**Authorized by:** Explicit human approval

**What happens:**
- Full sprint cycle without human handoffs
- `supervisor_loop.py run-on-latest` on real evidence bundle
- TM task graph populated from supervisor export
- Ruflo lanes active for sprint coordination
- Human receives final approval-gates.md + session-resume.md only
- Human approves or rejects continuation at next true gate

## Human Approval Policy

Stop for human ONLY at:
- Credentials (API keys, secrets, paid service config)
- Paid API access required
- MCP activation (MODE 4 minimum)
- Push/merge/deploy to remote
- Destructive operations (rm -rf, force-push, schema deletion)
- Governance conflicts unresolvable locally
- Format Factory gate approval (G11-G and above)

Do NOT stop between MODE 0-3 if plan + repo governance + evidence gates authorize continuation.

## Internal Promotion Criteria

MODE 0 → MODE 1: Plan evidence bundle BUNDLE_VALIDATION: PASS + final-verdict.md confirmed
MODE 1 → MODE 2: 27 tests pass + 6 scripts compile + schemas validate + supervisor compiles
MODE 2 → MODE 3: run-on-latest exits 0 or 1 (limitation) + replay idempotence confirmed
MODE 3 → MODE 4: **HUMAN GATE** — MCP activation requires explicit written approval
