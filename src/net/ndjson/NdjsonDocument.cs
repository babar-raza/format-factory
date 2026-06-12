// FormatFactory.Ndjson — NDJSON Document Model
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;

namespace FormatFactory.Ndjson;

/// <summary>
/// A simple in-memory NDJSON document that holds parsed JSON records.
/// </summary>
public sealed class NdjsonDocument
{
    /// <summary>The parsed JSON records.</summary>
    public List<JsonElement> Records { get; }

    /// <summary>Number of records in the document.</summary>
    public int Count => Records.Count;

    /// <summary>
    /// Creates a new <see cref="NdjsonDocument"/> with the given records.
    /// </summary>
    public NdjsonDocument(List<JsonElement> records)
    {
        Records = records ?? throw new ArgumentNullException(nameof(records));
    }

    /// <summary>Load from an NDJSON string.</summary>
    public static NdjsonDocument Load(string content)
    {
        var records = NdjsonReader.ReadRecords(content);
        return new NdjsonDocument(records);
    }

    /// <summary>Load from a stream.</summary>
    public static NdjsonDocument Load(Stream stream)
    {
        var records = NdjsonReader.ReadRecords(stream);
        return new NdjsonDocument(records);
    }

    /// <summary>Load from a file path.</summary>
    public static NdjsonDocument LoadFile(string path)
    {
        var records = NdjsonReader.ReadRecordsFromFile(path);
        return new NdjsonDocument(records);
    }

    /// <summary>
    /// Serialize all records back to an NDJSON string.
    /// Each record is serialized as compact JSON followed by LF.
    /// </summary>
    public string ToNdjson()
    {
        var sb = new StringBuilder();
        foreach (var record in Records)
        {
            sb.Append(record.GetRawText());
            sb.Append('\n');
        }
        return sb.ToString();
    }

    /// <summary>
    /// Save the document to a file. UTF-8, no BOM, LF line endings.
    /// </summary>
    public void SaveToFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new NdjsonException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        string content = ToNdjson();
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }
}
