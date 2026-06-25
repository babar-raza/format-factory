# Product Quality Review — Methodology

## Review Standard

This review judges Format Factory products as if they may be used by real
developers. We apply the same standard a senior library engineer would apply
when evaluating a third-party library for adoption or release.

## Evidence Hierarchy (most to least authoritative)

1. **Source code** — the primary truth. What a class actually does, not what it claims.
2. **Public API surface** — class names, method signatures, return types, overloads, exceptions visible to callers.
3. **Tests** — what tests actually verify vs. what they claim to verify.
4. **Examples** — whether examples are realistic, runnable, and show real workflows.
5. **Sample files** — whether real format files exist and can be loaded.
6. **Package/project files** — whether build/packaging is complete and correct.
7. **Generated outputs** — physical files produced by export/save operations.
8. **Sprint summaries, evidence bundles, capability matrices** — informational only; not used as proof of quality.

## What a "Real Professional Library" Looks Like

### .NET Commercial Library
- Stable namespace (FormatFactory.{Format})
- Primary Document class with Load/Save + domain-specific methods
- Typed model objects (Sheet, Row, Cell; Paragraph, Heading; Image)
- Separate parser/reader and writer/serializer
- Export classes for each target format (HtmlExporter, CsvExporter, etc.)
- Custom exception hierarchy with useful messages
- Nullable-safe properties and methods
- File path + Stream overloads for Load/Save
- XML security posture (DTD prohibition, XmlResolver null)
- README at project root with usage examples

### Python FOSS Library
- Importable as `from formatname import ...` after `pip install`
- Explicit `__all__` controlling what's exported
- Type hints on all public functions (Python 3.9+)
- parse/load function + dataclass or model class as return type
- write/save function (for writable formats)
- Custom exception class (not bare Exception)
- pyproject.toml with name, version, description, license, authors, urls, keywords, classifiers, readme
- README.md at package root
- Examples using `from formatname import ...` (not `from src.python.formatname import ...`)
- At least one CLI entry point for interactive use

## Scoring Scales

### All quality dimensions: 0–5
```
0 = absent (feature/quality dimension missing entirely)
1 = weak/demo (exists but unusable for real work)
2 = basic (minimal happy path, no edge cases)
3 = acceptable POC (works for basic workflows, limited edge case handling)
4 = strong (handles variants, errors, roundtrip; suitable for production use)
5 = professional/commercial (full-featured, documented, tested, polished)
```

### Feature Availability (FA): FA-0 to FA-5
```
FA-0: not available
FA-1: internal only or unproven
FA-2: public API exists, weak or no tests
FA-3: implemented and tested (basic case)
FA-4: implemented with edge/error/roundtrip tests
FA-5: professional with docs/examples/output proof
```

### Feature Complexity (C): C0 to C5
```
C0: no implementation
C1: trivial wrapper or hardcoded behavior
C2: simple happy-path implementation
C3: structured implementation with real parsing/model behavior
C4: handles variants, errors, roundtrip, and practical cases
C5: advanced, extensible, robust commercial-grade implementation
```

### Test Quality (TQ): TQ-0 to TQ-5
```
TQ-0: no tests
TQ-1: smoke only (import + basic instantiation)
TQ-2: happy path only (no edge cases, errors, or malformed input)
TQ-3: useful behavior tests (CRUD operations, format-specific behavior)
TQ-4: behavior + edge + error + output tests (roundtrip, malformed input)
TQ-5: strong product-confidence suite (comprehensive, feature-organized)
```

## Anti-Patterns to Flag

- God class: all logic in one class with 50+ methods
- Dual API confusion: two incompatible ways to do the same thing without guidance
- Dead abstraction: base class that nothing inherits from
- Architecture marker: class with `# GENERATED` and `pass` body
- Sprint-named tests: `R87ProductDeepening` rather than `SetCellValueTests`
- Dev-path examples: `from src.python.fods import ...` in examples/ (not from installed package)
- Missing README: csproj or pyproject.toml references README.md that doesn't exist
- Claim contradiction: one file says "Gate 11 approved", another says "in_progress"
- Write-only product: parser exists, writer missing (ZST .NET)
- Read-only product without disclosure: no write API, no user-facing documentation of this

## Review Process

For each product:
1. Enumerate all public classes and methods from source
2. Classify each feature with FA and C scores
3. Inspect tests for TQ score
4. Check examples for realism and installability
5. Check packaging completeness
6. Flag all problems with severity and confidence
7. Assign overall commercial/FOSS readiness score
8. List required fixes with priority

## Claim Verification Process

For each claim found in capability matrices, sprint reports, or package metadata:
1. Find the source-level implementation
2. Find the test covering it
3. Find the example demonstrating it
4. Assign: CLAIM_PROVEN / CLAIM_PARTIALLY_PROVEN / CLAIM_UNPROVEN / CLAIM_OVERSTATED / CLAIM_CONTRADICTED
