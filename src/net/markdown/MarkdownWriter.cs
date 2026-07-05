// FormatFactory.Markdown — Standalone .NET Markdown Target Writer Library
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
// target_ff_library: FormatFactory.Markdown.MarkdownWriter
// dogfood_status: IMPLEMENTED (FODT → Markdown)
// commercial_product_ready: false — G11-G not approved

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Markdown;

/// <summary>
/// Standalone Format Factory target writer for Markdown (CommonMark compatible).
///
/// Scope:
///   - Generates ATX-style headings (# through ######).
///   - Writes plain paragraph lines.
///   - Joins lines with LF separators.
///   - Outputs UTF-8 without BOM.
///   - Supports in-memory (WriteHeading, WriteParagraphs) and file (WriteLinesToFile) output.
///
/// MWP status: minimal viable product — production hardening is future work.
/// commercial_product_ready: false
/// </summary>
public static class MarkdownWriter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Format a heading at the given ATX level (1–6).
    /// Levels outside [1,6] are clamped.
    /// </summary>
    public static string WriteHeading(string text, int level)
    {
        if (level < 1) level = 1;
        if (level > 6) level = 6;
        return $"{new string('#', level)} {text ?? string.Empty}";
    }

    /// <summary>
    /// Format a sequence of paragraph strings (non-heading lines).
    /// Null lines become empty strings.
    /// </summary>
    public static string WriteParagraphs(IEnumerable<string?> paragraphs)
    {
        ArgumentNullException.ThrowIfNull(paragraphs);
        var parts = new List<string>();
        foreach (var p in paragraphs)
            parts.Add(p ?? string.Empty);
        return string.Join("\n", parts);
    }

    /// <summary>
    /// Return <paramref name="lines"/> joined with LF as a string.
    /// Null entries become empty strings.
    /// </summary>
    public static string WriteLines(IEnumerable<string?> lines)
    {
        ArgumentNullException.ThrowIfNull(lines);
        var parts = new List<string>();
        foreach (var line in lines)
            parts.Add(line ?? string.Empty);
        return string.Join("\n", parts);
    }

    /// <summary>
    /// Write <paramref name="lines"/> joined with LF to <paramref name="path"/>.
    /// Creates parent directories as needed. UTF-8, no BOM.
    /// </summary>
    public static void WriteLinesToFile(IEnumerable<string?> lines, string path)
    {
        ArgumentNullException.ThrowIfNull(lines);
        if (string.IsNullOrWhiteSpace(path))
            throw new MarkdownWriterException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var parts = new List<string>();
        foreach (var line in lines)
            parts.Add(line ?? string.Empty);
        var content = string.Join("\n", parts);
        content = content.Replace("\r\n", "\n").Replace("\r", "\n");
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }
}

/// <summary>Thrown by <see cref="MarkdownWriter"/> when output cannot be written.</summary>
public sealed class MarkdownWriterException : Exception
{
    public MarkdownWriterException(string message) : base(message) { }
    public MarkdownWriterException(string message, Exception inner) : base(message, inner) { }
}
