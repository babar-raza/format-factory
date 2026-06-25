// FormatFactory.Fodt -- FodtDocument query/analytics methods (partial class).
// Extracted from FodtDocument.cs via TC-NET-H2 (LOC decomposition).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

public sealed partial class FodtDocument
{
    /// <summary>
    /// Return the total word count of the document.
    /// Words are sequences of non-whitespace characters separated by whitespace.
    /// Empty paragraphs contribute zero words. Headings are included.
    /// R94 Train N: text analysis for document inspection.
    /// </summary>
    public int GetWordCount()
    {
        int count = 0;
        foreach (var para in Paragraphs)
        {
            var text = para.Text;
            if (string.IsNullOrWhiteSpace(text)) continue;
            var words = text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
            count += words.Length;
        }
        return count;
    }

    /// <summary>
    /// Return the total character count of the document (all paragraphs including headings).
    /// Only counts non-whitespace and visible characters; whitespace is included.
    /// Empty paragraphs contribute zero characters.
    /// R95 Train M: text analysis complement to GetWordCount.
    /// </summary>
    public int GetCharCount()
    {
        int count = 0;
        foreach (var para in Paragraphs)
        {
            var text = para.Text;
            if (text != null)
                count += text.Length;
        }
        return count;
    }

    /// <summary>
    /// Return the total number of headings (text:h elements) in the document.
    /// Complements GetHeadingParagraphs() for quick count without materializing the list.
    /// R96 Train M: document structure inspection.
    /// </summary>
    public int GetHeadingCount()
    {
        int count = 0;
        foreach (var para in Paragraphs)
        {
            if (para.IsHeading)
                count++;
        }
        return count;
    }

    /// <summary>
    /// Return the total number of paragraphs (including headings) in the document.
    /// Convenience alias for Paragraphs.Count without materializing the full list reference.
    /// R97 Train M: document structure metric.
    /// </summary>
    public int GetParagraphCount() => Paragraphs.Count;

    /// <summary>
    /// Return combined document statistics as a tuple.
    /// (WordCount, CharCount, ParagraphCount, HeadingCount)
    /// R104 Wave 1: bulk statistics for document analysis.
    /// </summary>
    public (int WordCount, int CharCount, int ParagraphCount, int HeadingCount) GetDocumentStats()
    {
        int words = 0, chars = 0, headings = 0;
        var paras = Paragraphs;
        foreach (var para in paras)
        {
            var text = para.Text;
            if (!string.IsNullOrEmpty(text))
            {
                chars += text.Length;
                if (!string.IsNullOrWhiteSpace(text))
                    words += text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
            }
            if (para.IsHeading) headings++;
        }
        return (words, chars, paras.Count, headings);
    }

