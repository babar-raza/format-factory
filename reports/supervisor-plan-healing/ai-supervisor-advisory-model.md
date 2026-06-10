# AI Supervisor Advisory Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Model Overview

AI advisory provides non-authoritative analysis alongside deterministic validation.
Deterministic results always take precedence.

## Advisory Output Format

All AI advisory outputs MUST have:
```json
{
  "authority_state": "ai_draft",
  "non_authoritative": true,
  "requires_deterministic_validation": true,
  "advisory_mode": "deterministic_advisory"
}
```

## Advisory Modes

| Mode | Description |
|------|-------------|
| `deterministic_advisory` | No live AI gateway — rule-based analysis |
| `fixture_ai` | Pre-built fixture responses |
| `live_ai` | Live AI gateway (requires explicit declaration) |

## Disagreement Resolution

When AI advisory and deterministic validation disagree:
1. `det valid=False + any AI` → return `NO_<deterministic reason>`
2. `det valid=True + ai drift_flag=True` → return `YES_WITH_LIMITATIONS`
3. `ai false_stop=True` → return `ROUTE_BLOCKER`
4. `ai overhead_flag=True` → return `YES_WITH_LIMITATIONS`
5. `both agree` → return `YES`

Deterministic failure always overrides AI pass. AI drift can downgrade YES to YES_WITH_LIMITATIONS.
