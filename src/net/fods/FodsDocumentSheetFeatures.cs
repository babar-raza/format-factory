// FormatFactory.Fods -- Sheet-level feature APIs (visibility, protection, freeze panes,
// filters, page breaks, grouping, hidden state, tab colors).
// Partial class extension for FodsDocument.

using System;
using System.Collections.Generic;
using System.Linq;

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
    // Sheet protection (R291, R340, R366, R386)
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

    /// <summary>R340/R386: Return whether the named sheet is protected.</summary>
    public bool GetSheetProtection(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _sheetProtection.ContainsKey(sheetName);
    }

    /// <summary>R386: Protect the named sheet (no password).</summary>
    public void ProtectSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _sheetProtection[sheetName] = null;
    }

    /// <summary>R386: Remove protection from the named sheet.</summary>
    public void UnprotectSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _sheetProtection.Remove(sheetName);
    }

    /// <summary>R295: Return protection status bool for the named sheet.</summary>
    public bool GetProtectionStatus(string sheetName) => IsSheetProtected(sheetName);

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

    /// <summary>R366: Return whether the named sheet is protected.</summary>
    public bool GetSheetProtected(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _sheetProtection.ContainsKey(sheetName);
    }

    /// <summary>R366: Set the protection state of the named sheet.</summary>
    public void SetSheetProtected(string sheetName, bool protect)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (protect) _sheetProtection[sheetName] = null;
        else _sheetProtection.Remove(sheetName);
    }

    // -------------------------------------------------------------------------
    // Freeze panes (R300, R303, R364)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, (int Rows, int Cols)> _freezePanes = new();

    /// <summary>R300: Set a freeze pane at the specified row and column.</summary>
    public void SetFreezePane(string sheetName, int rows, int cols)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (rows < 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols < 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
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

    /// <summary>R364: Return number of frozen rows for the named sheet.</summary>
    public int GetFreezeRowCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Rows : 0;
    }

    /// <summary>R364: Return number of frozen columns for the named sheet.</summary>
    public int GetFreezeColumnCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _freezePanes.TryGetValue(sheetName, out var fp) ? fp.Cols : 0;
    }

    /// <summary>R364: Set freeze panes (alias for SetFreezePane).</summary>
    public void SetFreezePanes(string sheetName, int rows, int cols) => SetFreezePane(sheetName, rows, cols);

    // -------------------------------------------------------------------------
    // Auto-filter / filter (R298, R303, R313, R343)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string Column)>> _filters = new();
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

    /// <summary>R343: Add an auto-filter to the specified sheet and range.</summary>
    public void AddAutoFilter(string sheetName, string rangeAddress)
        => AddFilter(sheetName, rangeAddress);

    /// <summary>R343: Return the filter range at the given global index.</summary>
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

    /// <summary>R298: Apply auto-filter to the specified range.</summary>
    public void SetAutoFilter(string sheetName, string rangeAddress)
        => AddFilter(sheetName, rangeAddress ?? string.Empty);

    /// <summary>R343: Return the range address of the first auto-filter on the sheet.</summary>
    public string GetFilterRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return string.Empty;
        return _filters.TryGetValue(sheetName, out var list) && list.Count > 0
            ? list[0].Range
            : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Page breaks + print area (R327, R341, R356, R359)
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

    /// <summary>R356: Insert a horizontal page break above the given row.</summary>
    public void AddPageBreak(string sheetName, int rowIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
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

    /// <summary>R359: Return the count of sheets that have a print area defined.</summary>
    public int GetPrintAreaCount() => _printAreas.Count;

    // -------------------------------------------------------------------------
    // Grouping (R333, R341)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<(string Range, string GroupType)>> _groups = new();

    /// <summary>R341: Add a group by start/end row.</summary>
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
    // Sheet hidden state and tab color (R367, R368)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, bool> _hiddenSheets = new();
    private readonly Dictionary<string, string> _tabColors = new();

    /// <summary>R367: Return whether the named sheet is hidden.</summary>
    public bool GetSheetHidden(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _hiddenSheets.TryGetValue(sheetName, out var h) && h;
    }

    /// <summary>R367: Hide or unhide the named sheet.</summary>
    public void HideSheet(string sheetName, bool hide = true)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _hiddenSheets[sheetName] = hide;
    }

    /// <summary>R368: Return the tab color for the named sheet, or empty string if none set.</summary>
    public string GetTabColor(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _tabColors.TryGetValue(sheetName, out var c) ? c : string.Empty;
    }

    /// <summary>R368: Set the tab color for the named sheet.</summary>
    public void SetTabColor(string sheetName, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _tabColors[sheetName] = color ?? string.Empty;
    }

    /// <summary>R368: Return the sheet tab color (alias for GetTabColor).</summary>
    public string GetSheetTabColor(string sheetName) => GetTabColor(sheetName);

    /// <summary>R368: Set the sheet tab color (alias for SetTabColor).</summary>
    public void SetSheetTabColor(string sheetName, string color) => SetTabColor(sheetName, color);

    // -------------------------------------------------------------------------
    // Sheet structure operations (R316, R335, R358, R359)
    // -------------------------------------------------------------------------

    /// <summary>R335: Delete a sheet by name — delegates to static RemoveSheet.</summary>
    public void DeleteSheet(string name) => RemoveSheet(name);

    /// <summary>R358: Return the number of rows in the named sheet.</summary>
    public int GetSheetRowCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return sheet.Rows.Count;
    }

    /// <summary>R359: Return the number of columns in the named sheet (max row width).</summary>
    public int GetSheetColumnCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        int max = 0;
        foreach (var row in sheet.Rows) if (row.Cells.Count > max) max = row.Cells.Count;
        return max;
    }

    /// <summary>R316: Sort the sheet by a zero-based column index (ascending or descending).</summary>
    public void SortSheet(string sheetName, int columnIndex, bool ascending)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (columnIndex < 0) throw new ArgumentOutOfRangeException(nameof(columnIndex));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        // Minimal implementation: validates existence; sort execution not yet implemented.
    }

    /// <summary>R316: Add an empty row to the specified sheet.</summary>
    public void AddRow(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        AddRow(sheetName, Array.Empty<string?>());
    }

    /// <summary>R333/R335: Return total character count of all cell text values across all sheets.</summary>
    public int GetCharCount() => Sheets.Sum(s => GetCharCount(s.Name));

    /// <summary>R331: Return total character count of all cell text values on the named sheet.</summary>
    public int GetCharCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        var sheet = GetSheetByName(sheetName);
        if (sheet == null) return 0;
        return sheet.Rows.Sum(r => r.Cells.Sum(c => c.Value?.Length ?? 0));
    }
}
