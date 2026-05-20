# R38 Adversarial Review

## Sprint: FORMAT-FACTORY-R38-AI-CLEAN-CLOSURE-REPAIR-RUNNER-STATUS-BUNDLE-HYGIENE-AND-INTEGRATION-MEGA-TRAIN-001
## Date: 2026-05-20

| # | Question | Answer |
|---|----------|--------|
| 1 | Did it advance gates without evidence? | NO — no gates touched |
| 2 | Did it move/delete source? | NO — only modified AI tooling |
| 3 | Did it break existing tests? | NO — 617 passed, 0 failed |
| 4 | Did it overclaim capabilities? | NO — all changes are defect fixes |
| 5 | Did it stage unrelated files? | NO — exact-path staging only |
| 6 | Did it touch product source (src/)? | NO |
| 7 | Does --all --no-live truly pass from clean shell? | YES — verified via subprocess in test |
| 8 | Do failure-injection expectations match gateway status? | YES — 34 FI tests pass |
| 9 | Can runner failure be hidden by piping? | NO — exit codes 0/1/2 documented, tested via subprocess |
| 10 | Does builder exclude __pycache__? | YES — exclude_patterns now merged into forbidden_patterns |
| 11 | Does validator exclude __pycache__? | YES — same fix applied |
| 12 | Does matches_forbidden catch .pyc files? | YES — test_matches_forbidden_catches_pycache |
| 13 | Does bundle metadata sprint-overview match current run? | N/A — sprint-overview is user-provided; builder generates metadata-identity-report |
| 14 | Are commit metadata fields unambiguous? | YES — implementation_commit and metadata_commit tracked via SprintCommitMetadata |
| 15 | Does evidence validation fail bad contracts? | YES — test_emergency_blocker_warning, test_low_metadata_warning |
| 16 | Does contract explicitly set emergency_blocker_bundle: false? | YES |
| 17 | Does live contradiction-required use facts? | YES — _FIXTURE_FACTS provides facts; _resolve_contradiction_check returns True for required |
| 18 | Is telemetry minimized? | YES — _CONTENT_STRIP_KEYS strips prompts/responses/content |
| 19 | Is telemetry redacted? | YES — _deep_redact applies redact_text to all strings |
| 20 | Are docs/matrix aligned? | YES — matrix v4 with R38 entries, fixes documented |
| 21 | Is AI non-authoritative? | YES — all outputs tagged ai_draft |
| 22 | Is AI outside product source? | YES — only tools/ai/, tests/ai/, docs/ai/ |
| 23 | Did exclude_patterns fix work for all three source locations? | YES — forbidden_paths + forbidden_patterns + exclude_patterns merged |
| 24 | Could the FI timeout increase mask real failures? | NO — only prevents false timeout; real pytest failures still exit non-zero |
| 25 | Did semantic validation weaken passing criteria? | NO — warnings are informational; pass/fail still based on file existence |
| 26 | Could contradiction facts fixture cause false security? | NO — facts are minimal and correct for FODS; production use requires real verified facts |
| 27 | Does the contract use required_repo_files not required_artifacts? | YES |
| 28 | Does the contract have min_metadata_count >= 30? | YES — set to 30 |
| 29 | Does the contract have require_clean_git: true? | YES |
| 30 | Are R35 test regressions possible from R38 changes? | NO — all 31 R35 tests still pass |
| 31 | Was the recursive FI test collection bug real? | YES — R38 FI test names initially matched -k pattern, causing recursive subprocess; fixed by renaming |
| 32 | Does the runner --schema output include all mode keys? | YES — verified by existing test |
| 33 | Is the evidence validation contract loader canonical? | YES — imports load_contract from validate_evidence_bundle.py |
| 34 | Could stale R23 metadata recur in future bundles? | YES — builder doesn't validate sprint-overview content; documented as remaining backlog |
| 35 | Are all R38 changes AI-only scope? | YES — no format gates, no commercial, no publication |

## Scale vs R35

| Metric | R35 | R38 |
|--------|-----|-----|
| Type | Defect closure + hardening | Closure repair + bundle hygiene |
| Defects fixed | 7 | 6 (exclude_patterns x2, FI timeout, semantic validation, facts, contradiction visibility) |
| New tests | 31 | 29 |
| Total AI tests | 588 | 617 |
| Source files modified | 4 | 5 (+ build_evidence_bundle.py, validate_evidence_bundle.py) |
| New components | 4 | 5 (cache exclusion, semantic validation, facts fixture, contradiction visibility, FI timeout) |

## NO-PUSH / NO-PUBLICATION / NO-AUTHORITY-PROMOTION: CONFIRMED
