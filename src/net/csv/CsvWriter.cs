// FormatFactory.Csv — Standalone .NET CSV Target Writer Library
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
// target_ff_library: FormatFactory.Csv.CsvWriter
// dogfood_status: IMPLEMENTED (FODS → CSV)
// commercial_product_ready: false — G11-G not approved

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Csv;

/// <summary>
/// Standalone Format Factory target writer for CSV (comma-separated values).
///
/// Scope:
///   - Serializes rows of string fields to RFC 4180 compatible CSV.
///   - Quotes fields containing comma, double-quote, CR, or LF.
///   - Doubles internal double-quotes.
///   - Outputs UTF-8 without BOM, LF line endings.
///   - Supports both in-memory (WriteRows) and file (WriteRowsToFile) output.
///
/// Usage:
///   var csv = CsvWriter.WriteRows(rows);
///   CsvWriter.WriteRowsToFile(rows, "/path/output.csv");
///
/// MWP status: minimal viable product — production hardening is future work.
/// commercial_product_ready: false
/// </summary>
public class CsvWriter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Serialize <paramref name="rows"/> and write to <paramref name="path"/> (static overload).
    /// Callable as <c>CsvWriter.WriteRows(rows, path)</c> or on an instance (static-on-instance).
    /// </summary>
    public static void WriteRows(IEnumerable<IEnumerable<string?>> rows, string path) => WriteRowsToFile(rows, path);

    /// <summary>Instance method: serialize a CsvDocument to a CSV string.</summary>
    public string Serialize(CsvDocument doc)
    {
        var allRows = new List<IEnumerable<string?>>();
        if (doc.Headers != null) allRows.Add(doc.Headers);
        allRows.AddRange(doc.Rows);
        return WriteRows(allRows);
    }

    /// <summary>Serialize <paramref name="rows"/> with the given header row prepended, to a CSV string.</summary>
    public static string WriteRows(IEnumerable<IEnumerable<string?>> rows, string[] headers)
    {
        var all = new List<IEnumerable<string?>> { headers };
        all.AddRange(rows);
        return WriteRows(all);
    }

    /// <summary>
    /// Serialize <paramref name="rows"/> to a CSV string.
    /// </summary>
    /// <param name="rows">Rows of fields. Null fields are treated as empty strings.</param>
    /// <returns>CSV content as a string with LF line endings.</returns>
    public static string WriteRows(IEnumerable<IEnumerable<string?>> rows)
    {
        ArgumentNullException.ThrowIfNull(rows);
        var sb = new StringBuilder();
        foreach (var row in rows)
        {
            var fields = new List<string>();
            foreach (var field in row)
                fields.Add(EscapeField(field));
            sb.Append(string.Join(",", fields));
            sb.Append('\n');
        }
        return sb.ToString();
    }

    /// <summary>
    /// Serialize <paramref name="rows"/> and write to <paramref name="path"/>.
    /// Creates parent directories as needed. UTF-8, no BOM.
    /// </summary>
    public static void WriteRowsToFile(IEnumerable<IEnumerable<string?>> rows, string path)
    {
        ArgumentNullException.ThrowIfNull(rows);
        if (string.IsNullOrWhiteSpace(path))
            throw new CsvWriterException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var content = WriteRows(rows);
        // Normalize any \r\n to \n
        content = content.Replace("\r\n", "\n");
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }

    /// <summary>Serialize dictionary rows using headers as column order, returns CSV string.</summary>
    public static string WriteRows(List<Dictionary<string, string>> rows, List<string> headers)
    {
        ArgumentNullException.ThrowIfNull(rows);
        ArgumentNullException.ThrowIfNull(headers);
        var all = new List<IEnumerable<string?>> { headers };
        all.AddRange(rows.Select(r => (IEnumerable<string?>)headers.Select(h => r.TryGetValue(h, out var v) ? v : "")));
        return WriteRows(all);
    }

    /// <summary>Serialize dictionary rows using headers as column order, write to file.</summary>
    public static void WriteRowsToFile(List<Dictionary<string, string>> rows, List<string> headers, string path)
    {
        ArgumentNullException.ThrowIfNull(rows);
        ArgumentNullException.ThrowIfNull(headers);
        var all = new List<IEnumerable<string?>> { headers };
        all.AddRange(rows.Select(r => (IEnumerable<string?>)headers.Select(h => r.TryGetValue(h, out var v) ? v : "")));
        WriteRowsToFile(all, path);
    }

    /// <summary>Write rows (with optional header) to a stream as CSV (UTF-8, no BOM).</summary>
    public static void WriteToStream(IEnumerable<IEnumerable<string?>> rows, Stream stream, string[]? headers = null)
    {
        ArgumentNullException.ThrowIfNull(rows);
        ArgumentNullException.ThrowIfNull(stream);
        IEnumerable<IEnumerable<string?>> all = headers != null
            ? new List<IEnumerable<string?>> { headers }.Concat(rows)
            : rows;
        var bytes = System.Text.Encoding.UTF8.GetBytes(WriteRows(all));
        stream.Write(bytes, 0, bytes.Length);
    }

    /// <summary>Write string[][] rows (with header array) to a file.</summary>
    public static void WriteRowsToFile(IEnumerable<string[]> rows, string path, string[] headers)
    {
        var all = new List<IEnumerable<string?>> { headers };
        all.AddRange(rows);
        WriteRowsToFile(all, path);
    }

    /// <summary>Write string[][] rows (with header array) to a stream.</summary>
    public static void WriteToStream(IEnumerable<string[]> rows, Stream stream, string[] headers)
    {
        var all = new List<IEnumerable<string?>> { headers };
        all.AddRange(rows);
        WriteToStream(all, stream);
    }

    /// <summary>Write a CsvDocument to a stream as CSV (UTF-8, no BOM).</summary>
    public static void WriteToStream(CsvDocument doc, Stream stream)
    {
        ArgumentNullException.ThrowIfNull(doc);
        ArgumentNullException.ThrowIfNull(stream);
        var bytes = System.Text.Encoding.UTF8.GetBytes(doc.ToCsv());
        stream.Write(bytes, 0, bytes.Length);
    }

    // -------------------------------------------------------------------------
    // Field escaping — RFC 4180 compatible
    // -------------------------------------------------------------------------

    /// <summary>
    /// Escape a single CSV field:
    /// - null/empty → empty string (no quotes)
    /// - Contains comma, double-quote, CR, or LF → wrap in double-quotes
    /// - Embedded double-quotes → doubled ("")
    /// </summary>
    public static string EscapeField(string? value)
    {
        if (value is null || value.Length == 0) return string.Empty;

        bool needsQuoting = value.IndexOf(',') >= 0 ||
                            value.IndexOf('"') >= 0 ||
                            value.IndexOf('\n') >= 0 ||
                            value.IndexOf('\r') >= 0;

        if (!needsQuoting) return value;
        return "\"" + value.Replace("\"", "\"\"") + "\"";
    }
}

/// <summary>Thrown by <see cref="CsvWriter"/> when output cannot be written.</summary>
public sealed class CsvWriterException : Exception
{
    public CsvWriterException(string message) : base(message) { }
    public CsvWriterException(string message, Exception inner) : base(message, inner) { }
}
