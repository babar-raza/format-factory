# 18 — Target Production Architecture

**Baseline commit:** dd909cf3a
**Objective:** Define the target production system that supports the continuous improvement loop

## Design Principles

1. **State-derived, not signal-derived:** Mission state is computed from committed files, never from local ephemeral signals
2. **Fail-closed by default:** Missing evidence, stale hashes, or unresolved contradictions block advancement
3. **Certification is derived, not declared:** No manually-writable string has certification authority
4. **One authority per concern:** Every question "who decides X" has exactly one answer backed by code
5. **Bootstrappable from clean clone:** `git clone` + one command reconstructs the complete mission state
6. **Idempotent re-execution:** Same committed state produces same next-action, evidence verdict, and certification

## Target Loop

```
CURRENT PRODUCT TRUTH (committed state)
    → FIND HIGHEST-VALUE GAP (unified scheduler)
    → CREATE EXECUTABLE TASK (task contract)
    → CLAIM ATOMICALLY (lease)
    → IMPLEMENT PRODUCT DELTA (governed skill)
    → EXECUTE CURRENT PROOF (test + oracle + reconciliation)
    → ACCEPT OR REJECT (transactional)
    → UPDATE AUTHORITATIVE STATE (committed)
    → INVALIDATE AFFECTED DERIVATIONS (hash-triggered)
    → SELECT NEXT GAP (scheduler re-evaluation)
```

## Authority Map (Target)

