# Supervisor Packet Generation

**Script:** `tools/supervisor/generate_supervisor_packet.py`
**Role:** Assembles all next-sprint artifacts from evidence review output + contradiction data.
**Authority:** Advisory only — all generated content is INPUT to the next sprint, not a gate approval.

---

## Overview

`generate_supervisor_packet.py` is the fourth step in the Local Supervisor Control Plane pipeline:

```
discover_latest_evidence.py
  → validate_evidence_for_supervisor.py  (produces evidence-review.json)
    → compare_goal_to_evidence.py        (produces contradictions.json)
      → generate_supervisor_packet.py    (produces 5 output files)
        → sync_local_memory.py
```

It reads `evidence-review.json` and `contradictions.json` from `reports/supervisor/`, then writes
five output files to the same directory:

| Output file | Purpose |
|-------------|---------|
| `next-sprint.md` | Full Claude Code prompt for the next sprint |
| `next-sprint-taskmaster.json` | Task Master import payload (schema-validated) |
| `next-ruflo-lanes.json` | Ruflo lane plan (schema-validated) |
| `approval-gates.md` | Gate classifications, mode-aware MCP status |
| `session-resume.md` | Briefing for a fresh Claude Code session |

No external API calls are made. All assembly is deterministic and local.

---

## Feature 1: JSON Schema Validation with Fallback

### Function
`validate_against_schema(data: dict, schema_path: Path) -> list[str]`

### Purpose
Validates generated JSON payloads (`next-sprint-taskmaster.json`, `next-ruflo-lanes.json`)
against their JSON Schema files in `.supervisor/schemas/`. Returns a list of error strings;
an empty list means valid.

### Two-tier validation strategy

**Tier 1 — `jsonschema` library (primary)**

When the `jsonschema` package is importable, full Draft-7 validation is performed:

```python
import jsonschema
jsonschema.validate(instance=data, schema=schema)
```

- Validates all structural constraints (types, enums, minItems, additionalProperties).
- Returns the `ValidationError.message` on failure.
- Returns `[]` on success.

**Tier 2 — Manual required-field check (fallback)**

When `jsonschema` is not installed (e.g. running with system `python3` instead of
`.local/venv/Scripts/python`), the function falls back to a minimal structural check:

1. Reads the schema file from `schema_path`.
2. Checks every field listed in `schema["required"]` is present in `data`.
3. Checks every field listed in `schema["properties"]["tasks"]["items"]["required"]`
   is present in each element of `data["tasks"]`.
4. If no errors are found, emits an advisory message to stderr:
   ```
   NOTE: jsonschema library not found; manual required-field check used.
   For full validation run with .local/venv/Scripts/python.
   ```
5. Returns `[]` when all required fields are present (not an error condition).

### Edge cases

| Situation | Behaviour |
|-----------|-----------|
| `jsonschema` installed, schema valid, data valid | Returns `[]`; no stderr output |
| `jsonschema` installed, data invalid | Returns list with one error message |
| `jsonschema` not installed, all required fields present | Returns `[]`; advisory to stderr |
| `jsonschema` not installed, required field missing | Returns error list; no stderr note |
| Schema file missing | Returns `["Schema file not found — skipping validation"]` |
| Schema file unreadable / not valid JSON | Returns error describing the parse failure |

### Integration

Called in `main()` immediately after each JSON payload is assembled:

```python
tm_errors = validate_against_schema(tm_data, schema_dir / "next-sprint-taskmaster.schema.json")
ruflo_errors = validate_against_schema(ruflo_data, schema_dir / "next-ruflo-lanes.schema.json")
```

Validation errors are printed as a suffix to the output line but do NOT cause a non-zero exit
code (they are warnings). Schema files live in `.supervisor/schemas/` and are tracked in git.

### Recommendation

Use `.local/venv/Scripts/python` for authoritative runs to get full schema validation.
The fallback covers required-field presence only; type and enum constraints are not checked
without `jsonschema`.

---

## Feature 2: Sprint-Specific Task Synthesis

### Overview

Instead of emitting a single generic "Continue next mega-train sprint" task, the script reads
live repo state and synthesises contextual tasks for each run. The task list changes every
sprint as gate states, taskcards, and uncommitted files change.

### Helper functions

#### `read_current_mode(repo_root: Path) -> int`

Reads the current MODE number from `.supervisor/config.yaml`.

- Looks for the pattern `Status: MODE N` (case-insensitive) in the config file.
- Returns the integer N, or 0 if the line is absent or the file does not exist.
- Used by `generate_approval_gates_md()` and `generate_session_resume_md()`.

