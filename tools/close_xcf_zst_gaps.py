"""One-off script to close XCF and ZST FOSS gaps in the gap ledger."""
import json

data = json.loads(open('reports/capability-layer/gap-ledger.json', encoding='utf-8').read())

xcf_map = {
    'GAP-XCF-FOSS-XCF_IS_MULTI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfIsMultiPixel',
    'GAP-XCF-FOSS-XCF_FILE_BYT-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfFileBytesPerLayer',
    'GAP-XCF-FOSS-XCF_COLOR_MO-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfColorModeName',
    'GAP-XCF-FOSS-XCF_LAYER_SI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfLayerSizeVariance',
    'GAP-XCF-FOSS-XCF_TOTAL_PI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfTotalPixels',
    'GAP-XCF-FOSS-XCF_FILE_HEA-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfFileHeaderOverhead',
    'GAP-XCF-FOSS-XCF_VERSION_-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfVersionNumber',
    'GAP-XCF-FOSS-XCF_IS_HIGH_-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfIsHighRes',
    'GAP-XCF-FOSS-XCF_MEGAPIXE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfMegapixelCount',
    'GAP-XCF-FOSS-XCF_IS_SQUAR-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfIsSquareCanvas',
    'GAP-XCF-FOSS-XCF_WIDTH_TO-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthToHeightRatio',
    'GAP-XCF-FOSS-XCF_HAS_SING-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfHasSingleLayer',
    'GAP-XCF-FOSS-XCF_ASPECT_R-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfAspectRatioString',
    'GAP-XCF-FOSS-XCF_LAYER_WI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfLayerWidthSum',
    'GAP-XCF-FOSS-XCF_TOTAL_CA-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfTotalCanvasPixels',
    'GAP-XCF-FOSS-XCF_HEIGHT_S-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfHeightSquared',
    'GAP-XCF-FOSS-XCF_MAX_SIDE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfMaxSideLength',
    'GAP-XCF-FOSS-XCF_AREA_TO_-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfAreaToLayerRatio',
    'GAP-XCF-FOSS-XCF_MIN_SIDE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfMinSideLength',
    'GAP-XCF-FOSS-XCF_CANVAS_H-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfCanvasHalfPerimeter',
    'GAP-XCF-FOSS-XCF_WIDTH_HE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthHeightSum',
    'GAP-XCF-FOSS-XCF_CANVAS_D-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfCanvasDiagonal',
    'GAP-XCF-FOSS-XCF_WIDTH_SQ-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthSquared',
    'GAP-XCF-FOSS-XCF_LAYER_NA-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfLayerNameList',
    'GAP-XCF-FOSS-XCF_COLOR_DE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfColorDepth',
    'GAP-XCF-FOSS-XCF_WIDTH_PL-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthPlusHeight',
    'GAP-XCF-FOSS-XCF_LAYER_PI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfLayerPixelCount',
    'GAP-XCF-FOSS-XCF_IS_COLOR-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfIsColor',
    'GAP-XCF-FOSS-XCF_PIXELS_E-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfPixelsExceedLayers',
    'GAP-XCF-FOSS-XCF_CANVAS_F-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfCanvasFillRatio',
    'GAP-XCF-FOSS-XCF_IS_TINY-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfIsTiny',
    'GAP-XCF-FOSS-XCF_AVG_LAYE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfAvgLayerArea',
    'GAP-XCF-FOSS-XCF_HEIGHT_T-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfHeightToLayerRatio',
    'GAP-XCF-FOSS-XCF_NUM_LAYE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfNumLayersPlusImageTypeId',
    'GAP-XCF-FOSS-XCF_WIDTH_TI-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthTimesFileSize',
    'GAP-XCF-FOSS-XCF_WIDTH_PE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWidthPerLayer',
    'GAP-XCF-FOSS-XCF_HEIGHT_P-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfHeightPlusNumLayers',
    'GAP-XCF-FOSS-XCF_PIXEL_CO-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfPixelCountTimesTwo',
    'GAP-XCF-FOSS-XCF_BYTES_PE-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfBytesPerLayer',
    'GAP-XCF-FOSS-XCF_PIXEL_AR-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfPixelArea',
    'GAP-XCF-FOSS-XCF_WH_TIMES-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfWhTimes400',
    'GAP-XCF-FOSS-XCF_AREA_PLU-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfAreaPlusFileSize',
    'GAP-XCF-FOSS-XCF_LAYERS_T-001': 'tests/python/xcf/test_xcf_gap_closure_foss.py::TestXcfLayersTimesWidth',
}

