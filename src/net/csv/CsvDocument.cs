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
}
