# Agent Execution Handoff Standard

**Document type:** Execution Standard
**Created:** 2026-05-08 (memory-planning-methodology-and-agent-handoff sprint)
**Visibility:** internal
**Authority:** This document defines how to write, structure, and use execution handoff prompts in format-factory.

---

## 1. What an Execution Handoff Is

An execution handoff is a self-contained prompt that an agent can execute from start to finish without requiring mid-task human intervention. It encodes:

- what the agent must read before starting.
- what the agent is authorized to do.
- what the agent is forbidden to do.
- every execution step with exact commands.
- every validation check with expected output.
- every taskcard update.
- the evidence contract and bundle requirements.
- stop conditions for every gate.
- the final response format including the evidence bundle path.

---

## 2. When to Use It

Use an execution handoff when:

1. The plan is fully hardened (all plan quality checks pass -- see docs/plan-hardening-checklist.md).
2. The human has authorized execution by running the prompt.
3. The scope is narrow enough to commit clearly.
4. The evidence contract is defined.
5. The expected output format is known.

Do NOT use an execution handoff for:

- planning sessions (use PLAN MODE prompts instead).
- exploratory or investigative work without a defined output.
- work that requires mid-task human decisions that cannot be pre-specified.

---

## 3. Difference Between Plan Prompt and Execution Prompt

| Dimension | Plan Prompt | Execution Prompt |
|---|---|---|
| Mode label | PLAN MODE ONLY | EXECUTION MODE |
| Creates repo files | NO | YES |
| Creates evidence bundle | NO | YES |
| Commits | NO | YES (if authorized) |
| Pushes | NO | NO (unless explicitly authorized) |
| Stop conditions | Produces list of issues | Produces BLOCKED state |
| Output | Hardened plan doc or analysis | Committed files + evidence bundle |
| Self-challenge | Optional | Required |

---

## 4. How to Convert Prose Plan to Execution-Ready Prompt

Step 1: Read all referenced files in the plan. Do not assume the plan is accurate.

Step 2: Run git status. Classify every dirty file as MEMORY_METHOD_ALLOWED, MAIN_SPRINT_OWNED, or UNKNOWN.

Step 3: For each prose instruction, convert to an executable form:

| Prose | Execution Form |
|---|---|
| "Check if the format is documented" | "Read docs/format-understanding-layer.md lines 1-50. If it does not exist, stop with MISSING_FILE." |
| "Update the registry" | "Edit registry/format-registry.yaml: set gate_X.status to Y. Verify with grep." |
| "Validate the bundle" | "Run: python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <path>. Expected: BUNDLE_VALIDATION: PASS." |
| "Make sure the tests pass" | "Run: python -m pytest tests/evidence/ -v. Expected: all tests PASS." |
| "Commit the changes" | "Run: git add <exact files>. Run: git commit -m '<message>'. Run: git status to verify clean." |

Step 4: Add forbidden paths for every file that must not be touched.

Step 5: Add a self-challenge section (minimum 17 questions, answered YES/NO).

Step 6: Add the final response format ending with EVIDENCE_BUNDLE: <absolute Windows path to zip>.

---

## 5. How to Prevent Agent Drift

Agent drift is when an agent gradually expands scope beyond what was authorized. Prevent it with:

1. Explicit forbidden paths list. The agent must not touch them regardless of what it discovers.
2. Hard prohibitions labeled clearly. Hard prohibitions override all other instructions.
3. No broad commands. Do not include "clean up any stale files" or "fix any issues found." Be exact.
4. Stop conditions. If a check fails, the agent must stop and not auto-fix.
5. Scope labels. Every section should state explicitly: "This section is authorized. No other changes to X are authorized."

---

## 6. How to Prevent Cross-Sprint Contamination

Cross-sprint contamination is when MAIN SPRINT work leaks into a MEMORY SPRINT, or SECONDARY SPRINT work appears in a MAIN SPRINT.

Prevent with:

1. Explicit sprint type at the top of the prompt.
2. Hard prohibition against the other stream. Example: "Do not execute SECONDARY SPRINT S-F2F work."
3. Dirty-file classification before staging. Classify every file as MEMORY_METHOD_ALLOWED, MAIN_SPRINT_OWNED, or SECONDARY_SPRINT_OWNED before running git add.
4. Separate commit per stream. MEMORY SPRINT files are committed separately from MAIN SPRINT files.
5. Separate evidence contracts per stream.

