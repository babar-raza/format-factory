# ABW Gate 2 Legal Notes
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 2 — Spec Retrieval

## Legal Classification

| Field | Value |
|-------|-------|
| Legal category | 2 |
| Application license | GPL-2.0 (AbiWord application) |
| Format license | None (open XML format, no parsing restriction) |
| DTD license | Public (AWML 1.0) |
| Legal gap | Minor — same as Gnumeric |

## GPL License Analysis

The AbiWord application is licensed under GPL-2.0. Key considerations:
1. **Format parsing**: Implementing an ABW parser is NOT affected by AbiWord's GPL license
   - GPL applies to application source code, not to the file format
   - The AWML XML format is openly published
2. **DTD reference**: The public identifier and DTD URL are in every ABW document,
   indicating intent to make the format publicly accessible
3. **AbiWord source reference**: Using AbiWord source code for reference understanding
   requires GPL compliance only if distributing modified source — not for format parsing

## Legal Gap Assessment

| Gap | Classification | Mitigation |
|-----|----------------|-----------|
| GPL application license | Minor | Format parsing not affected |
| Outdated AWML DTD | Minor | Source code + secondary docs sufficient |
| abisource.com unreachable | Minor | DTD not needed for format parsing |
| No formal spec body | Minor | AWML 1.0 public identifier is sufficient reference |

**Legal Gap Classification: MINOR** — same as Gnumeric. No blockers.

## Commercial Differentiation

Aspose.Words does NOT support ABW format. This is a positive for commercial differentiation:
- No Aspose competition for this format
- Our implementation would be unique commercial value
- Both Python FOSS and .NET commercial tracks viable

## Gate 2 Legal Conclusion

Legal category: **2 — Permissive OSS format, minor legal gaps**.
No blockers for acquisition progression. Consistent with Gnumeric legal assessment.
Risk classification: MEDIUM (per Gate 1) — due to outdated DTD, but legal risk is LOW.

GATE_2_LEGAL_NOTES: PASSED_WITH_NOTES (Category 2, minor gaps, no blockers)
