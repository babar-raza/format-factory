# TC-README-PLAN-002: Repository State Map
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

All claims marked: CONFIRMED_FROM_FILES | PROPOSED | UNVERIFIED

---

## 1. Source Directories

### src/net/ — .NET Commercial Products

| Directory | Key Files | Status |
|-----------|-----------|--------|
| src/net/fods/ | FodsDocument.cs, FodsParser.cs, FodsWriter.cs, FodsJsonExporter.cs, FodsCsvExporter.cs, FodsHtmlExporter.cs, Model/(FodsCell, FodsRow, FodsSheet) | CONFIRMED_FROM_FILES |
| src/net/fodt/ | FodtDocument.cs, FodtParser.cs, FodtWriter.cs, FodtHtmlExporter.cs, FodtMarkdownExporter.cs, FodtTxtExporter.cs, Model/(FodtBody, FodtParagraph) | CONFIRMED_FROM_FILES |
| src/net/netpbm/ | NetpbmImage.cs, NetpbmParser.cs, NetpbmWriter.cs, NetpbmExporter.cs, NetpbmException.cs, FormatFactory.Netpbm.csproj | CONFIRMED_FROM_FILES |
| src/net/csv/ | FormatFactory.Csv.csproj, CsvWriter.cs | CONFIRMED_FROM_FILES |
| src/net/html/ | FormatFactory.Html.csproj, HtmlWriter.cs | CONFIRMED_FROM_FILES |
| src/net/txt/ | FormatFactory.Txt.csproj, TxtWriter.cs | CONFIRMED_FROM_FILES |
| src/net/markdown/ | FormatFactory.Markdown.csproj, MarkdownWriter.cs | CONFIRMED_FROM_FILES |

**Note on target writer libraries (csv, html, txt, markdown):** These were built in sprint
`FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001` to unblock dogfood export paths
for FODS→CSV, FODS→HTML, FODT→TXT, FODT→Markdown. They are standalone format-factory writer
libraries (not format parsers). CONFIRMED_FROM_FILES.

### src/python/ — Python FOSS Products

Confirmed from directory listing (_readme.md present at root). Active POC format subdirs include:

| Directory | POC Status |
|-----------|-----------|
| src/python/fods/ | CONFIRMED — FODS Python parser |
| src/python/fodt/ | CONFIRMED — FODT Python parser |
| src/python/pbm/ | CONFIRMED — PBM (Netpbm family, FOSS target) |
| src/python/pgm/ | CONFIRMED — PGM (Netpbm family, FOSS target) |
| src/python/ppm/ | CONFIRMED — PPM (Netpbm family, FOSS target) |
| src/python/sylk/ | CONFIRMED — SYLK parser (FOSS target) |
| src/python/zst/ | CONFIRMED — ZST/Zstandard (FOSS target) |
| src/python/dif/ | CONFIRMED — DIF parser (ON_HOLD) |
| src/python/abw/ | CONFIRMED — AbiWord (Gate 1 approved) |
| src/python/csv/ | CONFIRMED — CSV |
| src/python/ods/ | CONFIRMED — ODS |
| src/python/odt/ | CONFIRMED — ODT |
| src/python/fodg/ | CONFIRMED — FODG |
| src/python/fodp/ | CONFIRMED — FODP |
| src/python/gnumeric/ | CONFIRMED — Gnumeric |
| src/python/qoi/ | CONFIRMED — QOI |
| src/python/tsv/ | CONFIRMED — TSV |
| src/python/xcf/ | CONFIRMED — XCF |

Total Python format directories: 18+ | CONFIRMED_FROM_FILES

---

## 2. Test Directories

### tests/net/

| Directory | Test Files (approx) |
|-----------|-------------------|
| tests/net/fods/ | 116+ test files (FodsR94 through FodsR116) | CONFIRMED_FROM_FILES |
| tests/net/fodt/ | 115+ test files (FodtR94 through FodtR116) | CONFIRMED_FROM_FILES |
| tests/net/netpbm/ | 48+ test files (NetpbmR94 through NetpbmR116) | CONFIRMED_FROM_FILES |

### tests/python/

Active POC format test directories:

