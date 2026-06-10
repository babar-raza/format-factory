# Stale Claim Report
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-GOVERNANCE-SYNC-20260604-001

## Stale Claims Found in Local Docs

| Stale Claim | Found In | Current Position | Action |
|---|---|---|---|
| Mainstream should run immediately after R113 | master plan §43.7 (implied) | Mainstream DEFERRED until all 3 hardening proofs | Section 44.4 resolves. §43.7 preserved as historical |
| Evidence cleanup as main sprint goal | some prior sprint prompts | Evidence repair justified only when blocking | docs/governance/evidence-handling-principles.md resolves |
| Old supervisor_loop.py / run-on-latest closeout style | some prompt templates | autonomous_cycle.py --declaration is mandatory | Section 44.7 resolves |
| Hardcoded taskcard/output counts as authority | Spec Authority plan (ticklish-dancing-lobster) | Declared-vs-materialized validation instead | Noted as plan repair requirement |
| ai_draft treated as accepted proof | — | ai_draft cannot satisfy proof per ai-authority-boundary.md | Already resolved in prior sync sprint |
| SVG as potential Netpbm replacement | — | Netpbm must be retained; SVG is NOT a replacement | Preserved in master plan §44.6 |
| Direct poc-targets.yaml mutation | — | Proposed delta only via PocTargetsSyncProposalGenerator | docs/governance/requirement-capability-authority-layer.md resolves |

## No Evidence of Active Use of Stale Claims

No current sprint prompt templates actively use the old supervisor_loop style. The stale references are in historical sprint IDs only, not in templates that would be sent.

## Claims Confirmed Current (not stale)

- Four-stream model: current (docs/governance/four-stream-operating-model.md)
- AI authority boundary: current (docs/governance/ai-authority-boundary.md)
- External tool posture: current (docs/governance/external-tool-architecture.md)
- Product-first operating model: current (docs/governance/product-first-operating-model.md)
- Supervisor/Skills bundle SHAs: current (memory/67 and stream state files)
