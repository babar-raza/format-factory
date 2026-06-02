// FormatFactory.Fodt -- Commercial .NET FODT Document (DOM-backed)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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

    /// <summary>
    /// Get the plain text content of the document (all paragraphs joined by newlines).
    /// R88 Train I: text analysis API.
    /// </summary>
    public string GetPlainText()
    {
        var paras = Paragraphs;
        if (paras.Count == 0) return string.Empty;
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < paras.Count; i++)
        {
            if (i > 0) sb.Append('\n');
            sb.Append(paras[i].Text ?? string.Empty);
        }
        return sb.ToString();
    }

    /// <summary>
    /// Count words in the document (whitespace-delimited tokens across all paragraphs).
    /// R88 Train I: text analysis API.
    /// </summary>
    public int WordCount
    {
        get
        {
            var text = GetPlainText();
            if (string.IsNullOrWhiteSpace(text)) return 0;
            return text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
        }
    }

    /// <summary>
    /// Count characters in the document (excluding leading/trailing whitespace per paragraph).
    /// R89 Train I: text statistics API.
    /// </summary>
    public int CharCount
    {
        get
        {
            int count = 0;
            foreach (var para in Paragraphs)
            {
                var text = para.Text;
                if (!string.IsNullOrEmpty(text))
                    count += text.Length;
            }
            return count;
        }
    }

    /// <summary>
    /// Search for all occurrences of a substring in the document text.
    /// Returns a list of (paragraphIndex, positionInParagraph) tuples.
    /// R89 Train I: text search API.
    /// </summary>
    public List<(int ParagraphIndex, int Position)> SearchText(string query, StringComparison comparison = StringComparison.Ordinal)
    {
        if (string.IsNullOrEmpty(query))
            throw new ArgumentException("Search query must not be null or empty.", nameof(query));

        var results = new List<(int, int)>();
        var paras = Paragraphs;
        for (int i = 0; i < paras.Count; i++)
        {
            var text = paras[i].Text;
            if (string.IsNullOrEmpty(text)) continue;

            int pos = 0;
            while ((pos = text.IndexOf(query, pos, comparison)) >= 0)
            {
                results.Add((i, pos));
                pos += query.Length;
            }
        }
        return results;
    }

    /// <summary>
    /// Replace all occurrences of a substring in paragraph text nodes.
    /// Returns the total number of replacements made.
    /// R92 Train C: text manipulation API.
    /// </summary>
    public int ReplaceText(string oldText, string newText, StringComparison comparison = StringComparison.Ordinal)
    {
        if (string.IsNullOrEmpty(oldText))
            throw new ArgumentException("oldText must not be null or empty.", nameof(oldText));
        ArgumentNullException.ThrowIfNull(newText);

        int totalReplacements = 0;
        var body = Body;
        if (body is null) return 0;

        foreach (var para in body.Paragraphs)
        {
            var element = para.Element;
            foreach (var textNode in element.DescendantNodes().OfType<XText>().ToList())
            {
                var original = textNode.Value;
                int count = 0;
                int pos = 0;
                while ((pos = original.IndexOf(oldText, pos, comparison)) >= 0)
                {
                    count++;
                    pos += oldText.Length;
                }
                if (count > 0)
                {
                    // Simple replacement — works for Ordinal comparison
                    var replaced = original;
                    if (comparison == StringComparison.Ordinal)
                        replaced = original.Replace(oldText, newText);
                    else
                        replaced = ReplaceWithComparison(original, oldText, newText, comparison);
                    textNode.Value = replaced;
                    totalReplacements += count;
                }
            }
        }
        return totalReplacements;
    }

    private static string ReplaceWithComparison(string source, string oldValue, string newValue, StringComparison comparison)
    {
        var sb = new System.Text.StringBuilder();
        int pos = 0;
        int idx;
        while ((idx = source.IndexOf(oldValue, pos, comparison)) >= 0)
        {
            sb.Append(source, pos, idx - pos);
            sb.Append(newValue);
            pos = idx + oldValue.Length;
        }
        sb.Append(source, pos, source.Length - pos);
        return sb.ToString();
    }

    /// <summary>
    /// Number of paragraphs in the document.
    /// R92 Train C: convenience property.
    /// </summary>
    public int ParagraphCount => Paragraphs.Count;

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
