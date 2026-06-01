# FORMAT-FACTORY-R89-MEGA-TRAIN-001
# Generated: 2026-06-01T19:44:47.621648
# Source: Supervisor autonomous-cycle review of FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
# ADVISORY ONLY -- not a Format Factory authority document

---

## Preflight (read before any code change)

Read these files before writing any code:

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `plans/master-plan.md`
4. `registry/format-registry.yaml`
5. `reports/supervisor/session-resume.md`
6. `reports/supervisor/latest-review.md`
7. `.supervisor/policies.yaml`
8. `product-capability-matrix/poc-targets.yaml`
9. `CLAUDE.md`

---

## Sprint Identity

- Sprint ID: FORMAT-FACTORY-R89-MEGA-TRAIN-001
- Prior sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
- Prior verdict: ACCEPTED
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: True

---

## Sprint Goal

**Goal:** Advance product POC: FODS .NET: FODS→CSV export; FODT .NET Product Deepening; Netpbm .NET: PPM load/parse (P3/P6); Netpbm .NET: Binary format write (P4/P5/P6). Build evidence declaration and run supervisor autonomous-cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.
2. Last instruction MUST be:
   ```
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
3. The declaration must list ALL work items with status, evidence paths, and test references.
4. Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.
5. Evidence is support infrastructure -- the goal is product POC progress.

---

## Train Manifest

| Train | Group | Title |
|-------|-------|-------|
| A | G1 | Governance Preflight |
| B | G3 | FODS .NET: FODS→CSV export |
| C | G3 | FODT .NET Product Deepening |
| D | G3 | Netpbm .NET: PPM load/parse (P3/P6) |
| E | G3 | Netpbm .NET: Binary format write (P4/P5/P6) |
| F | G4 | ZST Python Improvement |
| G | G4 | Netpbm Python: Write Ppm |
| H | G4 | SYLK Python: Write Sylk |
| I | G5 | Dogfood: fodt -> txt |
| J | G5 | Dogfood: fodt -> html |
| K | G6 | Package Build + Install Proof |
| L | G7 | State + Memory + POC Matrix Sync |
| M | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states.

**Acceptance Criteria:**
- All preflight files read
- No policy violations detected
- Gate states documented

**Files:**
- `reports/<run_id>/00-preflight.md`

## Group G3: Commercial .NET Product

### Train B: FODS .NET: FODS→CSV export

No FodsCsvExporter; FODS→CSV is a natural export for spreadsheet format. Status: NOT_IMPLEMENTED.

**Acceptance Criteria:**
- New tests pass for GAP-CAP-003
- FODS .NET capability implemented or documented

**Files:**
- `src/net/fods/`
- `tests/net/fods/`

**Verification:**
```bash
dotnet test tests/net/fods/ --verbosity quiet
```

### Train C: FODT .NET Product Deepening

Continue FODT commercial .NET product advancement. Gate 11 G11-G approval (external gate; human required)

**Acceptance Criteria:**
- FODT .NET test count increased or new API proven
- dotnet_status in poc-targets.yaml updated

**Files:**
- `src/net/fodt/`
- `tests/net/fodt/`

**Verification:**
```bash
dotnet test tests/net/fodt/ --verbosity quiet
```

### Train D: Netpbm .NET: PPM load/parse (P3/P6)

NetpbmParser handles P3/P6 tokens; no dedicated PPM-only tests yet. Status: PARTIAL.

**Acceptance Criteria:**
- New tests pass for GAP-CAP-001
- Netpbm .NET capability implemented or documented

**Files:**
- `src/net/netpbm/`
- `tests/net/netpbm/`

**Verification:**
```bash
dotnet test tests/net/netpbm/ --verbosity quiet
```

### Train E: Netpbm .NET: Binary format write (P4/P5/P6)

NetpbmWriter only writes ASCII (P1/P2/P3); binary write not implemented. Status: NOT_IMPLEMENTED.

**Acceptance Criteria:**
- New tests pass for GAP-CAP-002
- Netpbm .NET capability implemented or documented

**Files:**
- `src/net/netpbm/`
- `tests/net/netpbm/`

**Verification:**
```bash
dotnet test tests/net/netpbm/ --verbosity quiet
```

## Group G4: FOSS / Reduced Product

### Train F: ZST Python Improvement

Continue ZST FOSS product. Document dependency mode; verify installed workflow from review package

**Acceptance Criteria:**
- ZST Python test count maintained or increased

**Files:**
- `src/python/zst/`
- `tests/python/zst/`

**Verification:**
```bash
python -m pytest tests/python/zst/ -x -q
```

### Train G: Netpbm Python: Write Ppm

Implement write_ppm for Netpbm. R85 Train M: implement PBM→PGM dogfood export + test

**Acceptance Criteria:**
- write_ppm tests pass
- python_status.write_ppm updated to PASS in poc-targets.yaml

**Files:**
- `src/python/netpbm/`
- `tests/python/netpbm/`

**Verification:**
```bash
python -m pytest tests/python/netpbm/ -x -q
```

### Train H: SYLK Python: Write Sylk

Implement write_sylk for SYLK. Document read+export-only scope; add installed example; update docs

**Acceptance Criteria:**
- write_sylk tests pass
- python_status.write_sylk updated to PASS in poc-targets.yaml

**Files:**
- `src/python/sylk/`
- `tests/python/sylk/`

**Verification:**
```bash
python -m pytest tests/python/sylk/ -x -q
```

## Group G5: Dogfood Exports

### Train I: Dogfood: fodt -> txt

No FF .NET text write library. Prerequisite: Build FormatFactory.Text .NET library with write_text().

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml

### Train J: Dogfood: fodt -> html

No FF .NET HTML write library. Prerequisite: Build FormatFactory.Html .NET library.

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml

## Group G6: Package / Install Proof

### Train K: Package Build + Install Proof

Rebuild wheels/sdists for any changed packages. Run installed-workflow smoke test from extracted wheel.

**Acceptance Criteria:**
- All changed packages rebuilt
- Installed import test passes
- Package artifacts present in evidence directory

**Files:**
- `packaging/`

**Verification:**
```bash
python -m pytest tests/evidence/ -x -q
```

## Group G7: State / Memory / POC Matrix

### Train L: State + Memory + POC Matrix Sync

Update state/current-state.md, .supervisor/project-memory.md, and product-capability-matrix/poc-targets.yaml with sprint results.

**Acceptance Criteria:**
- poc-targets.yaml reflects actual status (no overclaiming)
- state/current-state.md updated
- project-memory.md entry appended

**Files:**
- `state/current-state.md`
- `.supervisor/project-memory.md`
- `product-capability-matrix/poc-targets.yaml`

## Group G8: Evidence + Supervisor Loop

### Train M: Evidence Declaration + Supervisor Autonomous-Cycle

Write evidence-declaration.yaml listing ALL work items. Run autonomous-cycle. Verify session-resume.md is regenerated.

**Acceptance Criteria:**
- evidence-declaration.yaml written with all work items
- autonomous-cycle exits 0 or 3
- session-resume.md regenerated with current data
- approval-gates.md shows correct AUTONOMOUS_CONTINUE

**Files:**
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `reports/supervisor/session-resume.md`

**Verification:**
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```


