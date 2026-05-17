// FormatFactory.Fodt -- Commercial .NET FODT → TXT Exporter (G11-E Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// This is a G11-E conversion/export prototype only.
// commercial_product_ready: false
// Do NOT package or publish.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Fodt;

/// <summary>
/// G11-E Prototype: Exports a FODT text document to plain text (TXT).
///
/// Scope:
///   - Extracts all paragraph and heading text from the document body.
///   - Paragraphs are separated by a single newline.
///   - Empty paragraphs become empty lines (preserved for document structure).
///   - Headings are exported as plain text (no markup).
///   - Output is UTF-8, LF line endings, no BOM.
///
/// Limitations (prototype):
///   - Tables, frames, annotations, footnotes, endnotes not extracted.
///   - Text in text:list items not extracted (future work).
///   - No DOCX or HTML output yet (future G11-E hardening sprint).
///   - Inline formatting (bold/italic/underline) is stripped — plain text only.
///
/// ODF basis:
///   §3.3 office:body, §3.4 office:text, §5.1.2 text:h, §5.1.3 text:p
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodtTxtExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodtPath"/> and export body text to TXT at <paramref name="txtPath"/>.
    /// </summary>
    /// <param name="fodtPath">Path to the .fodt source file.</param>
    /// <param name="txtPath">Path to write the output .txt file.</param>
    /// <param name="maxFileSizeBytes">File-size guard for the FODT input (default 50 MB).</param>
    /// <returns>Export result with paragraph count and status.</returns>
    /// <exception cref="FodtTxtExportException">On file-not-found, parse failure, or I/O error.</exception>
    public static FodtTxtExportResult ExportTxt(
        string fodtPath,
        string txtPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodtPath))
            throw new FodtTxtExportException("fodtPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(txtPath))
            throw new FodtTxtExportException("txtPath must not be null or empty.");

        FodtDocument doc;
        try
        {
            doc = FodtDocument.Load(fodtPath, maxFileSizeBytes);
        }
        catch (FodtDocumentException ex)
        {
            throw new FodtTxtExportException($"Failed to load FODT: {ex.Message}", ex);
        }

        return ExportTxt(doc, fodtPath, txtPath);
    }

    /// <summary>
    /// Export body text of a loaded <see cref="FodtDocument"/> to TXT at <paramref name="txtPath"/>.
    /// </summary>
    public static FodtTxtExportResult ExportTxt(
        FodtDocument doc,
        string sourcePath,
        string txtPath)
    {
        ArgumentNullException.ThrowIfNull(doc);
        if (string.IsNullOrWhiteSpace(txtPath))
            throw new FodtTxtExportException("txtPath must not be null or empty.");

        var dir = Path.GetDirectoryName(txtPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodtTxtExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = txtPath,
            Status     = "unknown",
        };

        var paragraphs = doc.Paragraphs;
        if (paragraphs.Count == 0)
        {
            // Write empty file
            File.WriteAllText(txtPath, string.Empty, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            result.ParagraphsExported = 0;
            result.Status = "exported_empty_no_paragraphs";
            result.Warnings.Add("Source FODT has no paragraphs in the body.");
            return result;
        }

        // Build output: each paragraph on its own line
        var lines = new List<string>(paragraphs.Count);
        foreach (var para in paragraphs)
        {
            // FodtParagraph.Text already concatenates all descendant text nodes
            lines.Add(para.Text);
        }

        // Join with LF (no trailing newline on last line — let caller decide)
        var content = string.Join("\n", lines);
        // Normalize any \r\n to \n for consistent output
        content = content.Replace("\r\n", "\n").Replace("\r", "\n");

        try
        {
            File.WriteAllText(txtPath, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
        catch (IOException ex)
        {
            throw new FodtTxtExportException($"Failed to write TXT to '{txtPath}': {ex.Message}", ex);
        }

        result.ParagraphsExported = paragraphs.Count;
        result.Status = "exported";
        return result;
    }
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodtTxtExporter.ExportTxt"/>.</summary>
public sealed class FodtTxtExportResult
{
    /// <summary>Path to the FODT source file.</summary>
    public string SourcePath { get; init; } = string.Empty;

    /// <summary>Path to the written TXT file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Number of paragraphs/headings exported.</summary>
    public int ParagraphsExported { get; set; }

    /// <summary>Export status: "exported", "exported_empty_no_paragraphs", or "unknown".</summary>
    public string Status { get; set; } = "unknown";

    /// <summary>Non-fatal warnings encountered during export.</summary>
    public List<string> Warnings { get; } = new();
}

// -------------------------------------------------------------------------
// Exception type
// -------------------------------------------------------------------------

/// <summary>Thrown by <see cref="FodtTxtExporter"/> when export cannot proceed.</summary>
public sealed class FodtTxtExportException : Exception
{
    public FodtTxtExportException(string message) : base(message) { }
    public FodtTxtExportException(string message, Exception inner) : base(message, inner) { }
}
