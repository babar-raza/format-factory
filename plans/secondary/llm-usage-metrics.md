PLAN MODE PROMPT: Production LLM Metrics Discovery and Google Sheet Reporting Design

You are operating in PLAN MODE only.

Your task is to deeply inspect this repository/project and produce a production-grade implementation plan for recording all agent/app activity related to llm.professionalize.com and posting summarized run metrics to the existing Google Sheet append endpoint.

Do not implement code.
Do not modify files.
Do not post to the Google Sheet.
Do not run live production-impacting actions.
Do not commit anything.
Do not assume how this project works. Discover it from the repository.

This is a planning sprint. The goal is to understand the current system, identify whether and how it uses llm.professionalize.com, design the best production-safe metrics solution for this project, and prepare a later execution handoff.

Context
The organization needs a generic metrics reporting pattern across many aspose.org and aspose.net website/family projects. Different projects may have different agents, apps, scripts, pipelines, orchestration systems, CI jobs, LLM clients, local LLM fallbacks, or no current LLM usage at all.

The metrics destination is a production Google Sheet exposed through an append-only Google Apps Script endpoint. Rows can only be added. There is no supported edit, delete, correction, or rollback operation. Because of this, the design must be extremely careful, idempotent, validated, and production-safe.

Agent owner must be hardcoded as:
Babar Raza

Required Google Sheet fields
The final row payload must use exactly these parameter names:

timestamp
agent_name
agent_owner
job_type
run_id
status
product
platform
website
website_section
item_name
items_discovered
items_failed
items_succeeded
run_duration_ms
token_usage
api_calls_count

Endpoint and token handling
The execution handoff will provide the real Google Apps Script endpoint and token.

In the plan, do not print the real token if it exists in the repo, logs, config, or prompt history.
Do not hardcode secrets into source files.
Recommend secret handling through environment variables or existing secret management, for example:

LLM_METRICS_ENDPOINT
LLM_METRICS_TOKEN

The production endpoint must only be called by a controlled metrics reporter after validation gates pass.

Critical production safety rule
Because the Google Sheet is append-only, the system must prevent accidental duplicate rows, malformed rows, production pollution, and repeated test submissions.

In PLAN MODE:
Do not send any POST request.

For the later EXECUTION MODE:
Design a single safe test-post strategy using clearly marked test data, such as:

agent_name: "test"
job_type: "test"
run_id: "test_<project>_<timestamp>_<short_hash>"
status: "test"
product: "test"
platform: "test"
website: "test"
website_section: "test"
item_name: "test"

The execution plan must make it clear that the test row is intentionally marked as test so it can be filtered out from production reporting. The agent must not send repeated test rows unless explicitly required by the execution handoff.

Discovery requirements
Perform a deep repository investigation before proposing any solution.

Inspect all relevant areas, including but not limited to:

1. Project purpose and execution model
   - What does this project do?
   - What websites, families, products, platforms, or sections does it affect?
   - Is it for aspose.org, aspose.net, aspose.com, docs, blog, kb, reference, tutorials, products, examples, or another surface?
   - What are the main commands, scripts, apps, services, agents, or workflows?
   - Is the project CLI-based, web-based, scheduled, CI-based, agent-driven, n8n-driven, or mixed?

2. Current LLM usage
   - Search for llm.professionalize.com.
   - Search for OpenAI-compatible endpoints.
   - Search for Ollama, LiteLLM, Anthropic, Claude, Codex, OpenAI, Gemini, Grok, local models, custom LLM wrappers, HTTP clients, API base URLs, environment variables, model routing, retry logic, and token accounting.
   - Identify all code paths that call LLMs directly or indirectly.
   - Identify whether calls already go through llm.professionalize.com.
   - Identify whether calls bypass llm.professionalize.com.
   - Identify local fallback behavior.
   - Identify places where agent/app run boundaries are created.

