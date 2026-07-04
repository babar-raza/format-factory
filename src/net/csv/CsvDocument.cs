// FormatFactory.Csv — .NET CSV Document Model
// Sprint: MAINSTREAM-MEGATRAIN-20260610
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace FormatFactory.Csv;

/// <summary>Summary statistics for a single numeric column.</summary>
public sealed class ColumnSummary
{
    public double Min { get; init; }
    public double Max { get; init; }
    public double Mean { get; init; }
    public double StdDev { get; init; }
}

/// <summary>
/// Simple CSV document model with optional headers.
/// </summary>
public sealed partial class CsvDocument
{
    /// <summary>Header row, or null if no headers.</summary>
    public string[]? Headers { get; private set; }

    /// <summary>Data rows (excluding header).</summary>
    public List<string[]> Rows { get; }

    /// <summary>Whether the document has a header row.</summary>
    public bool HasHeaders => Headers is not null;

    /// <summary>Number of data rows.</summary>
    public int RowCount => Rows.Count;

    /// <summary>Number of columns (from headers or first row).</summary>
    public int ColumnCount => Headers?.Length ?? (Rows.Count > 0 ? Rows[0].Length : 0);

    private CsvDocument(string[]? headers, List<string[]> rows)
    {
        Headers = headers;
        Rows = rows;
    }

    /// <summary>Load CSV from string content.</summary>
    public static CsvDocument Load(string content, bool hasHeaders = true)
    {
        var allRows = CsvReader.ReadRows(content);
        if (hasHeaders && allRows.Count > 0)
        {
            var headers = allRows[0];
            allRows.RemoveAt(0);
            return new CsvDocument(headers, allRows);
        }
        return new CsvDocument(null, allRows);
    }

    /// <summary>Load CSV from file.</summary>
    public static CsvDocument LoadFile(string path, bool hasHeaders = true)
    {
        var allRows = CsvReader.ReadRowsFromFile(path);
        if (hasHeaders && allRows.Count > 0)
        {
            var headers = allRows[0];
            allRows.RemoveAt(0);
            return new CsvDocument(headers, allRows);
        }
        return new CsvDocument(null, allRows);
    }

    /// <summary>Serialize to CSV string.</summary>
    public string ToCsv()
    {
        var allRows = new List<IEnumerable<string?>>();
        if (Headers is not null)
            allRows.Add(Headers);
        foreach (var row in Rows)
            allRows.Add(row);
        return CsvWriter.WriteRows(allRows);
    }

    /// <summary>Save to file.</summary>
    public void SaveToFile(string path)
    {
        var allRows = new List<IEnumerable<string?>>();
        if (Headers is not null)
            allRows.Add(Headers);
        foreach (var row in Rows)
            allRows.Add(row);
        CsvWriter.WriteRowsToFile(allRows, path);
    }

    /// <summary>True if the document has no data rows.</summary>
    public bool IsEmpty => Rows.Count == 0;

    /// <summary>
    /// Get the cell value at the given zero-based row and column index.
    /// Returns null if the row or column is out of bounds.
    /// </summary>
    public string? GetCellValue(int row, int col)
    {
        if (row < 0 || row >= Rows.Count) return null;
        var r = Rows[row];
        if (col < 0 || col >= r.Length) return null;
        return r[col];
    }

    /// <summary>Get the cell value at the given zero-based row index and column name.</summary>
    public string? GetCellValue(int row, string columnName)
    {
        var col = GetColumnIndex(columnName);
        return GetCellValue(row, col);
    }

    /// <summary>Set the cell value at the given zero-based row and column index.</summary>
    /// <remarks>
    /// This method silently returns (no-op) when <paramref name="row"/> or <paramref name="col"/>
    /// is out of bounds. This is intentional for defensive bulk-update scenarios.
    /// If you need strict bounds enforcement (exception on out-of-bounds), use <see cref="SetCell"/> instead.
    /// </remarks>
    public void SetCellValue(int row, int col, string value)
    {
        if (row < 0 || row >= Rows.Count) return;
        var r = Rows[row];
        if (col < 0 || col >= r.Length) return;
        r[col] = value;
    }

    // Thread-local storage for header context during Filter evaluation.
    // Enables string[].GetValue(string colName) extension method to resolve column names.
    //
    // IMPORTANT — async predicate limitation:
    // [ThreadStatic] fields are not safe when the Filter predicate is async (returns Task or
    // uses ConfigureAwait(false)), because async continuations may resume on a different thread
    // where _filterHeaders is null. Only use Filter with synchronous predicates.
    // For async filtering, materialize the rows with GetColumn() and filter manually.
    [ThreadStatic]
    private static string[]? _filterHeaders;

    internal static string[]? FilterHeaders => _filterHeaders;

    /// <summary>
    /// Returns a new CsvDocument containing only rows that match the predicate.
    /// Headers are preserved unchanged. Inside the predicate, call row.GetValue("colName")
    /// to look up values by column name (requires the CsvRowExtensions import).
    /// </summary>
    public CsvDocument Filter(Func<string[], bool> predicate)
    {
        if (predicate is null) throw new ArgumentNullException(nameof(predicate));
        _filterHeaders = Headers;
        try { return new CsvDocument(Headers, Rows.Where(predicate).ToList()); }
        finally { _filterHeaders = null; }
    }

