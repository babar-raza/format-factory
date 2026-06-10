# Stream-Local Authority Model

## Principle
Each stream has its own authoritative state directory. Global `reports/supervisor/` is a
convenience snapshot (last-writer-wins) and must NOT be used as current identity for any stream.

## Stream-Local Paths

### Per-Stream Directories
```
reports/supervisor-streams/{stream}/
  latest-review.md              # stream's own evidence review
  latest-next-worker-prompt.md  # stream's own next prompt
  work-item-grades.json         # stream's own grades
  work-item-grades.yaml
  work-item-grades.md
  latest-cycle-summary.md       # stream's own cycle summary
```

### Per-Stream Continuation Signals
```
.local/supervisor/streams/{stream}/
  continuation-signal.json      # stream's own continuation state
```

### Per-Stream Context Pack (future R110+)
```
.supervisor/streams/{stream}/
  context-pack.yaml             # stream's own context pack
```

## Global State Classification
| File | Type | Usage |
|------|------|-------|
| reports/supervisor/session-resume.md | Last-writer snapshot | Convenience only |
| reports/supervisor/evidence-review.md | Last-writer snapshot | Convenience only |
| reports/supervisor/contradictions.md | Last-writer snapshot | Convenience only |
| reports/supervisor/next-sprint.md | Last-writer snapshot | Convenience only |
| .local/supervisor/continuation-signal.json | Last-writer snapshot | Convenience only |
| .supervisor/context-pack.yaml | Global aggregate | Reference only |
| .local/supervisor/selected-product-gaps.json | Mainstream-only | Not for supervisor |

## Stream Identity Resolution
1. Extract stream from sprint_id (e.g., "SUPERVISOR-R109" -> "supervisor")
2. Read from `reports/supervisor-streams/{stream}/`
3. Fall back to `reports/supervisor/` only if stream-local not available
4. Never use another stream's local directory as current authority
