# 01 - LOC and Classification Report

## Reproducible LOC Measurements

All measurements at commit `6b3f6f07` on branch `main`, 2026-07-06.
Method: `find <dir> -name "*.py" -not -path "*/__pycache__/*" -exec cat {} + | wc -l`
(Physical LOC, all lines including blanks and comments.)

### Product Code

| Directory | Files | LOC | Language |
|---|---|---|---|
| `src/python/` | 409 | 49,483 | Python |
| `src/net/` | 173 | 22,643 | C# |
| **Product Total** | **582** | **72,126** | |

#### Python Product by Format (20 formats + shared)

| Format | LOC | Files |
|---|---|---|
| fodt | 5,263 | 42 |
| fods | 4,903 | 52 |
| ods | 2,974 | 22 |
| ndjson | 2,674 | 17 |
| abw | 2,639 | 19 |
| fodg | 2,572 | 18 |
| gnumeric | 2,508 | 16 |
| dif | 2,506 | 17 |
| csv | 2,485 | 19 |
| zst | 2,401 | 16 |
| tsv | 2,205 | 16 |
| sylk | 2,199 | 17 |
| ppm | 1,969 | 16 |
| pbm | 1,860 | 18 |
| qoi | 1,826 | 17 |
| pgm | 1,792 | 15 |
| toml | 1,779 | 17 |
| xcf | 1,773 | 17 |
| odt | 1,544 | 19 |
| fodp | 1,504 | 15 |
| _shared | 107 | 4 |

#### .NET Product by Format (10 formats)

| Format | LOC | Files |
|---|---|---|
| fods | 10,197 | 55 |
| fodt | 6,008 | 34 |
| netpbm | 2,849 | 17 |
| csv | 1,377 | 11 |
| ndjson | 603 | 13 |
| zst | 535 | 10 |
| tsv | 506 | 12 |
| html | 242 | 7 |
| markdown | 170 | 7 |
| txt | 156 | 7 |

### Machinery Code

| Directory | Files | LOC | Notes |
|---|---|---|---|
| `tools/supervisor/` | 262 | 85,469 | Core autonomous machinery |
| `tools/evidence/` | 15 | 21,396 | Evidence sprint writers + validation |
| `tools/skills/` | 25 | 8,304 | Skill execution infrastructure |
| `tools/specification-authority-layer/` | 24 | 5,874 | SAL ingestion |
| `tools/requirements_authority/` | 17 | 4,465 | Requirement validation |
| `tools/ai/` | 43 | 4,327 | AI/LLM integration |
| `tools/spec-normalize/` | 13 | 4,286 | Spec normalization |
| `tools/capability_layer/` | 8 | 4,260 | Capability mapping |
| `tools/oracle/` | 11 | 3,728 | Oracle validation |
| `tools/certification/` | 14 | 3,009 | Assertion quality analysis |
| `tools/playbook/` | 9 | 2,788 | Playbook governance |
| `tools/docs/` | 8 | 2,762 | Documentation generation |
| `tools/validators/` | 8 | 2,161 | Additional validators |
| Other `tools/` subdirs | 103 | 21,239 | 20 smaller directories |
| **tools/ Total** | **560** | **174,068** | |

#### Configuration & Governance Infrastructure

| Directory | Files | LOC | Notes |
|---|---|---|---|
| `.supervisor/` | 183 | 39,351 | Skill registry, schemas, prompts, state |
| `.claude/commands/` | 125 | 12,645 | Claude Code command definitions |
| `schemas/` | — | 6,371 | JSON/YAML schemas |
| `.governance/` | — | 2,193 | Capability registry, governance config |
| `registry/` | 42 | 15,919 | Format registry, baselines, lane scopes |
| **Config Total** | | **76,479** | |

### Tests

| Directory | Files | LOC | Notes |
|---|---|---|---|
| `tests/python/` | 2,307 | 240,892 | Format-specific Python tests |
| `tests/supervisor/` | 409 | 92,188 | Supervisor/governance tests |
| `tests/evidence/` | 156 | 21,632 | Evidence pipeline tests |
| `tests/skills/` | 38 | 10,222 | Skill tests |
| `tests/ai/` | 33 | 6,600 | AI integration tests |
| Other `tests/` subdirs | 152 | 24,658 | Packaging, playbook, SAL, etc. |
| **Tests Total** | **3,095** | **396,192** | |

