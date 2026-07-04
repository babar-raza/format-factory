// FormatFactory.Fodt -- FodtDocument section, bookmark, comment, and annotation operations (partial class).
// Split from FodtDocumentEditing.cs (TC-HEAL-NET-001 -- 2026-07-04).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

public sealed partial class FodtDocument
{

    /// <summary>R264: Return the items in the list at the given index.</summary>
    public List<string> GetListItems(int listIndex)
    {
        var lists = GetDomItems("list");
        if (listIndex < 0 || listIndex >= lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        return lists[listIndex].Elements(NsMeta + "item").Select(e => e.Value).ToList();
    }

    /// <summary>R264: Return the text of a specific list item by list and item index.</summary>
    public string GetListItemText(int listIndex, int itemIndex)
    {
        var lists = GetDomItems("list");
        if (listIndex < 0 || listIndex >= lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        var listItems = lists[listIndex].Elements(NsMeta + "item").ToList();
        if (itemIndex < 0 || itemIndex >= listItems.Count)
            throw new ArgumentOutOfRangeException(nameof(itemIndex));
        return listItems[itemIndex].Value;
    }

    /// <summary>R264: Return the text of the item at the given global index across all lists.</summary>
    public string GetListItemText(int globalIndex)
    {
        int remaining = globalIndex;
        foreach (var listEl in GetDomItems("list"))
        {
            var items = listEl.Elements(NsMeta + "item").ToList();
            if (remaining < items.Count) return items[remaining].Value;
            remaining -= items.Count;
        }
        throw new ArgumentOutOfRangeException(nameof(globalIndex));
    }

    // -------------------------------------------------------------------------
    // Image operations (R283)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Image operations (R283) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R283: Return the number of images in the document.</summary>
    public int GetImageCount() => GetDomItems("image").Count;

    /// <summary>R283: Add an image reference with the given file path.</summary>
    public void AddImage(string path, string caption = "")
    {
        ArgumentNullException.ThrowIfNull(path);
        AddDomItem(new XElement(NsMeta + "image",
            new XAttribute(NsMeta + "path", path),
            new XAttribute(NsMeta + "caption", caption ?? string.Empty)));
    }

    /// <summary>R283: Insert an image at the given paragraph position.</summary>
    public void InsertImage(int paragraphIndex, string path, string caption = "")
    {
        ArgumentNullException.ThrowIfNull(path);
        if (paragraphIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(paragraphIndex));
        AddDomItem(new XElement(NsMeta + "image",
            new XAttribute(NsMeta + "path", path),
            new XAttribute(NsMeta + "caption", caption ?? string.Empty),
            new XAttribute(NsMeta + "para", paragraphIndex.ToString())));
    }

    /// <summary>R283: Return the path of the image at the given index.</summary>
    public string GetImagePath(int index)
    {
        var items = GetDomItems("image");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "path")?.Value ?? string.Empty;
    }

    /// <summary>R283: Add an image at a paragraph position with path and caption.</summary>
    public void AddImage(int position, string path, string caption)
    {
        ArgumentNullException.ThrowIfNull(path);
        AddDomItem(new XElement(NsMeta + "image",
            new XAttribute(NsMeta + "path", path),
            new XAttribute(NsMeta + "caption", caption ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString())));
    }

    /// <summary>R283: Return the caption of the image at the given index.</summary>
    public string GetImageCaption(int index)
    {
        var items = GetDomItems("image");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "caption")?.Value ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Metadata operations (R196) — delegate to GetDocumentMetadata() + in-memory
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, string> _metaOverrides = new();

    private string? GetMeta(string key)
    {
        if (_metaOverrides.TryGetValue(key, out var ov)) return ov;
        var meta = GetDocumentMetadata();
        if (meta.TryGetValue(key, out var v)) return v;
        // Alias: "author" → "creator" (ODF canonical name)
        if (key == "author" && meta.TryGetValue("creator", out var c)) return c;
        return null;
    }

    private void SetMeta(string key, string? value)
    {
        _metaOverrides[key] = value ?? string.Empty;
        // Write through to DOM so metadata persists on save/load
        var root = _doc.Root;
        if (root is null) return;
        var metaEl = root.Element(NsOffice + "meta");
        if (metaEl is null)
        {
            metaEl = new XElement(NsOffice + "meta");
            var body = root.Element(NsOffice + "body");
            if (body != null) body.AddBeforeSelf(metaEl); else root.AddFirst(metaEl);
        }
        XName? elemName = key == "title" ? NsDc + "title"
            : key == "creator" ? NsDc + "creator"
            : key == "date" ? NsDc + "date"
            : key == "description" ? NsDc + "description"
            : key == "subject" ? NsDc + "subject"
            : key == "language" ? NsDc + "language"
            : key == "creation-date" ? NsMeta + "creation-date"
            : key == "editing-cycles" ? NsMeta + "editing-cycles"
            : key == "generator" ? NsMeta + "generator"
            : key == "initial-creator" ? NsMeta + "initial-creator"
            : (XName?)null;
        if (elemName is null) return;
        var el = metaEl.Element(elemName);
        if (el is null) { el = new XElement(elemName); metaEl.Add(el); }
        el.Value = value ?? string.Empty;
    }

    /// <summary>R196: Return the document title.</summary>
    public string? GetDocumentTitle() => GetMeta("title") ?? "Untitled";

    /// <summary>R196: Set the document title.</summary>
    public void SetDocumentTitle(string? title) => SetMeta("title", title);

    /// <summary>R196: Return the document title property.</summary>
    public string? Title => GetDocumentTitle();

    /// <summary>R196: Return the document author.</summary>
    public string? GetAuthor() => GetMeta("creator") ?? GetMeta("initial-creator");

    /// <summary>R196: Set the document author.</summary>
    public void SetAuthor(string? author) => SetMeta("creator", author);

    /// <summary>R196: Return the author as a property.</summary>
    public string? Author => GetAuthor();

    /// <summary>R196: Return the document creator.</summary>
    public string? GetCreator() => GetAuthor();

    /// <summary>R196: Set the document creator.</summary>
    public void SetCreator(string? creator) => SetAuthor(creator);

    /// <summary>R196: Return the document language.</summary>
    public string? GetLanguage() => GetMeta("language");

    /// <summary>R196: Set the document language.</summary>
    public void SetLanguage(string? lang) => SetMeta("language", lang);

    /// <summary>R196: Return the document description.</summary>
    public string? GetDocumentDescription() => GetMeta("description") ?? "Open Document Text document";

    /// <summary>R196: Set the document description.</summary>
    public void SetDocumentDescription(string? desc) => SetMeta("description", desc);

    /// <summary>R196: Return the document subject.</summary>
    public string? GetDocumentSubject() => GetMeta("subject") ?? "General";

    /// <summary>R196: Set the document subject.</summary>
    public void SetDocumentSubject(string? subject) => SetMeta("subject", subject);

    /// <summary>R196: Return the document keywords.</summary>
    public string? GetDocumentKeywords() => GetMeta("keywords") ?? "document";

    /// <summary>R196: Set the document keywords.</summary>
    public void SetDocumentKeywords(string? keywords) => SetMeta("keywords", keywords);

    /// <summary>R196: Return the document creation date.</summary>
    public string? GetCreationDate() => GetMeta("creation-date");

    /// <summary>R196: Return the document last modified date.</summary>
    public string? GetLastModifiedDate() => GetMeta("date");

    /// <summary>R196: Return a metadata dictionary (alias for GetDocumentMetadata + overrides).</summary>
    public IReadOnlyDictionary<string, string> GetMetadata()
    {
        var result = new Dictionary<string, string>(GetDocumentMetadata());
        foreach (var kv in _metaOverrides)
            result[kv.Key] = kv.Value;
        return result;
    }

    /// <summary>R196: Set a single metadata value by key.</summary>
    public void SetMetadata(string key, string value)
    {
        ArgumentNullException.ThrowIfNull(key);
        // Normalize key aliases before storing and writing to DOM
        var canonicalKey = key == "author" ? "creator" : key;
        _metaOverrides[key] = value ?? string.Empty;
        if (canonicalKey != key) _metaOverrides[canonicalKey] = value ?? string.Empty;
        SetMeta(canonicalKey, value);
    }

    /// <summary>R196: Get a single metadata value by key.</summary>
    public string? GetMetadata(string key)
    {
        ArgumentNullException.ThrowIfNull(key);
        return GetMeta(key);
    }

    /// <summary>R196: Set metadata from a dictionary.</summary>
    public void SetMetadata(IReadOnlyDictionary<string, string> metadata)
    {
        ArgumentNullException.ThrowIfNull(metadata);
        foreach (var kv in metadata)
            _metaOverrides[kv.Key] = kv.Value;
    }

    /// <summary>R196/R238: Return a document summary with paragraph, word, and heading counts.</summary>
    public FodtDocumentStats GetDocumentSummary()
    {
        var s = GetDocumentStats();
        return new FodtDocumentStats { WordCount = s.WordCount, CharCount = s.CharCount, ParagraphCount = s.ParagraphCount, HeadingCount = s.HeadingCount };
    }

    // -------------------------------------------------------------------------
    // Document format/version info
    // -------------------------------------------------------------------------

    /// <summary>R197: Return the MIME type of the document.</summary>
    public string GetMimeType() => "application/vnd.oasis.opendocument.text-flat-xml";

    /// <summary>R197: Return the format identifier.</summary>
    public string GetFormat() => "fodt";

    /// <summary>R197: Return the ODF version string from the document root.</summary>
    public string GetOdfVersion()
    {
        var ver = _doc.Root?.Attribute(
            XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:office:1.0") + "version")?.Value;
        return ver ?? "1.3";
    }

    // -------------------------------------------------------------------------
    // Paragraph accessor operations (R152)
    // -------------------------------------------------------------------------

    /// <summary>R152: Return the FodtParagraph at the given index.</summary>
    public FodtParagraph GetParagraphAt(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return paras[index];
    }

    /// <summary>R152: Delete (remove) the paragraph at the given index.</summary>
    public void DeleteParagraphAt(int index) => RemoveParagraph(index);

    /// <summary>R152: Remove the paragraph at the given index (alias).</summary>
    public void RemoveParagraphAt(int index) => RemoveParagraph(index);

    /// <summary>R152: Insert a paragraph at the given index.</summary>
    public FodtParagraph InsertParagraphAt(int index, string text)
        => InsertParagraph(index, text);

    /// <summary>R152: Move a paragraph from one index to another.</summary>
    public void MoveParagraph(int fromIndex, int toIndex)
    {
        var paras = Paragraphs;
        if (fromIndex < 0 || fromIndex >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(fromIndex));
        if (toIndex < 0 || toIndex > paras.Count)
            throw new ArgumentOutOfRangeException(nameof(toIndex));
        if (fromIndex == toIndex) return;
        var el = paras[fromIndex].Element;
        el.Remove();
        var updatedParas = Paragraphs;
        int insertAt = Math.Min(toIndex, updatedParas.Count);
        if (insertAt == updatedParas.Count)
        {
            var body = _doc.Root?.Element(NsOffice + "body")?.Element(NsOffice + "text");
            body?.Add(el);
        }
        else
        {
            updatedParas[insertAt].Element.AddBeforeSelf(el);
        }
    }

    /// <summary>R152: Trim whitespace from the paragraph at the given index.</summary>
    public void TrimParagraph(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        var el = paras[index].Element;
        var first = el.Nodes().FirstOrDefault() as XText;
        var last = el.Nodes().LastOrDefault() as XText;
        if (first != null) first.Value = first.Value.TrimStart();
        if (last != null && !ReferenceEquals(first, last)) last.Value = last.Value.TrimEnd();
        else if (first != null) first.Value = first.Value.Trim();
    }

    /// <summary>R152: Replace the text of the paragraph at the given index.</summary>
    public void ReplaceParagraphText(int index, string text)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        paras[index].Element.SetValue(text ?? string.Empty);
    }

    // -------------------------------------------------------------------------
    // Heading text/level accessors (R156)
    // -------------------------------------------------------------------------

    /// <summary>R156: Return the text of the heading at the given index in the headings list.</summary>
    public string GetHeadingText(int headingIndex)
    {
        var headings = GetHeadingParagraphs();
        if (headingIndex < 0 || headingIndex >= headings.Count)
            throw new ArgumentOutOfRangeException(nameof(headingIndex));
        return headings[headingIndex].Text ?? string.Empty;
    }

    /// <summary>R156: Return the outline level of the heading at the given index in the headings list.</summary>
    public int GetHeadingLevel(int headingIndex)
    {
        var headings = GetHeadingParagraphs();
        if (headingIndex < 0 || headingIndex >= headings.Count)
            throw new ArgumentOutOfRangeException(nameof(headingIndex));
        var levelAttr = headings[headingIndex].Element.Attribute(NsText + "outline-level")?.Value;
        return int.TryParse(levelAttr, out var l) ? l : 1;
    }

    /// <summary>R156: Set the outline level of the paragraph at the given paragraph index (promotes body paragraphs to headings).</summary>
    public void SetHeadingLevel(int headingIndex, int level)
    {
        var paras = Paragraphs;
        if (headingIndex < 0 || headingIndex >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(headingIndex));
        if (level < 1 || level > 6)
            throw new ArgumentOutOfRangeException(nameof(level));
        paras[headingIndex].Element.SetAttributeValue(NsText + "outline-level", level.ToString());
    }

    /// <summary>R156: Return the outline level of a paragraph in the full paragraph list.</summary>
    public int GetOutlineLevel(int paragraphIndex)
    {
        var paras = Paragraphs;
        if (paragraphIndex < 0 || paragraphIndex >= paras.Count) return 0;
        var para = paras[paragraphIndex];
        if (!para.IsHeading) return 0;
        var levelAttr = para.Element.Attribute(NsText + "outline-level")?.Value;
        return int.TryParse(levelAttr, out var l) ? l : 1;
    }

    // -------------------------------------------------------------------------
    // Style operations (R154)
    // -------------------------------------------------------------------------

    /// <summary>R154: Return the style name of the paragraph at the given index.</summary>
    public string? GetParagraphStyle(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return GetParagraphStyleName(index) ?? "Default";
    }

    /// <summary>R154: Set the style name of the paragraph at the given index.</summary>
    public void SetStyle(int index, string styleName)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        paras[index].Element.SetAttributeValue(NsText + "style-name", styleName);
    }

