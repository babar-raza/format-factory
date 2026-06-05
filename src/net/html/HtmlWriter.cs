// FormatFactory.Html — Standalone .NET HTML Target Writer Library
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
// target_ff_library: FormatFactory.Html.HtmlWriter
// dogfood_status: IMPLEMENTED (FODS → HTML)
// commercial_product_ready: false — G11-G not approved

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;

namespace FormatFactory.Html;

/// <summary>
/// Standalone Format Factory target writer for HTML table output.
///
/// Scope:
///   - Serializes rows of string fields to a minimal valid HTML5 table.
///   - Escapes HTML special characters (&amp; &lt; &gt; &quot; &#39;).
///   - Supports optional header row (first row rendered as &lt;th&gt; elements).
///   - Outputs UTF-8 without BOM, LF line endings.
///   - Supports both in-memory (WriteTable) and file (WriteTableToFile) output.
///
/// MWP status: minimal viable product — production hardening is future work.
/// commercial_product_ready: false
/// </summary>
public static class HtmlWriter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Serialize <paramref name="rows"/> to an HTML table string.
    /// </summary>
    /// <param name="rows">Rows of cell values. Null values become empty cells.</param>
    /// <param name="firstRowIsHeader">If true, the first row uses &lt;th&gt; elements.</param>
    /// <returns>HTML fragment: a single &lt;table&gt; element.</returns>
    public static string WriteTable(
        IEnumerable<IEnumerable<string?>> rows,
        bool firstRowIsHeader = false)
    {
        ArgumentNullException.ThrowIfNull(rows);
        var sb = new StringBuilder();
        sb.AppendLine("<table>");
        bool isFirst = true;
        foreach (var row in rows)
        {
            bool useHeader = isFirst && firstRowIsHeader;
            sb.AppendLine("  <tr>");
            string tag = useHeader ? "th" : "td";
            foreach (var cell in row)
            {
                var escaped = EscapeHtml(cell);
                sb.AppendLine($"    <{tag}>{escaped}</{tag}>");
            }
            sb.AppendLine("  </tr>");
            isFirst = false;
        }
        sb.AppendLine("</table>");
        return sb.ToString();
    }

    /// <summary>
    /// Serialize <paramref name="rows"/> to a full HTML5 document and write to <paramref name="path"/>.
    /// </summary>
    public static void WriteTableToFile(
        IEnumerable<IEnumerable<string?>> rows,
        string path,
        string title = "FormatFactory HTML Export",
        bool firstRowIsHeader = false)
    {
        ArgumentNullException.ThrowIfNull(rows);
        if (string.IsNullOrWhiteSpace(path))
            throw new HtmlWriterException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var tableHtml = WriteTable(rows, firstRowIsHeader);
        var sb = new StringBuilder();
        sb.AppendLine("<!DOCTYPE html>");
        sb.AppendLine("<html lang=\"en\">");
        sb.AppendLine("<head>");
        sb.AppendLine("  <meta charset=\"UTF-8\">");
        sb.AppendLine($"  <title>{EscapeHtml(title)}</title>");
        sb.AppendLine("</head>");
        sb.AppendLine("<body>");
        sb.Append(tableHtml);
        sb.AppendLine("</body>");
        sb.AppendLine("</html>");

        var content = sb.ToString().Replace("\r\n", "\n");
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }

    // -------------------------------------------------------------------------
    // HTML escaping
    // -------------------------------------------------------------------------

    /// <summary>
    /// HTML-escape a value: encodes &amp;, &lt;, &gt;, &quot;, &#39;.
    /// Returns empty string for null.
    /// </summary>
    public static string EscapeHtml(string? value)
    {
        if (value is null || value.Length == 0) return string.Empty;
        return WebUtility.HtmlEncode(value);
    }
}

/// <summary>Thrown by <see cref="HtmlWriter"/> when output cannot be written.</summary>
public sealed class HtmlWriterException : Exception
{
    public HtmlWriterException(string message) : base(message) { }
    public HtmlWriterException(string message, Exception inner) : base(message, inner) { }
}
