// FormatFactory.Fods -- Commercial .NET FODS → HTML Table Exporter (G11-E Expanded Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;

namespace FormatFactory.Fods;

/// <summary>
/// G11-E Expanded Prototype: Exports a FODS spreadsheet to an HTML document with tables.
///
/// Scope:
///   - Each sheet is exported as an HTML &lt;table&gt; with a preceding &lt;h2&gt; heading.
///   - Cell values are HTML-escaped.
///   - Covered/null cells produce empty &lt;td&gt; elements.
///   - Output is UTF-8 HTML5, LF line endings, no BOM.
///   - Output includes a minimal HTML5 wrapper with charset declaration.
///
/// Limitations (prototype):
///   - No CSS styling (plain tables only).
///   - No table:number-columns-repeated expansion.
///   - No formula evaluation.
///   - No merged-cell colspan/rowspan — covered cells render as empty &lt;td&gt;.
///   - First row is NOT treated as header row (all rows use &lt;td&gt;).
///
/// Security: all cell values are HTML-escaped via WebUtility.HtmlEncode.
///
/// ODF basis: §9.4.2 table:table, §9.4.4 table:table-row, §9.4.5 table:table-cell
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodsHtmlExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export all sheets to HTML at <paramref name="htmlPath"/>.
    /// </summary>
    public static FodsHtmlExportResult ExportToHtml(
        string fodsPath,
        string htmlPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new FodsHtmlExportException("fodsPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(htmlPath))
            throw new FodsHtmlExportException("htmlPath must not be null or empty.");

        FodsDocument doc;
        try
        {
            doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        }
        catch (FodsDocumentException ex)
        {
            throw new FodsHtmlExportException($"Failed to load FODS: {ex.Message}", ex);
        }

        return ExportToHtml(doc, fodsPath, htmlPath);
    }

    /// <summary>
    /// Export all sheets of a loaded <see cref="FodsDocument"/> to HTML at <paramref name="htmlPath"/>.
    /// </summary>
    public static FodsHtmlExportResult ExportToHtml(
        FodsDocument doc,
        string sourcePath,
        string htmlPath)
    {
        ArgumentNullException.ThrowIfNull(doc);
        if (string.IsNullOrWhiteSpace(htmlPath))
            throw new FodsHtmlExportException("htmlPath must not be null or empty.");

        var dir = Path.GetDirectoryName(htmlPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodsHtmlExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = htmlPath,
        };

        var sheets = doc.Sheets;
        result.SheetsExported = sheets.Count;

        var sb = new StringBuilder();
        sb.AppendLine("<!DOCTYPE html>");
        sb.AppendLine("<html lang=\"en\">");
        sb.AppendLine("<head>");
        sb.AppendLine("  <meta charset=\"UTF-8\">");
        sb.AppendLine("  <meta name=\"generator\" content=\"FormatFactory.Fods G11-E prototype (not production)\">");
        sb.AppendLine("  <title>FODS Export</title>");
        sb.AppendLine("</head>");
        sb.AppendLine("<body>");
        sb.AppendLine("<!-- G11-E prototype: commercial_product_ready=false -->");

        int totalRows = 0;

        if (sheets.Count == 0)
        {
            sb.AppendLine("<p><em>No sheets found in document.</em></p>");
            result.Status = "exported_empty_no_sheets";
        }
        else
        {
            foreach (var sheet in sheets)
            {
                var escapedSheetName = WebUtility.HtmlEncode(sheet.Name);
                sb.AppendLine($"  <h2>{escapedSheetName}</h2>");
                sb.AppendLine("  <table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">");

                foreach (var row in sheet.Rows)
                {
                    sb.AppendLine("    <tr>");
                    foreach (var cell in row.Cells)
                    {
                        var rawVal = cell.IsCovered ? null : cell.Value;
                        var cellText = rawVal is null ? "" : WebUtility.HtmlEncode(rawVal);
                        sb.AppendLine($"      <td>{cellText}</td>");
                    }
                    sb.AppendLine("    </tr>");
                    totalRows++;
                }

                sb.AppendLine("  </table>");
            }
            result.Status = "exported";
        }

        sb.AppendLine("</body>");
        sb.AppendLine("</html>");

        result.TotalRowsExported = totalRows;

        try
        {
            var content = sb.ToString().Replace("\r\n", "\n");
            File.WriteAllText(htmlPath, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
        catch (IOException ex)
        {
            throw new FodsHtmlExportException($"Failed to write HTML to '{htmlPath}': {ex.Message}", ex);
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Internal helper — exposed public for cross-assembly tests
    // -------------------------------------------------------------------------

    /// <summary>
    /// HTML-escape a single string value.
    /// Wrapper around WebUtility.HtmlEncode for testability.
    /// </summary>
    public static string HtmlEscape(string? value) =>
        value is null ? string.Empty : WebUtility.HtmlEncode(value);
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodsHtmlExporter.ExportToHtml"/>.</summary>
public sealed class FodsHtmlExportResult
{
    public string SourcePath { get; init; } = string.Empty;
    public string OutputPath { get; init; } = string.Empty;
    public int SheetsExported { get; set; }
    public int TotalRowsExported { get; set; }
    public string Status { get; set; } = "unknown";
    public List<string> Warnings { get; } = new();
}

// -------------------------------------------------------------------------
// Exception type
// -------------------------------------------------------------------------

/// <summary>Thrown by <see cref="FodsHtmlExporter"/> when export cannot proceed.</summary>
public sealed class FodsHtmlExportException : Exception
{
    public FodsHtmlExportException(string message) : base(message) { }
    public FodsHtmlExportException(string message, Exception inner) : base(message, inner) { }
}