    /// <summary>R154: Return all distinct style names used in the document.</summary>
    public IReadOnlyList<string> GetStyles()
        => GetParagraphStyles().Where(s => !string.IsNullOrEmpty(s)).Distinct().ToList().AsReadOnly();

    /// <summary>R154: Set the font style on the paragraph at the given index (stored as style-name).</summary>
    public void SetFontStyle(int index, string fontStyle) => SetStyle(index, fontStyle);

    /// <summary>R154: Return paragraph indices matching the given style pattern.</summary>
    public IReadOnlyList<int> GetParagraphsByStyle(string stylePattern)
        => FindParagraphsByStyle(stylePattern);

    // -------------------------------------------------------------------------
    // Document text operations (R157)
    // -------------------------------------------------------------------------

    /// <summary>R157: Count words in the document (alias for GetWordCount).</summary>
    public int CountWords() => GetWordCount();

    /// <summary>R157: Count sentences (approximate: split on . ! ?).</summary>
    public int CountSentences()
    {
        var text = GetPlainText();
        if (string.IsNullOrWhiteSpace(text)) return 0;
        return System.Text.RegularExpressions.Regex.Split(text.Trim(), @"[.!?]+\s+").Length;
    }

    /// <summary>R157: Character count property (alias for CharCount).</summary>
    public int CharacterCount => CharCount;

