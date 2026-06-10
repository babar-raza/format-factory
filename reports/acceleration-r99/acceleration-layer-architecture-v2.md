# Acceleration Layer Architecture v2 — Train B

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## System Overview

The acceleration layer is a set of tools, schemas, and conventions that turn the POC
capability matrix into bounded, repeatable, governed product work. It sits between the
supervisor pipeline and the worker agent.

```
                    +--------------------+
                    |  Supervisor Loop   |
                    | (autonomous_cycle) |
                    +--------+-----------+
                             |
                    +--------v-----------+
                    | Acceleration Layer |
                    +--------+-----------+
                             |
           +-----------------+-----------------+
           |        |        |        |        |
     Gap       Skill/    Execution  Lane     Sprint
     Selector  Handoff   Handoff    Recorder  Learning
               Router    Generator            Generator
           |        |        |        |        |
           +-----------------+-----------------+
                             |
                    +--------v-----------+
                    |   Worker Agent     |
                    | (skill execution)  |
                    +--------+-----------+
                             |
                    +--------v-----------+
                    | Evidence Pipeline  |
                    | (materializer +    |
                    |  review package)   |
                    +--------------------+
```

## Components

### 1. Gap Selector (`tools/supervisor/select_poc_gaps.py`)

**Input:** POC matrix, skill registry
**Output:** Ranked gap list with stream assignment

Responsibilities:
- Read `product-capability-matrix/poc-targets.yaml`
- Read `.supervisor/skill-registry.yaml`
- Rank gaps by product impact (save/export/dogfood > query APIs)
- Assign gaps to streams: mainstream, acceleration, skills, supervisor
- Filter stale sprint IDs
- Emit per-stream selected gap files

**v3 improvements (this sprint):**
- Stream-aware output (separate JSON per stream)
- Skill registry integration for decision enrichment
- Depth-priority scoring (save/export > query)

### 2. Skill/Handoff Router (`tools/supervisor/choose_skill_or_handoff.py`)

**Input:** Selected gap, skill registry, risk classification
**Output:** Decision: USE_SKILL | GENERATE_HANDOFF | BLOCK_EXTERNAL_GATE | NEED_PLAN_HARDENING | READ_ONLY_VERIFY

Responsibilities:
- Match gap to registered skill by capability path
- Assess risk (new file vs existing file edit)
- Check external gate status
- Return execution recommendation

**v2 improvements (this sprint):**
- Read skill registry YAML directly
- Match against `required_handoff_fields` and `mandatory_validations`
- Add NEED_PLAN_HARDENING and READ_ONLY_VERIFY decisions

### 3. Product-Code Ledger Interface

**Tool:** `tools/supervisor/validate_product_code_ledger.py`
**Ledger:** `reports/r90/product-code-change-ledger.json`

Already operational. The acceleration layer relies on:
- Every `src/*` edit being recorded before commit
- Ledger validator running before sprint closeout

### 4. Execution Handoff Generator

**Skill:** `/generate-execution-handoff`
**Command:** `.claude/commands/generate-execution-handoff.md`

Already operational. Generates structured YAML handoffs for skills that need
specific path scoping and validation rules.

### 5. Lane Execution Recorder (`tools/supervisor/record_lane_execution.py`)

**Input:** Lane metadata, file changes, test results
**Output:** `lane-execution-ledger.json`

**NEW in this sprint.** Captures:
- Lane ID, start/end timestamps, duration
- Concurrency group
- Files read and changed
- Commands executed
- Tests run and results
- Evidence artifacts produced
- Status and blockers

### 6. Evidence Materializer Integration

**Tools:**
- `tools/supervisor/materialize_declared_evidence.py`
- `tools/supervisor/build_declaration_review_package.py`

Already operational. The acceleration layer documents the quick-path:
1. Write `evidence-declaration.yaml`
2. Run materializer
3. Run review package builder
4. Report SHA-256

### 7. Package/Install Proof Helper (`tools/supervisor/package_install_proof.py`)

**NEW in this sprint.** Bridges the `/package-install-proof` skill to a standalone tool:
- Detect changed product source
- Select source-level vs installed proof
- Run smoke tests
- Capture logs
- Report blockers

### 8. Dogfood Verifier

**Skill:** `/verify-dogfood-path`
**Command:** `.claude/commands/verify-dogfood-path.md`

Already operational. Verifies that export paths use only FF libraries.

### 9. Product Progress Detector (`tools/supervisor/detect_product_progress.py`)

Already operational. Compares capability snapshots across sprints and detects stagnation.

### 10. Sprint Learning Feedback Loop

**NEW in this sprint.** Tool or template producing:
- `agent-learning-notes.md` — what worked, what didn't
- `speed-bottlenecks.md` — where time was lost
- `next-agent-briefing.md` — what the next agent should know
- `manual-process-to-skill-candidates.md` — processes to automate

## Decision Tree (v2)

```
Gap selected from POC matrix
  |
  +-- Is it blocked by external gate?
  |     YES -> BLOCK_EXTERNAL_GATE (report gate, stop)
  |     NO  -> continue
  |
  +-- Does a governed skill match?
  |     YES -> Does risk require plan hardening?
  |     |       YES -> NEED_PLAN_HARDENING
  |     |       NO  -> USE_SKILL (execute via skill command)
  |     NO  -> continue
  |
  +-- Is the gap read-only verifiable?
  |     YES -> READ_ONLY_VERIFY (test/check without src edit)
  |     NO  -> GENERATE_HANDOFF (create execution handoff, do not edit src)
```

## File Layout

```
tools/supervisor/
  select_poc_gaps.py          # Gap selector (v3)
  choose_skill_or_handoff.py  # Skill/handoff router (v2)
  record_lane_execution.py    # Lane execution recorder (NEW)
  generate_sprint_learning.py # Sprint learning generator (NEW)
  package_install_proof.py    # Package/install proof helper (NEW)
  detect_product_progress.py  # Product progress detector
  validate_product_code_ledger.py  # Ledger validator
  materialize_declared_evidence.py # Evidence materializer
  build_declaration_review_package.py # Review package builder

.supervisor/
  skill-registry.yaml         # Governed skill definitions
  context-pack.yaml           # Context snapshot

product-capability-matrix/
  poc-targets.yaml             # POC target matrix

reports/r90/
  product-code-change-ledger.json  # Product-code ledger
```

## Integration Points with Supervisor

1. `autonomous_cycle.py` calls gap selector after grading
2. `generate_supervisor_packet.py` uses selected gaps for next-sprint prompt
3. `build_context_pack.py` snapshots all acceleration layer state
4. Lane execution ledger feeds sprint learning generator
