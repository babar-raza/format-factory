# Mainstream POC Mega-Train Prompt Template

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-MAINSTREAM-POC-MEGA-TRAIN-{{ITERATION}}
- Stream: Mainstream Product
- Date: {{DATE}}
- Iteration: {{ITERATION}} of {{MAX_ITERATIONS}}
- Previous sprint: {{PREVIOUS_SPRINT_ID}} (verdict: {{PREVIOUS_VERDICT}})

## Mission
Build real product capability across the POC target products. Continue until POC_READY_CANDIDATE or hard blocker.

## Product-First Purpose
Produce measurable capability breadth across:
- Commercial .NET: FODS, FODT, Netpbm
- Reduced/FOSS: ZST, Python Netpbm (PBM/PGM/PPM), SYLK, DIF

{{SPECIFIC_PRODUCT_GOALS}}

## Allowed Paths (this iteration)
{{ALLOWED_PATHS}}

## Forbidden Paths (always)
- src/net/* — unless assigned to this lane
- src/python/* — unless assigned to this lane
- .vscode/mcp.json
- .supervisor/policies.yaml
- registry/format-registry.yaml (read-only)

## Hard PASS Quota
- Minimum {{PASS_QUOTA}} new product capabilities with tests
- At least 2 product tracks must receive work
- Evidence repair does not count

## Preflight (MANDATORY)
1. Read reports/supervisor/session-resume.md
2. Read product-capability-matrix/poc-targets.yaml
3. Read reports/supervisor/next-sprint.md
4. Read relevant source files before modifying
5. Check .supervisor/skill-registry.yaml for governed skills

## Lane Ownership (this iteration)
{{LANE_OWNERSHIP_MAP}}

## Cross-Stream Dependencies
{{CROSS_STREAM_DEPENDENCIES}}

## Machinery Status
- Ruflo mode: {{RUFLO_MODE}}
- Acceleration handoffs available: {{ACCELERATION_HANDOFFS}}
- Skills available: {{AVAILABLE_SKILLS}}

## Execution Waves

### Wave 1: Product Source Changes
- Implement APIs/features in assigned src/ paths
- Map each change to capability matrix entry
- Use governed skills where available

### Wave 2: Tests and Examples
- Write tests for every new capability
- Create examples/ entries where appropriate
- Run tests to confirm PASS

### Wave 3: Package and Dogfood
- Verify package proof (build, install, import)
- Create dogfood examples
- Update capability matrix

### Wave 4: Evidence and Closeout
- Write evidence declaration YAML
- Run supervisor pipeline
- Report changed files and test results
- Update POC readiness dashboard

## Continuation Decision
After closeout, ask Supervisor:
- POC_READY_CANDIDATE → stop and report to user
- CONTINUE_NEXT_ITERATION → read next-sprint.md and proceed
- CONTINUE_WITH_REROUTE → skip blocked lanes, proceed with available lanes
- STOP_EXTERNAL_GATE → stop and report blocker to user
- STOP_UNSAFE_WORKSPACE → stop immediately and report

## Hard Prohibitions
- No git push, commit, or publication without explicit user authorization
- No Gate 8 or Gate 11 approval
- No machinery-only work claiming product credit
- No external tool installation

## Allowed Verdicts
1. MAINSTREAM_PRODUCT_BREADTH_PASS — quota met, 2+ product tracks covered
2. MAINSTREAM_PRODUCT_PARTIAL — some capabilities added, breadth insufficient
3. MAINSTREAM_PRODUCT_BLOCKED — hard blocker reached
4. POC_READY_CANDIDATE — all products green

## Final Response Contract
- Exact verdict
- New capabilities per product
- Test results (passed/failed/skipped)
- Changed files
- Capability matrix updates
- Evidence declaration path
- Review package absolute path and SHA-256
- Continuation decision
- Explicit: no commit, no push, no publication unless authorized
