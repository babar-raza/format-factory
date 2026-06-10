# AI-Deterministic Disagreement Policy

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## 4 Rules (Priority Order)

### Rule 1: Deterministic Failure Always Wins

**Condition:** `det valid=False` (any AI result)
**Action:** Return `NO_<deterministic reason>`
**Example:** AI says PASS, deterministic finds missing_logs → `NO_MISSING_LOGS`

### Rule 2: Deterministic Pass + AI Drift Flag

**Condition:** `det valid=True AND ai drift_flag=True`
**Action:** Return `YES_WITH_LIMITATIONS`
**Example:** Deterministic ACCEPTED, AI detects overhead drift → `YES_WITH_LIMITATIONS`

### Rule 3: AI False-Stop Detected

**Condition:** `ai false_stop=True`
**Action:** Return `ROUTE_BLOCKER`
**Example:** Prompt quality failure flagged on real product work → `ROUTE_BLOCKER`

### Rule 4: AI Overhead Flag

**Condition:** `ai overhead_flag=True`
**Action:** Return `YES_WITH_LIMITATIONS`
**Example:** machinery_overhead_score >= 2 → `YES_WITH_LIMITATIONS`

### Rule 5: Both Agree

**Condition:** All other conditions false
**Action:** Return `YES`
**Example:** Deterministic ACCEPTED, no drift, no overhead → `YES`

## Implementation

See `tools/supervisor/ai_supervisor_advisor.py::handle_ai_deterministic_disagreement()`
