// FormatFactory.Ndjson — NDJSON Writer
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;

namespace FormatFactory.Ndjson;

/// <summary>
/// Writes objects as NDJSON (Newline-Delimited JSON).
///
/// Each record is serialized as a single-line JSON object followed by LF (\n).
/// Output is UTF-8 with no BOM and LF line endings.
/// </summary>
public static class NdjsonWriter
{
    private static readonly JsonSerializerOptions s_options = new()
    {
        // Ensure single-line output (no indentation)
        WriteIndented = false,
    };

    /// <summary>
    /// Serialize each record as a JSON line and return the complete NDJSON string.
    /// </summary>
    public static string WriteRecords(IEnumerable<object> records)
    {
        ArgumentNullException.ThrowIfNull(records);

        var sb = new StringBuilder();
        foreach (var record in records)
        {
            string json = JsonSerializer.Serialize(record, record?.GetType() ?? typeof(object), s_options);
            sb.Append(json);
            sb.Append('\n');
        }
        return sb.ToString();
    }

    /// <summary>
    /// Serialize each record as a JSON line and write to a file.
    /// UTF-8, no BOM, LF line endings.
    /// </summary>
    public static void WriteRecordsToFile(IEnumerable<object> records, string path)
    {
        ArgumentNullException.ThrowIfNull(records);
        if (string.IsNullOrWhiteSpace(path))
            throw new NdjsonException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        string content = WriteRecords(records);
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }
}
