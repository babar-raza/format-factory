// FormatFactory.Ndjson — NDJSON to CSV Exporter
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace FormatFactory.Ndjson;

/// <summary>
/// Exports an <see cref="NdjsonDocument"/> to CSV format.
///
/// Collects all unique property names across all records to form headers,
/// then writes each record as a CSV row. Missing keys produce empty fields.
/// Fields are escaped per RFC 4180 (comma, quote, newline → quoted).
/// </summary>
public static class NdjsonCsvExporter
{
    /// <summary>
    /// Export the document to a CSV string.
    /// </summary>
    public static string Export(NdjsonDocument doc)
    {
        ArgumentNullException.ThrowIfNull(doc);

        if (doc.Count == 0)
            return string.Empty;

        // Collect all unique keys in order of first appearance
        var headers = new List<string>();
        var headerSet = new HashSet<string>();
        foreach (var record in doc.Records)
        {
            if (record.ValueKind != JsonValueKind.Object)
                continue;

            foreach (var prop in record.EnumerateObject())
            {
                if (headerSet.Add(prop.Name))
                    headers.Add(prop.Name);
            }
        }

        if (headers.Count == 0)
            return string.Empty;

        var sb = new StringBuilder();

        // Header row
        sb.Append(string.Join(",", headers.Select(EscapeCsvField)));
        sb.Append('\n');

        // Data rows
        foreach (var record in doc.Records)
        {
            var fields = new List<string>();
            foreach (var header in headers)
            {
                string value = string.Empty;
                if (record.ValueKind == JsonValueKind.Object && record.TryGetProperty(header, out var prop))
                {
                    value = prop.ValueKind switch
                    {
                        JsonValueKind.String => prop.GetString() ?? string.Empty,
                        JsonValueKind.Null => string.Empty,
                        _ => prop.GetRawText(),
                    };
                }
                fields.Add(EscapeCsvField(value));
            }
            sb.Append(string.Join(",", fields));
            sb.Append('\n');
        }

        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // CSV field escaping (RFC 4180)
    // -------------------------------------------------------------------------

    private static string EscapeCsvField(string value)
    {
        if (value.Length == 0) return string.Empty;

        bool needsQuoting = value.IndexOf(',') >= 0 ||
                            value.IndexOf('"') >= 0 ||
                            value.IndexOf('\n') >= 0 ||
                            value.IndexOf('\r') >= 0;

        if (!needsQuoting) return value;
        return "\"" + value.Replace("\"", "\"\"") + "\"";
    }
}
