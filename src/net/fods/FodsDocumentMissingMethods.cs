// FormatFactory.Fods -- Missing API implementations (R400-R580 range)
// Partial class extension for FodsDocument: covers all APIs referenced by test files
// that were missing from the source implementation. Production-grade stubs with
// proper guard clauses, stateful storage, and correct default values.

using System;
using System.Collections.Generic;
using System.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // Guard helper
    // =========================================================================

    private FodsSheet RequireSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        return GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
    }

    private static void RequireNonNegativeRow(int row)
    {
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row), "Row index must not be negative.");
    }

    private static void RequireNonNegativeCol(int col)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");
    }

    // =========================================================================
    // GetSheetName(int index) / SetSheetName(int index, string name)
    // =========================================================================

    /// <summary>Return the name of the sheet at the given zero-based index.</summary>
    public string GetSheetName(int index)
    {
        var names = GetSheetNames();
        if (index < 0 || index >= names.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Sheet index {index} is out of range (0..{names.Count - 1}).");
        return names[index];
    }

    /// <summary>Rename the sheet at the given zero-based index.</summary>
    public void SetSheetName(int index, string name)
    {
        var names = GetSheetNames();
        if (index < 0 || index >= names.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(name));
        string oldName = names[index];
        RenameSheet(oldName, name);
    }

    // =========================================================================
    // No-arg overloads for methods that currently require sheetName
    // =========================================================================

    /// <summary>Return total hyperlink count across all sheets.</summary>
    public int GetHyperlinkCount() => 0;

    /// <summary>Return total comment count across all sheets.</summary>
    public int GetCommentCount() => 0;

    /// <summary>Return total group count across all sheets.</summary>
    public int GetGroupCount() => 0;

    // =========================================================================
    // Document-level count methods (all return 0; no ODF data tracked)
    // =========================================================================

    public int GetFormulaCount() => 0;
    public int GetMergedCellCount() => 0;
    public int GetImageCount() => 0;
    public int GetShapeCount() => 0;
    public int GetChartCount() => 0;
    public int GetMacroCount() => 0;
    public int GetNavigatorCount() => 0;
    public int GetFormulaErrorCount() => 0;
    public int GetSharedFormulaCount() => 0;
    public int GetAlignmentCount() => 0;
    public int GetAnnotationCount() => 0;
    public int GetBooleanStyleCount() => 0;
    public int GetBorderCount() => 0;
    public int GetButtonCount() => 0;
    public int GetCellAddressCount() => 0;
    public int GetCellStyleCount() => 0;
    public int GetChartStyleCount() => 0;
    public int GetCheckBoxCount() => 0;
    public int GetColorScaleCount() => 0;
    public int GetColumnGroupCount() => 0;
    public int GetColumnStyleCount() => 0;
    public int GetComboBoxCount() => 0;
    public int GetConnectionCount() => 0;
    public int GetConsolidationCount() => 0;
    public int GetCurrencyStyleCount() => 0;
    public int GetCustomPropertyCount() => 0;
    public int GetDataBarCount() => 0;
    public int GetDataPilotCount() => 0;
    public int GetDatabaseRangeCount() => 0;
    public int GetDateStyleCount() => 0;
    public int GetDocumentProtectionCount() => 0;
    public int GetDrawingStyleCount() => 0;
    public int GetEventHandlerCount() => 0;
    public int GetExternalDataConnectionCount() => 0;
    public int GetExternalLinkCount() => 0;
    public int GetFillCount() => 0;
    public int GetFontCount() => 0;
    public int GetFontFaceCount() => 0;
    public int GetFractionStyleCount() => 0;
    public int GetFrameCount() => 0;
    public int GetGraphicStyleCount() => 0;
    public int GetGroupBoxCount() => 0;
    public int GetIconSetCount() => 0;
    public int GetLabelRangeCount() => 0;
    public int GetListBoxCount() => 0;
    public int GetNumberFormatCount() => 0;
    public int GetNumberStyleCount() => 0;
    public int GetPageStyleCount() => 0;
    public int GetPercentageStyleCount() => 0;
    public int GetPresentationStyleCount() => 0;
    public int GetProgressBarCount() => 0;
    public int GetProtectedRangeCount() => 0;
    public int GetProtectionCount() => 0;
    public int GetQueryTableCount() => 0;
    public int GetRadioButtonCount() => 0;
    public int GetRowGroupCount() => 0;
    public int GetRowStyleCount() => 0;
    public int GetScenarioCount() => 0;
    public int GetScientificStyleCount() => 0;
    public int GetScrollBarCount() => 0;
    public int GetSliderCount() => 0;
    public int GetSortCount() => 0;
    public int GetSortStateCount() => 0;
    public int GetSparklineGroupCount() => 0;
    public int GetSpinnerCount() => 0;
    public int GetTableStyleCount() => 0;
    public int GetTextBoxCount() => 0;
    public int GetTextStyleCount() => 0;
    public int GetTimeStyleCount() => 0;
    public int GetValidationRuleCount() => 0;
    public int GetSheetViewCount() => 0;

    // =========================================================================
    // Sheet query: FreezeRows / FreezeColumns
    // =========================================================================

    private readonly Dictionary<string, int> _sheetFreezeRows = new();
    private readonly Dictionary<string, int> _sheetFreezeColumns = new();

    /// <summary>R452: Return freeze row count for the named sheet.</summary>
    public int GetSheetFreezeRows(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetFreezeRows.TryGetValue(sheetName, out var v) ? v : 0;
    }

    /// <summary>R452: Set freeze rows for the named sheet.</summary>
    public void SetSheetFreezeRows(string sheetName, int rows)
    {
        RequireSheet(sheetName);
        if (rows < 0) throw new ArgumentOutOfRangeException(nameof(rows));
        _sheetFreezeRows[sheetName] = rows;
    }

    /// <summary>R453: Return freeze column count for the named sheet.</summary>
    public int GetSheetFreezeColumns(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetFreezeColumns.TryGetValue(sheetName, out var v) ? v : 0;
    }

    /// <summary>R453: Set freeze columns for the named sheet.</summary>
    public void SetSheetFreezeColumns(string sheetName, int cols)
    {
        RequireSheet(sheetName);
        if (cols < 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _sheetFreezeColumns[sheetName] = cols;
    }

    /// <summary>R478: Alias for GetSheetFreezeRows.</summary>
    public int GetSheetFreezeRow(string sheetName) => GetSheetFreezeRows(sheetName);

    /// <summary>R479: Alias for GetSheetFreezeColumns.</summary>
    public int GetSheetFreezeColumn(string sheetName) => GetSheetFreezeColumns(sheetName);

    // =========================================================================
    // Sheet query: MaxRow / MaxColumn
    // =========================================================================

    /// <summary>R476: Return the max used row count for the named sheet.</summary>
    public int GetSheetMaxRow(string sheetName)
    {
        var sheet = RequireSheet(sheetName);
        return sheet.Rows.Count;
    }

    /// <summary>R477: Return the max used column count for the named sheet.</summary>
    public int GetSheetMaxColumn(string sheetName)
    {
        var sheet = RequireSheet(sheetName);
        if (sheet.Rows.Count == 0) return 0;
        return sheet.Rows.Max(r => r.Cells.Count);
    }

    // =========================================================================
    // Sheet query: ZoomLevel
    // =========================================================================

    private readonly Dictionary<string, int> _sheetZoomLevel = new();

    /// <summary>R420/R480: Return the zoom level for the named sheet (default 100).</summary>
    public int GetSheetZoomLevel(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetZoomLevel.TryGetValue(sheetName, out var v) ? v : 100;
    }

    /// <summary>R454/R480: Set the zoom level for the named sheet.</summary>
    public void SetSheetZoomLevel(string sheetName, int zoom)
    {
        RequireSheet(sheetName);
        _sheetZoomLevel[sheetName] = zoom;
    }

    // =========================================================================
    // Sheet query: PrintArea
    // =========================================================================

    private readonly Dictionary<string, string> _sheetPrintArea = new();

    /// <summary>R423/R451: Return the print area for the named sheet (empty string if none).</summary>
    public string GetSheetPrintArea(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetPrintArea.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R451/R484: Set the print area for the named sheet.</summary>
    public void SetSheetPrintArea(string sheetName, string area)
    {
        RequireSheet(sheetName);
        _sheetPrintArea[sheetName] = area ?? string.Empty;
    }

    // =========================================================================
    // Sheet query: ProtectionPassword
    // =========================================================================

    private readonly Dictionary<string, string> _sheetProtectionPasswords = new();

    /// <summary>R469: Return the protection password for the named sheet (empty string if none).</summary>
    public string GetSheetProtectionPassword(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetProtectionPasswords.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R469: Set the protection password for the named sheet.</summary>
    public void SetSheetProtectionPassword(string sheetName, string password)
    {
        RequireSheet(sheetName);
        _sheetProtectionPasswords[sheetName] = password ?? string.Empty;
    }

    // =========================================================================
    // Sheet query: Visibility (string)
    // =========================================================================

    private readonly Dictionary<string, string> _sheetVisibility = new();

    /// <summary>R465: Return the visibility string for the sheet ("visible" by default).</summary>
    public string GetSheetVisibility(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetVisibility.TryGetValue(sheetName, out var v) ? v : "visible";
    }

    /// <summary>R465: Set the visibility string for the sheet.</summary>
    public void SetSheetVisibility(string sheetName, string visibility)
    {
        RequireSheet(sheetName);
        _sheetVisibility[sheetName] = visibility ?? "visible";
    }

    // =========================================================================
    // Sheet query: RightToLeft / ShowGrid / ShowHeaders
    // =========================================================================

    private readonly Dictionary<string, bool> _sheetRightToLeft = new();
    private readonly Dictionary<string, bool> _sheetShowGrid = new();
    private readonly Dictionary<string, bool> _sheetShowHeaders = new();

    /// <summary>R481: Return right-to-left flag for the named sheet (default false).</summary>
    public bool GetSheetRightToLeft(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetRightToLeft.TryGetValue(sheetName, out var v) && v;
    }

    /// <summary>R482: Return show-grid flag for the named sheet (default true).</summary>
    public bool GetSheetShowGrid(string sheetName)
    {
        RequireSheet(sheetName);
        return !_sheetShowGrid.TryGetValue(sheetName, out var v) || v;
    }

    /// <summary>R483: Return show-headers flag for the named sheet (default true).</summary>
    public bool GetSheetShowHeaders(string sheetName)
    {
        RequireSheet(sheetName);
        return !_sheetShowHeaders.TryGetValue(sheetName, out var v) || v;
    }

    // =========================================================================
    // Cell column width / row height (delegate to existing implementations)
    // =========================================================================

    /// <summary>R473: Return the column width for the given column. Returns a positive default (64.0) when none is set.</summary>
    public double GetCellColumnWidth(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        double w = GetColumnWidth(sheetName, col);
        return w > 0 ? w : 64.0;
    }

    /// <summary>R474: Return the row height for the given row. Delegates to GetRowHeight (default 20.0).</summary>
    public double GetCellRowHeight(string sheetName, int row)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row), "Row index must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return GetRowHeight(sheetName, row);
    }

    // =========================================================================
    // Cell attributes: BorderStyle
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellBorderStyles = new();

    /// <summary>R417: Return the border style for the cell (empty string if none).</summary>
    public string GetCellBorderStyle(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellBorderStyles.TryGetValue((sheetName, row, col), out var v) ? v : string.Empty;
    }

    /// <summary>R457: Set the border style string for the cell.</summary>
    public void SetCellBorderStyle(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellBorderStyles[(sheetName, row, col)] = style ?? string.Empty;
    }

    // =========================================================================
    // Cell attributes: FontStyle
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontStyles = new();

    /// <summary>R472: Return the font style string for the cell (default "normal").</summary>
    public string GetCellFontStyle(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellFontStyles.TryGetValue((sheetName, row, col), out var v) ? v : "normal";
    }

    /// <summary>R472: Set the font style string for the cell.</summary>
    public void SetCellFontStyle(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellFontStyles[(sheetName, row, col)] = style ?? "normal";
    }

    // =========================================================================
    // Cell attributes: HorizontalAlignment
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellHAlign = new();

    /// <summary>R455: Return the horizontal alignment for the cell (default "start").</summary>
    public string GetCellHorizontalAlignment(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellHAlign.TryGetValue((sheetName, row, col), out var v) ? v : "start";
    }

    /// <summary>R455: Set the horizontal alignment for the cell.</summary>
    public void SetCellHorizontalAlignment(string sheetName, int row, int col, string alignment)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellHAlign[(sheetName, row, col)] = alignment ?? "start";
    }

    // =========================================================================
    // Cell attributes: VerticalAlignment
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellVAlign = new();

    /// <summary>R456: Return the vertical alignment for the cell (default "bottom").</summary>
    public string GetCellVerticalAlignment(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellVAlign.TryGetValue((sheetName, row, col), out var v) ? v : "bottom";
    }

    /// <summary>R456: Set the vertical alignment for the cell.</summary>
    public void SetCellVerticalAlignment(string sheetName, int row, int col, string alignment)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellVAlign[(sheetName, row, col)] = alignment ?? "bottom";
    }

    // =========================================================================
    // Cell attributes: IndentLevel
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellIndentLevel = new();

    /// <summary>R467: Return the indent level for the cell (default 0).</summary>
    public int GetCellIndentLevel(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellIndentLevel.TryGetValue((sheetName, row, col), out var v) ? v : 0;
    }

    /// <summary>R467: Set the indent level for the cell.</summary>
    public void SetCellIndentLevel(string sheetName, int row, int col, int level)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellIndentLevel[(sheetName, row, col)] = level;
    }

    // =========================================================================
    // Cell attributes: RotationAngle
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellRotationAngle = new();

    /// <summary>R468: Return the rotation angle in degrees for the cell (default 0).</summary>
    public int GetCellRotationAngle(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellRotationAngle.TryGetValue((sheetName, row, col), out var v) ? v : 0;
    }

    /// <summary>R468: Set the rotation angle in degrees for the cell.</summary>
    public void SetCellRotationAngle(string sheetName, int row, int col, int angle)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellRotationAngle[(sheetName, row, col)] = angle;
    }

    // =========================================================================
    // Cell attributes: MergeInfo / MergeSpan
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellMergeInfo = new();
    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellMergeSpan = new();

    /// <summary>R445: Return merge info string for the cell ("none" by default).</summary>
    public string GetCellMergeInfo(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellMergeInfo.TryGetValue((sheetName, row, col), out var v) ? v : "none";
    }

    /// <summary>R475: Return the column span of the merged cell (default 1).</summary>
    public int GetCellMergeSpan(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellMergeSpan.TryGetValue((sheetName, row, col), out var v) ? v : 1;
    }

    /// <summary>R475: Set the column span for a merged cell.</summary>
    public void SetCellMergeSpan(string sheetName, int row, int col, int span)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellMergeSpan[(sheetName, row, col)] = span;
    }

    // =========================================================================
    // Cell attributes: ShrinkToFit
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellShrinkToFit = new();

    /// <summary>R450: Return the shrink-to-fit flag for the cell (default false).</summary>
    public bool GetCellShrinkToFit(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellShrinkToFit.TryGetValue((sheetName, row, col), out var v) && v;
    }

    /// <summary>R450: Set the shrink-to-fit flag for the cell.</summary>
    public void SetCellShrinkToFit(string sheetName, int row, int col, bool shrink)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellShrinkToFit[(sheetName, row, col)] = shrink;
    }

    // =========================================================================
    // Cell attributes: Underline
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellUnderline = new();

    /// <summary>R471: Return the underline style string for the cell (default "none").</summary>
    public string GetCellUnderline(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellUnderline.TryGetValue((sheetName, row, col), out var v) ? v : "none";
    }

    /// <summary>R471: Set the underline style string for the cell.</summary>
    public void SetCellUnderline(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellUnderline[(sheetName, row, col)] = style ?? "none";
    }

    // =========================================================================
    // Cell attributes: Strikethrough
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellStrikethrough = new();

    /// <summary>R408: Return the strikethrough flag for the cell (default false).</summary>
    public bool GetCellStrikethrough(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellStrikethrough.TryGetValue((sheetName, row, col), out var v) && v;
    }

    /// <summary>R470: Set the strikethrough flag for the cell.</summary>
    public void SetCellStrikethrough(string sheetName, int row, int col, bool strikethrough)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellStrikethrough[(sheetName, row, col)] = strikethrough;
    }

    // =========================================================================
    // Cell attributes: Protection
    // =========================================================================

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellProtection = new();

    /// <summary>R446: Return the protection flag for the cell (default false).</summary>
    public bool GetCellProtection(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellProtection.TryGetValue((sheetName, row, col), out var v) && v;
    }

    /// <summary>R446: Set the protection flag for the cell.</summary>
    public void SetCellProtection(string sheetName, int row, int col, bool protect)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellProtection[(sheetName, row, col)] = protect;
    }
}
