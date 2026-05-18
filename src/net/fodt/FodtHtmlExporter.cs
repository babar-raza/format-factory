// FormatFactory.Fodt -- Commercial .NET FODT → HTML Exporter (G11-E Expanded Prototype)
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

namespace FormatFactory.Fodt;

/// <summary>
/// G11-E Expanded Prototype: Exports a FODT text document to HTML.
///
/// Scope:
///   - Extracts all text:h (heading) and text:p (paragraph) elements from the document body.
///   - Headings become &lt;h1&gt; through &lt;h6&gt; (clamped to valid HTML range).
///     - outline-level 0 or absent defaults to h1.
///   - Paragraphs become &lt;p&gt; elements.
///   - Empty paragraphs become &lt;p&gt;&lt;br&gt;&lt;/p&gt; (preserves spacing).
///   - All text content is HTML-escaped.
///   - Output is UTF-8 HTML5, LF line endings, no BOM.
///
/// Limitations (prototype):
///   - Inline formatting (bold, italic) not preserved — plain text extraction only.
///   - Tables, frames, annotations, footnotes, endnotes not extracted.
///   - Text in text:list items not extracted (future work).
///   - No CSS styling (plain semantic HTML only).
///
/// Security: all text values are HTML-escaped via WebUtility.HtmlEncode.
///
/// ODF basis: §3.3 office:body, §3.4 office:text, §5.1.2 text:h, §5.1.3 text:p
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodtHtmlExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodtPath"/> and export body content to HTML at <paramref name="htmlPath"/>.
    /// </summary>
    public static FodtHtmlExportResult ExportToHtml(
        string fodtPath,
        string htmlPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodtPath))
            throw new FodtHtmlExportException("fodtPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(htmlPath))
            throw new FodtHtmlExportException("htmlPath must not be null or empty.");

        FodtDocument doc;
        try
        {
            doc = FodtDocument.Load(fodtPath, maxFileSizeBytes);
        }
        catch (FodtDocumentException ex)
        {
            throw new FodtHtmlExportException($"Failed to load FODT: {ex.Message}", ex);
        }

        return ExportToHtml(doc, fodtPath, htmlPath);
    }

    /// <summary>
    /// Export body content of a loaded <see cref="FodtDocument"/> to HTML at <paramref name="htmlPath"/>.
    /// </summary>
    public static FodtHtmlExportResult ExportToHtml(
        FodtDocument doc,
        string sourcePath,
        string htmlPath)
    {
        ArgumentNullException.ThrowIfNull(doc);
        if (string.IsNullOrWhiteSpace(htmlPath))
            throw new FodtHtmlExportException("htmlPath must not be null or empty.");

        var dir = Path.GetDirectoryName(htmlPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodtHtmlExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = htmlPath,
        };

        var paragraphs = doc.Paragraphs;
        int headingCount = 0;
        int paraCount = 0;

        var sb = new StringBuilder();
        sb.AppendLine("<!DOCTYPE html>");
        sb.AppendLine("<html lang=\"en\">");
        sb.AppendLine("<head>");
        sb.AppendLine("  <meta charset=\"UTF-8\">");
        sb.AppendLine("  <meta name=\"generator\" content=\"FormatFactory.Fodt G11-E prototype (not production)\">");
        sb.AppendLine("  <title>FODT Export</title>");
        sb.AppendLine("</head>");
        sb.AppendLine("<body>");
        sb.AppendLine("<!-- G11-E prototype: commercial_product_ready=false -->");

        if (paragraphs.Count == 0)
        {
            sb.AppendLine("<p><em>No content found in document body.</em></p>");
            result.Status = "exported_empty_no_paragraphs";
            result.Warnings.Add("Source FODT has no paragraphs in the body.");
        }
        else
        {
            foreach (var para in paragraphs)
            {
                var escaped = WebUtility.HtmlEncode(para.Text);

                if (para.IsHeading)
                {
                    int level = para.OutlineLevel;
                    if (level < 1) level = 1;
                    if (level > 6) level = 6;
                    sb.AppendLine($"  <h{level}>{escaped}</h{level}>");
                    headingCount++;
                }
                else
                {
                    if (string.IsNullOrEmpty(para.Text))
                        sb.AppendLine("  <p><br></p>");
                    else
                        sb.AppendLine($"  <p>{escaped}</p>");
                    paraCount++;
                }
            }
            result.Status = "exported";
        }

        sb.AppendLine("</body>");
        sb.AppendLine("</html>");

        result.HeadingsExported = headingCount;
        result.ParagraphsExported = paraCount;

        try
        {
            var content = sb.ToString().Replace("\r\n", "\n");
            File.WriteAllText(htmlPath, content,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
        catch (IOException ex)
        {
            throw new FodtHtmlExportException(
                $"Failed to write HTML to '{htmlPath}': {ex.Message}", ex);
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Internal helper — exposed public for testability
    // -------------------------------------------------------------------------

    /// <summary>HTML-escape a string value. Wrapper for testability.</summary>
    public static string HtmlEscape(string? value) =>
        value is null ? string.Empty : WebUtility.HtmlEncode(value);
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodtHtmlExporter.ExportToHtml"/>.</summary>
public sealed class FodtHtmlExportResult
{
    public string SourcePath { get; init; } = string.Empty;
    public string OutputPath { get; init; } = string.Empty;
    public int HeadingsExported { get; set; }
    public int ParagraphsExported { get; set; }
    public string Status { get; set; } = "unknown";
    public List<string> Warnings { get; } = new();
}

// -------------------------------------------------------------------------
// Exception type
// -------------------------------------------------------------------------

/// <summary>Thrown by <see cref="FodtHtmlExporter"/> when export cannot proceed.</summary>
public sealed class FodtHtmlExportException : Exception
{
    public FodtHtmlExportException(string message) : base(message) { }
    public FodtHtmlExportException(string message, Exception inner) : base(message, inner) { }
}
