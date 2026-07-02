---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Meta-skill: proves idempotency of other skills"
loc_budget: "<90 lines"
test_path: "tests/supervisor/test_run_skill_idempotency.py"
---

# /run-skill-idempotency

For a given Python-backed tool path, run it twice against the same fixture
and produce an idempotency verdict.

## Purpose

Mechanically prove that a Python-backed skill produces identical output when run
twice on unchanged input. Required for Pilot A and any new skill registration claiming
deterministic behavior.

**SCOPE LIMITATION (explicit):** This skill applies ONLY to Python-backed tools in
`tools/supervisor/` that produce deterministic file outputs. Prompt-backed `.md` skills
are LLM-driven and cannot be proven idempotent via output comparison. Prompt-backed
skills are evaluated structurally (contract completeness), not by output identity.

## Steps

1. Run the target tool with `--output {run1_path}`
2. Run the target tool again with `--output {run2_path}`
3. Compare the two output files byte-for-byte
4. Write proof to `.supervisor/skill-idempotency-proof.yaml`

```bash
python tools/supervisor/run_skill_idempotency.py \
  --skill-id <skill_id> \
  --tool-path <path_to_tool.py> \
  --output-path <tool_native_output_path> \
  --run1-path .local/evidences/{run_id}/idempotency-run1.yaml \
  --run2-path .local/evidences/{run_id}/idempotency-run2.yaml
```

## Output

`.supervisor/skill-idempotency-proof.yaml` with:
- `skill_id`, `tool_path`
- `outputs_identical`: true/false
- `idempotency_verdict`: IDEMPOTENT_VERIFIED | NON_IDEMPOTENT_REPAIR_REQUIRED
- `scope_limitation`: explicit note about prompt-backed exclusion

## Acceptance

`idempotency_verdict: IDEMPOTENT_VERIFIED` — zero diff between run 1 and run 2.

## Allowed Paths

- `.supervisor/skill-idempotency-proof.yaml` (write)
- `.local/evidences/{run_id}/` (write run outputs)
- `tools/supervisor/` (execute target tools)

## Forbidden Paths

- `src/**`
- Running on prompt-backed `.md` skills

## Constraints

- Tool must produce deterministic output (no timestamps, no UUIDs in output)
- On exit code != 0 from either run: verdict is NON_IDEMPOTENT_REPAIR_REQUIRED

## Idempotency Contract

Proof itself is deterministic: same tool + same input = same verdict.

## Error Handling

On tool execution failure: write NON_IDEMPOTENT_REPAIR_REQUIRED with error detail.

## Usage

```
/run-skill-idempotency
```

## Output Format

- Generated artifact written to the configured output path
- Confirmation message: file path and size
- Validation result confirming the output is well-formed
