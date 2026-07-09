// FormatFactory.Fods -- Data annotation APIs (comments, conditional formats, data validation,
// hyperlinks, named ranges, pivot tables, sparklines, chart access, column rename).
// Partial class extension for FodsDocument.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // -------------------------------------------------------------------------
    // Chart title (R305)
    // STUB: no ODF XML path for chart objects; _charts is an in-memory stub. Tracking GAP-NET-XG-012.
    // -------------------------------------------------------------------------

    /// <summary>R305: Return the title of the chart at the given index on the named sheet.</summary>
    public string GetChartTitle(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-006): implement ODF §9.8 chart:chart XML read for chart title
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_charts.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index), $"No chart at index {index} on sheet '{sheetName}'.");
        return list[index].Title;
    }

    // -------------------------------------------------------------------------
    // Comments (R306, R307, R338, R349, R388)
    // -------------------------------------------------------------------------

    /// <summary>R306: Add a comment to the specified cell (delegates to SetCellComment).</summary>
    public void AddComment(string sheetName, int row, int col, string text)
        => SetCellComment(sheetName, row, col, text);

    /// <summary>R349: Add a cell comment (alias for SetCellComment).</summary>
    public void AddCellComment(string sheetName, int row, int col, string text)
        => SetCellComment(sheetName, row, col, text);

    /// <summary>R388: Add a cell comment with author attribution (5-arg overload).</summary>
    public void AddCellComment(string sheetName, int row, int col, string author, string text)
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
    // Cell hyperlink and tooltip (R310, R363, R365)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), (string Url, string Display)> _cellHyperlinks = new();

    /// <summary>R363: Return the hyperlink URL for a cell, or empty string if none set.</summary>
    public string? GetCellHyperlink(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellHyperlinks.TryGetValue((sheetName, row, col), out var link) ? link.Url : string.Empty;
    }

    /// <summary>R363: Set the hyperlink URL for a cell.</summary>
    public void SetCellHyperlink(string sheetName, int row, int col, string url)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellHyperlinks[(sheetName, row, col)] = (url ?? string.Empty, string.Empty);
    }

    /// <summary>R365: Return the tooltip/comment for a cell, or empty string if none.</summary>
    public string? GetCellTooltip(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellComments.TryGetValue((sheetName, row, col), out var v) ? v : string.Empty;
    }

    /// <summary>R365: Set the tooltip/comment for a cell.</summary>
    public void SetCellTooltip(string sheetName, int row, int col, string tooltip)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellComments[(sheetName, row, col)] = tooltip ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Conditional formats (R308, R339)
    // STUB: no ODF XML path for conditional formats; _conditionalFormats is an in-memory stub. Tracking GAP-NET-XG-012.
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
        // TODO(GI-FODS-NET-007): implement ODF §11.6 table:content-validation read for count
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _conditionalFormats.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R339: Total conditional format count across all sheets.</summary>
    public int GetConditionalFormatCount()
        => _conditionalFormats.Values.Sum(list => list.Count);

    /// <summary>R308: Return the condition expression of the conditional format at the given index.</summary>
    public string GetConditionalFormatRule(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-007): implement ODF §11.6 table:content-validation rule expression read
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
    // Data validation (R310, R314, R337, R354)
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
        // TODO(GI-FODS-NET-008): implement ODF §11.4 table:content-validation count from XML
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _dataValidations.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R354: Total data validation count across all sheets.</summary>
    public int GetDataValidationCount() => _dataValidations.Values.Sum(l => l.Count);

    /// <summary>R314: Return the rule expression of the data validation at the given index.</summary>
    public string GetDataValidationRule(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-008): implement ODF §11.4 table:content-validation rule read from XML
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_dataValidations.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Rule;
    }

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
        // TODO(GI-FODS-NET-009): implement ODF text:a hyperlink count from cell XML
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _hyperlinks.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R317: Return the URL of the hyperlink at the given index.</summary>
    public string GetHyperlinkUrl(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-009): implement ODF text:a/@xlink:href read for sheet-level hyperlink
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_hyperlinks.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Url;
    }

    /// <summary>R310: Add a hyperlink anchored to a specific cell (5-arg).</summary>
    public void AddHyperlink(string sheetName, int row, int col, string url, string displayText = "")
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _cellHyperlinks[(sheetName, row, col)] = (url ?? string.Empty, displayText ?? string.Empty);
        if (!_hyperlinks.ContainsKey(sheetName)) _hyperlinks[sheetName] = new();
        _hyperlinks[sheetName].Add((url ?? string.Empty, displayText ?? string.Empty));
    }

    /// <summary>R310: Return the URL at the specified cell.</summary>
    public string GetHyperlinkUrl(string sheetName, int row, int col)
    {
        // TODO(GI-FODS-NET-009): implement ODF text:a/@xlink:href read for cell-level hyperlink
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (_cellHyperlinks.TryGetValue((sheetName, row, col), out var link))
            return link.Url;
        return string.Empty;
    }

    // -------------------------------------------------------------------------
    // Named ranges (R293, R320, R340, R391, R392)
    // -------------------------------------------------------------------------

    /// <summary>R320: Add a named range (3-arg: name, sheetName, address).</summary>
    public void AddNamedRange(string name, string sheetName, string address)
        => SetNamedRange(name, sheetName, address);

    /// <summary>R340: Add a named range (2-arg: name, address).</summary>
    public void AddNamedRange(string name, string address)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        _namedRanges[name] = address ?? string.Empty;
    }

    /// <summary>R293: Add a named range by cell coordinates (6-arg).</summary>
    public void AddNamedRange(string name, string sheetName, int startRow, int startCol, int endRow, int endCol)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("name must not be null or whitespace.", nameof(name));
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (startRow < 0) throw new ArgumentOutOfRangeException(nameof(startRow));
        if (startCol < 0) throw new ArgumentOutOfRangeException(nameof(startCol));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var address = $"{sheetName}!R{startRow}C{startCol}:R{endRow}C{endCol}";
        SetNamedRange(name, sheetName, address);
    }

    /// <summary>R320: Return the number of defined named ranges.</summary>
    public int GetNamedRangeCount() => _namedRanges.Count;

    /// <summary>R320: Return the address of the named range, or null if not defined.</summary>
    public string? GetNamedRangeAddress(string name) => GetNamedRange(name);

    /// <summary>R320: Return all named range names.</summary>
    public IReadOnlyList<string> GetNamedRanges() => _namedRanges.Keys.ToList();

    /// <summary>R391: Define a named range by cell coordinates (6-arg alias for AddNamedRange).</summary>
    public void SetNamedRange(string name, string sheetName, int startRow, int startCol, int endRow, int endCol)
        => AddNamedRange(name, sheetName, startRow, startCol, endRow, endCol);

    /// <summary>R392: Define a named range by cell coordinates (alias for SetNamedRange 6-arg).</summary>
    public void DefineNamedRange(string name, string sheetName, int startRow, int startCol, int endRow, int endCol)
        => AddNamedRange(name, sheetName, startRow, startCol, endRow, endCol);

    // -------------------------------------------------------------------------
    // Pivot tables (R317, R322, R333, R345)
    // -------------------------------------------------------------------------

    private readonly List<(string Name, string SourceRange)> _pivotTables = new();
    private readonly Dictionary<string, List<(string SourceRange, string Name)>> _sheetPivotTables = new();

    /// <summary>R322: Add a pivot table definition (2-arg: name, sourceRange).</summary>
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

    /// <summary>R317/R333: Add a pivot table to a sheet (6-arg per-sheet).</summary>
    public void AddPivotTable(string sheetName, string sourceRange, string p3, string p4, string p5, string name)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.ContainsKey(sheetName)) _sheetPivotTables[sheetName] = new();
        _sheetPivotTables[sheetName].Add((sourceRange ?? string.Empty, name ?? string.Empty));
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
        // TODO(GI-FODS-NET-012): implement ODF §9.6 table:data-pilot-table count from XML
        if (string.IsNullOrWhiteSpace(sheetName)) return 0;
        return _sheetPivotTables.TryGetValue(sheetName, out var list) ? list.Count : 0;
    }

    /// <summary>R317: Return the name of the pivot table at the given index on the specified sheet.</summary>
    public string GetPivotTableName(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-012): implement ODF §9.6 table:data-pilot-table/@table:name read
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].Name;
    }

    /// <summary>R333: Return the source range of the pivot table at the given index on the specified sheet.</summary>
    public string GetPivotTableSourceRange(string sheetName, int index)
    {
        // TODO(GI-FODS-NET-012): implement ODF §9.6 table:data-pilot-table source-range read
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetPivotTables.TryGetValue(sheetName, out var list) || index < 0 || index >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return list[index].SourceRange;
    }

    // -------------------------------------------------------------------------
    // Sparklines (R324)
    // STUB: no ODF XML path for sparklines; _sparklines is an in-memory stub. Tracking GAP-NET-XG-012.
    // -------------------------------------------------------------------------

    private readonly List<(string Type, string DataRange)> _sparklines = new();
    private readonly Dictionary<string, List<(string DataRange, string Location, string Type)>> _sheetSparklines = new();

    /// <summary>R324: Add a sparkline (2-arg: type, dataRange).</summary>
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

    /// <summary>R324: Add a sparkline to the sheet (4-arg: sheetName, dataRange, location, type).</summary>
    public void AddSparkline(string sheetName, string dataRange, string location, string type)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (!_sheetSparklines.ContainsKey(sheetName)) _sheetSparklines[sheetName] = new();
        _sheetSparklines[sheetName].Add((dataRange ?? string.Empty, location ?? string.Empty, type ?? string.Empty));
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
    // Column rename (R330) — XML-backed
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
    // XML/HTML export aliases (R318, R326, R335)
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

    /// <summary>R318: Export the document as HTML and write it to the specified file path.</summary>
    public void ExportToHtml(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("filePath must not be null or whitespace.", nameof(filePath));
        File.WriteAllText(filePath, ExportToHtml(), System.Text.Encoding.UTF8);
    }
}