zst_map = {
    'GAP-ZST-FOSS-ZST_COMPRESS-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstCompressionSaving',
    'GAP-ZST-FOSS-ZST_IS_HIGHL-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsHighlyCompressed',
    'GAP-ZST-FOSS-ZST_IS_RLE_E-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsRleEfficient',
    'GAP-ZST-FOSS-ZST_FILE_SIZ-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstFileSizeBytes',
    'GAP-ZST-FOSS-ZST_IS_EMPTY-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsEmptyContent',
    'GAP-ZST-FOSS-ZST_DENSITY-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstDensity',
    'GAP-ZST-FOSS-ZST_UNIQUE_F-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstUniqueFrameSizeCount',
    'GAP-ZST-FOSS-ZST_IS_UNIFO-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsUniformFrames',
    'GAP-ZST-FOSS-ZST_CONTENT_-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstContentTypeHint',
    'GAP-ZST-FOSS-ZST_FRAME_HE-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstFrameHeaderDescriptor',
    'GAP-ZST-FOSS-ZST_IS_MINIM-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsMinimalFrame',
    'GAP-ZST-FOSS-ZST_MAGIC_VA-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstMagicValid',
    'GAP-ZST-FOSS-ZST_RATIO_VS-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstRatioVsUncompressed',
    'GAP-ZST-FOSS-ZST_BYTES_SA-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstBytesSaved',
    'GAP-ZST-FOSS-ZST_HEADER_S-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstHeaderSize',
    'GAP-ZST-FOSS-ZST_SIZE_EXC-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstSizeExceeds100k',
    'GAP-ZST-FOSS-ZST_FRAME_CO-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstFrameCountRatio',
    'GAP-ZST-FOSS-ZST_OVERHEAD-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstOverheadBytes',
    'GAP-ZST-FOSS-ZST_AVG_COMP-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstAvgCompressionPerByte',
    'GAP-ZST-FOSS-ZST_AVG_BYTE-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstAvgByteValue',
    'GAP-ZST-FOSS-ZST_SIZE_PER-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstSizePerFrame',
    'GAP-ZST-FOSS-ZST_BYTE_RAT-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstByteRatio',
    'GAP-ZST-FOSS-ZST_MAX_BYTE-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstMaxByteValue',
    'GAP-ZST-FOSS-ZST_MIN_BYTE-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstMinByteValue',
    'GAP-ZST-FOSS-ZST_AVG_DECO-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstAvgDecompressedByteValue',
    'GAP-ZST-FOSS-ZST_BYTE_SUM-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstByteSumPerFrame',
    'GAP-ZST-FOSS-ZST_BYTE_COU-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstByteCountSquared',
    'GAP-ZST-FOSS-ZST_BYTES_PE-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstBytesPerDecompressedByte',
    'GAP-ZST-FOSS-ZST_IS_TRIVI-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstIsTrivialCompression',
    'GAP-ZST-FOSS-ZST_SIZE_RAT-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstSizeRatio',
    'GAP-ZST-FOSS-ZST_DECOMP_T-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstDecompTimes',
    'GAP-ZST-FOSS-ZST_BYTE_RAN-001': 'tests/python/zst/test_zst_gap_closure_foss.py::TestZstByteRange',
}

all_map = dict(list(xcf_map.items()) + list(zst_map.items()))
closed = 0
for g in data['gaps']:
    gid = g['gap_id']
    if gid in all_map:
        g['status'] = 'closed'
        g['closed_by'] = all_map[gid]
        g['closed_date'] = '2026-06-18'
        closed += 1

open('reports/capability-layer/gap-ledger.json', 'w', encoding='utf-8').write(json.dumps(data, indent=2) + '\n')
print(f'Closed {closed} gaps')