| Directory | Status |
|-----------|--------|
| tests/python/sylk/ | CONFIRMED — 16+ test files |
| tests/python/zst/ | CONFIRMED — 20+ test files |
| tests/python/ppm/ | CONFIRMED — 16+ test files |
| tests/python/pbm/ | CONFIRMED — 12+ test files |
| tests/python/pgm/ | CONFIRMED — 6+ test files |
| tests/python/dif/ | CONFIRMED — 7+ test files |
| tests/python/fods/ | CONFIRMED |
| tests/python/fodt/ | CONFIRMED |
| tests/python/supervisor/ | CONFIRMED — supervisor/automation tests |

Total test dirs under tests/python/: 20+ | CONFIRMED_FROM_FILES

---

## 3. Examples Directory

### examples/net/ (C# class files)

| Directory | Example Files |
|-----------|--------------|
| examples/net/fods/ | ExportCsvExample.cs, CopySheetExample.cs, ClearSheetExample.cs, RowManipulationExample.cs |
| examples/net/fodt/ | DocumentStatsExample.cs, HtmlExportExample.cs, TextRangeExample.cs |
| examples/net/netpbm/ | LoadEditSaveExample.cs, PixelEditSaveExample.cs, FlipOverlayExample.cs, MergeBrightnessExample.cs, MergeContrastExample.cs |

### examples/dotnet/ (dotnet-script .csx files)

| Directory | Example Files |
|-----------|--------------|
| examples/dotnet/fods/ | export_sheet_to_csv.csx |
| examples/dotnet/fodt/ | export_to_plain_text.csx |
| examples/dotnet/netpbm/ | equalize_and_convert.csx |

### examples/python/

| Directory | Example Files |
|-----------|--------------|
| examples/python/fods/ | edit_save_fods.py, edit_save_export_fods.py, edit_save_export_fods_installed.py |
| examples/python/fodt/ | edit_save_fodt.py, edit_save_export_fodt.py, edit_save_fodt_installed.py |
| examples/python/pbm/ | pbm_to_pgm_example.py |
| examples/python/ppm/ | pgm_to_ppm_example.py |
| examples/python/sylk/ | write_export_sylk.py, sylk_csv_pipeline.py |
| examples/python/zst/ | compress_decompress_file.py, validate_compressed_file.py |
| examples/python/abw/ | extract_text.py |
| examples/python/fodp/ | extract_presentation_text.py |
| examples/python/fodg/ | inspect_drawing_shapes.py |
| examples/python/gnumeric/ | extract_cells.py |

All confirmed from glob. CONFIRMED_FROM_FILES.

---

## 4. POC Targets (from product-capability-matrix/poc-targets.yaml)

### Commercial .NET Products (3)

| Format | Gate Status | Source | Tests |
|--------|------------|--------|-------|
| FODS .NET | Gates 1–10 PASSED; Gate 11 G11-G NOT_STARTED | src/net/fods/ | tests/net/fods/ (116+) |
| FODT .NET | Gates 1–10 PASSED; Gate 11 G11-G NOT_STARTED | src/net/fodt/ | tests/net/fodt/ (115+) |
| Netpbm .NET | POC active | src/net/netpbm/ | tests/net/netpbm/ (48+) |

All three: CONFIRMED_FROM_FILES.

### FOSS / Reduced Products (3 active)

| Format | POC Status | Source | Tests |
|--------|-----------|--------|-------|
| ZST (Zstandard) | production_track_real, POC active | src/python/zst/ | tests/python/zst/ (20+) |
| Python Netpbm (PBM/PGM/PPM) | production_track_real, POC active | src/python/pbm/, pgm/, ppm/ | tests/python/pbm/, pgm/, ppm/ |
| SYLK | POC active | src/python/sylk/ | tests/python/sylk/ (16+) |

All three: CONFIRMED_FROM_FILES.

### On-Hold (2)

| Format | Status |
|--------|--------|
| QOI | ON_HOLD |
| DIF | ON_HOLD (empirical evidence exists in tests/python/dif/ but not promoted) |

---

## 5. Stream State (from state/current-state.md, 2026-06-04)

