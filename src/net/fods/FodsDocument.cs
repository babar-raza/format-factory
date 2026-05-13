// FormatFactory.Fods -- Commercial .NET FODS Document (DOM-backed)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Xml;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// DOM-backed editable document model for Flat OpenDocument Spreadsheet (FODS) files.
/// Implements the load → edit → save → reload vertical slice (C4-C7).
///
/// Security posture: DTD prohibited, XmlResolver disabled, file-size guard (50 MB default).
/// Unknown XML nodes are preserved by the DOM strategy — only explicitly accessed nodes
/// are read or written.
///
/// ODF spec basis:
///   §3.1.2  office:document root element (ODF 1.3)
///   §3.7    office:spreadsheet body element
///   §9.4.2  table:table (sheet)
///   §9.4.4  table:table-row
///   §9.4.5  table:table-cell
///   §6.1.1  text:p (paragraph / cell text)
///
/// Local source: format_understanding/fods/ (FUL-002 verified fact set)
///
/// Gate 11 status: commercial_readiness_in_progress — NOT release-ready.
/// </summary>
public sealed class FodsDocument
{
    // -------------------------------------------------------------------------
    // ODF namespace constants
    // -------------------------------------------------------------------------
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    /// <summary>Maximum file size accepted by Load(). Default: 50 MB.</summary>
    public long MaxFileSizeBytes { get; init; } = 50L * 1024 * 1024;

    private readonly XDocument _doc;

    private FodsDocument(XDocument doc)
    {
        _doc = doc;
    }

    // -------------------------------------------------------------------------
    // Factory: Load
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load a FODS file into a DOM-backed <see cref="FodsDocument"/>.
    /// Throws <see cref="FodsDocumentException"/> on parse or security failures.
    /// </summary>
    /// <param name="filePath">Path to the .fods file.</param>
    /// <param name="maxFileSizeBytes">Optional file-size guard (default 50 MB).</param>
    public static FodsDocument Load(string filePath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new FodsDocumentException("filePath must not be null or empty.");

        if (!File.Exists(filePath))
            throw new FodsDocumentException($"File not found: {filePath}");

        var info = new FileInfo(filePath);
        if (info.Length == 0)
            throw new FodsDocumentException("File is empty (0 bytes).");

        if (info.Length > maxFileSizeBytes)
            throw new FodsDocumentException(
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
            return new FodsDocument(doc) { MaxFileSizeBytes = maxFileSizeBytes };
        }
        catch (XmlException ex)
        {
            throw new FodsDocumentException($"XML parse error: {ex.Message}", ex);
        }
        catch (Exception ex) when (ex is not FodsDocumentException)
        {
            throw new FodsDocumentException(
                $"Unexpected error loading FODS: {ex.GetType().Name}: {ex.Message}", ex);
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
        FodsWriter.Save(_doc, filePath);
    }

    // -------------------------------------------------------------------------
    // Document model: Sheets
    // -------------------------------------------------------------------------

    /// <summary>
    /// All sheets (table:table elements under office:body/office:spreadsheet),
    /// in document order.
    /// </summary>
    public IReadOnlyList<FodsSheet> Sheets
    {
        get
        {
            var sheets = new List<FodsSheet>();
            if (_doc.Root is null) return sheets;

            // Navigate: office:document → office:body → office:spreadsheet → table:table
            var body = _doc.Root.Element(NsOffice + "body");
            if (body is null) return sheets;

            var spreadsheet = body.Element(NsOffice + "spreadsheet");
            if (spreadsheet is null) return sheets;

            foreach (var table in spreadsheet.Elements(NsTable + "table"))
                sheets.Add(new FodsSheet(table));

            return sheets;
        }
    }

    /// <summary>
    /// ODF MIME type from office:document/@office:mimetype, or null if absent.
    /// </summary>
    public string? MimeType =>
        _doc.Root?.Attribute(NsOffice + "mimetype")?.Value;

    /// <summary>
    /// ODF version from office:document/@office:version, or null if absent.
    /// </summary>
    public string? OdfVersion =>
        _doc.Root?.Attribute(NsOffice + "version")?.Value;
}

/// <summary>
/// Thrown by <see cref="FodsDocument.Load"/> when the file cannot be parsed or loaded safely.
/// </summary>
public sealed class FodsDocumentException : Exception
{
    public FodsDocumentException(string message) : base(message) { }
    public FodsDocumentException(string message, Exception inner) : base(message, inner) { }
}
