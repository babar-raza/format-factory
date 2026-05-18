// FormatFactory.Fodt -- Commercial .NET FODT → Markdown Exporter (G11-E Expanded Prototype)
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
using System.Text;

namespace FormatFactory.Fodt;

/// <summary>
/// G11-E Expanded Prototype: Exports a FODT text document to Markdown (CommonMark compatible).
///
/// Scope:
///   - Extracts all text:h (heading) and text:p (paragraph) elements from the document body.
///   - Headings are converted to ATX-style Markdown (# through ######).
///     - If outline-level is 0 or absent for a heading, defaults to level 1.
///     - Levels beyond 6 are clamped to ######.
///   - Paragraphs are exported as plain text lines.
///   - Empty paragraphs become blank lines (preserved for document structure).
///   - Output is UTF-8, LF line endings, no BOM.
///
/// Limitations (prototype):
///   - Inline formatting (bold, italic) not preserved — plain text extraction only.
///   - Tables, frames, annotations, footnotes, endnotes not extracted.
///   - Text in text:list items not extracted (future work).
///   - Markdown special characters in paragraph text are NOT escaped
///     (this is a prototype; full escaping is future hardening work).
///
/// ODF basis: §3.3 office:body, §3.4 office:text, §5.1.2 text:h, §5.1.3 text:p
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodtMarkdownExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodtPath"/> and export body content to Markdown at <paramref name="mdPath"/>.
    /// </summary>
    public static FodtMarkdownExportResult ExportToMarkdown(
        string fodtPath,
        string mdPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodtPath))
            throw new FodtMarkdownExportException("fodtPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(mdPath))
            throw new FodtMarkdownExportException("mdPath must not be null or empty.");

        FodtDocument doc;
        try
        {
            doc = FodtDocument.Load(fodtPath, maxFileSizeBytes);
        }
        catch (FodtDocumentException ex)
        {
            throw new FodtMarkdownExportException($"Failed to load FODT: {ex.Message}", ex);
        }

        return ExportToMarkdown(doc, fodtPath, mdPath);
    }

    /// <summary>
    /// Export body content of a loaded <see cref="FodtDocument"/> to Markdown at <paramref name="mdPath"/>.
    /// </summary>
    public static FodtMarkdownExportResult ExportToMarkdown(
        FodtDocument doc,
        string sourcePath,
        string mdPath)
    {
        ArgumentNullException.ThrowIfNull(doc);
        if (string.IsNullOrWhiteSpace(mdPath))
            throw new FodtMarkdownExportException("mdPath must not be null or empty.");

        var dir = Path.GetDirectoryName(mdPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodtMarkdownExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = mdPath,
        };

        var paragraphs = doc.Paragraphs;
        int headingCount = 0;
        int paraCount = 0;

        if (paragraphs.Count == 0)
        {
            File.WriteAllText(mdPath, string.Empty,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            result.Status = "exported_empty_no_paragraphs";
            result.Warnings.Add("Source FODT has no paragraphs in the body.");
            return result;
        }

        var lines = new List<string>(paragraphs.Count);

        foreach (var para in paragraphs)
        {
            if (para.IsHeading)
            {
                int level = para.OutlineLevel;
                if (level < 1) level = 1;
                if (level > 6) level = 6;
                string prefix = new string('#', level);
                lines.Add($"{prefix} {para.Text}");
                headingCount++;
            }
            else
            {
                lines.Add(para.Text);
                paraCount++;
            }
        }

        var content = string.Join("\n", lines);
        content = content.Replace("\r\n", "\n").Replace("\r", "\n");

        try
        {
            File.WriteAllText(mdPath, content,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
        catch (IOException ex)
        {
            throw new FodtMarkdownExportException(
                $"Failed to write Markdown to '{mdPath}': {ex.Message}", ex);
        }

        result.HeadingsExported = headingCount;
        result.ParagraphsExported = paraCount;
        result.Status = "exported";
        return result;
    }

    // -------------------------------------------------------------------------
    // Internal helper — exposed public for testability
    // -------------------------------------------------------------------------

    /// <summary>
    /// Format a single paragraph as a Markdown line.
    /// Headings use ATX format (# to ######); paragraphs are returned as-is.
    /// </summary>
    public static string FormatParagraphAsMarkdown(FodtParagraph para)
    {
        ArgumentNullException.ThrowIfNull(para);
        if (!para.IsHeading) return para.Text;
        int level = para.OutlineLevel;
        if (level < 1) level = 1;
        if (level > 6) level = 6;
        return $"{new string('#', level)} {para.Text}";
    }
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodtMarkdownExporter.ExportToMarkdown"/>.</summary>
public sealed class FodtMarkdownExportResult
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

/// <summary>Thrown by <see cref="FodtMarkdownExporter"/> when export cannot proceed.</summary>
public sealed class FodtMarkdownExportException : Exception
{
    public FodtMarkdownExportException(string message) : base(message) { }
    public FodtMarkdownExportException(string message, Exception inner) : base(message, inner) { }
}