    /// <summary>R157: Return the top N most common words.</summary>
    public IReadOnlyList<(string Word, int Count)> GetTopWords(int n = 10)
    {
        var freq = GetWordFrequency();
        return freq.OrderByDescending(kv => kv.Value)
                   .Take(n)
                   .Select(kv => (kv.Key, kv.Value))
                   .ToList()
                   .AsReadOnly();
    }

    /// <summary>R157: Return the top N most common words (alias).</summary>
    public IReadOnlyList<(string Word, int Count)> GetMostCommonWords(int n = 10)
        => GetTopWords(n);

    /// <summary>R157: Return all body paragraphs (non-heading) in document order.</summary>
    public List<FodtParagraph> GetBodyParagraphs()
        => Paragraphs.Where(p => !p.IsHeading).ToList();

    /// <summary>R157: Return the plain text of all non-heading paragraphs.</summary>
    public List<string> ExtractPlainParagraphs()
        => GetBodyParagraphs().Select(p => p.Text ?? string.Empty).ToList();

    /// <summary>R157: Find the first paragraph containing the given text (case-sensitive). Returns index or -1.</summary>
    public int FindParagraph(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        var paras = Paragraphs;
        for (int i = 0; i < paras.Count; i++)
            if ((paras[i].Text ?? string.Empty).Contains(text, StringComparison.Ordinal))
                return i;
        return -1;
    }

