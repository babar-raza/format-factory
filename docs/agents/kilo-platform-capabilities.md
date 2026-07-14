# Kilo AI Platform Capabilities Assessment
# Mission: FF-AGENTS-PARITY-001 (TC-ACP-001-01)
# Date: 2026-07-12

## 1. Platform Summary

Kilo AI (kilo.ai) is an AI coding assistant platform based on VS Code with an LLM backend.
The repository's Kilo configuration consists of:
- : declares dependency 
- : schema reference to , 

The system recon (FF-DEEP-RECON-20260705-052931) identified Kilo as "minimal config" with
ISSUE-DISC-001: "effectively unused" due to 2-line configuration.

## 2. Native Capabilities

Based on  v7.x and kilo.ai platform documentation:

| Capability | Status | Evidence |
|-----------|--------|---------|
| Native file I/O (read) | AVAILABLE | VS Code extension API provides file access |
| Native file I/O (write) | AVAILABLE | VS Code extension API provides write access |
| Shell execution | AVAILABLE | Terminal API in VS Code extensions |
| Tool calling (structured) | LIMITED | Depends on model API; not natively structured |
| Instruction file loading | UNKNOWN | No KILO.md instruction file exists; config-based |
| System prompt injection | AVAILABLE | kilo.jsonc config may accept system prompt fields |

## 3. Confirmed Limitations

1. **No KILO.md**: No instruction file equivalent to CLAUDE.md/AGENTS.md exists
2. **No skill integration**: Skill registry not loaded into Kilo context
3. **Minimal config**: Only 2 fields in kilo.jsonc (schema, snapshot)
4. **No governance binding**: Pre-mutation guard not configured for Kilo
5. ****: Disables context snapshot feature; reduces inter-session continuity

## 4. RC Achievability Map

| RC-ID | Capability | Achievable | Blocking Reason |
|-------|-----------|-----------|----------------|
| RC-001 | Read repository files | true | VS Code file API |
| RC-002 | Write repository files | true | VS Code file API |
| RC-003 | Execute shell commands | true | Terminal API |
| RC-004 | Load instruction files | unknown | No KILO.md; config only |
| RC-005 | Parse skill registry | unknown | Requires instruction file |
| RC-006 | Validate declarations | unknown | Requires skill invocation |
| RC-007 | Run governance validators | true | Shell execution |
| RC-008 | Call pre_mutation_guard | true | Shell execution |
| RC-009 | Parse capability registry | true | File read + YAML |
| RC-010 | Generate evidence declarations | true | File write |
| RC-011 | Index gap ledger | true | File read/write |
| RC-012 | Run tests | true | Shell execution |
| RC-013 | Commit to git | true | Shell execution |
| RC-014 | Push to remote | true | Shell execution + credentials |
| RC-015 | Run autonomous cycle | true | Shell execution |
| RC-016 | Invoke skills by name | unknown | No skill dispatch mechanism |
| RC-017 | Enforce skill-first policy | false | No pre-commit hook binding |
| RC-018 | Load session state | unknown | No .local/ state loader |
| RC-019 | Read AGENTS.md | true | File read |
| RC-020 | Parse capability-routing-registry | true | File read + YAML |
| RC-021 | Generate sprint prompt | true | Shell + file write |
| RC-022 | Multi-sprint autonomous loop | unknown | No continuation signal loader |

## 5. Peer Parity Assessment

| Feature | Claude Code | Codex | Kilo AI |
|---------|------------|-------|---------|
| Instruction file | CLAUDE.md (full) | AGENTS.md | None |
| Skill dispatch | .claude/commands/ | .codex/ | None |
| Shell access | Full | Full | Full (VS Code) |
| File access | Full | Full | Full (VS Code) |
| Governance binding | CLAUDE.md + hooks | AGENTS.md | None |
| Pre-mutation guard | Available (prompt) | Available (prompt) | Unknown |
| Multi-session continuity | session-resume.md | AGENTS.md | snapshot: false |
