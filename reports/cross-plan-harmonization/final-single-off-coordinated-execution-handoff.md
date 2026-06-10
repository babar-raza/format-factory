# Final Single-Go Coordinated Execution Handoff
# Sprint: FORMAT-FACTORY-CROSS-PLAN-HARMONIZATION-BEFORE-EXECUTION-001
# Date: 2026-06-04
# Mode: EXECUTION HANDOFF — all streams coordinated, ready for single-go run

---

## Execution Order

Streams execute in this sequence. No stream may start until the preceding dependency is met.

```
Stream 1: Supervisor   → runtime governance + traffic controller
Stream 2: Skills       → governed skill execution / Superpowers normalization
Stream 3: Acceleration → cognitive layer / external-tool intake
Stream 4: Mainstream   → POC mega-train execution until POC_READY_CANDIDATE or true stop
```

Dependency chain:
- Supervisor must produce `approval-gates.md` and `next-ruflo-lanes.json` before Mainstream starts
- Skills must produce `mainstream-consumption-packet.json` (if available) before Mainstream uses skill output
- Acceleration must produce at least one `mainstream-consumption-packets/*.json` before Mainstream uses acceleration output
- Mainstream does NOT block on Skills or Acceleration — it uses fallback if packets are absent

---

## Internal Coordinator

**Role:** Lane 0 (present in every stream)
**Responsibilities:**
- Initialize `taskcard-state.json` for each stream before any lane starts
- Capture and own `file-ownership-map.json`
- Run overlap checks between streams
- Record integration order and dependency resolution
- Detect and route emergency stops

**Meta-run coordinator artifact:** `reports/cross-plan-harmonization/taskcard-state.json`
(stream-specific states listed below)

---

## Lane Ownership

| Stream | Owner Role | Allowed Root Paths |
|--------|------------|-------------------|
| Supervisor | Lane 0: coordinator; C1: governance; C2: repair; C3: implementation; C4: dogfood; C5: package; C6: evidence | `reports/supervisor-product-first/`, `tools/supervisor/`, `tests/supervisor/` |
| Skills | Lane W0: coordinator; W1-W9: governed skills; W10: external-skills-intake | `reports/skills-plan-repair/`, `reports/skills-product-first/`, `.claude/commands/check-mcp-status.md` (conditional) |
| Acceleration | Lane 0: coordinator; Lane A: tests; Lane B: AI tools; Lane C: test execution; Lane D: healing; Lane X: external tool | `reports/acceleration-plan-repair/`, `reports/acceleration-product-first/`, `tools/supervisor/` (new tools only) |
| Mainstream | Lane 0: coordinator; FODS-LANE; FODT-LANE; NETPBM-LANE; ZST-LANE; DIF-LANE; SYLK-LANE; EVIDENCE-IV-LANE | `src/net/**`, `src/python/**` (governed skills only), `reports/mainstream-poc-train/`, `tests/net/**`, `tests/python/**`, `examples/**` |

---

## File Ownership

| Path Pattern | Owner Stream | Other Streams |
|--------------|-------------|---------------|
| `reports/supervisor-product-first/**` | Supervisor | read-only |
| `reports/supervisor/**` (outputs only) | Supervisor | read-only |
| `tools/supervisor/autonomous_cycle.py` | Supervisor only | FORBIDDEN |
| `.supervisor/skill-registry.yaml` | Skills only | read-only |
| `reports/skills-product-first/**` | Skills | read-only |
| `.claude/commands/**` | Skills only | FORBIDDEN |
| `reports/acceleration-product-first/**` | Acceleration | read-only |
| `reports/acceleration-plan-repair/**` | Acceleration | read-only |
| `tools/supervisor/` (new AI tools) | Acceleration | read-only |
| `src/net/**`, `src/python/**` | Mainstream (governed skills) | Forbidden direct |
| `reports/mainstream-poc-train/**` | Mainstream | read-only |
| `reports/mainstream-plan-repair/**` | Mainstream (creates); harmonization patched | read-only |
| `product-capability-matrix/poc-targets.yaml` | FROZEN (read-only ALL) | all read-only |
| `registry/**`, `plans/master-plan.md`, `AGENTS.md`, `GOVERNANCE.md` | FROZEN | FORBIDDEN |

