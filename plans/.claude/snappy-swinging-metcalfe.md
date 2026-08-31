# CI Forensic Audit — snappy-swinging-metcalfe
# Format Factory — GitHub Actions + GitLab CI

## Context

Full production-grade forensic audit of the Format Factory CI estate across two git remotes.
Triggered by the need to inspect, root-cause, heal, and green-verify every in-scope CI function
before the next release cycle. The three modified .NET CSV source files (`src/net/csv/`) and the
dual-remote architecture (GitHub + GitLab) create risk that CI is not covering recent changes
correctly.

**Repository:** `c:\Users\prora\OneDrive\Documents\GitHub\format-factory`
**Remotes:**
- `github` → `https://github.com/babar-raza/format-factory.git`
- `origin` → `https://oauth2@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git`

**CI Files In-Scope (3 total):**
- `.github/workflows/ci.yml` — GitHub Actions main CI (9 jobs)
- `.github/workflows/release.yml` — GitHub Actions per-format release gate
- `.gitlab-ci.yml` — GitLab CI mirror of ci.yml (10 jobs, 5 stages)

**Pre-existing working tree changes (DO NOT destroy):**
- `src/net/csv/CsvDocument.cs` (modified)
- `src/net/csv/CsvReader.cs` (modified)
- `src/net/csv/CsvWriter.cs` (modified)
- 4 untracked plan/report files in `plans/.claude/` and `reports/`

---

## Confirmed Defects (found in planning phase — fix in TC-FIX-* tasks)

| ID | File | Finding | Severity |
|----|------|---------|---------|
| DEF-001 | ci.yml + .gitlab-ci.yml | `--cov=src` should be `--cov=src/python`; C# src/net/ is included, inflating baseline | MEDIUM |
| DEF-002 | release.yml | Tag trigger `v*` too broad; tags like `v1.0.0` trigger workflow, waste resources, fail at format extraction | LOW-MEDIUM |
| DEF-003 | ci.yml vs .gitlab-ci.yml | `test-full` trigger diverges: GitHub fires on any branch push; GitLab only on main | MEDIUM |
| DEF-004 | ci.yml + .gitlab-ci.yml | `.NET SDK 10.0` is a preview/RC version, not LTS; non-determinism risk | MEDIUM |

**Confirmed Fragilities:**
| ID | Finding | Severity |
|----|---------|---------|
| FRAG-001 | `governance-check` inline Python uses relative `sys.path.insert(0, 'tools/supervisor')` with no error handling — fragile if CWD differs | MEDIUM |
| FRAG-002 | All GitHub Actions pinned at major version tags (v4/v5), not SHA — supply chain risk | MEDIUM |
| FRAG-003 | `skill-attribution-check` only diffs `HEAD~1..HEAD` on push; multi-commit pushes miss earlier commits | LOW |

**Confirmed Healthy (no action needed):**
- All 6 scripts called by CI exist and are non-empty
- All 10 .NET source + test project pairs exist and are complete
- Oracle obligations exit codes are defined and correct
- Bandit B314 skip is intentional and documented
- All secrets (PYPI_TOKEN) are referenced by name only, no leakage

**Unknown State (determined at runtime):**
- Validity of GitHub credential candidates: `GH_TOKEN`, `GITHUB_PAT`, `GITHUB_TOKEN`, `GITHUB_GIST_TOKEN`
- Validity of GitLab credential: `gitlab_token` (canonical; formerly `gitlab_pat`, `gl_pat`, `gl_username`+`gl_password`)
- Docker daemon availability
- GitLab runner container health
- Current remote pipeline status (both GitHub and GitLab)
- Branch protection / required status checks configuration

---

## Taskcards

### Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-BASELINE | CLOSED |
| TC-CRED-GH | CLOSED |
| TC-CRED-GL | CLOSED |
| TC-DOCKER | CLOSED |
| TC-GL-RUNNER | CLOSED |
| TC-GH-RUNNER | CLOSED |
| TC-REMOTE-STATUS | CLOSED |
| TC-FIX-COVERAGE | CLOSED |
| TC-FIX-TAG | CLOSED |
| TC-FIX-TESTFULL | CLOSED |
| TC-FIX-DOTNET-SDK | CLOSED |
| TC-FIX-GOVCHECK | CLOSED |
| TC-LINT-CI | CLOSED |
| TC-LOCAL-VERIFY | CLOSED |
| TC-REMOTE-TRIGGER | CLOSED |
| TC-ADVERSARIAL | CLOSED |
| TC-EVIDENCE | CLOSED |

