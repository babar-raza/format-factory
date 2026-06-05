"""
Specification Authority Layer — Format Factory.

Provides deterministic, source-backed specification management for all
product formats. Enforces anti-bypass: no ad-hoc URL citations, no
memory-only claims, no AI-summary-only references.

Module inventory:
  spec_source_registry.py   — register and manage specification sources
  spec_vault_ingest.py      — ingest raw snapshots with SHA-256 binding
  spec_parser.py            — parse specification content
  spec_normalizer.py        — normalize parsed content to canonical form
  spec_indexer.py           — build searchable term/section index
  spec_digestor.py          — compute stable digest/fingerprints
  requirement_extractor.py  — extract candidate requirements from specs
  spec_verifier.py          — verify requirements against source
  requirement_graph.py      — build requirement linkage graph
  context_pack_builder.py   — build deterministic context packs
  spec_governance_runtime.py — anti-bypass enforcement runtime
"""
__version__ = "1.0.0"
