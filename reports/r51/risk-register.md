# R51 Risk Register

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Active Risks

| ID | Risk | Impact | Probability | Mitigation | Status |
|----|------|--------|-------------|-----------|--------|
| RISK-001 | Gate 11 G11-G not started — commercial release blocked | HIGH | LOW | commercial_product_ready: false enforced; validator checks | OPEN |
| RISK-002 | Formula cells lose formula on FODS write | HIGH | CERTAIN | TC-0054 open; AI design draft available | OPEN_ESCALATED |
| RISK-003 | Inline/table/list lost on FODT write | HIGH | CERTAIN | TC-0057, TC-0058, TC-0059 open; .NET recommended for complex docs | OPEN |
| RISK-004 | Generated requirements not created for ZST/ODS/ODT | MEDIUM | HIGH | PA3 CONDITIONAL_PASS; Phase Audit 4 targets ODS/ODT next | OPEN |
| RISK-007 | Bundle built before proof file is finalized | HIGH | MEDIUM | R51 validator extended — PLACEHOLDER/will-be-replaced now caught | CLOSED_IN_R51 |
| RISK-008 | Validator endpoint URL has /v1 prefix — double-path 404 | LOW | CERTAIN | Use `endpoint + /chat/completions` (not `/v1/chat/completions`) | CLOSED_IN_R51 |

---

## R51 Risk Delta

### CLOSED in R51

| ID | Risk | Resolution |
|----|------|-----------|
| RISK-007 | Bundle proof placeholder missed by validator | Extended PROOF_FILE_PLACEHOLDER_PATTERNS with 7 new patterns; 16 tests |
| RISK-008 | AI endpoint URL double /v1 path | Documented correct URL pattern in llm-provider-summary.md |

### CARRIED FORWARD

| ID | Risk | Next Action |
|----|------|------------|
| RISK-001 | Gate 11 G11-G | No change — awaits Babar Raza approval |
| RISK-002 | Formula preservation | TC-0054 active; implement in R52 using AI design draft |
| RISK-003 | FODT preservation | TC-0057 to TC-0059 active; implement in R52 |
| RISK-004 | ZST/ODS/ODT requirements | Phase Audit 4 targets ODS/ODT in R52 |

### New Risks in R51

None.
