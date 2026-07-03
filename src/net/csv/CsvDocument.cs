// FormatFactory.Csv — .NET CSV Document Model
// Sprint: MAINSTREAM-MEGATRAIN-20260610
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace FormatFactory.Csv;

/// <summary>
/// Simple CSV document model with optional headers.
/// </summary>
public sealed class CsvDocument
{
    /// <summary>Header row, or null if no headers.</summary>
    public string[]? Headers { get; }

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

    /// <summary>
    /// Returns a new CsvDocument containing only rows that match the predicate.
    /// Headers are preserved unchanged.
    /// </summary>
    public CsvDocument Filter(Func<string[], bool> predicate)
    {
        if (predicate is null) throw new ArgumentNullException(nameof(predicate));
        return new CsvDocument(Headers, Rows.Where(predicate).ToList());
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

    private static IEnumerable<double> ParseNumericColumn(List<string> values) =>
        values
            .Where(v => double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out _))
            .Select(v => double.Parse(v, System.Globalization.CultureInfo.InvariantCulture));

    /// <summary>Returns the minimum numeric value in the specified column.</summary>
    public double GetColumnMin(int index) => ParseNumericColumn(GetColumn(index)).Min();

    /// <summary>Returns the maximum numeric value in the specified column.</summary>
    public double GetColumnMax(int index) => ParseNumericColumn(GetColumn(index)).Max();

    /// <summary>Returns the sum of numeric values in the specified column (by index).</summary>
    public double GetColumnSum(int index) => ParseNumericColumn(GetColumn(index)).Sum();

    /// <summary>Returns the sum of numeric values in the specified column (by header name).</summary>
    public double GetColumnSum(string headerName) => ParseNumericColumn(GetColumn(headerName)).Sum();

    /// <summary>Returns the arithmetic mean of numeric values in the specified column.</summary>
    public double GetColumnMean(int index) => ParseNumericColumn(GetColumn(index)).Average();

    /// <summary>Returns the range (max minus min) of numeric values in the specified column (by index).</summary>
    public double GetColumnRange(int index) => GetColumnMax(index) - GetColumnMin(index);

    /// <summary>Returns the range (max minus min) of numeric values in the specified column (by header name).</summary>
    public double GetColumnRange(string headerName) => GetColumnMax(headerName) - GetColumnMin(headerName);

    /// <summary>Returns the minimum numeric value in the specified column (by header name).</summary>
    public double GetColumnMin(string headerName) => ParseNumericColumn(GetColumn(headerName)).Min();

    /// <summary>Returns the maximum numeric value in the specified column (by header name).</summary>
    public double GetColumnMax(string headerName) => ParseNumericColumn(GetColumn(headerName)).Max();

    /// <summary>Returns the interquartile range (Q3 - Q1) of numeric values in the specified column.</summary>
    public double GetColumnInterquartileRange(int index)
    {
        var sorted = ParseNumericColumn(GetColumn(index)).OrderBy(x => x).ToArray();
        if (sorted.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        int n = sorted.Length;
        int q1Idx = (int)Math.Round((n - 1) * 0.25, MidpointRounding.ToEven);
        int q3Idx = (int)Math.Round((n - 1) * 0.75, MidpointRounding.ToEven);
        return sorted[q3Idx] - sorted[q1Idx];
    }
}
