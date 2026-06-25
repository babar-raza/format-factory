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
    /// <summary>
    /// Return the number of rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// R96 Train L: row count query for data analysis.
    /// </summary>
    public int GetRowCount()
    {
        var sheets = Sheets;
        return sheets.Count == 0 ? 0 : sheets[0].Rows.Count;
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
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
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
                result.Add(null);
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
            if (vtype != "float" && vtype != "currency" && vtype != "percentage") continue;
            var raw = cell.Attribute(NsOffice + "value")?.Value;
            if (raw is not null && double.TryParse(raw, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var d))
                result.Add(d);
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
    public string? GetCellDataType(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;

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
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "formula")?.Value;
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the first sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if the sheet is empty.
    /// R112: governed /add-dotnet-api.
    /// </summary>
    public (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange()
    {
        var sheet = Sheets.FirstOrDefault();
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the named sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if the sheet is empty.
    /// </summary>
    public (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the given sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if no cells have content.
    /// </summary>
    public static (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange(FodsSheet sheet)
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
        return found ? (minRow, minCol, maxRow, maxCol) : null;
    }

    /// <summary>
    /// Return aggregate statistics for a named sheet: total rows, max column count,
    /// total cell slots, and non-empty cell count.
    /// Returns zeros if the sheet is not found.
    /// R114 Train A: sheet-level aggregate stats for data analysis.
    /// </summary>
    public (int RowCount, int ColCount, int CellCount, int NonEmptyCellCount) GetSheetStats(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return (0, 0, 0, 0);

        int rowCount = sheet.Rows.Count;
        int maxCols = 0;
        int cellCount = 0;
        int nonEmpty = 0;

        foreach (var row in sheet.Rows)
        {
            int c = row.Cells.Count;
            if (c > maxCols) maxCols = c;
            cellCount += c;
            foreach (var cell in row.Cells)
                if (!cell.IsCovered && !string.IsNullOrEmpty(cell.Value))
                    nonEmpty++;
        }

        return (rowCount, maxCols, cellCount, nonEmpty);
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

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
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
            // Always include header row (row 0), include data rows that match
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

        // Skip row 0 (header)
        for (int r = 1; r < sheet.Rows.Count; r++)
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
}
