// FormatFactory.Fods — FodsDocument sheet and cell property operations (partial class).
// Domain: GetSheetConfigItem (private), GetCellElement/Direct (private),
//         sheet metadata props (FreezeRows/Cols, ZoomLevel, PrintArea, Visibility, etc.),
//         cell style props (BorderStyle, FontStyle, HAlign, VAlign, Indent, Rotation,
//         MergeInfo, ShrinkToFit, Underline, Strikethrough, Protection),
//         and support classes ColumnStats/FodsUsedRange/FodsCellStyle/FodsDocumentStats/FodsSheetStats.
// Split from FodsDocumentAccessor.cs (TC-PQLM-021 decomposition).

using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // GI-FODS-NET-001: config:config-item namespace helper
    // =========================================================================

    /// <summary>
    /// GI-FODS-NET-001 — navigate office:settings to find a config:config-item
    /// for the given sheet name and item name.
    /// ODF real-world nesting (e.g. LibreOffice):
    ///   office:settings/config:config-item-set/config:config-item-map-indexed
    ///     /config:config-item-map-entry/config:config-item-map-named
    ///     /config:config-item-map-entry[@config:name=sheetName]
    ///     /config:config-item[@config:name=itemName]
    /// We use Descendants to handle any depth of wrapping.
    /// </summary>
    private string? GetSheetConfigItem(string sheetName, string itemName)
    {
        var settings = _doc.Root?.Element(NsOffice + "settings");
        if (settings is null) return null;
        foreach (var mapNamed in settings.Descendants(NsConfig + "config-item-map-named"))
        {
            foreach (var entry in mapNamed.Elements(NsConfig + "config-item-map-entry"))
            {
                if (entry.Attribute(NsConfig + "name")?.Value != sheetName) continue;
                var item = entry.Elements(NsConfig + "config-item")
                    .FirstOrDefault(ci => ci.Attribute(NsConfig + "name")?.Value == itemName);
                if (item is not null) return item.Value;
            }
        }
        return null;
    }

    // =========================================================================
    // GI-FODS-NET-001: Cell element access helpers for FodsStyleResolver
    // =========================================================================

    /// <summary>
    /// Validate sheet/row/col and return the XElement for the cell, or null if out of range.
    /// Guards: RequireSheet (throws), RequireNonNegative (throws). Out-of-range row/col → null.
    /// </summary>
    private XElement? GetCellElement(string sheetName, int row, int col)
    {
        var sheet = RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return GetCellElementDirect(sheetName, row, col, sheet);
    }

    /// <summary>
    /// Return the XElement for a cell without guard validation.
    /// The caller is responsible for having already validated sheetName/row/col.
    /// </summary>
    private XElement? GetCellElementDirect(string sheetName, int row, int col, FodsSheet? sheet = null)
    {
        sheet ??= GetSheetByName(sheetName);
        if (sheet is null || row >= sheet.Rows.Count) return null;
        var rowEl = sheet.Rows[row].Element;
        var cells = rowEl.Elements(NsTable + "table-cell").ToList();
        return col < cells.Count ? cells[col] : null;
    }

    // =========================================================================
    // Sheet metadata properties — dict-backed with ODF config read-through
    // GI-FODS-NET-001: Category B stubs; adds XML round-trip
    // =========================================================================

    /// <summary>R452: Return freeze row count for the named sheet.</summary>
    // GI-FODS-NET-001 — reads HorizontalSplitPosition from office:settings
    // when HorizontalSplitMode == 2 (freeze). In-memory setter override takes priority.
    public int GetSheetFreezeRows(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetFreezeRows.TryGetValue(sheetName, out var ov)) return ov;
        var mode = GetSheetConfigItem(sheetName, "HorizontalSplitMode");
        if (mode != "2") return 0;
        var pos = GetSheetConfigItem(sheetName, "HorizontalSplitPosition");
        return pos is not null && int.TryParse(pos, out var p) ? p : 0;
    }

    /// <summary>R452: Set freeze rows for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 — write to office:settings/config:config-item
    public void SetSheetFreezeRows(string sheetName, int rows)
    {
        RequireSheet(sheetName);
        if (rows < 0) throw new ArgumentOutOfRangeException(nameof(rows));
        _sheetFreezeRows[sheetName] = rows;
    }

    /// <summary>R453: Return freeze column count for the named sheet.</summary>
    // GI-FODS-NET-001 — reads VerticalSplitPosition from office:settings
    // when VerticalSplitMode == 2 (freeze). In-memory setter override takes priority.
    public int GetSheetFreezeColumns(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetFreezeColumns.TryGetValue(sheetName, out var ov)) return ov;
        var mode = GetSheetConfigItem(sheetName, "VerticalSplitMode");
        if (mode != "2") return 0;
        var pos = GetSheetConfigItem(sheetName, "VerticalSplitPosition");
        return pos is not null && int.TryParse(pos, out var p) ? p : 0;
    }

    /// <summary>R453: Set freeze columns for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 — write to office:settings/config:config-item
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

    /// <summary>R420/R480: Return the zoom level for the named sheet (default 100).</summary>
    // GI-FODS-NET-001 — reads ZoomValue from office:settings.
    // In-memory setter override takes priority; ODF default is 100.
    public int GetSheetZoomLevel(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetZoomLevel.TryGetValue(sheetName, out var ov)) return ov;
        var val = GetSheetConfigItem(sheetName, "ZoomValue");
        return val is not null && int.TryParse(val, out var z) ? z : 100;
    }

    /// <summary>R454/R480: Set the zoom level for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 — write to office:settings/config:config-item
    public void SetSheetZoomLevel(string sheetName, int zoom)
    {
        RequireSheet(sheetName);
        _sheetZoomLevel[sheetName] = zoom;
    }

    /// <summary>R423/R451: Return the print area for the named sheet (empty string if none).</summary>
    // TODO: GI-FODS-NET-001 — read from table:named-range[@table:print-range]
    public string GetSheetPrintArea(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetPrintArea.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R451/R484: Set the print area for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 — write table:named-range to ODF XML
    public void SetSheetPrintArea(string sheetName, string area)
    {
        RequireSheet(sheetName);
        _sheetPrintArea[sheetName] = area ?? string.Empty;
    }

    /// <summary>R469: Return the protection password for the named sheet (empty string if none).</summary>
    // TODO: GI-FODS-NET-001 — read from table:table/@table:protection-key
    public string GetSheetProtectionPassword(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetProtectionPasswords.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R469: Set the protection password for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 — write to ODF XML protection attributes
    public void SetSheetProtectionPassword(string sheetName, string password)
    {
        RequireSheet(sheetName);
        _sheetProtectionPasswords[sheetName] = password ?? string.Empty;
    }

    /// <summary>R465: Return the visibility string for the sheet ("visible" by default).</summary>
    // TODO: GI-FODS-NET-001 — read from table:table/@table:display
    public string GetSheetVisibility(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetVisibility.TryGetValue(sheetName, out var v) ? v : "visible";
    }

    /// <summary>R465: Set the visibility string for the sheet.</summary>
    // TODO: GI-FODS-NET-001 — write to table:table/@table:display
    public void SetSheetVisibility(string sheetName, string visibility)
    {
        RequireSheet(sheetName);
        _sheetVisibility[sheetName] = visibility ?? "visible";
    }

    /// <summary>R481: Return right-to-left flag for the named sheet (default false).</summary>
    // TODO: GI-FODS-NET-001 — read from sheet style/@style:writing-mode
    public bool GetSheetRightToLeft(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetRightToLeft.TryGetValue(sheetName, out var v) && v;
    }

    /// <summary>R482: Return show-grid flag for the named sheet (default true).</summary>
    // GI-FODS-NET-001 — reads ShowGrid from office:settings.
    // In-memory setter override takes priority; ODF default is true.
    public bool GetSheetShowGrid(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetShowGrid.TryGetValue(sheetName, out var ov)) return ov;
        var val = GetSheetConfigItem(sheetName, "ShowGrid");
        if (val is null) return true;
        return !string.Equals(val, "false", StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>R483: Return show-headers flag for the named sheet (default true).</summary>
    // GI-FODS-NET-001 — reads HasColumnRowHeaders from office:settings.
    // In-memory setter override takes priority; ODF default is true.
    public bool GetSheetShowHeaders(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetShowHeaders.TryGetValue(sheetName, out var ov)) return ov;
        var val = GetSheetConfigItem(sheetName, "HasColumnRowHeaders");
        if (val is null) return true;
        return !string.Equals(val, "false", StringComparison.OrdinalIgnoreCase);
    }

    // =========================================================================
    // Cell style properties — dict-backed with ODF style chain read-through
    // =========================================================================

    /// <summary>R417: Return the border style for the cell (empty string if none). ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@fo:border. GI-FODS-NET-001.</remarks>
    public string GetCellBorderStyle(string sheetName, int row, int col)
    {
        if (_cellBorderStyles.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? string.Empty : (FodsStyleResolver.ResolveCellStyle(_doc, cellEl).BorderStyle ?? string.Empty);
    }

    /// <summary>R457: Set the border style for the cell. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellBorderStyle(string sheetName, int row, int col, string style)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        style ??= string.Empty;
        _cellBorderStyles[(sheetName, row, col)] = style;
        if (cellEl is not null && !string.IsNullOrEmpty(style))
            FodsStyleEditor.SetCellBorderStyle(_doc, cellEl, style);
    }

    /// <summary>R472: Return the font style string for the cell (default "normal").</summary>
    // TODO: GI-FODS-NET-001 — read via FodsStyleResolver from style:text-properties
    public string GetCellFontStyle(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellFontStyles.TryGetValue((sheetName, row, col), out var v) ? v : "normal";
    }

    /// <summary>R472: Set the font style string for the cell.</summary>
    // TODO: GI-FODS-NET-001 — write via FodsStyleEditor to ODF XML
    public void SetCellFontStyle(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellFontStyles[(sheetName, row, col)] = style ?? "normal";
    }

    /// <summary>R455: Return the horizontal alignment for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.11 style:paragraph-properties/@fo:text-align. GI-FODS-NET-001.</remarks>
    public string GetCellHorizontalAlignment(string sheetName, int row, int col)
    {
        if (_cellHAlign.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "start" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).HorizontalAlignment;
    }

    /// <summary>R455: Set the horizontal alignment for the cell. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellHorizontalAlignment(string sheetName, int row, int col, string alignment)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        alignment ??= "start";
        _cellHAlign[(sheetName, row, col)] = alignment;
        if (cellEl is not null)
            FodsStyleEditor.SetCellHorizontalAlignment(_doc, cellEl, alignment);
    }

    /// <summary>R456: Return the vertical alignment for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:vertical-align. GI-FODS-NET-001.</remarks>
    public string GetCellVerticalAlignment(string sheetName, int row, int col)
    {
        if (_cellVAlign.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "bottom" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).VerticalAlignment;
    }

    /// <summary>R456: Set the vertical alignment for the cell. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellVerticalAlignment(string sheetName, int row, int col, string alignment)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        alignment ??= "bottom";
        _cellVAlign[(sheetName, row, col)] = alignment;
        if (cellEl is not null)
            FodsStyleEditor.SetCellVerticalAlignment(_doc, cellEl, alignment);
    }

    /// <summary>R467: Return the indent level for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.11 style:paragraph-properties/@fo:margin-left. GI-FODS-NET-001.</remarks>
    public int GetCellIndentLevel(string sheetName, int row, int col)
    {
        if (_cellIndentLevel.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? 0 : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).IndentLevel;
    }

    /// <summary>R467: Set the indent level for the cell. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellIndentLevel(string sheetName, int row, int col, int level)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        _cellIndentLevel[(sheetName, row, col)] = level;
        if (cellEl is not null)
            FodsStyleEditor.SetCellIndentLevel(_doc, cellEl, level);
    }

    /// <summary>R468: Return the rotation angle for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:rotation-angle. GI-FODS-NET-001.</remarks>
    public int GetCellRotationAngle(string sheetName, int row, int col)
    {
        if (_cellRotationAngle.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? 0 : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).RotationAngle;
    }

    /// <summary>R468: Set the rotation angle for the cell. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellRotationAngle(string sheetName, int row, int col, int angle)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        _cellRotationAngle[(sheetName, row, col)] = angle;
        if (cellEl is not null)
            FodsStyleEditor.SetCellRotationAngle(_doc, cellEl, angle);
    }

    /// <summary>R445: Return merge info from ODF span attributes on the cell element.</summary>
    /// <remarks>ODF 1.3 §9.4.5 table:table-cell/@table:number-rows-spanned. GI-FODS-NET-001.</remarks>
    public string GetCellMergeInfo(string sheetName, int row, int col)
    {
        if (_cellMergeInfo.TryGetValue((sheetName, row, col), out var cached)) return cached;
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        var cellEl = GetCellElementDirect(sheetName, row, col);
        if (cellEl is null) return "none";
        var rSpan = cellEl.Attribute(NsTable + "number-rows-spanned")?.Value;
        var cSpan = cellEl.Attribute(NsTable + "number-columns-spanned")?.Value;
        return (rSpan is null && cSpan is null) ? "none" : $"rows:{rSpan ?? "1"},cols:{cSpan ?? "1"}";
    }

    /// <summary>R475: Return column span from ODF attribute.</summary>
    /// <remarks>ODF 1.3 §9.4.5 table:table-cell/@table:number-columns-spanned. GI-FODS-NET-001.</remarks>
    public int GetCellMergeSpan(string sheetName, int row, int col)
    {
        if (_cellMergeSpan.TryGetValue((sheetName, row, col), out var cached)) return cached;
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        var cellEl = GetCellElementDirect(sheetName, row, col);
        if (cellEl is null) return 1;
        var cSpan = cellEl.Attribute(NsTable + "number-columns-spanned")?.Value;
        return cSpan is not null && int.TryParse(cSpan, out int span) ? span : 1;
    }

    /// <summary>R475: Set the column span for a merged cell (in-memory; persisted via).</summary>
    // TODO: GI-FODS-NET-001 — write to table:table-cell/@table:number-columns-spanned
    public void SetCellMergeSpan(string sheetName, int row, int col, int span)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellMergeSpan[(sheetName, row, col)] = span;
    }

    /// <summary>R450: Return the shrink-to-fit flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:shrink-to-fit. GI-FODS-NET-001.</remarks>
    public bool GetCellShrinkToFit(string sheetName, int row, int col)
    {
        if (_cellShrinkToFit.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is not null && FodsStyleResolver.ResolveCellStyle(_doc, cellEl).ShrinkToFit;
    }

    /// <summary>R450: Set the shrink-to-fit flag. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellShrinkToFit(string sheetName, int row, int col, bool shrink)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        _cellShrinkToFit[(sheetName, row, col)] = shrink;
        if (cellEl is not null)
            FodsStyleEditor.SetCellShrinkToFit(_doc, cellEl, shrink);
    }

    /// <summary>R471: Return the underline style. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.4 style:text-properties/@style:text-underline-style. GI-FODS-NET-001.</remarks>
    public string GetCellUnderline(string sheetName, int row, int col)
    {
        if (_cellUnderline.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "none" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).Underline;
    }

    /// <summary>R471: Set the underline style. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellUnderline(string sheetName, int row, int col, string style)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        style ??= "none";
        _cellUnderline[(sheetName, row, col)] = style;
        if (cellEl is not null)
            FodsStyleEditor.SetCellUnderline(_doc, cellEl, style);
    }

    /// <summary>R408: Return the strikethrough flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.4 style:text-properties/@style:text-line-through-style. GI-FODS-NET-001.</remarks>
    public bool GetCellStrikethrough(string sheetName, int row, int col)
    {
        if (_cellStrikethrough.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        if (cellEl is null) return false;
        var s = FodsStyleResolver.ResolveCellStyle(_doc, cellEl).Strikethrough;
        return s != "none" && !string.IsNullOrEmpty(s);
    }

    /// <summary>R470: Set the strikethrough flag. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellStrikethrough(string sheetName, int row, int col, bool strikethrough)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        _cellStrikethrough[(sheetName, row, col)] = strikethrough;
        if (cellEl is not null)
            FodsStyleEditor.SetCellStrikethrough(_doc, cellEl, strikethrough);
    }

    /// <summary>R446: Return the protection flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:cell-protect. GI-FODS-NET-001.</remarks>
    public bool GetCellProtection(string sheetName, int row, int col)
    {
        if (_cellProtection.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is not null && FodsStyleResolver.ResolveCellStyle(_doc, cellEl).IsProtected;
    }

    /// <summary>R446: Set the protection flag. GI-FODS-NET-001: writes to ODF XML.</summary>
    public void SetCellProtection(string sheetName, int row, int col, bool protect)
    {
        var cellEl = GetCellElement(sheetName, row, col);
        _cellProtection[(sheetName, row, col)] = protect;
        if (cellEl is not null)
            FodsStyleEditor.SetCellProtection(_doc, cellEl, protect);
    }
}

