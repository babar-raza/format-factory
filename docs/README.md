# Documentation — Format Factory

Project documentation: governance standards, AI platform guides, automation contracts,
format acquisition strategy, product architecture, and publication procedures.

## Start Here

| File | Purpose |
|------|---------|
| [agent-methodology-index.md](agent-methodology-index.md) | Cross-cutting agent navigation index |
| [planning-methodology.md](planning-methodology.md) | Planning and sprint execution methodology |
| [agent-execution-handoff-standard.md](agent-execution-handoff-standard.md) | Handoff protocol between agents |
| [plan-hardening-checklist.md](plan-hardening-checklist.md) | Pre-sprint plan hardening checklist |
| [fresh-chat-continuity-brief.md](fresh-chat-continuity-brief.md) | Cross-chat continuity brief |
| [gates.md](gates.md) | Repository-wide gate authority |
| [spec-to-feature-correction-plan-summary.md](spec-to-feature-correction-plan-summary.md) | Spec-to-feature correction plan (mandatory pre-read) |

> **Document placement policy:** All new documents must go in a topical subfolder below.
> Only the 8 files listed above qualify for docs/ root placement (see [governance/](governance/) for the formal policy).

## Subdirectories

| Folder | Contents |
|--------|---------|
| [ai/](ai/) | AI platform, LLM strategy, embedding, oracle provider, RAG/retrieval policies |
| [automation/](automation/) | Supervisor pipeline, autonomous execution, state machines, bootstrap guides |
| [code-quality/](code-quality/) | Production library standards, architecture contracts, compiler specs, test layering |
| [governance/](governance/) | Compliance, legal, release control, security policy, execution standards, gate criteria |
| [python-foss/](python-foss/) | Format acquisition, spec cache, format onboarding, ODF reuse strategy |
| [product-factory/](product-factory/) | Commercial product architecture, capability model, product tracks |
| [api/](api/) | Per-format API reference documentation |
| [publication/](publication/) | Publication and release guides |
| [commercial-gate11/](commercial-gate11/) | Gate 11 commercial release procedures |
| [announcements/](announcements/) | Release announcements |
| [examples/](examples/) | Example guides and playbook examples |
| [format-family-playbooks/](format-family-playbooks/) | Family-based format guidance |
| [release/](release/) | Per-format release notes |
| [export/](export/) | Export procedures |
| [operations/](operations/) | Operational guides |
| [procedures/](procedures/) | Standard operating procedures |
| [prompt-templates/](prompt-templates/) | Reusable prompt templates |
| [prompts/](prompts/) | Prompt library |
| [taskmaster/](taskmaster/) | Taskmaster integration docs |
| [plans/](plans/) | Documentation plans (internal) |
| [history/](history/) | Archived master-plan snapshots (immutable historical records) |
| [_audit/](\_audit/) | Audit traceability documents (immutable historical records) |
| [audits/](audits/) | Audit reports |

## Compatibility Stubs (Temporary)

The following stub files remain at docs/ root while active references are migrated to their canonical paths. They will be removed once all active references point to canonical locations.

| Stub | Canonical Location |
|------|--------------------|
| [acquisition-workflow.md](acquisition-workflow.md) | [python-foss/acquisition-workflow.md](python-foss/acquisition-workflow.md) |
| [architecture.md](architecture.md) | [code-quality/architecture.md](code-quality/architecture.md) |
| [current-state-and-evidence-authority.md](current-state-and-evidence-authority.md) | [governance/current-state-and-evidence-authority.md](governance/current-state-and-evidence-authority.md) |
| [legal-and-licensing.md](legal-and-licensing.md) | [governance/legal-and-licensing.md](governance/legal-and-licensing.md) |
| [release-control.md](release-control.md) | [governance/release-control.md](governance/release-control.md) |
| [security.md](security.md) | [governance/security.md](governance/security.md) |
| [specification-cache.md](specification-cache.md) | [python-foss/specification-cache.md](python-foss/specification-cache.md) |

## Governance

- **Classification:** DOCUMENTATION
- **Producers:** developers, agents
- **Consumers:** developers, agents, publication workflow
- **Manual editing:** Yes — authored documentation
- **Registry:** `registry/repository-root-folders.yaml`
- **Placement policy:** `docs/governance/documentation-placement-policy.yaml`
