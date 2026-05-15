# R15A Gate 3 Semantics and Boundary Report
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
Date: 2026-05-15

## Gate 3 Pass Criteria (from docs/gates.md)

Gate 3 PASSES only when ALL of the following are true:
1. Actual sample files exist in samples/by-format/<format-id>/
2. A _provenance.yaml is present for each sample with provenance_status: confirmed
3. All samples use licenses from the acceptable list (project-owned synthetic, BSD, MIT, Apache-2.0, CC0, CC-BY, public-domain)
4. Human (Babar Raza) has reviewed provenance
5. Gate 3 is approved by human in a new execution prompt

## Gate 3A vs Gate 3B Distinction

### Gate 3A (This Sprint — R15A)
- Source identification: research candidate sources, record URLs and license info
- Output: acquisition-packs/zst/sample-sources.md
- Output: taskcards/ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md
- Registry state: gate_3.status = source_identification_complete (NOT passed)
- samples/by-format/zst/ does NOT exist at end of sprint

### Gate 3B (Future Sprint — R16)
- Actual file acquisition: download, generate, or copy sample files
- Create samples/by-format/zst/ with actual .zst files
- Create _provenance.yaml for each sample with confirmed provenance
- Submit for human review
- Gate 3 can only be set to passed after human approval in R16 or later

## Boundary Enforcement

The following actions are FORBIDDEN in R15A:
- Downloading any .zst files to the repository
- Creating samples/by-format/zst/ directory
- Setting gate_3.status to passed, in_progress, or any value implying completion
- Creating _provenance.yaml files for ZST samples
- Running the zstd compressor to create corpus files
- Claiming Gate 3 is complete based on source identification alone

The following actions are PERMITTED in R15A:
- Identifying and recording URLs of candidate .zst sample sources
- Classifying licenses of candidate sources
- Assessing provenance risk of each candidate
- Creating a plan for corpus acquisition (Gate 3B work plan)
- Updating registry fields: gate_3.source_identification_complete = true, gate_3.candidate_sources_identified = <count>
- Creating sample-sources.md in acquisition-packs/zst/

## Rationale

Gate 3A (source identification) cannot substitute for Gate 3B (corpus acquisition) because:
- docs/gates.md requires actual files with confirmed provenance for Gate 3 to pass
- URL identification alone does not confirm that files are accessible, usable, or license-compliant after inspection
- Human review of actual file provenance is required (not just URL review)
- DEC-034: independent IV sprint required before human review — this applies to Gate 3B, not Gate 3A

## Conclusion

R15A correctly scoped as Gate 3A. Gate 3 WILL NOT be set to passed at R15A close.
Next required action: R16 execution prompt to authorize Gate 3B corpus acquisition.
