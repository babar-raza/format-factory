// FormatFactory.Fods -- table:table-row / table:table-cell export serializers
// Separated from FodsDocument.cs per TC-NET-001 (QName-based split).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// ODF spec basis:
//   §9.4.2  table:table (sheet)
//   §9.4.4  table:table-row
//   §9.4.5  table:table-cell
//   §6.1.1  text:p (paragraph / cell text)

using System;
using System.Text;

namespace FormatFactory.Fods;

/// <summary>
/// Static export serializers for <see cref="FodsDocument"/> sheet data.
/// Handles transformation of table:table / table:table-cell structures to
/// HTML, JSON, Markdown, and CSV string output.
///
/// These methods are pure: they take a <see cref="FodsSheet"/> and return
/// a formatted string. They have no document lifecycle concerns.
///
/// Delegation target for <see cref="FodsDocument"/> export overloads.
/// </summary>
public static class FodsDocumentExporter
{
    // -------------------------------------------------------------------------
    // HTML (table:table → &lt;table&gt;)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as an HTML table string.
    /// Rows become &lt;tr&gt; elements, cells become &lt;td&gt; elements.
    /// Empty cells produce empty &lt;td&gt; elements. Cell text is HTML-escaped.
    /// HTML export implementation.
    /// </summary>
    public static string ExportSheetToHtml(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var sb = new StringBuilder();
        sb.AppendLine("<table>");
        foreach (var row in sheet.Rows)
        {
            sb.Append("  <tr>");
            foreach (var cell in row.Cells)
            {
                var text = System.Net.WebUtility.HtmlEncode(cell.Value ?? string.Empty);
                sb.Append($"<td>{text}</td>");
            }
            sb.AppendLine("</tr>");
        }
        sb.AppendLine("</table>");
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // JSON (table:table-row → JSON objects)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as a JSON array of row objects.
    /// The first row is treated as headers; subsequent rows become objects keyed by those headers.
    /// If the sheet has zero or one row, returns "[]".
    /// JSON export implementation.
    /// </summary>
    public static string ExportSheetToJson(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var rows = sheet.Rows;
        if (rows.Count <= 1)
            return "[]";

        var headers = new System.Collections.Generic.List<string>();
        foreach (var cell in rows[0].Cells)
            headers.Add(cell.Value ?? $"col{headers.Count}");

        var sb = new StringBuilder();
        sb.AppendLine("[");
        for (int i = 1; i < rows.Count; i++)
        {
            if (i > 1) sb.AppendLine(",");
            sb.Append("  {");
            var cells = rows[i].Cells;
            for (int j = 0; j < headers.Count; j++)
            {
                if (j > 0) sb.Append(", ");
                var key = JsonEscape(headers[j]);
                var val = j < cells.Count ? JsonEscape(cells[j].Value ?? "") : "";
                sb.Append($"\"{key}\": \"{val}\"");
            }
            sb.Append("}");
        }
        sb.AppendLine();
        sb.AppendLine("]");
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // Markdown (table:table-row → Markdown table)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as a Markdown table string.
    /// The first row is treated as headers with a separator line beneath.
    /// Pipe characters in cell values are escaped as \|.
    /// Returns an empty string if the sheet has no rows.
    /// Markdown export implementation.
    /// </summary>
    public static string ExportSheetToMarkdown(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var rows = sheet.Rows;
        if (rows.Count == 0) return string.Empty;

        var sb = new StringBuilder();

        // Header row
        var headerCells = rows[0].Cells;
        sb.Append('|');
        foreach (var cell in headerCells)
        {
            sb.Append(' ');
            sb.Append(MdEscape(cell.Value ?? string.Empty));
            sb.Append(" |");
        }
        sb.AppendLine();

        // Separator row
        sb.Append('|');
        for (int j = 0; j < headerCells.Count; j++)
        {
            sb.Append(" --- |");
        }
        sb.AppendLine();

        // Data rows
        for (int i = 1; i < rows.Count; i++)
        {
            sb.Append('|');
            var cells = rows[i].Cells;
            int colCount = Math.Max(headerCells.Count, cells.Count);
            for (int j = 0; j < colCount; j++)
            {
                sb.Append(' ');
                var val = j < cells.Count ? (cells[j].Value ?? string.Empty) : string.Empty;
                sb.Append(MdEscape(val));
                sb.Append(" |");
            }
            sb.AppendLine();
        }

        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // CSV (table:table-row → RFC 4180)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as CSV (comma-separated values).
    /// Each row becomes a line, cells are comma-separated, values containing
    /// commas/quotes/newlines are enclosed in double quotes with internal quotes
    /// doubled (RFC 4180).
    /// CSV export implementation.
    /// </summary>
    public static string ExportSheetToCsv(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var sb = new StringBuilder();
        foreach (var row in sheet.Rows)
        {
            bool firstCell = true;
            foreach (var cell in row.Cells)
            {
                if (!firstCell) sb.Append(',');
                firstCell = false;
                var val = cell.Value ?? string.Empty;
                if (val.Contains(',') || val.Contains('"') || val.Contains('\n') || val.Contains('\r'))
                {
                    sb.Append('"');
                    sb.Append(val.Replace("\"", "\"\""));
                    sb.Append('"');
                }
                else
                {
                    sb.Append(val);
                }
            }
            sb.AppendLine();
        }
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // TSV (table:table-row → tab-separated values)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as TSV (tab-separated values).
    /// Each row becomes a line, cells are tab-separated.
    /// Cell values that contain tabs or newlines have those characters replaced with spaces
    /// to preserve the single-row-per-line invariant.
    /// Sprint: FORMAT-FACTORY-FODS-TSV-EXPORT-20260625.
    /// </summary>
    public static string ExportSheetToTsv(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var sb = new StringBuilder();
        foreach (var row in sheet.Rows)
        {
            bool firstCell = true;
            foreach (var cell in row.Cells)
            {
                if (!firstCell) sb.Append('\t');
                firstCell = false;
                var val = cell.Value ?? string.Empty;
                // Replace tabs and newlines to preserve TSV structure
                val = val.Replace('\t', ' ').Replace('\r', ' ').Replace('\n', ' ');
                sb.Append(val);
            }
            sb.AppendLine();
        }
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // XML (table:table-row → simple XML table)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a sheet as a simple XML table string.
    /// Each row becomes a &lt;row&gt; element, each cell a &lt;cell&gt; element.
    /// Cell text is XML-escaped. Root element is &lt;table name="{sheetName}"&gt;.
    /// Empty cell values produce empty &lt;cell/&gt; elements.
    /// Sprint: FORMAT-FACTORY-FODS-XML-EXPORT-20260625.
    /// </summary>
    public static string ExportSheetToXml(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        var sb = new StringBuilder();
        var name = XmlAttrEscape(sheet.Name ?? "sheet");
        sb.AppendLine($"<table name=\"{name}\">");
        foreach (var row in sheet.Rows)
        {
            sb.Append("  <row>");
            foreach (var cell in row.Cells)
            {
                var text = XmlEscape(cell.Value ?? string.Empty);
                if (text.Length == 0)
                    sb.Append("<cell/>");
                else
                    sb.Append($"<cell>{text}</cell>");
            }
            sb.AppendLine("</row>");
        }
        sb.AppendLine("</table>");
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    private static string XmlEscape(string s) =>
        s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
         .Replace("\"", "&quot;").Replace("'", "&apos;");

    private static string XmlAttrEscape(string s) =>
        s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
         .Replace("\"", "&quot;");

    private static string MdEscape(string s) => s.Replace("|", "\\|");

    private static string JsonEscape(string s)
    {
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"")
                .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
    }
}