3. Existing metrics, logging, and ledgers
   - Search for existing logs, run records, manifests, taskcards, reports, JSONL ledgers, audit files, usage counters, token counters, duration counters, retry counters, API call counters, and status summaries.
   - Identify whether existing artifacts already contain the required Google Sheet fields or can derive them.
   - Identify the most reliable source of truth for run status, item counts, token usage, API call count, and duration.
   - Identify any mismatch between claimed metrics and actual generated evidence.

4. Production workflow
   - Identify where metrics should be captured with the least risk and highest reliability.
   - Prefer one shared metrics reporter or wrapper instead of scattered one-off curl calls.
   - Prefer deterministic derivation from final run summaries instead of fragile log scraping where possible.
   - Ensure reporting happens once per completed run, not once per item unless the project truly requires per-item rows.
   - Design idempotency protection so the same run does not append duplicate rows.

5. Projects that do not currently use llm.professionalize.com
   If no current usage is found, or usage cannot be proven after deep inspection:
   - State this clearly.
   - Do not pretend usage exists.
   - Identify current LLM providers or absence of LLM usage.
   - Provide a migration or adoption plan for routing future LLM load through llm.professionalize.com.
   - Identify the safest integration point.
   - Identify what metrics would become available after migration.
   - Identify what metrics can still be reported today, if any.

Required metric semantics
Define clear production semantics for each field:

timestamp
- UTC timestamp in ISO 8601 format.
- Prefer end-of-run timestamp unless the project already has a canonical run timestamp.

agent_name
- Human-readable name of the agent, app, workflow, or script.
- Must be stable across runs.

agent_owner
- Always "Babar Raza".

job_type
- Stable machine-readable category, for example:
  content_generation
  page_optimization
  reference_generation
  kb_generation
  blog_generation
  validation
  translation
  example_generation
  discovery
  migration
  unknown
- If the project has existing job names, map them cleanly.

run_id
- Globally unique per run.
- Must be deterministic enough to trace back to local evidence.
- Recommended pattern:
  <agent_or_job>_<YYYYMMDD_HHMMSS>_<short_hash>
- Must be persisted locally before posting.
- Must prevent duplicate append attempts.

status
- Use one of:
  success
  partial_success
  failure
  test
- Define exact rules for each status.
- partial_success must be used when at least one item succeeded and at least one item failed, or when the project completed with known non-blocking failures.

product
- Product or family, for example Aspose.Words, Aspose.Cells, Aspose.PDF.
- If multiple products are covered in one run, recommend either:
  1. one row per product, or
  2. product: "multiple" only if per-product metrics cannot be safely split.
- Prefer one row per product/family when metrics can be separated.

platform
- Platform such as .NET, Java, Python, C++, Node.js, Android, Cloud, or "multiple".
- Prefer specific platform when available.

website
- Website/domain such as aspose.org, aspose.net, aspose.com, docs.aspose.com, blog.aspose.com, kb.aspose.com, reference.aspose.com, products.aspose.org.
- Use the project’s actual target.

website_section
- Site section such as Products, Docs, KB, Blog, Reference, Tutorials, Examples, API Reference, Plugin Pages, or unknown.

item_name
- Type of processed item, such as Pages, Articles, Keywords, Examples, Products, Families, Repos, Docs, Claims, References.

items_discovered
- Total number of candidate items discovered or intended for processing.
- Must not be confused with succeeded count.
- If unavailable, use 0 only with explanation, or propose how to collect it.

items_failed
- Number of items that failed final validation or processing.
- Must not exceed discovered unless the project already has a justified retry/failure counting model. If retries are counted separately, explain that and recommend normalizing to item-level failures.

items_succeeded
- Number of items that passed final output or validation.
- Must not exceed discovered unless there is a known reason, such as one discovered item generating multiple outputs. If so, document the relationship.

run_duration_ms
- Wall-clock duration of the complete run in milliseconds.
- Prefer monotonic timer measurement from run start to run end.

