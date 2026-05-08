# Execution Handoff Prompt Template

**Mode:** EXECUTION MODE
**Sprint type:** MAIN SPRINT / MEMORY SPRINT / SECONDARY SPRINT (select one)
**Purpose:** Use this template when converting a hardened plan into a single-go autonomous execution prompt.

---

MODE:
EXECUTION MODE.

Sprint type:
<MAIN SPRINT | MEMORY SPRINT | SECONDARY SPRINT | CLOSURE HYGIENE | INDEPENDENT VERIFICATION>

Sprint name:
<unique descriptive name, e.g., "FODS Gate 10 OSS Implementation Sprint">

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute Windows path to the most recent passing evidence bundle>

Goal:
<2-5 sentences describing exactly what this sprint produces. Be specific. Name the files,
gates, or artifacts that will exist when the sprint is done.>

Human authorization:
By running this prompt, the human authorizes:
<numbered list of exactly what is authorized, e.g.:>
1. Reading and verifying the primary evidence bundle.
2. Executing <specific taskcard> to produce <specific artifact>.
3. Running <specific validation command>.
4. Committing only the files listed under "Allowed to stage."

This prompt does NOT authorize:
<numbered list of prohibited actions, e.g.:>
1. MAIN SPRINT gate changes (for MEMORY SPRINT).
2. Product source creation.
3. Embedding or vector DB creation.
4. Production LLM API calls.
5. Push.

Hard prohibitions:
Do not create src/net/.
Do not create src/python/fods/.
Do not create src/python/fodt/.
Do not create reports/legal/.
Do not create .github/workflows/.
Do not create embeddings or vector DB files.
Do not push.
<add any sprint-specific prohibitions>

Read first:

Read these files before starting:
1. plans/master-plan.md (current status section)
2. AGENTS.md (sections relevant to this sprint type)
3. GOVERNANCE.md (sections relevant to this sprint)
4. <specific taskcards referenced>
5. <specific contracts or evidence bundles>
6. docs/planning-methodology.md (for sprint type rules)
7. docs/agent-execution-handoff-standard.md (for execution rules)

Also run:
- git log --oneline -5
- git status --short
- python tools/evidence/check_current_state_consistency.py

If CURRENT_STATE_CONSISTENCY: FAIL, stop and print BLOCKED_CONSISTENCY_CHECK.

A. Verify current state

Create metadata file: <sprint-name>-current-state-review.md

Record:
1. Git branch and HEAD commit.
2. Git status classified by stream ownership.
3. Whether primary evidence bundle exists and validates.
4. Whether relevant taskcards are in expected status.
5. Whether any MAIN SPRINT gate status would be changed by this sprint.

If working tree has MAIN_SPRINT_OWNED or SECONDARY_SPRINT_OWNED files and clean git cannot be
achieved, document dirty_git_reason and set emergency_blocker_bundle: true in the contract.

B. <First execution section>

<Describe exact steps. Example:>
Execute taskcard <ID> to produce <artifact>. Steps:
1. Read <input file>.
2. Create <output file> with the following content: <exact content or schema>.
3. Run <validation command>. Expected: <expected output>.
4. If validation fails, stop with BLOCKED_<SECTION_NAME>: <failure detail>.
5. Update <taskcard> status to <new status>.

Allowed files for this section:
- <file1>
- <file2>

C. <Second execution section>

<Repeat B pattern for each section>

Validation

Run or perform:
1. YAML validation: python -c "import yaml; yaml.safe_load(open('<file>'))" -- expected: no error.
2. JSON validation: <if applicable>
3. python tools/evidence/check_current_state_consistency.py -- expected: CURRENT_STATE_CONSISTENCY: PASS
4. python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <path> -- expected: BUNDLE_VALIDATION: PASS
5. git status -- expected: nothing to commit, working tree clean (or documented dirty with reason)

Evidence contract

Contract path: tools/evidence/contracts/<sprint-name>.yaml
Required fields: require_clean_git, emergency_blocker_bundle, min_metadata_count, memory_sprint (if applicable)
Output path: .local/evidence-bundles/<sprint-name>-YYYYMMDD-HHMMSS.zip

Commit (if authorized)

Allowed to stage:
<exact list of files>

Do not stage:
.local/
acquisition-packs/ (unless authorized)
registry/format-registry.yaml (unless this sprint changes a gate)
src/ (unless product sprint)
.github/
evidence bundles

Commit message:
<exact commit message>

Do not push.

Self-challenge

Answer YES or NO to each:
1. Did I read all required files before acting?
2. Did I verify current repo state?
3. Did I classify all dirty files by stream ownership?
4. Did I complete <section B>?
5. Did I complete <section C>?
6. Did I run all validation checks?
7. Did I avoid MAIN SPRINT gate changes?
8. Did I avoid product source?
9. Did I avoid embeddings/vector DB?
10. Did I avoid production LLM calls?
11. Did I avoid new spec downloads?
12. Did I avoid secrets?
13. Did the evidence bundle validate?
14. Did I commit only authorized files?
15. Did I avoid pushing?
16. Did I update all relevant taskcards?
17. Did I capture any discovered gaps in backlog/memory?

Final response format:

1. Sprint summary.
2. Key results per section (labeled).
3. Validation results (PASS/FAIL per check).
4. Commit hash.
5. Git status (clean/dirty).
6. Next actions.
7. Stream declaration:
   - <SPRINT TYPE> ONLY
   - NO MAIN SPRINT GATE CHANGED (if applicable)
   - NO PRODUCT SOURCE CREATED
   - NO EMBEDDINGS OR VECTOR DB CREATED
   - NO PRODUCTION LLM CALL MADE
   - NO NEW SPECS DOWNLOADED
   - NO PUSH MADE

EVIDENCE_BUNDLE: <absolute Windows path to zip>
