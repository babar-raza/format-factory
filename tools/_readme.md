# Tools

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03 (run009 — spec-cache authorization notes added)

---

## Purpose

This directory contains the acquisition-layer tools: LLM endpoint client, scoring utilities, acquisition helpers, and validation scripts. Tools in this directory are internal only — they are never included in any product release. They support the format acquisition pipeline but are not shipped to end users.

---

## Directory Structure

```
tools/
+-- _readme.md              This file
+-- llm/                    LLM endpoint client and model selection
|   +-- endpoints.yaml      Endpoint configuration (Phase 0 — committed, no secrets)
|   +-- endpoint_client.py  Endpoint probe and model selection (Phase 1 — TC-0005)
|   +-- run_record.py       Run record writer (Phase 1 — TC-0005)
|   +-- prompt_cache.py     Prompt/response cache writer (Phase 1 — TC-0005)
|   +-- artifact_index.py   Artifact index manager (Phase 1 — TC-0005)
|   +-- model-selection.yaml Task-type to model mapping (Phase 1 — TC-0005)
+-- spec-cache/             Specification cache tooling
|   +-- _readme.md          Directory orientation (Phase 0 — committed)
|   +-- acquire_spec.py     Download, hash, and index a spec (Phase 1 — TC-0007)
|   +-- refresh_check.py    Staleness check for cached specs (Phase 1 — TC-0007)
|   +-- spec_index.py       Read/write spec-index.yaml entries (Phase 1 — TC-0007)
+-- acquisition/            Acquisition helper scripts (Phase 1+)
+-- scoring/                Scoring scripts (Phase 1+)
+-- validation/             Front matter and release manifest validation (Phase 3+ — TC-0006)
    +-- validate_frontmatter.py
    +-- generate_manifest.py
    +-- check_boundary.py
```

In Phase 0, only `tools/llm/endpoints.yaml` and `tools/spec-cache/_readme.md` exist. All other tool files are created in Phase 1+ via their respective taskcards.

---

## Tool Inventory (Planned)

| Tool | Directory | Phase | Taskcard | Purpose |
|---|---|---|---|---|
| Endpoint config | `llm/endpoints.yaml` | Phase 0 | — | Endpoint config template (no secrets) |
| Endpoint client | `llm/endpoint_client.py` | Phase 1 | TC-0005 | Probe endpoints, select model, handle fallback |
| Run record writer | `llm/run_record.py` | Phase 1 | TC-0005 | Write JSONL run records to .local/llm-logs/ |
| Prompt cache | `llm/prompt_cache.py` | Phase 1 | TC-0005 | Write prompt-response pairs to .local/llm-cache/ |
| Artifact index | `llm/artifact_index.py` | Phase 1 | TC-0005 | Bootstrap and update .local/artifact-index.yaml |
| Model selection | `llm/model-selection.yaml` | Phase 1 | TC-0005 | Task-type to model priority mappings |
| Spec cache index | `spec-cache/_readme.md` | Phase 0 | — | Directory orientation (committed) |
| Spec acquisition | `spec-cache/acquire_spec.py` | Phase 1 | TC-0007 | Download spec (requires --allow-network authorization); supports --dry-run |
| Spec refresh | `spec-cache/refresh_check.py` | Phase 1 | TC-0007 | Scan spec-index.yaml entries for staleness; never auto-downloads |
| Spec index lib | `spec-cache/spec_index.py` | Phase 1 | TC-0007 | Read/write/validate spec-index.yaml entries |
| Scoring scripts | `scoring/` | Phase 1 | TC-0001 | Automated scoring model application |
| Sample downloader | `acquisition/` | Phase 2 | (future) | Download and verify sample candidates |
| Front matter validator | `validation/validate_frontmatter.py` | Phase 3+ | TC-0006 | Validate artifact front matter schema |
| Manifest generator | `validation/generate_manifest.py` | Phase 3+ | TC-0006 | Generate release manifests |
| Boundary checker | `validation/check_boundary.py` | Phase 3+ | TC-0006 | Verify no commercial artifacts in OSS release |

---

## Security Requirements for Tools

Tools in `tools/llm/` handle API credentials. Security rules:
- Never hardcode API keys. Use environment variables from `.env` (gitignored).
- Read `auth_env` from `endpoints.yaml` and call `os.environ.get(<auth_env>)`.
- Never log or commit full prompt or response text.
- LLM prompt/response cache files go to `.local/llm-cache/` (gitignored, never committed).

---

## Visibility

All tools are `visibility: internal`. Tools are acquisition-layer artifacts — they are never released to users or included in product packages.

---

## Relationship to Other Documents

- `docs/ai/llm-endpoint-strategy.md` — endpoint configuration policy and credential rules
- `docs/python-foss/specification-cache.md` — specification cache policy and schema
- `docs/governance/release-control.md` — visibility classification (tools are always internal)
- `docs/python-foss/acquisition-workflow.md` — where tools are invoked in the pipeline
- `taskcards/TC-0005-llm-endpoint-impl.md` — LLM tool implementation scope
- `taskcards/TC-0006-release-manifest.md` — validation tool implementation scope
- `taskcards/TC-0007-specification-cache.md` — spec-cache tool implementation scope