token_usage
- Total tokens used if available.
- If provider returns prompt/completion tokens separately, recommend storing total here and preserving detailed breakdown locally.
- If unavailable, leave blank or null according to endpoint behavior, but explain how to add collection later.

api_calls_count
- Count of LLM API calls, preferably calls to llm.professionalize.com.
- Define whether retries count. Recommended:
  api_calls_count = actual HTTP/API attempts, including retries.
  local detailed metrics should separately track successful_calls, failed_calls, retry_count.

Production architecture expectations
Your plan must choose the best integration pattern for this project, but you must evaluate alternatives first.

Evaluate at least these options:

Option A: Central metrics reporter module
- A reusable project-local module/function that validates payloads and posts to the endpoint.
- Best when multiple scripts/agents need shared reporting.

Option B: LLM client wrapper instrumentation
- Capture token usage, API calls, model names, retries, and durations around the LLM client.
- Best when the project has centralized LLM access.

Option C: End-of-run summary reporter
- Read final run manifests, ledgers, validation results, or taskcards and append one row per run/product.
- Best when the project already has reliable run evidence.

Option D: CI/job-level reporter
- Report from GitHub Actions, scheduled tasks, or deployment jobs.
- Best when runs are already orchestrated in CI.

Option E: Hybrid approach
- LLM wrapper captures usage counters.
- End-of-run reporter posts final business metrics.
- Local ledger prevents duplicate posting.

For each option, explain:
- Fit for this repository.
- Benefits.
- Risks.
- Required changes.
- Testability.
- Production safety.
- Why it is accepted or rejected.

Preferred solution qualities
The chosen solution must be:

- Production-safe.
- Idempotent.
- Append-only aware.
- Reusable across projects.
- Minimal but not fragile.
- Easy to audit.
- Easy to disable.
- Safe under retries.
- Safe under partial failures.
- Safe when LLM usage is missing.
- Compatible with existing project conventions.
- Able to run without exposing secrets in logs.
- Able to produce local evidence before remote posting.

Required safeguards
Design all of the following safeguards:

1. Dry-run mode
   - Builds and validates payload.
   - Prints sanitized payload.
   - Does not call endpoint.

2. Test mode
   - Sends exactly one clearly marked test row only when explicitly enabled.
   - Requires endpoint and token from environment.
   - Must not run by default.

3. Production mode
   - Sends real rows only after validation passes.
   - Must require explicit enablement, for example:
     ENABLE_LLM_METRICS_POST=1
   - Must never post automatically during discovery or planning.

4. Payload validation
   - Required field presence.
   - Valid status enum.
   - Numeric fields are integers or blank/null where accepted.
   - No negative counts.
   - items_succeeded + items_failed relationship checked against items_discovered, with documented exceptions.
   - timestamp format checked.
   - token is not included in payload body.

5. Idempotency ledger
   - Store local record of posted run_id values.
   - Before posting, check whether run_id was already posted.
   - After successful post, persist endpoint response, timestamp, payload hash, and run_id.
   - Do not include secret token in the ledger.
   - Recommend a project-appropriate path, such as:
     .metrics/llm_metrics_posts.jsonl
     runs/metrics/llm_metrics_posts.jsonl
     artifacts/metrics/llm_metrics_posts.jsonl

6. Secret handling
   - Token must come from environment or approved secret manager.
   - Token must not be committed.
   - Token must not be printed.
   - Logs must show only masked token state, such as token_present=true.

7. Failure behavior
   - If post fails, local run must not be marked as posted.
   - The main production job must not be falsely marked success just because metrics posting failed.
   - Decide whether metrics post failure should be warning or hard failure based on project criticality.
   - Recommend default: warning for business workflow, hard failure for dedicated metrics test job.

8. Evidence bundle
   - Plan must require later execution to produce a source/evidence bundle.
   - Evidence must include changed files, tests, dry-run payloads, sanitized logs, and local ledger sample.
   - Evidence must not include token, full secrets, or unnecessary production data.

