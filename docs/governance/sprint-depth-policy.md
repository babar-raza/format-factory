# Sprint Depth Policy

**Created:** R33 (2026-05-19)
**Status:** ACTIVE

---

## Purpose

This policy replaces the prior breadth-first sprint approach with depth-first sprints. It addresses the root cause identified in R32: sprint incentives rewarded gate count over source quality, leading to 8 toy/shallow parsers at overclaimed gates.

## Rules

### 1. Depth Over Breadth

Each sprint must deepen existing formats before advancing new ones. Deepening means adding write/export capability, enriching neutral models, expanding test suites, or fixing bugs. Moving a format from G3 to G4 with a 170-line probe does NOT count as progress.

### 2. Maximum New Candidates Per Sprint

No more than 2 new format candidates may be introduced per sprint. New candidates stop at G3 (acquisition-only) until a focused deepening sprint advances them.

### 3. Minimum Deepening Per Sprint

Each sprint must include at least one measurable deepening deliverable:
- New write/export capability for an existing format
- Neutral model enrichment (5+ new modeled features)
- Test suite expansion (20+ new tests for a single format)
- Bug fix that improves correctness (verified by new tests)

### 4. Lane Count Limits

Mega-train sprints are capped at 12 lanes. If more work exists, prioritize the deepest lanes and defer the rest. "17-lane mega-train with 6 shallow gate advances" is prohibited.

### 5. Gate Advancement Requires Evidence

No format may advance through gates G5+ unless:
- The completion matrix entry is current
- The DRIFT taskcard (if any) has been reviewed
- The evidence-backed gate matches or is higher than the target gate
- The gate criteria in docs/governance/gate-quality-criteria.md are satisfied

### 6. Probe-Only Formats Are Capped

Formats classified as `probe_only` in the completion matrix may NOT advance past their evidence-backed gate without deepening. Packaging a probe as a release candidate is prohibited.

### 7. Reports Are Not Progress

Sprint reports describe work done. They do not substitute for source code, tests, or evidence. A sprint that produces only reports and no source/test changes is classified as a governance sprint, not a progress sprint.

## Enforcement

- Evidence validators in tests/evidence/ check matrix consistency
- Gate quality criteria in docs/governance/gate-quality-criteria.md define minimum requirements
- Completion matrix in registry/format-completion-matrix.yaml is the authority
- DRIFT taskcards track overclaim review outcomes
