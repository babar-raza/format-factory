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
public sealed partial class FodtDocument
{
    // -------------------------------------------------------------------------
    // ODF namespace constants
    // -------------------------------------------------------------------------
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private static readonly XNamespace NsMeta =
        "urn:oasis:names:tc:opendocument:xmlns:meta:1.0";
    private static readonly XNamespace NsDc =
        "http://purl.org/dc/elements/1.1/";
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    /// <summary>Maximum file size accepted by Load(). Default: 50 MB.</summary>
    public long MaxFileSizeBytes { get; init; } = 50L * 1024 * 1024;

    private readonly XDocument _doc;

    private FodtDocument(XDocument doc)
    {
        _doc = doc;
    }

    /// <summary>Create a new empty FODT document (equivalent to <see cref="CreateEmpty"/>).</summary>
    public FodtDocument() : this(CreateEmpty()._doc) { }

    // -------------------------------------------------------------------------
    // Factory: Load / CreateEmpty
    // -------------------------------------------------------------------------

    /// <summary>
    /// Create a new, empty FODT document with no paragraphs.
    /// Call <see cref="AppendParagraph"/> to add content.
    /// R114 Train B: blank document factory for programmatic construction.
    /// </summary>
    public static FodtDocument CreateEmpty()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            "  xmlns:style=\"urn:oasis:names:tc:opendocument:xmlns:style:1.0\"" +
            "  office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            "  office:version=\"1.3\">" +
            "  <office:automatic-styles/>" +
            "  <office:body><office:text/></office:body>" +
            "</office:document>";
        var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit };
        using var reader = XmlReader.Create(new System.IO.StringReader(xml), settings);
        var doc = XDocument.Load(reader);
        return new FodtDocument(doc);
    }

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

    /// <summary>
    /// Load a FODT document from a <see cref="Stream"/>.
    /// The stream must contain valid FODT XML.
    /// </summary>
    /// <param name="stream">Readable stream containing FODT content. Must not be null.</param>
    /// <param name="maxContentBytes">
    /// Optional maximum number of bytes to read from the stream (default 50 MB).
    /// </param>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="stream"/> is null.</exception>
    /// <exception cref="FodtDocumentException">Thrown on parse or security failures.</exception>
    public static FodtDocument Load(Stream stream,
        long maxContentBytes = 50L * 1024 * 1024)
    {
        if (stream is null) throw new ArgumentNullException(nameof(stream));

        var readerSettings = new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver   = null,
        };

        try
        {
            using var reader = XmlReader.Create(stream, readerSettings);
            var doc = XDocument.Load(reader, LoadOptions.PreserveWhitespace);
            return new FodtDocument(doc) { MaxFileSizeBytes = maxContentBytes };
        }
        catch (XmlException ex)
        {
            throw new FodtDocumentException($"XML parse error: {ex.Message}", ex);
        }
        catch (Exception ex) when (ex is not FodtDocumentException)
        {
            throw new FodtDocumentException(
                $"Unexpected error loading FODT from stream: {ex.GetType().Name}: {ex.Message}", ex);
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

    /// <summary>
    /// Save this document to the specified file path.
    /// Alias for <see cref="Save(string)"/> — provides explicit round-trip API name.
    /// R91 Train H: same-format save after edit demonstration.
    /// </summary>
    /// <param name="path">Absolute or relative path to write.</param>
    public void SaveToFile(string path) => Save(path);

    /// <summary>Save this document to a file (alias for <see cref="Save"/>).</summary>
    public void SaveFile(string path) => Save(path);

    /// <summary>Load a FODT document from an existing <see cref="XmlReader"/>.</summary>
    public static FodtDocument Load(System.Xml.XmlReader reader)
    {
        var doc = XDocument.Load(reader);
        return new FodtDocument(doc);
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
    /// Convenience accessor: all top-level tables from office:body/office:text,
    /// in document order. Returns empty list if body is absent or document has no tables.
    /// ODF spec basis: ODF 1.3 §9.4.2 table:table.
    /// </summary>
    public IReadOnlyList<FodtTable> Tables =>
        Body?.Tables ?? Array.Empty<FodtTable>();

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
    /// Return the plain text content of paragraphs in the range [startIndex, endIndex).
    /// Paragraphs are joined by newlines. Both indices are zero-based.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if indices are invalid.
    /// R103 Train B: section extraction for document splitting.
    /// </summary>
    public string GetPlainTextRange(int startIndex, int endIndex)
    {
        var paras = Paragraphs;
        if (startIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(startIndex), "Start index must be non-negative.");
        if (endIndex > paras.Count)
            throw new ArgumentOutOfRangeException(nameof(endIndex),
                $"End index {endIndex} exceeds paragraph count {paras.Count}.");
        if (startIndex >= endIndex)
            return string.Empty;

        var sb = new System.Text.StringBuilder();
        for (int i = startIndex; i < endIndex; i++)
        {
            if (i > startIndex) sb.Append('\n');
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
        ArgumentNullException.ThrowIfNull(oldText);
        if (oldText.Length == 0)
            throw new ArgumentException("oldText must not be empty.", nameof(oldText));
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

    /// <summary>
    /// Return all heading paragraphs (text:h elements) in document order.
    /// Returns an empty list if the document has no headings.
    /// R92 Train M: heading enumeration for document structure analysis.
    /// </summary>
    public List<FodtParagraph> GetHeadingParagraphs()
    {
        var result = new List<FodtParagraph>();
        foreach (var para in Paragraphs)
        {
            if (para.IsHeading)
                result.Add(para);
        }
        return result;
    }

    /// <summary>
    /// Return the text content of all paragraphs in document order.
    /// Each element corresponds to one paragraph's full text content.
    /// Returns an empty list if the document has no paragraphs.
    /// R93 Train L: bulk paragraph text extraction for diff/verification.
    /// </summary>
    public List<string> GetParagraphTexts()
    {
        var result = new List<string>();
        foreach (var para in Paragraphs)
            result.Add(para.Text ?? string.Empty);
        return result;
    }

    /// <summary>
    /// Append a new paragraph with the given text to the end of the document body.
    /// The paragraph is created as a text:p element under office:body/office:text.
    /// Returns the created paragraph. Throws if the document has no body.
    /// R100 Train C: paragraph mutation API.
    /// </summary>
    public FodtParagraph AppendParagraph(string text)
    {
        var body = _doc.Root?.Element(NsOffice + "body");
        var textElement = body?.Element(NsOffice + "text");
        if (textElement is null)
            throw new InvalidOperationException("Document has no text body.");

        var para = new XElement(NsText + "p", text ?? string.Empty);
        textElement.Add(para);
        return new FodtParagraph(para);
    }

    /// <summary>
    /// Insert a new paragraph with the given text at the specified zero-based index.
    /// Shifts existing paragraphs at and after the index down by one.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if the index is invalid.
    /// Index == ParagraphCount is allowed (same as AppendParagraph).
    /// R102 Train B: paragraph insertion for document editing.
    /// </summary>
    public FodtParagraph InsertParagraph(int index, string text)
    {
        var paras = Paragraphs;
        if (index < 0 || index > paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs, insert range 0..{paras.Count}).");

        if (index == paras.Count)
            return AppendParagraph(text);

        var newPara = new XElement(NsText + "p", text ?? string.Empty);
        paras[index].Element.AddBeforeSelf(newPara);
        return new FodtParagraph(newPara);
    }

    /// <summary>
    /// Remove the paragraph at the given zero-based index from the document body.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if the index is invalid.
    /// R101 Train B: paragraph removal for document editing roundtrip.
    /// </summary>
    public void RemoveParagraph(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs).");
        paras[index].Element.Remove();
    }

    /// <summary>
    /// Set the text content of the paragraph at the given index.
    /// Replaces all existing text nodes in the paragraph element.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if the index is invalid.
    /// R104 Wave 1: in-place paragraph text editing (preserves element identity).
    /// </summary>
    public void SetParagraphText(int index, string text)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs).");

        var element = paras[index].Element;
        // Remove all existing text content but preserve non-text children if any
        foreach (var textNode in element.DescendantNodes().OfType<XText>().ToList())
            textNode.Remove();
        // If element has no children, just set value directly
        if (!element.HasElements)
            element.Value = text ?? string.Empty;
        else
            element.Add(new XText(text ?? string.Empty));
    }

    /// <summary>
    /// Export the entire document as a Markdown string.
    /// Headings become # lines (level derived from text:outline-level attribute, default 1).
    /// Paragraphs become plain text lines separated by blank lines.
    /// R101 Train B: Markdown export for documentation pipeline.
    /// </summary>
    public string ExportToMarkdown()
    {
        var sb = new System.Text.StringBuilder();
        bool first = true;
        foreach (var para in Paragraphs)
        {
            if (!first) sb.AppendLine();
            first = false;

            if (para.IsHeading)
            {
                int level = para.OutlineLevel;
                if (level < 1) level = 1;
                if (level > 6) level = 6;
                sb.Append(new string('#', level));
                sb.Append(' ');
                sb.AppendLine(para.Text ?? string.Empty);
            }
            else
            {
                sb.AppendLine(para.Text ?? string.Empty);
            }
        }
        return sb.ToString();
    }

    /// <summary>
    /// Export the document body to an HTML string.
    /// Headings become h1..h6 elements, paragraphs become p elements.
    /// R105 Wave 2: HTML export for web pipeline and dogfood.
    /// </summary>
    public string ExportToHtml()
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("<!DOCTYPE html>");
        sb.AppendLine("<html><body>");
        foreach (var para in Paragraphs)
        {
            var text = System.Net.WebUtility.HtmlEncode(para.Text ?? string.Empty);
            if (para.IsHeading)
            {
                int level = para.OutlineLevel;
                if (level < 1) level = 1;
                if (level > 6) level = 6;
                sb.AppendLine($"<h{level}>{text}</h{level}>");
            }
            else
            {
                sb.AppendLine($"<p>{text}</p>");
            }
        }
        sb.AppendLine("</body></html>");
        return sb.ToString();
    }

    /// <summary>
    /// Get the text content of a single paragraph by zero-based index.
    /// Returns null if the index is out of range.
    /// R105 Wave 2: single paragraph text access for efficient lookups.
    /// </summary>
    public string? GetParagraphText(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs).");
        return paras[index].Text;
    }

    /// <summary>
    /// Remove all paragraphs and headings from the document body.
    /// After this call ParagraphCount will be 0.
    /// R106 Wave 2: document clearing for editing workflows.
    /// </summary>
    public void RemoveAllParagraphs()
    {
        var paras = Paragraphs;
        var toRemove = new List<XElement>(paras.Count);
        foreach (var p in paras)
            toRemove.Add(p.Element);
        foreach (var el in toRemove)
            el.Remove();
    }

    /// <summary>
    /// Extract the concatenated text of paragraphs from startIndex (inclusive) to endIndex (exclusive).
    /// Returns paragraphs separated by newlines.
    /// Returns null if either index is out of range or start >= end.
    /// R106 Wave 2: text range extraction for document analysis.
    /// </summary>
    public string? GetTextBetweenParagraphs(int startIndex, int endIndex)
    {
        var paras = Paragraphs;
        if (startIndex < 0 || endIndex > paras.Count || startIndex >= endIndex)
            return null;
        var sb = new System.Text.StringBuilder();
        for (int i = startIndex; i < endIndex; i++)
        {
            if (i > startIndex) sb.Append('\n');
            sb.Append(paras[i].Text ?? string.Empty);
        }
        return sb.ToString();
    }

    /// <summary>
    /// Return the text content of all headings in document order.
    /// Returns an empty list if the document has no headings.
    /// Complements GetParagraphTexts() by filtering to headings only.
    /// R107 Wave 2: heading text extraction for document structure analysis.
    /// </summary>
    public IReadOnlyList<string> GetHeadingTexts()
    {
        var result = new List<string>();
        foreach (var para in Paragraphs)
        {
            if (para.IsHeading)
                result.Add(para.Text ?? string.Empty);
        }
        return result.AsReadOnly();
    }

    /// <summary>
    /// Export the document body to a plain text file.
    /// Paragraphs are joined by newlines, headings are treated as plain text.
    /// Creates or overwrites the file at the specified path.
    /// R107 Wave 2: plain text export for TXT dogfood pipeline.
    /// </summary>
    public void ExportToPlainTextFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var text = GetPlainText();
        File.WriteAllText(filePath, text);
    }

    /// <summary>
    /// Export the document content as Markdown to a file.
    /// Creates or overwrites the file at the specified path.
    /// R108 Lane D: Markdown file export for documentation workflow.
    /// </summary>
    public void ExportToMarkdownFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var markdown = ExportToMarkdown();
        File.WriteAllText(filePath, markdown);
    }

    /// <summary>
    /// Export the document body to an HTML file on disk.
    /// Creates or overwrites the file at the specified path.
    /// R109 Lane D: HTML file export for web publishing workflow.
    /// </summary>
    public void ExportToHtmlFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var html = ExportToHtml();
        File.WriteAllText(filePath, html);
    }

    /// <summary>
    /// Insert a new heading with the given text and outline level at the specified index.
    /// Creates a text:h element (not text:p). Level must be 1-6.
    /// Shifts existing paragraphs at and after the index down by one.
    /// R110 Wave 4: heading insertion for document structure editing.
    /// </summary>
    public FodtParagraph InsertHeading(int index, string text, int level)
    {
        if (level < 1 || level > 6)
            throw new ArgumentOutOfRangeException(nameof(level), "Heading level must be between 1 and 6.");

        var paras = Paragraphs;
        if (index < 0)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs, insert range 0..{paras.Count}).");
        if (index > paras.Count + 1)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Heading index {index} is out of range (document has {paras.Count} paragraphs, insert range 0..{paras.Count}).");
        if (index > paras.Count)
            index = paras.Count; // clamp to append at end

        var heading = new XElement(NsText + "h",
            new XAttribute(NsText + "outline-level", level.ToString()),
            text ?? string.Empty);

        if (index == paras.Count)
        {
            var body = _doc.Root?.Element(NsOffice + "body");
            var textElement = body?.Element(NsOffice + "text");
            if (textElement is null)
                throw new InvalidOperationException("Document has no text body.");
            textElement.Add(heading);
        }
        else
        {
            paras[index].Element.AddBeforeSelf(heading);
        }

        return new FodtParagraph(heading);
    }

    /// <summary>
    /// Remove a heading element by its index within the combined paragraph/heading list.
    /// Only removes elements that are headings (text:h). Throws if the element at the index
    /// is not a heading or the index is out of range.
    /// R111 Wave 5: object-model depth, complements InsertHeading.
    /// </summary>
    public void RemoveHeading(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs).");

        var element = paras[index].Element;
        if (element.Name.LocalName != "h")
            throw new InvalidOperationException(
                $"Element at index {index} is a '{element.Name.LocalName}', not a heading ('h').");

        element.Remove();
    }

    /// <summary>
    /// Set the style name on the paragraph at the given index.
    /// For heading paragraphs, updates text:style-name on the text:h element.
    /// For body paragraphs, updates text:style-name on the text:p element.
    /// Throws if the index is out of range.
    /// R114 Train B: paragraph style management for formatting pipelines.
    /// </summary>
    public void SetParagraphStyle(int index, string styleName)
    {
        ArgumentNullException.ThrowIfNull(styleName);
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Paragraph index {index} is out of range (document has {paras.Count} paragraphs).");

        paras[index].Element.SetAttributeValue(NsText + "style-name", styleName);
    }

    // -------------------------------------------------------------------------
    // Metadata
    // -------------------------------------------------------------------------

    /// <summary>ODF MIME type from office:document/@office:mimetype, or null if absent.</summary>
    public string? MimeType =>
        _doc.Root?.Attribute(NsOffice + "mimetype")?.Value;

    /// <summary>ODF version from office:document/@office:version, or null if absent.</summary>
    public string? OdfVersion =>
        _doc.Root?.Attribute(NsOffice + "version")?.Value;
}
