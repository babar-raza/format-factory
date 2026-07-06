# Evidence: Commands and Results

All commands executed during the investigation at commit `6b3f6f07` on branch `main`.

## Baseline Commands

```bash
git rev-parse --short HEAD
# Result: 6b3f6f07

git branch --show-current
# Result: main

git ls-files | wc -l
# Result: 15731
```

## LOC Measurement Commands

```bash
# tools/supervisor/ (recursive)
find tools/supervisor -name "*.py" -not -path "*/__pycache__/*" | wc -l
# Result: 262 files
find tools/supervisor -name "*.py" -not -path "*/__pycache__/*" -exec cat {} + | wc -l
# Result: 85469 LOC

# tools/ total
find tools -name "*.py" -not -path "*/__pycache__/*" | wc -l
# Result: 560 files
find tools -name "*.py" -not -path "*/__pycache__/*" -exec cat {} + | wc -l
# Result: 174068 LOC

# src/python/
find src/python -name "*.py" -not -path "*/__pycache__/*" -not -path "*/build/*" -not -path "*egg-info*" | wc -l
# Result: 409 files
find src/python -name "*.py" -not -path "*/__pycache__/*" -not -path "*/build/*" -not -path "*egg-info*" -exec cat {} + | wc -l
# Result: 49483 LOC

# src/net/
find src/net -name "*.cs" | wc -l
# Result: 173 files
find src/net -name "*.cs" -exec cat {} + | wc -l
# Result: 22643 LOC

# tests/
find tests -name "*.py" -not -path "*/__pycache__/*" | wc -l
# Result: 3095 files
find tests -name "*.py" -not -path "*/__pycache__/*" -exec cat {} + | wc -l
# Result: 396192 LOC

# .supervisor/
find .supervisor -type f | wc -l
# Result: 183 files
find .supervisor -type f -exec cat {} + | wc -l
# Result: 39351 LOC

# registry/
find registry -type f | wc -l
# Result: 42 files
find registry -type f -exec cat {} + | wc -l
# Result: 15919 LOC

# .claude/commands/
find .claude/commands -type f | wc -l
# Result: 125 files
find .claude/commands -type f -exec cat {} + | wc -l
# Result: 12645 LOC

# .governance/
find .governance -type f -exec cat {} + | wc -l
# Result: 2193 LOC

# schemas/
find schemas -type f -exec cat {} + | wc -l
# Result: 6371 LOC

# docs/ (markdown)
find docs -type f -name "*.md" -exec cat {} + | wc -l
# Result: 40890 LOC
```

## File Family Analysis Commands

```bash
# Evidence sprint writers
wc -l tools/evidence/run04[6-9]_sprint_writer.py tools/evidence/run050_sprint_writer.py
# Result: 2922 + 2709 + 3103 + 2690 + 4116 = 15540 total

# Governance validators
wc -l tools/supervisor/governance_validators*.py
# Result: 10908 total across 18 files

# Autonomous family
wc -l tools/supervisor/autonomous_*.py
# Result: 9964 total across 10 files

# Validate family
wc -l tools/supervisor/validate_*.py
# Result: 5122 total across 17 files
```

## Dead Code Analysis Commands

```bash
# Zero-import files (top-level tools/supervisor/*.py)
for f in tools/supervisor/*.py; do
  b=$(basename "$f" .py)
  c=$(grep -rl "from.*${b}\b\|import ${b}\b" tools/ --include="*.py" | grep -v "$f" | grep -v __pycache__ | wc -l)
  [ "$c" -eq 0 ] && echo "ZERO_IMPORTS: $f"
done
# Result: ~60+ files with zero Python imports (many are CLI entry points)

# Files with __main__ guard
grep -rl "if __name__" tools/supervisor/*.py | wc -l
# Result: 142

# Dynamic dispatch patterns
grep -rn "importlib\|__import__" tools/supervisor/ --include="*.py" | grep -v __pycache__
# Result: 15+ dynamic loading sites

# Subprocess call count
grep -rn "subprocess.run\|subprocess.call\|subprocess.Popen" tools/supervisor/ --include="*.py" | grep -v __pycache__ | wc -l
# Result: 56

# Evidence sprint writer references
grep -rl "run050_sprint_writer\|run049_sprint_writer\|run048_sprint_writer\|run047_sprint_writer\|run046_sprint_writer" tools/ tests/ .claude/ .supervisor/ --include="*.py" --include="*.yaml" --include="*.md"
# Result: Only self-references (the 5 files themselves)

# Evidence sprint writer function signature comparison
diff <(grep "^def " tools/evidence/run046_sprint_writer.py) <(grep "^def " tools/evidence/run050_sprint_writer.py)
# Result: Signatures diverged significantly (run046 has write/update/read/validate_sample; run050 has wf/pf/sm/ck/test_*/split_frontmatter/etc.)
```

## Skill Registry and Command References

```bash
# References in .claude/commands/
grep -rl "supervisor/" .claude/commands/ | wc -l
# Result: 10+

# References in skill-registry.yaml
grep -c "supervisor/" .supervisor/skill-registry.yaml
# Result: 50

# References in CLAUDE.md
grep -c "supervisor/" CLAUDE.md
# Result: 24
```