#### `read_registry_gate_states(repo_root: Path) -> dict`

Reads `registry/format-registry.yaml` to find formats with incomplete high-number gates.

**Registry YAML structure handled:**

```yaml
formats:
  - format_id: fods
    gates:
      gate_11:
        status: commercial_readiness_in_progress
  - format_id: fodt
    ...
```

The YAML is parsed with a line-by-line state machine (not a full YAML parser) to avoid
adding a `pyyaml` dependency. Key regex detail: format_id lines use the list-item
syntax `  - format_id: fods`, so the pattern is:

```python
re.match(r"\s+(?:-\s+)?format_id:\s+(\S+)", line)
```

The `(?:-\s+)?` optional group handles the `- ` list marker that sits between the leading
spaces and the `format_id:` key.

**Filtering:** Only formats with at least one gate numbered >= 10 in a non-terminal state
are returned. Terminal states excluded from results: `passed`, `not_applicable`, `waived`.

**Returns:** `{format_id: {gate_N: status}}` for matching formats.

#### `read_open_taskcards(repo_root: Path, limit: int = 5) -> list[dict]`

Scans `taskcards/*.md` for open work items.

- A taskcard is considered open if `**Status:**` matches one of:
  `not_started`, `in_progress`, `open`, `pending`.
- Extracts the taskcard ID (filename stem) and title (first `# H1` line).
- Returns up to `limit` entries sorted by filename (alphabetical).
- Silently skips files that cannot be read.

#### `synthesize_sprint_tasks(review, contradictions, repo_root) -> list[dict]`

Combines the three data sources above into a TM-schema-compatible task list.

**When critical contradictions exist:**
Returns one REPAIR task per CRITICAL contradiction. The list is short-circuited — no
gate or taskcard tasks are added until contradictions are resolved.

**When no critical contradictions exist:**

Tasks are assembled in this order:

| Priority | Source | Condition | Status | Blocker |
|----------|--------|-----------|--------|---------|
| 1 | `git status --short` | Modified tracked product files (`src/`, `state/`, `packaging/`) | `approval-blocked` | `human_approval` |
| 2 | Registry gate states | Incomplete gates >= 10 (commercial_readiness_in_progress) | `approval-blocked` | `human_approval` |
| 2 | Registry gate states | Incomplete gates >= 10 (other non-terminal states) | `blocked` | `external_gate` |
| 3 | Open taskcards | Status: not_started / in_progress / open / pending | `pending` | (none) |
| 4 | Always | Evidence bundle task | `pending` | (none) |

Up to 3 gate tasks and 3 taskcard tasks are included. Task IDs are sequential (`TASK-001`,
`TASK-002`, ...).

**Fallback:** If no tasks are generated (no modified files, no incomplete gates, no open
taskcards), a single generic task "Continue next mega-train sprint" is returned pointing to
`plans/master-plan.md`.

**Task schema fields populated:**

| Field | Notes |
|-------|-------|
| `task_id` | Sequential `TASK-NNN` or `REPAIR-NNN` |
| `title` | Human-readable description |
| `description` | Context from source data |
| `status` | One of the enum values from the TM schema |
| `ff_gate_ref` | Set for gate tasks: `{format}_{gate}` |
| `ff_taskcard_ref` | Set for taskcard tasks: taskcard stem |
| `ff_doc_ref` | Always set: `plans/master-plan.md` or specific path |
| `supervisor_task_ref` | Set for known supervisor task references |
| `acceptance_evidence` | Verifiable acceptance condition |
| `validation_command` | Exact command to confirm completion |
| `blocker_type` | Set when `status` is `blocked` or `approval-blocked` |
| `non_authoritative` | Always `true` — these tasks are advisory |
| `lane` | Lane assignment: C2 (repair), C3 (implementation), C6 (evidence) |

---

## Feature 3: Mode-Aware Approval Gates

### Function
`generate_approval_gates_md(review: dict, contradictions: dict, current_mode: int) -> str`

### Purpose
Produces `reports/supervisor/approval-gates.md` — a human-readable classification of
what actions require human approval vs. can proceed autonomously.

The content changes based on the current MODE, reflecting the actual state of MCP activation
rather than always showing a pending gate.

### Mode-dependent content

#### MCP activation row (in the Pending Actions table)

| MODE | Row content |
|------|-------------|
| < 4 | `\| MCP activation \| stop-mcp-activation-required \| User \|` |
| >= 4 | `\| MCP activation (MODE 4 ACTIVE — .vscode/mcp.json present) \| autonomous-continue \| already-done \|` |

