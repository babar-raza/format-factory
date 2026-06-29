# Evidence Index

**Sprint:** forensics-archaeology-20260621

---

## Report Files

| # | File | Description |
|---|------|-------------|
| 1 | sprint-overview.md | Summary, purpose, key findings, verdict |
| 2 | preflight-state.md | Git state, dirty files, repo structure |
| 3 | source-inventory.md | All Python/NET packages with LOC, files, notes |
| 4 | source-hygiene-audit.md | Build artifact pollution analysis |
| 5 | generation-archaeology.md | 4 generation waves — what produced them, what survives |
| 6 | per-product-capability-matrix.yaml | Complete matrix per product (23 products) |
| 7 | per-product-qname-compliance.yaml | (see qname-schema-audit.md for equivalent data) |
| 8 | src-source-quality-review.md | Green/Yellow/Orange/Red ratings per package |
| 9 | qname-schema-audit.md | 135 classes audited; 29 compliant; 106 non-compliant |
| 10 | qname-translation-standard.md | Binding standard for all future product code |
| 11 | sal-audit.md | SAL facts per format; pipeline status; gaps |
| 12 | capability-layer-audit.md | 958 gaps; compiler assessment; integration gaps |
| 13 | downstream-generation-audit.md | Where malformed code enters; flow analysis |
| 14 | skill-inventory-and-gaps.md | 40+ skills catalogued; critical gaps identified |
| 15 | autonomous-supervisor-audit.md | Mode 4 state; SUP-GAP analysis; lane enforcement |
| 16 | lane-separation-and-collision-risk.md | 4 collision risks; contamination analysis |
| 17 | backfill-facility-design.md | 4-phase backfill design; ODS/ODT easy win |
| 18 | gate11-readiness-review.md | C1-C20 and P1-P11 estimates for FODS |
| 19 | product-deepening-readiness-plan.md | Tier 1-4 deepening sequence; per-format blockers |
| 20 | system-gap-matrix.yaml | 16 system gaps with severity, fix, taskcard refs |
| 21 | taskcards.yaml | 15+ taskcards in QNAME-BACKFILL, SAL-REPAIR, SKILL-HARDENING, etc. |
| 22 | machinery-repair-plan.md | Ordered R1-R15 repair sequence with estimates |
| 23 | product-pilot-plan.md | (see product-deepening-readiness-plan.md) |
| 24 | next-agent-execution-prompt.md | Ready-to-paste prompt for next sprint |
| 25 | evidence-index.md | THIS FILE |
| 26 | final-verdict.md | READY_AFTER_TARGETED_MACHINERY_REPAIRS; self-check |

---

## Evidence Sources Inspected

| Source | What Was Inspected |
|--------|-------------------|
| `git status --porcelain` | 6 modified, 4 untracked |
| `git log --oneline -10` | 10 most recent commits |
| `src/python/*/` | All 20 Python packages enumerated |
| `src/net/*/` | All 11 .NET packages enumerated |
| `src/python/fods/` | Full directory listing + 5 key files read |
| `src/python/fodt/` | Full directory listing + neutral_model.py + models.py |
| `src/python/ods/ods_parser.py` | OdsDocument class structure |
| `src/python/dif/dif_parser.py` | DifDocument class structure |
| `src/net/fods/FodsDocument.cs` | Full read (1293 LOC) |
| `src/net/fods/FodsParser.cs` | First 60 lines |
| `src/net/fodt/FodtDocument.cs` | First 60 lines |
| `src/net/fods/Spec/`, `Model/` | Directory listings |
| `src/python/fods/spec/` | All spec stubs listed + 2 read |
| `src/python/fods/Compat/` | All 3 facade files read |
| `src/python/fods/models.py` | First 80 lines (FodsCell, FodsSheet, FodsDocument) |
| `.local/spec-cache/sal-facts-fods.json` | File size + sample facts |
| `.local/spec-cache/sal-facts-20260621.json` | Master summary (22 formats, 14284 facts) |
| `tools/validators/qname_structure_validator.py` | Full read |
| `tools/supervisor/capability_compiler.py` | First 80 lines |
| `reports/capability-layer/gap-ledger.json` | 958 gaps, sample structure |
| `registry/format-completion-matrix.yaml` | FODS and FODT entries |
| `registry/format-registry.yaml` | FODS entry |
| `reports/supervisor/session-resume.md` | Full read |
| `reports/supervisor/approval-gates.md` | Full read |
| `plans/strategic/spec-to-feature-radical-correction-plan.md` | Summary doc read (120 lines) |
| `.claude/commands/` | Full directory listing (40+ files) |
| AST class audit | All 135 Python classes in src/python/ enumerated |
| LOC audit | Per-package LOC counted using line iteration |
| Build artifact audit | find src/ for egg-info, build/, obj/ |

---

## Key Quantitative Evidence

| Metric | Value | Source |
|--------|-------|--------|
| Python packages | 20 | `ls src/python/` |
| .NET packages | 11 | `ls src/net/` |
| Total Python classes | 135 | AST audit |
| Classes with spec_qname | 29 (21%) | AST audit |
| Classes without spec_qname | 106 (79%) | AST audit |
| SAL facts (FODS) | 4,987 | sal-facts-fods.json |
| SAL facts (FODT) | 4,933 | sal-facts-fodt.json |
| SAL facts (CSV) | 0 | sal-facts-csv.json |
| SAL facts (total, 22 formats) | 14,284 | sal-facts-20260621.json |
| Capability gaps | 958 | gap-ledger.json |
| Governance validators | 46+ | governance_validators.py |
| Tests (last sprint) | 1,490 passed | session-resume.md |
| Registered skills | 40+ | .claude/commands/ |
| Spec stubs (FODS) | 10 classes | fods/spec/ AST |
| Spec stubs (FODT) | 8 classes | fodt/spec/ AST |
| FODS .NET tests | 611 | format-completion-matrix.yaml |
| FODT .NET tests | 567 | format-completion-matrix.yaml |