---

## Overlap Checks

Before execution, verify these paths have no multi-stream write conflict:

| Path | Supervisor | Skills | Acceleration | Mainstream | Conflict? |
|------|-----------|--------|-------------|------------|-----------|
| `src/net/*` | FORBIDDEN | FORBIDDEN | FORBIDDEN | governed-write | NO |
| `src/python/*` | FORBIDDEN | FORBIDDEN | FORBIDDEN | governed-write | NO |
| `tools/supervisor/autonomous_cycle.py` | modify-ok | FORBIDDEN | FORBIDDEN | FORBIDDEN | NO |
| `tools/supervisor/*.py` (new tools) | read-only | FORBIDDEN | create-ok | FORBIDDEN | NO |
| `.supervisor/skill-registry.yaml` | read-only | modify-ok | read-only | read-only | NO |
| `reports/supervisor/**` | write | read | read | read | NO |
| `poc-targets.yaml` | read-only | FORBIDDEN | read-only | read-only | NO |

**Result:** No overlap conflicts detected.

---

## Taskcard State Files

### Meta-Run
```
reports/cross-plan-harmonization/taskcard-state.json
```

### Stream-Specific
```
reports/supervisor-product-first/taskcard-state.json      (created by Supervisor Lane 0)
reports/skills-product-first/taskcard-state.json          (created by Skills Lane W0)
reports/acceleration-product-first/taskcard-state.json    (created by Acceleration Lane 0)
reports/mainstream-poc-train/taskcard-state.json          (created by Mainstream Lane 0)
```

Each file must be initialized before any lane in that stream starts.

---

## Stop Conditions

### Per-Stream Hard Stops (never autonomous)
- git push / commit
- Gate 8 or Gate 11 approval
- Package publication
- MCP activation changes beyond current state
- Destructive git operations
- External tool installation (Ruflo daemon, Superpowers, GhidraMCP)

### Mainstream-Specific Stop Conditions
- `MAINSTREAM_POC_READY_CANDIDATE` — all required POC targets green: proceed to Phase 7 closeout
- `MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE` — true external blocker: report to user, do not continue
- `MAINSTREAM_POC_UNSAFE_WORKSPACE` — source corruption or >3x same foundational failure: stop
- `CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT` — write `train-state.json` + `next-iteration-prompt.md`; do NOT report done

### Acceleration-Specific Stop
- External tool detected as installed → HARD STOP, investigate before continuing

### Not a Hard Stop
- `max_iterations reached` in Mainstream → checkpoint rollover, continue
- Supervisor advisory outputs differ from plan expectations → log, continue with local coordinator
- Skills packet absent → fallback transcript, continue
- Acceleration packet absent → deterministic gap selection, continue
- Ruflo DETECTED_NOT_CONFIGURED → local coordinator, continue (NOT a stop)

---

## Final Response Rules

**No final user-facing response after each Mainstream iteration.**
Write iteration evidence to disk. Update `train-state.json`. Continue immediately.
Response to user ONLY at terminal state.

**Terminal states requiring user response:**
1. `MAINSTREAM_POC_READY_CANDIDATE` — full verdict, absolute review package path + SHA-256
2. `MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE` — blocker description, `train-state.json` path
3. `MAINSTREAM_POC_UNSAFE_WORKSPACE` — corruption description, recovery steps
4. `CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT` — paths to `train-state.json` + `next-iteration-prompt.md`

---

## Evidence Bundle and Review Package Requirements

