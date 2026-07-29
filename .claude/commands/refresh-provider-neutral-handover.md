---
version: "1.0"
last-updated: "2026-07-29"
phase-available: "all"
gate-required: null
skill_type: DOCUMENT_PIPELINE
risk_level: MEDIUM
created-by: TC-FF6-HANDOVER-CLAUDE-001
generated_by: codex
visibility: generated
---

# /refresh-provider-neutral-handover

Refresh a tracked mission handover from live canonical evidence so Claude,
Codex, or another governed executor can resume at the same clean checkpoint.

## Required inputs

- `mission_id`
- `source_checkpoint`
- `canonical_remote`
- `canonical_branch`
- `controller_path`
- `journal_path`
- `current_taskcard`
- `exact_next_task`
- `packet_root`

## Execution

1. Verify the source checkpoint exists on the canonical remote and branch.
2. Read the goal, controller, complete journal, current gaps, current taskcard,
   proof manifests, operating contract, and live coordination status.
3. Recompute the event chain, task status, promotion state, proof digests, and
   unresolved gaps. Do not copy status from the old packet.
4. Update every stale packet statement, including start instructions, state
   machine position, achieved work, remaining work, exact next task, validation
   commands, known failures, and coordination rules.
5. Keep the packet derived: canonical repository state always wins.
6. Generate LF-normalized SHA-256 values for every packet file except the
   manifest itself, avoiding self-referential hashes.
7. Validate internal links, YAML/JSON parsing, packet hashes, event chain,
   task registration, GitLab ancestry, and forbidden-path preservation.
8. Commit only explicit packet/control files and push only to GitLab main after
   a remote ancestry check.

## Invariants

- One absolute `START-HERE.md` path reaches every other handover artifact.
- The packet never claims that planning, compilation, tests, or file presence
  prove a production library.
- Completed work, unresolved work, blocked work, and baseline-known failures
  are separate.
- The exact next task is registered and executable without conversation memory.
- No provider identity, provider-local branch, ignored file, or chat transcript
  is required to resume.
- No source, gate, certification, or promotion state changes.
- A packet commit may cite its source checkpoint; it must not claim a
  self-referential commit hash for its own final bytes.

## Allowed paths

- `plans/codex/handover/**`
- `taskcards/TC-FF6-HANDOVER-CLAUDE-001.md`
- `taskcards/index.yaml`
- `.local/transcripts/refresh-provider-neutral-handover-*.json`

Canonical goal, controller, journal, taskcards, manifests, source, tests,
registry, and evidence are read-only inputs.

## Forbidden paths

- `src/**`
- product tests
- format contracts and SAL stores
- package or release metadata
- gate, certification, approval, or promotion records
- GitHub remotes and non-main branches

## Mandatory validation

- packet internal links resolve;
- manifest hashes match LF-normalized packet bytes;
- YAML and JSON parse;
- controller and event journal validate through the cited event;
- source checkpoint is an ancestor of `origin/main`;
- exact next task exists in `taskcards/index.yaml`;
- transcript validates;
- worktree contains no unexplained changes.