/// <summary>
/// Aggregate statistics for a numeric column: Min, Max, Sum, Avg, Count.
/// Returned by <see cref="FodsDocument.GetColumnStats"/>.
/// R225: ColumnStats result type for simplified single-sheet API.
/// </summary>
public sealed class ColumnStats
{
    public double Min { get; init; }
    public double Max { get; init; }
    public double Sum { get; init; }
    public double Avg { get; init; }
    public int Count { get; init; }
}

/// <summary>
/// Bounding range of used cells in a sheet.
/// Returned by <see cref="FodsDocument.GetUsedRange()"/>.
/// Exposes MinRow/MinCol/MaxRow/MaxCol plus computed RowCount/ColCount/Rows/Columns.
/// The <see cref="Value"/> property returns <c>this</c> for backward-compat with
/// code that used the tuple-form <c>range.Value.MinRow</c>.
/// R238.
/// </summary>
public sealed class FodsUsedRange
{
    public FodsUsedRange(int minRow, int minCol, int maxRow, int maxCol)
    {
        MinRow = minRow;
        MinCol = minCol;
        MaxRow = maxRow;
        MaxCol = maxCol;
    }

    public int MinRow { get; }
    public int MinCol { get; }
    public int MaxRow { get; }
    public int MaxCol { get; }

