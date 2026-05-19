# R28 Lane G: Next Format Train
# Date: 2026-05-19

## XCF Status Review

XCF (GIMP Native Image Format) was advanced through Gates 1-3 in R27 and Gate 4 prototype in R28.

- **Gate 1:** PASS (score 78/100, Accept band)
- **Gate 2:** PASS (public spec via GIMP developer docs)
- **Gate 3:** PASS (3 valid + 1 invalid samples, Python struct generation)
- **Gate 4:** prototype_complete (17 tests pass, src/python/xcf/xcf_parser.py)
- Parses header, property list, layer offset table
- Security: 64 MiB file size guard, magic validation, dimension limits
- **Awaiting human IV per DEC-034**

## ZPAQ Status Review

ZPAQ remains blocked at Gate 3.

- **Gate 1:** PASS (score 62/100, Review band — below 7.0 threshold)
- **Gate 2:** PASS (public domain spec at mattmahoney.net)
- **Gate 3:** BLOCKED_SAMPLE_GENERATION_REQUIRES_TOOL
  - ZPAQ archives require embedded ZPAQL bytecode programs
  - Cannot construct valid samples with Python struct alone
  - zpaq CLI tool not available in current environment
  - Recovery attempted in R28: still blocked (CLI not found)
- **Resolution paths:**
  1. Install zpaq CLI (RECOMMENDED)
  2. Source pre-existing public domain test files
  3. Port minimal ZPAQL context model (NOT RECOMMENDED)
- **Gate 1 score (6.2) is in Review band** — even if unblocked, human review needed

## New Candidate Selection

Two additional candidates selected from backlog for intake planning:

### Candidate 1: AVIF (AV1 Image File Format)
- **Family:** imaging
- **Spec:** public (ISO/IEC 23000-22, based on HEIF container + AV1 codec)
- **Legal:** Category 2 (royalty-free AV1, ISOBMFF container)
- **Rationale:** Modern image format with growing browser adoption. Public spec. Royalty-free. No Aspose support. Complements QOI (simple) and XCF (layered) in imaging track.
- **Risk:** Moderate complexity (ISOBMFF container parsing + AV1 decode reference)
- **Status:** INTAKE_CANDIDATE — requires Gate 1 scoring before advancing

### Candidate 2: Markdown (.md)
- **Family:** document
- **Spec:** public (CommonMark spec, RFC 7763)
- **Legal:** Category 1 (open standard, no restrictions)
- **Rationale:** Extremely common document format. Well-defined spec (CommonMark). Low implementation complexity. High community demand. No Aspose native support for pure markdown parsing.
- **Risk:** Low complexity. Many edge cases in spec but basic parsing is straightforward.
- **Status:** INTAKE_CANDIDATE — requires Gate 1 scoring before advancing

## Lane G Summary

| Format | Gate Status | Action Taken |
|--------|------------|-------------|
| XCF | Gate 4 prototype_complete | Reviewed, verified 17 tests |
| ZPAQ | Gate 3 BLOCKED | Recovery attempted, still blocked (CLI needed) |
| AVIF | INTAKE_CANDIDATE | Selected for Gate 1 scoring |
| Markdown | INTAKE_CANDIDATE | Selected for Gate 1 scoring |
