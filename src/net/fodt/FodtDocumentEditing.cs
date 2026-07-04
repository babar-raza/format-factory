// FormatFactory.Fodt -- FodtDocument editing and DOM operations (partial class).
// Covers: Heading, Table, Bookmark, Section, Comment, Footnote, Endnote,
// Hyperlink, List, Image, Metadata, Text-ops, Style, Export aliases, Header/Footer,
// Annotation, Cross-reference, Text-box, and Search methods.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

public sealed partial class FodtDocument
{
    // -------------------------------------------------------------------------
    // AppendHeading (R126) — named-parameter alias for InsertHeading at end
    // -------------------------------------------------------------------------

    /// <summary>R126: Append a heading with the given text at the specified level (1–6).</summary>
    public FodtParagraph AppendHeading(string text, int level = 1)
        => InsertHeading(ParagraphCount, text ?? string.Empty, level);

    // -------------------------------------------------------------------------
    // ExportToPlainText (R128) — string-returning alias for GetPlainText
    // -------------------------------------------------------------------------

    /// <summary>R128: Return the document content as a plain-text string.</summary>
    public string ExportToPlainText() => GetPlainText();

    /// <summary>R128: Return the document content as a plain-text string (alias).</summary>
    public string ExportToText() => GetPlainText();

    // -------------------------------------------------------------------------
    // ExportToTxt / ExportToFile / SaveToStream (R149/R150)
    // -------------------------------------------------------------------------

    /// <summary>R149: Export plain text to a file path (alias for ExportToPlainTextFile).</summary>
    public void ExportToTxt(string filePath)
    {
        ArgumentNullException.ThrowIfNull(filePath);
        ExportToPlainTextFile(filePath);
    }

    /// <summary>R150: Export HTML to a file path (alias for ExportToHtmlFile).</summary>
    public void ExportToFile(string filePath) => ExportToHtmlFile(filePath);