| Stream | Latest Sprint | State | Next Priority |
|--------|--------------|-------|---------------|
| Mainstream | R113 | ACCEPTED; product breadth weak; product-first push active | Force real breadth: FODS, FODT, Netpbm .NET + FOSS |
| Acceleration | R111 | Governance progress; AI acceleration being restored | Restore AI product acceleration |
| Skills | R113 | Strong milestone; near-live v3 handoff proof | Full live cycle, stream convergence |
| Supervisor | R110 | Real stream-local authority, 1050 tests | Ledger, sample outputs, replay closure |

**Latest accepted sprint (session-resume.md):** R118 (FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001)
CONFIRMED_FROM_FILES.

---

## 6. Governance Documents

### docs/governance/ (13 files — CONFIRMED_FROM_FILES)

| File | Purpose |
|------|---------|
| four-stream-operating-model.md | Defines 4 streams: Mainstream, Acceleration, Skills, Supervisor |
| lane-definitions.md | Hard rules per stream, outputs, authority |
| acceleration-definition.md | Acceleration-A (Governance) + Acceleration-B (AI Product) split |
| autonomous-supervisor-role.md | Supervisor as traffic controller; 6 responsibilities; 5 must-nots |
| mainstream-product-output-floor.md | Minimum deliverables per stream PASS |
| machinery-success-criteria.md | Grading impact table; anti-patterns |
| product-first-operating-model.md | 5 operating rules; hard PASS quota; product-output floor |
| ai-authority-boundary.md | "AI thinks and drafts. Evidence decides." MAY/MAY NOT tables |
| external-tool-architecture.md | Ruflo, Superpowers, GhidraMCP — modes, risk register |
| ruflo-runtime-governance.md | Ruflo mode transitions; what it controls/does-not-control |
| superpowers-skill-intake.md | 5-step normalization; risk classification |
| ghidra-mcp-compliance-gate.md | DISABLED_BY_DEFAULT; 6 gate conditions; hard prohibitions |
| mainstream-poc-mega-train.md | Continuation loop; 8 hard stops; 7 false stops |

---

## 7. Prompt Templates

### docs/prompt-templates/ (15 files — CONFIRMED_FROM_FILES)

| File | Stream |
|------|--------|
| lane-planning-template.md | All streams |
| mainstream-product-execution-template.md | Mainstream |
| acceleration-ai-product-execution-template.md | Acceleration |
| skills-governed-execution-template.md | Skills |
| supervisor-autonomous-continuation-template.md | Supervisor |
| evidence-review-template.md | All |
| final-adversarial-iv-template.md | All |
| stream-state-reconciliation-template.md | All |
| next-sprint-generation-template.md | Supervisor |
| cross-stream-dependency-template.md | All |
| mainstream-poc-mega-train-template.md | Mainstream |
| repair-order-reference.md | All |
| format-factory-stream-prompt-requirements.md | All |
| external-tool-aware-repair-template.md | All |
| README.md | Index |

---

## 8. Supervisor Tools

### tools/supervisor/ (39 Python scripts — CONFIRMED_FROM_FILES)

Key tools by function:

| Tool | Function |
|------|----------|
| supervisor_loop.py | Main control plane CLI |
| autonomous_cycle.py | Declaration-driven sprint cycle |
| build_context_pack.py | Project state snapshot |
| generate_next_worker_prompt.py | Next sprint prompt generation |
| grade_declared_work.py | Work item grading engine (12 grade levels) |
| materialize_declared_evidence.py | Evidence resolver + SHA-256 |
| anti_skip_checker.py | 18 detectors for sprint quality |
| detect_product_progress.py | Product progress classifier |
| validate_product_code_ledger.py | Ledger validator (R90+ governance) |
| validate_evidence_for_supervisor.py | Evidence bundle validator |
| build_declaration_review_package.py | ZIP review package builder |
| select_poc_gaps.py | Next POC gap selection |
| check_cross_stream_consumption.py | Skills/Acceleration bridge |
| generate_stream_routing_packet.py | Velocity scoring + routing |
| build_proof_graph_iter003.py | Proof graph construction |

---

## 9. Skill Registry

