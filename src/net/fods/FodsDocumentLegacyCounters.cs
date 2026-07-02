// FormatFactory.Fods -- Legacy constant-zero counter APIs (Category D)
// GI-FODS-NET-001 Phase 3a: Staged removal file.
// These 74 public Get*Count() methods return 0 unconditionally and have no ODF specification
// basis. They were created to satisfy test compilation only (not spec behavior).
//
// PENDING REMOVAL: GI-FODS-NET-001 Phase 3f
// Pre-condition for deletion: All test files referencing these methods must be
// rewritten or deleted (Lane 4d). See plans/.claude/buzzing-wiggling-whistle.md
//
// DO NOT ADD NEW METHODS TO THIS FILE.
// DO NOT PROMOTE THESE METHODS TO PRODUCT APIS.
// Governance validators V87 and V89 monitor this file.

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // PENDING REMOVAL: GI-FODS-NET-001 Phase 3f — Category D: constant-zero count APIs

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetHyperlinkCount() => 0; // computable via text:a elements; see Phase 3f note

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCommentCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetGroupCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFormulaCount() => 0; // computable via @table:formula count; see Phase 3f note

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetMergedCellCount() => 0; // computable via @table:number-columns-spanned > 1; see Phase 3f note

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetImageCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetShapeCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetChartCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetMacroCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetNavigatorCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFormulaErrorCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSharedFormulaCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetAlignmentCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetAnnotationCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetBooleanStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetBorderCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetButtonCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCellAddressCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCellStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetChartStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCheckBoxCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetColorScaleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetColumnGroupCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetColumnStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetComboBoxCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetConnectionCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetConsolidationCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCurrencyStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetCustomPropertyCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDataBarCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDataPilotCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDatabaseRangeCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDateStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDocumentProtectionCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetDrawingStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetEventHandlerCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetExternalDataConnectionCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetExternalLinkCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFillCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFontCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFontFaceCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFractionStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetFrameCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetGraphicStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetGroupBoxCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetIconSetCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetLabelRangeCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetListBoxCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetNumberFormatCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetNumberStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetPageStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetPercentageStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetPresentationStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetProgressBarCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetProtectedRangeCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetProtectionCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetQueryTableCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetRadioButtonCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetRowGroupCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetRowStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetScenarioCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetScientificStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetScrollBarCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSliderCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSortCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSortStateCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSparklineGroupCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSpinnerCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetTableStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetTextBoxCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetTextStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetTimeStyleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetValidationRuleCount() => 0;

    /// <summary>PENDING REMOVAL (GI-FODS-NET-001). No ODF basis. Returns 0.</summary>
    public int GetSheetViewCount() => 0;
}