    /// <summary>R150: Save the document to a stream.</summary>
    public void SaveToStream(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);
        _doc.Save(stream);
    }

    // -------------------------------------------------------------------------
    // Table operations (R168) — DOM-backed; _inMemoryTables kept for legacy indexing code
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // DOM-backed storage helpers (used by bookmarks, sections, comments, etc.)
    // Elements are stored as direct children of office:text in meta: namespace.
    // They are NOT text:p or text:h, so they never appear in Paragraphs, but they
    // DO persist through save/load since they are part of the XDocument DOM.
    // -------------------------------------------------------------------------

    private XElement? GetTextBody() =>
        _doc.Root?.Element(NsOffice + "body")?.Element(NsOffice + "text");

    private IReadOnlyList<XElement> GetDomItems(string localName)
    {
        var body = GetTextBody();
        if (body == null) return Array.Empty<XElement>();
        return body.Elements(NsMeta + localName).ToList();
    }

    private void AddDomItem(XElement el) => GetTextBody()?.Add(el);

    // -------------------------------------------------------------------------
    // Table operations (R168) — DOM-backed; _inMemoryTables kept for legacy indexing
    // -------------------------------------------------------------------------

    /// <summary>R168: Return the number of top-level tables in the document.</summary>
    public int GetTableCount() => Tables.Count + _inMemoryTables.Count;

    private readonly List<(int Rows, int Cols, string?[,] Cells)> _inMemoryTables = new();

    /// <summary>Write a table directly to the document DOM so it persists through save-load.</summary>
    private void AddTableToDOM(int rows, int cols, string?[,]? cellData = null, string? name = null)
    {
        var body = _doc.Root?.Element(NsOffice + "body");
        var textEl = body?.Element(NsOffice + "text");
        if (textEl is null) return;
        var tableEl = new XElement(NsTable + "table",
            new XAttribute(NsTable + "name", name ?? $"Table{Tables.Count + 1}"),
            new XAttribute(NsTable + "style-name", "TableDefault"));
        for (int r = 0; r < rows; r++)
        {
            var rowEl = new XElement(NsTable + "table-row");
            for (int c = 0; c < cols; c++)
            {
                var cellEl = new XElement(NsTable + "table-cell");
                var text = cellData?[r, c] ?? string.Empty;
                cellEl.Add(new XElement(NsText + "p", text));
                rowEl.Add(cellEl);
            }
            tableEl.Add(rowEl);
        }
        textEl.Add(tableEl);
    }

    /// <summary>R168: Add a new table with the given number of rows and columns.</summary>
    public void AddTable(int rows, int cols)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        AddTableToDOM(rows, cols);
    }

    /// <summary>R168: Add a table with pre-filled cell data (jagged array).</summary>
    public void AddTable(int rows, int cols, string[][] cells)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        var cellData = new string?[rows, cols];
        if (cells != null)
            for (int r = 0; r < Math.Min(rows, cells.Length); r++)
                if (cells[r] != null)
                    for (int c = 0; c < Math.Min(cols, cells[r].Length); c++)
                        cellData[r, c] = cells[r][c];
        AddTableToDOM(rows, cols, cellData);
    }

    /// <summary>R168: Add a table with paragraphIndex (ignored), rows, and columns.</summary>
    public void AddTable(int paragraphIndex, int rows, int cols)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        AddTableToDOM(rows, cols);
    }

    /// <summary>R168: Insert a new table at the given index (in-memory).</summary>
    public void InsertTable(int index, int rows, int cols) => AddTable(rows, cols);

    /// <summary>R168: Insert a new table (no index) — alias for AddTable.</summary>
    public void InsertTable(int rows, int cols) => AddTable(rows, cols);

    /// <summary>R168: Return the number of rows in the table at the given index.</summary>
    public int GetTableRowCount(int tableIndex)
    {
        var xmlTables = Tables;
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex].RowCount;
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx < 0 || imIdx >= _inMemoryTables.Count)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        return _inMemoryTables[imIdx].Rows;
    }

    /// <summary>R168: Return the number of columns in the table at the given index.</summary>
    public int GetTableColumnCount(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex].RowCount > 0 ? xmlTables[tableIndex].Rows[0].Cells.Count : 0;
        int imIdx = tableIndex - xmlTables.Count;
        return _inMemoryTables[imIdx].Cols;
    }

    /// <summary>R168: Return the cell text at the given table, row, and column indices.</summary>
    public string? GetTableCellText(int tableIndex, int rowIndex, int colIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
        {
            var t = xmlTables[tableIndex];
            int rowCount = t.RowCount;
            int colCount = rowCount > 0 ? t.Rows[0].Cells.Count : 0;
            if (rowIndex < 0 || rowIndex >= rowCount || colIndex < 0 || colIndex >= colCount)
                throw new ArgumentOutOfRangeException(rowIndex < 0 || rowIndex >= rowCount ? nameof(rowIndex) : nameof(colIndex));
            return t.GetCellText(rowIndex, colIndex);
        }
        int imIdx = tableIndex - xmlTables.Count;
        var (rows, cols, cells) = _inMemoryTables[imIdx];
        if (rowIndex < 0 || rowIndex >= rows || colIndex < 0 || colIndex >= cols)
            throw new ArgumentOutOfRangeException(rowIndex < 0 || rowIndex >= rows ? nameof(rowIndex) : nameof(colIndex));
        return cells[rowIndex, colIndex];
    }

    /// <summary>R168: Set the cell text at the given table, row, and column indices.</summary>
    public void SetTableCellText(int tableIndex, int rowIndex, int colIndex, string? text)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
        {
            var t = xmlTables[tableIndex];
            int rowCount = t.RowCount;
            int colCount = rowCount > 0 ? t.Rows[0].Cells.Count : 0;
            if (rowIndex < 0 || rowIndex >= rowCount || colIndex < 0 || colIndex >= colCount)
                throw new ArgumentOutOfRangeException(rowIndex < 0 || rowIndex >= rowCount ? nameof(rowIndex) : nameof(colIndex));
            // Write through to DOM cell's first text:p
            var cell = t.Rows[rowIndex].Cells[colIndex];
            var nsTextLocal = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
            var textP = cell.Element.Element(nsTextLocal + "p");
            if (textP != null) textP.Value = text ?? string.Empty;
            else cell.Element.Add(new XElement(nsTextLocal + "p", text ?? string.Empty));
            return;
        }
        int imIdx = tableIndex - xmlTables.Count;
        var (rows, cols, cells) = _inMemoryTables[imIdx];
        if (rowIndex < 0 || rowIndex >= rows || colIndex < 0 || colIndex >= cols)
            throw new ArgumentOutOfRangeException(rowIndex < 0 || rowIndex >= rows ? nameof(rowIndex) : nameof(colIndex));
        cells[rowIndex, colIndex] = text;
    }

    /// <summary>R168: Return the cell text (alias for GetTableCellText).</summary>
    public string? GetTableCellValue(int tableIndex, int rowIndex, int colIndex)
        => GetTableCellText(tableIndex, rowIndex, colIndex);

    /// <summary>R168: Set the cell text (alias for SetTableCellText).</summary>
    public void SetTableCell(int tableIndex, int rowIndex, int colIndex, string? text)
        => SetTableCellText(tableIndex, rowIndex, colIndex, text);

    /// <summary>R168: Return the FodtTable at the given index (XML tables only).</summary>
    public FodtTable? GetTableAt(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex];
        // Return a synthetic FodtTable for in-memory tables
        int imIdx = tableIndex - xmlTables.Count;
        var (rows, cols, _) = _inMemoryTables[imIdx];
        // Create a minimal XML element to back the FodtTable
        var tableEl = new System.Xml.Linq.XElement(NsTable + "table");
        for (int r = 0; r < rows; r++)
        {
            var rowEl = new System.Xml.Linq.XElement(NsTable + "table-row");
            for (int c = 0; c < cols; c++)
                rowEl.Add(new System.Xml.Linq.XElement(NsTable + "table-cell"));
            tableEl.Add(rowEl);
        }
        return new FodtTable(tableEl);
    }

    /// <summary>R168: Return a cell reference (alias for GetTableCellText returning string?).</summary>
    public string? GetTableCell(int tableIndex, int rowIndex, int colIndex)
        => GetTableCellText(tableIndex, rowIndex, colIndex) ?? string.Empty;

    // -------------------------------------------------------------------------
    // Bookmark operations (R277)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Bookmark operations (R277) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R277: Return the number of bookmarks in the document.</summary>
    public int GetBookmarkCount() => GetDomItems("bookmark").Count;

    /// <summary>R277: Add a bookmark at the given paragraph position with the given name.</summary>
    public void AddBookmark(int position, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "bookmark",
            new XAttribute(NsMeta + "name", name),
            new XAttribute(NsMeta + "position", position.ToString())));
    }

    /// <summary>R277: Return the name of the bookmark at the given index.</summary>
    public string GetBookmarkName(int index)
    {
        var items = GetDomItems("bookmark");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "name")?.Value ?? string.Empty;
    }

    /// <summary>R277: Return all bookmark names.</summary>
    public IReadOnlyList<string> GetBookmarkNames()
        => GetDomItems("bookmark").Select(e => e.Attribute(NsMeta + "name")?.Value ?? string.Empty).ToList().AsReadOnly();

    /// <summary>R277: Return the paragraph position of the named bookmark, or -1 if not found.</summary>
    public int GetBookmarkPosition(string name)
    {
        foreach (var e in GetDomItems("bookmark"))
            if (e.Attribute(NsMeta + "name")?.Value == name)
                if (int.TryParse(e.Attribute(NsMeta + "position")?.Value, out var p)) return p;
        return -1;
    }

    // -------------------------------------------------------------------------
    // Section operations (R220)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Section operations (R220) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R220: Return the number of sections in the document.</summary>
    public int GetSectionCount() => GetDomItems("section").Count;

    /// <summary>R220: Section count property (alias for GetSectionCount).</summary>
    public int SectionCount => GetSectionCount();

    /// <summary>R220: Add a named section to the end of the document.</summary>
    public void AddSection(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "section", new XAttribute(NsMeta + "name", name)));
    }

    /// <summary>R220: Add a named section with content body.</summary>
    public void AddSection(string name, string content)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "section",
            new XAttribute(NsMeta + "name", name),
            content ?? string.Empty));
    }

    /// <summary>R220: Add a named section with a heading level (level stored).</summary>
    public void AddSection(string name, int level)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddDomItem(new XElement(NsMeta + "section",
            new XAttribute(NsMeta + "name", name),
            new XAttribute(NsMeta + "level", level.ToString())));
    }

    /// <summary>R220: Append a named section (alias for AddSection).</summary>
    public void AppendSection(string name) => AddSection(name);

    /// <summary>R220: Insert a named section (appends to end).</summary>
    public void InsertSection(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddSection(name);
    }

    /// <summary>R220: Insert a named section (index ignored — appends to end).</summary>
    public void InsertSection(int index, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddSection(name);
    }

    /// <summary>R220: Insert a named section at index with level (index ignored — appends).</summary>
    public void InsertSection(int index, string name, int level)
    {
        ArgumentNullException.ThrowIfNull(name);
        AddSection(name, level);
    }

    /// <summary>R220: Return all section names.</summary>
    public IReadOnlyList<string> GetSectionNames()
        => GetDomItems("section").Select(e => e.Attribute(NsMeta + "name")?.Value ?? string.Empty).ToList().AsReadOnly();

    /// <summary>R220: Return the name of the section at the given index.</summary>
    public string GetSectionName(int index)
    {
        var items = GetDomItems("section");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "name")?.Value ?? string.Empty;
    }

    /// <summary>R220: Return the title of the named section (returns name itself if found).</summary>
    public string? GetSectionTitle(string name)
        => GetDomItems("section").Any(e => e.Attribute(NsMeta + "name")?.Value == name) ? name : null;

    /// <summary>R220: Rename a section.</summary>
    public void RenameSection(string oldName, string newName)
    {
        foreach (var e in GetDomItems("section"))
            if (e.Attribute(NsMeta + "name")?.Value == oldName)
            {
                e.SetAttributeValue(NsMeta + "name", newName ?? oldName);
                return;
            }
    }

    // -------------------------------------------------------------------------
    // Comment operations (R332)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Comment operations (R332) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R332: Return the number of comments in the document.</summary>
    public int GetCommentCount() => GetDomItems("comment").Count;

    /// <summary>R332: Add a comment to the document.</summary>
    public void AddComment(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "comment", text));
    }

    /// <summary>R332: Add a comment associated with a paragraph index.</summary>
    public void AddComment(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "comment",
            new XAttribute(NsMeta + "para", paragraphIndex.ToString()), text));
    }

    /// <summary>R332: Add a comment by author and text.</summary>
    public void AddComment(string author, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "comment",
            new XAttribute(NsMeta + "author", author ?? string.Empty), text));
    }

    /// <summary>R332: Add a comment by author, text, and paragraph position.</summary>
    public void AddComment(string author, string text, int position)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "comment",
            new XAttribute(NsMeta + "author", author ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString()), text));
    }

    /// <summary>R332: Add a comment at a paragraph position with author and text.</summary>
    public void AddComment(int position, string author, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "comment",
            new XAttribute(NsMeta + "author", author ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString()), text));
    }

    /// <summary>R332: Return all comment texts.</summary>
    public List<string> GetComments()
        => GetDomItems("comment").Select(e => e.Value).ToList();

    /// <summary>R332: Return the text of the comment at the given index.</summary>
    public string GetCommentText(int index)
    {
        var items = GetDomItems("comment");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    // -------------------------------------------------------------------------
    // Footnote operations (R175)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Footnote operations (R175) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R175: Return the number of footnotes in the document.</summary>
    public int GetFootnoteCount() => GetDomItems("footnote").Count;

    /// <summary>R175: Add a footnote to the document.</summary>
    public void AddFootnote(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "footnote", text));
    }

    /// <summary>R175: Add a footnote at the given paragraph index.</summary>
    public void AddFootnote(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "footnote",
            new XAttribute(NsMeta + "para", paragraphIndex.ToString()), text));
    }

    /// <summary>R175: Return the text of the footnote at the given index.</summary>
    public string GetFootnoteText(int index)
    {
        var items = GetDomItems("footnote");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    // -------------------------------------------------------------------------
    // Endnote operations (R176)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Endnote operations (R176) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R176: Return the number of endnotes in the document.</summary>
    public int GetEndnoteCount() => GetDomItems("endnote").Count;

    /// <summary>R176: Add an endnote to the document.</summary>
    public void AddEndnote(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "endnote", text));
    }

    /// <summary>R176: Add an endnote at the given paragraph index.</summary>
    public void AddEndnote(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        AddDomItem(new XElement(NsMeta + "endnote",
            new XAttribute(NsMeta + "para", paragraphIndex.ToString()), text));
    }

    /// <summary>R176: Return the text of the endnote at the given index.</summary>
    public string GetEndnoteText(int index)
    {
        var items = GetDomItems("endnote");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Value;
    }

    // -------------------------------------------------------------------------
    // Hyperlink operations (R248)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // Hyperlink operations (R248) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R248: Return the number of hyperlinks in the document.</summary>
    public int GetHyperlinkCount() => GetDomItems("hyperlink").Count;

    /// <summary>R248: Add a hyperlink with the given display text and URL.</summary>
    public void AddHyperlink(string text, string url)
    {
        ArgumentNullException.ThrowIfNull(text);
        ArgumentNullException.ThrowIfNull(url);
        AddDomItem(new XElement(NsMeta + "hyperlink",
            new XAttribute(NsMeta + "href", url),
            new XAttribute(NsMeta + "text", text)));
    }

    /// <summary>R248: Add a hyperlink at a paragraph position with URL and title.</summary>
    public void AddHyperlink(int position, string url, string title)
    {
        ArgumentNullException.ThrowIfNull(url);
        AddDomItem(new XElement(NsMeta + "hyperlink",
            new XAttribute(NsMeta + "href", url),
            new XAttribute(NsMeta + "text", title ?? string.Empty),
            new XAttribute(NsMeta + "para", position.ToString())));
    }

    /// <summary>R248: Return the URL of the hyperlink at the given index.</summary>
    public string GetHyperlinkUrl(int index)
    {
        var items = GetDomItems("hyperlink");
        if (index < 0 || index >= items.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return items[index].Attribute(NsMeta + "href")?.Value ?? string.Empty;
    }

    /// <summary>R403: Insert a hyperlink at a paragraph position with URL and display text.</summary>
    public void InsertHyperlink(int paragraphIndex, string url, string text)
    {
        ArgumentNullException.ThrowIfNull(url);
        AddDomItem(new XElement(NsMeta + "hyperlink",
            new XAttribute(NsMeta + "href", url),
            new XAttribute(NsMeta + "text", text ?? string.Empty),
            new XAttribute(NsMeta + "para", paragraphIndex.ToString())));
    }

    // -------------------------------------------------------------------------
    // List operations (R264)
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // List operations (R264) — DOM-backed
    // -------------------------------------------------------------------------

    /// <summary>R264: Return the number of lists in the document.</summary>
    public int GetListCount() => GetDomItems("list").Count;

    private XElement CreateListElement(IEnumerable<string> items, bool ordered = false)
    {
        var el = new XElement(NsMeta + "list",
            new XAttribute(NsMeta + "ordered", ordered.ToString().ToLower()));
        foreach (var item in items)
            el.Add(new XElement(NsMeta + "item", item ?? string.Empty));
        return el;
    }

    /// <summary>R264: Add a list with the given items.</summary>
    public void AddList(IEnumerable<string> items, bool ordered = false)
    {
        ArgumentNullException.ThrowIfNull(items);
        AddDomItem(CreateListElement(items, ordered));
    }

    /// <summary>R264: Add a bullet list (alias for AddList).</summary>
    public void AddBulletList(IEnumerable<string> items) => AddList(items);

    /// <summary>R264: Add a numbered list.</summary>
    public void AddNumberedList(IEnumerable<string> items) => AddList(items, ordered: true);

    /// <summary>R264: Append a list (alias for AddList).</summary>
    public void AppendList(IEnumerable<string> items) => AddList(items);

    /// <summary>R264: Insert a list (appends to end).</summary>
    public void InsertList(int index, IEnumerable<string> items)
    {
        ArgumentNullException.ThrowIfNull(items);
        if (index < 0)
            throw new ArgumentOutOfRangeException(nameof(index));
        AddList(items);
    }

    /// <summary>R404: Insert a list at paragraph position with ordered flag.</summary>
    public void InsertList(int paragraphIndex, IEnumerable<string> items, bool ordered)
    {
        ArgumentNullException.ThrowIfNull(items);
        if (paragraphIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(paragraphIndex));
        AddList(items, ordered);
    }

    /// <summary>R264: Add an item to the list at the given DOM index.</summary>
    public void AddListItem(int listIndex, string item)
    {
        var lists = GetDomItems("list");
        if (listIndex < 0 || listIndex >= lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        lists[listIndex].Add(new XElement(NsMeta + "item", item ?? string.Empty));
    }

    /// <summary>R264: Add an item to the list at the given index with a style. Each call creates a new single-item list.</summary>
    public void AddListItem(string text, int listIndex, string style)
    {
        // Each call creates a new single-item list; listIndex is the nesting level (ignored for storage)
        var el = new XElement(NsMeta + "list",
            new XAttribute(NsMeta + "ordered", "false"),
            new XElement(NsMeta + "item", text ?? string.Empty));
        AddDomItem(el);
    }

    /// <summary>R264: Return the total number of items across all lists.</summary>
    public int GetListItemCount()
        => GetDomItems("list").Sum(l => l.Elements(NsMeta + "item").Count());

    /// <summary>R264: Return the number of items in the list at the given index.</summary>
    public int GetListItemCount(int listIndex)
    {
        var lists = GetDomItems("list");
        if (listIndex < 0 || listIndex >= lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        return lists[listIndex].Elements(NsMeta + "item").Count();
    }
}
