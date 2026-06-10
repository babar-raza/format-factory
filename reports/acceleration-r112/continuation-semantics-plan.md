# Continuation Semantics Plan — R112

## States
| State | Meaning |
|-------|---------|
| YES | All accepted, anti-skip clean |
| YES_WITH_LIMITATIONS | Accepted but low/medium non-blocking caveats |
| YES_WITH_REWORK | Rework items exist but safe lanes continue |
| NO_MAX_ITERATIONS | Iteration limit reached |
| NO_EXTERNAL_GATE | Blocked by gate approval / credentials / push |
| NO_BROKEN_BASELINE | Critical rework blocks continuation |
| NO_UNSAFE_SOURCE_STATE | Overclaimed items present |
| NO_PROMPT_QUALITY_FAILURE | Prompt quality validation failed |
| NO_WRONG_STREAM_CURRENT_AUTHORITY | Wrong-stream artifact treated as authority |
| NO_MISSING_REQUIRED_SAMPLE_OUTPUTS | Required sample outputs missing |
| NO_MISSING_EVIDENCE_MANIFEST | Evidence manifest missing or invalid |

## Rules
- Clean anti-skip + prompt quality -> YES
- Low/medium non-blocking caveats -> YES_WITH_LIMITATIONS
- Current-authority wrong stream -> NO_WRONG_STREAM_CURRENT_AUTHORITY
- Missing required evidence -> NO_MISSING_REQUIRED_SAMPLE_OUTPUTS

## Implementation
classify_continuation_state in autonomous_cycle.py checks anti_skip_result.
When all_pass=false but impact has no blocking/downgrading violations, returns YES_WITH_LIMITATIONS.
