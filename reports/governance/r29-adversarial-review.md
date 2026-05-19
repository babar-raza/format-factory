# R29 Adversarial Review
# Sprint: FORMAT-FACTORY-R29-MEGA-TRAIN-STATE-CONSISTENCY-AI-FORMAT-COMMERCIAL-PUBLICATION-EVIDENCE-001
# Date: 2026-05-19

## 25 Pointed Questions

### R28 Repair
1. **Q:** Was the R28 sprint-state actually wrong? **A:** YES. `status: in_progress` with all lanes `pending` contradicted the R28 final verdict (R28_COMPLETE) and sprint overview (all lanes DONE). This is a closure defect — sprint-state was initialized but never updated.

2. **Q:** Could you have just deleted the sprint-state instead of fixing it? **A:** NO. Deleting would hide evidence. The repair with `repair_note` documents what happened.

3. **Q:** Does the repair change the R28 evidence bundle? **A:** NO. The R28 bundle at `.local/evidence-bundles/r28-full-throttle-train-20260519.zip` is untouched. The fix is forward — R29 bundle includes the corrected file.

### Evidence Validator
4. **Q:** Could a future sprint bypass the new tests? **A:** Not easily. Tests run in `tests/evidence/` which is part of the mandatory validation suite.

5. **Q:** Do the tests have false positives for multi-sprint directories? **A:** NO. Tests match by `sprint_id` in both sprint-state.yaml and verdict files. A new in_progress sprint sharing a directory with an old completed sprint won't false-positive.

6. **Q:** Do the tests handle missing YAML parser? **A:** YES. Tests use PyYAML (installed). If PyYAML is missing, `_load_yaml` returns empty dict and tests skip that file.

### AI Platform
7. **Q:** Are any AI modules calling live endpoints? **A:** NO. GPT_OSS_ENDPOINT is not set. All AI tests use fixture mode. 0 live API calls.

8. **Q:** Could the citation verifier be bypassed? **A:** Only by providing fake `source_texts`. Repo-based verification checks actual file existence.

9. **Q:** Does the evaluator allow authority escalation? **A:** NO. `evaluate_synthesis()` never changes `authority_state`. It only produces pass/fail.

10. **Q:** Could the requirements generator produce authoritative requirements? **A:** NO. Generation always sets `authority_state = "ai_draft"`. Even if input dict contains `authority_state: "authoritative"`, the generator ignores it and hardcodes `ai_draft`.

11. **Q:** Are retrieval namespace boundaries enforced? **A:** YES. `CrossNamespaceError` raised for cross-format queries. Test confirms.

12. **Q:** Is telemetry leaking secrets? **A:** NO. Spool validation is tested. No env var values appear in spool records.

### Format Gates
13. **Q:** Did the prior R29 overclaim gate states? **A:** NO. Prior R29 advanced 6 formats from Gate 3-5 to Gate 7, all backed by passing tests (77 ODS/ODT/QOI + 25 XCF + 39 DIF + 40 PPM = 181 new tests).

14. **Q:** Are ODS/ODT/QOI at Gate 7 really? **A:** YES. Oracle tests (deterministic) and fuzz tests (malformed input) both pass. Pack.yaml entries are precise.

15. **Q:** Is XCF overclaimed? **A:** NO. XCF header+property+layer parsing works (Gate 4). Neutral model (Gate 5) identifies supported/unsupported features. Oracle and fuzz tests pass (Gates 6-7). No pixel decode — consistent with prototype scope.

16. **Q:** Is ZPAQ still honestly blocked? **A:** YES. `gate_3_blocked_sample_generation_requires_tool`. No fake samples created. Blocker documented with three resolution options.

### Commercial
17. **Q:** Did any .NET code change? **A:** NO. .NET FODS 157/157, FODT 145/145 unchanged from prior R28/R29 work.

18. **Q:** Is commercial_product_ready still false? **A:** YES. All formats.

19. **Q:** Is G11-G still NOT_STARTED? **A:** YES. Unchanged.

20. **Q:** Were any Gate 11 sub-gates self-approved? **A:** NO. No gate approval in this sprint.

### Publication
21. **Q:** Was anything published? **A:** NO. No push, no PR, no package upload.

22. **Q:** Are publication packets stale? **A:** NO. 68/68 packaging tests pass. 5 packages at Gate 10 verified.

### Governance
23. **Q:** Was the mega-train rule saved? **A:** YES. In Claude project memory (MEMORY.md + mega-train-operating-rule.md).

24. **Q:** Can repo agents find the rule? **A:** Via the mega-train rule reference in MEMORY.md. Repo-level memory/50 will document it.

25. **Q:** Are all sprint artifacts consistent? **A:** YES. R29 sprint-state tracks all lanes. Test counts match. No stale PENDING markers. No stale COMMIT_SHA. Evidence bundle will include all artifacts.

## Adversarial Verdict: NO DEFECTS FOUND
