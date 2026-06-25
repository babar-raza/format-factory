# Review Methodology
# Expert Manual System Review — Format Factory

## Guiding Principle: System-First, Source-Verified

Every product weakness is treated as a potential system symptom before being treated as an isolated
product defect. The review follows this sequence for every confirmed problem:

```
1. Observe product weakness
2. Inspect source directly (never trust sprint claims alone)
3. Ask: which system component produced, validated, or allowed this weakness?
4. Confirm system gap root cause
5. Design system healing path
6. Design product healing path THROUGH the healed system
7. Add recurrence prevention (validator, gate, test, authority rule)
8. Only then mark the problem closed
```

## Source Inspection Standard

- Read source files directly, not sprint summaries
- Check LOC, public API surface, test file count, test name quality
- Compare poc-targets.yaml PASS claims against src/ reality
- Identify "prototype" or "design_complete_in_progress" labels in source comments vs. PASS in authority
- Check for architecture stubs (files with `# GENERATED — architecture_only` or `pass` as sole body)
- Identify analytics masquerade (files named `*_document.py` or `*_stats.py` that contain analytics functions)

## Test Quality Dimensions

Not all tests are equal. For each format, classify tests as:

- **Smoke** — imports package, checks a property is not None
- **Behavioral** — verifies specific values, behaviors, edge cases
- **Roundtrip** — load → edit → save → reload → verify
- **Malformed input** — feed broken files and verify exception handling
- **Installed** — runs from installed wheel, not editable install
- **Export physical** — produces a file, checks the file is non-empty or parseable

Commercial readiness requires: behavioral + roundtrip + malformed + export physical.

## Authority Hierarchy

When claims conflict:

| Layer | Trust Level | Notes |
|-------|-------------|-------|
| `src/` source code | HIGHEST | Only truth for what the product actually does |
| Test results | HIGH | Verifies behavior, but tests can be shallow |
| `poc-targets.yaml` | MEDIUM | Self-declared, requires source verification |
| Sprint evidence bundles | MEDIUM | Self-declared, grader may be unavailable |
| `session-resume.md` | LOW | Generated summary, may lag source reality |
| `next-sprint.md` | LOW | Advisor, not authority |
| Memory files (.supervisor/project-memory.md) | LOW | Sprint notes, not verified against HEAD |

## Rubric Application Method

For each product, scores are derived from direct observation:

1. **Open the source files** — not just __init__.py
2. **Count public API methods** — from the actual class or module, not documentation
3. **Read at least 3 test files** — look for behavioral assertions, not just import checks
4. **Check examples** — can a developer run the example and get real output?
5. **Try the installed flow** — is the package installable from wheel?

## System Layer Evaluation

For each system layer (Supervisor, Skills, SAL, Gap Ledger, Evidence):

1. **What does it claim to enforce?** — Read the layer's own docs/code
2. **What does it actually enforce?** — Look for enforcement at code level
3. **What bypasses it?** — Look for "skip", "best-effort", "advisory" labels
4. **Does it prevent recurrence?** — Look for validators, gates, tests
5. **Does it produce actionable output?** — Check that its outputs can guide the next sprint

## Known Biases to Guard Against

- **Sprint success bias**: A sprint ACCEPTED does not mean the product quality is commercial-ready
- **Test count bias**: 93 test files does not mean 93 behavioral tests
- **LOC cap bias**: Files at LOC cap are not necessarily well-structured — they may be bloated with analytics
- **Gate approval bias**: Gate 11 G11-G approval is a business decision, not a code quality certificate
- **Continuation bias**: AUTONOMOUS_CONTINUE=YES means the pipeline is not blocked, not that the products are complete
