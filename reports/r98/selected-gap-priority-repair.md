# Selected Gap Priority Repair

## Priority Order (R98+)
1. **Dogfood/export/package gaps** — prove Format Factory libraries are used end-to-end
2. **Same-format save after edits** — edit-save roundtrip is core product value
3. **Load/edit/save/export completeness** — full workflow, not just query APIs
4. **Installed workflow proof** — package imports without PYTHONPATH
5. **Query helpers** — only after above are complete

## R98 Selected Gaps
- FODS .NET: Same-format save after SetCellValue (Train L) — priority 2
- FODT .NET: ReplaceText for text editing (Train M) — priority 3
- Netpbm .NET: SaveToFile for edit persistence (Train N) — priority 2
- ZST: File-level roundtrip (Train O) — priority 3
- PPM: Pixel edit API tests (Train P) — priority 3
- SYLK: Installed workflow (Train Q) — priority 4