---

## 7. How to Handle Untracked Files

When git status shows untracked files:

1. Classify each as: EXPECTED (known from previous sprints), MAIN_SPRINT_OWNED, SECONDARY_SPRINT_OWNED, or UNKNOWN.
2. Stage only MEMORY_METHOD_ALLOWED or sprint-authorized files.
3. Do not stage MAIN_SPRINT_OWNED or SECONDARY_SPRINT_OWNED files unless this is a MAIN or SECONDARY sprint respectively.
4. Record the classification in current-state metadata.
5. If UNKNOWN untracked files exist that might be harmful, flag them in the metadata and ask the human before proceeding.

---

## 8. How to Handle Dirty Worktrees

When the working tree is dirty with files owned by other sprint streams:

1. Do not run git stash -u, git reset --hard, or git clean -fd.
2. Classify each dirty file.
3. If clean git cannot be achieved without touching MAIN_SPRINT_OWNED files, use emergency_blocker_bundle: true and document the dirty_git_reason.
4. After MAIN_SPRINT_OWNED files are committed (in a later MAIN SPRINT), run a closure hygiene sprint to normalize the contract.

---

## 9. How to Handle Old Evidence Bundles

When the primary evidence input is an older bundle:

1. Extract the bundle and read bundle-metadata/git-status-final.txt and bundle-metadata/git-log.txt.
2. Verify the bundle was built from the correct commit.
3. Compare the bundle commit to current HEAD.
4. If there are commits between the bundle commit and HEAD, list them and determine if any affect the current sprint scope.
5. Do not proceed if a relevant gate changed between the bundle commit and HEAD without verification.

---

## 10. How to Handle Stale Current-State Files

Stale current-state files contain "Latest commit: PENDING" markers or point to old commits. Before each sprint:

1. Run python tools/evidence/check_current_state_consistency.py.
2. Review output. All checks must PASS before proceeding.
3. If stale state is found, add a stale-state repair step at the start of the sprint plan.

---

## 11. How to Handle Taskcards

For each taskcard referenced in a sprint:

1. Read the taskcard file before updating it.
2. Verify its current status is the expected status.
3. Update status only if the sprint authorizes it.
4. Record the DEC-034 verification reference if applicable.
5. Stage the taskcard file as part of the sprint commit.

---

## 12. How to Handle Evidence Contracts

For each sprint:

1. Create a sprint-specific contract in tools/evidence/contracts/.
2. Set min_metadata_count to at least the actual number of metadata files the sprint produces.
3. Set require_clean_git: true unless dirty git is unavoidable (see section 8).
4. Add forbidden_patterns for all paths that must not be in the bundle.
5. List required_repo_files and required_metadata_files explicitly.
6. Validate the contract YAML before building the bundle.

---

## 13. How to Handle Final Bundle Validation

Before the final response:

1. Build the bundle: python tools/evidence/build_evidence_bundle.py --repo-root . --contract <contract> --output <output> --metadata-dir <dir>.
2. Validate: python tools/evidence/validate_evidence_bundle.py --bundle <output> --contract <contract>.
3. If BUNDLE_VALIDATION: FAIL, do not commit. Fix the issue and rebuild.
4. Run python tools/evidence/check_current_state_consistency.py.
5. Confirm metadata count >= min_metadata_count.
6. Confirm no PENDING markers.
7. Confirm no forbidden paths.

---

## 14. How to Handle No-Push Policy

Push is prohibited unless explicitly authorized in the current session:

1. Do not include git push in any script or command sequence.
2. If the human asks for a commit, commit only. Do not push.
3. If push is authorized, confirm with the human before running git push.
4. Record in every self-challenge: "Did I avoid pushing? YES."

---

## 15. How to Decide Blocked/Partial/Pass/Needs Repair/Ready for Next Sprint

