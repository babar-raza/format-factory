// FormatFactory.Ndjson — NDJSON Document Model
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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

    /// <summary>
    /// Load from an NDJSON content string (one JSON object per line).
    /// This is the preferred method when loading from in-memory content.
    /// For file loading, use <see cref="LoadFile(string)"/>.
    /// </summary>
    /// <param name="ndjsonContent">NDJSON content string.</param>
    public static NdjsonDocument LoadFromContent(string ndjsonContent)
    {
        var records = NdjsonReader.ReadRecords(ndjsonContent);
        return new NdjsonDocument(records);
    }

    /// <summary>
    /// Load from an NDJSON string.
    /// </summary>
    /// <remarks>
    /// Prefer <see cref="LoadFromContent(string)"/> which makes the intent explicit.
    /// This overload is retained for backward compatibility.
    /// </remarks>
    public static NdjsonDocument Load(string content)
        => LoadFromContent(content);

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
    /// Returns all unique JSON property keys found across all object records.
    /// Only keys at the top level of each record are included.
    /// Non-object records (arrays, primitives) contribute no keys.
    /// </summary>
    public IReadOnlyList<string> GetAllKeys()
    {
        var keys = new SortedSet<string>(StringComparer.Ordinal);
        foreach (var rec in Records)
        {
            if (rec.ValueKind == JsonValueKind.Object)
                foreach (var prop in rec.EnumerateObject())
                    keys.Add(prop.Name);
        }
        return keys.ToList();
    }

    /// <summary>
    /// Returns a new NdjsonDocument containing only records that match the predicate.
    /// </summary>
    public NdjsonDocument Filter(Func<JsonElement, bool> predicate)
    {
        if (predicate is null) throw new ArgumentNullException(nameof(predicate));
        return new NdjsonDocument(Records.Where(predicate).ToList());
    }

    /// <summary>
    /// Returns all string representations of the value at the given field key
    /// for every object record that contains the key.
    /// Records missing the key or non-object records are skipped.
    /// </summary>
    public IReadOnlyList<string> GetFieldValues(string key)
    {
        if (key is null) throw new ArgumentNullException(nameof(key));
        var result = new List<string>();
        foreach (var rec in Records)
        {
            if (rec.ValueKind == JsonValueKind.Object
                && rec.TryGetProperty(key, out var val))
                result.Add(val.ToString());
        }
        return result;
    }

    /// <summary>
    /// Returns true if all object records in the document share exactly the same set of top-level keys.
    /// An empty document returns true. Non-object records are ignored.
    /// </summary>
    public bool IsUniformSchema()
    {
        IReadOnlyCollection<string>? referenceKeys = null;
        foreach (var rec in Records)
        {
            if (rec.ValueKind != JsonValueKind.Object) continue;
            var keys = rec.EnumerateObject().Select(p => p.Name).OrderBy(k => k).ToList();
            if (referenceKeys is null)
                referenceKeys = keys;
            else if (!keys.SequenceEqual(referenceKeys))
                return false;
        }
        return true;
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
