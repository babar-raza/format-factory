# Lane Ownership — Acceleration R105

## Coordinator (this sprint)
Owns shared file integration after lane-local evidence passes.

## Shared files (coordinator-serialized writes):
- tools/supervisor/build_declaration_review_package.py
- tools/supervisor/anti_skip_checker.py
- tests/supervisor/acceleration/**
- .local/evidences/acceleration-r105/evidence-declaration.yaml
- reports/acceleration-r105/final-verdict.md

## Lane-local (each train writes independently):
- reports/acceleration-r105/*.md (per-train reports)
- reports/acceleration-r105/sample-outputs/*.json
- reports/acceleration-r105/generated-stream-prompts/*.md

## Stream boundary:
- Acceleration stream: tools/supervisor/, tests/supervisor/, .supervisor/
- Forbidden: src/net/, src/python/ (product code)
- Global state files: reports/supervisor/* (read-only for identity audit, write only via autonomous-cycle)
