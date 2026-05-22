# R51 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Policy Summary

If a lane is blocked by approval, SDK, credentials, or external dependency:
1. Record the blocker
2. Create/update a taskcard
3. Prepare remediation packet
4. Continue to next safe local task
5. Do NOT stop the sprint

---

## R51 Blockers and Work-Ahead Actions

| Blocker | Lane | Action Taken |
|---------|------|--------------|
| TC-0054 formula preservation implementation — large scope | Lane 3B | AI design draft obtained; implementation deferred to R52; no taskcard change needed |
| FODT TXT export — requires non-trivial blocks iteration | Lane 7B | Noted as R52 target; existing blocks structure is ready |
| Phase Audit 4 for ZST/ODS/ODT — requires prior format work | Lane 6B | Roadmap documented; targets set for R52 |
| Gate 11 G11-G — requires Babar Raza approval | All | Consistently `commercial_product_ready: false`; no gate work attempted |
| PDF acquisition — large scope | Lane 7C | Not started; R52 target |

---

## Completed Work-Ahead Items

| Original Task | Work Done While Blocked |
|---------------|------------------------|
| FODT TXT export (blocked on scope) | Verified FODT blocks model is ready; documented approach for R52 |
| TC-0054 implementation (blocked on size) | AI design draft obtained (548 tokens); formula schema + parser + writer approach documented |
| Phase Audit 4 ZST (blocked on format state) | FODS/FODT depth audit completed; next targets planned |