---

### TC-BASELINE — Non-Destructive State Capture
**Status:** OPEN
**Objective:** Capture complete CI baseline before any changes.
**Steps:**
1. `git status` — record exact modified + untracked files
2. `git log --oneline -5` — record HEAD
3. `git remote -v` — confirm remote URLs
4. `gh run list --limit 10` — GitHub recent workflow runs (if gh auth works)
5. `glab pipeline list --per-page 10` — GitLab recent pipelines (if glab auth works)
6. `docker info 2>&1 | head -20` — Docker daemon state
7. `docker ps -a --filter name=runner` — check for existing runner containers
8. List env var NAMES only: `env | grep -iE "^(GH_|GITHUB_|GL_|GITLAB_)" | cut -d= -f1 | sort`
9. Record sha256 of ci.yml and .gitlab-ci.yml for change tracking

**Evidence:** Baseline YAML block saved to `.local/evidences/ci-audit-metcalfe/baseline.yaml`

---

### TC-CRED-GH — GitHub Credential Validation
**Status:** OPEN
**Objective:** Identify working GitHub credential, establish canonical reference, verify scopes.
**Candidates to test (names only, never print values):**
- `GH_TOKEN`
- `GITHUB_PAT`
- `GITHUB_TOKEN`
- `GITHUB_GIST_TOKEN`

**Steps for each candidate:**
```bash
# Test in isolated env — NEVER echo the value
GH_TOKEN="$CANDIDATE" gh auth status 2>&1
GH_TOKEN="$CANDIDATE" gh api user --jq '.login' 2>&1
GH_TOKEN="$CANDIDATE" gh repo view babar-raza/format-factory --json name,defaultBranchRef 2>&1
GH_TOKEN="$CANDIDATE" gh api /repos/babar-raza/format-factory/actions/runs --jq '.workflow_runs[0].status' 2>&1
```

**Selection:** Pick first candidate with: auth OK + repo access + actions read.
**Canonical reference:** Document selected variable name (not value) in evidence.
**Fresh-shell test:** Verify `gh auth status` works in a new shell using selected variable.

**If gh CLI missing:** Install via `winget install GitHub.cli` or check `scoop install gh`.

**Evidence:** `ci-audit-metcalfe/cred-github.yaml` — variable name, masked fingerprint, scopes, identity

---

### TC-CRED-GL — GitLab Credential Validation
**Status:** OPEN
**Objective:** Identify working GitLab credential, establish canonical reference.
**Canonical variable:** `gitlab_token` (all lowercase, machine-level Windows system env var).
Former candidates (`gitlab_pat`, `gl_pat`, `gl_username`+`gl_password`) are retired.

**Steps to test:**
```bash
# Test PAT against GitLab API — use curl or glab
curl -s --header "PRIVATE-TOKEN: $gitlab_token" \
  "https://gitlab.recruitize.ai/api/v4/user" | python -c "import sys,json; u=json.load(sys.stdin); print(u.get('username','FAIL'))"

# Or via glab:
GITLAB_TOKEN="$gitlab_token" glab auth status
GITLAB_TOKEN="$gitlab_token" glab api /user --field username
GITLAB_TOKEN="$gitlab_token" glab repo view sialkot/cantt-smallize/format-factory
```

**Canonical reference:** Document selected variable name (not value).
**Check glab CLI:** If missing, install via `scoop install glab` or `winget install glab`.
**Note:** `gl_ssh` is for git transport only, not API. Do not test SSH against REST API.

**Evidence:** `ci-audit-metcalfe/cred-gitlab.yaml` — variable name, masked fingerprint, identity, usable projects

---

### TC-DOCKER — Docker Daemon Verification
**Status:** OPEN
**Objective:** Verify Docker is available and healthy for runner operations.
**Steps:**
```bash
docker version                          # Client + server info
docker info                             # Daemon status, storage driver, disk space
docker ps -a                            # All containers (look for runner containers)
docker images | grep -E "gitlab|runner|dotnet|python"  # Relevant images
docker network ls                       # Networks
docker volume ls                        # Volumes
```

