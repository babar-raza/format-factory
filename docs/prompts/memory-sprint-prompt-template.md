# Memory Sprint Prompt Template

**Mode:** EXECUTION MODE
**Sprint type:** MEMORY SPRINT
**Purpose:** Use this template when capturing strategic decisions, architecture gaps, or user preferences into durable local repo artifacts.

---

MODE:
EXECUTION MODE.

Sprint type:
MEMORY SPRINT.

Sprint name:
Memory Sprint: <describe what decisions or strategy is being captured>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute Windows path to the most recent passing evidence bundle, or the memory closure bundle>

Goal:
Capture the following decisions and architecture notes into durable local repo artifacts:
<list the specific decisions being captured>

This is a MEMORY SPRINT ONLY. No MAIN SPRINT gate work. No SECONDARY SPRINT execution.
No product source. No embeddings. No production LLM calls. No spec downloads.

Human authorization:
By running this prompt, the human authorizes:
1. Reading current repo state, memory files, governance, and evidence.
2. Creating new memory files for the listed decisions.
3. Updating relevant memory files and memory/00-index.md.
4. Updating plans/master-plan.md with backlog or architecture notes (additive only, no gate changes).
5. Updating ROADMAP.md with backlog milestones (additive only).
6. Updating AGENTS.md and GOVERNANCE.md with governance rules (additive only).
7. Creating taskcards (status: proposed_pending_human_approval) for any out-of-scope backlog items.
8. Building and validating the memory sprint evidence bundle.
9. Committing only MEMORY_SPRINT_ALLOWED files.

This prompt does NOT authorize:
1. MAIN SPRINT gate status changes.
2. SECONDARY SPRINT execution.
3. Product source (src/python/ or src/net/).
4. Embeddings or vector DB.
5. Production LLM calls.
6. Spec downloads.
7. Push.

Hard prohibitions:
Do not create src/net/.
Do not create src/python/fods/.
Do not create src/python/fodt/.
Do not create reports/legal/.
Do not create .github/workflows/.
Do not create embeddings.
Do not create vector DB files.
Do not call LLM endpoints.
Do not download specs.
Do not modify registry gate statuses.
Do not push.

Read first:

1. plans/master-plan.md
2. ROADMAP.md
3. AGENTS.md
4. GOVERNANCE.md
5. memory/00-index.md
6. All existing memory files
7. docs/planning-methodology.md
8. docs/agent-execution-handoff-standard.md
9. Primary evidence input bundle (read bundle-metadata/verdict.md and git-log.txt)

A. Verify current state

Create: <sprint-name>-current-state-review.md

Record git branch, HEAD commit, git status (classify dirty files by stream ownership), and
confirmation that no product source, embeddings, or LLM calls exist.

B. Capture decisions into memory

Create: memory/<NN>-<description>.md

Required front matter:
  memory_package: format-factory-chat-memory
  version: 1.0
  created_at: <date>
  source: <describe source>
  visibility: internal

Required content:
<detailed decisions to capture>

C. Update backlog and governance

Create or update:
- plans/master-plan.md (additive sections only, no gate changes)
- ROADMAP.md (additive milestones only)
- AGENTS.md (additive sections only)
- GOVERNANCE.md (additive sections only)
- Taskcards for any out-of-scope items (status: proposed_pending_human_approval)

D. Update memory index

Update memory/00-index.md:
- Add entry for new memory file.
- Add stream history entry.

Evidence contract

Contract path: tools/evidence/contracts/<sprint-name>.yaml
Required fields:
  require_clean_git: true (or false with documented dirty_git_reason if MAIN_SPRINT_OWNED dirty files exist)
  emergency_blocker_bundle: false (or true if dirty git unavoidable)
  memory_sprint: true
  no_main_sprint_gate_change: true
  no_secondary_execution: true
  no_product_source_created: true
  no_embedding_created: true
  no_vector_db_created: true
  no_llm_production_call: true
  no_new_spec_download: true
  no_push: true
  min_metadata_count: <at least 55>

Allowed to stage (MEMORY_SPRINT_ALLOWED):
- memory/<new file>
- memory/00-index.md
- docs/ (new methodology/strategy docs created in this sprint)
- taskcards/ (new proposed_pending_human_approval taskcards)
- AGENTS.md (if sections added)
- GOVERNANCE.md (if sections added)
- plans/master-plan.md (if backlog sections added)
- ROADMAP.md (if milestone sections added)
- tools/evidence/contracts/<sprint-name>.yaml

Do not stage:
- .local/
- registry/format-registry.yaml
- src/
- .github/
- acquisition-packs/ active gate outputs

Commit message: docs: <short description of what was captured>

Do not push.

Self-challenge (17+ questions):

1. Did I capture all listed decisions into durable memory files?
2. Did I update memory/00-index.md?
3. Did I avoid MAIN SPRINT gate changes?
4. Did I avoid SECONDARY SPRINT execution?
5. Did I avoid product source?
6. Did I avoid embeddings/vector DB?
7. Did I avoid production LLM calls?
8. Did I avoid spec downloads?
9. Did I avoid secrets?
10. Did I capture discovered gaps in backlog/taskcards/roadmap?
11. Did I classify all dirty files by stream ownership?
12. Did validation pass?
13. Did the evidence bundle validate?
14. Did I commit only MEMORY_SPRINT_ALLOWED files?
15. Did I avoid pushing?
16. Did I update the evidence contract correctly?
17. Did the memory index reflect all new files?

Final response:

1. Memory sprint summary.
2. Decisions captured.
3. Files created and modified.
4. Validation result.
5. Evidence contract validation result.
6. Commit hash.
7. Git status.
8. Next actions.
9. Stream declaration:
   - MEMORY SPRINT ONLY
   - NO MAIN SPRINT GATE CHANGED
   - NO SECONDARY EXECUTION STARTED
   - NO PRODUCT SOURCE CREATED
   - NO EMBEDDINGS OR VECTOR DB CREATED
   - NO PRODUCTION LLM CALL MADE
   - NO NEW SPECS DOWNLOADED
   - NO PUSH MADE

EVIDENCE_BUNDLE: <absolute Windows path to zip>
