# R99 Continuation Policy Review

## Current Policy State (verified from policies.yaml)
- max_iterations: 12 (raised from 5 in R98)
- checkpoint_every: 3
- max_dirty_files_before_checkpoint: 75
- max_src_files_changed_before_checkpoint: 12
- max_consecutive_accept_with_limitations: 2
- max_consecutive_no_product_gap_closure: 2
- hard_prohibitions: git_push, package_publication, gate_8_approval, gate_11_approval, mcp_activation_beyond_mode_3, destructive_git_operations
- continuation_signal_modes: true, true_with_rework, false
- critical_grades: OVERCLAIMED, REJECTED
- non_critical_grades: REWORK_REQUIRED, ACCEPTED_WITH_WARNINGS

## R99 Changes
1. Continuation state machine: 8 states (up from 6)
2. NO_POLICY_BLOCK: New state for force_stop
3. classify_continuation_state(): Extracted into dedicated function
4. Context pack rebuilt as part of cycle (ensures fresh state for next prompt)
5. Legacy markdown regenerated (ensures session-resume matches cycle summary)

## What Is NOT Changed
- max_iterations remains 12 (R98 value is appropriate)
- Checkpoint enforcement deferred (requires git status counting per iteration)
- NO_NO_PROGRESS state is reserved but not enforced (requires cross-sprint history)
