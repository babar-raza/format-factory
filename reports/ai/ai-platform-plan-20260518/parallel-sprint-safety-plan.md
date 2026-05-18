# Parallel Sprint Safety Plan

**Date:** 2026-05-18

## 1. Problem

Format Factory runs parallel sprints (acquisition, commercial, AI platform) that may conflict on shared files. The AI platform implementation must not break ongoing acquisition or commercial work.

## 2. Shared File Conflict Prevention

### Files AI Platform May Modify
- `tools/ai/**` (exclusive to AI platform — no conflict)
- `.local/ai/**` (exclusive, gitignored — no conflict)
- `tests/ai/**` (exclusive — no conflict)
- `AGENTS.md` (shared — requires coordination)
- `GOVERNANCE.md` (shared — requires coordination)
- `plans/master-plan.md` (shared — requires coordination)
- `docs/ai/**` (exclusive — no conflict)

### Coordination Protocol for Shared Files
1. Before modifying AGENTS.md, GOVERNANCE.md, or master-plan.md: check if other sprint has pending changes
2. If conflict detected: coordinate with Lane 0 coordinator
3. Use additive edits only (new sections, not rewriting existing sections)
4. Never rewrite sections owned by acquisition or commercial tracks

## 3. Dependency Isolation

### AI Platform Dependencies
- LiteLLM, Pydantic v2, LanceDB (Phase 3), LlamaIndex (Phase 3)
- Installed in `.venv` or AI-specific requirements file
- MUST NOT conflict with existing Python test dependencies
- MUST NOT add runtime dependencies to product packages

### Isolation Rules
1. AI dependencies in separate requirements file (e.g., `requirements-ai.txt`)
2. No AI dependency in `pyproject.toml` for product packages
3. AI imports only in `tools/ai/` and `tests/ai/`
4. pytest collection must not fail if AI dependencies missing (conditional imports in tests)

## 4. Evidence Bundle Isolation

AI platform sprints produce separate evidence bundles. They do not modify or depend on acquisition/commercial evidence bundles.

## 5. Taskcard Isolation

AI taskcards (`AI-*`) are separate from acquisition taskcards (`TC-*`), commercial taskcards, and format taskcards. No cross-taskcard state dependencies except documented prerequisites.

## 6. Failure Handling

If AI platform sprint conflicts with parallel work:
1. Stop AI platform sprint
2. Document conflict
3. Coordinate resolution with human authority
4. Resume after conflict resolved
5. Do not force-overwrite parallel sprint work