    public int RowCount => MaxRow - MinRow + 1;
    public int Rows => RowCount;
    public int ColCount => MaxCol - MinCol + 1;
    public int Columns => ColCount;
    public int Cols => ColCount;

    /// <summary>Always true; mirrors nullable-struct semantics. R212.</summary>
    public bool HasValue => true;

    /// <summary>Row count (tuple Item1 compat). R253.</summary>
    public int Item1 => RowCount;
    /// <summary>Column count (tuple Item2 compat). R253.</summary>
    public int Item2 => ColCount;

    /// <summary>Total cells in range (RowCount * ColCount). R230.</summary>
    public int Length => RowCount * ColCount;

    /// <summary>Returns <c>this</c>; for backward-compat with <c>range.Value.MinRow</c>.</summary>
    public FodsUsedRange Value => this;

    public override bool Equals(object? obj) =>
        obj is FodsUsedRange other &&
        MinRow == other.MinRow && MinCol == other.MinCol &&
        MaxRow == other.MaxRow && MaxCol == other.MaxCol;

    public override int GetHashCode() => HashCode.Combine(MinRow, MinCol, MaxRow, MaxCol);
}

/// <summary>
/// Cell formatting state returned by <see cref="FodsDocument.GetCellStyle"/>.
/// Holds the ODF style-name, bold, italic, and font-size attributes.
/// Provides an implicit conversion to <see langword="string?"/> for backward-compat with
/// code that did <c>Assert.Equal("ce1", style)</c>.
/// R237.
/// </summary>
public sealed class FodsCellStyle
{
    private static readonly XNamespace NsTable =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
    private static readonly XNamespace NsFo =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");

