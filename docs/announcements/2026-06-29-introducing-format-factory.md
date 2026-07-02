---
title: "Introducing Format Factory"
date: 2026-06-29
author: Format Factory Team
summary: "Format Factory is an autonomous engineering system that converts file format specifications into production-quality Python and .NET libraries through a governed, evidence-driven development pipeline."
categories: [Announcements]
tags: [Format Factory, File Formats, Open Source, Developer Tools, Automation]
draft: true
---

# Introducing Format Factory

Format Factory is an autonomous engineering system that converts file format specifications into Python and .NET libraries through a governed, evidence-driven development pipeline.

Rather than generating code directly, the project builds the machinery required to repeatedly transform formal specifications into maintainable software. Every product is developed from specification-derived facts, verified through deterministic testing, and continuously refined as the factory itself evolves.

## How It Works

Every supported format begins with its official specification.

The Specification Authority Layer extracts canonical facts from the specification and establishes a single source of truth for the entire development process. These facts drive downstream capability planning, specification-aligned object models, parser and writer implementation, deterministic oracle verification, and compliance validation.

Each format passes through an eleven-gate acquisition pipeline covering legal review, specification analysis, prototype development, security testing, and oracle verification before it reaches production status.

Development itself is performed through a growing collection of specialized skills coordinated by an autonomous supervisor. Product work and machinery improvements follow separate but connected execution pipelines: one continuously hardens the factory, while the other applies those capabilities to individual products. 840 sprint cycles have been completed through this pipeline, each producing evidence, gap analysis, and a backlog for the next iteration. 101 governance validators enforce quality rules automatically on every sprint, covering schema compliance, security policy, source structure limits, and specification traceability.

Importantly, the development pipeline is agent-orchestrated: sprint planning, code generation, test writing, governance validation, and gap analysis are performed by AI agents coordinated through the supervisor pipeline. Human oversight applies at defined gates — primarily commercial release authorization. All shipped library code is pure and deterministic, containing no LLM calls or AI runtime dependencies.

## Current Progress

The project currently spans twenty file formats across seven families:

| Family | Formats |
|--------|---------|
| Spreadsheets | FODS, ODS, CSV, TSV, DIF, SYLK, Gnumeric |
| Documents | FODT, ODT, ABW |
| Presentations | FODP |
| Drawing | FODG |
| Images | PBM, PGM, PPM, QOI, XCF |
| Data | TOML, NDJSON |
| Compression | ZST |

Each of these twenty formats has:

- A working Python implementation with parse, inspect, and write capabilities
- An installable local package
- Oracle verification against specification-derived test cases
- A consumer roundtrip proof — a script that loads, inspects, mutates, writes, and reloads the format using only the installed package API
- Independent certification across nine quality dimensions

Product maturity intentionally varies. Some formats provide working parser, inspection, editing, writing, and roundtrip capabilities, while others remain focused on foundational parsing or object model development. Six formats (FODS, FODT, CSV, TSV, NDJSON, ZST) also have .NET implementations, with three (FODS, FODT, Netpbm) on a commercial track with a quality sub-gate approved for code readiness.

The project includes over 4,700 test files across both platforms, with a zero-failure policy enforced on every sprint. Development is guided by product-specific gap ledgers, allowing each format to evolve independently while benefiting from improvements made to the shared machinery.

## What Comes Next

Current work focuses less on adding new formats and more on strengthening the factory itself.

Active development includes deepening specification-aligned data models, expanding writer and roundtrip capabilities for existing formats, extending deterministic oracle verification, growing the reusable skill ecosystem, and working toward package publication on public registries.

The long-term objective is a repeatable engineering platform capable of producing well-structured, specification-compliant file format libraries with minimal manual implementation while maintaining complete traceability from specification to shipped code — and commercial release of .NET products once full readiness criteria are met.

Format Factory remains under active development. Python packages are built and tested locally but not yet published to PyPI. Commercial .NET products are not yet released.

For architecture details, supported products, setup instructions, current status, limitations, and contribution guidelines, see the project README:
`https://gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory`

> **Note to publisher:** The repository URL above points to a private GitLab instance. Confirm or replace with the intended public-facing URL before publication.

---

> **Numbers in this post** are derived from `PROJECT_STATUS.md`, which is auto-generated from repository evidence. Run `python tools/docs/generate_project_status.py` to regenerate current values.
