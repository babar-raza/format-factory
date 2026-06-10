# Hard Quota Plan — R101

## Quota 1: 7+ tools improved/validated, 4+ with pos/neg tests, 3+ sample outputs
Plan: Improve all 8 tools, add pos/neg tests to select_poc_gaps, choose_skill_or_handoff,
generate_execution_handoff, detect_product_progress. Generate sample outputs from gap selector,
handoff generator, lane recorder.

## Quota 2: Fresh gaps for all 4 streams, no stale R98
Plan: Run select_poc_gaps.py with --stream-output-dir. Verify sprint_id matches R101.

## Quota 3: 2+ execution handoffs generated
Plan: Generate handoffs from selected gaps. If all match skills, create synthetic gaps.

## Quota 4: 1+ end-to-end dry run
Plan: selected gap -> router -> handoff -> lane ledger -> evidence snippet.

## Quota 5: Sprint learning outputs generated
Plan: Create sample ledger, run generate_sprint_learning.py.

## Quota 6: evidence-manifest.yaml present
Plan: Write at closeout before review package.

## Quota 7: Raw logs present
Plan: Capture pytest output to reports/acceleration-r101/raw-test-log.txt.
