// FormatFactory.Txt — Standalone .NET Plain-Text Target Writer Library
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
// target_ff_library: FormatFactory.Txt.TxtWriter
// dogfood_status: IMPLEMENTED (FODT → TXT)
// commercial_product_ready: false — G11-G not approved

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Txt;

/// <summary>
/// Standalone Format Factory target writer for plain-text output.
///
/// Scope:
///   - Joins string lines with LF separators.
///   - Null lines are converted to empty strings.
///   - Normalizes any \r\n to \n for consistent output.
///   - Outputs UTF-8 without BOM.
///   - Supports both in-memory (WriteLines) and file (WriteLinesToFile) output.
///
/// MWP status: minimal viable product — production hardening is future work.
/// commercial_product_ready: false
/// </summary>
public static class TxtWriter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Join <paramref name="lines"/> with LF separators into a plain-text string.
    /// Null lines become empty strings.
    /// </summary>
    public static string WriteLines(IEnumerable<string?> lines)
    {
        ArgumentNullException.ThrowIfNull(lines);
        var parts = new List<string>();
        foreach (var line in lines)
            parts.Add(line ?? string.Empty);
        var result = string.Join("\n", parts);
        return result.Replace("\r\n", "\n").Replace("\r", "\n");
    }

    /// <summary>
    /// Join <paramref name="lines"/> and write to <paramref name="path"/>.
    /// Creates parent directories as needed. UTF-8, no BOM.
    /// </summary>
    public static void WriteLinesToFile(IEnumerable<string?> lines, string path)
    {
        ArgumentNullException.ThrowIfNull(lines);
        if (string.IsNullOrWhiteSpace(path))
            throw new TxtWriterException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var content = WriteLines(lines);
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }
}

/// <summary>Thrown by <see cref="TxtWriter"/> when output cannot be written.</summary>
public sealed class TxtWriterException : Exception
{
    public TxtWriterException(string message) : base(message) { }
    public TxtWriterException(string message, Exception inner) : base(message, inner) { }
}
