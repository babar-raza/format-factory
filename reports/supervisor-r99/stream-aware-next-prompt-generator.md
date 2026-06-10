# Train K: Stream-Aware Next Prompt Generator

## Problem (D99-PROMPT-01)
`generate_next_worker_prompt.py` produced a single mega-train prompt containing all groups. Supervisor-only sprints received product trains (G3-G5) they could not execute. Product sprints received supervisor infrastructure trains they did not need.

## Fix (R99)
Added `stream` parameter to `generate_prompt()`:

```python
def generate_prompt(review, next_work=None, repo_root=None, stream=None):
    # stream: None/"product" | "acceleration" | "skills" | "supervisor"
```

### Stream Definitions
| Stream | Groups Included | Purpose |
|--------|----------------|---------|
| `product` (default) | G1-G8 (all) | Full mega-train for mainstream sprints |
| `acceleration` | G1, G2, G7, G8 | Acceleration layer work (governance + rework + state + evidence) |
| `skills` | G1, G2, G7, G8 | Governed skill development (same scope as acceleration) |
| `supervisor` | G1, G2, G7, G8 | Supervisor infrastructure only |

### Each Stream Gets
1. Own prompt (filtered by allowed groups)
2. Own evidence root (same `.local/evidences/<run_id>/` pattern)
3. Own reconciliation (via normal declaration → grade cycle)
4. Own next prompt (via stream parameter on next call)
5. Own scope boundaries (groups act as the filter)

## Usage
```python
# From autonomous_cycle.py or direct call:
prompt = generate_prompt(review, repo_root=repo_root, stream="supervisor")
```

The combined prompt (stream=None) remains the default for backward compatibility.
