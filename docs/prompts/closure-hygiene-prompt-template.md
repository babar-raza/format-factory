# Closure Hygiene Prompt Template

**Mode:** EXECUTION MODE
**Sprint type:** CLOSURE HYGIENE
**Purpose:** Use this template when an evidence contract was created with emergency_blocker_bundle: true (due to dirty worktree), but the final bundle state was actually clean. This sprint normalizes the contract and produces a clean closure bundle.

---

MODE:
EXECUTION MODE.

Sprint type:
CLOSURE HYGIENE.

Sprint name:
Closure Hygiene: <sprint name being closed>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute path to the original emergency bundle being normalized>

Goal:
Normalize the original evidence contract for <sprint name> from emergency mode to clean PASS mode.
Verify the original bundle content is valid. Produce a clean closure evidence bundle.

No new content. No new scope. No gate changes. No product source. No push.

Human authorization:
By running this prompt, the human authorizes:
1. Reading and verifying the original sprint evidence bundle.
2. Setting require_clean_git: true in the original contract.
3. Setting emergency_blocker_bundle: false in the original contract.
4. Removing stale dirty-git justification text from the original contract.
5. Adding a historical note explaining the normalization.
6. Creating a closure evidence contract.
7. Building and validating the closure evidence bundle.
8. Committing only the normalized and new closure contract files.

This prompt does NOT authorize:
1. New content beyond contract normalization.
2. Gate changes.
3. Product source.
4. Push.

Hard prohibitions:
Do not modify any artifact that was committed in the original sprint (except the contract).
Do not create product source.
Do not push.

Read first:

1. <original evidence contract>
2. <original bundle>.zip -- read bundle-metadata/git-status-final.txt and verdict.md
3. plans/master-plan.md
4. docs/planning-methodology.md

A. Verify original bundle

Read original bundle:
- git-status-final.txt: confirm working tree was clean.
- verdict.md: confirm PASS.
- self-challenge.md: confirm all YES.

Create: <sprint-name>-closure-current-state-review.md

B. Verify original sprint content

For each original sprint artifact, confirm it exists and has not changed since the sprint commit.
Create: <sprint-name>-content-reverification.md

C. Normalize the contract

Update <original contract>:
- Set require_clean_git: true
- Set emergency_blocker_bundle: false
- Remove dirty_git_reason and stale comments
- Add historical note: "The original sprint was executed during run interleaving, but the
  final committed state was clean. This normalized contract is the authority for future
  validation of this sprint as a normal PASS bundle."

Create: <original contract name>-closure.yaml with require_clean_git: true, min_metadata_count >= 45.

Create: contract-diff-summary.md and emergency-contract-normalization-report.md

Evidence contract

Contract path: tools/evidence/contracts/<sprint-name>-closure.yaml
Output: .local/evidence-bundles/<sprint-name>-closure-YYYYMMDD-HHMMSS.zip

Commit (if authorized)

Allowed to stage:
- <original contract> (normalized)
- <closure contract> (new)
- plans/master-plan.md (if only closure note added)

Do not stage:
- anything from the original sprint that did not change
- .local/
- registry/format-registry.yaml (unless authorized)

Commit message: docs: normalize <sprint name> evidence contract

Do not push.

Final response:

1. Closure summary.
2. Original bundle verification result.
3. Contract normalization result.
4. Content preservation result.
5. Commit hash.
6. Stream declaration:
   - CLOSURE HYGIENE ONLY
   - NO MAIN SPRINT GATE CHANGED
   - NO PRODUCT SOURCE CREATED
   - NO EMBEDDINGS OR VECTOR DB CREATED
   - NO PRODUCTION LLM CALL MADE
   - NO PUSH MADE

EVIDENCE_BUNDLE: <absolute Windows path to zip>