    public string? StyleName { get; }
    public bool IsBold { get; }
    public bool IsItalic { get; }
    public int FontSize { get; }

    /// <summary>For backward-compat: <c>style.Length</c> returns the StyleName length. R114.</summary>
    public int Length => StyleName?.Length ?? 0;

    public FodsCellStyle(string? styleName = null, bool isBold = false, bool isItalic = false, int fontSize = 0)
    {
        StyleName = styleName;
        IsBold = isBold;
        IsItalic = isItalic;
        FontSize = fontSize;
    }

    /// <summary>
    /// Implicit conversion to <see langword="string?"/>: returns <see cref="StyleName"/>.
    /// Enables <c>Assert.Equal("ce1", style)</c> to work after the return type changed from string?.
    /// </summary>
    public static implicit operator string?(FodsCellStyle? s) => s?.StyleName;

    public override string ToString()
    {
        if (StyleName is not null) return StyleName;
        var parts = new List<string>();
        if (IsBold) parts.Add("bold");
        if (IsItalic) parts.Add("italic");
        if (FontSize > 0) parts.Add(FontSize.ToString());
        return string.Join(",", parts);
    }

    public override bool Equals(object? obj)
    {
        if (obj is string s) return StyleName == s;
        if (obj is FodsCellStyle other)
            return StyleName == other.StyleName && IsBold == other.IsBold &&
                   IsItalic == other.IsItalic && FontSize == other.FontSize;
        return false;
    }

