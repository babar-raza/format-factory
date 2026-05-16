# FODP Gate 3 Sample Sources
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 3 — Sample Corpus

## Corpus Strategy

Samples are project-owned synthetic files generated directly from the ODF 1.3 spec.
No external downloads required. Same approach as FODS/FODT Gate 3.

## Samples Created

| Filename | Sample ID | Category | Description |
|----------|-----------|----------|-------------|
| minimal-presentation.fodp | fodp-minimal-01 | minimal | Single slide, title "Hello" |
| two-slides-basic.fodp | fodp-two-slides-01 | basic | Two slides (Introduction + Conclusion) |
| title-only.fodp | fodp-title-only-01 | edge-case | Empty presentation body (no slides) |

All samples:
- License: Apache-2.0 (project-owned)
- Provenance: synthetic, deterministic
- Spec basis: ODF 1.3 Part 3 (OASIS)
- Location: samples/by-format/fodp/

## External Source Candidates (for future corpus expansion)

If more diverse samples are needed in future sprints:
1. LibreOffice Impress — can generate FODP via "Save As > Flat ODF Presentation"
   (LibreOffice 7.x+ confirmed available at C:/Program Files/LibreOffice/)
2. OASIS ODF test suite — conformance test samples (if available under open license)
3. LibreOffice test corpus — demo/example .odp files converted to flat XML

For Gate 3 purposes, 3 synthetic samples are sufficient to validate corpus parsing.

GATE_3_SAMPLE_SOURCES: COMPLETE (3 synthetic project-owned samples)
