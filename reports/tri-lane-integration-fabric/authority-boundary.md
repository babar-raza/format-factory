# Authority Boundary — Tri-Lane Integration
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001

## Stream Authority Hierarchy

```
FORMAT FACTORY GATES (human, final authority)
     |
     v
SUPERVISOR (routing_authority)
     |
     v
SKILLS (governed_execution_authority)
     |
     v
ACCELERATION (ai_draft — advisory only)
     |
     v
MAINSTREAM (product_implementation_authority — executes within governed boundaries)
```

## Per-Stream Authority Definitions

### Supervisor Stream
- **Authority**: routing_authority
- **Can**: Make routing decisions, set continuation states, classify cross-stream status
- **Cannot**: Approve gates, push, commit, edit product source, upgrade acceleration output
- **Key constraint**: Supervisor output is advisory to Format Factory. Gate authority is always human.

### Skills Stream
- **Authority**: governed_execution_authority
- **Can**: Define handoff templates, validate governed transcripts, produce execution contracts
- **Cannot**: Edit product source, approve gates, declare capability implemented
- **Key constraint**: Skills handoff must be consumed by Mainstream — not self-executed by Skills stream.

### Acceleration Stream
- **Authority**: ai_draft (advisory only)
- **Can**: Provide implementation pattern reference, test plan suggestions, source pattern observations
- **Cannot**: Authorize implementation, approve gates, upgrade its own outputs to authoritative, mutate poc-targets.yaml
- **Key constraint**: ALL Acceleration outputs carry authority_state: ai_draft. Requires deterministic validation (tests passing) before any evidence value.

### Mainstream Stream
- **Authority**: product_implementation_authority
- **Can**: Edit src/, write tests, declare governed transcripts, propose capability delta (not direct write)
- **Cannot**: Self-approve gates, push without human auth, override Supervisor routing, use acceleration advisory as evidence
- **Key constraint**: Mainstream is the only stream that produces product source changes.

### Format Factory Gates (Human Authority)
- **Authority**: FINAL
- **Gate 11 G11-G**: Requires Babar Raza written approval
- **Cannot be delegated to any stream**

## Prohibited Authority Crossings

| Crossing | Classification | Result |
|----------|---------------|--------|
| Acceleration declares capability implemented | AUTHORITY_MISUSE | Contract validation FAIL |
| direct poc-targets.yaml mutation request | AUTHORITY_MUTATION | Contract validation FAIL |
| SVG declared as Netpbm replacement | ROUTING_OVERRIDE | Contract validation FAIL |
| Skills packet declared authoritative without test evidence | EVIDENCE_FRAUD | Contract validation FAIL |
| Supervisor self-approves Gate 8 or Gate 11 | GATE_BYPASS | Hard stop |
