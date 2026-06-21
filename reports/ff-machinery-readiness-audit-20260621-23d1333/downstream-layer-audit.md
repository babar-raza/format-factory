# Downstream Product-Generation Layers Audit
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Layers Audited

### Feature Planning Layer

**Status: AI-DRIVEN, NOT DETERMINISTIC**

Tool: `tools/supervisor/ai_implementation_designer.py`
- Uses an AI model to generate feature plans from gap descriptions
- NOT a deterministic compiler from capability map
- Plans generated are advisory, not spec-grounded

Gap: No spec→capability→feature→code deterministic pipeline exists.

### Code Generation Layer

**Status: SKILL-BASED, PARTIALLY GOVERNED**

Skills (add-dotnet-api, add-python-api, etc.) generate code through:
1. Skill invocation with exact_source_paths declared
2. Human/agent produces code following skill template
3. Product code ledger entry required
4. Governance validator runs at sprint closeout

**What this DOES ensure:**
- No ad-hoc source edits without declared scope
- Product code ledger tracks every change
- Governance validators check for monolith violations (GOV_BLOCK)
- TC-GUARD-001 (BLOCK mode) requires gap_ledger_ref or spec_fact_refs

**What this DOES NOT ensure:**
- QName compliance in generated class names
- Spec-hierarchy folder structure
- Canonical namespace usage
- Backfill migration safety

### Source Quality Enforcement

| Validator | Active | Severity | Notes |
|-----------|--------|----------|-------|
| monolith_detection_validator | YES | Blocks | LOC cap per file |
| validate_source_architecture | YES | Blocks | Architecture violations |
| validate_deepening_suspension (V42) | YES | Rejects | Arithmetic rotation items |
| TC-GUARD-001 (gap_ledger_ref required) | YES | Block mode | Requires spec_fact_refs |
| TC-GUARD-002 (PURPOSEFUL check) | YES | Warn | Checks item purposefulness |
| validate_qname_compliance | NOT BUILT | — | Missing critical validator |

### Test Layer

Test layer baseline (`registry/test-layer-manifest.yaml`) exists.
46,000+ test files documented.

**Problems identified:**
- 31 ImportError failures in FODS Python test suite (collection failure, not test failure)
- Arithmetic deepening tests (697 files per MEMORY.md) are classified as arithmetic-only, non-spec-backed
- `--skip-arithmetic` flag exists to skip 697 files at runtime

### Export / Conversion Layer

**Status: WORKING for FODS/FODT**

FODS: CSV, HTML, JSON, ODS, PDF, PNG, Markdown exporters exist and pass tests
FODT: HTML, Markdown, PDF, PNG, TXT exporters exist and pass tests

Cross-format conversion via Format Factory libraries: PARTIALLY PROVEN (dogfood evidence exists)
The dogfood proof is: FODS→CSV→load CSV via .NET CSV library (chain established).

### Gate Logic

Gate readiness is assessed per format in poc-targets.yaml.
Gate 11 stop behavior: described in CLAUDE.md, enforced by TRUE_EXTERNAL_GATE classification.
No automated gate signal when a product becomes G11-submission-ready.

### Where Malformed Code is Introduced

Root causes of current non-qname code:

1. **Skills were written before QName schema was finalized** — skills produce code that follows
   format-prefixed conventions because the canonical class library doesn't exist yet.

2. **No QName validator at sprint closeout** — agents add code that passes governance validators
   (no GOV_BLOCK) but uses format-prefixed names because qname is not enforced.

3. **Template/AI-based code generation** — ai_implementation_designer.py generates code without
   QName awareness; generated code mimics existing style (format-prefixed).

4. **Spec-free analytics rotation** — before suspension, hundreds of `{format}_mod_{N}_times_{M}`
   functions were generated with no spec backing. These are in the codebase but tests are deleted.
