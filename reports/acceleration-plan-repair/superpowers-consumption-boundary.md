# Superpowers Marketplace Consumption Boundary

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04
**authority_state:** ai_draft

---

## What Superpowers Marketplace Is

Superpowers Marketplace (https://github.com/obra/superpowers-marketplace) is a community
registry of AI agent skills, plugins, and workflows. Skills define actions that AI agents
can invoke, packaged with metadata and invocation contracts.

Skills can automate tasks like:
- Test case generation
- Code pattern extraction
- Workflow tracing
- Format analysis

---

## Stream Ownership

**Owner:** Skills stream

Superpowers Marketplace skills belong primarily to the Skills stream.

**Acceleration's role:** Recommend which Superpowers workflows could improve AI planning,
testing, debugging, or execution handoffs — then hand off to Skills stream for evaluation.

**Acceleration may NOT:**
- Install plugins or import skills directly
- Write to `.supervisor/skill-registry.yaml`
- Execute plugin code without Skills normalization
- Add Superpowers commands to `.claude/commands/`

---

## Skills Normalization Path

Every Superpowers skill recommended by Acceleration must go through this pipeline
before it may be used in Format Factory:

```
Superpowers Marketplace Skill
         ↓
Acceleration Recommendation (advisory, authority_state: ai_draft)
         ↓
Skills Stream Review
         ↓
Local Wrapper Created
         ↓
allowed_files defined (what files the skill may read/write)
         ↓
forbidden_files defined (what files the skill may never touch)
         ↓
validation_command defined and tested
         ↓
evidence_rule defined
         ↓
skill-registry.yaml entry added by Skills stream
         ↓
Skill available for authorized use
```

---

## Acceleration Rules

1. **Catalog read only:** Acceleration may browse the Superpowers catalog to identify relevant skills.
2. **Recommendations only:** All Acceleration output about Superpowers is `authority_state: ai_draft`.
3. **No installation:** Acceleration never installs Superpowers plugins.
4. **No registry writes:** Only the Skills stream writes to `skill-registry.yaml`.
5. **Each skill needs normalization:** No skill bypasses the allowed/forbidden files and validation pipeline.

---

## Acceleration Output for Superpowers

Acceleration produces `superpowers-recommendations-for-skills.json` with:
- Skill names and marketplace source URLs
- Proposed use in Format Factory
- Stream ownership: Skills
- `installation_required_by_acceleration: false` in every entry
- All entries: `authority_state: ai_draft`, `non_authoritative: true`

---

## This Sprint

Superpowers mode: **audit_only** (catalog read only)

No Superpowers plugins were installed. No commands were added to `.claude/commands/`.
Three skill recommendations were produced for the Skills stream to evaluate.

---

*authority_state: ai_draft | non_authoritative: true*
