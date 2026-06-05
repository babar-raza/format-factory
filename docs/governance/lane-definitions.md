# Lane Definitions

**Added:** 2026-06-03
**Authority:** plans/master-plan.md Section 43

## 1. Mainstream Product

Product output engine. Produces real capability breadth across commercial and FOSS products.

**Hard rules:**
- Cannot pass with evidence repair alone.
- Must produce measurable product capability changes (new APIs, new tests, new export paths).
- Must cover both commercial .NET and reduced/FOSS tracks.

**Output:** Source code changes in `src/net/` and `src/python/`, tests, examples, package proof, capability matrix updates.

## 2. Acceleration

Originally: AI/LLM/embeddings/retrieval/product-code-generation acceleration.
Drift: became anti-skip/prompt-quality machinery.
Corrected: split into two sub-lanes.

### 2A. Acceleration-A: Governance Harness
- Anti-skip enforcement
- Prompt-quality validation
- Evidence-quality safety checks
- Must prove it prevents false PASS or false STOP

### 2B. Acceleration-B: AI Product Acceleration
- LLM-assisted spec understanding
- Source-pattern mining
- Code-generation handoffs
- Test generation
- Product gap ranking
- Must prove it makes Mainstream faster or less blocked

## 3. Skills / Governed Execution

Reusable execution skills, handoffs, transcripts, receiver fixtures, validation.

**Hard rules:**
- Must make product source changes faster and safer.
- Must not produce proof in isolation only.
- Skills must be consumed by Mainstream or other lanes.

**Output:** Skill definitions, handoff templates, validation tools, execution transcripts.

## 4. Supervisor / Autonomous Continuation

Autonomous traffic controller.

**Hard rules:**
- Must decide what continues, what stops, what downgrades.
- Must prevent false PASS and false STOP.
- Must route blockers to the right stream.
- Must protect product throughput.
- Not merely an evidence auditor.

**Output:** Continuation signals, contradiction reports, sprint routing, lane health assessments.
