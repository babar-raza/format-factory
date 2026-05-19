# Lane K: Pipeline Failure-Injection Verification

## 15 Failure Cases Tested

| # | Failure Case | Expected | Actual | Status |
|---|-------------|----------|--------|--------|
| 1 | Gateway blocked (no env) | blocked_missing_env | blocked_missing_env | PASS |
| 2 | Malformed JSON output | malformed_json_output error | malformed_json_output error | PASS |
| 3 | Missing citation | no citations error | no citations provided | PASS |
| 4 | Citation text not found in source | text_not_found error | text not found in source | PASS |
| 5 | Contradiction with verified facts | contradictions_found | contradictions_found:1 | PASS |
| 6 | Missing verified facts when required | blocked status | blocked_missing_verified_facts | PASS |
| 7 | Retrieval namespace mismatch | CrossNamespaceError | CrossNamespaceError raised | PASS |
| 8 | Stale chunk hash | is_stale=True | is_stale=True | PASS |
| 9 | Authority escalation blocked | transition rejected | transition_to returns False | PASS |
| 10 | Secret-like text in output | contains_secret=True | contains_secret=True | PASS |
| 11 | Prompt injection bypass attempt | authority stays ai_draft | authority_state=ai_draft | PASS |
| 12 | Oversized requirements (200) | generated without crash | 200 requirements generated | PASS |
| 13 | Empty requirement packet | ValueError raised | ValueError raised | PASS |
| 14 | Agentic scope violation | discarded=True | discarded=True | PASS |
| 15 | Contract validation failure | errors list non-empty | errors: task_id required | PASS |

## All 15 failure cases produce safe, expected outcomes.
## No silent failures, no data leaks, no authority escalation.

## Status: VERIFIED
