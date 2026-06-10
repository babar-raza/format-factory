# Skill-or-Handoff Router v2 — Train D

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## What Changed

### 1. Skill registry integration
- `choose_skill_or_handoff()` accepts optional `skill_registry` parameter
- `_match_skill_registry()` dynamically matches gap text to registered skills
- Matches require 3+ word overlap with skill purpose text

### 2. New decisions
- `NEED_PLAN_HARDENING`: returned when gap matches a skill rule AND contains high-risk patterns (new file, create new, restructure, migrate, refactor)
- `READ_ONLY_VERIFY`: returned when gap text contains read-only patterns (verify, check, inspect) and no skill rule matches

### 3. Decision priority order
1. EXTERNAL_GATE_ESCALATION (external gates)
2. Hardcoded SKILL_RULES with PLAN_HARDENING check
3. Dynamic skill registry matching
4. READ_ONLY_VERIFY
5. GOVERNED_HANDOFF_REQUIRED (fallback)

### 4. CLI enhancement
- `--skill-registry` flag for providing registry path
- Auto-loads default registry if available

## Test Results

- 10 new tests in `test_choose_skill_or_handoff_v2.py`
- All pass (external gate, dogfood, plan hardening, read-only, registry match, backward compat)
