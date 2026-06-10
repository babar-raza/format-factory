# External Runtime Governance Review

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Detection Summary

| Tool | Mode | Verdict |
|------|------|---------|
| Ruflo/claude-flow | DETECTED_NOT_CONFIGURED | APPROVAL_REQUIRED_FOR_INVOCATION |
| task-master-ai | DETECTED_NOT_CONFIGURED | APPROVAL_REQUIRED_FOR_INVOCATION |
| Superpowers | ABSENT | EVALUATE_ONLY |
| GhidraMCP | ABSENT | DISABLED_DEFAULT |

## Governance Posture

- Deterministic Supervisor retains full authority
- No external tool may close taskcards or approve continuation
- Ruflo output = `runtime_advisory` (not authoritative)
- No activations occurred this sprint

## Risk Register

- Auto-install risk: `npx -y` in mcp.json for both claude-flow and task-master-ai
  → Mitigated: neither was invoked
- Workspace mutation risk: claude-flow could create `.claude-flow/`
  → Mitigated: no invocation, directory absent
