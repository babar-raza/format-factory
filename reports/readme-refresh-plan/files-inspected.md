# Files Inspected
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

## Primary Target

| File | Lines | Status |
|------|-------|--------|
| README.md | 160 | READ — full content reviewed |

## Plans and State

| File | Status |
|------|--------|
| plans/master-plan.md | READ — confirmed §43 product-first POC direction |
| state/current-state.md | READ — confirmed stream state, POC targets, production blockers |
| reports/supervisor/session-resume.md | READ — R118 last sprint, ACCEPTED, autonomous continue |
| reports/supervisor/approval-gates.md | READ — AUTONOMOUS_CONTINUE: YES, MODE 4, Gate 11 NOT_STARTED |
| reports/supervisor/contradictions.md | READ — CLEAN, 0 critical, 0 warnings |
| reports/supervisor/work-item-grades.md | READ — 19 items ACCEPTED_WITH_LIMITATIONS |

## Product Capability Matrix and Registry

| File | Status |
|------|--------|
| product-capability-matrix/poc-targets.yaml | READ — 3 commercial .NET + 3 FOSS + 2 on-hold |
| registry/format-registry.yaml | REFERENCED (22 formats) |

## Governance Documents (docs/governance/)

| File | Status |
|------|--------|
| docs/governance/lane-definitions.md | READ via agent |
| docs/governance/acceleration-definition.md | READ via agent |
| docs/governance/autonomous-supervisor-role.md | READ via agent |
| docs/governance/mainstream-product-output-floor.md | READ via agent |
| docs/governance/machinery-success-criteria.md | READ via agent |
| docs/governance/product-first-operating-model.md | READ via agent |
| docs/governance/four-stream-operating-model.md | READ via agent |
| docs/governance/ai-authority-boundary.md | READ via agent |
| docs/governance/external-tool-architecture.md | READ via agent |
| docs/governance/ruflo-runtime-governance.md | READ via agent |
| docs/governance/superpowers-skill-intake.md | READ via agent |
| docs/governance/ghidra-mcp-compliance-gate.md | READ via agent |
| docs/governance/mainstream-poc-mega-train.md | READ via agent |

## Prompt Templates (docs/prompt-templates/)

| File | Status |
|------|--------|
| docs/prompt-templates/README.md | READ via agent |
| docs/prompt-templates/lane-planning-template.md | READ via agent |
| docs/prompt-templates/mainstream-product-execution-template.md | READ via agent |
| docs/prompt-templates/acceleration-ai-product-execution-template.md | READ via agent |
| docs/prompt-templates/skills-governed-execution-template.md | READ via agent |
| docs/prompt-templates/supervisor-autonomous-continuation-template.md | READ via agent |
| docs/prompt-templates/evidence-review-template.md | LISTED |
| docs/prompt-templates/final-adversarial-iv-template.md | LISTED |
| docs/prompt-templates/stream-state-reconciliation-template.md | LISTED |
| docs/prompt-templates/next-sprint-generation-template.md | LISTED |
| docs/prompt-templates/cross-stream-dependency-template.md | LISTED |
| docs/prompt-templates/mainstream-poc-mega-train-template.md | LISTED |
| docs/prompt-templates/repair-order-reference.md | LISTED |
| docs/prompt-templates/format-factory-stream-prompt-requirements.md | LISTED |
| docs/prompt-templates/external-tool-aware-repair-template.md | LISTED |

## Configuration and Registry

| File | Status |
|------|--------|
| .supervisor/skill-registry.yaml | READ — 25 skills, 24 active |
| .supervisor/context-pack.yaml | READ — generated 2026-06-03, project state snapshot |
| .supervisor/policies.yaml | REFERENCED |
| .supervisor/project-memory.md | REFERENCED |
| .supervisor/prompts/mega-train-template.md | READ (first 80 lines) |
| AGENTS.md | READ via agent |
| CLAUDE.md | REFERENCED |

## Source Directories (confirmed from glob)

| Path | Confirmed |
|------|-----------|
| src/net/fods/ | YES — FodsDocument.cs, FodsParser.cs, FodsWriter.cs, Model/ |
| src/net/fodt/ | YES — FodtDocument.cs, FodtParser.cs, FodtWriter.cs, Model/ |
| src/net/netpbm/ | YES — NetpbmImage.cs, NetpbmParser.cs, NetpbmWriter.cs |
| src/net/csv/ | YES — FormatFactory.Csv.csproj, CsvWriter.cs |
| src/net/html/ | YES — FormatFactory.Html.csproj, HtmlWriter.cs |
| src/net/txt/ | YES — FormatFactory.Txt.csproj, TxtWriter.cs |
| src/net/markdown/ | YES — FormatFactory.Markdown.csproj, MarkdownWriter.cs |
| src/python/ | YES — _readme.md present; 18+ format subdirs |

## Example Directories (confirmed from glob)

| Path | Confirmed |
|------|-----------|
| examples/net/fods/ | YES — ExportCsvExample.cs, CopySheetExample.cs, ClearSheetExample.cs, RowManipulationExample.cs |
| examples/net/fodt/ | YES — DocumentStatsExample.cs, HtmlExportExample.cs, TextRangeExample.cs |
| examples/net/netpbm/ | YES — LoadEditSaveExample.cs, PixelEditSaveExample.cs, FlipOverlayExample.cs, MergeBrightnessExample.cs, MergeContrastExample.cs |
| examples/dotnet/fods/ | YES — export_sheet_to_csv.csx |
| examples/dotnet/fodt/ | YES — export_to_plain_text.csx |
| examples/dotnet/netpbm/ | YES — equalize_and_convert.csx |
| examples/python/fods/ | YES |
| examples/python/fodt/ | YES |
| examples/python/pbm/ | YES |
| examples/python/ppm/ | YES |
| examples/python/sylk/ | YES |
| examples/python/zst/ | YES |
| examples/python/abw/ | YES |
| examples/python/fodp/ | YES |
| examples/python/fodg/ | YES |
| examples/python/gnumeric/ | YES |

## Evidence Directories

| Path | Status |
|------|--------|
| .local/evidences/ | LISTED — 10+ sprint directories |
| .local/supervisor/reviews/ | REFERENCED — review packages per sprint |
| reports/supervisor/ | READ — multiple output files |

## Tools

| Path | Status |
|------|--------|
| tools/supervisor/ | LISTED — 39 Python scripts |
| .claude/commands/ | LISTED — 30 command files |
