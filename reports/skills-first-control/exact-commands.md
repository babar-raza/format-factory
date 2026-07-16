# Exact commands run (key)
```
# Audit + gate (fail-closed)
.venv/Scripts/python -m tools.governance.skills_first.audit --write
.venv/Scripts/python tools/governance/validate_skills_first_control.py

# Resolution
.venv/Scripts/python -m tools.governance.skills_first.resolve --operation "<op>" --paths <p>...

# Execution manifest
.venv/Scripts/python -m tools.governance.skills_first.manifest create --task-id <T> --agent-type CLAUDE_CODE --operation "<op>" --skill <id> --allowed-paths <globs> --write

# Closeout gate
.venv/Scripts/python -m tools.governance.skills_first.closeout --manifest <execution_id> --changed-files <files> --evidence <paths> --close

# Tests
.venv/Scripts/python -m pytest tests/governance/test_skills_first_*.py -q

# Regression: existing tooling
.venv/Scripts/python tools/supervisor/sync_skill_command_registry.py   # -> 0 flags (orphans healed)
.venv/Scripts/python tools/supervisor/skill_inventory.py               # -> 188 entries
```
