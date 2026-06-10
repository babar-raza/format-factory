# Final Single-Go Execution Prompt (Repaired)

**Sprint ID:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-REPLAN-AND-EXECUTION-001
**Repair Version:** v4 (External Tool Intelligence Intake added)
**authority_state:** ai_draft

---

## Mission

Establish AI as the non-authoritative cognitive operating layer of Format Factory. This sprint:

1. Creates 8 AI cognitive tools (ai_product_brain, ai_sprint_manager, ai_implementation_designer,
   ai_evidence_critic, ai_learning_loop, source_pattern_miner, test_plan_generator,
   mainstream_acceleration_packet)
2. Runs 4 Mainstream consumption packets (FODS/FODT/Netpbm/SYLK)
3. Models 3 external tools (Ruflo, Superpowers, GhidraMCP) with governance gates
4. Verifies no external tool was installed or activated

---

## Hard Prohibitions

- NEVER modify `src/net/` or `src/python/`
- NEVER modify `product-capability-matrix/poc-targets.yaml`
- NEVER modify `.supervisor/skill-registry.yaml` or `plans/master-plan.md`
- NEVER use direct openai/anthropic/gemini imports — only `gateway_chat()` via approved gateway
- NEVER store API keys in code or files
- NEVER treat fixture output as equivalent to live AI output in evidence
- NEVER install Ruflo, Superpowers plugins, or GhidraMCP
- NEVER analyze any binary without Supervisor approval + all 9 GhidraMCP gate conditions met
- NEVER claim external tool is installed when it is not

---

## Staged Gates

| Gate | Description | Key Outputs |
|------|-------------|-------------|
| Gate 0 | Environment verification + poc checksum | gate-0-env.txt, ai-authority-validation.json |
| Gate 1 | Tool creation (8 tools) | All 8 .py files in tools/supervisor/ |
| Gate 2 | Test suite (58+ tests passing) | gate-2-*.txt test logs |
| Gate 3 | AI Product Brain | 4 JSON files in ai-product-brain/ |
| Gate 4 | Pre-sprint management pass | pre-sprint-plan.json (status=skipped if no agentic_low_risk) |
| Gate 5 | Source patterns + designs + test plans | patterns/designs/test-plans per format |
| Gate 5.5 | External tool intelligence intake | 9 repair docs + 6 product-first ext-tool files |
| Gate 6 | Mid-sprint management pass | mid-sprint-reroute.json |
| Gate 7 | Four Mainstream consumption packets + TC-EXT-007 | 4 packet JSONs + ext-tool-authority-validation.json |
| Gate 8 | Evidence critic + learning loop | evidence-critique.json + sprint-learnings.jsonl |
| Gate 9 | Final authority validation | All invariants VERIFIED |
| Gate 10 | Healing documents (11 files) | reports/acceleration-plan-healing/*.md |
| Gate 11 | Evidence declaration + review package | ZIP + SHA-256 |

---

## Gateway Decision Table

| Case | Condition | Action |
|------|-----------|--------|
| LIVE | cfg.is_configured == True | Use gateway_chat(); log to ai-usage-ledger.jsonl |
| FIXTURE-OK | Not configured; role NOT in NO_FALLBACK_ROLES | Fixture template; label mode: fixture, live_ai_used: false |
| SKIP | Not configured; role in NO_FALLBACK_ROLES | Write status: skipped; do not fabricate output |
| PARTIAL | Configured but blocked_no_model returned | Treat as FIXTURE-OK; log status: blocked_no_model |

NO_FALLBACK_ROLES = {agentic_low_risk, security_analysis}

---

## External Tool Summary

| Tool | Mode | Owner | This Sprint Action |
|------|------|-------|-------------------|
| Ruflo | absent | Supervisor/Mainstream | Gate doc + risk register only |
| Superpowers | audit_only | Skills | Recommendations JSON only |
| GhidraMCP | disabled_pending_supervisor_approval | Acceleration (gate) | Gate doc only |

**All 3: not installed, not activated, not used for evidence.**

---

## Final Response Contract

Report exact verdict from:
- ACCELERATION_PRODUCT_FIRST_AI_LAYER_PASS
- ACCELERATION_PRODUCT_FIRST_AI_LAYER_WITH_LIMITATIONS
- ACCELERATION_PRODUCT_FIRST_AI_LAYER_BLOCKED_EXTERNAL_GATE
- ACCELERATION_PRODUCT_FIRST_AI_LAYER_FAILED_NEEDS_REWORK

Plus: EXTERNAL TOOL INTAKE VERDICT from:
- EXTERNAL_TOOL_MODELED
- PARTIAL
- NOT_MODELED

And: REPAIR VERDICT from:
- ACCELERATION_PLAN_REPAIRED_EXTERNAL_TOOL_READY
- ACCELERATION_PLAN_REPAIRED_WITH_LIMITATIONS
- ACCELERATION_PLAN_STILL_REQUIRES_REWORK

---

*authority_state: ai_draft | non_authoritative: true | This is the repaired v4 execution prompt.*
