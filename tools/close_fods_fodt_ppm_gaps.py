"""One-off script to close FODS/FODT/PPM FOSS gaps in the gap ledger."""
import json

data = json.loads(open('reports/capability-layer/gap-ledger.json', encoding='utf-8').read())

gap_map = {
    'GAP-FODS-FOSS-FODS_HAS_STR-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsHasStringCells',
    'GAP-FODS-FOSS-FODS_ROW_COU-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsRowCountVariance',
    'GAP-FODS-FOSS-FODS_AVG_STR-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsAvgStringLength',
    'GAP-FODS-FOSS-FODS_COL_COU-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsColCountVariance',
    'GAP-FODS-FOSS-FODS_AVG_NUM-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsAvgNumericValue',
    'GAP-FODS-FOSS-FODS_LONGEST-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsLongestRowIndex',
    'GAP-FODS-FOSS-FODS_NUMERIC-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsNumericSumAll',
    'GAP-FODS-FOSS-FODS_CELL_TO-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsCellToSheetRatio',
    'GAP-FODS-FOSS-FODS_FORMULA-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsFormulaCellCount',
    'GAP-FODS-FOSS-FODS_SHEET_R-001': 'tests/python/fods/test_fods_gap_closure_foss.py::TestFodsSheetRowVariance',
    'GAP-FODT-FOSS-FODT_LONGEST-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtLongestWord',
    'GAP-FODT-FOSS-FODT_AVG_HEA-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtAvgHeadingLength',
    'GAP-FODT-FOSS-FODT_TABLE_D-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtTableDensity',
    'GAP-FODT-FOSS-FODT_TOTAL_T-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtTotalTableCells',
    'GAP-FODT-FOSS-FODT_HAS_NUM-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtHasNumericContent',
    'GAP-FODT-FOSS-FODT_AVG_SEN-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtAvgSentenceLength',
    'GAP-FODT-FOSS-FODT_MAX_HEA-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtMaxHeadingDepth',
    'GAP-FODT-FOSS-FODT_TOTAL_C-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtTotalCharCount',
    'GAP-FODT-FOSS-FODT_IS_TEXT-001': 'tests/python/fodt/test_fodt_gap_closure_foss.py::TestFodtIsTextHeavy',
    'GAP-PPM-FOSS-PPM_IS_MONOC-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmIsMonochrome',
    'GAP-PPM-FOSS-PPM_TOTAL_CH-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmTotalChannelSum',
    'GAP-PPM-FOSS-PPM_AVG_BRIG-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmAvgBrightness',
    'GAP-PPM-FOSS-PPM_COLOR_VA-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmColorVariance',
    'GAP-PPM-FOSS-PPM_RED_RATI-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmRedRatio',
    'GAP-PPM-FOSS-PPM_BORDER_B-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmBorderBrightness',
    'GAP-PPM-FOSS-PPM_GREEN_RA-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmGreenRatio',
    'GAP-PPM-FOSS-PPM_PIXEL_BR-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmPixelBrightnessRange',
    'GAP-PPM-FOSS-PPM_BLUE_RAT-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmBlueRatio',
    'GAP-PPM-FOSS-PPM_IS_BRIGH-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmIsBright',
    'GAP-PPM-FOSS-PPM_MAXVAL-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmMaxval',
    'GAP-PPM-FOSS-PPM_NORMALIZ-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmNormalizedBrightness',
    'GAP-PPM-FOSS-PPM_AREA-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmArea',
    'GAP-PPM-FOSS-PPM_MAX_PIXE-001': 'tests/python/ppm/test_ppm_gap_closure_foss.py::TestPpmMaxPixelBrightness',
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
