# Format Family Playbooks

**Added:** R85 Train H
**Purpose:** Reusable templates for adding new format families to Format Factory

## Playbooks

| File | Format Family | Examples |
|------|--------------|---------|
| xml-office-like.md | XML-based office documents | FODS, FODT, ODS, ODT |
| text-table.md | Text/tabular formats | SYLK, DIF, CSV, TSV |
| simple-binary-image.md | Simple binary/text image | PBM, PGM, PPM, QOI |
| compression-container.md | Compression/container | ZST, ZPAQ |

## How to use

1. Copy the appropriate playbook template
2. Fill in format-specific values
3. Follow the acquisition → implementation → test → package sequence
4. Do not skip steps — each step is a gate prerequisite

## Authority note

These playbooks are guides, not gate approvals. Each format still requires the full 11-gate pipeline.
