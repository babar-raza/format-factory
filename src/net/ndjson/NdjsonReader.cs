// FormatFactory.Ndjson — NDJSON Reader
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;

namespace FormatFactory.Ndjson;

/// <summary>
/// Reads NDJSON (Newline-Delimited JSON) from strings, streams, or files.
///
/// Each non-blank line is parsed as a standalone JSON value.
/// Blank lines are skipped. A 64 MB size guard is enforced.
/// Throws <see cref="NdjsonException"/> on invalid JSON lines.
/// </summary>
public static class NdjsonReader
{
    /// <summary>Maximum input size in bytes (64 MB).</summary>
    public const long MaxSize = 64 * 1024 * 1024;

    /// <summary>
    /// Parse NDJSON from a string. Each non-blank line becomes a <see cref="JsonElement"/>.
    /// </summary>
    public static List<JsonElement> ReadRecords(string content)
    {
        ArgumentNullException.ThrowIfNull(content);

        long byteCount = Encoding.UTF8.GetByteCount(content);
        if (byteCount > MaxSize)
            throw new NdjsonException($"Input exceeds maximum allowed size of {MaxSize} bytes (got {byteCount}).");

        return ParseLines(content);
    }

    /// <summary>
    /// Parse NDJSON from a stream. The stream is read to the end as UTF-8.
    /// </summary>
    public static List<JsonElement> ReadRecords(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);

        using var reader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, bufferSize: 8192, leaveOpen: true);
        string content = reader.ReadToEnd();

        long byteCount = Encoding.UTF8.GetByteCount(content);
        if (byteCount > MaxSize)
            throw new NdjsonException($"Input exceeds maximum allowed size of {MaxSize} bytes (got {byteCount}).");

        return ParseLines(content);
    }

    /// <summary>
    /// Parse NDJSON from a file path.
    /// </summary>
    public static List<JsonElement> ReadRecordsFromFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new NdjsonException("path must not be null or empty.");

        var fileInfo = new FileInfo(path);
        if (!fileInfo.Exists)
            throw new NdjsonException($"File not found: {path}");
        if (fileInfo.Length > MaxSize)
            throw new NdjsonException($"File exceeds maximum allowed size of {MaxSize} bytes (got {fileInfo.Length}).");

        string content = File.ReadAllText(path, Encoding.UTF8);
        return ParseLines(content);
    }

    // -------------------------------------------------------------------------
    // Internal
    // -------------------------------------------------------------------------

    private static List<JsonElement> ParseLines(string content)
    {
        var records = new List<JsonElement>();
        using var stringReader = new StringReader(content);

        int lineNumber = 0;
        string? line;
        while ((line = stringReader.ReadLine()) != null)
        {
            lineNumber++;

            // Skip blank lines
            if (string.IsNullOrWhiteSpace(line))
                continue;

            try
            {
                using var doc = JsonDocument.Parse(line);
                // Clone so the element survives after doc disposal
                records.Add(doc.RootElement.Clone());
            }
            catch (JsonException ex)
            {
                throw new NdjsonException($"Invalid JSON on line {lineNumber}: {ex.Message}", ex);
            }
        }

        return records;
    }
}