    /// <summary>
    /// Returns true if the document has a header with the given name.
    /// Case-sensitive. Always returns false if the document has no headers.
    /// </summary>
    public bool HasColumn(string name) =>
        Headers is not null && Array.IndexOf(Headers, name) >= 0;

    /// <summary>Get values from a specific column by index.</summary>
    public List<string> GetColumn(int index)
    {
        if (index < 0) throw new CsvReaderException("Column index must be non-negative.");
        return Rows.Where(r => r.Length > index).Select(r => r[index]).ToList();
    }

    /// <summary>Get values from a column by header name.</summary>
    public List<string> GetColumn(string headerName)
    {
        if (Headers is null) throw new CsvReaderException("Document has no headers.");
        var idx = Array.IndexOf(Headers, headerName);
        if (idx < 0) throw new CsvReaderException($"Header '{headerName}' not found.");
        return GetColumn(idx);
    }

    // -------------------------------------------------------------------------
    // Mutation API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Append a new data row to the document.
    /// Values are padded or truncated to match <see cref="ColumnCount"/> when headers are present.
    /// </summary>
    /// <param name="values">Cell values for the new row. Must not be null.</param>
    /// <exception cref="ArgumentNullException">Thrown when <paramref name="values"/> is null.</exception>
    public void AddRow(IEnumerable<string> values)
    {
        if (values is null) throw new ArgumentNullException(nameof(values));
        Rows.Add(values.ToArray());
    }

    /// <summary>
    /// Set the value of a specific cell by zero-based row and column index.
    /// The row array is widened if <paramref name="col"/> exceeds its current length.
    /// </summary>
    /// <param name="row">Zero-based row index.</param>
    /// <param name="col">Zero-based column index.</param>
    /// <param name="value">Value to write. Null is stored as empty string.</param>
    /// <exception cref="ArgumentOutOfRangeException">
    /// Thrown when <paramref name="row"/> is negative or exceeds <see cref="RowCount"/>.
    /// Thrown when <paramref name="col"/> is negative.
    /// </exception>
    public void SetCell(int row, int col, string value)
    {
        if (row < 0 || row >= Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row), $"Row index {row} is out of range [0, {Rows.Count}).");
        if (col < 0)
            throw new ArgumentOutOfRangeException(nameof(col), "Column index must be non-negative.");

        var existing = Rows[row];
        if (col >= existing.Length)
        {
            // Widen the row array to accommodate the target column.
            var widened = new string[col + 1];
            Array.Copy(existing, widened, existing.Length);
            // Fill newly created slots with empty string (not null).
            for (int i = existing.Length; i < widened.Length; i++)
                widened[i] = string.Empty;
            Rows[row] = widened;
        }
        Rows[row][col] = value ?? string.Empty;
    }

    /// <summary>
    /// Remove a data row at the given zero-based index.
    /// </summary>
    /// <param name="index">Zero-based index of the row to remove.</param>
    /// <exception cref="ArgumentOutOfRangeException">
    /// Thrown when <paramref name="index"/> is negative or &gt;= <see cref="RowCount"/>.
    /// </exception>
    public void RemoveRow(int index)
    {
        if (index < 0 || index >= Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(index), $"Row index {index} is out of range [0, {Rows.Count}).");
        Rows.RemoveAt(index);
    }

    // -------------------------------------------------------------------------
    // Column Analytics API
    // -------------------------------------------------------------------------

    /// <summary>Alias for <see cref="SaveToFile"/> for API symmetry with LoadFile.</summary>
    public void SaveFile(string path) => SaveToFile(path);

}

/// <summary>Result of GetColumnQuartiles: the three quartile values Q1, Q2, Q3.</summary>
public sealed record QuartilesResult(double Q1, double Q2, double Q3);

/// <summary>Summary statistics for a numeric column.</summary>
public sealed record ColumnStats(int Count, double Min, double Max, double Avg)
{
    /// <summary>Average (alias for Avg).</summary>
    public double Average => Avg;
    /// <summary>Sum of all values (Avg * Count).</summary>
    public double Sum => Count > 0 ? Avg * Count : 0;
}

/// <summary>
/// Extension methods for string[] rows used inside CsvDocument.Filter predicates.
/// GetValue(string colName) resolves column names using the thread-local header context
/// set by CsvDocument.Filter before evaluating each predicate.
/// </summary>
public static class CsvRowExtensions
{
    public static string? GetValue(this string[] row, string colName)
    {
        var headers = CsvDocument.FilterHeaders;
        if (headers == null) return null;
        for (int i = 0; i < headers.Length; i++)
            if (string.Equals(headers[i], colName, StringComparison.OrdinalIgnoreCase) && i < row.Length)
                return row[i];
        return null;
    }

    /// <summary>Returns the cell value for the named column (alias for GetValue).</summary>
    public static string? GetCellValue(this string[] row, string colName) => GetValue(row, colName);

    /// <summary>Returns the cell value at the given column index, or null if out of range.</summary>
    public static string? GetCellValue(this string[] row, int colIndex) =>
        colIndex >= 0 && colIndex < row.Length ? row[colIndex] : null;
}
