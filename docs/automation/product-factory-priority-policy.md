# Product-Factory Priority Policy

## Principle

Evidence supports product progress but must not become the main goal. The supervisor always includes forward product-factory work in every next-worker prompt.

## POC Target Matrix

### Commercial .NET (3 targets)
| Format | Gate | Status |
|--------|------|--------|
| FODS | Gate 10 | 161 tests, installed workflow proven |
| FODT | Gate 10 | 145 tests, structural gap repaired |
| QOI/Netpbm | Gate 5 | 43 tests (.NET first slice) |

### FOSS Reduced-Scope (3 targets)
| Format | Gate | Status |
|--------|------|--------|
| ZST | Gate 10 | Local RC ready, dependency resolution needed |
| PBM/PGM/PPM | Gate 10 | PBM->PGM dogfood export proven |
| SYLK/DIF | Gate 8 | sylk_to_csv + dif_to_csv implemented |

### Dogfood Exports
| Export | Description |
|--------|-------------|
| PBM -> PGM | Uses FF write_pgm (17 tests) |
| SYLK -> CSV | Uses FF csv writer |
| DIF -> CSV | Uses FF csv writer |

## Priority Ordering

1. **Rework** (from supervisor grading) — always first
2. **System-healing** — fix broken tools/infrastructure
3. **Product-advancement** — forward work on POC targets
4. **Evidence-hardening** — improve evidence quality
5. **State-sync** — memory and state updates
6. **Verification** — final checks

## Gate 11 Policy

Gate 11 (G11-G commercial approval) requires human approval from Babar Raza. The supervisor never approves Gate 11 autonomously. Gate 11 items are tracked as BLOCKED_EXTERNAL_GATE.

## Format Expansion Policy

Do NOT add new formats until Conway R9 is proven. Current focus is finishing the 6 POC targets through their respective gates.

## Key Files

- `plans/master-plan.md` — full product roadmap
- `.supervisor/policies.yaml` — product_factory section
- `tools/evidence/contracts/r85-poc-direction-local-supervisor-autonomous-product-factory.yaml` — R85 POC contract
- `docs/format-expansion-roadmap.md` — format expansion backlog