**If Docker daemon not running:**
```bash
# Windows: Start Docker Desktop or service
Start-Service docker   # PowerShell
# Or: Open Docker Desktop application
```

**If Docker Desktop not installed:** Check if Docker Engine is available via WSL2.
Do not claim Docker unavailable until both Docker Desktop and WSL2 paths are tried.

**Evidence:** `ci-audit-metcalfe/docker-state.yaml` — version, daemon OK/FAIL, containers list

---

### TC-GL-RUNNER — GitLab Docker Runner Inspection and Healing
**Status:** OPEN
**Objective:** Verify existing Docker-based GitLab runner is registered, healthy, and can claim jobs.
**Steps:**
```bash
# 1. Find existing runner containers
docker ps -a --filter "name=gitlab-runner" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# 2. If runner container found, inspect config
docker exec gitlab-runner gitlab-runner verify
docker exec gitlab-runner cat /etc/gitlab-runner/config.toml

# 3. Check runner registration status via API (using validated GL credential)
curl -s --header "PRIVATE-TOKEN: $gitlab_token" \
  "https://gitlab.recruitize.ai/api/v4/projects/<PROJECT_ID>/runners" | \
  python -c "import sys,json; [print(r['id'],r['status'],r['description']) for r in json.load(sys.stdin)]"

# 4. Check runner logs
docker logs gitlab-runner --tail 50

# 5. If runner stopped, attempt restart
docker start gitlab-runner

# 6. If runner unhealthy/absent, obtain registration token via API
curl -s --header "PRIVATE-TOKEN: $gitlab_token" \
  "https://gitlab.recruitize.ai/api/v4/projects/<PROJECT_ID>/runners/all" | python -m json.tool
```

**If runner needs registration:**
```bash
# Get runner token via API (never print — capture to env)
RUNNER_TOKEN=$(curl -s --header "PRIVATE-TOKEN: $gitlab_token" \
  "https://gitlab.recruitize.ai/api/v4/user/runners" \
  --data "runner_type=project_type&project_id=<ID>&description=format-factory-local&tag_list=docker,local" \
  | python -c "import sys,json; print(json.load(sys.stdin).get('token',''))")

# Register with Docker executor
docker run --rm -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  gitlab/gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.recruitize.ai" \
  --token "$RUNNER_TOKEN" \
  --executor docker \
  --docker-image python:3.11 \
  --description "format-factory-local-docker"
```

**Job proof:** Trigger a simple pipeline job (e.g., lint stage) and confirm this runner claims it.
**Evidence:** `ci-audit-metcalfe/runner-gitlab.yaml` — container name, registration state, job claim proof

---

### TC-GH-RUNNER — GitHub Actions Runner Verification
**Status:** OPEN
**Objective:** Confirm GitHub-hosted runners (`ubuntu-latest`) are sufficient for all CI jobs.
**Steps:**
```bash
# Check if any self-hosted runners are registered
gh api /repos/babar-raza/format-factory/actions/runners --jq '.runners[] | {name, status, labels: [.labels[].name]}'

# Check current active workflow runs
gh run list --limit 5 --json name,status,conclusion,headBranch

# Verify the most recent run result
gh run view <RUN_ID> --log | tail -100
```

**Assessment:**
- All 9 jobs in ci.yml use `runs-on: ubuntu-latest` (GitHub-hosted)
- No self-hosted runner is needed unless a job is labeled otherwise
- If self-hosted runners found: check they're online and not conflicting

**If self-hosted runner needed (and absent):**
```bash
# Create GitHub Actions runner via API
gh api /repos/babar-raza/format-factory/actions/runners/registration-token --method POST \
  --jq '.token' > /dev/null  # Never print — capture only

# Then docker run with the token (never echo)
```

**Evidence:** `ci-audit-metcalfe/runner-github.yaml` — hosted runner OK, self-hosted inventory, job claim proof

---

### TC-REMOTE-STATUS — Current Remote Pipeline Status
**Status:** OPEN
**Objective:** Determine baseline pass/fail state of both remotes before making fixes.
**GitHub Steps:**
```bash
# List recent workflow runs with status
gh run list --repo babar-raza/format-factory --limit 10 \
  --json name,status,conclusion,headBranch,createdAt \
  --jq '.[] | [.name, .status, .conclusion, .headBranch, .createdAt] | @tsv'

# View logs of most recent CI run
gh run list --workflow ci.yml --limit 1 --json databaseId --jq '.[0].databaseId' | \
  xargs gh run view --log | tail -200
```

