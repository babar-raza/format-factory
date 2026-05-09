---
memory_package: format-factory-chat-memory
created_at: 2026-05-09
source: ChatGPT AI-direction conversation and evidence-bundle review
visibility: internal
publish_allowed: false
authority: context_only
supersedes: none
must_cross_check:
  - plans/master-plan.md
  - registry/format-registry.yaml
  - evidence bundles
---

# 13 -- ChatGPT Initial Project Analysis, 2026-05-09

## Purpose

This file captures ChatGPT's first project-level analysis after inspecting the attached Format Factory
source archive in the 2026-05-09 AI-direction conversation. It is stored separately so future agents
can understand the project's state from the requirement perspective before executing new sprints.

## What the project is

The Format Factory project is not just a parser project. It is an acquisition system for file formats.
Its purpose is to take a file format from discovery to legally safe, evidence-backed, reproducible
product implementation.

The final output is intended to become real source code, packaging, tests, and product assets. The
project currently spends most of its energy on controlled acquisition before source generation.

The project is organized around gates, evidence, taskcards, registry state, human approvals, and
independent verification. `AGENTS.md`, `GOVERNANCE.md`, `plans/master-plan.md`, `ROADMAP.md`,
`docs/`, `taskcards/`, `schemas/`, `tools/`, `reports/`, and `memory/` define how agents are allowed
to plan, execute, verify, package evidence, and move the project forward without drifting.

The core idea is sound: before writing product code for a format, the system should know what the
format is, where its legal specification comes from, what can be implemented safely, what samples
prove, what the neutral model looks like, what the parser strategy should be, what the security risks
are, and what product tier is allowed.

## User requirement as understood

The user's original requirement was not "write parsers manually with some documentation around them."

The real requirement is:

The project must become AI-assisted, retrieval-grounded, evidence-verified, replayable, and
product-producing.

The user wants an agentic format-acquisition and product-generation system where AI speeds up tedious
work, but AI is never treated as an uncontrolled authority.

LLMs, embeddings, agent workflows, skills, playbooks, and retrieval should help agents:

- understand specifications
- produce candidate facts
- draft requirements
- suggest parser strategies
- generate tests
- compare behavior
- repair failures
- move formats faster toward actual usable source code

At the same time, strict consistency is required. The project must avoid a system where every run
invents a new interpretation of the same format. Near-identical results should come from deterministic
inputs, cached evidence, normalized specs, verified facts, schemas, replayable playbooks, validation
commands, oracle comparisons, and audit logs.

AI should accelerate the pipeline, but every AI output should be converted into structured artifacts
and checked before it becomes project truth.

## Current project standing

The project has a mature governance and planning framework, but not yet a mature AI execution framework.

The project has a clear acquisition model. It has an 11-gate process, taskcards, format registry,
master plan, memory files, evidence rules, visibility classifications, source boundaries, playbook
schemas, format understanding schemas, and validation tools.

The project has made real progress on at least two XML-style formats: FODS and FODT.

FODS appears to be the most advanced. The registry shows FODS has passed Gates 1 through 10 and is
at Gate 11 planning. It has synthetic Apache-2.0 samples, a prototype parser, neutral model work,
security analysis, oracle comparison concepts, and product planning signals. Gate 10 defines the
initial OSS scope as Tiers 0-2 and mentions `format-factory-fods v0.1.0`. However, no product source
exists yet under `src/python/fods/` or `src/net/fods/`.

FODT is also advanced, but slightly behind or less consistently recorded. The registry shows FODT has
passed Gates 1 through 9 and Gate 10 is planning-ready. There is a prototype parser, samples, neutral
model work, and security findings. One important security/design issue is that recursive list handling
in the prototype must not be carried into product source without being replaced by iterative traversal.

The source layer is still mostly empty. `src/python/_readme.md` and `src/dotnet/_readme.md` are
placeholders. The project explicitly forbids promoting prototypes directly into product source. That
is correct from a governance perspective, but it also means the archive does not yet contain tangible
product implementation.

## What the project has solved well

The project has solved the most important non-AI problem: uncontrolled agent drift.

The governance model is strict. Agents must read the governing docs first. They must distinguish
planning from execution. They must not approve their own outputs. They must package evidence. They
must avoid forbidden paths. They must preserve legal boundaries. They must not promote prototypes
directly into product code. They must avoid reverse engineering or IP-unsafe behavior. They must keep
visibility classes clear. They must update registry, taskcards, memory, and evidence artifacts.