**File:** `.supervisor/skill-registry.yaml` CONFIRMED_FROM_FILES

| Metric | Value |
|--------|-------|
| Total skills | 25 |
| Active skills | 24 |
| Deferred skills | 1 (check-mcp-status — no command file) |
| Skill command files | .claude/commands/*.md (30 files) |

Key skill categories:
- Core product skills (R90): add-dotnet-api, add-python-api, add-dogfood-export, update-capability-matrix
- Object model skills (R93+): add-dotnet-object-model-feature, add-python-object-model-feature
- Writer/roundtrip skills: add-same-format-writer-feature, add-roundtrip-test
- Package skills: add-installed-package-example, package-install-proof
- Gap promotion: promote-gap-to-taskcard, select-poc-gap
- Supervisor skills: materialize-declaration-review, record-lane-execution, build-context-pack
- Validation skills: validate-product-code-ledger, validate-skill-transcript
- Governance skills: evidence-review-next-prompt, execution-handoff, plan-hardening

---

## 10. Evidence and Review Packages

### .local/evidences/ (local-only, gitignored)

| Sprint Dir (prefix) | Status |
|--------------------|--------|
| acceleration-r100 through acceleration-r109+ | Each has evidence-declaration.yaml |
| readme-refresh-plan | THIS SPRINT (being written now) |

### .local/supervisor/reviews/ (local-only, gitignored)

Review packages per sprint. Latest confirmed:
`unified-poc-authority-reconciliation-r118/declaration-review-package.zip`

### reports/supervisor/ (tracked outputs)

| File | Purpose |
|------|---------|
| session-resume.md | Start-of-session briefing |
| approval-gates.md | AUTONOMOUS_CONTINUE classification |
| next-sprint.md | Next sprint task list |
| contradictions.md | Contradiction detection results |
| work-item-grades.md | Per-item grades |
| evidence-review.md | Evidence review summary |
| materialized-evidence-review.md | Materialized evidence details |
| context-pack.md | Human-readable context pack |

---

## 11. Git State

| Metric | Value | Source |
|--------|-------|--------|
| Branch | main | git branch |
| HEAD | 3a86a05 (R93) | git log |
| Last committed sprint | R93 (2026-06-02) | git log |
| Latest sprint in tree | R118 (2026-06-05) | session-resume.md |
| Modified tracked | 85 files | git status |
| Untracked | 351 files | git status |
| Worktree | DIRTY (expected) | governance policy |

**Note:** Dirty worktree is expected — R94–R118 are local-only sprints awaiting user-authorized commit.

---

## 12. Claim Verification Summary

| README Claim | Evidence Status |
|-------------|----------------|
| "FODS .NET and FODT .NET" in Products table | CONFIRMED — but INCOMPLETE (Netpbm .NET missing) |
| "Gates 1-10 passed for FODS/FODT" | CONFIRMED |
| "Gate 11 NOT approved" | CONFIRMED |
| "commercial_product_ready: false" | CONFIRMED |
| "Six format families" | CONFIRMED EXISTS — but MISLEADING (SVG listed, Netpbm not) |
| "Phase 3/4 current" | STALE — replaced by four-stream model |
| "ZST Gates 1-4 complete (R18)" | STALE — ZST is now FOSS POC target at R118 |
| "Netpbm .NET" in products | MISSING from README — CONFIRMED from repo |
| "SYLK as FOSS target" | MISSING from README — CONFIRMED from repo |
| "PBM/PGM/PPM as FOSS target" | MISSING from README — CONFIRMED from repo |
| "Four-stream model" | MISSING from README — CONFIRMED from docs/governance/ |
| "AI authority boundary" | MISSING from README — CONFIRMED from docs/governance/ |
| "Autonomous supervisor" | MISSING from README — CONFIRMED from tools/supervisor/ |
| "Skill registry" | MISSING from README — CONFIRMED from .supervisor/ |
| "tools/supervisor/ directory" | MISSING from README structure — CONFIRMED from glob |
| ".supervisor/ directory" | MISSING from README structure — CONFIRMED from glob |
| "examples/ directory" | MISSING from README structure — CONFIRMED from glob |
