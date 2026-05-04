---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run008
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 01 — Project Origin and Intent

## Original business problem

Historically, requests for minor file formats were logged in Redmine and then left inactive because those formats were not globally popular enough to justify manual product-team effort.

The AI-era thesis is different:

> If agents can systematically acquire file-format knowledge, minor file formats become scalable rather than one-off manual work.

The project exists to convert long-tail file-format support from a human backlog problem into an agentic acquisition and implementation pipeline.

## Meaning of “file format hacking”

In this project, “hacking file formats” means legally safe engineering work:

- parsers
- converters
- importers
- exporters
- validators
- compatibility tools
- format inspectors
- sample analyzers
- neutral intermediate models
- acquisition agents
- evidence packs
- fuzzing and malformed-file testing
- oracle/reference comparison

It does **not** mean:

- breaking into systems
- bypassing access control
- circumventing DRM
- unsafe exploit work
- legally questionable reverse engineering
- copying restricted specifications into released artifacts
- using unauthorized sample files

## Strategic goal

Build a repeatable **File Format Acquisition System** that can take a minor format and produce:

1. format profile
2. legal/spec evidence
3. local spec/source metadata
4. sample corpus policy and provenance
5. parser notes
6. prototype evidence
7. neutral model
8. oracle comparison
9. security and fuzz findings
10. product-mapping recommendation
11. implementation taskcards

## Scope of suitable formats

The early system should focus on formats that have one or more of the following:

- open specification
- public documentation
- official schema
- public registry metadata
- legally usable open-source implementation
- text/XML/JSON structure
- simple or well-documented binary structure

Formats that rely only on reverse-engineered binary behavior with no public permission are blocked or rejected until legally cleared.

## Initial pilot thinking

The proposed first pilot is **FODS**, Flat OpenDocument Spreadsheet, because it is:

- standards-based
- XML-based
- spreadsheet-family aligned
- useful for Cells-style product tracks
- safer than proprietary binary formats
- a stepping stone to ODS

The proposed second candidate is **Gnumeric**, because it remains in the spreadsheet family and introduces compression/container handling after the first XML-only pilot succeeds.

Formal scoring for FODS has **not** been performed yet. That is Phase 1A work only.
