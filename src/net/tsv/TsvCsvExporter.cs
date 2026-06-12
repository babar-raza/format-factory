// FormatFactory.Tsv — Export TSV to CSV (RFC 4180)
// commercial_product_ready: false

using System.Text;

namespace FormatFactory.Tsv;

/// <summary>
/// Exports a <see cref="TsvDocument"/> to CSV format using RFC 4180 quoting rules.
///
/// Quoting rules:
///   - Fields containing comma, double-quote, CR, or LF are wrapped in double-quotes.
///   - Embedded double-quotes are doubled ("").
///   - LF line endings, UTF-8 output.
/// </summary>
public static class TsvCsvExporter
{
    /// <summary>Export a TsvDocument to a CSV string.</summary>
    public static string Export(TsvDocument doc)
    {
        ArgumentNullException.ThrowIfNull(doc);

        var sb = new StringBuilder();

        if (doc.HasHeaders && doc.Headers is not null)
        {
            sb.Append(FormatCsvRow(doc.Headers));
            sb.Append('\n');
        }

        foreach (var row in doc.Rows)
        {
            sb.Append(FormatCsvRow(row));
            sb.Append('\n');
        }

        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // Internal — RFC 4180 field escaping
    // -------------------------------------------------------------------------

    private static string FormatCsvRow(string[] fields)
    {
        var escaped = new string[fields.Length];
        for (int i = 0; i < fields.Length; i++)
            escaped[i] = EscapeCsvField(fields[i]);
        return string.Join(",", escaped);
    }

    private static string EscapeCsvField(string? value)
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
