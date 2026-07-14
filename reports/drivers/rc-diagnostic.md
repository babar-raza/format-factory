# Root Cause Diagnostic — DRIVERS-PRODUCTION-INTEGRATION-001
Date: 2026-07-13T00:00:00Z
HEAD Commit: 3fdaf841 feat(portfolio): complete MCP-W1-007 and MCP-W2-002 portfolio execution

## RC-1: Skill command bypasses driver system

Evidence: .claude/commands/add-python-api.md (v1.5) Step 7 text:
"7. Add focused tests for normal behavior, one boundary case, and one invalid-input case when applicable."

Confirmed: Zero FeatureFactory / generate_and_write_scaffold / product_feature_factory references in skill command.
V_VALIDATE_WEAK_TEST_ASSERTIONS absent from skill command validator table.

## RC-2: V19 detection gap (partial — see note)

Evidence: V19 (`validate_no_stub_tests`) was extended at TC-ZS-006 (2026-06-22) to detect
`assert result is not None` at >80% file-level threshold. V19 DOES flag files where >80% of
assertions are weak. However, V19 only fires during evidence declaration review — it does NOT
fire on agent-written tests that are never declared. The structural gap remains: agents write
tests without invoking the driver/scaffold pipeline.

Sample weak test: tests/python/abw/test_abw_gap_closure_batch.py — contains `assert result is not None`
without FIXTURE_REQUIRED or SCAFFOLD_STATUS markers.

Total weak tests identified: 51 (discovered by glob fallback — generated-test-portfolio-audit.yaml
contains invalid YAML at line 13).

## RC-3: FeatureFactory returns strings only

Evidence: write_promotion_task callers (outside test files): ZERO
  grep -rn "write_promotion_task" tools/ src/ .claude/ --include="*.py" → only
  tools/supervisor/drivers_promotion.py:187 (the definition itself)

FeatureFactory external calls: ZERO (no instantiation outside product_feature_factory.py CLI block)
generate_and_write_scaffold present: NO — function entirely absent from all Python files

## RC-4: Prior mission false completion

Evidence: .local/evidences/drivers-subsystem-healing-001/ → does NOT exist
Prior mission (DRIVERS-SUBSYSTEM-HEALING-001) wrote terminal-closeout.yaml to a different path
or was never written. The 79 test suite passes proved machinery quality, not production wiring.

---

## Summary

| RC | Finding | Confirmed |
|---|---|---|
| RC-1 | Skill command .claude/commands/add-python-api.md v1.5 has no FeatureFactory invocation | YES |
| RC-2 | V19 partially detects weak assertions at file level; function-level gap remains | PARTIAL |
| RC-3 | write_promotion_task has zero production callers; generate_and_write_scaffold absent | YES |
| RC-4 | .local/evidences/drivers-subsystem-healing-001/ absent; prior mission did not wire production | YES |

Evidence token: RC_DIAGNOSTIC_WRITTEN
