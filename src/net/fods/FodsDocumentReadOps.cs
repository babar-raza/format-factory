// FormatFactory.Fods — FodsDocument read/query operations (partial class).
// Domain: All field declarations, read-only data queries, column/row/cell access.
// Split from FodsDocumentAccessor.cs (TC-PQLM-021 decomposition).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // Field declarations (all Accessor-origin fields consolidated here)
    // =========================================================================

    private readonly Dictionary<string, Dictionary<int, double>> _columnWidths = new();
    private readonly Dictionary<string, (string ColName, string Value)> _activeFilters = new();
    private static readonly XNamespace NsFfExt =
        XNamespace.Get("urn:format-factory:fods-extensions");
    private static readonly XNamespace NsFo =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");
    private static readonly XNamespace NsConfig =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:config:1.0");
    private static readonly XNamespace NsCustom =
        XNamespace.Get("urn:format-factory:cell-style");
    private string? _activeSheet;
    private readonly Dictionary<(string sheet, int row, int col), string> _cellComments = new();
    private readonly Dictionary<string, string> _sheetProtectionPasswords = new();
    private readonly Dictionary<(string sheet, int row), double> _rowHeights = new();
    private readonly Dictionary<string, string> _namedRanges = new();

    // =========================================================================
    // Restore filter state from XML
    // =========================================================================

    private void RestoreFilterStateFromDocument()
    {
        foreach (var sheet in Sheets)
        {
            var attr = sheet.Element.Attribute(NsFfExt + "auto-filter");
            if (attr != null)
            {
                var parts = attr.Value.Split(':', 2);
                if (parts.Length == 2)
                    _activeFilters[sheet.Name] = (parts[0], parts[1]);
            }
        }
    }

    // =========================================================================
    // Private guard helpers
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

    private XElement? GetTableColumnElement(string sheetName, int colIndex)
    {
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        int cur = 0;
        foreach (var colEl in sheet.Element.Elements(NsTable + "table-column"))
        {
            var repAttr = colEl.Attribute(NsTable + "number-columns-repeated")?.Value;
            int rep = repAttr is not null && int.TryParse(repAttr, out int r) ? r : 1;
            if (colIndex < cur + rep) return colEl;
            cur += rep;
        }
        return null;
    }

    // =========================================================================
    // Row/cell/column count queries
    // =========================================================================

    /// <summary>Return the number of rows in the first (or active) sheet. R96.</summary>
    public int GetRowCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        if (_activeSheet != null)
            return GetSheetByName(_activeSheet)?.Rows.Count ?? sheets[0].Rows.Count;
        return sheets[0].Rows.Count;
    }

    /// <summary>Return the number of rows in the named sheet. R96.</summary>
    public int GetRowCount(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return sheet.Rows.Count;
    }

    /// <summary>Return the max column count for the named sheet. R108.</summary>
    public int GetColumnCount(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        int maxCols = 0;
        foreach (var row in sheet.Rows)
        {
            int cellCount = row.Cells.Count;
            if (cellCount > maxCols) maxCols = cellCount;
        }
        return maxCols;
    }

    /// <summary>Return the max column count for the first sheet. R108.</summary>
    public int GetColumnCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        var name = sheets[0].Name;
        return name != null ? GetColumnCount(name) : 0;
    }

    /// <summary>Return the total cell count in the first sheet. R97.</summary>
    public int GetCellCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        int count = 0;
        foreach (var row in sheets[0].Rows)
            count += row.Cells.Count;
        return count;
    }

    /// <summary>Return the total cell count in the named sheet. R197.</summary>
    public int GetCellCount(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        int count = 0;
        foreach (var row in sheet.Rows)
            count += row.Cells.Count;
        return count;
    }

    /// <summary>Total number of rows in the first sheet. R225.</summary>
    public int RowCount => GetRowCount();

    /// <summary>Return the column count of the first sheet. R212.</summary>
    public int ColumnCount
    {
        get
        {
            var sheets = Sheets;
            if (sheets.Count == 0) return 0;
            return GetColumnCount(sheets[0].Name!);
        }
    }

    // =========================================================================
    // Row value extraction
    // =========================================================================

    /// <summary>Return all cell values from a given row in the first sheet. R102.</summary>
    public IReadOnlyList<string?> GetRowValues(int row)
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new ArgumentOutOfRangeException(nameof(row), "Document has no sheets.");
        return GetRowValues(sheets[0], row);
    }

    /// <summary>Return all cell values from a given row in the named sheet. R102.</summary>
    public IReadOnlyList<string?> GetRowValues(string sheetName, int row)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return GetRowValues(sheet, row);
    }

    /// <summary>Return all cell values from a given row in the given sheet. R102.</summary>
    public static IReadOnlyList<string?> GetRowValues(FodsSheet sheet, int row)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0 || row >= sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row), $"Row {row} is out of range [0, {sheet.Rows.Count}).");
        var cells = sheet.Rows[row].Cells;
        var values = new List<string?>(cells.Count);
        foreach (var cell in cells)
            values.Add(cell.IsCovered ? null : cell.Value);
        return values.AsReadOnly();
    }

    // =========================================================================
    // Column value extraction
    // =========================================================================

    /// <summary>Return all cell values from a column by index in the named sheet. R106.</summary>
    public IReadOnlyList<string?> GetColumnValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0)
            throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var result = new List<string?>();
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col < cells.Count)
                result.Add(cells[col].Element(nsText + "p")?.Value);
        }
        return result;
    }

    /// <summary>Return all cell values from a column by index in the first sheet. R225.</summary>
    public IReadOnlyList<string?> GetColumnValues(int col)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheets = Sheets;
        if (sheets.Count == 0) return Array.Empty<string?>();
        var name = sheets[0].Name;
        if (name is null) return Array.Empty<string?>();
        return GetColumnValues(name, col);
    }

    /// <summary>Return all cell values from a column identified by header name. R238.</summary>
    public List<string> GetColumnValues(string sheetName, string header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        var sheet = GetSheetByName(sheetName);
        if (sheet is null || sheet.Rows.Count == 0) return new List<string>();
        var headerRowVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerRowVals.Count; i++)
            if (headerRowVals[i] == header) { colIndex = i; break; }
        if (colIndex < 0) return new List<string>();
        var result = new List<string>();
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var vals = GetRowValues(sheet, r);
            result.Add(colIndex < vals.Count ? (vals[colIndex] ?? "") : "");
        }
        return result;
    }

    /// <summary>Return numeric column values from the named sheet. R100.</summary>
    public IReadOnlyList<double> GetNumericColumnValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0)
            throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var result = new List<double>();
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col >= cells.Count) continue;
            var cell = cells[col];
            var vtype = cell.Attribute(NsOffice + "value-type")?.Value;
            if (vtype == "float" || vtype == "currency" || vtype == "percentage")
            {
                var raw = cell.Attribute(NsOffice + "value")?.Value;
                if (raw is not null && double.TryParse(raw, System.Globalization.NumberStyles.Float,
                        System.Globalization.CultureInfo.InvariantCulture, out var d))
                { result.Add(d); continue; }
            }
            var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
            var textVal = cell.Element(nsText + "p")?.Value;
            if (textVal is not null && double.TryParse(textVal, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var dText))
                result.Add(dText);
        }
        return result;
    }

    /// <summary>Return all column values as non-null strings. R237.</summary>
    public List<string> GetStringColumnValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        var result = new List<string>();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var row in sheet.Rows)
        {
            if (col >= row.Cells.Count) { result.Add(""); continue; }
            var val = row.Cells[col].Element.Element(nsText + "p")?.Value
                   ?? row.Cells[col].Element.Value ?? "";
            result.Add(val);
        }
        return result;
    }

    /// <summary>Return distinct cell values in a column. R223.</summary>
    public IReadOnlyList<string?> GetDistinctValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var values = GetColumnValues(sheetName, col);
        var seen = new HashSet<string?>();
        var result = new List<string?>();
        foreach (var v in values)
            if (seen.Add(v)) result.Add(v);
        return result;
    }

    // =========================================================================
    // Cell data type and formula queries
    // =========================================================================

    /// <summary>Return the ODF value-type of a cell. R110.</summary>
    public bool HasSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return false;
        return GetSheetByName(name) != null;
    }

    /// <summary>Return the ODF value-type attribute of a cell (static overload). R110.</summary>
    public static string? GetCellDataType(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsOffice + "value-type")?.Value;
    }

    /// <summary>Return the ODF value-type of a cell in the named sheet. R110.</summary>
    public string? GetCellDataType(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null || row < 0 || col < 0) return null;
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsOffice + "value-type")?.Value;
    }

    /// <summary>Search all cells in the named sheet for the given text value. R110.</summary>
    public IReadOnlyList<(int Row, int Col)> FindCellsByValue(string sheetName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(value);
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var results = new List<(int, int)>();
        var rows = sheet.Rows;
        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Cells;
            for (int c = 0; c < cells.Count; c++)
                if (!cells[c].IsCovered && cells[c].Value == value)
                    results.Add((r, c));
        }
        return results;
    }

    /// <summary>Return the formula expression from a cell. R111.</summary>
    public string? GetCellFormula(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null || row < 0 || col < 0) return null;
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "formula")?.Value;
    }

    /// <summary>Return the displayed value for a formula cell. R238.</summary>
    public string? GetCellFormulaValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Value ?? string.Empty;
    }

    /// <summary>Return the formula for a cell (alias for GetCellFormula). R249.</summary>
    public string? GetFormula(string sheetName, int row, int col) => GetCellFormula(sheetName, row, col);

    // =========================================================================
    // Used range and sheet statistics
    // =========================================================================

    /// <summary>Return the bounding range of non-empty cells in the first sheet. R112.</summary>
    public FodsUsedRange? GetUsedRange()
    {
        var sheet = Sheets.FirstOrDefault();
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>Return the bounding range of non-empty cells in the named sheet. R112.</summary>
    public FodsUsedRange? GetUsedRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>Return the bounding range of non-empty cells in the given sheet. R112.</summary>
    public static FodsUsedRange? GetUsedRange(FodsSheet sheet)
    {
        int minRow = int.MaxValue, minCol = int.MaxValue;
        int maxRow = int.MinValue, maxCol = int.MinValue;
        bool found = false;
        var rows = sheet.Rows;
        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Cells;
            for (int c = 0; c < cells.Count; c++)
            {
                var text = cells[c].Element.Value;
                if (!string.IsNullOrEmpty(text))
                {
                    found = true;
                    if (r < minRow) minRow = r;
                    if (r > maxRow) maxRow = r;
                    if (c < minCol) minCol = c;
                    if (c > maxCol) maxCol = c;
                }
            }
        }
        return found ? new FodsUsedRange(minRow, minCol, maxRow, maxCol) : null;
    }

    /// <summary>Return aggregate statistics for a named sheet. R114.</summary>
    public FodsSheetStats GetSheetStats(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return new FodsSheetStats(0, 0, 0, 0);
        int rowCount = sheet.Rows.Count;
        int maxCols = 0;
        int nonEmpty = 0;
        foreach (var row in sheet.Rows)
        {
            int c = row.Cells.Count;
            if (c > maxCols) maxCols = c;
            foreach (var cell in row.Cells)
                if (!cell.IsCovered && !string.IsNullOrEmpty(cell.Value))
                    nonEmpty++;
        }
        return new FodsSheetStats(rowCount, maxCols, rowCount * maxCols, nonEmpty);
    }

    // =========================================================================
    // Cell style reads
    // =========================================================================

    /// <summary>Get the ODF table:style-name attribute from a cell. R114.</summary>
    public string? GetCellStyle(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
    }

    /// <summary>Get cell style from the first (active) sheet. R229.</summary>
    public string? GetCellStyle(int row, int col)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return null;
        return GetCellStyle(sheets[0].Name!, row, col);
    }

    /// <summary>Get a cell's style-name by explicit FodsSheet reference. R212.</summary>
    public static string? GetCellStyle(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
    }

    /// <summary>Resolve the full ODF style chain for a cell. R114.</summary>
    public FodsOdfCellStyle? GetResolvedCellStyle(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return FodsStyleResolver.ResolveCellStyle(_doc, r.Cells[col].Element);
    }

    /// <summary>GetResolvedCellStyle from the first (active) sheet.</summary>
    public FodsOdfCellStyle? GetResolvedCellStyle(int row, int col)
    {
        var sheets = Sheets;
        return sheets.Count == 0 ? null : GetResolvedCellStyle(sheets[0].Name!, row, col);
    }

    /// <summary>Resolve the ODF column style for the given column index.</summary>
    public FodsOdfColumnStyle? GetResolvedColumnStyle(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var colEl = GetTableColumnElement(sheetName, col);
        return colEl is null ? null : FodsStyleResolver.ResolveColumnStyle(_doc, colEl);
    }

    /// <summary>Resolve the ODF row style for the given row index.</summary>
    public FodsOdfRowStyle? GetResolvedRowStyle(string sheetName, int row)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row >= sheet.Rows.Count) return null;
        return FodsStyleResolver.ResolveRowStyle(_doc, sheet.Rows[row].Element);
    }

    // =========================================================================
    // Column/row width and height reads
    // =========================================================================

    /// <summary>Return the width of a column (in-memory override takes priority). R218.</summary>
    public double GetColumnWidth(string sheetName, int colIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex), "Column index must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (_columnWidths.TryGetValue(sheetName, out var cols) && cols.TryGetValue(colIndex, out var width))
            return width;
        var colEl = GetTableColumnElement(sheetName, colIndex);
        return colEl is null ? 0.0 : FodsStyleResolver.ResolveColumnStyle(_doc, colEl).Width;
    }

    /// <summary>Return the row height for the given row (in-memory override takes priority). R284.</summary>
    public double GetRowHeight(string sheetName, int rowIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (_rowHeights.TryGetValue((sheetName, rowIndex), out var h)) return h;
        if (rowIndex >= sheet.Rows.Count) return 0.0;
        return FodsStyleResolver.ResolveRowStyle(_doc, sheet.Rows[rowIndex].Element).Height;
    }

    /// <summary>Return the column width with positive fallback (64.0). R473.</summary>
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

    /// <summary>Return the row height with positive fallback (20.0). R474.</summary>
    public double GetCellRowHeight(string sheetName, int row)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row), "Row index must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var h = GetRowHeight(sheetName, row);
        return h > 0 ? h : 20.0;
    }

    // =========================================================================
    // Document and sheet-level queries
    // =========================================================================

    /// <summary>Return the number of sheets in the document. R233.</summary>
    public int GetSheetCount() => Sheets.Count;

    /// <summary>Return aggregate stats for the document (first sheet). R233.</summary>
    public FodsDocumentStats GetDocumentStats()
    {
        var sheets = Sheets;
        return new FodsDocumentStats
        {
            SheetCount = sheets.Count,
            RowCount = sheets.Count == 0 ? 0 : sheets[0].Rows.Count,
            ColumnCount = sheets.Count == 0 ? 0 : GetColumnCount(sheets[0].Name!),
        };
    }

    /// <summary>Return the zero-based index of the named sheet. R271.</summary>
    public int GetSheetIndex(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheets = Sheets;
        for (int i = 0; i < sheets.Count; i++)
            if (sheets[i].Name == sheetName) return i;
        throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
    }

    /// <summary>Return the name of the sheet at the given zero-based index.</summary>
    public string GetSheetName(int index)
    {
        var names = GetSheetNames();
        if (index < 0 || index >= names.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Sheet index {index} is out of range (0..{names.Count - 1}).");
        return names[index];
    }

    /// <summary>Return the max used row count for the named sheet. R476.</summary>
    public int GetSheetMaxRow(string sheetName) => RequireSheet(sheetName).Rows.Count;

    /// <summary>Return the max used column count for the named sheet. R477.</summary>
    public int GetSheetMaxColumn(string sheetName)
    {
        var sheet = RequireSheet(sheetName);
        if (sheet.Rows.Count == 0) return 0;
        return sheet.Rows.Max(r => r.Cells.Count);
    }

    // =========================================================================
    // Column header, cell range, and type queries
    // =========================================================================

    /// <summary>Check whether a sheet has a column with the given header. R197.</summary>
    public bool HasColumn(string sheetName, string header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        if (GetSheetByName(sheetName) is null)
            throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        var headers = GetColumnHeaders(sheetName);
        return headers.Contains(header, StringComparer.Ordinal);
    }

    /// <summary>Return data values of the column with the given header. R197.</summary>
    public IReadOnlyList<string?> GetColumn(string sheetName, string header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var headers = GetColumnHeaders(sheetName);
        int col = -1;
        for (int i = 0; i < headers.Count; i++)
            if (string.Equals(headers[i], header, StringComparison.Ordinal)) { col = i; break; }
        if (col < 0)
            throw new InvalidOperationException(
                $"No column with header '{header}' found in sheet '{sheetName}'.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var result = new List<string?>();
        for (int r = 1; r < sheet.Rows.Count; r++)
        {
            var cells = sheet.Rows[r].Element.Elements(NsTable + "table-cell").ToList();
            result.Add(col < cells.Count ? cells[col].Element(nsText + "p")?.Value : null);
        }
        return result;
    }

    /// <summary>Return column header names for the named sheet (alias for GetColumnHeaders). R251.</summary>
    public List<string> GetColumnNames(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (GetSheetByName(sheetName) is null)
            throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        return GetColumnHeaders(sheetName).ToList();
    }

    /// <summary>Return a 2D array of cell values from a rectangular range. R256.</summary>
    public string?[,] GetCellRange(string sheetName, int startRow, int startCol, int endRow, int endCol)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        int rows = Math.Max(0, endRow - startRow + 1);
        int cols = Math.Max(0, endCol - startCol + 1);
        var result = new string?[rows, cols];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                result[r, c] = GetCellValue(sheet, startRow + r, startCol + c);
        return result;
    }

    /// <summary>Return the data type of a cell as a string. R286.</summary>
    public string GetCellType(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row >= sheet.Rows.Count) return "empty";
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return "empty";
        var cell = r.Cells[col];
        var valueType = cell.Element.Attribute(NsOffice + "value-type")?.Value;
        if (!string.IsNullOrEmpty(valueType)) return valueType;
        var nsText2 = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var text = cell.Element.Element(nsText2 + "p")?.Value ?? cell.Element.Value;
        return string.IsNullOrEmpty(text) ? "empty" : "string";
    }

    /// <summary>Return true if the cell at (row, col) has no content. R283.</summary>
    public bool IsCellEmpty(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return true;
        if (row < 0 || row >= sheet.Rows.Count) return true;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return true;
        return string.IsNullOrEmpty(GetCellValue(sheetName, row, col));
    }

    // =========================================================================
    // Aggregate, filtered rows, and formulas
    // =========================================================================

    /// <summary>Compute numeric aggregates for a column. R116.</summary>
    public (double Min, double Max, double Sum, int Count) GetColumnAggregates(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return (0, 0, 0, 0);
        double min = double.MaxValue, max = double.MinValue, sum = 0;
        int count = 0;
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            if (col >= rowVals.Count) continue;
            var raw = rowVals[col];
            if (raw is null) continue;
            if (double.TryParse(raw, System.Globalization.NumberStyles.Any,
                                System.Globalization.CultureInfo.InvariantCulture, out double v))
            {
                if (v < min) min = v;
                if (v > max) max = v;
                sum += v;
                count++;
            }
        }
        return count == 0 ? (0, 0, 0, 0) : (min, max, sum, count);
    }

    /// <summary>Return data rows matching the active auto-filter. R265.</summary>
    public IReadOnlyList<Dictionary<string, string?>> GetFilteredRows(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (!_activeFilters.TryGetValue(sheetName, out var filter))
            return new List<Dictionary<string, string?>>();
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return new List<Dictionary<string, string?>>();
        var headers = GetRowValues(sheetName, 0).ToList();
        int colIndex = headers.IndexOf(filter.ColName);
        if (colIndex < 0) return new List<Dictionary<string, string?>>();
        var result = new List<Dictionary<string, string?>>();
        int rowCount = GetRowCount(sheetName);
        for (int r = 1; r < rowCount; r++)
        {
            var cellVal = GetCellValue(sheetName, r, colIndex);
            if (cellVal == filter.Value)
            {
                var rowValues = GetRowValues(sheetName, r).ToList();
                var dict = new Dictionary<string, string?>();
                for (int c = 0; c < headers.Count; c++)
                    dict[headers[c] ?? $"Col{c}"] = c < rowValues.Count ? rowValues[c] : null;
                result.Add(dict);
            }
        }
        return result;
    }

    /// <summary>Return all formulas in the named sheet. R278.</summary>
    public List<string> GetFormulas(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        var result = new List<string>();
        foreach (var row in sheet.Rows)
            foreach (var cell in row.Cells)
            {
                var formula = cell.Element.Attribute(NsTable + "formula")?.Value;
                if (!string.IsNullOrEmpty(formula))
                    result.Add(formula);
            }
        return result;
    }

    /// <summary>Return aggregate statistics for a numeric column in the first sheet. R225.</summary>
    public ColumnStats GetColumnStats(int col)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheets = Sheets;
        if (sheets.Count == 0) return new ColumnStats();
        var sheet = sheets[0];
        double min = double.MaxValue, max = double.MinValue, sum = 0;
        int count = 0;
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            if (col >= rowVals.Count) continue;
            var raw = rowVals[col];
            if (raw is null) continue;
            if (double.TryParse(raw, System.Globalization.NumberStyles.Any,
                    System.Globalization.CultureInfo.InvariantCulture, out double v))
            {
                if (v < min) min = v;
                if (v > max) max = v;
                sum += v;
                count++;
            }
        }
        return count == 0
            ? new ColumnStats()
            : new ColumnStats { Min = min, Max = max, Sum = sum, Avg = sum / count, Count = count };
    }

    /// <summary>Switch the active sheet for first-sheet methods. R231.</summary>
    public void SwitchSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _activeSheet = sheetName;
    }
}
