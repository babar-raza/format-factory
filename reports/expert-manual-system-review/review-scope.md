# Review Scope
# Expert Manual System Review — Format Factory

## Scope Statement

This expert manual review covers the entire Format Factory system with special emphasis on
the `src/` folder as the real product output. The review is system-first: product weaknesses
are traced to their producing or validating system before product repair is recommended.

## What Is In Scope

### Product Code
- `src/net/` — 10 .NET projects (CSV, FODS, FODT, HTML, Markdown, NDJSON, NetPBM, TSV, TXT, ZST)
- `src/python/` — 20 Python packages (ABW, CSV, DIF, FODG, FODP, FODS, FODT, GNUMERIC, NDJSON, ODS, ODT, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, ZST)
- `examples/` — .NET and Python examples
- `tests/` — all test suites

### Authority Layers
- `registry/format-registry.yaml` — format scoring and classification
- `registry/parity-matrix.yaml` — spec parity status
- `product-capability-matrix/poc-targets.yaml` — capability proof matrix (read-only during review)
- `shared/qname-registry/` — 20 QName YAML files
- `registry/source-structure-baseline.json` — LOC caps

### Autonomous System
- `tools/supervisor/` — supervisor scripts (autonomous_cycle.py, governance_validators.py, check_continuation.py, etc.)
- `.supervisor/` — skill registry, policies, capability routing
- `reports/supervisor/` — session state files
- `.local/evidences/` — evidence bundles

### Specification Authority
- `.local/spec-cache/` — SAL spec fact files
- `shared/qname-registry/` — QName authority

### Evidence and Outputs
- `reports/capability-layer/` — gap ledger, capability map
- `reports/supervisor/` — session-resume, approval-gates, next-sprint
- Evidence bundles in `.local/evidences/`

## What Is Out of Scope (During This Review)

- Any modifications to src/, tests/, registry/, poc-targets.yaml, .supervisor/policies.yaml
- Commits, pushes, publications
- Gate 8 or Gate 11 approval changes
- New feature implementation

## Review Deliverables

All deliverables written to `reports/expert-manual-system-review/`:

### Phase 0 (Preflight)
- 00-preflight.md ✓
- current-git-status.txt ✓
- review-scope.md ✓ (this file)
- file-ownership-map.json
- review-methodology.md
- expert-review-questions.md
- plan-mode-limitations.md

### Phase 1 (System Map)
- system-map.md
- system-map.json
- repo-inventory.md
- repo-inventory.json

### Phase 2 (src/ Inventory)
- src-inventory.md
- src-inventory.json
- src-review-plan.md
- src-review-checklist.md
- src-format-matrix.json

### Phase 3 (.NET Commercial Review)
- dotnet-commercial-review-plan.md
- dotnet-commercial-review-matrix.json
- dotnet-commercial-quality-rubric.md

### Phase 4 (Python FOSS Review)
- python-foss-review-plan.md
- python-foss-review-matrix.json
- python-feature-requirement-model.md

### Phase 5 (Layer Review)
- layer-review-plan.md
- layer-review-matrix.json

### Phase 6 (Output Review)
- output-review-plan.md
- evidence-output-matrix.json

### Phase 7 (Problem Matrix)
- problem-matrix-template.md
- problem-matrix-schema.json
- problem-confirmation-process.md
- phase-a-investigation/confirmed-problems.json

### Phase 8-9 (Execution Design and Rubrics)
- review-execution-phases.md
- dry-run-plan.md
- live-readonly-run-plan.md
- pilot-run-plan.md
- code-quality-rubric.md
- commercial-readiness-rubric.md
- foss-readiness-rubric.md
- autonomy-layer-rubric.md
- evidence-quality-rubric.md

### Phase 10 (Master Plan)
- manual-review-master-plan.md
- manual-review-master-plan.json
- initial-risk-register.md
- initial-risk-register.json
- recommended-review-sequence.md
- final-plan-mode-summary.md

### Phase 11 (Validation)
- raw-logs/plan-validation.log
- final-git-status.txt
