**Document type:** Directory Orientation
**Last reviewed:** 2026-06-29

# Acquisition Packs

## Purpose

Format onboarding packs — specification summaries, scoring, and readiness assessments for the 11-gate acquisition pipeline.

## Directory Structure

One subdirectory per format (22 formats + candidates). Each contains `pack.yaml`, spec-cache manifests, and gate plans.

## Governance

- **Classification:** PIPELINE_ARTIFACT
- **Producers:** acquisition tools, `/score-format` skill
- **Consumers:** gate checks, developers
- **Manual editing:** Yes — packs are authored during format acquisition

## Relationships

- Registry entry: `registry/repository-root-folders.yaml`
- Acquisition pipeline: `docs/governance/` acquisition gate documentation