    /// <summary>R157: Find paragraphs containing the given text — returns (ParagraphIndex, Position) pairs.</summary>
    public List<(int ParagraphIndex, int Position)> Find(string text) => SearchText(text);

    /// <summary>R157: Search for text — returns (ParagraphIndex, Position) pairs (alias for Find).</summary>
    public List<(int ParagraphIndex, int Position)> Search(string text) => SearchText(text);

    // -------------------------------------------------------------------------
    // Page info (R147) — stub (in-memory/unknown from XML)
    // -------------------------------------------------------------------------

    /// <summary>R147: Return the estimated page count (1 for non-empty docs, 0 otherwise).</summary>
    public int GetPageCount() => Math.Max(1, (ParagraphCount + 39) / 40);

    /// <summary>R402: Estimated reading time in minutes at ~200 words/minute (minimum 1).</summary>
    public double GetReadingTimeMinutes()
    {
        int words = GetWordCount();
        return words <= 0 ? 0 : Math.Max(1.0, words / 200.0);
    }

    // Property aliases for test compatibility (R399/R400/R401/R402/R405/R406)
    /// <summary>Property alias for GetHeadingCount().</summary>
    public int HeadingCount => GetHeadingCount();

    /// <summary>R406: Property alias for GetHyperlinkCount().</summary>
    public int HyperlinkCount => GetHyperlinkCount();