### Documentation

| Directory | LOC | Notes |
|---|---|---|
| `docs/` (markdown) | 40,890 | Architecture, standards, guides |

## Summary Ratios

| Ratio | Value | Interpretation |
|---|---|---|
| **Machinery (tools/) : Product** | **2.41 : 1** | Machinery is 2.4x product code |
| **Machinery (tools/ + config) : Product** | **3.47 : 1** | Including config, 3.5x product |
| **Tests : All Production** | **1.61 : 1** | Tests are 1.6x all production code |
| **Supervisor tests : Supervisor code** | **1.08 : 1** | Tests slightly exceed implementation |
| **Product tests : Product code** | **3.34 : 1** | 3.3 test lines per product line |

## Assessment of Original 81K:72K Claim

### Verdict: **PARTIALLY_ACCURATE**

**What was correct:**
- Product code at ~72K LOC is accurate (actual: 72,126)
- `tools/supervisor/` at ~81K LOC is close (actual: 85,469)

**What was misleading:**
- The comparison used only `tools/supervisor/` as "machinery" — but this is only 49% of `tools/` (174K total)
- It excluded `tools/evidence/` (21K), `tools/skills/` (8K), `tools/ai/` (4K), `tools/oracle/` (4K), and 15 other tooling directories totaling 89K additional LOC
- It excluded configuration infrastructure (`.supervisor/` 39K, `.claude/commands/` 13K, `schemas/` 6K, `registry/` 16K, `.governance/` 2K) totaling 76K LOC
- The true machinery-to-product ratio is 2.4:1 (tools only) or 3.5:1 (tools + config), not 1.13:1

**Why this matters:**
The 1.13:1 framing suggested machinery was slightly larger than product. The actual ratio of 2.4:1-3.5:1 tells a fundamentally different story: the factory infrastructure is the dominant codebase component by a significant margin. This is not inherently problematic — factory code amortizes across formats — but it changes the maintenance calculus.

## Notable File Families (Duplication Indicators)

| Family | Files | Total LOC | Pattern |
|---|---|---|---|
| Evidence sprint writers (run046-050) | 5 | 15,540 | Versioned snapshots; likely only run050 active |
| Governance validators (*) | 18 | 10,908 | Accretive extension files (ext, ext2, ext3, ext4) |
| Autonomous-* family | 10 | 9,964 | Multiple orchestration entry points |
| Validate-* family | 17 | 5,122 | Separate from governance_validators |
| Generate-* family | 12 | ~8,000 | Prompt/packet/sample generation |
| Build-* family | 5 | ~2,000 | Evidence/context/proof building |

These families account for ~51K LOC (~30% of tools/) and represent the primary consolidation investigation targets.

## Largest Files (Potential Monoliths)

| File | LOC | Functions | Responsibility |
|---|---|---|---|
| `tools/evidence/run050_sprint_writer.py` | 4,116 | — | Evidence bundle generation |
| `tools/supervisor/governance_validators.py` | 3,183 | 53 | Core governance validators |
| `tools/evidence/run048_sprint_writer.py` | 3,103 | — | Evidence sprint writer |
| `tools/evidence/run046_sprint_writer.py` | 2,922 | — | Evidence sprint writer |
| `tools/evidence/run047_sprint_writer.py` | 2,709 | — | Evidence sprint writer |
| `tools/evidence/run049_sprint_writer.py` | 2,690 | — | Evidence sprint writer |
| `tools/supervisor/autonomous_cycle.py` | 2,651 | 4 | Main autonomous loop |
| `tools/evidence/validate_evidence_bundle.py` | 2,638 | — | Evidence validation |
| `tools/supervisor/autonomous_task_generator.py` | 1,920 | 8 | Task generation |
| `tools/capability_layer/capability_map_generator.py` | 1,721 | — | Capability mapping |