#### NEXT_HUMAN_GATE line (in Summary section)

| MODE | Line content |
|------|-------------|
| < 4 | `NEXT_HUMAN_GATE: MODE 4 MCP activation (explicit user approval required)` |
| >= 4 | `NEXT_HUMAN_GATE: MODE 5 autonomous sprint loop (explicit user approval required)` |

#### MCP_STATUS line (in Summary section)

| MODE | Line content |
|------|-------------|
| < 4 | `MCP_STATUS: NOT_ACTIVATED (MODE < 4)` |
| >= 4 | `MCP_STATUS: ACTIVE (task-master-ai@0.43.1, claude-flow@3.10.14 in .vscode/mcp.json)` |

### Mode label in header

The header includes a human-readable label for the current mode:

```
Current Mode: MODE 4 (ACTIVE_MCP_ACTIVATION)
Current Mode: MODE 5 (AUTONOMOUS_SPRINT_LOOP_RC)
```

### How current_mode is passed

`main()` calls `read_current_mode(repo_root)` once and passes the result to both
`generate_approval_gates_md()` and `generate_session_resume_md()`:

```python
current_mode = read_current_mode(repo_root)
# ...
gates_text = generate_approval_gates_md(review, contradictions, current_mode)
resume_text = generate_session_resume_md(review, contradictions, memory_snippet, current_mode)
```

### When critical contradictions exist

The Pending Actions table is replaced by a repair-focused table regardless of mode:

```
| Repair N CRITICAL contradictions | local-repair-loop | Claude_Code |
| Continue to next sprint | stop-contradictions-present | Claude_Code (after repair) |
```

The mode-aware MCP row is suppressed in this case — no advancement decisions are
relevant until contradictions are resolved.

---

## Usage and CLI

```bash
# Default (reads reports/supervisor/evidence-review.json + contradictions.json)
python tools/supervisor/generate_supervisor_packet.py

# Explicit input paths
python tools/supervisor/generate_supervisor_packet.py \
  --review reports/supervisor/evidence-review.json \
  --contradictions reports/supervisor/contradictions.json \
  --output-dir reports/supervisor \
  --repo-root .
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success — all 5 files written, no critical contradictions |
| 3 | Critical contradictions present — next-sprint focuses on repair |
| 9 | Unexpected error |

### Standard output on success

```
PACKET_GENERATION: COMPLETE
  Output dir: reports/supervisor
  next-sprint.md: written (8 tasks synthesized)
  next-sprint-taskmaster.json: written (schema OK)
  next-ruflo-lanes.json: written (schema OK)
  approval-gates.md: written (mode 4: MCP ACTIVE)
  session-resume.md: written
```

If `jsonschema` is absent, an advisory note appears on stderr:
```
NOTE: jsonschema library not found; manual required-field check used.
For full validation run with .local/venv/Scripts/python.
```

---

## Idempotence

Running the script twice with the same inputs produces identical output files.
The only non-deterministic field is the `timestamp` in JSON payloads and the
`Generated:` lines in Markdown files, which are ISO 8601 wall-clock timestamps.

The `sprint_id` field in JSON exports uses the wall-clock timestamp of the run
(`supervisor-export-YYYYMMDD-HHMMSS`), not the source evidence sprint ID.
This allows multiple export runs from the same evidence to be distinguished.

---

## Schema Files

| Schema | Validates |
|--------|----------|
| `.supervisor/schemas/next-sprint-taskmaster.schema.json` | `next-sprint-taskmaster.json` |
| `.supervisor/schemas/next-ruflo-lanes.schema.json` | `next-ruflo-lanes.json` |

Both schemas are self-contained (no `$ref` to external URLs) and tracked in git.
Schema fields: `sprint_id` (required), `timestamp` (required), `verdict` (required),
`tasks[]` or `lanes[]` with per-item required fields.

---

## Related Files

| File | Role |
|------|------|
| `tools/supervisor/compare_goal_to_evidence.py` | Produces `contradictions.json` consumed here |
| `tools/supervisor/sync_local_memory.py` | Runs after this script; reads `next-sprint.md` |
| `tools/supervisor/supervisor_loop.py` | Orchestrates the full pipeline |
| `.supervisor/config.yaml` | Source of current MODE number |
| `registry/format-registry.yaml` | Source of gate states for task synthesis |
| `taskcards/*.md` | Source of open taskcard work items |
| `docs/automation/local-supervisor-control-plane.md` | Overall supervisor architecture |
