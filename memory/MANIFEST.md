---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run008
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# Memory Package Manifest

Package: `format-factory-memory-v1-20260503.zip`

Target extraction location:

```text
<repo-root>/memory/
```

Files included:

```text
memory/README.md
memory/00-index.md
memory/01-project-origin-and-intent.md
memory/02-standing-operating-rules.md
memory/03-architecture-and-product-tracks.md
memory/04-phase0-evolution-and-bundle-reviews.md
memory/05-decision-register-expanded.md
memory/06-gap-risk-and-healing-history.md
memory/07-agent-governance-model.md
memory/08-specification-cache-amendment.md
memory/09-current-state-before-phase1.md
memory/10-memory-maintenance-protocol.md
memory/11-prompting-and-agent-style-rules.md
memory/12-glossary.md
memory/AGENT_MEMORY_INTEGRATION_PROMPT.md
memory/MANIFEST.md
```

Recommended immediate use:

1. Extract the zip at repo root so it creates `/memory`.
2. Give the agent the prompt in `AGENT_MEMORY_INTEGRATION_PROMPT.md`.
3. Do not let the agent edit AGENTS.md until the plan-mode proposal is reviewed.
4. After review, request an execution handoff to amend AGENTS.md and include `/memory` in governance.
