# Non-Blocking Evidence Caveats

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001

## Caveats That Do NOT Block This Sprint

| Item | Caveat | Workaround |
|------|--------|-----------|
| agentic_low_risk: status=skipped | No agentic_low_risk model configured. Correct per spec. | Sprint management documented as advisory-skipped. |
| Source patterns: corpus may be sparse | Some formats have limited src/ files. Lexical scores may be low. | corpus_empty flag set. Patterns still present for major formats. |
| Implementation designer: ai_pattern_summary may be gateway fixture | summarization role is fixture-OK. If live AI unavailable, fixture used. | labeled mode: fixture in output. |
| Healing docs: no schema validation | 11 healing docs are markdown; no JSON schema. | Advisory only; not consumed by automated pipeline. |
| Plan repair docs: guidance only | 9 plan repair docs are advisory. | Not consumed by Supervisor pipeline. |
| External tool recommendations: advisory only | Superpowers/Ruflo/GhidraMCP recommendations are ai_draft. | Skills stream must normalize before any use. |

## Items That Remain Advisory After This Sprint

- Mainstream packet ai_rationale: still advisory even when AI-generated (ai_draft authority)
- Implementation design .md files: advisory for Mainstream worker
- Test plan JSON: advisory (must be verified by running actual tests)
- Sprint management passes: status=skipped (correct) — advisory management structure exists
