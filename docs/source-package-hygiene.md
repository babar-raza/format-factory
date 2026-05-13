# Source Package Hygiene Policy
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane G — Source Package Hygiene
# Date: 2026-05-13
# Status: ACTIVE — normative for all source packaging operations

## 1. Purpose

This document defines the hygiene rules for all source packages, review packages, and
ZIP archives produced by or for the Format Factory project.

---

## 2. Repository Hygiene (Git)

The `.gitignore` at repository root already excludes:

| Category | Patterns Excluded |
|---|---|
| .NET build outputs | `bin/`, `obj/`, `*.nupkg`, `*.snupkg`, `TestResults/` |
| Python cache | `__pycache__/`, `*.py[cod]`, `*.pyc`, `*.pyo`, `*.pyd` |
| Python venv | `.venv/`, `venv/`, `env/`, `ENV/` |
| Python dist | `*.egg-info/`, `dist/`, `build/`, `*.egg` |
| Coverage | `htmlcov/`, `.coverage`, `coverage.xml` |
| Local data | `.local/` |
| Secrets | `.env`, `.env.*` |
| IDE | `.vs/`, `.idea/`, `*.suo`, `*.user` |

**Repository status: CLEAN** — no build artifacts are committed.

---

## 3. Source Review ZIP Policy

When creating a source review package (ZIP) for human review or external sharing,
the following MUST be excluded:

### 3.1 Must Exclude from Source ZIPs

- `bin/` — compiled output
- `obj/` — MSBuild intermediate files
- `__pycache__/` — Python bytecode cache
- `*.pyc`, `*.pyo`, `*.pyd` — compiled Python
- `*.nupkg`, `*.snupkg` — NuGet packages
- `TestResults/` — test runner outputs
- `.local/` — local-only data (evidence bundles, spec-cache, etc.)
- `.env`, `.env.*` — secrets
- `bundle-metadata/` — staging area for evidence bundles
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`

### 3.2 Must Include in Source ZIPs

- All `.cs` source files
- All `.csproj` project files
- All `.py` source files
- `README.md` for each component
- Relevant test files
- Planning docs (if creating a review package)

---

## 4. Current Audit Findings

### 4.1 Repository (as of 2026-05-13)

- Status: **CLEAN**
- Committed tracked files in `src/net/fods/`: `FodsParser.cs`, `FormatFactory.Fods.csproj`, `README.md`
- Committed tracked files in `src/net/fodt/`: `FodtParser.cs`, `FormatFactory.Fodt.csproj`, `README.md`
- `bin/` and `obj/` are gitignored and present locally only

### 4.2 User-Supplied ZIP (src/src.zip)

- File: `src/src.zip` (untracked, not committed)
- Contains: 117 build artifact entries including compiled DLLs, PDB files, MSBuild cache
- Classification: **REPO_CLEAN_BUT_USER_ZIP_DIRTY**
- Impact: Repository integrity is maintained; the ZIP is a local review artifact
- Action: When re-creating review ZIPs, run exclusion filters before packaging

---

## 5. Recommended ZIP Creation Pattern

To create a clean source review ZIP from the repository:

```bash
# From repository root — example for src/net/fods/
zip -r source-review-fods.zip src/net/fods/ \
  --exclude "*/bin/*" \
  --exclude "*/obj/*" \
  --exclude "*/__pycache__/*" \
  --exclude "*.pyc" \
  --exclude "*.nupkg" \
  --exclude "*.snupkg"
```

Or use `git archive` for a clean tarball from committed source only:

```bash
git archive HEAD:src/net/fods/ --format=zip -o source-review-fods.zip
```

---

## 6. Evidence Bundle Exclusions

Evidence bundles built by `tools/evidence/build_evidence_bundle.py` already exclude:

- `.local/` (contains spec-cache, evidence bundles, local artifacts)
- `bundle-metadata/` (staging area)
- `bin/`, `obj/` (gitignored)
- `__pycache__/` (gitignored)

These exclusions are enforced by the bundle validator and the `.gitignore`-based
file inclusion logic in `build_evidence_bundle.py`.

---

## 7. Lane G Verdict

```
LANE_G_VERDICT: LANE_G_PASS
repo_clean: true
gitignore_adequate: true
user_zip_dirty: true (src/src.zip — local artifact, not committed)
action_taken: documented policy; no .gitignore changes required
```
