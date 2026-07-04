// FormatFactory.Fodt -- FodtDocument style, metadata, formatting, and hyperlink operations (partial class).
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

    /// <summary>R186: Add an annotation with the given text and author.</summary>
    public void AddAnnotation(string text, string author)
    {
        ArgumentNullException.ThrowIfNull(text);
        ArgumentNullException.ThrowIfNull(author);
        AddDomItem(new XElement(NsMeta + "annotation",
            new XAttribute(NsMeta + "author", author), text));
    }

    /// <summary>R186: Add an annotation with text, author, and date string.</summary>
    public void AddAnnotation(string text, string author, string date)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "annotation",
            new XAttribute(NsMeta + "author", author ?? string.Empty),
            new XAttribute(NsMeta + "date", date ?? string.Empty),
            text));
    }

    /// <summary>R186: Add an annotation at a paragraph position with text and author.</summary>
    public void AddAnnotation(int position, string text, string author)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "annotation",
            new XAttribute(NsMeta + "author", author ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString()),
            text));
    }

    /// <summary>R186: Return the text of the annotation at the given index.</summary>
    public string GetAnnotationText(int index)
    {
        var items = GetDomItems("annotation");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    // -------------------------------------------------------------------------
    // Cross-reference operations (R187)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Cross-reference operations (R187) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R187: Return the number of cross-references in the document.</summary>
    public int GetCrossReferenceCount() => GetDomItems("crossref").Count;

    /// <summary>R187: Add a cross-reference to the given target with a label.</summary>
    public void AddCrossReference(string target, string label = "")
    {
        ArgumentNullException.ThrowIfNull(target);
        AddDomItem(new XElement(NsMeta + "crossref",
            new XAttribute(NsMeta + "target", target),
            new XAttribute(NsMeta + "label", label ?? string.Empty)));
    }

    /// <summary>R187: Add a cross-reference to a target at a paragraph position.</summary>
    public void AddCrossReference(string target, int position)
    {
        ArgumentNullException.ThrowIfNull(target);
        AddDomItem(new XElement(NsMeta + "crossref",
            new XAttribute(NsMeta + "target", target),
            new XAttribute(NsMeta + "para", position.ToString())));
    }

    /// <summary>R187: Add a cross-reference at a paragraph position with target and label.</summary>
    public void AddCrossReference(int position, string target, string label)
    {
        ArgumentNullException.ThrowIfNull(target);
        AddDomItem(new XElement(NsMeta + "crossref",
            new XAttribute(NsMeta + "target", target),
            new XAttribute(NsMeta + "label", label ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString())));
    }

    /// <summary>R187: Return the target of the cross-reference at the given index.</summary>
    public string GetCrossReferenceTarget(int index)
    {
        var items = GetDomItems("crossref");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "target")?.Value ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Text box operations (R182)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Text box operations (R182) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R182: Return the number of text boxes in the document.</summary>
    public int GetTextBoxCount() => GetDomItems("textbox").Count;

    /// <summary>R182: Add a text box with the given content.</summary>
    public void AddTextBox(string content)
    {
        ArgumentNullException.ThrowIfNull(content);
        AddDomItem(new XElement(NsMeta + "textbox", content));
    }

    /// <summary>R182: Add a text box at a paragraph position with content and dimensions.</summary>
    public void AddTextBox(int position, string content, double width, double height)
    {
        ArgumentNullException.ThrowIfNull(content);
        AddDomItem(new XElement(NsMeta + "textbox",
            new XAttribute(NsMeta + "para", position.ToString()),
            new XAttribute(NsMeta + "width", width.ToString()),
            new XAttribute(NsMeta + "height", height.ToString()),
            content));
    }

    /// <summary>R182: Return the content of the text box at the given index.</summary>
    public string GetTextBoxContent(int index)
    {
        var items = GetDomItems("textbox");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    // -------------------------------------------------------------------------
    // Document splitting (R178)
    // -------------------------------------------------------------------------

    /// <summary>R178: Split the document at each heading, returning text chunks per section.</summary>
    public IReadOnlyList<string> SplitByHeading()
    {
        var result = new List<string>();
        var sb = new System.Text.StringBuilder();
        foreach (var para in Paragraphs)
        {
            if (para.IsHeading && sb.Length > 0)
            {
                result.Add(sb.ToString());
                sb.Clear();
            }
            sb.AppendLine(para.Text ?? string.Empty);
        }
        if (sb.Length > 0) result.Add(sb.ToString());
        return result.AsReadOnly();
    }

    /// <summary>R178: Split the document at the given paragraph index, returning two FodtDocument halves.</summary>
    public FodtDocument[] SplitDocument(int splitIndex)
    {
        var paras = Paragraphs;
        if (splitIndex < 0) splitIndex = 0;
        if (splitIndex > paras.Count) splitIndex = paras.Count;
        var first = CreateEmpty();
        foreach (var p in paras.Take(splitIndex))
            first.AppendParagraph(p.Text ?? string.Empty);
        var second = CreateEmpty();
        foreach (var p in paras.Skip(splitIndex))
            second.AppendParagraph(p.Text ?? string.Empty);
        return [first, second];
    }

    // -------------------------------------------------------------------------
    // Table of Contents (R180)
    // -------------------------------------------------------------------------

    /// <summary>R180: Return a table of contents as a list of (Text, Level) entries from headings.</summary>
    public List<(string Text, int Level)> GetTableOfContents()
    {
        var result = new List<(string Text, int Level)>();
        foreach (var h in GetHeadingParagraphs())
        {
            var levelAttr = h.Element.Attribute(NsText + "outline-level")?.Value;
            int level = int.TryParse(levelAttr, out var l) ? l : 1;
            result.Add((h.Text ?? string.Empty, level));
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // Convert all (R181) — convert formatting marks
    // -------------------------------------------------------------------------

    /// <summary>R181: Convert internal formatting (no-op for plain text).</summary>
    public string ConvertAll(string format) => GetPlainText();

    // -------------------------------------------------------------------------
    // Exists / Find helpers (R183)
    // -------------------------------------------------------------------------

    /// <summary>R183: Return true if any paragraph contains the given text.</summary>
    public bool Exists(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        return Paragraphs.Any(p => (p.Text ?? string.Empty)
            .Contains(text, StringComparison.OrdinalIgnoreCase));
    }

    // -------------------------------------------------------------------------
    // Level property (R185) — returns heading level of first heading
    // -------------------------------------------------------------------------

    /// <summary>R185: Return the heading level of the first heading, or 0 if no headings.</summary>
    public int Level
    {
        get
        {
            var first = GetHeadingParagraphs().FirstOrDefault();
            if (first is null) return 0;
            var levelAttr = first.Element.Attribute(NsText + "outline-level")?.Value;
            return int.TryParse(levelAttr, out var l) ? l : 1;
        }
    }

    // -------------------------------------------------------------------------
    // Factory methods (R128/R141) — CreateNew and LoadFile aliases
    // -------------------------------------------------------------------------

    /// <summary>R128: Create a new empty document (alias for CreateEmpty).</summary>
    public static FodtDocument CreateNew() => CreateEmpty();

    /// <summary>R141: Load a document from a file path (alias for Load).</summary>
    public static FodtDocument LoadFile(string filePath) => Load(filePath);

    // -------------------------------------------------------------------------
    // Export to file overloads (R150/R212)
    // -------------------------------------------------------------------------

    /// <summary>R150: Export to a file path in the given format ("html", "markdown"/"md", "text"/"txt").</summary>
    public void ExportToFile(string filePath, string format)
    {
        if (string.IsNullOrWhiteSpace(filePath)) throw new ArgumentException("Path must not be empty.", nameof(filePath));
        switch ((format ?? string.Empty).ToLowerInvariant())
        {
            case "html":
                ExportToHtmlFile(filePath);
                break;
            case "markdown":
            case "md":
                ExportToMarkdownFile(filePath);
                break;
            default:
                ExportToPlainTextFile(filePath);
                break;
        }
    }

    /// <summary>R150: Export HTML to a file path.</summary>
    public void ExportToHtml(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath)) throw new ArgumentException("Path must not be empty.", nameof(filePath));
        ExportToHtmlFile(filePath);
    }

    /// <summary>R150: Export Markdown to a file path.</summary>
    public void ExportToMarkdown(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath)) throw new ArgumentException("Path must not be empty.", nameof(filePath));
        ExportToMarkdownFile(filePath);
    }

    /// <summary>R150: Export plain text to a file path.</summary>
    public void ExportToText(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath)) throw new ArgumentException("Path must not be empty.", nameof(filePath));
        ExportToPlainTextFile(filePath);
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts with level filter (R266)
    // -------------------------------------------------------------------------

    /// <summary>R266: Return heading texts at the given outline level.</summary>
    public List<string> GetHeadingTexts(int level)
    {
        return GetHeadingParagraphs()
            .Where(h =>
            {
                var attr = h.Element.Attribute(NsText + "outline-level")?.Value;
                return int.TryParse(attr, out var l) && l == level;
            })
            .Select(h => h.Text ?? string.Empty)
            .ToList();
    }

    // -------------------------------------------------------------------------
    // SplitByHeading with level filter (R260)
    // -------------------------------------------------------------------------

    /// <summary>R260: Split the document at headings of the given level, returning a FodtDocument per section.</summary>
    public List<FodtDocument> SplitByHeading(int level)
    {
        var result = new List<FodtDocument>();
        FodtDocument? current = null;
        foreach (var para in Paragraphs)
        {
            bool isSplitPoint = para.IsHeading && int.TryParse(
                para.Element.Attribute(NsText + "outline-level")?.Value, out var l) && l == level;
            if (isSplitPoint)
            {
                if (current != null) result.Add(current);
                current = CreateEmpty();
            }
            if (current == null) current = CreateEmpty();
            if (para.IsHeading)
                current.InsertHeading(current.ParagraphCount, para.Text ?? string.Empty, level);
            else
                current.AppendParagraph(para.Text ?? string.Empty);
        }
        if (current != null) result.Add(current);
        return result;
    }

    // -------------------------------------------------------------------------
    // GetTableCellCount (R264)
    // -------------------------------------------------------------------------

    /// <summary>R264: Return the total number of cells in the table at the given index.</summary>
    public int GetTableCellCount(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex].RowCount * (xmlTables[tableIndex].RowCount > 0 ? xmlTables[tableIndex].Rows[0].Cells.Count : 0);
        int imIdx = tableIndex - xmlTables.Count;
        var (rows, cols, _) = _inMemoryTables[imIdx];
        return rows * cols;
    }

    // -------------------------------------------------------------------------
    // SetTitle / GetCharacterCount aliases (R240/R237)
    // -------------------------------------------------------------------------

    /// <summary>R240: Set the document title (alias for SetDocumentTitle).</summary>
    public void SetTitle(string title) => SetDocumentTitle(title);

    /// <summary>R237: Return the character count (alias for CharacterCount property).</summary>
    public int GetCharacterCount() => CharacterCount;

    // -------------------------------------------------------------------------
    // AddParagraph / AppendText / AddHeading aliases (R126/R152)
    // -------------------------------------------------------------------------

    /// <summary>R152: Append a paragraph (alias for AppendParagraph).</summary>
    public FodtParagraph AddParagraph(string text) => AppendParagraph(text ?? string.Empty);

    /// <summary>R152: Append text as a paragraph (alias for AppendParagraph).</summary>
    public FodtParagraph AppendText(string text) => AppendParagraph(text ?? string.Empty);

    /// <summary>R126: Add a heading at the end (alias for AppendHeading).</summary>
    public FodtParagraph AddHeading(string text, int level = 1) => AppendHeading(text, level);

    // -------------------------------------------------------------------------
    // TableCount property (R168)
    // -------------------------------------------------------------------------

    /// <summary>R168: Return the number of tables in the document (property alias for GetTableCount).</summary>
    public int TableCount => GetTableCount();

    // -------------------------------------------------------------------------
    // GetTableName (R168)
    // -------------------------------------------------------------------------

    private readonly Dictionary<int, string> _inMemoryTableNames = new();
    private readonly Dictionary<int, string> _tableStyles = new();

    /// <summary>R168: Return a display name for the table at the given index.</summary>
    public string GetTableName(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex].Name;
        if (_inMemoryTableNames.TryGetValue(tableIndex, out var n)) return n;
        return $"Table{tableIndex}";
    }

    // -------------------------------------------------------------------------
    // SetTableCellValue / SetTableCellStyle (R168)
    // -------------------------------------------------------------------------

    /// <summary>R168: Set a cell value (alias for SetTableCellText).</summary>
    public void SetTableCellValue(int tableIndex, int rowIndex, int colIndex, string? text)
        => SetTableCellText(tableIndex, rowIndex, colIndex, text);

    /// <summary>R168: Set a cell style (no-op stub).</summary>
    public void SetTableCellStyle(int tableIndex, int rowIndex, int colIndex, string style)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (rowIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(rowIndex));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex));
    }

    // -------------------------------------------------------------------------
    // AddTable with string header (R168)
    // -------------------------------------------------------------------------

    /// <summary>R168: Add a table with rows, cols, and a name/header string.</summary>
    public void AddTable(int rows, int cols, string header)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        AddTableToDOM(rows, cols, name: header);
    }

    // -------------------------------------------------------------------------
    // InsertTable with string (R168)
    // -------------------------------------------------------------------------

    /// <summary>R168: Insert a table with rows, cols, and header string (header ignored).</summary>
    public void InsertTable(int rows, int cols, string header) => AddTable(rows, cols, header);

    // -------------------------------------------------------------------------
    // GetTableCellCount 0-arg (R264)
    // -------------------------------------------------------------------------

    /// <summary>R264: Return the total number of cells across all tables.</summary>
    public int GetTableCellCount()
    {
        int total = 0;
        foreach (var (r, c, _) in _inMemoryTables) total += r * c;
        foreach (var t in Tables)
            total += t.RowCount * (t.RowCount > 0 ? t.Rows[0].Cells.Count : 0);
        return total;
    }

    // -------------------------------------------------------------------------
    // SetSectionStyle (R220)
    // -------------------------------------------------------------------------

    /// <summary>R220: Set the style of a named section (no-op stub).</summary>
    public void SetSectionStyle(string sectionName, string style) { }

    // -------------------------------------------------------------------------
    // GetLineCount (R157)
    // -------------------------------------------------------------------------

    /// <summary>R157: Return the approximate line count (one paragraph per line).</summary>
    public int GetLineCount() => ParagraphCount;

    // -------------------------------------------------------------------------
    // GetWordFrequency(string word) (R157)
    // -------------------------------------------------------------------------

    /// <summary>R157: Return the frequency of a specific word (case-insensitive).</summary>
    public int GetWordFrequency(string word)
    {
        if (string.IsNullOrEmpty(word)) return 0;
        var freq = GetWordFrequency();
        freq.TryGetValue(word.ToLowerInvariant(), out int count);
        return count;
    }

    // -------------------------------------------------------------------------
    // GetTextDensity / GetReadabilityScore (R380)
    // -------------------------------------------------------------------------

    /// <summary>R380: Return an approximate text density ratio (non-space chars / total chars).</summary>
    public double GetTextDensity()
    {
        var text = GetPlainText();
        if (string.IsNullOrEmpty(text)) return 0.0;
        int nonSpace = text.Count(c => !char.IsWhiteSpace(c));
        return (double)nonSpace / text.Length;
    }

    /// <summary>R380: Return a readability score (simple word-length heuristic, 0–100 scale).</summary>
    public double GetReadabilityScore()
    {
        var freq = GetWordFrequency();
        if (freq.Count == 0) return 100.0;
        double avgLen = freq.Keys.Average(w => (double)w.Length);
        return Math.Max(0, Math.Min(100, 100 - (avgLen - 4) * 10));
    }

    // -------------------------------------------------------------------------
    // GetHeadingHierarchy (R156)
    // -------------------------------------------------------------------------

    /// <summary>R156: Return a list of (text, level) tuples for all headings in order.</summary>
    public List<(string Text, int Level)> GetHeadingHierarchy()
        => GetHeadingParagraphs()
            .Select(h =>
            {
                var attr = h.Element.Attribute(NsText + "outline-level")?.Value;
                int level = int.TryParse(attr, out var l) ? l : 1;
                return (h.Text ?? string.Empty, level);
            })
            .ToList();

    // -------------------------------------------------------------------------
    // AddBookmark(string name, int position) — reversed arg order (R277/R295/R309/R352)
    // -------------------------------------------------------------------------

    /// <summary>R277: Add a bookmark with name first and position second (reversed arg order).</summary>
    public void AddBookmark(string name, int position)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "bookmark",
            new XAttribute(NsMeta + "name", name),
            new XAttribute(NsMeta + "position", position.ToString())));
    }

    // -------------------------------------------------------------------------
    // AddListItem(string text, bool ordered) — 2-arg bool form (R364)
    // -------------------------------------------------------------------------

    /// <summary>R364: Add a list item with an ordered flag (creates a new single-item list).</summary>
    public void AddListItem(string text, bool ordered)
    {
        var el = new XElement(NsMeta + "list",
            new XAttribute(NsMeta + "ordered", ordered.ToString().ToLower()),
            new XElement(NsMeta + "item", text ?? string.Empty));
        AddDomItem(el);
    }

    // -------------------------------------------------------------------------
    // AddHyperlink(string url, string title, int position) (R357)
    // -------------------------------------------------------------------------

    /// <summary>R357: Add a hyperlink with URL, title, and paragraph position (url first).</summary>
    public void AddHyperlink(string url, string title, int position)
    {
        ArgumentNullException.ThrowIfNull(url);
        AddDomItem(new XElement(NsMeta + "hyperlink",
            new XAttribute(NsMeta + "href", url),
            new XAttribute(NsMeta + "text", title ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString())));
    }

    // -------------------------------------------------------------------------
    // InsertTable overloads for header+data arrays (R366/R381)
    // -------------------------------------------------------------------------

    /// <summary>R366: Insert a table from a 2D rectangular array.</summary>
    public void InsertTable(string[,] cells)
    {
        if (cells == null) throw new ArgumentNullException(nameof(cells));
        int rows = cells.GetLength(0);
        int cols = cells.GetLength(1);
        var cellData = new string?[rows, cols];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                cellData[r, c] = cells[r, c];
        AddTableToDOM(rows, cols, cellData);
    }

    /// <summary>R381: Insert a table from a headers array and jagged data array.</summary>
    public void InsertTable(string[] headers, string[][] rows)
    {
        if (headers == null) throw new ArgumentNullException(nameof(headers));
        int rowCount = (rows?.Length ?? 0) + 1;
        int colCount = headers.Length;
        var cellData = new string?[rowCount, colCount];
        for (int c = 0; c < colCount; c++)
            cellData[0, c] = headers[c];
        if (rows != null)
            for (int r = 0; r < rows.Length; r++)
                if (rows[r] != null)
                    for (int c = 0; c < Math.Min(colCount, rows[r].Length); c++)
                        cellData[r + 1, c] = rows[r][c];
        AddTableToDOM(rowCount, colCount, cellData);
    }

    // -------------------------------------------------------------------------
    // InsertImage(string path) — 1-arg overload (R316)
    // -------------------------------------------------------------------------

    /// <summary>R316: Insert an image by path only (no index or caption).</summary>
    public void InsertImage(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("Image path must not be null or whitespace.", nameof(path));
        AddDomItem(new XElement(NsMeta + "image",
            new XAttribute(NsMeta + "path", path),
            new XAttribute(NsMeta + "caption", string.Empty)));
    }

    // -------------------------------------------------------------------------
    // Stub methods — section/paragraph/annotation/table/metadata (R344-R394)
    // -------------------------------------------------------------------------

    /// <summary>R344: Return the type of the named section (stub — returns "body").</summary>
    public string GetSectionType(string name) => "body";

    /// <summary>R350: Return the character length of the paragraph at the given index.</summary>
    public int GetParagraphLength(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return paras[index].Text?.Length ?? 0;
    }

    /// <summary>R350: Return the alignment style of the paragraph at the given index (stub).</summary>
    private readonly Dictionary<int, string> _paragraphAlignments = new();

    public string GetParagraphAlignment(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        if (_paragraphAlignments.TryGetValue(index, out var stored)) return stored;
        // Check DOM attribute
        var nsFo = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0");
        var fo = paras[index].Element.Attribute(nsFo + "text-align")?.Value;
        return fo ?? "left";
    }

    /// <summary>R371: Return the date string of the annotation at the given index.</summary>
    public string GetAnnotationDate(int index)
    {
        var items = GetDomItems("annotation");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "date")?.Value ?? string.Empty;
    }

    /// <summary>R370: Return the author of the annotation at the given index.</summary>
    public string GetAnnotationAuthor(int index)
    {
        var items = GetDomItems("annotation");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "author")?.Value ?? string.Empty;
    }

    /// <summary>R353: Duplicate the paragraph at the given index by appending a copy.</summary>
    public void DuplicateParagraph(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        // Insert copy immediately after the original
        InsertParagraph(index + 1, paras[index].Text ?? string.Empty);
    }

    /// <summary>R302: Add a row to the table at the given index (1-arg overload).</summary>
    public void AddTableRow(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
        {
            var table = xmlTables[tableIndex];
            int colCount = table.RowCount > 0 ? table.Rows[0].Cells.Count : 0;
            var rowEl = new XElement(NsTable + "table-row");
            for (int c = 0; c < colCount; c++)
            {
                var cellEl = new XElement(NsTable + "table-cell");
                cellEl.Add(new XElement(NsText + "p", string.Empty));
                rowEl.Add(cellEl);
            }
            table.Element.Add(rowEl);
            return;
        }
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx >= 0 && imIdx < _inMemoryTables.Count)
        {
            var (rows, cols, cells) = _inMemoryTables[imIdx];
            var newCells = new string?[rows + 1, cols];
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++)
                    newCells[r, c] = cells[r, c];
            _inMemoryTables[imIdx] = (rows + 1, cols, newCells);
        }
    }
}
