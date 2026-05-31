# Stop-Gate Log — dual-orchestration-supervisor-e2e-20260530-165603

## Emergency Stop Conditions
The following conditions require immediate halt and user notification:
1. .vscode/mcp.json appears unexpectedly
2. .taskmaster/ appears in repo root before MODE 3 authorization
3. .ruflo/ or .swarm/ appears in repo root before MODE 3
4. Ruflo daemon starts unexpectedly
5. AGENTS.md, GOVERNANCE.md, plans/master-plan.md, registry/**, tools/evidence/**, tests/evidence/** modified
6. Any R78 untracked file changes
7. Any real API key written to any file
8. MCP server registration happens accidentally
9. Evidence validation fails twice after repair attempts

## Stop Events (append as they occur)

| Time | Condition | Files Affected | Action Taken | Human Notified |
|------|-----------|----------------|--------------|----------------|
| — | No stop conditions triggered | — | — | — |
