# External Tool Workspace Mutation Policy

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Paths Each Tool Can Mutate If Invoked

| Tool | Potential Mutation Paths |
|------|--------------------------|
| Ruflo/claude-flow | `.claude-flow/`, `CLAUDE.md` (via hooks), any file passed to tasks |
| task-master-ai | `.task-master/`, `CLAUDE.md` (via hooks), task state files |
| Superpowers | `.claude-plugin/`, `CLAUDE.md` (SessionStart injection) |
| GhidraMCP | `tools/`, `src/` (if analysis results saved) |

## Mutation Detection Approach

1. Capture `git status` and `git diff --name-only` before and after each potential activation
2. Check for new directories: `.claude-flow/`, `.claude-plugin/`, `.task-master/`
3. Verify `CLAUDE.md` unchanged (hash check)
4. Verify mcp.json unchanged (hash check)

## Current Sprint

No external tool mutations detected. Verdict: **NO_MUTATIONS_DETECTED**