    public override int GetHashCode() => HashCode.Combine(StyleName, IsBold, IsItalic, FontSize);

    /// <summary>Create a FodsCellStyle from a cell XML element.</summary>
    internal static FodsCellStyle? FromElement(XElement cell)
    {
        var styleName = cell.Attribute(NsTable + "style-name")?.Value;
        var fontWeight = cell.Attribute(NsFo + "font-weight")?.Value;
        var fontStyle = cell.Attribute(NsFo + "font-style")?.Value;
        var fontSizeStr = cell.Attribute(NsFo + "font-size")?.Value;

        bool isBold = fontWeight == "bold";
        bool isItalic = fontStyle == "italic";
        int fontSize = 0;
        if (fontSizeStr is not null) int.TryParse(fontSizeStr, out fontSize);

        return new FodsCellStyle(styleName, isBold, isItalic, fontSize);
    }
}

/// <summary>Aggregate document statistics. Returned by <see cref="FodsDocument.GetDocumentStats"/>. R233.</summary>
public sealed class FodsDocumentStats
{
    public int SheetCount { get; init; }
    public int RowCount { get; init; }
    public int ColumnCount { get; init; }
}

/// <summary>
/// Per-sheet statistics. Returned by <see cref="FodsDocument.GetSheetStats"/>. R114/R234.
/// Supports both property access (<c>stats.RowCount</c>, <c>stats.ColumnCount</c>) and
/// tuple-style deconstruction (<c>var (rows, cols, cells, nonEmpty) = stats;</c>).
/// </summary>
public sealed class FodsSheetStats
{
    public int RowCount { get; }
    /// <summary>Maximum column count across all rows. Alias: <see cref="ColumnCount"/>.</summary>
    public int ColCount { get; }
    /// <summary>Alias for <see cref="ColCount"/>. R234.</summary>
    public int ColumnCount => ColCount;
    public int CellCount { get; }
    public int NonEmptyCellCount { get; }

    public FodsSheetStats(int rowCount, int colCount, int cellCount, int nonEmptyCellCount)
    {
        RowCount = rowCount;
        ColCount = colCount;
        CellCount = cellCount;
        NonEmptyCellCount = nonEmptyCellCount;
    }

    /// <summary>Support <c>var (rows, cols, cells, nonEmpty) = stats;</c>. R114.</summary>
    public void Deconstruct(out int rowCount, out int colCount, out int cellCount, out int nonEmptyCellCount)
    {
        rowCount = RowCount;
        colCount = ColCount;
        cellCount = CellCount;
        nonEmptyCellCount = NonEmptyCellCount;
    }
}
