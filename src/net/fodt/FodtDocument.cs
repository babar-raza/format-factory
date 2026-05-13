// FormatFactory.Fodt -- Commercial .NET FODT Document (DOM-backed)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Xml;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// DOM-backed editable document model for Flat OpenDocument Text (FODT) files.
/// Implements the load → edit → save → reload vertical slice (C4-C7).
///
/// Security posture: DTD prohibited, XmlResolver disabled, file-size guard (50 MB default).
/// Unknown XML nodes are preserved by the DOM strategy — only explicitly accessed nodes
/// are read or written.
///
/// ODF spec basis:
///   §3.1.2  office:document root element (ODF 1.3)
///   §3.3    office:body element
///   §3.4    office:text element
///   §5.1.2  text:h (heading)
///   §5.1.3  text:p (paragraph)
///
/// Local source: format_understanding/fodt/ (FUL-003 verified fact set)
///
/// Gate 11 status: commercial_readiness_in_progress — NOT release-ready.
/// </summary>
public sealed class FodtDocument
{
    // -------------------------------------------------------------------------
    // ODF namespace constants
    // -------------------------------------------------------------------------
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";

    /// <summary>Maximum file size accepted by Load(). Default: 50 MB.</summary>
    public long MaxFileSizeBytes { get; init; } = 50L * 1024 * 1024;

    private readonly XDocument _doc;

    private FodtDocument(XDocument doc)
    {
        _doc = doc;
    }

    // -------------------------------------------------------------------------
    // Factory: Load
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load a FODT file into a DOM-backed <see cref="FodtDocument"/>.
    /// Throws <see cref="FodtDocumentException"/> on parse or security failures.
    /// </summary>
    /// <param name="filePath">Path to the .fodt file.</param>
    /// <param name="maxFileSizeBytes">Optional file-size guard (default 50 MB).</param>
    public static FodtDocument Load(string filePath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new FodtDocumentException("filePath must not be null or empty.");

        if (!File.Exists(filePath))
            throw new FodtDocumentException($"File not found: {filePath}");

        var info = new FileInfo(filePath);
        if (info.Length == 0)
            throw new FodtDocumentException("File is empty (0 bytes).");

        if (info.Length > maxFileSizeBytes)
            throw new FodtDocumentException(
                $"File size {info.Length:N0} bytes exceeds limit {maxFileSizeBytes:N0} bytes.");

        var readerSettings = new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver   = null,
        };

        try
        {
            using var reader = XmlReader.Create(filePath, readerSettings);
            var doc = XDocument.Load(reader, LoadOptions.PreserveWhitespace);
            return new FodtDocument(doc) { MaxFileSizeBytes = maxFileSizeBytes };
        }
        catch (XmlException ex)
        {
            throw new FodtDocumentException($"XML parse error: {ex.Message}", ex);
        }
        catch (Exception ex) when (ex is not FodtDocumentException)
        {
            throw new FodtDocumentException(
                $"Unexpected error loading FODT: {ex.GetType().Name}: {ex.Message}", ex);
        }
    }

    // -------------------------------------------------------------------------
    // Save
    // -------------------------------------------------------------------------

    /// <summary>
    /// Save this document to the specified file path.
    /// Writes the full XDocument; all unknown/preserved nodes are written as-is.
    /// </summary>
    /// <param name="filePath">Absolute or relative path to write.</param>
    public void Save(string filePath)
    {
        FodtWriter.Save(_doc, filePath);
    }

    // -------------------------------------------------------------------------
    // Document model: Body and Paragraphs
    // -------------------------------------------------------------------------

    /// <summary>
    /// The document body (office:body/office:text wrapper).
    /// Returns null if the document has no office:body or office:text element.
    /// </summary>
    public FodtBody? Body
    {
        get
        {
            if (_doc.Root is null) return null;
            var body = _doc.Root.Element(NsOffice + "body");
            if (body is null) return null;
            var text = body.Element(NsOffice + "text");
            if (text is null) return null;
            return new FodtBody(text);
        }
    }

    /// <summary>
    /// Convenience accessor: top-level paragraphs and headings from office:body/office:text,
    /// in document order. Returns empty list if body is absent.
    /// </summary>
    public IReadOnlyList<FodtParagraph> Paragraphs =>
        Body?.Paragraphs ?? Array.Empty<FodtParagraph>();

    /// <summary>ODF MIME type from office:document/@office:mimetype, or null if absent.</summary>
    public string? MimeType =>
        _doc.Root?.Attribute(NsOffice + "mimetype")?.Value;

    /// <summary>ODF version from office:document/@office:version, or null if absent.</summary>
    public string? OdfVersion =>
        _doc.Root?.Attribute(NsOffice + "version")?.Value;
}

/// <summary>
/// Thrown by <see cref="FodtDocument.Load"/> when the file cannot be parsed or loaded safely.
/// </summary>
public sealed class FodtDocumentException : Exception
{
    public FodtDocumentException(string message) : base(message) { }
    public FodtDocumentException(string message, Exception inner) : base(message, inner) { }
}