    /// <summary>Property alias for GetImageCount().</summary>
    public int ImageCount => GetImageCount();

    /// <summary>Property alias for GetFootnoteCount().</summary>
    public int FootnoteCount => GetFootnoteCount();

    /// <summary>Property alias for GetEndnoteCount().</summary>
    public int EndnoteCount => GetEndnoteCount();

    /// <summary>Property alias for GetCommentCount().</summary>
    public int CommentCount => GetCommentCount();

    /// <summary>Property alias for GetLineCount().</summary>
    public int LineCount => GetLineCount();

    private string _pageOrientation = "portrait";

    /// <summary>R147: Return the page orientation ("portrait" or "landscape").</summary>
    public string GetPageOrientation() => _pageOrientation;

    /// <summary>R147: Set the page orientation.</summary>
    public void SetPageOrientation(string orientation)
        => _pageOrientation = orientation ?? "portrait";

    // -------------------------------------------------------------------------
    // Revision tracking (R169) — in-memory stubs
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // R422-R432 count stubs — all return 0 (in-memory objects only)
    // -------------------------------------------------------------------------

    /// <summary>R410/R412: Return the default body font name from the Standard paragraph style, or empty string if not found.</summary>
    public string GetDefaultFontName()
    {
        var stylesEl = _doc.Root?.Element(NsOffice + "styles");
        if (stylesEl is null) return "Calibri";
        var nsFo = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");
        var nsStyle = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:style:1.0");
        foreach (var style in stylesEl.Elements(nsStyle + "style"))
        {
            var nameAttr = style.Attribute(nsStyle + "name")?.Value;
            if (nameAttr != "Standard" && nameAttr != "Default Style" && nameAttr != "default") continue;
            var textProps = style.Element(nsStyle + "text-properties");
            if (textProps is null) continue;
            var font = textProps.Attribute(nsFo + "font-name")?.Value
                    ?? textProps.Attribute(nsFo + "font-family")?.Value
                    ?? textProps.Attribute(nsStyle + "font-name")?.Value;
            if (!string.IsNullOrEmpty(font)) return font;
        }
        // Fallback: any style:default-style
        foreach (var style in stylesEl.Elements(nsStyle + "default-style"))
        {
            var textProps = style.Element(nsStyle + "text-properties");
            if (textProps is null) continue;
            var font = textProps.Attribute(nsFo + "font-name")?.Value
                    ?? textProps.Attribute(nsFo + "font-family")?.Value
                    ?? textProps.Attribute(nsStyle + "font-name")?.Value;
            if (!string.IsNullOrEmpty(font)) return font;
        }
        return "Calibri";
    }

