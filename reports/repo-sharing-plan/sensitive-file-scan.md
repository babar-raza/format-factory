# Sensitive File Scan
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04
# Policy: Do NOT print actual credential values. Report only: file path, risk type, tracked/untracked, recommended action.

## Overall Security Verdict: LOW RISK

No actual credentials, API keys, tokens, or secrets found in any tracked or untracked file.
All sensitive configuration is correctly gitignored.

---

## Findings

### FINDING 1 — LOW: Absolute local path in tracked report
| Field | Value |
|-------|-------|
| File | `reports/supervisor/product-gap-selection.md` |
| Risk type | Machine-specific absolute path disclosure (username in path) |
| Tracked | YES (M — modified) |
| Pattern found | `C:/Users/prora/OneDrive/Documents/GitHub/format-factory/` |
| Line | 1 |
| Actual credential? | NO — informational path only |
| Recommended action | CONDITIONAL_SHARE — sanitize line 1 before committing |
| Sanitization | Replace `C:/Users/prora/OneDrive/Documents/GitHub/format-factory/` with `./` |

---

### FINDING 2 — SAFE: API key templates (not actual credentials)
| File | Risk type | Tracked | Content | Action |
|------|-----------|---------|---------|--------|
| `.env.example` | API key placeholder | YES | Empty values (`ANTHROPIC_API_KEY=`) | SAFE — template only |
| `.vscode/mcp.dual-orchestration.provider-key.example.json` | API key placeholder | YES | `"your-key-here"` placeholder | SAFE — template only |
| `.vscode/mcp.dual-orchestration.claude-code-oauth.example.json` | OAuth placeholder | YES | `"your-token-here"` placeholder | SAFE — template only |

---

### FINDING 3 — SAFE: .env files (actual, not templates)
| File | Tracked | Status |
|------|---------|--------|
| `.env` | NO (gitignored) | SAFE — correctly gitignored |
| `.env.*` (any variant) | NO (gitignored) | SAFE — correctly gitignored |
| `.env.taskmaster` | NO (gitignored) | SAFE — correctly gitignored |
| `.ruflo/.env` | NO (gitignored) | SAFE — correctly gitignored |
| `.vscode/mcp.json` | NO (gitignored) | SAFE — actual MCP config correctly gitignored |

---

### FINDING 4 — SAFE: PEM certificate files
| File | Type | Risk |
|------|------|------|
| `.local/venv/Lib/site-packages/pip/_vendor/certifi/cacert.pem` | Public CA bundle | NONE — public certificate authority bundle |
| `.local/.../public_key.pem` | Public key | NONE — public key, not private |

Note: `.local/` is gitignored. These files are not tracked.

---

### FINDING 5 — SAFE: Virtual environments
All virtual environments are in `.local/` (gitignored):
- `.local/venv/` — main project venv
- `.local/build-venv/` — build venv
- `.local/smoke-venv-*/` — smoke test venvs

No venv is tracked. Correct.

---

### FINDING 6 — SAFE: Package artifacts
- `.local/r*-metadata/package-artifacts/*.whl` — gitignored (in .local/)
- `.local/pack-output*/*.nupkg` — gitignored (in .local/)

No wheels or NuGet packages are tracked. Correct.

---

### FINDING 7 — SAFE: Log files
- All raw log files are in `.local/` (gitignored)
- `*.log` pattern in .gitignore covers any logs outside .local/
- No log files are tracked

---

### FINDING 8 — INFO: Absolute paths in other reports/supervisor/ files
The scan did not find absolute paths with username `prora` in other tracked files
besides `product-gap-selection.md`. All other reports/supervisor/ content is safe.

---

## Recommended Pre-Push Actions

1. **REQUIRED**: Fix `reports/supervisor/product-gap-selection.md` line 1 — replace absolute path
2. **REQUIRED**: Remove `/reports` lines 173-174 from `.gitignore` (not a credential issue, but blocks sharing)
3. **OPTIONAL**: Search all tracked files for `prora` before each push:
   ```bash
   git diff --cached | grep -i "prora"
   # Must return empty
   ```

---

## What Was NOT Found (confirming good security posture)
- No `ANTHROPIC_API_KEY=<real_value>` in any tracked file
- No `OPENAI_API_KEY=<real_value>` in any tracked file
- No NuGet publish API keys
- No PyPI tokens
- No private RSA/EC keys (*.key, *.pem with PRIVATE KEY header)
- No database connection strings with credentials
- No JWT secrets
- No OAuth client secrets
