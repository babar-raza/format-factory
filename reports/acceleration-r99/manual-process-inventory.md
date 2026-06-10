# Manual Process Inventory — Train A

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Inventory of Recurring Agent Actions (R86-R98)

### 1. Source Editing

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Add .NET API method | Every sprint | Governed via `/add-dotnet-api` skill | ALREADY_AUTOMATED |
| Add Python API method | Every sprint | Governed via `/add-python-api` skill | ALREADY_AUTOMATED |
| Add dogfood export | Occasional | Governed via `/add-dogfood-export` skill | ALREADY_AUTOMATED |
| Add object model feature | Every sprint | Governed via `/add-dotnet-object-model-feature` | ALREADY_AUTOMATED |
| Add same-format writer | Occasional | Governed via `/add-same-format-writer-feature` | ALREADY_AUTOMATED |

### 2. Adding Tests

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Write focused .NET tests | Every sprint | Manual (skill produces test path) | PARTIALLY_AUTOMATED |
| Write focused Python tests | Every sprint | Manual | PARTIALLY_AUTOMATED |
| Add roundtrip test | Occasional | Governed via `/add-roundtrip-test` | ALREADY_AUTOMATED |
| Capture raw test logs | Every sprint | Manual redirect to file | SHOULD_BECOME_SKILL |

### 3. Updating POC Matrix

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Update poc-targets.yaml | Every sprint | Governed via `/update-capability-matrix` | ALREADY_AUTOMATED |
| Verify matrix accuracy | Occasional | Manual comparison | SHOULD_BECOME_SUPERVISOR_TOOL |

### 4. Updating Product-Code Ledger

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Add ledger entry | Every src edit | Manual JSON edit | PARTIALLY_AUTOMATED |
| Validate ledger | Every sprint | `validate_product_code_ledger.py` | ALREADY_AUTOMATED |

### 5. Generating Reports

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Write preflight report | Every sprint | Manual | SHOULD_BECOME_SKILL |
| Write lane ownership | Every sprint | Manual | SHOULD_BECOME_SKILL |
| Write parallel execution map | Every sprint | Manual | SHOULD_BECOME_SKILL |
| Write scoreboard | Every sprint | Manual (copy pattern) | SHOULD_BECOME_SKILL |
| Write agent-learning-notes | Every sprint | Manual | SHOULD_BECOME_SKILL |
| Write speed-bottlenecks | Every sprint | Manual | SHOULD_BECOME_SKILL |

### 6. Building Evidence Packages

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Write evidence-declaration.yaml | Every sprint | Manual YAML | PARTIALLY_AUTOMATED |
| Run materializer | Every sprint | `materialize_declared_evidence.py` | ALREADY_AUTOMATED |
| Build review package | Every sprint | `build_declaration_review_package.py` | ALREADY_AUTOMATED |
| Report review package SHA | Every sprint | Manual copy from output | SHOULD_BECOME_SUPERVISOR_TOOL |

### 7. Context and State Management

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Build context pack | Every sprint | `build_context_pack.py` | ALREADY_AUTOMATED |
| Check MCP status | Every sprint | `check_mcp_status.py` | ALREADY_AUTOMATED |
| Read session-resume.md | Every sprint | Manual | REMAINS_MANUAL (session init) |
| Read approval-gates.md | Every sprint | Manual | REMAINS_MANUAL (governance) |

### 8. Product Gap Selection and Routing

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Select POC gaps | Every sprint | `select_poc_gaps.py` | PARTIALLY_AUTOMATED |
| Choose skill vs handoff | Every sprint | `choose_skill_or_handoff.py` | PARTIALLY_AUTOMATED |
| Generate execution handoff | Occasional | `/generate-execution-handoff` skill | ALREADY_AUTOMATED |
| Promote gap to taskcard | Occasional | `/promote-gap-to-taskcard` skill | ALREADY_AUTOMATED |

### 9. Package and Install Proof

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Build wheel | Occasional | Manual pip command | SHOULD_BECOME_SUPERVISOR_TOOL |
| Install and import test | Occasional | Manual venv + pip | SHOULD_BECOME_SUPERVISOR_TOOL |
| `/package-install-proof` skill | Exists | Skill command available | ALREADY_AUTOMATED |

### 10. Dogfood Verification

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Verify FF library backend | Occasional | `/verify-dogfood-path` skill | ALREADY_AUTOMATED |
| Run dogfood export tests | Occasional | Manual test invocation | PARTIALLY_AUTOMATED |

### 11. Lane Execution Recording

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Record lane start/end/files | Every train | MISSING | SHOULD_BECOME_SUPERVISOR_TOOL |
| Track concurrency groups | Every sprint | MISSING | SHOULD_BECOME_SUPERVISOR_TOOL |
| Lane execution ledger | Every sprint | MISSING | SHOULD_BECOME_SUPERVISOR_TOOL |

### 12. Detect Product Progress

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Compare snapshots | Every sprint | `detect_product_progress.py` | ALREADY_AUTOMATED |
| Write progress snapshot | Every sprint | CLI flag `--write-snapshot` | ALREADY_AUTOMATED |

### 13. Sprint Learning

| Action | Frequency | Current State | Recommendation |
|--------|-----------|---------------|----------------|
| Identify speed bottlenecks | End of sprint | Manual notes | SHOULD_BECOME_SKILL |
| Identify manual-to-skill candidates | End of sprint | Manual notes | SHOULD_BECOME_SKILL |
| Generate next-agent briefing | End of sprint | MISSING | SHOULD_BECOME_SKILL |

## Classification Summary

| Category | Count |
|----------|-------|
| ALREADY_AUTOMATED | 16 |
| PARTIALLY_AUTOMATED | 5 |
| SHOULD_BECOME_SKILL | 8 |
| SHOULD_BECOME_SUPERVISOR_TOOL | 5 |
| REMAINS_MANUAL (governance) | 2 |
| MISSING (no solution) | 3 |

## Priority Actions for This Sprint

1. Create `record_lane_execution.py` (MISSING, high frequency)
2. Create sprint learning generator (MISSING, every sprint)
3. Enhance `select_poc_gaps.py` with stream-awareness (PARTIALLY_AUTOMATED)
4. Enhance `choose_skill_or_handoff.py` with skill registry integration (PARTIALLY_AUTOMATED)
5. Create package/install proof tool (bridge existing skill to CLI)
6. Document evidence materialization quick-path (reduce manual steps)
