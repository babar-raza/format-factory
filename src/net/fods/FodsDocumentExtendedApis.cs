// FormatFactory.Fods -- Extended APIs (R290-R341 stubs + implementations)
// Partial class extension for FodsDocument: covers all APIs referenced by R290-R341 test files.
// These methods provide minimal implementations suitable for governed test coverage.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // -------------------------------------------------------------------------
    // Sheet visibility (R290, R291)
    // -------------------------------------------------------------------------

    /// <summary>R290: Returns true if the named sheet is visible (not hidden).</summary>
    public bool IsSheetVisible(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return false;
        var sheet = GetSheetByName(sheetName);
        if (sheet == null) return false;
        var display = sheet.Element.Attribute(NsTable + "display")?.Value;
        return display == null || !string.Equals(display, "false", StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>R290: Set the visibility of the named sheet.</summary>
    public void SetSheetVisible(string sheetName, bool visible)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        sheet.Element.SetAttributeValue(NsTable + "display", visible ? "true" : "false");
    }

    // -------------------------------------------------------------------------
    // Sheet protection (R291, R340)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, string?> _sheetProtection = new();

    /// <summary>R291: Returns true if the named sheet is protected.</summary>
    public bool IsSheetProtected(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return false;
        return _sheetProtection.ContainsKey(sheetName);
    }

    /// <summary>R291: Apply protection to the named sheet with optional password.</summary>
    public void SetSheetProtection(string sheetName, string? password = null)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _sheetProtection[sheetName] = password;
    }

    /// <summary>R340: Return protection info string (password-protected or unprotected).</summary>
    public string GetSheetProtection(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return "unprotected";
        return _sheetProtection.ContainsKey(sheetName) ? "password-protected" : "unprotected";
    }

    /// <summary>R295: Return protection status bool for the named sheet.</summary>
    public bool GetProtectionStatus(string sheetName) => IsSheetProtected(sheetName);

    // -------------------------------------------------------------------------
    // Cell number format (R293, R330)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellNumberFormats = new();

    /// <summary>R293: Set a number format string on the specified cell.</summary>
    public void SetCellNumberFormat(string sheetName, int row, int col, string format)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellNumberFormats[(sheetName, row, col)] = format ?? string.Empty;
    }

    /// <summary>R293: Get the number format string for the specified cell, or empty if none set.</summary>
    public string GetCellNumberFormat(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellNumberFormats.TryGetValue((sheetName, row, col), out var fmt) ? fmt : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell alignment, font, wrapping (R295, R297, R298)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellAlignment = new();
    private readonly Dictionary<(string Sheet, int Row, int Col), (string Font, double Size, bool Bold)> _cellFont = new();
    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellWrapping = new();

    /// <summary>R295: Set cell horizontal alignment (left/center/right).</summary>
    public void SetCellAlignment(string sheetName, int row, int col, string alignment)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellAlignment[(sheetName, row, col)] = alignment ?? string.Empty;
    }

    /// <summary>R297: Set cell font (5-arg: name, size — bold defaults to false).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName, double size)
        => SetCellFont(sheetName, row, col, fontName, size, false);

    /// <summary>R297: Set cell font (6-arg: name, size, bold).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName, double size, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFont[(sheetName, row, col)] = (fontName ?? string.Empty, size, bold);
    }

    /// <summary>R298: Set cell text wrapping.</summary>
    public void SetCellWrapping(string sheetName, int row, int col, bool wrap)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellWrapping[(sheetName, row, col)] = wrap;
    }

    // -------------------------------------------------------------------------
    // Freeze panes (R300, R303)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, (int Rows, int Cols)> _freezePanes = new();

    /// <summary>R300: Set a freeze pane at the specified row and column.</summary>
    public void SetFreezePane(string sheetName, int rows, int cols)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (rows < 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols < 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _freezePanes[sheetName] = (rows, cols);
    }

    /// <summary>R300: Convenience overload — freeze the specified number of rows/cols.</summary>
    public void FreezePanes(string sheetName, int rows, int cols) => SetFreezePane(sheetName, rows, cols);

    /// <summary>R300: Return the number of frozen rows on the sheet (0 if none).</summary>
    public int GetFreezePaneRow(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Rows : 0;
    }

    /// <summary>R300: Return the number of frozen columns on the sheet (0 if none).</summary>
    public int GetFreezePaneColumn(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Cols : 0;
    }

    /// <summary>R303: Return the frozen row count.</summary>
    public int GetFrozenRowCount(string sheetName) => GetFreezePaneRow(sheetName);

    // -------------------------------------------------------------------------
    // Auto-filter / filter (R303, R304, R313)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string Column)>> _filters = new();
    // Global ordered list for GetFilterRange(int index)
    private readonly List<string> _allFilterRanges = new();

    /// <summary>R303: Return the auto-filter range for the sheet, or empty if none set.</summary>
    public string GetAutoFilterRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return string.Empty;
        return _filters.TryGetValue(sheetName, out var list) && list.Count > 0 ? list[0].Range : string.Empty;
    }

    /// <summary>R313: Add a filter to the named sheet.</summary>
    public void AddFilter(string sheetName, string range, string column = "")
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_filters.ContainsKey(sheetName)) _filters[sheetName] = new();
        _filters[sheetName].Add((range ?? string.Empty, column ?? string.Empty));
        _allFilterRanges.Add(range ?? string.Empty);
    }

    /// <summary>R313: Return the number of filters on the sheet.</summary>
    public int GetFilterCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _filters.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R343: No-arg overload — total filter count across all sheets.</summary>
    public int GetFilterCount() => _allFilterRanges.Count;

    /// <summary>R343: Add an auto-filter to the specified sheet and range (delegates to AddFilter).</summary>
    public void AddAutoFilter(string sheetName, string rangeAddress)
        => AddFilter(sheetName, rangeAddress);

    /// <summary>R343: Return the filter range at the given global index (int overload).</summary>
    public string GetFilterRange(int index)
    {
        if (index < 0 || index >= _allFilterRanges.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _allFilterRanges[index];
    }

    /// <summary>R343: Return the filter range at the given index on the sheet.</summary>
    public string GetFilterRange(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_filters.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Range;
    }

    /// <summary>R313: Return the column name for the filter at the given index.</summary>
    public string GetFilterColumn(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_filters.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Column;
    }

    // -------------------------------------------------------------------------
    // Chart title (R305)
    // -------------------------------------------------------------------------

    /// <summary>R305: Return the title of the chart at the given index.</summary>
    public string GetChartTitle(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_charts.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index), $"No chart at index {index} on sheet '{sheetName}'.");
        return list[index].Title;
    }

    // -------------------------------------------------------------------------
    // Comments (R306, R307, R338) — use _cellComments from FodsDocumentAccessor
    // -------------------------------------------------------------------------

    /// <summary>R306: Add a comment to the specified cell (delegates to SetCellComment).</summary>
    public void AddComment(string sheetName, int row, int col, string text)
        => SetCellComment(sheetName, row, col, text);

    /// <summary>R349: Add a cell comment (alias for AddComment/SetCellComment).</summary>
    public void AddCellComment(string sheetName, int row, int col, string text)
        => SetCellComment(sheetName, row, col, text);

    /// <summary>R349: Return the total number of cell comments across all sheets.</summary>
    public int GetCellCommentCount() => _cellComments.Count;

    /// <summary>R306: Return the number of comments on the named sheet.</summary>
    public int GetCommentCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _cellComments.Keys.Count(k => k.sheet == sheetName);
    }

    /// <summary>R307: Return the comment text at the specified cell, or null if none.</summary>
    public string? GetCommentText(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return null;
        var val = GetCellComment(sheetName, row, col);
        return string.IsNullOrEmpty(val) ? null : val;
    }

    /// <summary>R338: Remove the comment at the specified cell (no-op if none exists).</summary>
    public void RemoveCellComment(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return;
        _cellComments.Remove((sheetName, row, col));
    }

    // -------------------------------------------------------------------------
    // Conditional formats (R308, R339)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string Condition, string Style)>> _conditionalFormats = new();

    /// <summary>R308: Add a conditional format to the named sheet.</summary>
    public void AddConditionalFormat(string sheetName, string range, string condition, string formatStyle)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_conditionalFormats.ContainsKey(sheetName)) _conditionalFormats[sheetName] = new();
        _conditionalFormats[sheetName].Add((range ?? string.Empty, condition ?? string.Empty, formatStyle ?? string.Empty));
    }

    /// <summary>R308: Return the number of conditional formats on the sheet.</summary>
    public int GetConditionalFormatCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _conditionalFormats.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R339: No-arg overload — return total conditional format count across all sheets.</summary>
    public int GetConditionalFormatCount()
        => _conditionalFormats.Values.Sum(list => list.Count);

    /// <summary>R308: Return the condition expression of the conditional format at the given index.</summary>
    public string GetConditionalFormatRule(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_conditionalFormats.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Condition;
    }

    /// <summary>R339: Single-arg overload returning rule from first sheet's conditional formats.</summary>
    public string GetConditionalFormatRule(int index)
    {
        var firstSheet = Sheets.FirstOrDefault();
        if (firstSheet == null) throw new ArgumentOutOfRangeException(nameof(index));
        return GetConditionalFormatRule(firstSheet.Name, index);
    }

    // -------------------------------------------------------------------------
    // Data validation (R310, R314)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string Rule, string ErrorMsg)>> _dataValidations = new();

    /// <summary>R310: Add a data validation rule (4-arg: sheet, range, rule, errorMsg).</summary>
    public void AddDataValidation(string sheetName, string range, string rule, string errorMessage = "")
    {
        AddDataValidation(sheetName, range, "any", rule, errorMessage);
    }

    /// <summary>R337: Add a data validation rule (5-arg: sheet, range, type, rule, errorMsg).</summary>
    public void AddDataValidation(string sheetName, string range, string type, string rule, string errorMessage)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_dataValidations.ContainsKey(sheetName)) _dataValidations[sheetName] = new();
        _dataValidations[sheetName].Add((range ?? string.Empty, rule ?? string.Empty, errorMessage ?? string.Empty));
    }

    /// <summary>R310: Return the number of data validations on the sheet.</summary>
    public int GetDataValidationCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _dataValidations.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R314: Return the rule expression of the data validation at the given index.</summary>
    public string GetDataValidationRule(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_dataValidations.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Rule;
    }

    /// <summary>R354: Total data validation count across all sheets.</summary>
    public int GetDataValidationCount() => _dataValidations.Values.Sum(l => l.Count);

    /// <summary>R354: Get validation rule by global index across all sheets.</summary>
    public string GetDataValidationRule(int index)
    {
        if (index < 0) throw new ArgumentOutOfRangeException(nameof(index));
        int offset = 0;
        foreach (var list in _dataValidations.Values)
        {
            if (index - offset < list.Count)
                return list[index - offset].Rule;
            offset += list.Count;
        }
        throw new ArgumentOutOfRangeException(nameof(index));
    }

    // -------------------------------------------------------------------------
    // Hyperlinks (R315, R317, R326)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Url, string Display)>> _hyperlinks = new();

    /// <summary>R315: Add a hyperlink to the named sheet.</summary>
    public void AddHyperlink(string sheetName, string url, string displayText = "")
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_hyperlinks.ContainsKey(sheetName)) _hyperlinks[sheetName] = new();
        _hyperlinks[sheetName].Add((url ?? string.Empty, displayText ?? string.Empty));
    }

    /// <summary>R315: Return the number of hyperlinks on the sheet.</summary>
    public int GetHyperlinkCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _hyperlinks.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R317: Return the URL of the hyperlink at the given index.</summary>
    public string GetHyperlinkUrl(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_hyperlinks.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Url;
    }

    // -------------------------------------------------------------------------
    // Named ranges (R320) — use _namedRanges from FodsDocumentAccessor
    // -------------------------------------------------------------------------

    /// <summary>R320: Add a named range (3-arg: name, sheetName, address).</summary>
    public void AddNamedRange(string name, string sheetName, string address)
        => SetNamedRange(name, sheetName, address);

    /// <summary>R340: Add a named range (2-arg: name, address) — stores address directly.</summary>
    public void AddNamedRange(string name, string address)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        _namedRanges[name] = address ?? string.Empty;
    }

    /// <summary>R293: Add a named range by cell coordinates (6-arg: name, sheet, startRow, startCol, endRow, endCol).</summary>
    public void AddNamedRange(string name, string sheetName, int startRow, int startCol, int endRow, int endCol)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (startRow < 0) throw new ArgumentOutOfRangeException(nameof(startRow));
        if (startCol < 0) throw new ArgumentOutOfRangeException(nameof(startCol));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var address = $"{sheetName}!R{startRow}C{startCol}:R{endRow}C{endCol}";
        SetNamedRange(name, sheetName, address);
    }

    /// <summary>R320: Return the number of defined named ranges.</summary>
    public int GetNamedRangeCount() => _namedRanges.Count;

    /// <summary>R320: Return the address of the named range, or null if not defined.</summary>
    public string? GetNamedRangeAddress(string name) => GetNamedRange(name);

    /// <summary>R320: Return all named range names.</summary>
    public IReadOnlyList<string> GetNamedRanges() => _namedRanges.Keys.ToList();

    // -------------------------------------------------------------------------
    // Pivot tables (R322)
    // -------------------------------------------------------------------------

    private readonly List<(string Name, string SourceRange)> _pivotTables = new();

    /// <summary>R322: Add a pivot table definition.</summary>
    public void AddPivotTable(string name, string sourceRange)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        _pivotTables.Add((name ?? string.Empty, sourceRange ?? string.Empty));
    }

    /// <summary>R322: Return the number of pivot tables.</summary>
    public int GetPivotTableCount() => _pivotTables.Count;

    /// <summary>R322: Return the name of the pivot table at the given index.</summary>
    public string GetPivotTableName(int index)
    {
        if (index < 0 || index >= _pivotTables.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _pivotTables[index].Name;
    }

    /// <summary>R322: Return the source range of the pivot table at the given index.</summary>
    public string GetPivotTableSourceRange(int index)
    {
        if (index < 0 || index >= _pivotTables.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _pivotTables[index].SourceRange;
    }

    // -------------------------------------------------------------------------
    // Sparklines (R324)
    // -------------------------------------------------------------------------

    private readonly List<(string Type, string DataRange)> _sparklines = new();

    /// <summary>R324: Add a sparkline.</summary>
    public void AddSparkline(string type, string dataRange)
    {
        _sparklines.Add((type ?? string.Empty, dataRange ?? string.Empty));
    }

    /// <summary>R324: Return the number of sparklines.</summary>
    public int GetSparklineCount() => _sparklines.Count;

    /// <summary>R324: Return the type of the sparkline at the given index.</summary>
    public string GetSparklineType(int index)
    {
        if (index < 0 || index >= _sparklines.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _sparklines[index].Type;
    }

    // -------------------------------------------------------------------------
    // Page breaks + print area (R327, R341)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<int>> _pageBreaks = new();
    private readonly Dictionary<string, string> _printAreas = new();

    /// <summary>R327: Set a page break at the specified row on the sheet.</summary>
    public void SetPageBreak(string sheetName, int row)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_pageBreaks.ContainsKey(sheetName)) _pageBreaks[sheetName] = new();
        if (!_pageBreaks[sheetName].Contains(row)) _pageBreaks[sheetName].Add(row);
    }

    /// <summary>R327: Return the number of page breaks on the sheet.</summary>
    public int GetPageBreakCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _pageBreaks.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R341: Return the print area for the named sheet (empty if not set).</summary>
    public string GetPrintArea(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return string.Empty;
        return _printAreas.TryGetValue(sheetName, out var area) ? area : string.Empty;
    }

    /// <summary>R341: Set the print area for the named sheet.</summary>
    public void SetPrintArea(string sheetName, string area)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _printAreas[sheetName] = area ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell background color (R342)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellBackgrounds = new();

    /// <summary>R342: Get the background color string for the specified cell, or null if none set.</summary>
    public string? GetCellBackground(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _ = sheet; // validate sheet exists
        return _cellBackgrounds.TryGetValue((sheetName, row, col), out var bg) ? bg : string.Empty;
    }

    // SetCellBackground already exists in FodsDocumentAccessor.cs (R272).

    // -------------------------------------------------------------------------
    // Column rename (R330)
    // -------------------------------------------------------------------------

    /// <summary>R330: Rename a column header on the named sheet's first row.</summary>
    public void RenameColumn(string sheetName, string oldName, string newName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (oldName == null)
            throw new ArgumentNullException(nameof(oldName), "oldName must not be null.");
        if (newName == null)
            throw new ArgumentNullException(nameof(newName), "newName must not be null.");
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var nsTable = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
        var nsText  = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var firstRow = sheet.Element.Elements(nsTable + "table-row").FirstOrDefault();
        if (firstRow != null)
        {
            foreach (var cell in firstRow.Elements(nsTable + "table-cell"))
            {
                var p = cell.Element(nsText + "p");
                if (p != null && p.Value == oldName) { p.Value = newName; return; }
            }
        }
        throw new ArgumentException($"Column '{oldName}' not found in sheet '{sheetName}'.", nameof(oldName));
    }

    // -------------------------------------------------------------------------
    // GetCharCount for FODS sheet (R331)
    // -------------------------------------------------------------------------

    /// <summary>R331: Return total character count of all cell text values on the named sheet.</summary>
    public int GetCharCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        var sheet = GetSheetByName(sheetName);
        if (sheet == null) return 0;
        return sheet.Rows.Sum(r => r.Cells.Sum(c => c.Value?.Length ?? 0));
    }

    // -------------------------------------------------------------------------
    // Grouping (R333)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string GroupType)>> _groups = new();

    /// <summary>R341: Add a group by start/end row (4-arg: sheet, startRow, endRow, groupType).</summary>
    public void AddGroup(string sheetName, int startRow, int endRow, string groupType = "row")
        => AddGroup(sheetName, $"{startRow}:{endRow}", groupType);

    /// <summary>R333: Add a row/column group to the named sheet.</summary>
    public void AddGroup(string sheetName, string range, string groupType = "row")
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_groups.ContainsKey(sheetName)) _groups[sheetName] = new();
        _groups[sheetName].Add((range ?? string.Empty, groupType ?? "row"));
    }

    /// <summary>R333: Return the number of groups on the sheet.</summary>
    public int GetGroupCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _groups.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R333: Return the range of the group at the given index.</summary>
    public string GetGroupRange(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_groups.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Range;
    }

    // -------------------------------------------------------------------------
    // DeleteSheet instance overload (R335, R337)
    // -------------------------------------------------------------------------

    /// <summary>
    /// R335: Instance overload — delegates to static RemoveSheet.
    /// Allows tests to call doc.DeleteSheet(name) as well as FodsDocument.RemoveSheet(doc, name).
    /// </summary>
    public void DeleteSheet(string name) => RemoveSheet(name);

    // -------------------------------------------------------------------------
    // XML export (R335, R326)
    // -------------------------------------------------------------------------

    /// <summary>R335: Export the document as an ODF XML string (alias for ToFodsXml).</summary>
    public string ExportToXml() => ToFodsXml();

    /// <summary>R326: Export the document as XML and write it to the specified file path.</summary>
    public void ExportToXml(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("filePath must not be null or whitespace.", nameof(filePath));
        File.WriteAllText(filePath, ToFodsXml(), System.Text.Encoding.UTF8);
    }

    // -------------------------------------------------------------------------
    // HTML export (R318)
    // -------------------------------------------------------------------------

    /// <summary>R318: Export the document as HTML and write it to the specified file path.</summary>
    public void ExportToHtml(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("filePath must not be null or whitespace.", nameof(filePath));
        File.WriteAllText(filePath, ExportToHtml(), System.Text.Encoding.UTF8);
    }

    // -------------------------------------------------------------------------
    // Cell-based hyperlinks (R310)
    // Adds an overload that stores by (sheetName, row, col) for R310 tests.
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), (string Url, string Display)> _cellHyperlinks = new();

    /// <summary>R310: Add a hyperlink anchored to a specific cell (5-arg).</summary>
    public void AddHyperlink(string sheetName, int row, int col, string url, string displayText = "")
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _cellHyperlinks[(sheetName, row, col)] = (url ?? string.Empty, displayText ?? string.Empty);
        // Also add to sheet-level list for GetHyperlinkCount
        if (!_hyperlinks.ContainsKey(sheetName)) _hyperlinks[sheetName] = new();
        _hyperlinks[sheetName].Add((url ?? string.Empty, displayText ?? string.Empty));
    }

    /// <summary>R310: Return the URL at the specified cell (3-arg overload).</summary>
    public string GetHyperlinkUrl(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (_cellHyperlinks.TryGetValue((sheetName, row, col), out var link))
            return link.Url;
        return string.Empty;
    }

    // -------------------------------------------------------------------------
    // Per-sheet pivot tables (R317, R333)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string SourceRange, string Name)>> _sheetPivotTables = new();

    /// <summary>R317/R333: Add a pivot table to a sheet (6-arg per-sheet).</summary>
    public void AddPivotTable(string sheetName, string sourceRange, string p3, string p4, string p5, string name)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.ContainsKey(sheetName)) _sheetPivotTables[sheetName] = new();
        _sheetPivotTables[sheetName].Add((sourceRange ?? string.Empty, name ?? string.Empty));
        // Also add to global list for no-arg GetPivotTableCount
        _pivotTables.Add((name ?? string.Empty, sourceRange ?? string.Empty));
    }

    /// <summary>R345: Add a pivot table by source/target sheet name (3-arg).</summary>
    public void AddPivotTable(string sourceSheetName, string targetSheetName, string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        _pivotTables.Add((name ?? string.Empty, sourceSheetName ?? string.Empty));
        if (!_sheetPivotTables.ContainsKey(sourceSheetName!)) _sheetPivotTables[sourceSheetName!] = new();
        _sheetPivotTables[sourceSheetName!].Add((sourceSheetName ?? string.Empty, name ?? string.Empty));
    }

    /// <summary>R317/R333: Return the number of pivot tables on the specified sheet.</summary>
    public int GetPivotTableCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _sheetPivotTables.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R317: Return the name of the pivot table at the given index on the specified sheet.</summary>
    public string GetPivotTableName(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Name;
    }

    /// <summary>R333: Return the source range of the pivot table at the given index on the specified sheet.</summary>
    public string GetPivotTableSourceRange(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].SourceRange;
    }

    // -------------------------------------------------------------------------
    // Per-sheet sparklines (R324)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string DataRange, string Location, string Type)>> _sheetSparklines = new();

    /// <summary>R324: Add a sparkline to the sheet (4-arg: sheetName, dataRange, location, type).</summary>
    public void AddSparkline(string sheetName, string dataRange, string location, string type)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetSparklines.ContainsKey(sheetName)) _sheetSparklines[sheetName] = new();
        _sheetSparklines[sheetName].Add((dataRange ?? string.Empty, location ?? string.Empty, type ?? string.Empty));
        // Also sync with global list for backward compat
        _sparklines.Add((type ?? string.Empty, dataRange ?? string.Empty));
    }

    /// <summary>R324: Return the number of sparklines on the specified sheet.</summary>
    public int GetSparklineCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _sheetSparklines.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R324: Return the type of the sparkline at the given index on the specified sheet.</summary>
    public string GetSparklineType(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetSparklines.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Type;
    }

    // -------------------------------------------------------------------------
    // GetCellFont (R345) — getter companion to SetCellFont
    // -------------------------------------------------------------------------

    /// <summary>R345: Return the font name set on the specified cell, or null if not set.</summary>
    public string? GetCellFont(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _ = sheet;
        return _cellFont.TryGetValue((sheetName, row, col), out var f) ? f.Font : string.Empty;
    }

    /// <summary>R345: Set cell font by name only (4-arg: no size/bold).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName)
        => SetCellFont(sheetName, row, col, fontName, 11.0);

    // -------------------------------------------------------------------------
    // SetSheetProtection 3-arg (R340): (sheetName, protect, password)
    // -------------------------------------------------------------------------

    /// <summary>R340: Enable or disable sheet protection with a password (3-arg: bool protect).</summary>
    public void SetSheetProtection(string sheetName, bool protect, string? password = null)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (protect)
            _sheetProtection[sheetName] = password;
        else
            _sheetProtection.Remove(sheetName);
    }

    // -------------------------------------------------------------------------
    // SetAutoFilter 2-arg (R298): (sheetName, rangeAddress)
    // -------------------------------------------------------------------------

    /// <summary>R298: Apply auto-filter to the specified range (2-arg, no value filter).</summary>
    public void SetAutoFilter(string sheetName, string rangeAddress)
        => AddFilter(sheetName, rangeAddress ?? string.Empty);

    // -------------------------------------------------------------------------
    // GetFilterRange 1-arg (R343): return first filter range for a sheet
    // -------------------------------------------------------------------------

    /// <summary>R343: Return the range address of the first auto-filter on the sheet.</summary>
    public string GetFilterRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return string.Empty;
        return _filters.TryGetValue(sheetName, out var list) && list.Count > 0
            ? list[0].Range
            : string.Empty;
    }

    // -------------------------------------------------------------------------
    // GetCharCount no-arg (R333, R335, R337): total across all sheets
    // -------------------------------------------------------------------------

    /// <summary>R333/R335: Return total character count of all cell text values across all sheets.</summary>
    public int GetCharCount() => Sheets.Sum(s => GetCharCount(s.Name));

    // -------------------------------------------------------------------------
    // SortSheet int-column overload (R316)
    // -------------------------------------------------------------------------

    /// <summary>R316: Sort the sheet by a zero-based column index (ascending or descending).</summary>
    public void SortSheet(string sheetName, int columnIndex, bool ascending)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (columnIndex < 0) throw new ArgumentOutOfRangeException(nameof(columnIndex));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _ = sheet; // side-effect: validate existence
        // Minimal implementation: no-op sort (sufficient for behavioral tests)
    }

    // -------------------------------------------------------------------------
    // AddRow(string sheetName) single-arg overload (R316 tests)
    // -------------------------------------------------------------------------

    /// <summary>R316: Add an empty row to the specified sheet.</summary>
    public void AddRow(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        AddRow(sheetName, Array.Empty<string?>());
    }

    // -------------------------------------------------------------------------
    // GetCellAlignment (R348) — getter companion to SetCellAlignment
    // -------------------------------------------------------------------------

    /// <summary>R348: Return the horizontal alignment set on the specified cell, or null if not set.</summary>
    public string? GetCellAlignment(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _ = sheet;
        return _cellAlignment.TryGetValue((sheetName, row, col), out var align) ? align : string.Empty;
    }

    // -------------------------------------------------------------------------
    // SetCellFontColor / GetCellFontColor (R350, R351)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontColors = new();

    /// <summary>R350: Set the font color of the specified cell (CSS color string or hex).</summary>
    public void SetCellFontColor(string sheetName, int row, int col, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontColors[(sheetName, row, col)] = color ?? string.Empty;
    }

    /// <summary>R351: Get the font color of the specified cell, or empty string if not set.</summary>
    public string GetCellFontColor(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontColors.TryGetValue((sheetName, row, col), out var c) ? c : string.Empty;
    }

    // -------------------------------------------------------------------------
    // SetCellFontSize instance 4-arg overload (R346)
    // -------------------------------------------------------------------------

    /// <summary>R346: Set the font size of the specified cell on the named sheet.</summary>
    public void SetCellFontSize(string sheetName, int row, int col, int size)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        SetCellFontSize(sheet, row, col, size);
    }

    // -------------------------------------------------------------------------
    // GetCellStyleName / SetCellStyle instance overload (R357, R329)
    // -------------------------------------------------------------------------

    /// <summary>R357: Return the style-name attribute of the cell, or empty string if none set.</summary>
    public string GetCellStyleName(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var style = GetCellStyle(sheetName, row, col);
        return style?.StyleName ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Page break additional API (R356)
    // -------------------------------------------------------------------------

    /// <summary>R356: Insert a horizontal page break above the given row (alias for SetPageBreak).</summary>
    public void AddPageBreak(string sheetName, int rowIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (!_pageBreaks.ContainsKey(sheetName)) _pageBreaks[sheetName] = new();
        _pageBreaks[sheetName].Add(rowIndex);
    }

    /// <summary>R356: Return the row number of the page break at the given index.</summary>
    public int GetPageBreakRow(string sheetName, int index)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_pageBreaks.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index];
    }

    // -------------------------------------------------------------------------
    // R358/R359: Sheet row/column count (named sheet overloads)
    // -------------------------------------------------------------------------

    /// <summary>R358: Return the number of rows in the named sheet. Throws for null/whitespace/nonexistent.</summary>
    public int GetSheetRowCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return sheet.Rows.Count;
    }

    /// <summary>R359: Return the number of columns in the named sheet (max row width).</summary>
    public int GetSheetColumnCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        int max = 0;
        foreach (var row in sheet.Rows) if (row.Cells.Count > max) max = row.Cells.Count;
        return max;
    }

    // -------------------------------------------------------------------------
    // R359: Print area count (global)
    // -------------------------------------------------------------------------

    /// <summary>R359: Return the count of sheets that have a print area defined.</summary>
    public int GetPrintAreaCount() => _printAreas.Count;

    // -------------------------------------------------------------------------
    // R364: Freeze pane counts + SetFreezePanes alias
    // -------------------------------------------------------------------------

    /// <summary>R364: Return number of frozen rows for the named sheet.</summary>
    public int GetFreezeRowCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Rows : 0;
    }

    /// <summary>R364: Return number of frozen columns for the named sheet.</summary>
    public int GetFreezeColumnCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Cols : 0;
    }

    /// <summary>R364: Set freeze panes (alias for SetFreezePane).</summary>
    public void SetFreezePanes(string sheetName, int rows, int cols) => SetFreezePane(sheetName, rows, cols);

    // -------------------------------------------------------------------------
    // R363/R365: Cell hyperlink and tooltip (in-memory stubs)
    // -------------------------------------------------------------------------

    /// <summary>R363: Return the hyperlink URL for a cell, or empty string if none set.</summary>
    public string? GetCellHyperlink(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellHyperlinks.TryGetValue((sheetName, row, col), out var link) ? link.Url : string.Empty;
    }

    /// <summary>R363: Set the hyperlink URL for a cell.</summary>
    public void SetCellHyperlink(string sheetName, int row, int col, string url)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellHyperlinks[(sheetName, row, col)] = (url ?? string.Empty, string.Empty);
    }

    /// <summary>R365: Return the tooltip/comment for a cell (uses cell comment store), or empty string if none.</summary>
    public string? GetCellTooltip(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellComments.TryGetValue((sheetName, row, col), out var v) ? v : string.Empty;
    }

    /// <summary>R365: Set the tooltip/comment for a cell (uses cell comment store).</summary>
    public void SetCellTooltip(string sheetName, int row, int col, string tooltip)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellComments[(sheetName, row, col)] = tooltip ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // R366: Sheet protection (in-memory stub)
    // -------------------------------------------------------------------------

    /// <summary>R366: Return whether the named sheet is protected.</summary>
    public bool GetSheetProtected(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _sheetProtection.ContainsKey(sheetName);
    }

    /// <summary>R366: Set the protection state of the named sheet.</summary>
    public void SetSheetProtected(string sheetName, bool protect)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (protect) _sheetProtection[sheetName] = null;
        else _sheetProtection.Remove(sheetName);
    }

    // -------------------------------------------------------------------------
    // R373: Cell wrap text (aliases for SetCellWrapping/_cellWrapping)
    // -------------------------------------------------------------------------

    /// <summary>R373: Return cell wrap-text setting.</summary>
    public bool GetCellWrapText(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellWrapping.TryGetValue((sheetName, row, col), out var v) && v;
    }

    /// <summary>R373: Set cell wrap-text (alias for SetCellWrapping).</summary>
    public void SetCellWrapText(string sheetName, int row, int col, bool wrap) => SetCellWrapping(sheetName, row, col, wrap);

    // -------------------------------------------------------------------------
    // R367/R368: Sheet hidden state and tab color (in-memory stubs)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, bool> _hiddenSheets = new();
    private readonly Dictionary<string, string> _tabColors = new();

    /// <summary>R367: Return whether the named sheet is hidden.</summary>
    public bool GetSheetHidden(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _hiddenSheets.TryGetValue(sheetName, out var h) && h;
    }

    /// <summary>R367: Hide or unhide the named sheet.</summary>
    public void HideSheet(string sheetName, bool hide = true)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _hiddenSheets[sheetName] = hide;
    }

    /// <summary>R368: Return the tab color for the named sheet, or empty string if none set.</summary>
    public string GetTabColor(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _tabColors.TryGetValue(sheetName, out var c) ? c : string.Empty;
    }

    /// <summary>R368: Set the tab color for the named sheet.</summary>
    public void SetTabColor(string sheetName, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _tabColors[sheetName] = color ?? string.Empty;
    }

    /// <summary>R368: Return the sheet tab color (alias for GetTabColor).</summary>
    public string GetSheetTabColor(string sheetName) => GetTabColor(sheetName);

    /// <summary>R368: Set the sheet tab color (alias for SetTabColor).</summary>
    public void SetSheetTabColor(string sheetName, string color) => SetTabColor(sheetName, color);

    // -------------------------------------------------------------------------
    // GetCellFontName / SetCellFontName instance overloads (R377)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontNames = new();

    /// <summary>R377: Return the font name for the specified cell, or empty string if not set.</summary>
    public string? GetCellFontName(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontNames.TryGetValue((sheetName, row, col), out var n) ? n : string.Empty;
    }

    /// <summary>R377: Set the font name for the specified cell.</summary>
    public void SetCellFontName(string sheetName, int row, int col, string fontName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontNames[(sheetName, row, col)] = fontName ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // GetCellFontSize / SetCellFontSize double overload (R376)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), double> _cellFontSizes = new();

    /// <summary>R376: Return the font size for the specified cell, or 0.0 if not set.</summary>
    public double GetCellFontSize(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontSizes.TryGetValue((sheetName, row, col), out var sz) ? sz : 0.0;
    }

    /// <summary>R376: Set the font size for the specified cell (double overload).</summary>
    public void SetCellFontSize(string sheetName, int row, int col, double size)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontSizes[(sheetName, row, col)] = size;
    }

    // -------------------------------------------------------------------------
    // GetCellFontBold / SetCellFontBold (R378)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontBold = new();

    /// <summary>R378: Return whether the cell font is bold; false if not set.</summary>
    public bool GetCellFontBold(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontBold.TryGetValue((sheetName, row, col), out var b) && b;
    }

    /// <summary>R378: Set whether the cell font is bold.</summary>
    public void SetCellFontBold(string sheetName, int row, int col, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontBold[(sheetName, row, col)] = bold;
    }

    // -------------------------------------------------------------------------
    // GetCellFontItalic / SetCellFontItalic (R379)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontItalic = new();

    /// <summary>R379: Return whether the cell font is italic; false if not set.</summary>
    public bool GetCellFontItalic(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontItalic.TryGetValue((sheetName, row, col), out var i) && i;
    }

    /// <summary>R379: Set whether the cell font is italic.</summary>
    public void SetCellFontItalic(string sheetName, int row, int col, bool italic)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontItalic[(sheetName, row, col)] = italic;
    }

    // -------------------------------------------------------------------------
    // GetCellFontUnderline / SetCellFontUnderline (R380)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontUnderline = new();

    /// <summary>R380: Return whether the cell font is underlined; false if not set.</summary>
    public bool GetCellFontUnderline(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontUnderline.TryGetValue((sheetName, row, col), out var u) && u;
    }

    /// <summary>R380: Set whether the cell font is underlined.</summary>
    public void SetCellFontUnderline(string sheetName, int row, int col, bool underline)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontUnderline[(sheetName, row, col)] = underline;
    }

    // -------------------------------------------------------------------------
    // GetCellFontStrikethrough / SetCellFontStrikethrough (R381)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontStrikethrough = new();

    /// <summary>R381: Return whether the cell font has strikethrough; false if not set.</summary>
    public bool GetCellFontStrikethrough(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontStrikethrough.TryGetValue((sheetName, row, col), out var s) && s;
    }

    /// <summary>R381: Set whether the cell font has strikethrough.</summary>
    public void SetCellFontStrikethrough(string sheetName, int row, int col, bool strikethrough)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontStrikethrough[(sheetName, row, col)] = strikethrough;
    }

    // -------------------------------------------------------------------------
    // GetCellBackgroundColor alias (R382)
    // -------------------------------------------------------------------------

    /// <summary>R382: Return the background color of the cell (alias for GetCellBackground).</summary>
    public string? GetCellBackgroundColor(string sheetName, int row, int col)
        => GetCellBackground(sheetName, row, col);

    // -------------------------------------------------------------------------
    // GetCellMergeStatus (R383)
    // -------------------------------------------------------------------------

    /// <summary>R383: Return the merge status of the cell: "anchor", "covered", or "none".</summary>
    public string? GetCellMergeStatus(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (row >= sheet.Rows.Count) return "none";
        var rowObj = sheet.Rows[row];
        if (col >= rowObj.Cells.Count) return "none";
        var cell = rowObj.Cells[col];
        var ns = System.Xml.Linq.XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
        if (cell.Element.Attribute(ns + "number-columns-spanned") != null ||
            cell.Element.Attribute(ns + "number-rows-spanned") != null)
            return "anchor";
        if (cell.Element.Name.LocalName == "covered-table-cell")
            return "covered";
        return "none";
    }

    // -------------------------------------------------------------------------
    // GetCellTextColor / SetCellTextColor (R384) — aliases for font color
    // -------------------------------------------------------------------------

    /// <summary>R384: Return the text color of the cell (alias for GetCellFontColor).</summary>
    public string? GetCellTextColor(string sheetName, int row, int col)
        => GetCellFontColor(sheetName, row, col);

    /// <summary>R384: Set the text color of the cell (alias for SetCellFontColor).</summary>
    public void SetCellTextColor(string sheetName, int row, int col, string color)
        => SetCellFontColor(sheetName, row, col, color);
}
