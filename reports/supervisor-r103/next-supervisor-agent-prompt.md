# Next Supervisor Agent Prompt

## Context
R103 fixed cross-stream contamination (tests_supporting, manifest, package self-containment)
and added 2 new continuation states. 32 new tests, 614 total passing.

## Remaining Gaps
1. Raw test/build log capture during autonomous-cycle
2. Per-stream state directory isolation (prevent cross-stream overwrite)
3. Stale selected-product-gaps.json (still R98)
4. Grade explanation field (why ACCEPTED_VERIFIED)

## Next Sprint Directive
Focus: Raw logs + per-stream state isolation
Stream: supervisor
Priority: Raw logs > state isolation > stale gaps
