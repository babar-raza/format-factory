# Current .gitignore Rules Analysis
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Summary

The `.gitignore` is generally well-configured with one CRITICAL BUG and several patterns
that are already present (requiring no additions).

---

## CRITICAL BUG: /reports appears twice (lines 173-174)

```
173: /reports
174: /reports
```

**Effect**: The pattern `/reports` gitignores the entire `reports/` directory for ALL
new additions. Any file in `reports/` that is not already tracked cannot be added with
`git add` — it requires `git add -f` (force).

**Confirmed by**:
```
git check-ignore -v reports/repo-sharing-plan/
.gitignore:174:/reports    reports/repo-sharing-plan/
```

**Why existing tracked files are unaffected**: Once a file is tracked by git, `.gitignore`
has no effect on it. The 1867 tracked files in `reports/` continue to show as modified (M)
correctly. However, the 375 untracked files include ZERO from `reports/` because of this bug.

**Root cause**: The two `/reports` lines were likely accidentally appended at the end of
the Ruflo config section (lines 163-174). They have no comment explaining their intent.

**Required fix**: Remove BOTH `/reports` lines (173 and 174) from `.gitignore`.
This is the MOST IMPORTANT change in the proposed patch.

---

## Already-Covered Patterns (no additions needed)

The following patterns that were initially thought to be missing are already present:

| Pattern | Line | Section |
|---------|------|---------|
| `dist/` | 34 | Python |
| `build/` | 35 | Python |
| `.coverage` | 39 | Python |
| `.coverage.*` | 40 | Python |
| `coverage.xml` | 41 | Python |
| `*.snupkg` | 57 | .NET |
| `*.nupkg` | 56 | .NET |
| `*.log` | 92 | Editor/IDE |
| `*.tmp` | 93 | Editor/IDE |

---

## Full .gitignore Content with Line Numbers

```
  1: # format-factory .gitignore
  2: # Phase 0 Foundation
  3:
  7: .local/                          # LOCAL-ONLY EXECUTION DATA
  8: .local/**
 13: .env                             # SECRETS AND CREDENTIALS
 14: .env.*
 15: !.env.example
 20: __pycache__/                     # PYTHON
 21: *.py[cod]
 22: *$py.class
 23: *.pyc
 24: *.pyo
 25: *.pyd
 26: .pytest_cache/
 27: .mypy_cache/
 28: .ruff_cache/
 29: .venv/
 30: venv/
 31: env/
 32: ENV/
 33: *.egg-info/
 34: dist/
 35: build/
 36: *.egg
 37: .tox/
 38: htmlcov/
 39: .coverage
 40: .coverage.*
 41: coverage.xml
 42: *.cover
 47: bin/                             # .NET / C#
 48: obj/
 49: *.dll
 50: *.pdb
 51: *.user
 52: *.suo
 55: .vs/
 56: *.nupkg
 57: *.snupkg
 58: TestResults/
 64: node_modules/                    # NODE
 65: npm-debug.log*
 72: json                             # STRAY ARTIFACTS
 73: ff.zip
 74: src/src.zip
 75: format-factory.zip
 80: .DS_Store                        # OS ARTIFACTS
 85: ehthumbs.db
 86: Thumbs.db
 92: *.log                            # EDITOR / IDE
 93: *.tmp
 94: *.swp
 95: *.swo
115: evidence-bundles/*.zip           # GENERATED EVIDENCE BUNDLES
120: reports/evidence/                # REPORTS EVIDENCE SUBFOLDER
127: bundle-metadata/                 # BUNDLE-METADATA STAGING
134: reports/ai/ai-platform-*/       # LANE F AI PLATFORM
143: reports/**/*.sha256-proof.json  # R58 SIDECAR PROOF
145: docs/_audit/
153: .supervisor/state/              # LOCAL SUPERVISOR STATE
158: .vscode/mcp.json                # TASK MASTER AI
159: .env.taskmaster
160: .taskmaster/.env
161: .taskmaster/config.local.json
166: .env.ruflo                      # RUFLO (claude-flow)
167: .ruflo/.env
168: .ruflo/config.local.json
169: .ruflo/state/
170: .ruflo/logs/
171: .swarm/
172: .local/ruflo/
173: /reports                        # ← CRITICAL BUG (1 of 2)
174: /reports                        # ← CRITICAL BUG (2 of 2)
```

---

## Patterns NOT yet covered (genuine gaps)

| Pattern | Priority | Reason |
|---------|----------|--------|
| `tmp/` | LOW | Temp scratch directories |
| `temp/` | LOW | Temp scratch directories |
| `output*/` | LOW | Generated output directories |
| `.claude-flow/` | LOW | claude-flow runtime state (if created) |
| `.claude-flow-state/` | LOW | claude-flow state directory |
| `*.tar.gz` | VERY LOW | Source distributions outside .local/ |

---

## .git/info/exclude

Not inspected (local-only, machine-specific). Mentioned in plan as containing an exclude
for `reports/r33/live-telemetry/` but not verified in this run.
