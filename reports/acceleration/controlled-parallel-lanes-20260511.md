# Controlled Parallel Lanes and Sprint-Sizing Policy
**Date:** 2026-05-11
**Sprint:** FODT-GATE10-REVIEW-PACKET-AND-NEXT-LANE-ACCELERATION-001

---

## 1. Diagnosis: Why Progress Slowed

### Root Causes
1. **Too many micro-proof repairs.** Every metadata note (candidate path, byte size, count wording) triggered a new repair sprint with full evidence contract, metadata directory, and bundle. Each micro-sprint consumed a full agent session for near-zero implementation value.

2. **Serial-only execution.** Every action waited for the prior sprint to close. Gate packet preparation waited for proof repair, which waited for IV, which waited for implementation. No parallelism was attempted.

3. **Proof perfection treated as blocker.** If a final proof referenced the candidate bundle path (with identical content), the bundle was classified as defective even though it validated directly. This created a "defect → repair sprint → new proof → new potential note" loop.

4. **IV and repair split too aggressively.** IV sprints were forbidden from applying narrow non-behavior repairs (like adding a missing README), forcing a separate repair session. Then the repair needed its own IV, creating recursive verification demand.

5. **No explicit lane scheduler.** All work funneled through one lane (main product stream). Secondary streams (playbook, governance, tooling) couldn't proceed because the main stream held the commit/review queue.

---

## 2. New Sprint-Sizing Policy

### Combine Related Work
- **IV may include narrow repair** if: (a) the repair does not change product behavior, (b) the repair is documented in the IV metadata, (c) the repaired code passes the same tests.
- **Gate packet may include next-lane planning** (this sprint is an example).
- **Source execution should include source + tests + state update + evidence** in one sprint.

### Classify Instead of Repair
- **Implementation defect** → BLOCKER (new repair sprint required)
- **Gate-state contradiction** → BLOCKER (stop and report)
- **Final bundle cannot validate directly** → BLOCKER (repair required)
- **Candidate/final path note** → METADATA_NOTE (record in verdict, do not create new sprint)
- **Byte size note** → METADATA_NOTE (if final bundle validates directly)
- **Count wording note** → METADATA_NOTE (if actual validation passes)
- **Missing README** → NARROW_REPAIR (include in IV sprint)

### Reserve Separate Repair Sprints Only For
1. Implementation bugs that change parser behavior
2. Gate-state contradictions (registry says approved but shouldn't be)
3. Final bundle cannot pass `validate_evidence_bundle.py --check-no-pending`
4. Source tests fail

---

## 3. Controlled Parallel Lanes

### Lane A: Main Product Source and Gate Stream
**Owner:** Primary agent session
**Scope:** Format source, tests, gates, registry, master-plan
**Current:** FODT Gate 10 packet prepared → awaiting human decision
**Next after Gate 10 approval:**
- Record Gate 10 approval in registry and master-plan
- Prepare FODT Gate 11 commercial readiness assessment
- Next format acquisition (if new format authorized)

### Lane B: Secondary Playbook Stream
**Owner:** Separate agent session (or same session after Lane A idle)
**Scope:** schemas/playbook/, tools/playbook/, tests/playbook/, docs/playbook-layer.md
**Current:** S-F2F-05 queued (ODF-flat family playbook)
**Constraint:** Must NOT touch product source, registry gate fields, or master-plan gate sections
**Safe because:** Playbook files are structurally isolated from product source

### Lane C: Governance and Backlog Stream
**Owner:** Separate agent session (or same session when authorized)
**Scope:** GOV-REVERT-002 planning, governance docs, AGENTS.md/GOVERNANCE.md policy updates
**Current:** GOV-REVERT-002 exists but does not block Gate 10
**Constraint:** No stash apply/pop, no hidden-work recovery unless explicitly authorized
**Safe because:** Governance documents don't affect product code or gate states

### Lane D: Evidence Tooling Quality Stream
**Owner:** Any session when Lane A is idle
**Scope:** tools/evidence/, tests/evidence/
**Current:** Two-pass final-proof builder could be improved to auto-replace candidate paths
**Proposed improvement:** `build_evidence_bundle.py` two-pass mode that:
  1. Builds candidate
  2. Validates candidate
  3. Writes proof with candidate output + note about final
  4. Rebuilds final
  5. Validates final
  6. Verifies proof references correct final path
**Constraint:** Tooling changes must not affect existing validated bundles

---

## 4. Concurrency Rules

1. **One writer per file group.** No two lanes may modify the same file simultaneously.
2. **Shared files require merge coordination.** `plans/master-plan.md` and `registry/format-registry.yaml` are shared. Only one lane may modify them at a time. If Lane B needs to update master-plan, it must wait for Lane A to be idle.
3. **Isolated worktrees recommended.** For true parallel execution, use `git worktree` per lane.
4. **Same worktree: one execution writer at a time.** If using a single worktree, only one lane executes at a time. Other lanes may read.
5. **Verification-only lanes can run read-only.** An IV sprint can run read-only checks in parallel with Lane B work, as long as it doesn't commit.

---

## 5. Larger Sprint Templates

### Template A: Source + Tests + State + Evidence (1 sprint)
Scope: Implement source, write tests, update registry/master-plan, build evidence bundle.
Replaces: Implementation sprint + state update sprint + evidence sprint (3 → 1).

### Template B: IV + Narrow Repair + Proof (1 sprint)
Scope: Independent verification of prior sprint. If narrow non-behavior repair needed (e.g., missing README), apply it. Build proof bundle.
Replaces: IV sprint + repair sprint + proof repair sprint (3 → 1).

### Template C: Gate Packet + Next-Lane Planning (1 sprint)
Scope: Prepare human review packet. Create acceleration or next-lane plans. Update master-plan.
Replaces: Gate packet sprint + planning sprint (2 → 1).

### Template D: Multi-Gate Verification (1 sprint)
Scope: If multiple gates are ready for verification (e.g., both FODS Gate 11 planning and FODT Gate 10 planning), verify both in one sprint with shared baseline.
Replaces: Separate verification sprints per gate (N → 1).

---

## 6. Stop Conditions

Any lane must stop immediately if:
1. Implementation defect discovered (product tests fail)
2. Gate-state contradiction found (registry vs. actual state)
3. Dirty unknown files appear (UNKNOWN_REQUIRES_STOP classification)
4. Hidden work overlaps the active lane's file scope
5. Final bundle cannot validate directly
6. Source tests fail after a change
7. Another lane has modified a shared file since baseline was taken

---

## 7. New Expected Cadence

| Old Pattern | New Pattern |
|-------------|-------------|
| Implementation → State update → Evidence → IV → Repair → Proof repair → Gate packet | Implementation+State+Evidence → IV+Repair+Proof → Gate packet+Planning |
| 6-7 sprints per gate | 2-3 sprints per gate |
| 1 sprint = 1 narrow action | 1 sprint = 1 complete milestone |
| Every metadata note = new sprint | Metadata notes classified, not repaired unless blocking |
| Serial-only | Safe parallel lanes where file scopes don't overlap |
