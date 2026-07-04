// FormatFactory.Csv — .NET CSV Reader (RFC 4180)
// Sprint: MAINSTREAM-MEGATRAIN-20260610
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Csv;

/// <summary>
/// RFC 4180 compliant CSV reader.
/// Supports quoted fields, embedded commas/newlines/quotes, BOM stripping.
/// </summary>
public class CsvReader
{
    private const long MaxSizeBytes = 64 * 1024 * 1024; // 64 MB

    /// <summary>
    /// Parse CSV content into rows of string fields, OR read from a file path.
    /// Auto-detects: if the string contains no newlines and the file exists on disk, reads from file.
    /// Otherwise, parses the string as CSV content directly.
    /// This allows both static usage (CsvReader.ReadRows(csvContent)) and
    /// instance usage (new CsvReader().ReadRows(filePath)) with the same method.
    /// </summary>
    public static List<string[]> ReadRows(string content)
    {
        if (content is null) throw new CsvReaderException("content must not be null.");
        if (content.Length == 0) return new List<string[]>();

        // Auto-detect file path: no newlines + file exists on disk → read from file, strip header
        if (content.IndexOf('\n') < 0 && content.IndexOf('\r') < 0 && File.Exists(content))
        {
            var all = ReadRowsFromFile(content);
            return all.Count > 0 ? all.GetRange(1, all.Count - 1) : all;
        }

        // Strip BOM
        if (content[0] == '\uFEFF')
            content = content[1..];

        return ParseCsv(content);
    }

    /// <summary>Parse CSV from a stream.</summary>
    public static List<string[]> ReadRows(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);
        using var reader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        var content = reader.ReadToEnd();
        if (content.Length > MaxSizeBytes)
            throw new CsvReaderException($"Input exceeds maximum size of {MaxSizeBytes} bytes.");
        return ReadRows(content);
    }

    /// <summary>Parse CSV from a stream, stripping the header row.</summary>
    public static List<string[]> ReadRowsFromStream(Stream stream)
    {
        var all = ReadRows(stream);
        return all.Count > 0 ? all.GetRange(1, all.Count - 1) : all;
    }

    /// <summary>Returns the header row from a CSV file as a list of field names.</summary>
    public static List<string> GetHeaders(string path)
    {
        var rows = ReadRowsFromFile(path);
        if (rows.Count == 0) return new List<string>();
        return rows[0].ToList();
    }

    /// <summary>Parse CSV from a file path.</summary>
    public static List<string[]> ReadRowsFromFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new CsvReaderException("path must not be null or empty.");

        var info = new FileInfo(path);
        if (info.Length > MaxSizeBytes)
            throw new CsvReaderException($"File exceeds maximum size of {MaxSizeBytes} bytes.");

        var content = File.ReadAllText(path, Encoding.UTF8);
        return ReadRows(content);
    }

    /// <summary>Instance method: parse CSV content into a CsvDocument (treats first row as headers).</summary>
    public CsvDocument Deserialize(string content) => CsvDocument.Load(content);

    private static List<string[]> ParseCsv(string content)
    {
        var rows = new List<string[]>();
        var fields = new List<string>();
        var field = new StringBuilder();
        int i = 0;
        int len = content.Length;

        while (i < len)
        {
            if (content[i] == '"')
            {
                // Quoted field
                i++; // skip opening quote
                while (i < len)
                {
                    if (content[i] == '"')
                    {
                        if (i + 1 < len && content[i + 1] == '"')
                        {
                            field.Append('"');
                            i += 2;
                        }
                        else
                        {
                            i++; // skip closing quote
                            break;
                        }
                    }
                    else
                    {
                        field.Append(content[i]);
                        i++;
                    }
                }
                // Skip to comma or end of line
                while (i < len && content[i] != ',' && content[i] != '\n' && content[i] != '\r')
                    i++;
            }
            else
            {
                // Unquoted field
                while (i < len && content[i] != ',' && content[i] != '\n' && content[i] != '\r')
                {
                    field.Append(content[i]);
                    i++;
                }
            }

            if (i < len && content[i] == ',')
            {
                fields.Add(field.ToString());
                field.Clear();
                i++;
            }
            else
            {
                // End of row
                fields.Add(field.ToString());
                field.Clear();
                rows.Add(fields.ToArray());
                fields.Clear();

                // Handle \r\n or \n or \r
                if (i < len && content[i] == '\r')
                    i++;
                if (i < len && content[i] == '\n')
                    i++;
            }
        }

        // Remove trailing empty row (common with trailing newline)
        if (rows.Count > 0 && rows[^1].Length == 1 && rows[^1][0] == "")
            rows.RemoveAt(rows.Count - 1);

        return rows;
    }
}

/// <summary>Thrown by <see cref="CsvReader"/> when input cannot be parsed.</summary>
public sealed class CsvReaderException : ArgumentOutOfRangeException
{
    public CsvReaderException(string message) : base(null, message) { }
    public CsvReaderException(string message, Exception inner) : base(message, inner) { }
}
