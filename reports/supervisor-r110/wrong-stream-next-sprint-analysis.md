# Wrong-Stream Next-Sprint Analysis

## Source Tracing
| Field | Value |
|-------|-------|
| path_read | reports/supervisor/next-sprint.md |
| source_kind | workspace (global last-writer-wins) |
| detected_stream | acceleration |
| target_stream | supervisor |
| authority | ARCHIVED_LAST_WRITER_SNAPSHOT |
| is_blocking | false |

## Root Cause
The global `reports/supervisor/next-sprint.md` is written by whichever stream's autonomous-cycle
runs last. Currently it was written by `FORMAT-FACTORY-ACCELERATION-R112-*`, so it contains
acceleration-stream content. This is expected behavior under the stream-local authority model.

## Classification
- **Type:** ARCHIVED_LAST_WRITER_SNAPSHOT
- **Impact:** Non-blocking (low severity)
- **Reason:** Global next-sprint.md is explicitly documented as convenience snapshot only.
  The authoritative next-sprint prompt for supervisor is at:
  `reports/supervisor-streams/supervisor/latest-next-worker-prompt.md`

## Resolution
- Wrong current authority → would block (but this is NOT current authority)
- Archived/reference wrong-stream output → YES_WITH_LIMITATIONS (this case)
- Recommendation: Continue using stream-local authority files. Global is reference only.