Deep self-challenge requirement
Before finalizing the plan, challenge your own recommendation.

Answer these questions explicitly:

1. Did I actually prove whether llm.professionalize.com is used, or did I infer it?
2. Did I search all likely endpoint, provider, environment, and wrapper patterns?
3. Did I identify every likely agent/app run boundary?
4. Is the proposed reporting point the least risky reliable point?
5. Could this design append duplicate rows?
6. Could this design pollute the production sheet with test rows?
7. Could this design leak the token?
8. Could failed runs still report useful metrics?
9. Could partial successes be misreported as success?
10. Are product, platform, website, and website_section derived from reliable sources?
11. What happens if token usage is unavailable?
12. What happens if the project processes multiple products in one run?
13. What happens if the project has no LLM usage today?
14. Is the solution reusable across similar aspose.org/aspose.net projects?
15. What must be verified in execution before enabling production posting?

Required output format
Return the plan using this structure:

# LLM Metrics Reporting Plan

## 1. Executive Verdict
State one of:
- READY_FOR_EXECUTION_PLAN
- NEEDS_REPOSITORY_CLARIFICATION
- BLOCKED_MISSING_CONTEXT
- NO_CURRENT_LLM_PROFESSIONALIZE_USAGE_FOUND
- CURRENT_USAGE_FOUND_PLAN_READY

Briefly summarize the recommended path.

## 2. Repository Understanding
Explain what the project appears to do, what surfaces it affects, and how it runs.

## 3. Current llm.professionalize.com State
Include:
- Confirmed usages.
- Possible usages.
- Bypasses.
- Missing evidence.
- Files inspected.
- Commands or searches used.

## 4. Current Metrics and Evidence Sources
List existing logs, ledgers, manifests, reports, summaries, taskcards, or run outputs that can feed the required fields.

## 5. Required Google Sheet Mapping
Provide a table with:
- Sheet field
- Source in this project
- Derivation rule
- Fallback if missing
- Confidence level

## 6. Candidate Implementation Options
Evaluate Options A through E.
Accept one recommended option or a phased combination.
Reject weaker options with reasons.

## 7. Recommended Production Design
Describe the proposed architecture in detail:
- Where code should live.
- How it should be called.
- How payloads are created.
- How dry-run/test/production modes work.
- How idempotency works.
- How secrets are handled.
- How failures are handled.

## 8. If Current Project Does Not Use llm.professionalize.com
If applicable, provide:
- Current provider state.
- Proposed migration path.
- Minimal safe routing change.
- Metrics that become available after migration.
- Interim metrics that can be reported before migration.

## 9. Validation and Test Plan
Include:
- Unit tests.
- Integration tests.
- Dry-run tests.
- One-row test-post plan for later execution mode.
- Production posting gate.
- Duplicate prevention tests.
- Secret leakage tests.
- Failure simulation tests.

## 10. Production Rollout Plan
Give phased rollout:
- Phase 0: discovery confirmation.
- Phase 1: local reporter and dry-run.
- Phase 2: test row only.
- Phase 3: shadow reporting.
- Phase 4: production enablement.
- Phase 5: monitoring and cleanup.

## 11. Risks and Mitigations
Include append-only Google Sheet risks, duplicate rows, wrong field mapping, missing token usage, multi-product runs, secrets, retries, and stale assumptions.

## 12. Files Likely to Change in Execution
List expected files and why.
Do not modify them in plan mode.

## 13. Execution Handoff Draft
Provide a concise draft of what the later execution prompt should ask the next agent to do.

## 14. Self-Challenge
Answer all self-challenge questions honestly.

## 15. Final Recommendation
State exactly what should be done next and what must not be done yet.

Important final rules
- Be thorough.
- Do not skip uncertainty.
- Do not invent current usage.
- Do not post to the Google Sheet in plan mode.
- Do not expose tokens.
- Prefer production-grade design over quick curl calls.
- Remember that rows are append-only and mistakes cannot be edited or deleted through the available endpoint.