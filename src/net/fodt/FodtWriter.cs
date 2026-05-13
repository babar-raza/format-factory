// FormatFactory.Fodt -- Commercial .NET FODT Writer
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using System.Text;
using System.Xml;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Writes a FODT XDocument to a file path.
///
/// Security posture: output is ODF flat XML (UTF-8). No external entity resolution.
/// Preserves all nodes in the XDocument, including unknown nodes (DOM-backed preservation).
///
/// Gate 11 status: commercial_readiness_in_progress — NOT release-ready.
/// </summary>
internal static class FodtWriter
{
    /// <summary>
    /// Save the given XDocument to the specified file path as UTF-8 XML.
    /// The output includes the XML declaration.
    /// </summary>
    /// <param name="document">The XDocument to save.</param>
    /// <param name="filePath">Absolute or relative path to write.</param>
    /// <exception cref="ArgumentNullException">If document or filePath is null.</exception>
    /// <exception cref="IOException">If the file cannot be written.</exception>
    internal static void Save(XDocument document, string filePath)
    {
        ArgumentNullException.ThrowIfNull(document);
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("filePath must not be null or empty.", nameof(filePath));

        var writerSettings = new XmlWriterSettings
        {
            Encoding            = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
            Indent              = true,
            IndentChars         = "  ",
            OmitXmlDeclaration  = false,
            NewLineHandling     = NewLineHandling.Replace,
        };

        var dir = Path.GetDirectoryName(filePath);
        if (!string.IsNullOrEmpty(dir))
            Directory.CreateDirectory(dir);

        using var stream = new FileStream(filePath, FileMode.Create, FileAccess.Write,
                                          FileShare.None);
        using var writer = XmlWriter.Create(stream, writerSettings);
        document.Save(writer);
    }
}
