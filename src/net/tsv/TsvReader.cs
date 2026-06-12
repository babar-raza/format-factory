// FormatFactory.Tsv — TSV Reader
// commercial_product_ready: false

using System.Text;

namespace FormatFactory.Tsv;

/// <summary>
/// Reads tab-separated values from strings, streams, or files.
///
/// Behaviour:
///   - Splits each line by the tab character ('\t').
///   - Strips UTF-8 BOM if present.
///   - Skips empty trailing lines.
///   - Enforces a 64 MB size guard.
///
/// MWP status: minimal viable product.
/// </summary>
public static class TsvReader
{
    private const long MaxSizeBytes = 64L * 1024 * 1024; // 64 MB

    /// <summary>Read rows from a TSV string.</summary>
    public static List<string[]> ReadRows(string content)
    {
        ArgumentNullException.ThrowIfNull(content);

        if (Encoding.UTF8.GetByteCount(content) > MaxSizeBytes)
            throw new TsvException($"Input exceeds the maximum allowed size of {MaxSizeBytes} bytes.");

        // Strip BOM if present
        if (content.Length > 0 && content[0] == '\uFEFF')
            content = content[1..];

        return ParseLines(content);
    }

    /// <summary>Read rows from a stream (UTF-8).</summary>
    public static List<string[]> ReadRows(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);

        if (stream.CanSeek && stream.Length > MaxSizeBytes)
            throw new TsvException($"Stream exceeds the maximum allowed size of {MaxSizeBytes} bytes.");

        using var reader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, leaveOpen: true);
        var content = reader.ReadToEnd();

        if (Encoding.UTF8.GetByteCount(content) > MaxSizeBytes)
            throw new TsvException($"Input exceeds the maximum allowed size of {MaxSizeBytes} bytes.");

        return ParseLines(content);
    }

    /// <summary>Read rows from a file path.</summary>
    public static List<string[]> ReadRowsFromFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new TsvException("path must not be null or empty.");

        if (!File.Exists(path))
            throw new TsvException($"File not found: {path}");

        var info = new FileInfo(path);
        if (info.Length > MaxSizeBytes)
            throw new TsvException($"File exceeds the maximum allowed size of {MaxSizeBytes} bytes.");

        var content = File.ReadAllText(path, Encoding.UTF8);

        // Strip BOM if present
        if (content.Length > 0 && content[0] == '\uFEFF')
            content = content[1..];

        return ParseLines(content);
    }

    // -------------------------------------------------------------------------
    // Internal
    // -------------------------------------------------------------------------

    private static List<string[]> ParseLines(string content)
    {
        // Normalize line endings to LF
        content = content.Replace("\r\n", "\n").Replace("\r", "\n");

        var lines = content.Split('\n');
        var rows = new List<string[]>();

        foreach (var line in lines)
        {
            // Skip empty trailing lines
            if (line.Length == 0)
                continue;

            rows.Add(line.Split('\t'));
        }

        return rows;
    }
}
