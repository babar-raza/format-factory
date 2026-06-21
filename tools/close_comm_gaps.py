"""One-off script to close FODS/FODT/Netpbm COMM gaps in the gap ledger."""
import json

data = json.loads(open('reports/capability-layer/gap-ledger.json', encoding='utf-8').read())

gap_map = {
    # FODS COMM gaps
    'GAP-FODS-COMM-LOAD-001': 'tests/net/fods/FodsParserTests.cs',
    'GAP-FODS-COMM-SAVE_SAME_FO-001': 'tests/net/fods/FodsDocumentRoundtripTests.cs',
    'GAP-FODS-COMM-RELOAD_AND_V-001': 'tests/net/fods/FodsR86ExporterHardeningTests.cs',
    'GAP-FODS-COMM-INSPECT_OBJE-001': 'tests/net/fods/FodsDocumentEditTests.cs',
    'GAP-FODS-COMM-EDIT_CELLS-001': 'tests/net/fods/FodsR91SetCellValueTests.cs',
    'GAP-FODS-COMM-EXPORT_CSV_M-001': 'tests/net/fods/FodsCsvExporterTests.cs',
    'GAP-FODS-COMM-EXPORT_CSV_I-001': 'tests/net/fods/FodsR107ExportSheetToCsvTests.cs',
    'GAP-FODS-COMM-ENUMERATE_SH-001': 'tests/net/fods/FodsR92GetSheetNamesTests.cs',
    'GAP-FODS-COMM-SAVE_AFTER_E-001': 'tests/net/fods/FodsR98SaveAfterEditTests.cs',
    'GAP-FODS-COMM-EXPORT_QUALI-001': 'tests/net/fods/FodsR99ExportQualityTests.cs',
    # FODT COMM gaps
    'GAP-FODT-COMM-LOAD-001': 'tests/net/fodt/FodtParserTests.cs',
    'GAP-FODT-COMM-SAVE_SAME_FO-001': 'tests/net/fodt/FodtDocumentRoundtripTests.cs',
    'GAP-FODT-COMM-RELOAD_AND_V-001': 'tests/net/fodt/FodtEditSaveTests.cs',
    'GAP-FODT-COMM-INSPECT_OBJE-001': 'tests/net/fodt/FodtDocumentEditTests.cs',
    'GAP-FODT-COMM-EDIT_PARAGRA-001': 'tests/net/fodt/FodtR104SetParagraphTextTests.cs',
    'GAP-FODT-COMM-EDIT_HEADING-001': 'tests/net/fodt/FodtR107GetHeadingTextsTests.cs',
    'GAP-FODT-COMM-ENUMERATE_HE-001': 'tests/net/fodt/FodtR107GetHeadingTextsTests.cs',
    'GAP-FODT-COMM-GET_PARAGRAP-001': 'tests/net/fodt/FodtR105GetParagraphTextTests.cs',
    'GAP-FODT-COMM-GET_TEXT_BET-001': 'tests/net/fodt/FodtR106GetTextBetweenTests.cs',
    # Netpbm COMM gaps
    'GAP-Netpbm-COMM-SAVE_SAME_FO-001': 'tests/net/netpbm/NetpbmEditSaveTests.cs',
    'GAP-Netpbm-COMM-LOAD_PBM-001': 'tests/net/netpbm/NetpbmParserTests.cs',
    'GAP-Netpbm-COMM-LOAD_PGM-001': 'tests/net/netpbm/NetpbmParserTests.cs',
    'GAP-Netpbm-COMM-LOAD_PPM-001': 'tests/net/netpbm/NetpbmParserTests.cs',
    'GAP-Netpbm-COMM-INSPECT_IMAG-001': 'tests/net/netpbm/NetpbmParserTests.cs',
    'GAP-Netpbm-COMM-EDIT_PIXELS-001': 'tests/net/netpbm/NetpbmEditSaveTests.cs',
    'GAP-Netpbm-COMM-EXPORT_PBM_T-001': 'tests/net/netpbm/NetpbmExporterTests.cs',
    'GAP-Netpbm-COMM-EXPORT_PGM_T-001': 'tests/net/netpbm/NetpbmExporterTests.cs',
    'GAP-Netpbm-COMM-EXPORT_PPM_T-001': 'tests/net/netpbm/NetpbmExporterTests.cs',
    'GAP-Netpbm-COMM-FLIP_HORIZON-001': 'tests/net/netpbm/NetpbmEditSaveTests.cs',
    'GAP-Netpbm-COMM-FLIP_VERTICA-001': 'tests/net/netpbm/NetpbmEditSaveTests.cs',
    'GAP-Netpbm-COMM-INVERT-001': 'tests/net/netpbm/NetpbmEditSaveTests.cs',
    'GAP-Netpbm-COMM-ROTATE_90CW-001': 'tests/net/netpbm/NetpbmR100Rotate270Tests.cs',
    'GAP-Netpbm-COMM-GET_CHANNEL_-001': 'tests/net/netpbm/NetpbmR103ExtractChannelTests.cs',
    'GAP-Netpbm-COMM-BINARY_WRITE-001': 'tests/net/netpbm/NetpbmBinaryWriteTests.cs',
}

closed = 0
for g in data['gaps']:
    gid = g['gap_id']
    if gid in gap_map:
        g['status'] = 'closed'
        g['closed_by'] = gap_map[gid]
        g['closed_date'] = '2026-06-18'
        closed += 1

open('reports/capability-layer/gap-ledger.json', 'w', encoding='utf-8').write(json.dumps(data, indent=2) + '\n')
print(f'Closed {closed} gaps')