    /// <summary>
    /// Get the ODF style name (text:style-name attribute) of the paragraph at the given index.
    /// Returns null if the paragraph has no style-name attribute or the index is out of range.
    /// R110 Wave 4: paragraph style inspection for formatting analysis.
    /// </summary>
    public string? GetParagraphStyleName(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count) return null;
        return paras[index].Element.Attribute(NsText + "style-name")?.Value;
    }

    /// <summary>
    /// Return the document outline as a list of (Level, Text) tuples from all heading elements.
    /// Level comes from text:outline-level (defaults to 1 if absent). Text is the heading text.
    /// Useful for generating table-of-contents or structural summaries.
    /// R111 Wave 5: object-model depth for document structure analysis.
    /// </summary>
    public IReadOnlyList<(int Level, string Text)> GetDocumentOutline()
    {
        var result = new List<(int, string)>();
        var paras = Paragraphs;
        foreach (var p in paras)
        {
            if (p.Element.Name.LocalName != "h") continue;
            var levelAttr = p.Element.Attribute(NsText + "outline-level")?.Value;
            int level = int.TryParse(levelAttr, out var l) ? l : 1;
            result.Add((level, p.Text ?? string.Empty));
        }
        return result;
    }

    /// <summary>
    /// Extract document metadata from the office:meta element.
    /// Returns a dictionary with keys like "title", "creator", "date",
    /// "description", "subject", "language", "creation-date", "editing-cycles".
    /// Missing fields are omitted. Returns empty dict if no metadata present.
    /// R113: governed /add-dotnet-api.
    /// </summary>
    public IReadOnlyDictionary<string, string> GetDocumentMetadata()
    {
        var result = new Dictionary<string, string>();
        var metaEl = _doc.Root?.Element(NsOffice + "meta");
        if (metaEl is null) return result;

        // Dublin Core elements
        AddIfPresent(result, "title", metaEl.Element(NsDc + "title"));
        AddIfPresent(result, "creator", metaEl.Element(NsDc + "creator"));
        AddIfPresent(result, "date", metaEl.Element(NsDc + "date"));
        AddIfPresent(result, "description", metaEl.Element(NsDc + "description"));
        AddIfPresent(result, "subject", metaEl.Element(NsDc + "subject"));
        AddIfPresent(result, "language", metaEl.Element(NsDc + "language"));

        // ODF meta elements
        AddIfPresent(result, "creation-date", metaEl.Element(NsMeta + "creation-date"));
        AddIfPresent(result, "editing-cycles", metaEl.Element(NsMeta + "editing-cycles"));
        AddIfPresent(result, "generator", metaEl.Element(NsMeta + "generator"));
        AddIfPresent(result, "initial-creator", metaEl.Element(NsMeta + "initial-creator"));

        return result;
    }

    private static void AddIfPresent(Dictionary<string, string> dict, string key, XElement? el)
    {
        var val = el?.Value;
        if (!string.IsNullOrEmpty(val))
            dict[key] = val;
    }

    /// <summary>
    /// Return the style names of all paragraphs in document order.
    /// Returns an empty string for paragraphs without a style-name attribute.
    /// R114 Train B: paragraph style inspection for formatting analysis.
    /// </summary>
    public IReadOnlyList<string> GetParagraphStyles()
    {
        var paras = Paragraphs;
        var styles = new List<string>(paras.Count);
        foreach (var p in paras)
            styles.Add(p.Element.Attribute(NsText + "style-name")?.Value ?? string.Empty);
        return styles.AsReadOnly();
    }

    /// <summary>
    /// Export the document outline as a JSON string.
    /// Each entry includes paragraph index, style name, text, and heading level (0 if body paragraph).
    /// Heading level is read from text:outline-level attribute (set by <see cref="InsertHeading"/>).
    /// R115 Train A: structured document outline for downstream pipeline integration.
    /// </summary>
    public string ExportToOutlineJson()
    {
        var paragraphs = Paragraphs;
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("[");
        for (int i = 0; i < paragraphs.Count; i++)
        {
            var p = paragraphs[i];
            var styleName = GetParagraphStyleName(i) ?? "";
            var levelAttr = p.Element.Attribute(NsText + "outline-level")?.Value;
            int level = 0;
            if (levelAttr != null && int.TryParse(levelAttr, out int parsed))
                level = parsed;
            else if (styleName.Contains("Heading", StringComparison.OrdinalIgnoreCase) ||
                     styleName.Contains("heading", StringComparison.OrdinalIgnoreCase))
            {
                foreach (char c in styleName)
                    if (char.IsDigit(c)) { level = c - '0'; break; }
                if (level == 0) level = 1;
            }
            var escaped = System.Text.Json.JsonSerializer.Serialize(p.Text ?? "");
            var styleEscaped = System.Text.Json.JsonSerializer.Serialize(styleName);
            sb.Append("  {");
            sb.Append($"\"index\":{i},");
            sb.Append($"\"style\":{styleEscaped},");
            sb.Append($"\"level\":{level},");
            sb.Append($"\"text\":{escaped}");
            sb.Append(i < paragraphs.Count - 1 ? "},\n" : "}\n");
        }
        sb.Append("]");
        return sb.ToString();
    }

    /// <summary>
    /// Return paragraph indices whose style name or element type contains <paramref name="stylePattern"/>
    /// (case-insensitive substring match). For heading elements (text:h), the synthetic style
    /// "Heading" is used when no explicit style-name attribute is set.
    /// R115 Train B: style-based paragraph filter for content extraction pipelines.
    /// </summary>
    public IReadOnlyList<int> FindParagraphsByStyle(string stylePattern)
    {
        ArgumentNullException.ThrowIfNull(stylePattern);
        var result = new List<int>();
        var paragraphs = Paragraphs;
        for (int i = 0; i < paragraphs.Count; i++)
        {
            var explicitStyle = GetParagraphStyleName(i) ?? "";
            var isHeadingElement = paragraphs[i].Element.Name.LocalName == "h";
            var effectiveStyle = explicitStyle.Length > 0 ? explicitStyle
                                 : isHeadingElement ? "Heading" : "";
            if (effectiveStyle.Contains(stylePattern, StringComparison.OrdinalIgnoreCase))
                result.Add(i);
        }
        return result.AsReadOnly();
    }

    /// <summary>
    /// Return a frequency map of words in the document body (case-insensitive, punctuation stripped).
    /// Words shorter than minLength are excluded. R116 Train A: document word frequency analysis.
    /// </summary>
    public IReadOnlyDictionary<string, int> GetWordFrequency(int minLength = 1)
    {
        var freq = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        foreach (var para in Paragraphs)
        {
            var text = para.Text ?? "";
            var words = System.Text.RegularExpressions.Regex.Split(text, @"[\s\p{P}]+");
            foreach (var w in words)
            {
                if (w.Length >= minLength)
                {
                    var key = w.ToLowerInvariant();
                    freq.TryGetValue(key, out int prev);
                    freq[key] = prev + 1;
                }
            }
        }
        return freq;
    }
}
