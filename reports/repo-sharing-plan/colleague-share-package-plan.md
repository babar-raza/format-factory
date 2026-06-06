# Colleague Share Package Plan
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## What a Colleague Gets After Clone

Remote: `https://github.com/babar-raza/format-factory.git`

A colleague running `git clone https://github.com/babar-raza/format-factory.git` will receive
the following, assuming the proposed remote refresh has been executed:

---

## Immediately Usable

### Product Source Code

| Path | Files | Contents |
|------|-------|----------|
| `src/python/` | ~50 | Python parsers/converters: fods, fodt, netpbm (pbm/pgm/ppm), sylk, dif, zst |
| `src/net/` | ~47 | .NET parsers/converters: fods, fodt, netpbm |

### Tests

| Path | Files | Contents |
|------|-------|----------|
| `tests/python/` | ~200+ | pytest test suites for all Python formats |
| `tests/net/` | ~120+ | .NET xUnit test suites for FODS, FODT, Netpbm |
| `tests/supervisor/` | ~40+ | Supervisor pipeline test suite |

### Examples

| Path | Files | Contents |
|------|-------|----------|
| `examples/python/` | ~10 | Python usage examples: ppm, sylk, zst |
| `examples/net/` | ~10 | .NET usage examples: fods, fodt, netpbm |
| `examples/dotnet/` | varies | Additional .NET examples |

### Documentation

| Path | Files | Contents |
|------|-------|----------|
| `docs/automation/` | ~20 | Supervisor worker contract, automation flow docs |
| `docs/governance/` | ~15 | Authority boundary, AI toolchain governance |
| `docs/prompt-templates/` | ~10 | Stream prompt requirements, repair templates |
| `docs/ai/` | ~10 | AI platform docs |
| `docs/taskmaster/` | ~5 | TaskMaster bridge docs |

### Project Authority Files

| Path | Purpose |
|------|---------|
| `registry/format-registry.yaml` | Gate authority — defines all supported formats |
| `product-capability-matrix/poc-targets.yaml` | What's implemented and to what depth |
| `plans/master-plan.md` | Sprint roadmap |
| `state/current-state.md` | Current project state snapshot |
| `CLAUDE.md` | Session instructions for AI assistants |
| `AGENTS.md` | Governance — never modify without Babar Raza approval |

### Supervisor System

| Path | Files | Purpose |
|------|-------|---------|
| `tools/supervisor/` | ~50+ | Supervisor pipeline, evidence tools, validators |
| `.supervisor/` | ~25 | Supervisor config, schemas, prompt templates |
| `reports/supervisor/` | ~21 | Live sprint state: session-resume, approval-gates, next-sprint |
| `.claude/commands/` | ~26 | Claude Code automation command definitions |

### Knowledge Base

| Path | Files | Purpose |
|------|-------|---------|
| `memory/` | ~73 | Sprint history, decisions, architectural knowledge |
| `taskcards/` | ~185 | Sprint task definitions |
| `acquisition-packs/` | ~165 | Format acquisition specifications |
| `schemas/` | ~34 | JSON/YAML validation schemas |
| `samples/` | ~126 | Sample format files used by tests |

---

## NOT Included (Local Only — Gitignored)

| Item | Size | Why Excluded |
|------|------|--------------|
| `.local/` | ~957 MB | Evidence runs, built wheels, venvs — machine-specific |
| `.local/venv/`, `.local/build-venv/` | varies | Python virtual environments |
| `.local/r*-metadata/package-artifacts/` | varies | Built .whl and .nupkg files |
| `.local/evidences/` | varies | Sprint evidence ZIP bundles |
| `.local/raw-*-logs/` | varies | Raw test/install/build logs |
| `.supervisor/state/` | varies | Supervisor runtime state |
| `.ruflo/`, `.swarm/` | varies | External orchestration tool state |
| `.vscode/mcp.json` | small | Actual MCP config (may contain API keys) |
| `.env` | small | Credentials (if present) |

---

## Onboarding Steps for a New Colleague

### Python Setup

```bash
# 1. Clone
git clone https://github.com/babar-raza/format-factory.git
cd format-factory

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# 3. Install in development mode
pip install -e src/python/fods/
pip install -e src/python/fodt/
pip install -e src/python/sylk/
pip install -e src/python/dif/
# etc. for each format

# 4. Run tests
pytest tests/python/fods/ -v
pytest tests/python/fodt/ -v
```

### .NET Setup

```bash
# 1. Ensure .NET SDK 8.0+ is installed

# 2. Build
cd src/net
dotnet build

# 3. Run tests
dotnet test tests/net/fods/
dotnet test tests/net/fodt/
dotnet test tests/net/netpbm/
```

### Supervisor System

```bash
# 1. Install supervisor dependencies
pip install -r tools/supervisor/requirements.txt  # if present
# or: pip install pyyaml jsonschema

# 2. Read session context
# Follow CLAUDE.md instructions — read reports/supervisor/session-resume.md first
```

---

## Missing Onboarding Items (Gaps to Address)

| Gap | Priority | Notes |
|-----|----------|-------|
| No top-level `README.md` | HIGH | Colleagues need entry point with setup instructions |
| No `requirements.txt` at root | MEDIUM | For installing all Python dependencies at once |
| No `pyproject.toml` at root | MEDIUM | For unified Python project configuration |
| `AGENTS.md` should clarify supervisor entry point | LOW | Add pointer to `reports/supervisor/session-resume.md` |

---

## Security Posture for Colleagues

- No API keys, tokens, or credentials in the repo
- `.env.example` shows required environment variables (values are empty placeholders)
- `.vscode/mcp.*.example.json` shows MCP config structure (values are `"your-key-here"`)
- Colleagues must create their own `.env` and `.vscode/mcp.json` from the examples
