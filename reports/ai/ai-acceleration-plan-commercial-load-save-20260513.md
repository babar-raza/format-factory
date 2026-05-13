# AI Acceleration Plan — Commercial Load-Save Vertical Slice
# COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
# Date: 2026-05-13

## AI Endpoint Discovery

| Endpoint | Status | Notes |
|---|---|---|
| VS Code / Claude Code (in-repo) | AVAILABLE | Claude Sonnet 4.6 — this executor |
| llm.professionalize.com | NOT CHECKED | No secrets printed in discovery |
| Ollama (local) | NOT CHECKED | Not pre-configured |
| Embedding models | NOT AVAILABLE | No vector DB pre-configured |

## Fallback Strategy
LEXICAL_FALLBACK — Using deterministic lexical search over repo-owned normalized artifacts.
Embedding index NOT created. No vector DB files in evidence bundle.

## Local Retrieval Sources Available
- docs/commercial-product-capability-model.md
- docs/commercial-dotnet-architecture.md
- format_understanding/fods/ — FODS FUL facts
- format_understanding/fodt/ — FODT FUL facts
- acquisition-packs/fods/ — gate evidence and roadmaps
- acquisition-packs/fodt/ — gate evidence and roadmaps
- samples/by-format/fods/ — 4 FODS fixtures
- samples/by-format/fodt/ — 4 FODT fixtures
- schemas/neutral-model/fods/ — FODS object model schema
- schemas/neutral-model/fodt/ — FODT object model schema

## AI Use Authorization Per Lane

| Lane | AI Use Allowed | Restrictions |
|---|---|---|
| Lane A | Yes (self) | No secrets, no copyrighted spec text |
| Lane B | Yes (architecture review) | No raw copyrighted text |
| Lane C | Yes (edge-case test ideas, model naming) | Tests must pass |
| Lane D | Yes (ODF cell update rules from local facts) | Cite local files |
| Lane E | Yes (edge-case test ideas, model naming) | Tests must pass |
| Lane F | Yes (paragraph replacement rules from local facts) | Cite local files |
| Lane G | Yes (adversarial fixtures) | Human validation required |
| Lane H | Yes (adversarial code review) | No gate approval |
| Lane I | No AI involvement | State update only |
| Lane J | No AI involvement | Build verification only |
| Lane M | No AI involvement | Memory sync only |

## What Cannot Be Sent to AI
- GitHub PAT or any credentials
- Raw copyrighted ODF specification text
- Secrets from environment variables

## Validation Required Before AI Output Acceptance
- Structured output: schema validation
- Code: dotnet build + dotnet test pass
- Facts: citation to local files or verified product decisions
- No gate approval from AI
- No spec claims invented by AI

## Lane A Verdict
LANE_A_PASS_LEXICAL_FALLBACK
