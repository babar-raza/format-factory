# Stream-Local Replay Plan

## Objective
Replay latest packages from all four streams and prove each resolves its own stream-local authority files.

## Packages to Replay
1. Supervisor: supervisor-r109 (current stream)
2. Mainstream: mainstream-r112 (latest)
3. Skills: skills-r112 (latest)
4. Acceleration: acceleration-r112 (latest)

## Verification Criteria
- Each package's stream-local dir exists under reports/supervisor-streams/{stream}/
- Each dir has at least evidence-review.json or latest-review.md
- Global reports/supervisor/ files are reference-only (last-writer-wins)
