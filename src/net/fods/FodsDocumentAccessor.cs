// FormatFactory.Fods -- FodsDocument query/export methods (partial class).
// Extracted from FodsDocument.cs via TC-NET-H1 (LOC decomposition).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // Column width storage (in-memory only; not persisted to FODS XML)
    private readonly Dictionary<string, Dictionary<int, double>> _columnWidths = new();

    // Named ranges storage (in-memory; not persisted to FODS XML)
    private readonly Dictionary<string, string> _namedRanges = new();

    // Auto-filter storage (persisted to FODS XML via custom namespace)
    private readonly Dictionary<string, (string ColName, string Value)> _activeFilters = new();

    // Custom namespace for FF extensions (filter state persistence)
    private static readonly XNamespace NsFfExt =
        XNamespace.Get("urn:format-factory:fods-extensions");

    /// <summary>Restore filter state from the document's XML on construction/load.</summary>
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

    /// <summary>
    /// Return the number of rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// R96 Train L: row count query for data analysis.
    /// </summary>
    public int GetRowCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        if (_activeSheet != null)
            return GetSheetByName(_activeSheet)?.Rows.Count ?? sheets[0].Rows.Count;
        return sheets[0].Rows.Count;
    }

    /// <summary>
    /// Return the number of rows in the named sheet.
    /// Throws if the sheet is not found.
    /// R96 Train L: row count query (named sheet overload).
    /// </summary>
    public int GetRowCount(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return sheet.Rows.Count;
    }

    /// <summary>
    /// Return the maximum number of columns (cells in any single row) in the named sheet.
    /// Returns 0 if the sheet has no rows.
    /// R108 Lane C: column count for data structure analysis.
    /// </summary>
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

    /// <summary>
    /// Return the maximum number of columns in the first sheet.
    /// Returns 0 if the document has no sheets or the first sheet has no rows.
    /// R108 Lane C: column count for data structure analysis.
    /// </summary>
    public int GetColumnCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        var name = sheets[0].Name;
        return name != null ? GetColumnCount(name) : 0;
    }

    /// <summary>
    /// Return the total number of cells across all rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// R97 Train L: cell count for data density analysis.
    /// </summary>
    public int GetCellCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        int count = 0;
        foreach (var row in sheets[0].Rows)
            count += row.Cells.Count;
        return count;
    }

    /// <summary>
    /// Return the total cell count for the named sheet.
    /// R197: sheet-name overload for test compatibility.
    /// </summary>
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

    /// <summary>
    /// Return all cell values from a given row in the first sheet as a list of strings.
    /// Returns null values for empty or covered cells.
    /// Throws if the row index is out of range.
    /// R102 Train A: row-level data extraction for export pipelines.
    /// </summary>
    public IReadOnlyList<string?> GetRowValues(int row)
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new ArgumentOutOfRangeException(nameof(row), "Document has no sheets.");
        return GetRowValues(sheets[0], row);
    }

    /// <summary>
    /// Return all cell values from a given row in the named sheet.
    /// R102 Train A: row-level data extraction (named sheet overload).
    /// </summary>
    public IReadOnlyList<string?> GetRowValues(string sheetName, int row)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return GetRowValues(sheet, row);
    }

    /// <summary>
    /// Return all cell values from a given row in the specified sheet.
    /// R102 Train A: row-level data extraction (static overload).
    /// </summary>
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

    /// <summary>
    /// Export a sheet as a JSON array of row objects.
    /// The first row is treated as headers; subsequent rows become objects keyed by those headers.
    /// If the sheet has zero or one row, returns "[]".
    /// R95 Train L: JSON export for data interchange pipeline.
    /// </summary>
    public string ExportSheetToJson()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToJson(sheets[0]);
    }

    /// <summary>
    /// Export a named sheet as a JSON array of row objects.
    /// R95 Train L: JSON export (named sheet overload).
    /// </summary>
    public string ExportSheetToJson(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToJson(sheet);
    }

    /// <summary>
    /// Export a specific sheet as a JSON array of row objects.
    /// First row = header keys; subsequent rows = value objects.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToJson"/>.
    /// R95 Train L: JSON export (static overload).
    /// </summary>
    public static string ExportSheetToJson(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToJson(sheet);

    /// <summary>
    /// Export a sheet as a Markdown table string.
    /// The first row is treated as headers with a separator line beneath.
    /// Pipe characters in cell values are escaped as \|.
    /// Returns an empty string if the sheet has no rows.
    /// R101 Train A: Markdown export for documentation pipeline.
    /// </summary>
    public string ExportSheetToMarkdown()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToMarkdown(sheets[0]);
    }

    /// <summary>
    /// Export a named sheet as a Markdown table string.
    /// R101 Train A: Markdown export (named sheet overload).
    /// </summary>
    public string ExportSheetToMarkdown(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToMarkdown(sheet);
    }

    /// <summary>
    /// Export a specific sheet as a Markdown table string.
    /// First row = headers; separator line = dashes; subsequent rows = data.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToMarkdown"/>.
    /// R101 Train A: Markdown export (static overload).
    /// </summary>
    public static string ExportSheetToMarkdown(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToMarkdown(sheet);

    /// <summary>
    /// Return all cell values from the specified column (zero-based) across all rows
    /// in the named sheet. Returns null for cells that are empty or missing.
    /// Throws if the sheet is not found or the column index is negative.
    /// R106 Wave 2: column extraction for data analysis workflows.
    /// </summary>
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
            {
                var textP = cells[col].Element(nsText + "p");
                result.Add(textP?.Value);
            }
            else
            {
                continue;
            }
        }
        return result;
    }

    /// <summary>
    /// Return numeric (float) cell values from the given column in the named sheet.
    /// Reads office:value-type="float" cells and returns their office:value attribute as double.
    /// Cells with no value, non-numeric type, or out-of-range column index are skipped.
    /// Spec: FACT-FODS-006 (table:table-cell), FACT-FODS-010 (office:value-type float).
    /// R100 Wave 5: numeric column extraction for data analysis.
    /// </summary>
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
                {
                    result.Add(d);
                    continue;
                }
            }
            // Fallback: try to parse the text:p content as a number
            var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
            var textVal = cell.Element(nsText + "p")?.Value;
            if (textVal is not null && double.TryParse(textVal, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var dText))
                result.Add(dText);
        }
        return result;
    }

    /// <summary>
    /// Export a sheet as CSV (comma-separated values).
    /// Each row becomes a line, cells are comma-separated, values containing commas/quotes/newlines
    /// are enclosed in double quotes with internal quotes doubled (RFC 4180).
    /// R107 Wave 2: CSV export for data interchange and dogfood pipeline.
    /// </summary>
    public string ExportSheetToCsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return ExportSheetToCsv(sheet);
    }

    /// <summary>
    /// Export the first sheet as CSV.
    /// R107 Wave 2: CSV export (default sheet overload).
    /// </summary>
    public string ExportSheetToCsv()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToCsv(sheets[0]);
    }

    /// <summary>
    /// Export a specific sheet as CSV.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToCsv"/>.
    /// R107 Wave 2: CSV export (static overload).
    /// </summary>
    public static string ExportSheetToCsv(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToCsv(sheet);

    /// <summary>
    /// Check whether a sheet with the given name exists in the document.
    /// Returns true if found, false otherwise.
    /// R109 Lane C: sheet existence check for defensive programming.
    /// </summary>
    public bool HasSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            return false;
        return GetSheetByName(name) != null;
    }

    /// <summary>
    /// Return the ODF value-type of a cell (e.g. "string", "float", "date").
    /// Reads the office:value-type attribute from the table-cell element.
    /// Returns null if the cell has no value-type attribute or indices are out of range.
    /// R110 Wave 4: cell metadata inspection for data analysis.
    /// </summary>
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

    /// <summary>
    /// Search all cells in the named sheet for the given text value.
    /// Returns a list of (Row, Col) tuples for every cell whose text content matches exactly.
    /// The comparison is ordinal (case-sensitive). Returns an empty list if no matches found.
    /// Throws if the sheet is not found.
    /// R110 Wave 4: cell search for data lookup and validation.
    /// </summary>
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
            {
                if (!cells[c].IsCovered && cells[c].Value == value)
                    results.Add((r, c));
            }
        }
        return results;
    }

    /// <summary>
    /// Get the formula expression from a cell, or null if no formula is set.
    /// Reads the table:formula attribute from the cell element.
    /// R111 Wave 5: complement to SetCellFormula for formula inspection.
    /// </summary>
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

    /// <summary>
    /// Return the bounding range of non-empty cells in the first sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if the sheet is empty.
    /// R112: governed /add-dotnet-api.
    /// </summary>
    public FodsUsedRange? GetUsedRange()
    {
        var sheet = Sheets.FirstOrDefault();
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the named sheet, or null if the sheet is empty.
    /// </summary>
    public FodsUsedRange? GetUsedRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the given sheet, or null if no cells have content.
    /// </summary>
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

    /// <summary>
    /// Return aggregate statistics for a named sheet: total rows, max column count,
    /// total cell slots, and non-empty cell count.
    /// Returns zeros if the sheet is not found.
    /// R114 Train A: sheet-level aggregate stats for data analysis.
    /// </summary>
    public FodsSheetStats GetSheetStats(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return new FodsSheetStats(0, 0, 0, 0);

        int rowCount = sheet.Rows.Count;
        int maxCols = 0;
        int cellCount = 0;
        int nonEmpty = 0;

        foreach (var row in sheet.Rows)
        {
            int c = row.Cells.Count;
            if (c > maxCols) maxCols = c;
            foreach (var cell in row.Cells)
                if (!cell.IsCovered && !string.IsNullOrEmpty(cell.Value))
                    nonEmpty++;
        }

        cellCount = rowCount * maxCols;
        return new FodsSheetStats(rowCount, maxCols, cellCount, nonEmpty);
    }

    /// <summary>
    /// Get the ODF table:style-name attribute from a cell, or null if not set.
    /// Returns null if the sheet, row, or col index is not found.
    /// R114 Train A: cell style retrieval.
    /// </summary>
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
        // Return the explicit style name, or "Default" if none set (ODF default style)
        return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
    }

    /// <summary>Get cell style from the first (active) sheet. R229.</summary>
    public string? GetCellStyle(int row, int col)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return null;
        return GetCellStyle(sheets[0].Name!, row, col);
    }

    /// <summary>
    /// Get a cell's style-name attribute by explicit FodsSheet reference.
    /// Returns null if indices are out of range or the cell has no style.
    /// Throws ArgumentNullException for null sheet; ArgumentOutOfRangeException for negative indices.
    /// R212: static overload for direct sheet-handle access.
    /// </summary>
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

    /// <summary>
    /// Set a cell's style-name attribute by explicit FodsSheet reference.
    /// Uses sequential-append semantics to create the row/cell if needed.
    /// R212: static overload for direct sheet-handle access.
    /// </summary>
    public static void SetCellStyle(FodsSheet sheet, int row, int col, string styleName)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(styleName);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row > sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
        if (row == sheet.Rows.Count)
            sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count)
            r.Element.Add(new XElement(NsTable + "table-cell"));
        r.Cells[col].Element.SetAttributeValue(NsTable + "style-name", styleName);
    }

    /// <summary>
    /// Export a named sheet as CSV and write the result to <paramref name="filePath"/>.
    /// R115 Train A: CSV file export for dogfood pipeline integration.
    /// </summary>
    /// <exception cref="ArgumentException">sheetName or filePath null/empty.</exception>
    /// <exception cref="InvalidOperationException">Sheet not found.</exception>
    public void ExportSheetToCsvFile(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var csv = ExportSheetToCsv(sheetName);
        File.WriteAllText(filePath, csv, System.Text.Encoding.UTF8);
    }

    /// <summary>
    /// Export the first sheet as CSV and write to <paramref name="filePath"/>.
    /// R115 Train A: CSV file export (default-sheet overload).
    /// </summary>
    public void ExportSheetToCsvFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var csv = ExportSheetToCsv();
        File.WriteAllText(filePath, csv, System.Text.Encoding.UTF8);
    }

    /// <summary>
    /// Return a filtered view of rows where <paramref name="col"/> equals <paramref name="value"/>
    /// (case-sensitive exact match). The header row (index 0) is always included.
    /// R115 Train B: row filtering for data query pipeline.
    /// </summary>
    /// <returns>List of row value arrays (including header). Empty if sheet not found.</returns>
    public IReadOnlyList<IReadOnlyList<string?>> FilterRows(string sheetName, int col, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(value);

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<IReadOnlyList<string?>>();

        var rows = sheet.Rows;
        var result = new List<IReadOnlyList<string?>>();

        for (int r = 0; r < rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            // Header row (index 0) is always included
            if (r == 0 || (col < rowVals.Count && rowVals[col] == value))
                result.Add(rowVals);
        }
        return result;
    }

    /// <summary>
    /// Compute numeric aggregates (min, max, sum, count) for a column in a sheet.
    /// Non-numeric cells and the header row are skipped.
    /// R116: column aggregate query.
    /// </summary>
    /// <returns>A tuple (Min, Max, Sum, Count). Count is 0 if no numeric cells.</returns>
    public (double Min, double Max, double Sum, int Count) GetColumnAggregates(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null)
            return (0, 0, 0, 0);

        double min = double.MaxValue;
        double max = double.MinValue;
        double sum = 0;
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

    /// <summary>
    /// Export the first sheet as XML (the raw table:table element serialized as a string).
    /// R194: XML export for data exchange pipeline.
    /// </summary>
    public string ExportSheetToXml()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return sheets[0].Element.ToString(System.Xml.Linq.SaveOptions.None);
    }

    /// <summary>
    /// Export the named sheet as XML (the raw table:table element serialized as a string).
    /// R194: XML export (named sheet overload).
    /// </summary>
    public string ExportSheetToXml(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return sheet.Element.ToString(System.Xml.Linq.SaveOptions.None);
    }

    /// <summary>
    /// Export the named sheet as CSV and write to <paramref name="filePath"/>.
    /// Alias for <see cref="ExportSheetToCsvFile(string, string)"/>.
    /// R198: ExportSheetToCsv overload accepting 2 arguments (sheet + path).
    /// </summary>
    public void ExportSheetToCsv(string sheetName, string filePath)
        => ExportSheetToCsvFile(sheetName, filePath);

    /// <summary>
    /// Filter rows in the named sheet using a predicate on the value in column
    /// <paramref name="col"/>. Returns a list of matching row indices (0-based).
    /// Does NOT auto-include the header row — all matching rows are included.
    /// Returns an empty list if the sheet is not found or no rows match.
    /// R199: predicate-based row filter returning row indices.
    /// </summary>
    public IReadOnlyList<int> FilterRows(string sheetName, int col, Func<string?, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();

        var rows = sheet.Rows;
        var result = new List<int>();
        var nsText = System.Xml.Linq.XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");

        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Element.Elements(NsTable + "table-cell").ToList();
            string? cellValue = null;
            if (col < cells.Count)
            {
                var textP = cells[col].Element(nsText + "p");
                cellValue = textP?.Value;
            }
            if (predicate(cellValue))
                result.Add(r);
        }
        return result;
    }

    /// <summary>
    /// Filter rows in the named sheet using a row-index predicate.
    /// The predicate receives a zero-based row index; returns true to include that row.
    /// Returns a list of matching row indices. Returns empty list if sheet not found.
    /// R207: row-index predicate overload for flexible filtering.
    /// </summary>
    public IReadOnlyList<int> FilterRows(string sheetName, Func<int, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();

        var result = new List<int>();
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            if (predicate(r))
                result.Add(r);
        }
        return result;
    }

    /// <summary>
    /// Return true if the named sheet has a column whose header (first-row cell value)
    /// matches <paramref name="header"/> exactly (case-sensitive, ordinal comparison).
    /// Returns false if the sheet does not exist, has no rows, or has no matching header.
    /// Spec: FACT-FODS-006 (table:table-cell), FACT-FODS-003 (table:table-row).
    /// ODF §9.4.5 table:table-cell — cell value extraction from first row.
    /// R197: column existence check by header name.
    /// </summary>
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

    /// <summary>
    /// Return the data values of the column whose first-row header equals <paramref name="header"/>
    /// in the named sheet. The header row itself is excluded from the result.
    /// Returns null for empty or missing cells in the data rows.
    /// Throws <see cref="InvalidOperationException"/> if the sheet does not exist or the header
    /// is not found. Use <see cref="HasColumn"/> to check before calling.
    /// Spec: FACT-FODS-006 (table:table-cell), FACT-FODS-003 (table:table-row).
    /// ODF §9.4.5 table:table-cell — column data extraction by header name.
    /// R197: column value extraction by header name.
    /// </summary>
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
        {
            if (string.Equals(headers[i], header, StringComparison.Ordinal))
            { col = i; break; }
        }
        if (col < 0)
            throw new InvalidOperationException(
                $"No column with header '{header}' found in sheet '{sheetName}'.");

        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var result = new List<string?>();

        // Skip row 0 (header row), collect data rows
        for (int r = 1; r < sheet.Rows.Count; r++)
        {
            var cells = sheet.Rows[r].Element.Elements(NsTable + "table-cell").ToList();
            if (col < cells.Count)
            {
                var textP = cells[col].Element(nsText + "p");
                result.Add(textP?.Value);
            }
            else
            {
                result.Add(null);
            }
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // AddColumn, SetColumnWidth, GetColumnWidth (R217, R218)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Append a column to the named sheet by adding a cell to each existing row.
    /// If header is non-null, sets the cell value in the first row.
    /// R217: AddColumn for spreadsheet editing.
    /// </summary>
    public void AddColumn(string sheetName, string? header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        bool isFirstRow = true;
        bool hasRows = false;
        foreach (var row in sheet.Rows)
        {
            hasRows = true;
            var cell = new XElement(NsTable + "table-cell");
            if (isFirstRow && header != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", header));
            }
            row.Element.Add(cell);
            isFirstRow = false;
        }
        // If the sheet has no rows but a header was given, create a header row
        if (!hasRows && header != null)
        {
            var headerRow = new XElement(NsTable + "table-row");
            var cell = new XElement(NsTable + "table-cell");
            cell.SetAttributeValue(NsOffice + "value-type", "string");
            cell.Add(new XElement(nsText + "p", header));
            headerRow.Add(cell);
            sheet.Element.Add(headerRow);
        }
    }

    /// <summary>
    /// Store the width for a column in the named sheet.
    /// Width is stored in-memory (not persisted to FODS XML in this implementation).
    /// R218: SetColumnWidth for spreadsheet formatting.
    /// </summary>
    public void SetColumnWidth(string sheetName, int colIndex, double width)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex), "Column index must not be negative.");
        if (width < 0)
            throw new ArgumentOutOfRangeException(nameof(width), "Width must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (!_columnWidths.TryGetValue(sheetName, out var cols))
        {
            cols = new Dictionary<int, double>();
            _columnWidths[sheetName] = cols;
        }
        cols[colIndex] = width;
    }

    /// <summary>
    /// Return the width of the column at <paramref name="colIndex"/> in the named sheet, in points.
    /// GI-FODS-NET-001 Phase 3d: reads from ODF style chain via FodsStyleResolver.
    /// SetColumnWidth in-memory override takes priority. Returns 0.0 if no style defined.
    /// R218: GetColumnWidth for spreadsheet formatting.
    /// </summary>
    public double GetColumnWidth(string sheetName, int colIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex), "Column index must not be negative.");
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        // In-memory override takes priority (from SetColumnWidth)
        if (_columnWidths.TryGetValue(sheetName, out var cols) && cols.TryGetValue(colIndex, out var width))
            return width;
        // ODF style chain read (Phase 3d)
        var colEl = GetTableColumnElement(sheetName, colIndex);
        return colEl is null ? 0.0 : FodsStyleResolver.ResolveColumnStyle(_doc, colEl).Width;
    }

    /// <summary>
    /// Navigate to the <c>table:table-column</c> element at <paramref name="colIndex"/>
    /// inside the named sheet, respecting <c>table:number-columns-repeated</c>.
    /// Returns null if the sheet does not exist or the column index is out of range.
    /// </summary>
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

    // -------------------------------------------------------------------------
    // SetCellBold / GetCellBold / SetCellItalic / GetCellItalic (R221, R222)
    // -------------------------------------------------------------------------
    private static readonly XNamespace NsFo =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");

    // GI-FODS-NET-001 Phase 3c: config:config-item namespace for office:settings parsing
    private static readonly XNamespace NsConfig =
        XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:config:1.0");

    /// <summary>
    /// GI-FODS-NET-001 Phase 3c — navigate office:settings to find a config:config-item
    /// for the given sheet name and item name.
    /// ODF path: office:settings/config:config-item-set/config:config-item-map-named
    ///           /config:config-item-map-entry[@config:name=sheetName]
    ///           /config:config-item[@config:name=itemName]
    /// </summary>
    private string? GetSheetConfigItem(string sheetName, string itemName)
    {
        var settings = _doc.Root?.Element(NsOffice + "settings");
        if (settings is null) return null;
        foreach (var itemSet in settings.Elements(NsConfig + "config-item-set"))
        {
            foreach (var mapNamed in itemSet.Elements(NsConfig + "config-item-map-named"))
            {
                foreach (var entry in mapNamed.Elements(NsConfig + "config-item-map-entry"))
                {
                    if (entry.Attribute(NsConfig + "name")?.Value != sheetName) continue;
                    var item = entry.Elements(NsConfig + "config-item")
                        .FirstOrDefault(ci => ci.Attribute(NsConfig + "name")?.Value == itemName);
                    if (item is not null) return item.Value;
                }
            }
        }
        return null;
    }

    private static void EnsureCell(FodsSheet sheet, int row, int col)
    {
        while (row >= sheet.Rows.Count)
            sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count)
            r.Element.Add(new XElement(NsTable + "table-cell"));
    }

    public static void SetCellBold(FodsSheet sheet, int row, int col, bool bold)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(
            NsFo + "font-weight", bold ? "bold" : "normal");
    }

    public static bool GetCellBold(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return false;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return false;
        return r.Cells[col].Element.Attribute(NsFo + "font-weight")?.Value == "bold";
    }

    public static void SetCellItalic(FodsSheet sheet, int row, int col, bool italic)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(
            NsFo + "font-style", italic ? "italic" : "normal");
    }

    public static bool GetCellItalic(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return false;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return false;
        return r.Cells[col].Element.Attribute(NsFo + "font-style")?.Value == "italic";
    }

    // -------------------------------------------------------------------------
    // SetCellFontSize / GetCellFontSize (R223)
    // -------------------------------------------------------------------------

    public static void SetCellFontSize(FodsSheet sheet, int row, int col, int size)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (size < 0) throw new ArgumentOutOfRangeException(nameof(size));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-size", size.ToString());
    }

    public static int GetCellFontSize(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return 0;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return 0;
        var raw = r.Cells[col].Element.Attribute(NsFo + "font-size")?.Value;
        return raw is not null && int.TryParse(raw, out int v) ? v : 0;
    }

    // -------------------------------------------------------------------------
    // SetCellFontName / GetCellFontName (R224)
    // -------------------------------------------------------------------------

    public static void SetCellFontName(FodsSheet sheet, int row, int col, string fontName)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(fontName);
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-family", fontName);
    }

    public static string? GetCellFontName(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "font-family")?.Value;
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues (R223)
    // -------------------------------------------------------------------------

    public IReadOnlyList<string?> GetDistinctValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var values = GetColumnValues(sheetName, col);
        var seen = new System.Collections.Generic.HashSet<string?>();
        var result = new List<string?>();
        foreach (var v in values)
        {
            if (seen.Add(v))
                result.Add(v);
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // FilterRows with row-values predicate (R221)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Return row indices from the named sheet where the predicate on the row values returns true.
    /// R221: FilterRows with row-values predicate — returns matching row indices.
    /// </summary>
    public IReadOnlyList<int> FilterRows(string sheetName, Func<IReadOnlyList<string?>, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();

        var result = new List<int>();
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            if (predicate(rowVals))
                result.Add(r);
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // Simplified first-sheet API (R225, R227)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Total number of rows in the first sheet. Returns 0 if document has no sheets.
    /// R225: RowCount property for simplified single-sheet API.
    /// </summary>
    public int RowCount => GetRowCount();

    /// <summary>
    /// Append a row with the given values to the first sheet.
    /// R225: AddRow for simplified single-sheet API.
    /// </summary>
    public void AddRow(IList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        var sheet = _activeSheet != null ? (GetSheetByName(_activeSheet) ?? sheets[0]) : sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var row = new XElement(NsTable + "table-row");
        foreach (var val in values)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (!string.IsNullOrEmpty(val))
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", val));
            }
            row.Add(cell);
        }
        sheet.Element.Add(row);
    }

    /// <summary>
    /// Return aggregate statistics for a numeric column in the first sheet.
    /// All rows are scanned; non-numeric cells are skipped.
    /// Returns a default ColumnStats (all zeros) if no numeric values are found.
    /// R225: GetColumnStats for simplified single-sheet API.
    /// </summary>
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

    /// <summary>
    /// Return all cell values from the given column (zero-based) in the first sheet.
    /// All rows including the header row are returned.
    /// Returns empty if the document has no sheets.
    /// R225: single-arg GetColumnValues for simplified first-sheet API.
    /// </summary>
    public IReadOnlyList<string?> GetColumnValues(int col)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheets = Sheets;
        if (sheets.Count == 0) return Array.Empty<string?>();
        var name = sheets[0].Name;
        if (name is null) return Array.Empty<string?>();
        return GetColumnValues(name, col);
    }

    /// <summary>
    /// Delete <paramref name="count"/> rows starting at <paramref name="startRow"/> in the first sheet.
    /// R225: DeleteRows for simplified single-sheet API.
    /// </summary>
    public void DeleteRows(int startRow, int count)
    {
        if (startRow < 0) throw new ArgumentOutOfRangeException(nameof(startRow));
        if (count < 0) throw new ArgumentOutOfRangeException(nameof(count));
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        var sheet = sheets[0];
        for (int i = 0; i < count; i++)
        {
            var rows = sheet.Rows;
            if (startRow >= rows.Count) break;
            rows[startRow].Element.Remove();
        }
    }

    /// <summary>
    /// Remove all rows from the first sheet.
    /// R225: ClearSheet for simplified single-sheet API.
    /// </summary>
    public void ClearSheet()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        var sheet = sheets[0];
        foreach (var row in sheet.Rows.ToList())
            row.Element.Remove();
    }

    /// <summary>
    /// Insert a new row with the given values at <paramref name="index"/> in the first sheet.
    /// Existing rows at and after the index shift down. Appends when index >= row count.
    /// R227: InsertRow(int, IList&lt;string&gt;) for simplified single-sheet API.
    /// </summary>
    public void InsertRow(int index, IList<string> values)
    {
        if (index < 0) throw new ArgumentOutOfRangeException(nameof(index));
        ArgumentNullException.ThrowIfNull(values);
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        var sheet = sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var newRow = new XElement(NsTable + "table-row");
        foreach (var val in values)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (!string.IsNullOrEmpty(val))
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", val));
            }
            newRow.Add(cell);
        }
        var rows = sheet.Rows;
        if (index < rows.Count)
            rows[index].Element.AddBeforeSelf(newRow);
        else if (rows.Count > 0)
            rows[^1].Element.AddAfterSelf(newRow);
        else
            sheet.Element.Add(newRow);
    }

    /// <summary>
    /// Return a new FodsDocument containing only the rows from the first sheet where
    /// the cell at <paramref name="col"/> equals <paramref name="value"/> (case-sensitive).
    /// The matching rows are copied to positions 0..N-1 in the new document (no header row).
    /// R227: FilterRows(int, string) returning FodsDocument for simplified single-sheet API.
    /// </summary>
    public FodsDocument FilterRows(int col, string value)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(value);
        var sheets = Sheets;
        if (sheets.Count == 0)
            return FodsDocument.CreateEmpty();
        var sheet = sheets[0];
        var result = FodsDocument.CreateEmpty();
        result.AddSheet(sheet.Name ?? "Sheet1");
        var resultSheet = result.Sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col >= cells.Count) continue;
            var cellVal = cells[col].Element(nsText + "p")?.Value;
            if (cellVal == value)
                resultSheet.Element.Add(new XElement(row.Element));
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // R238, R245, R247: Additional compatibility APIs
    // -------------------------------------------------------------------------

    /// <summary>Export the named sheet as a JSON string, or write all-sheets JSON to a file path. R245/R319.</summary>
    public string ExportToJson(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        if (sheetName.Contains(System.IO.Path.DirectorySeparatorChar) || sheetName.Contains(System.IO.Path.AltDirectorySeparatorChar) || System.IO.Path.HasExtension(sheetName))
        { System.IO.File.WriteAllText(sheetName, ExportToJson(), System.Text.Encoding.UTF8); return string.Empty; }
        return ExportSheetToJson(sheetName);
    }

    /// <summary>Export the named sheet as JSON and write it to the given file path. R288.</summary>
    public void ExportToJson(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var json = ExportSheetToJson(sheetName);
        System.IO.File.WriteAllText(filePath, json);
    }

    /// <summary>Apply a named format to a cell (stored as fo:data-style-name attribute). R257.</summary>
    public void SetCellFormatting(string sheetName, int row, int col, string format)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        while (row >= sheet.Rows.Count)
            sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count)
            r.Element.Add(new XElement(NsTable + "table-cell"));
        r.Cells[col].Element.SetAttributeValue(NsFo + "data-style-name", format);
    }

    /// <summary>Export all sheets as a combined JSON object. R256.</summary>
    public string ExportToJson()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return "{}";
        var parts = new System.Collections.Generic.List<string>();
        foreach (var sheet in sheets)
        {
            var name = sheet.Name ?? "sheet";
            var json = ExportSheetToJson(name);
            parts.Add($"\"{EscapeJson(name)}\": {json}");
        }
        return "{" + string.Join(", ", parts) + "}";
    }

    private static string EscapeJson(string s)
        => s.Replace("\\", "\\\\").Replace("\"", "\\\"");

    /// <summary>Return a 2D array of cell values from startRow/Col to endRow/Col (inclusive). R256.</summary>
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
        {
            int absRow = startRow + r;
            for (int c = 0; c < cols; c++)
                result[r, c] = GetCellValue(sheet, absRow, startCol + c);
        }
        return result;
    }

    /// <summary>Delete a single row at rowIndex in the named sheet. R245.</summary>
    public void DeleteRow(string sheetName, int rowIndex)
    {
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        DeleteRows(sheetName, rowIndex, 1);
    }

    /// <summary>Clear the value of the cell at (row, col) in the named sheet. R245.</summary>
    public void ClearCellValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return;
        if (row < 0 || row >= sheet.Rows.Count) return;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return;
        SetCellValue(sheetName, row, col, "");
    }

    /// <summary>Set the bold attribute for a cell in the named sheet. R247.</summary>
    public void SetCellBold(string sheetName, int row, int col, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        SetCellBold(sheet, row, col, bold);
    }

    /// <summary>Set the italic attribute for a cell in the named sheet. R247.</summary>
    public void SetCellItalic(string sheetName, int row, int col, bool italic)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        SetCellItalic(sheet, row, col, italic);
    }

    private readonly Dictionary<(string sheet, int row), double> _rowHeights = new();

    /// <summary>Set the row height for a row (in-memory only; not persisted to FODS XML). R247.</summary>
    public void SetRowHeight(string sheetName, int rowIndex, double height)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        _rowHeights[(sheetName, rowIndex)] = height;
    }

    /// <summary>
    /// Return the row height for the row at <paramref name="rowIndex"/> in the named sheet, in points.
    /// GI-FODS-NET-001 Phase 3d: reads from ODF style chain via FodsStyleResolver.
    /// SetRowHeight in-memory override takes priority. Returns 0.0 if no ODF height style defined.
    /// R284.
    /// </summary>
    public double GetRowHeight(string sheetName, int rowIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        // In-memory override takes priority (from SetRowHeight)
        if (_rowHeights.TryGetValue((sheetName, rowIndex), out var h)) return h;
        // ODF style chain read (Phase 3d)
        if (rowIndex >= sheet.Rows.Count) return 0.0;
        return FodsStyleResolver.ResolveRowStyle(_doc, sheet.Rows[rowIndex].Element).Height;
    }

    /// <summary>
    /// Return all cell values from the column whose header matches the given name.
    /// Scans row 0 for the header; returns all rows in that column (including header).
    /// R238.
    /// </summary>
    public List<string> GetColumnValues(string sheetName, string header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        var sheet = GetSheetByName(sheetName);
        if (sheet is null || sheet.Rows.Count == 0) return new List<string>();

        // Find column index by scanning row 0 (header row)
        var headerRowVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerRowVals.Count; i++)
        {
            if (headerRowVals[i] == header) { colIndex = i; break; }
        }
        if (colIndex < 0) return new List<string>();

        var result = new List<string>();
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var vals = GetRowValues(sheet, r);
            result.Add(colIndex < vals.Count ? (vals[colIndex] ?? "") : "");
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // R229: First-sheet SetCellBold / SetCellItalic / SetCellFontSize (3-arg)
    // -------------------------------------------------------------------------

    /// <summary>Set bold on first sheet cell. R229.</summary>
    public void SetCellBold(int row, int col, bool bold)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        SetCellBold(sheets[0], row, col, bold);
    }

    /// <summary>Set italic on first sheet cell. R229.</summary>
    public void SetCellItalic(int row, int col, bool italic)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        SetCellItalic(sheets[0], row, col, italic);
    }

    /// <summary>Set font size on first sheet cell. R229.</summary>
    public void SetCellFontSize(int row, int col, int size)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        SetCellFontSize(sheets[0], row, col, size);
    }

    // -------------------------------------------------------------------------
    // R233: GetSheetCount, GetDocumentStats
    // -------------------------------------------------------------------------

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

    // -------------------------------------------------------------------------
    // R231: SwitchSheet, GetSheetCount already above
    // -------------------------------------------------------------------------

    private string? _activeSheet;

    /// <summary>Switch the active sheet for first-sheet methods. R231.</summary>
    public void SwitchSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _activeSheet = sheetName;
    }

    // -------------------------------------------------------------------------
    // R240: AddRow(sheetName, values)
    // -------------------------------------------------------------------------

    /// <summary>Append a row with the given values to the named sheet. R240.</summary>
    public void AddRow(string sheetName, IReadOnlyList<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        int rowIndex = sheet.Rows.Count;
        InsertRowWithValues(sheetName, rowIndex, values);
    }

    // -------------------------------------------------------------------------
    // R243: InsertRowWithValues(sheetName, values) — append overload
    // -------------------------------------------------------------------------

    /// <summary>Append a row with the given values to the named sheet (2-arg overload). R243.</summary>
    public void InsertRowWithValues(string sheetName, IReadOnlyList<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        InsertRowWithValues(sheetName, sheet.Rows.Count, values);
    }

    // -------------------------------------------------------------------------
    // R236: ExportSheetToTsv, AddColumn (3-arg)
    // -------------------------------------------------------------------------

    /// <summary>Export a named sheet as TSV (tab-separated). R236.</summary>
    public string ExportSheetToTsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var sb = new System.Text.StringBuilder();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var row in sheet.Rows)
        {
            var cells = row.Cells;
            for (int i = 0; i < cells.Count; i++)
            {
                if (i > 0) sb.Append('\t');
                var val = cells[i].Element.Element(nsText + "p")?.Value ?? cells[i].Element.Value;
                sb.Append(val ?? "");
            }
            sb.AppendLine();
        }
        return sb.ToString();
    }

    /// <summary>
    /// Add a new column to the named sheet with the given header and values.
    /// Row 0 gets the header; subsequent rows get the values (in order).
    /// R236.
    /// </summary>
    public void AddColumn(string sheetName, string header, IEnumerable<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));

        var valueList = values.ToList();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");

        // Ensure header row (row 0) exists
        while (sheet.Rows.Count == 0)
            sheet.Element.Add(new XElement(NsTable + "table-row"));

        // Add header to row 0
        var headerCell = new XElement(NsTable + "table-cell",
            new XElement(nsText + "p", header));
        sheet.Rows[0].Element.Add(headerCell);

        // Add values to rows 1..n
        for (int i = 0; i < valueList.Count; i++)
        {
            int rowIdx = i + 1;
            while (sheet.Rows.Count <= rowIdx)
                sheet.Element.Add(new XElement(NsTable + "table-row"));
            var cell = new XElement(NsTable + "table-cell",
                new XElement(nsText + "p", valueList[i] ?? ""));
            sheet.Rows[rowIdx].Element.Add(cell);
        }
    }

    // -------------------------------------------------------------------------
    // R243/R251: GetColumnNames alias
    // -------------------------------------------------------------------------

    /// <summary>Return column header names for the named sheet. Alias for GetColumnHeaders. R251.</summary>
    public List<string> GetColumnNames(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (GetSheetByName(sheetName) is null)
            throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        var headers = GetColumnHeaders(sheetName);
        return headers.ToList();
    }

    // -------------------------------------------------------------------------
    // R249: GetFormula, SetFormula, EvaluateFormulas
    // -------------------------------------------------------------------------

    /// <summary>Return the formula for a cell (alias for GetCellFormula). R249.</summary>
    public string? GetFormula(string sheetName, int row, int col) => GetCellFormula(sheetName, row, col);

    /// <summary>Set the formula for a cell (alias for SetCellFormula). R249.</summary>
    public void SetFormula(string sheetName, int row, int col, string formula)
        => SetCellFormula(sheetName, row, col, formula);

    /// <summary>No-op formula evaluator (formulas are stored but not computed). R249.</summary>
    public void EvaluateFormulas() { /* no-op: evaluation not supported */ }

    /// <summary>Return the displayed value for a formula cell. R238.</summary>
    public string? GetCellFormulaValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        // Return empty string (not null) for cells that exist but have no computed value
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Value ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // R250: MergeSheet, CopyRange
    // -------------------------------------------------------------------------

    /// <summary>Copy a sheet from sourceDoc into this document under the given name. R250.</summary>
    public void MergeSheet(FodsDocument sourceDoc, string sheetName)
    {
        ArgumentNullException.ThrowIfNull(sourceDoc);
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var srcSheet = sourceDoc.GetSheetByName(sheetName);
        if (srcSheet is null) return;

        // Add the sheet with a new (possibly renamed) name
        string destName = sheetName;
        int suffix = 2;
        while (GetSheetByName(destName) != null)
            destName = $"{sheetName}_{suffix++}";

        AddSheet(destName);
        var destSheet = GetSheetByName(destName)!;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");

        foreach (var srcRow in srcSheet.Rows)
        {
            var newRow = new XElement(NsTable + "table-row");
            foreach (var srcCell in srcRow.Cells)
            {
                var val = srcCell.Element.Element(nsText + "p")?.Value ?? srcCell.Element.Value;
                newRow.Add(new XElement(NsTable + "table-cell",
                    new XElement(nsText + "p", val ?? "")));
            }
            destSheet.Element.Add(newRow);
        }
    }

    /// <summary>
    /// Copy a rectangular range from srcSheet to destSheet.
    /// R250.
    /// </summary>
    public void CopyRange(string srcSheet, int srcRow, int srcCol,
                          string destSheet, int destRow, int destCol,
                          int rows, int cols)
    {
        if (string.IsNullOrWhiteSpace(srcSheet))
            throw new ArgumentException("Source sheet name must not be null or empty.", nameof(srcSheet));
        if (string.IsNullOrWhiteSpace(destSheet))
            throw new ArgumentException("Destination sheet name must not be null or empty.", nameof(destSheet));
        var src = GetSheetByName(srcSheet);
        var dest = GetSheetByName(destSheet);
        if (src is null || dest is null) return;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        for (int r = 0; r < rows; r++)
        {
            int sr = srcRow + r, dr = destRow + r;
            while (dest.Rows.Count <= dr)
                dest.Element.Add(new XElement(NsTable + "table-row"));
            var destRowEl = dest.Rows[dr];
            for (int c = 0; c < cols; c++)
            {
                int sc = srcCol + c, dc = destCol + c;
                string val = "";
                if (sr < src.Rows.Count)
                {
                    var srcCells = src.Rows[sr].Cells;
                    if (sc < srcCells.Count)
                        val = srcCells[sc].Element.Element(nsText + "p")?.Value ?? srcCells[sc].Element.Value ?? "";
                }
                while (destRowEl.Cells.Count <= dc)
                    destRowEl.Element.Add(new XElement(NsTable + "table-cell"));
                var destCell = destRowEl.Cells[dc].Element;
                var pEl = destCell.Element(nsText + "p");
                if (pEl is null)
                {
                    destCell.Add(new XElement(nsText + "p", val));
                }
                else
                {
                    pEl.Value = val;
                }
            }
        }
    }

    // -------------------------------------------------------------------------
    // R248: ImportFromCsv
    // -------------------------------------------------------------------------

    /// <summary>Import a CSV file into the named sheet. R248.</summary>
    public void ImportFromCsv(string sheetName, string csvFilePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(csvFilePath))
            throw new ArgumentException("CSV file path must not be null or empty.", nameof(csvFilePath));

        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));

        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var line in File.ReadAllLines(csvFilePath))
        {
            var parts = line.Split(',');
            var rowEl = new XElement(NsTable + "table-row");
            foreach (var part in parts)
            {
                var val = part.Trim('"');
                rowEl.Add(new XElement(NsTable + "table-cell",
                    new XElement(nsText + "p", val)));
            }
            sheet.Element.Add(rowEl);
        }
    }

    // -------------------------------------------------------------------------
    // R251: ToXml alias
    // -------------------------------------------------------------------------

    /// <summary>Return the document as an FODS XML string. Alias for ToFodsXml. R251.</summary>
    public string ToXml() => ToFodsXml();

    // -------------------------------------------------------------------------
    // R225/R229: SetCellColor, GetCellColor (static + instance)
    // -------------------------------------------------------------------------

    private static readonly XNamespace NsCustom =
        XNamespace.Get("urn:format-factory:cell-style");

    /// <summary>Set the background color for a cell (static overload). R225.</summary>
    public static void SetCellColor(FodsSheet sheet, int row, int col, string color)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(color);
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "background-color", color);
    }

    /// <summary>Get the background color of a cell (static overload). R225.</summary>
    public static string? GetCellColor(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "background-color")?.Value;
    }

    /// <summary>Set the background color for a first-sheet cell. R229.</summary>
    public void SetCellColor(int row, int col, string color)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        SetCellColor(sheets[0], row, col, color);
    }

    /// <summary>Get the background color of a first-sheet cell. R229.</summary>
    public string? GetCellColor(int row, int col)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return null;
        return GetCellColor(sheets[0], row, col);
    }

    /// <summary>Set the background color for a named-sheet cell. R229.</summary>
    public void SetCellColor(string sheetName, int row, int col, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        SetCellColor(sheet, row, col, color);
    }

    /// <summary>Get the background color of a named-sheet cell. R229.</summary>
    public string GetCellColor(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return string.Empty;
        return GetCellColor(sheet, row, col) ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // R226: SetCellBorder, GetCellBorder (static + instance)
    // -------------------------------------------------------------------------

    /// <summary>Set the border style for a cell (static overload). R226.</summary>
    public static void SetCellBorder(FodsSheet sheet, int row, int col, string border)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(border);
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "border", border);
    }

    /// <summary>Get the border style of a cell (static overload). R226.</summary>
    public static string? GetCellBorder(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "border")?.Value;
    }

    /// <summary>Set the border style for a named-sheet cell. R226.</summary>
    public void SetCellBorder(string sheetName, int row, int col, string border)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        SetCellBorder(sheet, row, col, border);
    }

    /// <summary>Get the border style of a named-sheet cell. R226/R353.</summary>
    public string? GetCellBorder(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return GetCellBorder(sheet, row, col) ?? string.Empty;
    }

    /// <summary>Set cell background color (alias for SetCellColor, static overload). R225.</summary>
    public static void SetCellBackgroundColor(FodsSheet sheet, int row, int col, string color)
        => SetCellColor(sheet, row, col, color);

    /// <summary>Set cell background color (alias for SetCellColor). R229.</summary>
    public void SetCellBackgroundColor(string sheetName, int row, int col, string color)
        => SetCellColor(sheetName, row, col, color);

    /// <summary>Set cell background color (alias for SetCellBackgroundColor). R272.</summary>
    public void SetCellBackground(string sheetName, int row, int col, string colorName)
        => SetCellColor(sheetName, row, col, colorName);

    // -------------------------------------------------------------------------
    // R273: SetCellRange
    // -------------------------------------------------------------------------

    /// <summary>Bulk-set a block of cells starting at startRow/startCol from a jagged array. R273.</summary>
    public void SetCellRange(string sheetName, int startRow, int startCol, string[][] values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        for (int r = 0; r < values.Length; r++)
        {
            var rowValues = values[r];
            if (rowValues == null) continue;
            for (int c = 0; c < rowValues.Length; c++)
                SetCellValueAutoExpand(sheet, startRow + r, startCol + c, rowValues[c] ?? "");
        }
    }

    // -------------------------------------------------------------------------
    // R276: SetColumnHeaders / GetColumnHeaders (sheet-name overload)
    // -------------------------------------------------------------------------

    /// <summary>Set the header row (row 0) of the named sheet to the given values. R276.</summary>
    public void SetColumnHeaders(string sheetName, string[] headers)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(headers);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        for (int c = 0; c < headers.Length; c++)
            SetCellValueAutoExpand(sheet, 0, c, headers[c] ?? "");
    }

    // -------------------------------------------------------------------------
    // R237: GetStringColumnValues
    // -------------------------------------------------------------------------

    /// <summary>Return all values in the specified column of the named sheet as non-null strings. R237.</summary>
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
            var val = row.Cells[col].Element.Element(nsText + "p")?.Value ?? row.Cells[col].Element.Value ?? "";
            result.Add(val);
        }
        return result;
    }

    /// <summary>Return a new document containing only rows where the given column header's cell matches value. R241.</summary>
    public FodsDocument FilterRows(string sheetName, string columnName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnName);
        ArgumentNullException.ThrowIfNull(value);
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (sheet.Rows.Count == 0) { var empty = FodsDocument.CreateEmpty(); empty.AddSheet(sheetName); return empty; }
        var headerVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerVals.Count; i++)
            if (headerVals[i] == columnName) { colIndex = i; break; }
        var result = FodsDocument.CreateEmpty();
        result.AddSheet(sheetName);
        var resultSheet = result.GetSheetByName(sheetName)!;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        resultSheet.Element.Add(new XElement(sheet.Rows[0].Element));
        if (colIndex >= 0)
        {
            foreach (var row in sheet.Rows.Skip(1))
            {
                var cells = row.Element.Elements(NsTable + "table-cell").ToList();
                if (colIndex < cells.Count && cells[colIndex].Element(nsText + "p")?.Value == value)
                    resultSheet.Element.Add(new XElement(row.Element));
            }
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // R212/R238: ColumnCount property
    // -------------------------------------------------------------------------

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

    // -------------------------------------------------------------------------
    // R255: SortSheet (alias for SortRows)
    // -------------------------------------------------------------------------

    /// <summary>Sort data rows by column header (alias for SortRows). R255.</summary>
    public void SortSheet(string sheetName, string columnHeader, bool ascending)
        => SortRows(sheetName, columnHeader, ascending);

    /// <summary>Delete a column identified by its header name. R253/R311.</summary>
    public void DeleteColumn(string sheetName, string columnName)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnName);
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (sheet.Rows.Count == 0) throw new ArgumentException($"Column '{columnName}' not found in sheet '{sheetName}'.", nameof(columnName));
        var headerVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerVals.Count; i++)
            if (headerVals[i] == columnName) { colIndex = i; break; }
        if (colIndex < 0) throw new ArgumentException($"Column '{columnName}' not found in sheet '{sheetName}'.", nameof(columnName));
        DeleteColumn(sheetName, colIndex);
    }

    /// <summary>
    /// Sort data rows (rows 1..N) in the named sheet by the column with the given header name.
    /// Row 0 (header row) is kept in place. R238.
    /// </summary>
    public void SortRows(string sheetName, string columnHeader, bool ascending)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnHeader);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        if (sheet.Rows.Count <= 1) return;

        // Find column index from header row
        var headerRowVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerRowVals.Count; i++)
        {
            if (headerRowVals[i] == columnHeader) { colIndex = i; break; }
        }
        if (colIndex < 0) return;

        var rows = sheet.Rows;
        var headerEl = rows[0].Element;
        var dataRows = rows.Skip(1).ToList();

        var sorted = dataRows.OrderBy(r =>
        {
            var cells = r.Cells;
            if (colIndex >= cells.Count) return (object)"";
            var val = cells[colIndex].Element.Value ?? "";
            if (double.TryParse(val, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var num))
                return (object)num;
            return val;
        }, Comparer<object>.Create((a, b) =>
        {
            if (a is double da && b is double db) return da.CompareTo(db);
            return string.Compare(a?.ToString() ?? "", b?.ToString() ?? "", StringComparison.Ordinal);
        })).ToList();

        if (!ascending) sorted.Reverse();

        var tableEl = sheet.Element;
        var allRowEls = rows.Select(r => r.Element).ToList();
        foreach (var el in allRowEls) el.Remove();
        tableEl.Add(headerEl);
        foreach (var r in sorted) tableEl.Add(r.Element);
    }

    // -------------------------------------------------------------------------
    // FreezeRows, SetNamedRange, GetNamedRange (R264)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // GetSheetIndex (R271)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Return the zero-based index of the named sheet in the document's sheet list.
    /// Throws ArgumentException for null/whitespace names, or InvalidOperationException if not found.
    /// R271: GetSheetIndex for sheet position queries.
    /// </summary>
    public int GetSheetIndex(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheets = Sheets;
        for (int i = 0; i < sheets.Count; i++)
            if (sheets[i].Name == sheetName) return i;
        throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
    }

    // -------------------------------------------------------------------------
    // MergeSheets (R270)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Append all rows from the source sheet to the end of the target sheet.
    /// Both sheets must exist. The source sheet is not modified.
    /// R270: MergeSheets for combining sheet data.
    /// </summary>
    public void MergeSheets(string sourceSheetName, string targetSheetName)
    {
        if (string.IsNullOrWhiteSpace(sourceSheetName))
            throw new ArgumentException("Source sheet name must not be null or empty.", nameof(sourceSheetName));
        if (string.IsNullOrWhiteSpace(targetSheetName))
            throw new ArgumentException("Target sheet name must not be null or empty.", nameof(targetSheetName));
        var source = GetSheetByName(sourceSheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sourceSheetName}' exists.");
        var target = GetSheetByName(targetSheetName)
            ?? throw new InvalidOperationException($"No sheet named '{targetSheetName}' exists.");
        foreach (var row in source.Rows)
        {
            var clonedRow = new XElement(row.Element);
            target.Element.Add(clonedRow);
        }
    }

    /// <summary>
    /// Freeze the top N rows of a sheet (analogous to freeze panes).
    /// This operation is validated but not persisted to FODS XML in this implementation.
    /// R264: FreezeRows for spreadsheet view control.
    /// </summary>
    public void FreezeRows(string sheetName, int rowCount)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowCount < 0)
            throw new ArgumentOutOfRangeException(nameof(rowCount), "rowCount must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        // no-op: freeze pane metadata not persisted in this implementation
    }

    /// <summary>
    /// Define a named range on a sheet.
    /// Stored in-memory (not persisted to FODS XML in this implementation).
    /// R264: SetNamedRange for spreadsheet named-range support.
    /// </summary>
    public void SetNamedRange(string name, string sheetName, string range)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name must not be null or empty.", nameof(name));
        _namedRanges[name] = range;
    }

    /// <summary>
    /// Retrieve the range string for a named range previously set via SetNamedRange.
    /// Returns null if the name has not been defined.
    /// R264: GetNamedRange for spreadsheet named-range support.
    /// </summary>
    public string? GetNamedRange(string name)
    {
        if (name == null) throw new ArgumentNullException(nameof(name));
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("name must not be whitespace.", nameof(name));
        if (!_namedRanges.TryGetValue(name, out var r))
            throw new KeyNotFoundException($"Named range '{name}' not found.");
        return r;
    }

    // -------------------------------------------------------------------------
    // SetAutoFilter, GetFilteredRows, ClearFilter (R265)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Apply an auto-filter on the named column of a sheet.
    /// Only rows where the column value equals the specified value are returned by GetFilteredRows.
    /// Filter state is persisted in the FODS file for save/load round-trips.
    /// R265: SetAutoFilter for spreadsheet filtering.
    /// </summary>
    public void SetAutoFilter(string sheetName, string colName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        _activeFilters[sheetName] = (colName, value);
        // Persist in XDocument for save/load round-trip
        sheet.Element.SetAttributeValue(NsFfExt + "auto-filter", $"{colName}:{value}");
    }

    /// <summary>
    /// Clear the active auto-filter from a sheet.
    /// R265: ClearFilter for spreadsheet filtering.
    /// </summary>
    public void ClearFilter(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _activeFilters.Remove(sheetName);
        var sheet = GetSheetByName(sheetName);
        sheet?.Element.Attribute(NsFfExt + "auto-filter")?.Remove();
    }

    /// <summary>
    /// Return the data rows (as column-name → value dictionaries) matching the active auto-filter on the sheet.
    /// Returns an empty list if no filter is active.
    /// The first row is treated as the header row.
    /// R265: GetFilteredRows for spreadsheet filtering.
    /// </summary>
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

    // -------------------------------------------------------------------------
    // ExportToCsv alias (R267)
    // -------------------------------------------------------------------------

    /// <summary>Export the specified sheet to a CSV string. Alias for ExportSheetToCsv. R289.</summary>
    public string ExportToCsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return ExportSheetToCsv(sheetName);
    }

    /// <summary>
    /// Export the specified sheet to a CSV file.
    /// Alias for ExportSheetToCsvFile with identical semantics.
    /// R267: ExportToCsv for spreadsheet CSV export.
    /// </summary>
    public void ExportToCsv(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        ExportSheetToCsvFile(sheetName, filePath);
    }

    // -------------------------------------------------------------------------
    // AddColumn(string, string[]) overload (R266)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Append a column to the named sheet using an array of values.
    /// values[0] is placed in the first row, values[1] in the second, etc.
    /// If the sheet has more rows than values, remaining cells are left empty.
    /// If values has more elements than rows, new rows are added.
    /// R266: AddColumn(string[]) overload for bulk column insertion.
    /// </summary>
    public void AddColumn(string sheetName, string[] values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (values == null) throw new ArgumentNullException(nameof(values));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        int rowIdx = 0;
        foreach (var row in sheet.Rows)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (rowIdx < values.Length && values[rowIdx] != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", values[rowIdx]));
            }
            row.Element.Add(cell);
            rowIdx++;
        }
        while (rowIdx < values.Length)
        {
            var newRow = new XElement(NsTable + "table-row");
            var cell = new XElement(NsTable + "table-cell");
            if (values[rowIdx] != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", values[rowIdx]));
            }
            newRow.Add(cell);
            sheet.Element.Add(newRow);
            rowIdx++;
        }
    }

    // -------------------------------------------------------------------------
    // R278: GetFormulas
    // -------------------------------------------------------------------------

    /// <summary>Return all formulas in the named sheet as a list of formula strings. R278.</summary>
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

    // -------------------------------------------------------------------------
    // R280: SetCellComment / GetCellComment
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string sheet, int row, int col), string> _cellComments = new();

    /// <summary>Attach a text comment to a cell. R280.</summary>
    public void SetCellComment(string sheetName, int row, int col, string comment)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (GetSheetByName(sheetName) == null)
            throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        _cellComments[(sheetName, row, col)] = comment ?? string.Empty;
    }

    /// <summary>Return the comment attached to a cell, or empty string if none. R280.</summary>
    public string GetCellComment(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellComments.TryGetValue((sheetName, row, col), out var c) ? c : string.Empty;
    }

    // -------------------------------------------------------------------------
    // R281: SetCell / AddRowToSheet / ExportToHtml
    // -------------------------------------------------------------------------

    /// <summary>Set cell value (alias for SetCellValue). R281.</summary>
    public void SetCell(string sheetName, int row, int col, string value)
        => SetCellValue(sheetName, row, col, value);

    /// <summary>Append a row to the named sheet (alias for AddRow). R281.</summary>
    public void AddRowToSheet(string sheetName, string[] values)
        => AddRow(sheetName, values);

    /// <summary>Export the document to an HTML string. R281.</summary>
    public string ExportToHtml()
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head><body>");
        foreach (var sheet in Sheets)
        {
            sb.AppendLine($"<h2>{HtmlEscape(sheet.Name ?? "")}</h2>");
            sb.AppendLine("<table border=\"1\">");
            foreach (var row in sheet.Rows)
            {
                sb.Append("<tr>");
                foreach (var cell in row.Cells)
                {
                    var nsText2 = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
                    var val = cell.Element.Element(nsText2 + "p")?.Value ?? cell.Element.Value ?? "";
                    sb.Append($"<td>{HtmlEscape(val)}</td>");
                }
                sb.AppendLine("</tr>");
            }
            sb.AppendLine("</table>");
        }
        sb.AppendLine("</body></html>");
        return sb.ToString();
    }

    private static string HtmlEscape(string s)
        => s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;").Replace("\"", "&quot;");

    // -------------------------------------------------------------------------
    // R286: GetCellType
    // -------------------------------------------------------------------------

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
        // No value-type attribute: check for text content
        var nsText2 = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var text = cell.Element.Element(nsText2 + "p")?.Value ?? cell.Element.Value;
        return string.IsNullOrEmpty(text) ? "empty" : "string";
    }

    // -------------------------------------------------------------------------
    // R283: ClearCell / IsCellEmpty
    // -------------------------------------------------------------------------

    /// <summary>Clear the content of a cell (alias for ClearCellValue). R283.</summary>
    public void ClearCell(string sheetName, int row, int col)
        => ClearCellValue(sheetName, row, col);

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
        var val = GetCellValue(sheetName, row, col);
        return string.IsNullOrEmpty(val);
    }

    // =========================================================================
    // GI-FODS-NET-001 Phase 3a: Category E — Guard helpers
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
    // GI-FODS-NET-001 Phase 3a: Category A — DOM-computed methods + delegates
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
    // GI-FODS-NET-001 Phase 3a: Category B — Dict-backed property stubs
    // TODO: GI-FODS-NET-001 Phase 3b/3c — replace each getter with ODF XML read;
    //       replace each setter with ODF XML write. See plans/.claude/buzzing-wiggling-whistle.md
    // =========================================================================

    private readonly Dictionary<string, int> _sheetFreezeRows = new();
    private readonly Dictionary<string, int> _sheetFreezeColumns = new();

    /// <summary>R452: Return freeze row count for the named sheet.</summary>
    // GI-FODS-NET-001 Phase 3c — reads HorizontalSplitPosition from office:settings
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
    // TODO: GI-FODS-NET-001 Phase 3c — write to office:settings/config:config-item
    public void SetSheetFreezeRows(string sheetName, int rows)
    {
        RequireSheet(sheetName);
        if (rows < 0) throw new ArgumentOutOfRangeException(nameof(rows));
        _sheetFreezeRows[sheetName] = rows;
    }

    /// <summary>R453: Return freeze column count for the named sheet.</summary>
    // GI-FODS-NET-001 Phase 3c — reads VerticalSplitPosition from office:settings
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
    // TODO: GI-FODS-NET-001 Phase 3c — write to office:settings/config:config-item
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

    private readonly Dictionary<string, int> _sheetZoomLevel = new();

    /// <summary>R420/R480: Return the zoom level for the named sheet (default 100).</summary>
    // GI-FODS-NET-001 Phase 3c — reads ZoomValue from office:settings.
    // In-memory setter override takes priority; ODF default is 100.
    public int GetSheetZoomLevel(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetZoomLevel.TryGetValue(sheetName, out var ov)) return ov;
        var val = GetSheetConfigItem(sheetName, "ZoomValue");
        return val is not null && int.TryParse(val, out var z) ? z : 100;
    }

    /// <summary>R454/R480: Set the zoom level for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 Phase 3c — write to office:settings/config:config-item
    public void SetSheetZoomLevel(string sheetName, int zoom)
    {
        RequireSheet(sheetName);
        _sheetZoomLevel[sheetName] = zoom;
    }

    private readonly Dictionary<string, string> _sheetPrintArea = new();

    /// <summary>R423/R451: Return the print area for the named sheet (empty string if none).</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — read from table:named-range[@table:print-range]
    public string GetSheetPrintArea(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetPrintArea.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R451/R484: Set the print area for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — write table:named-range to ODF XML
    public void SetSheetPrintArea(string sheetName, string area)
    {
        RequireSheet(sheetName);
        _sheetPrintArea[sheetName] = area ?? string.Empty;
    }

    private readonly Dictionary<string, string> _sheetProtectionPasswords = new();

    /// <summary>R469: Return the protection password for the named sheet (empty string if none).</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — read from table:table/@table:protection-key
    public string GetSheetProtectionPassword(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetProtectionPasswords.TryGetValue(sheetName, out var v) ? v : string.Empty;
    }

    /// <summary>R469: Set the protection password for the named sheet.</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — write to ODF XML protection attributes
    public void SetSheetProtectionPassword(string sheetName, string password)
    {
        RequireSheet(sheetName);
        _sheetProtectionPasswords[sheetName] = password ?? string.Empty;
    }

    private readonly Dictionary<string, string> _sheetVisibility = new();

    /// <summary>R465: Return the visibility string for the sheet ("visible" by default).</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — read from table:table/@table:display
    public string GetSheetVisibility(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetVisibility.TryGetValue(sheetName, out var v) ? v : "visible";
    }

    /// <summary>R465: Set the visibility string for the sheet.</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — write to table:table/@table:display
    public void SetSheetVisibility(string sheetName, string visibility)
    {
        RequireSheet(sheetName);
        _sheetVisibility[sheetName] = visibility ?? "visible";
    }

    private readonly Dictionary<string, bool> _sheetRightToLeft = new();
    private readonly Dictionary<string, bool> _sheetShowGrid = new();
    private readonly Dictionary<string, bool> _sheetShowHeaders = new();

    /// <summary>R481: Return right-to-left flag for the named sheet (default false).</summary>
    // TODO: GI-FODS-NET-001 Phase 3c — read from sheet style/@style:writing-mode
    public bool GetSheetRightToLeft(string sheetName)
    {
        RequireSheet(sheetName);
        return _sheetRightToLeft.TryGetValue(sheetName, out var v) && v;
    }

    /// <summary>R482: Return show-grid flag for the named sheet (default true).</summary>
    // GI-FODS-NET-001 Phase 3c — reads ShowGrid from office:settings.
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
    // GI-FODS-NET-001 Phase 3c — reads HasColumnRowHeaders from office:settings.
    // In-memory setter override takes priority; ODF default is true.
    public bool GetSheetShowHeaders(string sheetName)
    {
        RequireSheet(sheetName);
        if (_sheetShowHeaders.TryGetValue(sheetName, out var ov)) return ov;
        var val = GetSheetConfigItem(sheetName, "HasColumnRowHeaders");
        if (val is null) return true;
        return !string.Equals(val, "false", StringComparison.OrdinalIgnoreCase);
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellBorderStyles = new();

    /// <summary>R417: Return the border style for the cell (empty string if none). ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@fo:border. GI-FODS-NET-001 Phase 3b.</remarks>
    public string GetCellBorderStyle(string sheetName, int row, int col)
    {
        if (_cellBorderStyles.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? string.Empty : (FodsStyleResolver.ResolveCellStyle(_doc, cellEl).BorderStyle ?? string.Empty);
    }

    /// <summary>R457: Set the border style string for the cell.</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellBorderStyle(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellBorderStyles[(sheetName, row, col)] = style ?? string.Empty;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontStyles = new();

    /// <summary>R472: Return the font style string for the cell (default "normal").</summary>
    // TODO: GI-FODS-NET-001 Phase 3b — read via FodsStyleResolver from style:text-properties
    public string GetCellFontStyle(string sheetName, int row, int col)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        return _cellFontStyles.TryGetValue((sheetName, row, col), out var v) ? v : "normal";
    }

    /// <summary>R472: Set the font style string for the cell.</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellFontStyle(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellFontStyles[(sheetName, row, col)] = style ?? "normal";
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellHAlign = new();

    /// <summary>R455: Return the horizontal alignment for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.11 style:paragraph-properties/@fo:text-align. GI-FODS-NET-001 Phase 3b.</remarks>
    public string GetCellHorizontalAlignment(string sheetName, int row, int col)
    {
        // In-memory setter override takes priority over parsed ODF value
        if (_cellHAlign.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "start" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).HorizontalAlignment;
    }

    /// <summary>R455: Set the horizontal alignment for the cell (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellHorizontalAlignment(string sheetName, int row, int col, string alignment)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellHAlign[(sheetName, row, col)] = alignment ?? "start";
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellVAlign = new();

    /// <summary>R456: Return the vertical alignment for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:vertical-align. GI-FODS-NET-001 Phase 3b.</remarks>
    public string GetCellVerticalAlignment(string sheetName, int row, int col)
    {
        if (_cellVAlign.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "bottom" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).VerticalAlignment;
    }

    /// <summary>R456: Set the vertical alignment for the cell (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellVerticalAlignment(string sheetName, int row, int col, string alignment)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellVAlign[(sheetName, row, col)] = alignment ?? "bottom";
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellIndentLevel = new();

    /// <summary>R467: Return the indent level for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.11 style:paragraph-properties/@fo:margin-left. GI-FODS-NET-001 Phase 3b.</remarks>
    public int GetCellIndentLevel(string sheetName, int row, int col)
    {
        if (_cellIndentLevel.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? 0 : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).IndentLevel;
    }

    /// <summary>R467: Set the indent level for the cell (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellIndentLevel(string sheetName, int row, int col, int level)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellIndentLevel[(sheetName, row, col)] = level;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellRotationAngle = new();

    /// <summary>R468: Return the rotation angle for the cell. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:rotation-angle. GI-FODS-NET-001 Phase 3b.</remarks>
    public int GetCellRotationAngle(string sheetName, int row, int col)
    {
        if (_cellRotationAngle.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? 0 : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).RotationAngle;
    }

    /// <summary>R468: Set the rotation angle for the cell (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellRotationAngle(string sheetName, int row, int col, int angle)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellRotationAngle[(sheetName, row, col)] = angle;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellMergeInfo = new();
    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellMergeSpan = new();

    /// <summary>R445: Return merge info from ODF span attributes on the cell element.</summary>
    /// <remarks>ODF 1.3 §9.4.5 table:table-cell/@table:number-rows-spanned. GI-FODS-NET-001 Phase 3b.</remarks>
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
    /// <remarks>ODF 1.3 §9.4.5 table:table-cell/@table:number-columns-spanned. GI-FODS-NET-001 Phase 3b.</remarks>
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

    /// <summary>R475: Set the column span for a merged cell (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write to table:table-cell/@table:number-columns-spanned
    public void SetCellMergeSpan(string sheetName, int row, int col, int span)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellMergeSpan[(sheetName, row, col)] = span;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellShrinkToFit = new();

    /// <summary>R450: Return the shrink-to-fit flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:shrink-to-fit. GI-FODS-NET-001 Phase 3b.</remarks>
    public bool GetCellShrinkToFit(string sheetName, int row, int col)
    {
        if (_cellShrinkToFit.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is not null && FodsStyleResolver.ResolveCellStyle(_doc, cellEl).ShrinkToFit;
    }

    /// <summary>R450: Set the shrink-to-fit flag (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellShrinkToFit(string sheetName, int row, int col, bool shrink)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellShrinkToFit[(sheetName, row, col)] = shrink;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellUnderline = new();

    /// <summary>R471: Return the underline style. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.4 style:text-properties/@style:text-underline-style. GI-FODS-NET-001 Phase 3b.</remarks>
    public string GetCellUnderline(string sheetName, int row, int col)
    {
        if (_cellUnderline.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is null ? "none" : FodsStyleResolver.ResolveCellStyle(_doc, cellEl).Underline;
    }

    /// <summary>R471: Set the underline style (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellUnderline(string sheetName, int row, int col, string style)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellUnderline[(sheetName, row, col)] = style ?? "none";
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellStrikethrough = new();

    /// <summary>R408: Return the strikethrough flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.4 style:text-properties/@style:text-line-through-style. GI-FODS-NET-001 Phase 3b.</remarks>
    public bool GetCellStrikethrough(string sheetName, int row, int col)
    {
        if (_cellStrikethrough.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        if (cellEl is null) return false;
        var s = FodsStyleResolver.ResolveCellStyle(_doc, cellEl).Strikethrough;
        return s != "none" && !string.IsNullOrEmpty(s);
    }

    /// <summary>R470: Set the strikethrough flag (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellStrikethrough(string sheetName, int row, int col, bool strikethrough)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellStrikethrough[(sheetName, row, col)] = strikethrough;
    }

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellProtection = new();

    /// <summary>R446: Return the protection flag. ODF style chain read.</summary>
    /// <remarks>ODF 1.3 §15.5 style:table-cell-properties/@style:cell-protect. GI-FODS-NET-001 Phase 3b.</remarks>
    public bool GetCellProtection(string sheetName, int row, int col)
    {
        if (_cellProtection.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElement(sheetName, row, col);
        return cellEl is not null && FodsStyleResolver.ResolveCellStyle(_doc, cellEl).IsProtected;
    }

    /// <summary>R446: Set the protection flag (in-memory; persisted via Phase 3e).</summary>
    // TODO: GI-FODS-NET-001 Phase 3e — write via FodsStyleEditor to ODF XML
    public void SetCellProtection(string sheetName, int row, int col, bool protect)
    {
        RequireSheet(sheetName);
        RequireNonNegativeRow(row);
        RequireNonNegativeCol(col);
        _cellProtection[(sheetName, row, col)] = protect;
    }

    // =========================================================================
    // GI-FODS-NET-001 Phase 3b: Cell element access helpers for FodsStyleResolver
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
        var cells = System.Linq.Enumerable.ToList(rowEl.Elements(NsTable + "table-cell"));
        return col < cells.Count ? cells[col] : null;
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
    private static readonly System.Xml.Linq.XNamespace NsTable =
        System.Xml.Linq.XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
    private static readonly System.Xml.Linq.XNamespace NsFo =
        System.Xml.Linq.XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");

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
        var parts = new System.Collections.Generic.List<string>();
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
    internal static FodsCellStyle? FromElement(System.Xml.Linq.XElement cell)
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
