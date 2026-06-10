# Automation Adoption Map

## Tool -> Adoption Status

| Tool | R101 Status | R102 Status | Adopted? |
|------|------------|------------|----------|
| select_poc_gaps.py | v4 | v4 + consumed by next_best_action | Yes |
| choose_skill_or_handoff.py | v4 | v4 + consumed by dry runs | Yes |
| generate_execution_handoff.py | v2 | v2 + generates 4 stream handoffs | Yes |
| record_lane_execution.py | v3 | v3 + used in all 4 dry runs | Yes |
| generate_sprint_learning.py | v3 | v3 (unchanged) | Partial |
| package_install_proof.py | v3 | v3 (unchanged) | Partial |
| detect_product_progress.py | v3 | v3 + consumed by forecaster | Yes |
| materialize_and_review.py | v2 | v2 (unchanged) | Partial |
| next_best_action.py | NEW | v1 + sample outputs | Yes |
| stream_forecaster.py | NEW | v1 + sample outputs | Yes |
| anti_skip_checker.py | NEW | v1 + sample outputs + detects 4 violation types | Yes |
| stream_prompt_generator.py | NEW | v1 + generates 4 stream prompts | Yes |

## Pipeline Flow
```
poc-targets.yaml
  -> select_poc_gaps.py (gaps)
  -> next_best_action.py (ranked actions per stream)
  -> stream_forecaster.py (3-sprint plan per stream)
  -> choose_skill_or_handoff.py (route each gap)
  -> generate_execution_handoff.py (handoff per gap)
  -> stream_prompt_generator.py (stream-specific next prompt)
  -> anti_skip_checker.py (validate before close)
```