That foundation is exactly what an AI-assisted system needs. Without this, adding LLMs would likely
make the project faster but less reliable. With this foundation, LLMs can be used safely as proposal
engines, summarizers, extractors, test designers, and repair assistants.

The Format Understanding Layer is also the right architectural move. The six planned per-format
artifacts, `format-profile.yaml`, `verified-facts.yaml`, `implementation-requirements.yaml`,
`parser-strategy.yaml`, `security-surface.yaml`, and `product-readiness.yaml`, are the correct
bridge between messy acquisition evidence and product implementation.

The spec retrieval strategy is also well thought out. It correctly prioritizes deterministic
section/page/element lookup first, lexical retrieval second, and vector or semantic retrieval third.
Embeddings should not replace deterministic retrieval. They should help find relevant evidence when
deterministic retrieval is insufficient.

The playbook layer is another strong design. It is not fully implemented yet, but the idea is
important: agents should not merely follow prose prompts. They should eventually operate through
replayable, validated, schema-backed playbooks that list expected files, commands, outputs, conflicts,
evidence, and validation gates.

## Where the project falls short from the AI requirement

The main gap is that AI is currently acknowledged, but not yet part of the critical execution path.

The project has `docs/llm-and-embedding-strategy.md`, but the strategy is still largely backlog-only.
It defines good future uses for LLMs and embeddings, but those uses are not yet implemented.

The project has `tools/llm/endpoints.yaml`, but the active client layer is absent or incomplete.
There is not yet an operational model discovery, model selection, prompt cache, run record, artifact
index integration, local endpoint discovery, or governed LLM call wrapper.

The related taskcards confirm this: `TC-0005-llm-endpoint-impl.md` is not complete; `LLM-001` is
proposed or pending; `EMB-001` is design-only; `TC-0016-fods-vector-index-pilot.md` is not started.

That explains the user's concern that results are not tangible. The project is doing careful
acquisition, but it is not yet using AI to compress the tedious parts. It is still relying heavily on
manual or deterministic artifact construction.

There is also a gap between "format understanding" and "product source." The Format Understanding
Layer is the right bridge, but the product source consumption task, `FUL-004`, is not implemented.
Until source scaffolding, tests, parser implementation, package metadata, and CLI/API surfaces are
generated from FUL artifacts, the project will continue to produce planning/evidence rather than
end-user libraries.

Another gap is that playbooks are still mostly schema and validation, not execution. The project can
describe how a replayable acquisition workflow should work, but it does not yet have a working replay
engine that can take a format, inspect current state, run deterministic steps, call governed AI when
needed, update artifacts, and produce a validated evidence bundle.

## How the project currently plans to achieve the goal

The project's intended path is visible in the documents and taskcards:

1. Each format passes acquisition gates.
2. Scattered evidence is compiled into the Format Understanding Layer.
3. Governed LLM endpoints are introduced.
4. Controlled embeddings are introduced.
5. Playbooks and replay are introduced.
6. Product source is generated under the format-first layout:
   - `src/python/{format}/`
   - `src/net/{format}/`

## The next-level interpretation

The next level is not simply to "turn on LLMs." The next level is to make AI a governed worker
inside the existing factory.

AI may propose facts, but facts become truth only after citation, schema validation, and
deterministic review.

AI may draft implementation requirements, but requirements must trace to source sections, samples,
oracle behavior, and product-scope decisions.

AI may suggest parser strategy, but the strategy must be checked against security constraints,
streaming requirements, XML parser policy, memory limits, and product tier boundaries.

AI may generate tests, but tests must run against samples, prototypes, oracle outputs, fuzz cases,
and expected neutral models.

AI may generate product code, but only from the Format Understanding Layer package, not from raw
imagination. Generated code must pass lint, unit tests, security checks, fixture validation,
packaging checks, and review gates.

AI may explain failures and propose repairs, but repair prompts must include exact failing evidence,
forbidden patterns, required APIs, and previous bad attempts so the system does not repeat mistakes.

Embeddings should help agents find relevant verified facts and requirements quickly. Embeddings must
never become the source of truth. They should only point back to cited facts and normalized spec
sections.

## Bottom-line assessment

The project is not in bad shape. It is well prepared for AI, but it has not crossed the line into
being AI-driven yet.

Right now, it is closer to a governed acquisition framework with prototypes than an agentic AI
product factory.

It has strong control but insufficient acceleration.

The next phase should preserve the control system while making AI operational, measurable, cached,
replayable, and directly tied to producing source code and tests.