| Concern | Single Authority | Location | Readers |
|---------|-----------------|----------|---------|
| Active mission | FF6 product-goal.yaml (repaired) | plans/strategic/ff6/product-goal.yaml | Goal driver, scheduler |
| Format definitions | Product-goal.yaml format entries | Same | All format tools |
| Obligation baseline | Per-format obligation registers | plans/strategic/ff6/obligations/*.yaml | Reconciler, scheduler |
| Current evidence | Hash-bound evidence store (repaired) | shared/format-contracts/implementation-evidence/*.yaml | Reconciler, certification |
| Evidence freshness | Source/test/corpus file hashes in evidence | Same evidence files | Reconciler (auto-invalidation) |
| Certification | Derived certification function (new) | tools/ff6/certify.py | Goal driver, scheduler, CI |
| Task selection | Unified scheduler (new) | tools/ff6/scheduler.py | Official command |
| Task claims | Lease-based coordination | Coordination DB | Scheduler, workers |
| Continuation | Goal driver resume (state-derived) | tools/ff6/goal_driver.py | Official command |
| Terminal condition | 6/6 derived certification | Goal driver | Official command |
| Transition history | Append-only event journal | plans/strategic/ff6/events.jsonl | Audit (not authority) |

## One Official Command

```
python -m tools.ff6.run
```

Behavior:
1. **Bootstrap:** Validate environment (Python version, venv, packages). Install missing deps.
2. **Reconstruct:** Read committed product-goal.yaml, obligation registers, evidence stores, contracts, test results. Compute current state from files, not from .local/ signals.
3. **Certify:** Run derived certification for each format. Fail-closed: missing evidence = NOT CERTIFIED. Stale hash = INVALIDATED. Failed test = NOT CERTIFIED.
4. **Schedule:** Select highest-value gap across all formats using unified breadth/depth scheduler.
5. **Claim:** Atomic lease on selected task. Conflict = retry with different task.
6. **Emit:** Executable task contract with expected delta, test selectors, acceptance criteria.
7. **Execute:** Invoke governed skill for product change.
8. **Verify:** Run cited test selectors. Run oracle if available. Run reconciliation. Check governance validators.
9. **Accept/Reject:** Transactional. All tests pass + reconciliation matches + no governance blocks = ACCEPT. Otherwise REJECT with typed failure.
10. **Update:** Commit accepted evidence with source/test/corpus hashes. Recompute certification. Append event.
11. **Next:** Return to step 4.

Exit conditions:
- `exit 0`: GOAL_ACHIEVED (6/6 certified by proof)
- `exit 1`: BLOCKED_EXTERNAL (true external gate with classification)
- `exit 2`: NO_PROGRESS (circuit breaker — N consecutive cycles with no accepted delta)
- `exit 3`: PRODUCT_REGRESSION (accepted evidence invalidated during cycle)

## Derived Certification Model

```python
def is_certified(format_id: str) -> tuple[bool, list[str]]:
    """Compute certification from current evidence. Fail-closed."""
    failures = []
    
    # 1. All obligations resolved
    obligations = load_obligations(format_id)
    evidence = load_evidence(format_id)
    for obl in obligations:
        ev = evidence.get(obl.id)
        if not ev:
            failures.append(f"Missing evidence for {obl.id}")
            continue
        # 2. Evidence hashes match current files
        for hash_entry in ev.source_hashes:
            current = sha256(read(hash_entry.path))
            if current != hash_entry.digest:
                failures.append(f"Stale evidence for {obl.id}: {hash_entry.path} changed")
        # 3. Cited tests currently pass
        for selector in ev.test_selectors:
            if not test_currently_passes(selector):
                failures.append(f"Test fails for {obl.id}: {selector}")
    
    # 4. Package installable
    if not package_installable(format_id):
        failures.append(f"Package not installable")
    
    # 5. No unresolved governance blocks
    gov_blocks = check_governance(format_id)
    if gov_blocks:
        failures.extend(gov_blocks)
    
    # 6. Namespace consistent
    goal = load_product_goal(format_id)
    if not namespace_matches_package(goal):
        failures.append(f"Namespace mismatch")
    
    return (len(failures) == 0, failures)
```

Key properties:
- **Fail-closed:** Missing evidence = NOT CERTIFIED (never assumed present)
- **Hash-bound:** Source changes invalidate evidence automatically
- **Test-current:** Cited test selectors must currently pass, not historically
- **Package-verified:** Installed package must import correctly
- **Governance-clear:** No blocking governance failures allowed
- **Regressive:** Certification automatically regresses when any input changes

## Evidence Freshness Model

Each accepted evidence record stores:
```yaml
evidence_id: IPYNB-EXEC-001
obligation_id: SAL-IPYNB-OBL-63250AAB7522792F
accepted_at: 2026-08-31T12:00:00Z
source_hashes:
  - path: src/python/ipynb/src/format_factory/ipynb/execution.py
    digest: sha256:abc123...
test_hashes:
  - path: tests/python/ipynb/test_execution.py
    digest: sha256:def456...
corpus_hashes:
  - path: tests/python/ipynb/corpus/sample.ipynb
    digest: sha256:789abc...
test_selectors:
  - tests/python/ipynb/test_execution.py::test_timeout_preserves_partial_output
execution_result: PASS
execution_timestamp: 2026-08-31T12:00:00Z
```

Invalidation triggers:
- Source file hash changes → evidence invalidated
- Test file hash changes → evidence invalidated
- Corpus file hash changes → evidence invalidated
- Obligation definition changes → evidence invalidated
- Contract changes → evidence invalidated

Invalidation is **automatic and immediate** — not dependent on a scheduled reconciliation run.

## Unified Breadth/Depth Scheduler

Priority ordering (highest first):
1. **Invalidated evidence** — previously accepted, now stale (regression)
2. **Unresolved normative obligations** — contractual requirements
3. **Confirmed product defects** — known failures
4. **Missing user-facing capabilities** — breadth gaps
5. **Shallow implementation depth** — depth gaps
6. **Weak corpus coverage** — testing gaps
7. **Weak oracle/interoperability** — external validation gaps
8. **Packaging/downstream** — distribution gaps

Within each priority level, round-robin across formats to prevent starvation.

Anti-starvation rule: No format goes more than 3 consecutive cycles without selection.

## Failure Semantics

Replace "best effort and continue" with typed outcomes:

| Outcome | Blocks advancement? | Retry? | Example |
|---------|-------------------|--------|---------|
| RETRYABLE_FAILURE | No (retry immediately) | Yes | Transient network, file lock |
| INVALID_INPUT | Yes (fix input) | After fix | Malformed evidence declaration |
| STALE_STATE | Yes (refresh) | After refresh | Evidence hash mismatch |
| EVIDENCE_FAILURE | Yes (investigate) | After fix | Test fails, reconciliation disagrees |
| PRODUCT_REGRESSION | Yes (block) | After fix | Previously passing test now fails |
| INFRASTRUCTURE_FAILURE | No (skip) | Yes | Validator tool import error |
| TRUE_EXTERNAL_BLOCKER | Yes (report) | No | Credentials, business approval |
| OPERATOR_INTERVENTION | Yes (report) | No | Ambiguous situation requiring human judgment |

Only INFRASTRUCTURE_FAILURE allows proceeding without resolution. All others block until classified and addressed.

## State Machine

```
DISCOVERED: obligation identified in contract
SPECIFIED: obligation has test selectors and acceptance criteria
READY: all prerequisites met, can be claimed
CLAIMED: leased to a specific worker/session
IMPLEMENTED: code change exists
CURRENTLY_VERIFIED: tests pass, hashes match, reconciliation agrees NOW
ACCEPTED: evidence committed with current hashes
CERTIFIED: all obligations for format are ACCEPTED (derived, not declared)

INVALIDATED: previously accepted, hash changed
RETRYABLE_FAILURE: implementation attempted, recoverable failure
BLOCKED_INTERNAL: depends on other unresolved work
BLOCKED_EXTERNAL: requires credentials, business approval, etc.
SUPERSEDED: replaced by newer obligation
ABANDONED: explicitly removed from scope
```

State transitions are transactional: no partial advancement.

## Recovery

Clean clone reconstruction:
1. `git clone` → all committed files available
2. `python -m tools.ff6.run --status` → reads product-goal.yaml, obligations, evidence, computes certification
3. No .local/ state required for correctness
4. .local/ used ONLY for: caching compiled artifacts, session-specific leases, performance optimization
5. Deleting .local/ is safe — next run rebuilds caches

## Observability

Structured log entries for:
- Task selection (format, gap type, priority, alternatives considered)
- State reads (what was read, hash, freshness)
- Evidence produced (obligation, selectors, results)
- Evidence rejected (obligation, failure reason, typed outcome)
- Product delta (what changed, measurable improvement)
- State transitions (from → to, evidence, timestamp)
- Certification computation (per-format, pass/fail with reasons)
- Invalidation events (what changed, what was invalidated)
