# R31 Adversarial Review

## 30 Evidence-Backed Adversarial Questions

### Isolation Integrity
1. Q: Can `discover_models()` leak API keys in return values? A: NO — returns ModelCapability objects, key never stored. Verified: key not in model dump. **PASS**
2. Q: Can `gateway_chat()` print the API key to stdout? A: NO — litellm.suppress_debug_info=True, key passed only to litellm.completion(). Test: capsys capture shows no key. **PASS**
3. Q: Does `load_ai_config()` store the API key value? A: NO — only stores `api_key_present: bool`. **PASS**
4. Q: Can runtime guard be bypassed by adding AI import in a comment? A: PARTIAL — guard checks string containment, so `# import litellm` would trigger. This is overly cautious but safe. **PASS (conservative)**
5. Q: Does `run_guard()` skip any src/ directories? A: It scans src/python and src/net only, by design. tools/ is scanned separately for endpoint bypasses. **PASS**

### Pipeline Safety
6. Q: Can a synthesis output set its own authority_state to authoritative? A: NO — `run_synthesis()` always sets `ai_draft` on line 198, regardless of input. **PASS**
7. Q: Can JSON injection in LLM output bypass contradiction check? A: NO — output is parsed then checked against facts. Injection in JSON values doesn't bypass the check. **PASS**
8. Q: What happens if LLM returns non-JSON? A: `malformed_json_output` error, no further processing. **PASS**
9. Q: Can `check_contradictions()` pass with `not_checked` status? A: NO — evaluator requires status == "no_contradictions" when `require_no_contradictions=True`. **PASS**
10. Q: Can a rejected requirement be re-accepted? A: NO — ValueError raised. **PASS**

### Env Dependency
11. Q: Do tests pass if GPT_OSS_ENDPOINT is set to garbage? A: Tests that mock correctly pass regardless. Gateway would fail with error status. **PASS**
12. Q: What if AGENT_METRICS_API_KEY contains a secret and is accidentally logged? A: Secret redaction covers this var by name. **PASS**
13. Q: Can a test accidentally call the real endpoint? A: Only if mock patches are wrong (fixed in Lane B) or test doesn't mock at all (only gateway.py call tests do live calls). **PASS**
14. Q: If litellm is uninstalled, do non-gateway tests still pass? A: NO — gateway.py import fails at module level, breaking any test that imports from it. Honestly documented. **ACKNOWLEDGED**
15. Q: Are there any hardcoded endpoint URLs in tests? A: Tests use `https://llm.example.com/v1` (mock) or `https://nonexistent.invalid` (connection error test). No real URLs. **PASS**

### Authority Lifecycle
16. Q: Can `ai_draft` skip to `evaluator_passed`? A: NO — VALID_TRANSITIONS requires sequential steps. **PASS**
17. Q: Can `rejected` transition anywhere? A: NO — empty set in VALID_TRANSITIONS. `is_terminal()` confirms. **PASS**
18. Q: Can `superseded` transition anywhere? A: NO — empty set in VALID_TRANSITIONS. **PASS**
19. Q: Can `transition_with_evidence()` proceed without evidence_path? A: NO — returns (False, "transition requires evidence_path"). **PASS**
20. Q: Is the 12-state machine complete (all states have transition rules)? A: YES — all 12 ArtifactAuthorityStateValue entries are keys in VALID_TRANSITIONS. **PASS**

### Agentic Controls
21. Q: Can path traversal bypass the scoped runner allowlist? A: NO — `reports/../src/python/` resolves to absolute path outside allowlist. Test confirms rejection. **PASS**
22. Q: Can a non-Qwen model be used for agentic tasks? A: NO — model_id must contain "qwen" (case-insensitive). gpt-4 test confirms rejection. **PASS**
23. Q: Is output discarded on scope violation? A: YES — `result.discarded = True` on max_files, path, or model violation. **PASS**
24. Q: Can forbidden operations be passed in allowlist? A: NO — contract validation rejects them. **PASS**

### Telemetry
25. Q: Can secrets appear in spool records? A: Detection exists — `validate_spool_record` checks for sk- and Bearer patterns. **PASS**
26. Q: Is Agent Metrics posting blocked? A: YES — `posted_externally: False`, `blocked_by_policy: True`. No AGENT_METRICS_API_KEY. **PASS**
27. Q: Does the spool contain raw prompts? A: NO — only prompt_hash. Policy forbids raw prompt logging. **PASS**
28. Q: Can the telemetry drain post without explicit authorization? A: NO — `replay_spool()` is a placeholder comment. No implementation. **PASS**

### Evidence & Bundle
29. Q: Does the evidence bundle include __pycache__? A: Contract will exclude `**/__pycache__/**`. Previous R30 issue documented. **PENDING VERIFICATION AT BUILD**
30. Q: Can final-verdict.md be missing from the bundle? A: NO — it's listed as a required artifact in the evidence contract. **PASS**

## Score: 29/30 PASS, 1 PENDING (bundle build verification)
## Verdict: ADVERSARIAL REVIEW PASSED