**GitLab Steps:**
```bash
# List recent pipelines
glab pipeline list --per-page 10

# View most recent pipeline jobs
glab pipeline ci view

# Download logs of failed jobs
glab pipeline list --per-page 1 --json | \
  python -c "import sys,json; p=json.load(sys.stdin)[0]; print(p['id'],p['status'],p['web_url'])"
```

**Record for each remote:**
- Last pipeline/run status
- Failing jobs (if any)
- Last passing commit

**Evidence:** `ci-audit-metcalfe/remote-status.yaml`

---

### TC-FIX-COVERAGE — Fix --cov=src → --cov=src/python
**Status:** OPEN
**Files:** `.github/workflows/ci.yml`, `.gitlab-ci.yml`
**Root cause:** Coverage arg `--cov=src` includes `src/net/` (C# files) giving false coverage inflation.
**Fix:**

In `.github/workflows/ci.yml` (test-full job):
```yaml
# Before:
run: pytest --cov=src --cov-report=xml --cov-report=term-missing
# After:
run: pytest --cov=src/python --cov-report=xml --cov-report=term-missing
```

In `.gitlab-ci.yml` (test-full job):
```yaml
# Before:
- pytest --cov=src --cov-report=xml --cov-report=term-missing
# After:
- pytest --cov=src/python --cov-report=xml --cov-report=term-missing
```

**Local verification:**
```bash
# Confirm src/python/ exists and contains Python packages
ls src/python/
# Run coverage locally to verify it now only measures Python
.venv/Scripts/pytest --cov=src/python --cov-report=term-missing tests/unit/ -x -q 2>&1 | grep "TOTAL"
```

**Evidence:** Changed lines in both files + local coverage output showing Python-only measurement.

---

### TC-FIX-TAG — Fix release.yml Tag Trigger Pattern
**Status:** OPEN
**File:** `.github/workflows/release.yml`
**Root cause:** `tags: ["v*"]` matches `v1.0.0`, wasting runner time before the format-extraction guard fires.
**Fix:**
```yaml
# Before:
on:
  push:
    tags: ["v*"]
# After:
on:
  push:
    tags: ["[a-z]*-v[0-9]*"]
```

This pattern matches `fods-v0.1.0`, `csv-v1.0.0`, etc. and rejects `v1.0.0` at GitHub filter level.

**Local verification:** `actionlint .github/workflows/release.yml` (if actionlint available)
**Evidence:** Changed file + explanation of pattern.

---

### TC-FIX-TESTFULL — Fix test-full Trigger Divergence
**Status:** OPEN
**Files:** `.github/workflows/ci.yml`, `.gitlab-ci.yml`
**Root cause:** GitHub `test-full` runs on any branch push; GitLab only on main.
**Decision:** Align to GitLab behavior (main-only) as running full matrix on every feature-branch push wastes CI budget. The PR/MR fast tests (test-fast) provide interim feedback.

In `.github/workflows/ci.yml` (test-full job):
```yaml
# Before:
test-full:
  if: github.event_name == 'push'
# After:
test-full:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

**Local verification:** Validate with `actionlint .github/workflows/ci.yml`
**Evidence:** Changed file + explanation.

---

### TC-FIX-DOTNET-SDK — Document .NET SDK Version Risk
**Status:** OPEN
**Files:** `.github/workflows/ci.yml`, `.gitlab-ci.yml`
**Root cause:** `dotnet/sdk:10.0` and `dotnet-version: "10.0.x"` reference a preview SDK.
**Assessment required first:** Run `docker run --rm mcr.microsoft.com/dotnet/sdk:10.0 dotnet --version` to confirm the image exists and reports a version. If it resolves to a stable GA release, downgrade this to LOW risk and add a comment. If it resolves to a preview build, evaluate switching to `9.0.x` (current stable LTS).

**Fix options (choose based on runtime check):**
- Option A (if 10.0 is GA): Add `# .NET 10.0 GA — stable as of <date>` comment to both files.
- Option B (if 10.0 is preview): Downgrade to `dotnet-version: "9.0.x"` and `mcr.microsoft.com/dotnet/sdk:9.0`. Verify projects compile.

**Verification:** `dotnet build src/net/csv/FormatFactory.Csv.csproj --configuration Release`
**Evidence:** `dotnet --version` output, build result.

---

### TC-FIX-GOVCHECK — Harden governance-check Inline Python
**Status:** OPEN
**Files:** `.github/workflows/ci.yml`, `.gitlab-ci.yml`
**Root cause:** Inline `sys.path.insert(0, 'tools/supervisor')` is fragile. No error handling.
**Fix:** Extract inline Python to a dedicated script `tools/governance/run_ci_governance_check.py` that:
1. Uses `pathlib.Path(__file__).parent.parent.parent` for robust path resolution
2. Wraps import in try/except with clear error message
3. Is importable/testable independently

**In CI files, replace inline python -c block with:**
```yaml
# Both ci.yml and .gitlab-ci.yml governance-check job:
- python tools/governance/run_ci_governance_check.py
```

**New script** (`tools/governance/run_ci_governance_check.py`):
```python
#!/usr/bin/env python3
"""CI governance check wrapper — robust path resolution."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

try:
    from governance_validators import run_all_governance_validators
except ImportError as e:
    print(f"ERROR: Cannot import governance_validators: {e}", file=sys.stderr)
    print(f"  Tried path: {REPO_ROOT / 'tools' / 'supervisor'}", file=sys.stderr)
    sys.exit(2)

decl = {
    "run_id": "ci-governance-check",
    "sprint_id": "ci",
    "declared_scope": "CI_CHECK",
    "planned_work_items": [],
    "evidence_paths": [],
    "test_references": [],
    "worker_verdict": "PASS",
}
result = run_all_governance_validators(decl)
print(
    f"Governance validators: fail={result['fail_count']} "
    f"warn={result['warn_count']} pass={result['pass_count']} "
    f"blocks={result['blocks_sprint']}"
)
sys.exit(1 if result["blocks_sprint"] else 0)
```

**Verification:** `python tools/governance/run_ci_governance_check.py`
**Evidence:** Script exists, runs without error, matches inline behavior.

---

### TC-LINT-CI — CI File Linting
**Status:** OPEN
**Objective:** Lint all GitHub Actions workflow files with actionlint and validate GitLab CI config.
**GitHub Actions linting:**
```bash
# Install actionlint if not present
# Option 1: Download binary
curl -sL https://github.com/rhysd/actionlint/releases/latest/download/actionlint_linux_amd64.tar.gz | tar xz
# Option 2: If go is available: go install github.com/rhysd/actionlint/cmd/actionlint@latest
# Option 3: Run via docker
docker run --rm -v "${PWD}:/repo" --workdir /repo rhysd/actionlint:latest -color

# Run on all workflow files
actionlint .github/workflows/ci.yml .github/workflows/release.yml
```

**GitLab CI validation:**
```bash
# Validate via GitLab API
cat .gitlab-ci.yml | curl -s --header "PRIVATE-TOKEN: $gitlab_token" \
  --header "Content-Type: application/json" \
  --data '{"content": "'$(cat .gitlab-ci.yml | python -c "import sys,json; print(json.dumps(sys.stdin.read()))" )'"' \
  "https://gitlab.recruitize.ai/api/v4/ci/lint" | \
  python -c "import sys,json; r=json.load(sys.stdin); print('VALID' if r.get('valid') else 'INVALID:', r.get('errors',[]))"
```

**Evidence:** lint output (PASS/FAIL per file, per rule).

---

### TC-LOCAL-VERIFY — Local CI Command Verification
**Status:** OPEN
**Objective:** Verify key CI commands pass locally before triggering remote pipelines.
**Commands to run locally (in order):**
```bash
# 1. Ruff lint (mirrors CI lint job)
.venv/Scripts/python -m ruff check src/ tests/ tools/ --output-format=text 2>&1 | tail -20

# 2. Bandit security scan (mirrors CI security job)
.venv/Scripts/python -m bandit -r src/python/ -ll -q --skip B314 2>&1 | tail -20

# 3. Source structure validator
.venv/Scripts/python tools/validators/source_structure_validator.py 2>&1

# 4. Governance check (via new extracted script after TC-FIX-GOVCHECK)
.venv/Scripts/python tools/governance/run_ci_governance_check.py 2>&1

# 5. Oracle obligations
.venv/Scripts/python tools/oracle/validate_oracle_obligations.py 2>&1

# 6. Capability drift
.venv/Scripts/python tools/capability_sync/detect_drift.py 2>&1 | tail -20

# 7. Fast tests (mirrors test-fast CI job)
.venv/Scripts/python tools/test_runner.py --layer 3 \
  --known-failures registry/known-failure-ledger.yaml \
  --json-out .local/test-results/ci-metcalfe-fast.json 2>&1 | tail -30

# 8. Coverage test with FIXED arg (mirrors test-full after DEF-001 fix)
.venv/Scripts/pytest --cov=src/python --cov-report=term-missing -x -q 2>&1 | tail -20

# 9. .NET build (if .NET SDK available locally — check first)
dotnet --version 2>&1 || echo "dotnet not available locally"
# If available:
dotnet build src/net/csv/FormatFactory.Csv.csproj --configuration Release 2>&1 | tail -20
```

**Pass criteria:** All commands exit 0 (or match known-acceptable warnings).
**Evidence:** `ci-audit-metcalfe/local-verify.yaml` — command, exit code, truncated output

---

### TC-REMOTE-TRIGGER — Trigger and Monitor Remote Pipelines
**Status:** OPEN
**Objective:** After all fixes are staged and committed, trigger both remotes and monitor to green.

**Pre-conditions:** TC-FIX-* tasks complete, TC-LOCAL-VERIFY passes.

**Commit approach:**
```bash
# Stage only CI file changes (not src/net/csv/ — those are pre-existing uncommitted)
git add .github/workflows/ci.yml .github/workflows/release.yml .gitlab-ci.yml
git add tools/governance/run_ci_governance_check.py
git status  # Confirm staged files

git commit -m "$(cat <<'EOF'
fix(ci): correct --cov path, tag pattern, test-full trigger, governance script

- Fix --cov=src → --cov=src/python (DEF-001: C# files excluded)
- Narrow release tag filter to [a-z]*-v[0-9]* (DEF-002)
- Restrict test-full to main branch on GitHub (DEF-003: parity with GitLab)
- Extract governance-check inline Python to tools/governance/run_ci_governance_check.py (FRAG-001)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

**GitHub push:**
```bash
git push "https://${GH_TOKEN}@github.com/babar-raza/format-factory.git" main
```

**GitLab push:**
```bash
git push "https://oauth2:${gitlab_token}@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git" main
```

**Monitor GitHub:**
```bash
# Wait for run to start (poll every 10s, max 3 min)
gh run list --workflow ci.yml --limit 1 --json databaseId,status --jq '.[0]'
gh run watch <RUN_ID>
gh run view <RUN_ID> --log-failed  # Only if failed
```

**Monitor GitLab:**
```bash
glab pipeline list --per-page 1
glab pipeline ci view  # Interactive monitor
# Or:
glab pipeline status
```

**Evidence:** `ci-audit-metcalfe/remote-trigger.yaml` — run IDs, job statuses, final conclusions

---

### TC-ADVERSARIAL — Adversarial Review
**Status:** OPEN
**Objective:** Re-inspect all changed files and remote logs; confirm no false greens, no weakened tests.
**Checklist:**
1. Reopen `.github/workflows/ci.yml` — verify every job still present, no accidental removals
2. Reopen `.github/workflows/release.yml` — verify tag filter change is correct regex
3. Reopen `.gitlab-ci.yml` — verify mirror stays in sync after changes
4. Download GitHub Actions CI run log: `gh run view <ID> --log > /tmp/ci-run.log && grep -E "FAIL|ERROR|exit" /tmp/ci-run.log`
5. Download GitLab job trace: `glab job trace <JOB_ID> > /tmp/gl-job.log && grep -E "FAIL|ERROR|exit" /tmp/gl-job.log`
6. Verify coverage threshold still enforced: grep `fail-under=85` in run log
7. Verify oracle-obligations still runs and exits non-zero on violation
8. Verify Gate 11 check in release.yml still blocks non-approved formats
9. Check no `continue-on-error: true` was accidentally added to mandatory jobs
10. Verify `tools/governance/run_ci_governance_check.py` output matches previous inline behavior
11. Verify GitHub branch protection still requires CI checks (if accessible via API)
12. Confirm PYPI_TOKEN is NOT in any committed file

**Evidence:** Adversarial review checklist with PASS/FAIL per item.

---

### TC-EVIDENCE — Final Evidence Collection and Report
**Status:** OPEN
**Objective:** Compile all evidence and write the final CI estate status report.
**Steps:**
```bash
# Create evidence directory
mkdir -p .local/evidences/ci-audit-metcalfe/

# Collect final git state
git log --oneline -5 > .local/evidences/ci-audit-metcalfe/final-git-state.txt
git status >> .local/evidences/ci-audit-metcalfe/final-git-state.txt

# Final remote run IDs
echo "GitHub run: $(gh run list --workflow ci.yml --limit 1 --json databaseId --jq '.[0].databaseId')" \
  >> .local/evidences/ci-audit-metcalfe/final-git-state.txt

# Summarize runner state
docker ps --filter name=runner --format "table {{.Names}}\t{{.Status}}" \
  >> .local/evidences/ci-audit-metcalfe/runner-state.txt
```

**Final report fields:**
- Repository register (2 remotes)
- Credential register (canonical references, masked fingerprints)
- CI function inventory (3 files, 10 jobs + release job)
- Manual review ledger (all 10 jobs reviewed)
- Root-cause records (DEF-001 through DEF-004, FRAG-001 through FRAG-003)
- Fixes applied (list with before/after)
- Local verification: PASS/FAIL per command
- GitHub remote verification: run ID + all job conclusions
- GitLab remote verification: pipeline ID + all job conclusions
- Runner register
- Adversarial review results
- Final estate status: GREEN_VERIFIED or BLOCKED_TRUE_EXTERNAL_DEPENDENCY

---

## Execution Order

```
TC-BASELINE
  → TC-CRED-GH (parallel)
  → TC-CRED-GL (parallel)
  → TC-DOCKER (parallel)
  ↓
TC-GL-RUNNER (after TC-DOCKER)
TC-GH-RUNNER (after TC-CRED-GH)
TC-REMOTE-STATUS (after credentials validated)
  ↓
TC-FIX-COVERAGE (parallel)
TC-FIX-TAG (parallel)
TC-FIX-TESTFULL (parallel)
TC-FIX-DOTNET-SDK (parallel, after runtime .NET version check)
TC-FIX-GOVCHECK (parallel)
  ↓
TC-LINT-CI (after all fixes)
TC-LOCAL-VERIFY (after all fixes)
  ↓
TC-REMOTE-TRIGGER (after lint + local verify pass)
  ↓
TC-ADVERSARIAL
  ↓
TC-EVIDENCE
```

## Files Modified by This Plan

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | DEF-001 (coverage), DEF-003 (test-full trigger), FRAG-001 (governance script) |
| `.github/workflows/release.yml` | DEF-002 (tag pattern) |
| `.gitlab-ci.yml` | DEF-001 (coverage), FRAG-001 (governance script) |
| `tools/governance/run_ci_governance_check.py` | NEW — extracted from inline CI python |

## Constraints

- DO NOT modify `src/net/csv/CsvDocument.cs`, `CsvReader.cs`, `CsvWriter.cs` — pre-existing uncommitted changes
- DO NOT weaken any test gates (`continue-on-error`, threshold reduction, job removal)
- DO NOT expose credential values in logs, files, or commits
- DO NOT push to GitLab if host is unreachable (classify as EXTERNAL_BLOCKER: gitlab_host_unreachable)
- DO NOT register a broad organization-wide runner; project-scoped only
- Preserve all 8 pre-existing untracked files (plans/.claude/ and reports/)

## True External Blockers (if encountered)

- `EXTERNAL_BLOCKER: git_push_credentials_unavailable` — if all 4 GitHub candidates fail
- `EXTERNAL_BLOCKER: gitlab_host_unreachable` — if GitLab host at recruitize.ai is down
- `EXTERNAL_BLOCKER: gitlab_credentials_all_invalid` — if all GL candidates fail AND host is reachable
- `EXTERNAL_BLOCKER: docker_unavailable` — if Docker Desktop AND WSL2 paths both fail
- `EXTERNAL_BLOCKER: gate11_approval_required` — if release pipeline needs Babar Raza sign-off (release.yml only, not CI)


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-04T04:33:43.767015+00:00"
  locked_by: "12632ba0096e"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