### Per Stream
Each stream MUST produce at closeout:
1. `.local/evidences/<stream-id>/evidence-declaration.yaml`
2. `.local/evidences/<stream-id>/evidence-manifest.yaml`
3. Run `python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/<stream-id>/evidence-declaration.yaml`
4. Run `python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/<stream-id>/evidence-declaration.yaml`

### Final Absolute Path + SHA-256 Reporting
All evidence bundle paths reported to user MUST be absolute paths:
```
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\<run_id>\declaration-review-package.zip
```
Never relative paths. Always include SHA-256.

---

## Ruflo Mode Governance (Mainstream execution)

Before each Mainstream iteration:
1. Run Supervisor MCP status detection
2. Read `reports/supervisor/next-ruflo-lanes.json` — check if `ruflo_mode` field is present
3. If FULL_LOOP_APPROVED confirmed → may use claude-flow (non-authoritative only)
4. If DETECTED_NOT_CONFIGURED, ABSENT, BLOCKED, or unclear → local coordinator only
5. Record mode in `reports/mainstream-poc-train/ruflo-lane-map.json` each iteration
6. Ruflo unavailability NEVER blocks the train

---

## Acceleration External Tool Validation (before Mainstream consumes Acceleration output)

Before Mainstream consumes any Acceleration packet:
1. Verify `reports/acceleration-product-first/external-tool-authority-validation.json` exists
2. Verify its status is `PASS`, `SKIPPED_WITH_REASON`, or `BLOCKED_WITH_REASON` (not PENDING)
3. Verify all packets have `external_tool_activation_required_for_packet: false`
4. If any validation is PENDING → do not use Acceleration packet; use deterministic fallback

---

## Stream Execution Specifications

### Stream 1: Supervisor
**Plan:** `C:\Users\prora\.claude\plans\generic-swimming-moon.md`
**Evidence root:** `.local/evidences/supervisor-product-first/`
**Key outputs:** `reports/supervisor-product-first/`, updated `autonomous_cycle.py`, new supervisor tests

### Stream 2: Skills
**Plan:** `C:\Users\prora\.claude\plans\dazzling-inventing-pie.md`
**Evidence root:** `.local/evidences/skills-product-first/`
**Key outputs:** `reports/skills-product-first/mainstream-consumption-packet.json`, external-skills-intake docs

### Stream 3: Acceleration
**Plan:** `C:\Users\prora\.claude\plans\bubbly-wiggling-pizza.md`
**Evidence root:** `.local/evidences/acceleration-product-first/`
**Key outputs:** 4 mainstream consumption packets, `external-tool-authority-validation.json` (PASS/SKIPPED/BLOCKED — not PENDING)

### Stream 4: Mainstream
**Plan:** `C:\Users\prora\.claude\plans\twinkling-percolating-hare.md`
**Evidence root:** `.local/evidences/mainstream-poc-train/`
**Key outputs:** POC gap closures (load/edit/save/export/dogfood), updated `poc-readiness-dashboard.json`, `train-state.json`
**Terminal target:** `MAINSTREAM_POC_READY_CANDIDATE`

---

## Post-Harmonization Verdicts

| Plan | Pre-Harmonization | Post-Harmonization |
|------|------------------|-------------------|
| Mainstream | PLAN_NEEDS_REPAIR | HARMONIZED — Ruflo mode detection fixed |
| Acceleration | PLAN_NEEDS_REPAIR | HARMONIZED — TC-EXT-007 mandatory |
| Skills | READY | READY — unchanged, compatible |
| Supervisor | READY | READY — unchanged, compatible |

**Meta-verdict:** `CROSS_PLAN_HARMONIZED_WITH_LIMITATIONS`

Limitation: Ruflo mode must be freshly detected during Mainstream execution. The actual
runtime state (`DETECTED_NOT_CONFIGURED` per current Supervisor session) means Mainstream
will default to local coordinator unless Supervisor runtime governance explicitly approves
FULL_LOOP_APPROVED for the execution run.
