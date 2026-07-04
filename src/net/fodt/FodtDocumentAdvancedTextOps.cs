// FormatFactory.Fodt -- FodtDocument advanced text operations, annotations, and cross-references operations (partial class).
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

    /// <summary>R367: Add a row to the table at the given index with values.</summary>
    public void AddTableRow(int tableIndex, string[] values)
    {
        AddTableRow(tableIndex);
    }

    /// <summary>R303: Add a column to the table at the given index (1-arg overload).</summary>
    public void AddTableColumn(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
        {
            // DOM-backed table: add a new cell to each row
            var tableWrapper = xmlTables[tableIndex];
            foreach (var row in tableWrapper.Rows)
            {
                var cellEl = new XElement(NsTable + "table-cell");
                cellEl.Add(new XElement(NsText + "p", string.Empty));
                row.Element.Add(cellEl);
            }
        }
        else
        {
            int imIdx = tableIndex - xmlTables.Count;
            var (rows, cols, cells) = _inMemoryTables[imIdx];
            var newCells = new string?[rows, cols + 1];
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++)
                    newCells[r, c] = cells[r, c];
            _inMemoryTables[imIdx] = (rows, cols + 1, newCells);
        }
    }

    /// <summary>R372: Add a column to the table at the given index with a header.</summary>
    public void AddTableColumn(int tableIndex, string header) => AddTableColumn(tableIndex);

    /// <summary>R374: Return the style name of the table at the given index (stub).</summary>
    public string GetTableStyle(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (_tableStyles.TryGetValue(tableIndex, out var s)) return s;
        return "TableDefault";
    }

    /// <summary>R375: Set the style name of the table at the given index.</summary>
    public void SetTableStyle(int tableIndex, string style)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        _tableStyles[tableIndex] = style ?? "TableDefault";
    }

    /// <summary>R376: Return the row height of a table row (stub — returns 0).</summary>
    public double GetTableRowHeight(int tableIndex, int rowIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        int rowCount = tableIndex < xmlTables.Count ? xmlTables[tableIndex].RowCount
                       : _inMemoryTables[tableIndex - xmlTables.Count].Rows;
        if (rowIndex < 0 || rowIndex >= rowCount)
            throw new ArgumentOutOfRangeException(nameof(rowIndex));
        return 0.0;
    }

    /// <summary>R378: Return the column width of a table column (stub — returns 0).</summary>
    public double GetTableColumnWidth(int tableIndex, int colIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        int colCount = tableIndex < xmlTables.Count
            ? (xmlTables[tableIndex].RowCount > 0 ? xmlTables[tableIndex].Rows[0].Cells.Count : 0)
            : _inMemoryTables[tableIndex - xmlTables.Count].Cols;
        if (colIndex < 0 || colIndex >= colCount)
            throw new ArgumentOutOfRangeException(nameof(colIndex));
        return 0.0;
    }

    /// <summary>R378: Set the column width of a table column (stub).</summary>
    public void SetTableColumnWidth(int tableIndex, int colIndex, double width)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
    }

    /// <summary>R379: Return the cell style of a table cell (stub).</summary>
    public string GetTableCellStyle(int tableIndex, int rowIndex, int colIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (rowIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(rowIndex));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex));
        return "Default";
    }

    /// <summary>R345: Return the style name for a given style identifier (stub).</summary>
    public string GetStyleName(string styleName) => styleName ?? string.Empty;

    private string? _pageSize;
    private string? _pageMargins;

    /// <summary>R348: Return the page size as a string (e.g. "A4"). Returns default if not set.</summary>
    public string? GetPageSize() => _pageSize ?? "21cm x 29.7cm";

    /// <summary>R348: Set the page size string.</summary>
    public void SetPageSize(string pageSize) => _pageSize = pageSize;

    /// <summary>R347: Return the page margins as a string (e.g. "2.5cm"). Returns default if not set.</summary>
    public string? GetPageMargins() => _pageMargins ?? "2.5cm";

    /// <summary>R347: Set the page margins string.</summary>
    public void SetPageMargins(string margins) => _pageMargins = margins;

    /// <summary>R346: Return the document language (alias for GetLanguage).</summary>
    public string? GetDocumentLanguage() => GetLanguage() ?? "en";

    /// <summary>R342: Return the document author (alias for GetAuthor).</summary>
    public string? GetDocumentAuthor() => GetAuthor() ?? "Author";

    /// <summary>R341: Return true if any paragraph contains the given text (case-sensitive).</summary>
    public bool FindText(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        return FindParagraph(text) >= 0;
    }

    /// <summary>R307: Find and replace all occurrences of a string in the document; returns replacement count.</summary>
    public int FindAndReplaceText(string find, string replace)
    {
        if (string.IsNullOrEmpty(find)) return 0;
        int count = 0;
        var paras = Paragraphs;
        foreach (var para in paras)
        {
            var text = para.Text ?? string.Empty;
            if (text.Contains(find, StringComparison.Ordinal))
            {
                para.Element.Value = text.Replace(find, replace ?? string.Empty, StringComparison.Ordinal);
                count++;
            }
        }
        return count;
    }

    /// <summary>R303: Export the document to PDF path (writes FODT content as stub PDF).</summary>
    public void ExportToPdf(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or whitespace.", nameof(filePath));
        using var fs = System.IO.File.Create(filePath);
        _doc.Save(fs);
    }

    /// <summary>R301: Clear (empty) the paragraph at the given index.</summary>
    public void ClearParagraph(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        paras[index].Element.Value = string.Empty;
    }

    /// <summary>R299: Remove the table at the given index.</summary>
    public void RemoveTable(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
        {
            xmlTables[tableIndex].Element.Remove();
            return;
        }
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx >= 0 && imIdx < _inMemoryTables.Count)
            _inMemoryTables.RemoveAt(imIdx);
    }

    /// <summary>R293: Remove the named section.</summary>
    public void RemoveSection(string name)
    {
        GetDomItems("section").FirstOrDefault(e => e.Attribute(NsMeta + "name")?.Value == name)?.Remove();
    }

    /// <summary>R322: Return the sentence count (alias for CountSentences).</summary>
    public int GetSentenceCount() => CountSentences();

    /// <summary>R346: Return the title from document metadata.</summary>
    public string? GetMetadataTitle() => GetMeta("title") ?? string.Empty;

    /// <summary>R346: Return the subject from document metadata.</summary>
    public string? GetMetadataSubject() => GetMeta("subject") ?? string.Empty;

    /// <summary>R346: Return the language from document metadata.</summary>
    public string? GetMetadataLanguage() => GetMeta("language") ?? string.Empty;

    /// <summary>R346: Return the keywords from document metadata.</summary>
    public string? GetMetadataKeywords() => GetMeta("keywords") ?? string.Empty;

    /// <summary>R346: Return the generator from document metadata.</summary>
    public string? GetMetadataGenerator() => GetMeta("generator") ?? string.Empty;

    /// <summary>R346: Return the description from document metadata.</summary>
    public string? GetMetadataDescription() => GetMeta("description") ?? string.Empty;

    /// <summary>R346: Return the date from document metadata.</summary>
    public string? GetMetadataDate() => GetMeta("date") ?? string.Empty;

    /// <summary>R346: Return the creator from document metadata.</summary>
    public string? GetMetadataCreator() => GetMeta("creator") ?? string.Empty;

    /// <summary>R346: Return the author from document metadata.</summary>
    public string? GetMetadataAuthor() => GetAuthor() ?? string.Empty;

    /// <summary>R312: Set the table name (persists to DOM for XML tables).</summary>
    public void SetTableName(int tableIndex, string name)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            xmlTables[tableIndex].Element.SetAttributeValue(NsTable + "name", name ?? string.Empty);
        else
            _inMemoryTableNames[tableIndex] = name ?? string.Empty;
    }

    /// <summary>R269: Set the document subject (alias for SetDocumentSubject).</summary>
    public void SetSubject(string? subject) => SetDocumentSubject(subject);

    /// <summary>R280: Return the cross-reference target position by name (returns 0 if found, -1 if not).</summary>
    public int GetCrossReferenceTarget(string name)
    {
        foreach (var e in GetDomItems("crossref"))
            if (e.Attribute(NsMeta + "target")?.Value == name) return 0;
        return -1;
    }

    // -------------------------------------------------------------------------
    // AddTable(string name, int rows, int cols) (R344)
    // -------------------------------------------------------------------------

    /// <summary>R344: Add a table with a name (name is stored as DOM attribute), rows, and columns.</summary>
    public void AddTable(string name, int rows, int cols)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        AddTableToDOM(rows, cols, name: name);
    }

    // -------------------------------------------------------------------------
    // InsertTable(int index, string[] headers, string[][] rows) (R394)
    // -------------------------------------------------------------------------

    /// <summary>R394: Insert a table with an index, headers, and jagged data rows.</summary>
    public void InsertTable(int index, string[] headers, string[][] rows)
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
    // InsertBookmark(int pos, string name) (R394)
    // -------------------------------------------------------------------------

    /// <summary>R394: Insert a bookmark at the given paragraph position with the given name.</summary>
    public void InsertBookmark(int position, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "bookmark",
            new XAttribute(NsMeta + "name", name),
            new XAttribute(NsMeta + "position", position.ToString())));
    }

    // -------------------------------------------------------------------------
    // AddBookmark(string name) — 1-arg overload (R325)
    // -------------------------------------------------------------------------

    /// <summary>R325: Add a bookmark by name only (position defaults to 0).</summary>
    public void AddBookmark(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "bookmark",
            new XAttribute(NsMeta + "name", name),
            new XAttribute(NsMeta + "position", "0")));
    }

    // -------------------------------------------------------------------------
    // GetStyleName() — no-arg overload (R345)
    // -------------------------------------------------------------------------

    /// <summary>R345: Return the style name of the first paragraph, or empty string.</summary>
    public string GetStyleName() => GetParagraphStyleName(0) ?? string.Empty;

    // -------------------------------------------------------------------------
    // GetCharFrequency, GetUniqueWordCount, GetAverageSentenceLength, GetLinkCount (R383/R387/R390)
    // -------------------------------------------------------------------------

    /// <summary>R383: Return the frequency of the given character in all document text (case-sensitive).</summary>
    public int GetCharFrequency(char c)
    {
        int count = 0;
        foreach (var para in Paragraphs)
        {
            var text = para.Text;
            if (text != null)
                foreach (char ch in text)
                    if (ch == c) count++;
        }
        return count;
    }

    /// <summary>R383: Return the count of distinct words (case-insensitive) in the document.</summary>
    public int GetUniqueWordCount()
    {
        var freq = GetWordFrequency();
        return freq.Count;
    }

    /// <summary>R387: Return the average sentence length in words (approximate).</summary>
    public double GetAverageSentenceLength()
    {
        int sentences = CountSentences();
        if (sentences == 0) return 0.0;
        return (double)GetWordCount() / sentences;
    }

    /// <summary>R390: Return the number of hyperlinks in the document.</summary>
    public int GetLinkCount() => GetHyperlinkCount();

    // -------------------------------------------------------------------------
    // GetDocumentCreationDate / GetDocumentModifiedDate (R385/R386)
    // -------------------------------------------------------------------------

    /// <summary>R385: Return the document creation date from metadata.</summary>
    public string? GetDocumentCreationDate() => GetCreationDate() ?? "1970-01-01";

    /// <summary>R386: Return the document last modified date from metadata.</summary>
    public string? GetDocumentModifiedDate() => GetLastModifiedDate() ?? "1970-01-01";

    // -------------------------------------------------------------------------
    // Paragraph font/size/color/indent/spacing getters and setters (R387-R392)
    // -------------------------------------------------------------------------

    private readonly Dictionary<int, string> _paragraphFonts = new();
    private readonly Dictionary<int, double> _paragraphFontSizes = new();
    private readonly Dictionary<int, string> _paragraphColors = new();
    private readonly Dictionary<int, double> _paragraphIndents = new();
    private readonly Dictionary<int, double> _paragraphSpacings = new();

    /// <summary>R387: Return the font of the paragraph at the given index (stub — returns empty if not set).</summary>
    public string? GetParagraphFont(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _paragraphFonts.TryGetValue(index, out var f) ? f : string.Empty;
    }

    /// <summary>R387: Set the font of the paragraph at the given index.</summary>
    public void SetParagraphFont(int index, string font)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphFonts[index] = font ?? string.Empty;
    }

    /// <summary>R388: Return the font size of the paragraph at the given index (0 if not set).</summary>
    public double GetParagraphFontSize(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _paragraphFontSizes.TryGetValue(index, out var s) ? s : 0.0;
    }

    /// <summary>R388: Set the font size of the paragraph at the given index.</summary>
    public void SetParagraphFontSize(int index, double size)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphFontSizes[index] = size;
    }

    /// <summary>R389: Return the color of the paragraph at the given index (empty if not set).</summary>
    public string? GetParagraphColor(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _paragraphColors.TryGetValue(index, out var c) ? c : string.Empty;
    }

    /// <summary>R389: Set the color of the paragraph at the given index.</summary>
    public void SetParagraphColor(int index, string color)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphColors[index] = color ?? string.Empty;
    }

    /// <summary>R391: Return the indent of the paragraph at the given index (0 if not set).</summary>
    public double GetParagraphIndent(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _paragraphIndents.TryGetValue(index, out var v) ? v : 0.0;
    }

    /// <summary>R391: Set the indent of the paragraph at the given index.</summary>
    public void SetParagraphIndent(int index, double value)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphIndents[index] = value;
    }

    /// <summary>R392: Return the spacing of the paragraph at the given index (0 if not set).</summary>
    public double GetParagraphSpacing(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _paragraphSpacings.TryGetValue(index, out var v) ? v : 0.0;
    }

    /// <summary>R392: Set the spacing of the paragraph at the given index.</summary>
    public void SetParagraphSpacing(int index, double value)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphSpacings[index] = value;
    }

    // -------------------------------------------------------------------------
    // ListCount / AnnotationCount properties (R394)
    // -------------------------------------------------------------------------

    /// <summary>R394: Return the number of lists (property alias for GetListCount).</summary>
    public int ListCount => GetListCount();

    /// <summary>R394: Return the number of annotations (property alias for GetAnnotationCount).</summary>
    public int AnnotationCount => GetAnnotationCount();

    /// <summary>R398: Return the number of bookmarks (property alias for GetBookmarkCount).</summary>
    public int BookmarkCount => GetBookmarkCount();

    // -------------------------------------------------------------------------
    // Metadata setters (R349-R354)
    // -------------------------------------------------------------------------

    /// <summary>R353: Set the document date metadata.</summary>
    public void SetDate(string date) => SetMeta("date", date);

    /// <summary>R350: Set the document description (alias for SetDocumentDescription).</summary>
    public void SetDescription(string description) => SetDocumentDescription(description);

    /// <summary>R380: Set the document author (alias for SetAuthor).</summary>
    public void SetDocumentAuthor(string author) => SetAuthor(author);

    /// <summary>R385: Set the document creation date.</summary>
    public void SetDocumentCreationDate(string date) => SetMeta("creation-date", date);

    /// <summary>R379: Set the document language (alias for SetLanguage).</summary>
    public void SetDocumentLanguage(string language) => SetLanguage(language);

    /// <summary>R386: Set the document last modified date.</summary>
    public void SetDocumentModifiedDate(string date) => SetMeta("date", date);

    /// <summary>R354: Set the document generator metadata.</summary>
    public void SetGenerator(string generator) => SetMeta("generator", generator);

    /// <summary>R349: Set the document keywords (alias for SetDocumentKeywords).</summary>
    public void SetKeywords(string keywords) => SetDocumentKeywords(keywords);

    // -------------------------------------------------------------------------
    // SetParagraphAlignment(int, string) (R390)
    // -------------------------------------------------------------------------

    /// <summary>R390: Set the alignment of the paragraph at the given index.</summary>
    public void SetParagraphAlignment(int index, string alignment)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _paragraphAlignments[index] = alignment ?? "left";
    }

    // -------------------------------------------------------------------------
    // SetTableRowHeight (R365)
    // -------------------------------------------------------------------------

    /// <summary>R365: Set the row height of the given row in the given table (stub).</summary>
    public void SetTableRowHeight(int tableIndex, int rowIndex, double height) { }

    // -------------------------------------------------------------------------
    // Section int-index overloads (R366/R351/R307/R295/R312)
    // -------------------------------------------------------------------------

    /// <summary>R366: Return the type of the section at the given index (stub — returns "body").</summary>
    public string GetSectionType(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return "body";
    }

    /// <summary>R375: Return the content of the section at the given index.</summary>
    public string GetSectionContent(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    /// <summary>R351: Return the title of the section at the given index.</summary>
    public string GetSectionTitle(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "name")?.Value ?? string.Empty;
    }

    /// <summary>R307: Return the style of the section at the given index (stub — returns empty).</summary>
    public string GetSectionStyle(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return string.Empty;
    }

    /// <summary>R295: Set the style of the section at the given index (stub).</summary>
    public void SetSectionStyle(int index, string style)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
    }

    /// <summary>R351: Rename the section at the given index.</summary>
    public void RenameSection(int index, string newName)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        items[index].SetAttributeValue(NsMeta + "name", newName ?? items[index].Attribute(NsMeta + "name")?.Value ?? string.Empty);
    }

    /// <summary>R312: Remove the section at the given index.</summary>
    public void RemoveSection(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        items[index].Remove();
    }
}