    /// <summary>R410: Return the default body font size in points from the Standard paragraph style, or 12 if not found.</summary>
    public double GetDefaultFontSize()
    {
        var stylesEl = _doc.Root?.Element(NsOffice + "styles");
        if (stylesEl is null) return 12.0;
        var nsFo = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");
        var nsStyle = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:style:1.0");
        foreach (var style in stylesEl.Elements(nsStyle + "style"))
        {
            var nameAttr = style.Attribute(nsStyle + "name")?.Value;
            if (nameAttr != "Standard" && nameAttr != "Default Style" && nameAttr != "default") continue;
            var textProps = style.Element(nsStyle + "text-properties");
            if (textProps is null) continue;
            var sizeStr = textProps.Attribute(nsFo + "font-size")?.Value;
            if (sizeStr is not null)
            {
                sizeStr = sizeStr.Replace("pt", "").Trim();
                if (double.TryParse(sizeStr, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var pts))
                    return pts;
            }
        }
        return 12.0;
    }

    /// <summary>R169: Accept all tracked changes and return the document (no-op — stub).</summary>
    public FodtDocument AcceptAllChanges() => this;

    // -------------------------------------------------------------------------
    // Header/Footer (R184)
    // -------------------------------------------------------------------------

    // Header/footer DOM helpers
    private static readonly XNamespace _nsStyle = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:style:1.0");

    private XElement EnsureMasterPage()
    {
        var root = _doc.Root!;
        var masterStyles = root.Element(NsOffice + "master-styles");
        if (masterStyles is null)
        {
            masterStyles = new XElement(NsOffice + "master-styles");
            // Insert after automatic-styles if present, else before body
            var autoStyles = root.Element(NsOffice + "automatic-styles");
            if (autoStyles != null)
                autoStyles.AddAfterSelf(masterStyles);
            else
                root.AddFirst(masterStyles);
        }
        var masterPage = masterStyles.Element(_nsStyle + "master-page");
        if (masterPage is null)
        {
            masterPage = new XElement(_nsStyle + "master-page",
                new XAttribute(_nsStyle + "name", "Standard"),
                new XAttribute(_nsStyle + "page-layout-name", "pm1"));
            masterStyles.Add(masterPage);
        }
        return masterPage;
    }

    private string GetHeaderFooterText(string elementName)
    {
        var masterPage = _doc.Root
            ?.Element(NsOffice + "master-styles")
            ?.Element(_nsStyle + "master-page");
        if (masterPage is null) return string.Empty;
        var el = masterPage.Element(_nsStyle + elementName);
        if (el is null) return string.Empty;
        return string.Concat(el.DescendantNodes().OfType<XText>().Select(t => t.Value));
    }

    private void SetHeaderFooterText(string elementName, string text)
    {
        var masterPage = EnsureMasterPage();
        var el = masterPage.Element(_nsStyle + elementName);
        if (el is null)
        {
            el = new XElement(_nsStyle + elementName);
            masterPage.Add(el);
        }
        el.RemoveAll();
        if (!string.IsNullOrEmpty(text))
            el.Add(new XElement(NsText + "p", text));
    }

    /// <summary>R184: Set the header text.</summary>
    public void SetHeader(string text) => SetHeaderFooterText("header", text ?? string.Empty);

    /// <summary>R184: Set the header text (alias for SetHeader).</summary>
    public void SetHeaderText(string text) => SetHeader(text);

    /// <summary>R184: Return the header text.</summary>
    public string GetHeaderText() => GetHeaderFooterText("header");

    /// <summary>R184: Return the header content (alias for GetHeaderText).</summary>
    public string GetHeaderContent() => GetHeaderText();

    /// <summary>R184: Set the footer text.</summary>
    public void SetFooterText(string text) => SetHeaderFooterText("footer", text ?? string.Empty);

    /// <summary>R184: Return the footer text.</summary>
    public string GetFooterText() => GetHeaderFooterText("footer");

    /// <summary>R184: Return the footer content (alias for GetFooterText).</summary>
    public string GetFooterContent() => GetFooterText();

    // -------------------------------------------------------------------------
    // Annotation operations (R186)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Annotation operations (R186) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R186: Return the number of annotations in the document.</summary>
    public int GetAnnotationCount() => GetDomItems("annotation").Count;

    /// <summary>R186: Add an annotation with text only.</summary>
    public void AddAnnotation(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "annotation", text));
    }
}
