# Preflight State
# Sprint: ff-machinery-readiness-audit-20260625
# Generated: 2026-06-25

## Git State

| Field | Value |
|---|---|
| Branch | main |
| HEAD | c7694fe4 |
| HEAD Message | chore(psl-close): immutable-percolating-forest CLOSED — §64 added, all-green convergence verified |
| Prior commits | 0e880794 (CI machinery hardening), af54d34b (GOV-ENFORCE closure), e7e4011a (PSL loop closed), 01a28925 (supervisor reports sync) |
| Working tree | PARTIALLY DIRTY (28 modified/untracked files) |

## Dirty Files Classification

Current `git status --short` output (28 files):

### Modified Files — Machinery/Governance (8 files)
| File | Classification |
|---|---|
| .supervisor/context-pack.yaml | machinery_source |
| tools/supervisor/guard_001_checker.py | machinery_source |
| tools/supervisor/product_task_selector.py | machinery_source |
| tests/supervisor/test_governance_validators.py | machinery_source |
| tests/supervisor/test_tc_guard_001_enforce.py | machinery_source |
| docs/architecture.md | plans_and_docs |
| docs/automation/supervisor-worker-contract.md | plans_and_docs |
| reports/gate11/fods-gate11-check-gate-result.md | generated_evidence |

### Modified Files — Generated Evidence (6 files)
| File | Classification |
|---|---|
| reports/capability-layer/gap-sal-traceability-20260625.json | generated_evidence |
| reports/sal-qname-gap-20260625.json | generated_evidence |
| reports/supervisor-streams/mainstream/contradictions.json | generated_evidence |
| reports/supervisor-streams/mainstream/evidence-review.json | generated_evidence |
| reports/supervisor/context-pack.md | generated_evidence |
| reports/supervisor/contradictions.json + evidence-review.json + grading-history.jsonl + materialized-evidence-review.md + maturity-signal.json | generated_evidence |

### Modified Files — Product Source (2 files)
| File | Classification |
|---|---|
| src/net/netpbm/NetpbmExporter.cs | product_source |
| src/python/fods/pyproject.toml | product_source (packaging config) |

### Untracked Files (8 items)
| File | Classification |
|---|---|
| reports/forensic-audit-20260625/ | generated_evidence (prior audit) |
| reports/skill-governance-forensic/ | generated_evidence |
| reports/spec-authority-machinery/spec-authority-machinery-explosion-20260625-c6b2470/audit/ | generated_evidence |
| src/python/fods/__init__.pyi | product_source (type stub) |
| src/python/fodt/__init__.pyi | product_source (type stub) |
| src/python/gnumeric/__init__.pyi | product_source (type stub) |
| src/python/ndjson/__init__.pyi | product_source (type stub) |
| src/python/toml/__init__.pyi | product_source (type stub) |

**Risk assessment:** LOW. No risky/conflicting files. Modified product source is minimal (NetpbmExporter.cs, pyproject.toml). Type stubs are new untracked additions. Prior audit artifacts are already committed — the large count seen by Phase 1 agents reflected pre-commit state.

## Governance State

### Continuation Signal (.local/supervisor/continuation-signal.json)
- autonomous_continue: true
- iteration: 7/12
- continuation_state: YES
- session_id: 5c16c5c46b6f
- source_sprint_id: ff-sprint-s63-checkgate-fods11-20260626
- hard_stops_detected: []
- rework_items: []
- global_repair_applied: true

### Approval Gates (reports/supervisor/approval-gates.md)
- AUTONOMOUS_CONTINUE: YES
- Current Mode: MODE 4 (ACTIVE_MCP_ACTIVATION)
- NEXT_HUMAN_GATE: MODE 5 autonomous sprint loop (explicit user approval required)
- MCP_STATUS: ACTIVE (.vscode/mcp.json verified present)
- DAEMON_STATUS: NOT_STARTED

### Last Sprint (reports/supervisor/session-resume.md)
- Sprint ID: ff-gates-advancement-20260625
- Evidence verdict: ACCEPTED
- Tests: 1609 passed / 0 failed
- PENDING markers: 0
- CRITICAL contradictions: 0

### Next Sprint Direction (reports/supervisor/next-sprint.md)
- Focus: ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging
- Open taskcards: TC-0015 (spec-retrieval-strategy), TC-0016 (fods-vector-index-pilot), TC-0020 (spec-workbench-core)

## Key Infrastructure State

### Plans (read at session start per CLAUDE.md)
- plans/master-plan.md — v6.0 (multiple sprints confirmed ACCEPTED 2026-06-25)
- plans/strategic/spec-to-feature-radical-correction-plan.md — BINDING AUTHORITY; 27 sections; 6 systemic failures documented
- No per-chat plan loaded for this session (audit sprint)

### Evidence Directories
- .local/evidences/ — multiple sprint bundles (ff-gates-advancement-20260625, ff-ods-dogfood-20260625, etc.)
- .local/supervisor/reviews/ — ZIP packages for each sprint
- reports/machinery-readiness-audit-20260625/ — THIS AUDIT (being created now)

### Existing Audit Reports (pre-existing, not this sprint)
- reports/forensic-audit-20260625/ — prior forensic audit artifacts
- reports/spec-authority-machinery/ — SAL machinery explosion audit
- reports/skill-governance-forensic/ — skill governance forensics

## Classification Summary

| Category | Count | Risk |
|---|---|---|
| machinery_source | 5 | LOW (tests + tools) |
| product_source | 4 | LOW (NetpbmExporter, pyproject.toml, type stubs) |
| generated_evidence | 13 | LOW (reports, supervisor outputs) |
| plans_and_docs | 2 | LOW (architecture docs) |
| unknown | 4 | LOW (new type stubs, clearly identified) |
| **Total** | **28** | **LOW** |

No risky or conflicting files detected. Safe to proceed with audit.