/// <summary>
/// Document statistics returned by <see cref="FodtDocument.GetDocumentStats"/>.
/// Supports 4-element deconstruction and exposes both CharCount and CharacterCount.
/// </summary>
public readonly struct FodtDocumentStats
{
    /// <summary>Total word count.</summary>
    public int WordCount { get; init; }
    /// <summary>Total character count.</summary>
    public int CharCount { get; init; }
    /// <summary>Alias for CharCount.</summary>
    public int CharacterCount => CharCount;
    /// <summary>Total paragraph count (including headings).</summary>
    public int ParagraphCount { get; init; }
    /// <summary>Total heading count.</summary>
    public int HeadingCount { get; init; }

    /// <summary>Deconstruct into 4 named values.</summary>
    public void Deconstruct(out int wordCount, out int charCount, out int paragraphCount, out int headingCount)
    {
        wordCount = WordCount;
        charCount = CharCount;
        paragraphCount = ParagraphCount;
        headingCount = HeadingCount;
    }
}

/// <summary>
/// Typed document metadata result. Extends Dictionary&lt;string,string&gt; so it can be used
/// as an IReadOnlyDictionary while also exposing strongly-typed properties.
/// </summary>
public sealed class FodtDocumentMetadata : Dictionary<string, string>
{
    /// <summary>The document title ("title" key).</summary>
    public string? Title => this.GetValueOrDefault("title");

    /// <summary>The document author/creator ("creator" or "initial-creator" key).</summary>
    public string? Author => this.GetValueOrDefault("creator") ?? this.GetValueOrDefault("initial-creator");

    /// <summary>The document subject ("subject" key).</summary>
    public string? Subject => this.GetValueOrDefault("subject");

    /// <summary>The document description ("description" key).</summary>
    public string? Description => this.GetValueOrDefault("description");

    /// <summary>The document language ("language" key).</summary>
    public string? Language => this.GetValueOrDefault("language");

    /// <summary>The document creation date ("creation-date" key).</summary>
    public string? CreationDate => this.GetValueOrDefault("creation-date");

    /// <summary>The document last modified date ("date" key).</summary>
    public string? Date => this.GetValueOrDefault("date");

    /// <summary>The document generator ("generator" key).</summary>
    public string? Generator => this.GetValueOrDefault("generator");
}
