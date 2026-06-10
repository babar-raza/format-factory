# Package Contamination Root Cause — R105

## Problem
Acceleration R104 review package primary files reference Mainstream R106 and Skills R103.

## Root Cause
build_declaration_review_package.py lines 103-166 (pre-R105) copied global supervisor state files from reports/supervisor/ and .supervisor/ directly into primary ZIP paths (supervisor/, state/). These global files are shared across all 4 streams and reflect whichever stream ran autonomous-cycle most recently.

In R104's case:
- Mainstream R106 ran last -> latest-cycle-summary.md, evidence-review.md, contradictions.md all point to Mainstream R106
- Skills R103 ran before that -> context-pack.yaml points to Skills R103
- selected-product-gaps.json was from mainstream gap selection, not acceleration

## Fix
1. Stream-scoped packaging: supervisor/ now pulls from the run_id's own review directory first
2. Global state relabeled: global-state/ prefix makes cross-stream nature explicit
3. Package identity validator: automated check prevents packaging contamination from going undetected
4. Dirty state classification: declarations must classify dirty state to pass anti-skip checks