| State | Meaning | Final Line |
|---|---|---|
| PASS | All checks pass, bundle validates, clean git | EVIDENCE_BUNDLE: <path> |
| BLOCKED | A required tool/dependency is missing, or clean git cannot be achieved | BLOCKER_EVIDENCE_BUNDLE: <path> |
| NEEDS_REPAIR | Evidence exists but one or more checks failed or content is incomplete | EVIDENCE_BUNDLE: <path> (with NEEDS_REPAIR label in summary) |
| PARTIAL | Sprint completed some but not all planned work due to scope/time; what was done is valid | EVIDENCE_BUNDLE: <path> (with PARTIAL label) |
| READY_FOR_NEXT | No bundle needed (PLAN MODE), next prompt is ready | NEXT_PROMPT_READY: yes |

---

## 16. How to Keep MAIN, SECONDARY, and MEMORY Streams Separate

| Rule | Detail |
|---|---|
| Label the stream | Every prompt header declares the sprint type explicitly |
| Separate commits | MAIN commits do not include MEMORY files and vice versa |
| Separate contracts | Each sprint type has its own evidence contract |
| Dirty-file classification | Before staging, classify every file by stream ownership |
| No stream mixing | MEMORY SPRINT must not change gate statuses; MAIN SPRINT must not add to LLM strategy backlog |
| Closure hygiene is its own sprint | After a MEMORY SPRINT with dirty worktree, run a CLOSURE HYGIENE sprint once the MAIN SPRINT files are committed |

---

## 17. How to Require Local-Only Run Records

After every sprint:

1. Create a local run record in .local/llm-logs/ as a JSONL file.
2. Include: sprint name, date, type, llm_calls (0 for non-production), and a note.
3. Do not include raw prompts or model responses in the run record.
4. Update .local/artifact-index.yaml with the sprint entry.

---

## 18. How to Write Final Response Status

The final response must include, in order:

1. Sprint summary (2-3 sentences).
2. Key results for each major phase (labeled).
3. Validation result (PASS or FAIL).
4. Commit hash and description.
5. Git status (clean/dirty).
6. Remaining next actions (numbered).
7. Stream declaration:
   - MEMORY METHODOLOGY SPRINT ONLY (or appropriate type)
   - NO MAIN SPRINT GATE CHANGED
   - NO SECONDARY EXECUTION STARTED
   - NO PRODUCT SOURCE CREATED
   - NO EMBEDDINGS OR VECTOR DB CREATED
   - NO PRODUCTION LLM CALL MADE
   - NO NEW SPECS DOWNLOADED
   - NO PUSH MADE
8. Final line: EVIDENCE_BUNDLE: <absolute Windows path to zip>

The final line is always the evidence bundle path. Nothing follows it.

---

## 19. Always-Updated Enforcement Model (added 2026-05-09)

Every execution sprint must include a mandatory closeout phase. This is not optional.
The closeout phase runs after all sprint work is complete and before the evidence bundle is built.

### 19.1 Mandatory closeout steps

1. Update all Level 6 session hint files:
   - memory/09-current-state-before-phase1.md
   - .claude/settings.json
   - docs/fresh-chat-continuity-brief.md
   These files must not contain stale gate statuses or stale run references after the sprint.

2. If gate status changed: update registry/format-registry.yaml, plans/master-plan.md header,
   and all pack.yaml files for the affected format. All three must agree before bundle build.

3. If a new taskcard was created or completed: update plans/master-plan.md (taskcards table).

4. If ROADMAP.md or README.md are stale: update or create a pending-propagation report at
   reports/propagation/{sprint-id}-propagation-pending.md.

5. Run the current-state consistency checker:
   python tools/evidence/check_current_state_consistency.py
   Expected: CURRENT_STATE_CONSISTENCY: PASS

6. If CURRENT_STATE_CONSISTENCY fails: fix the failing check before building the bundle.

### 19.2 Pending propagation reports

When a sprint cannot safely update a file because another active stream owns it:
- Create reports/propagation/{sprint-id}-propagation-pending.md
- Required fields: sprint_id, blocked_file, blocking_stream, propagation_content, follow_up_sprint

### 19.3 Failure rule

A sprint that skips the always-updated closeout and builds a bundle with a known stale-state
failure is considered INCOMPLETE. Build the bundle only after CURRENT_STATE_CONSISTENCY: PASS.

See memory/15-ai-modules-and-state-management-architecture-20260509.md for the full model.