---

## Hard Prohibitions

- No `git push` without explicit user authorization.
- No `git commit` without explicit user authorization.
- No Gate 8 or Gate 11 approval (requires Babar Raza).
- No `commercial_product_ready: true` in any file.
- No PyPI / NuGet / GitHub release publication.
- No paid external AI API or web automation.
- No MCP activation unless MODE 4 already authorized.
- No destructive git operations (`git reset --hard`, `git clean -fd`, force-push).
- No deletion of existing test files.
- No PENDING markers in final state files.
- No overclaiming: if evidence is missing, declare status honestly.

---

## Final Validation Sequence

After all trains complete, run this exact sequence:

```bash
# 1. Python tests
.local/venv/Scripts/python -m pytest tests/ -x -q --tb=short

# 2. Compile check on supervisor tools
.local/venv/Scripts/python -m py_compile tools/supervisor/autonomous_cycle.py
.local/venv/Scripts/python -m py_compile tools/supervisor/supervisor_loop.py
.local/venv/Scripts/python -m py_compile tools/supervisor/generate_supervisor_packet.py

# 3. .NET tests (if .NET work was done)
dotnet test tests/net/ --verbosity quiet

# 4. Write evidence declaration
# (create .local/evidences/<run_id>/evidence-declaration.yaml)

# 5. Run supervisor autonomous-cycle
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Allowed Verdicts

The sprint MUST end with one of these verdicts in the evidence declaration:

| Verdict | Meaning |
|---------|---------|
| ALL_TRAINS_COMPLETE | All trains passed acceptance criteria |
| PARTIAL_TRAINS_COMPLETE_PUBLICATION_BLOCKED | Some trains done, publication gate blocks remaining |
| REWORK_REQUIRED | Supervisor review found issues requiring repair |
| BLOCKED_EXTERNAL_GATE | Cannot proceed without external gate approval |

---

## Final Artifact Specification

At sprint end, these files MUST exist:

- `.local/evidences/<run_id>/evidence-declaration.yaml` -- declaration of all work items
- `reports/supervisor/session-resume.md` -- regenerated by autonomous-cycle
- `reports/supervisor/approval-gates.md` -- regenerated by autonomous-cycle
- `product-capability-matrix/poc-targets.yaml` -- updated if any product status changed
- `state/current-state.md` -- updated with sprint outcome

---

END OF SUPERVISOR-GENERATED MEGA-TRAIN EXECUTION PROMPT
