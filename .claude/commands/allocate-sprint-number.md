# /allocate-sprint-number

Allocate an atomic, strictly-monotonic sprint number for a new sprint.

## Usage

```bash
python tools/supervisor/sprint_number_allocator.py allocate \
  --semantic-alias "<alias>" \
  --mission-id "<mission-id>" \
  [--plan-id "plans/.claude/<plan>.md"]
```

## Behavior

- Idempotent: repeating the same `--semantic-alias` returns the original allocation (exit 2)
- Atomic: uses `os.replace()` + module-level `threading.Lock()` for crash-safe writes
- Receipt written to `.local/supervisor/sprint-receipts/<SPRINT-NNNNN>.json`
- Ledger at `.local/supervisor/sprint-ledger.json`

## Exit Codes

- 0: newly allocated
- 1: error
- 2: already allocated (idempotent — not an error)

## Other Commands

```bash
# Check ledger status
python tools/supervisor/sprint_number_allocator.py status

# List recent allocations
python tools/supervisor/sprint_number_allocator.py list [--n 10]

# Recover from interrupted allocation
python tools/supervisor/sprint_number_allocator.py recover --sprint-id SPRINT-NNNNN
```

## Implementation

- `tools/supervisor/sprint_number_allocator.py`
- Tests: `tests/supervisor/test_sprint_number_allocator.py` (9 tests)
- Skill: `allocate-sprint-number` in `.supervisor/skill-registry.yaml`
