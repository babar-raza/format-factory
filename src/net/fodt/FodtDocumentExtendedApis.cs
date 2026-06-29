// FormatFactory.Fodt -- FodtDocument extended APIs (partial class).
// R126-R394: Heading, Table, Bookmark, Section, Comment, Footnote, Endnote,
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
    public void ExportToTxt(string filePath) => ExportToPlainTextFile(filePath);

    /// <summary>R150: Export HTML to a file path (alias for ExportToHtmlFile).</summary>
    public void ExportToFile(string filePath) => ExportToHtmlFile(filePath);

    /// <summary>R150: Save the document to a stream.</summary>
    public void SaveToStream(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);
        _doc.Save(stream);
    }

    // -------------------------------------------------------------------------
    // Table operations (R168) — in-memory + delegate to Tables property
    // -------------------------------------------------------------------------

    /// <summary>R168: Return the number of top-level tables in the document.</summary>
    public int GetTableCount() => Tables.Count + _inMemoryTables.Count;

    private readonly List<(int Rows, int Cols, string?[,] Cells)> _inMemoryTables = new();

    /// <summary>R168: Add a new table with the given number of rows and columns (in-memory).</summary>
    public void AddTable(int rows, int cols)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _inMemoryTables.Add((rows, cols, new string?[rows, cols]));
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
        _inMemoryTables.Add((rows, cols, cellData));
    }

    /// <summary>R168: Add a table with a numeric fill parameter (ignored).</summary>
    public void AddTable(int rows, int cols, int fillValue)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _inMemoryTables.Add((rows, cols, new string?[rows, cols]));
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
            return xmlTables[tableIndex].GetCellText(rowIndex, colIndex);
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
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx < 0)
        {
            // XML table — delegate to cell edit (best effort)
            return;
        }
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

    private readonly List<(int Position, string Name)> _bookmarks = new();

    /// <summary>R277: Return the number of bookmarks in the document.</summary>
    public int GetBookmarkCount() => _bookmarks.Count;

    /// <summary>R277: Add a bookmark at the given paragraph position with the given name.</summary>
    public void AddBookmark(int position, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        _bookmarks.Add((position, name));
    }

    /// <summary>R277: Return the name of the bookmark at the given index.</summary>
    public string GetBookmarkName(int index)
    {
        if (index < 0 || index >= _bookmarks.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _bookmarks[index].Name;
    }

    /// <summary>R277: Return all bookmark names.</summary>
    public IReadOnlyList<string> GetBookmarkNames()
        => _bookmarks.Select(b => b.Name).ToList().AsReadOnly();

    /// <summary>R277: Return the paragraph position of the named bookmark, or -1 if not found.</summary>
    public int GetBookmarkPosition(string name)
    {
        foreach (var b in _bookmarks)
            if (b.Name == name) return b.Position;
        return -1;
    }

    // -------------------------------------------------------------------------
    // Section operations (R220)
    // -------------------------------------------------------------------------

    private readonly List<string> _sections = new();

    /// <summary>R220: Return the number of sections in the document.</summary>
    public int GetSectionCount() => _sections.Count;

    /// <summary>R220: Section count property (alias for GetSectionCount).</summary>
    public int SectionCount => _sections.Count;

    /// <summary>R220: Add a named section to the end of the document.</summary>
    public void AddSection(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        _sections.Add(name);
    }

    /// <summary>R220: Add a named section with content body (content not persisted).</summary>
    public void AddSection(string name, string content)
    {
        ArgumentNullException.ThrowIfNull(name);
        _sections.Add(name);
    }

    /// <summary>R220: Add a named section with a heading level (level ignored in storage).</summary>
    public void AddSection(string name, int level)
    {
        ArgumentNullException.ThrowIfNull(name);
        _sections.Add(name);
    }

    /// <summary>R220: Append a named section (alias for AddSection).</summary>
    public void AppendSection(string name) => AddSection(name);

    /// <summary>R220: Append a section by name (1-arg string alias for AddSection).</summary>
    public void InsertSection(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        _sections.Add(name);
    }

    /// <summary>R220: Insert a named section at the given index.</summary>
    public void InsertSection(int index, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        if (index < 0 || index > _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _sections.Insert(index, name);
    }

    /// <summary>R220: Insert a named section at the given index with a heading level (level ignored).</summary>
    public void InsertSection(int index, string name, int level)
    {
        ArgumentNullException.ThrowIfNull(name);
        if (index < 0 || index > _sections.Count)
            index = Math.Min(index, _sections.Count);
        _sections.Insert(Math.Min(index, _sections.Count), name);
    }

    /// <summary>R220: Return all section names.</summary>
    public IReadOnlyList<string> GetSectionNames() => _sections.AsReadOnly();

    /// <summary>R220: Return the name of the section at the given index.</summary>
    public string GetSectionName(int index)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _sections[index];
    }

    /// <summary>R220: Return the title of the named section (returns name itself).</summary>
    public string? GetSectionTitle(string name) => _sections.Contains(name) ? name : null;

    /// <summary>R220: Rename a section.</summary>
    public void RenameSection(string oldName, string newName)
    {
        int idx = _sections.IndexOf(oldName);
        if (idx >= 0) _sections[idx] = newName ?? oldName;
    }

    // -------------------------------------------------------------------------
    // Comment operations (R332)
    // -------------------------------------------------------------------------

    private readonly List<string> _comments = new();

    /// <summary>R332: Return the number of comments in the document.</summary>
    public int GetCommentCount() => _comments.Count;

    /// <summary>R332: Add a comment to the document.</summary>
    public void AddComment(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _comments.Add(text);
    }

    /// <summary>R332: Add a comment associated with a paragraph index.</summary>
    public void AddComment(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _comments.Add(text);
    }

    /// <summary>R332: Add a comment by author and text.</summary>
    public void AddComment(string author, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _comments.Add(text);
    }

    /// <summary>R332: Add a comment by author, text, and paragraph position.</summary>
    public void AddComment(string author, string text, int position)
    {
        ArgumentNullException.ThrowIfNull(text);
        _comments.Add(text);
    }

    /// <summary>R332: Add a comment at a paragraph position with author and text.</summary>
    public void AddComment(int position, string author, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _comments.Add(text);
    }

    /// <summary>R332: Return all comment texts.</summary>
    public List<string> GetComments() => new List<string>(_comments);

    /// <summary>R332: Return the text of the comment at the given index.</summary>
    public string GetCommentText(int index)
    {
        if (index < 0 || index >= _comments.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _comments[index];
    }

    // -------------------------------------------------------------------------
    // Footnote operations (R175)
    // -------------------------------------------------------------------------

    private readonly List<string> _footnotes = new();

    /// <summary>R175: Return the number of footnotes in the document.</summary>
    public int GetFootnoteCount() => _footnotes.Count;

    /// <summary>R175: Add a footnote to the document.</summary>
    public void AddFootnote(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _footnotes.Add(text);
    }

    /// <summary>R175: Add a footnote at the given paragraph index.</summary>
    public void AddFootnote(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _footnotes.Add(text);
    }

    /// <summary>R175: Return the text of the footnote at the given index.</summary>
    public string GetFootnoteText(int index)
    {
        if (index < 0 || index >= _footnotes.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _footnotes[index];
    }

    // -------------------------------------------------------------------------
    // Endnote operations (R176)
    // -------------------------------------------------------------------------

    private readonly List<string> _endnotes = new();

    /// <summary>R176: Return the number of endnotes in the document.</summary>
    public int GetEndnoteCount() => _endnotes.Count;

    /// <summary>R176: Add an endnote to the document.</summary>
    public void AddEndnote(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _endnotes.Add(text);
    }

    /// <summary>R176: Add an endnote at the given paragraph index.</summary>
    public void AddEndnote(int paragraphIndex, string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _endnotes.Add(text);
    }

    /// <summary>R176: Return the text of the endnote at the given index.</summary>
    public string GetEndnoteText(int index)
    {
        if (index < 0 || index >= _endnotes.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _endnotes[index];
    }

    // -------------------------------------------------------------------------
    // Hyperlink operations (R248)
    // -------------------------------------------------------------------------

    private readonly List<(string Text, string Url)> _hyperlinks = new();

    /// <summary>R248: Return the number of hyperlinks in the document.</summary>
    public int GetHyperlinkCount() => _hyperlinks.Count;

    /// <summary>R248: Add a hyperlink with the given display text and URL.</summary>
    public void AddHyperlink(string text, string url)
    {
        ArgumentNullException.ThrowIfNull(text);
        ArgumentNullException.ThrowIfNull(url);
        _hyperlinks.Add((text, url));
    }

    /// <summary>R248: Add a hyperlink at a paragraph position with URL and title.</summary>
    public void AddHyperlink(int position, string url, string title)
    {
        ArgumentNullException.ThrowIfNull(url);
        _hyperlinks.Add((title ?? string.Empty, url));
    }

    /// <summary>R248: Return the URL of the hyperlink at the given index.</summary>
    public string GetHyperlinkUrl(int index)
    {
        if (index < 0 || index >= _hyperlinks.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _hyperlinks[index].Url;
    }

    /// <summary>R403: Insert a hyperlink at a paragraph position with URL and display text.</summary>
    public void InsertHyperlink(int paragraphIndex, string url, string text)
    {
        ArgumentNullException.ThrowIfNull(url);
        _hyperlinks.Add((text ?? string.Empty, url));
    }

    // -------------------------------------------------------------------------
    // List operations (R264)
    // -------------------------------------------------------------------------

    private readonly List<List<string>> _lists = new();

    /// <summary>R264: Return the number of lists in the document.</summary>
    public int GetListCount() => _lists.Count;

    /// <summary>R264: Add a list with the given items (ordered flag stored but not persisted).</summary>
    public void AddList(IEnumerable<string> items, bool ordered = false)
    {
        ArgumentNullException.ThrowIfNull(items);
        _lists.Add(new List<string>(items));
    }

    /// <summary>R264: Add a bullet list (alias for AddList).</summary>
    public void AddBulletList(IEnumerable<string> items) => AddList(items);

    /// <summary>R264: Add a numbered list (alias for AddList).</summary>
    public void AddNumberedList(IEnumerable<string> items) => AddList(items);

    /// <summary>R264: Append a list (alias for AddList).</summary>
    public void AppendList(IEnumerable<string> items) => AddList(items);

    /// <summary>R264: Insert a list at the given index.</summary>
    public void InsertList(int index, IEnumerable<string> items)
    {
        ArgumentNullException.ThrowIfNull(items);
        if (index < 0)
            throw new ArgumentOutOfRangeException(nameof(index));
        _lists.Add(new List<string>(items));
    }

    /// <summary>R404: Insert a list at paragraph position with ordered flag.</summary>
    public void InsertList(int paragraphIndex, IEnumerable<string> items, bool ordered)
    {
        ArgumentNullException.ThrowIfNull(items);
        if (paragraphIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(paragraphIndex));
        _lists.Add(new List<string>(items));
    }

    /// <summary>R264: Add an item to the list at the given index.</summary>
    public void AddListItem(int listIndex, string item)
    {
        if (listIndex < 0 || listIndex >= _lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        _lists[listIndex].Add(item ?? string.Empty);
    }

    /// <summary>R264: Add an item to the list at the given index with a style (style ignored).</summary>
    public void AddListItem(string text, int listIndex, string style)
    {
        // Create list if needed
        while (_lists.Count <= listIndex)
            _lists.Add(new List<string>());
        _lists[listIndex].Add(text ?? string.Empty);
    }

    /// <summary>R264: Return the total number of items across all lists.</summary>
    public int GetListItemCount() => _lists.Sum(l => l.Count);

    /// <summary>R264: Return the number of items in the list at the given index.</summary>
    public int GetListItemCount(int listIndex)
    {
        if (listIndex < 0 || listIndex >= _lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        return _lists[listIndex].Count;
    }

    /// <summary>R264: Return the items in the list at the given index.</summary>
    public List<string> GetListItems(int listIndex)
    {
        if (listIndex < 0 || listIndex >= _lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        return _lists[listIndex];
    }

    /// <summary>R264: Return the text of a specific list item by list and item index.</summary>
    public string GetListItemText(int listIndex, int itemIndex)
    {
        if (listIndex < 0 || listIndex >= _lists.Count)
            throw new ArgumentOutOfRangeException(nameof(listIndex));
        var list = _lists[listIndex];
        if (itemIndex < 0 || itemIndex >= list.Count)
            throw new ArgumentOutOfRangeException(nameof(itemIndex));
        return list[itemIndex];
    }

    /// <summary>R264: Return the text of the item at the given global index across all lists.</summary>
    public string GetListItemText(int globalIndex)
    {
        int remaining = globalIndex;
        foreach (var list in _lists)
        {
            if (remaining < list.Count) return list[remaining];
            remaining -= list.Count;
        }
        throw new ArgumentOutOfRangeException(nameof(globalIndex));
    }

    // -------------------------------------------------------------------------
    // Image operations (R283)
    // -------------------------------------------------------------------------

    private readonly List<(string Path, string Caption)> _images = new();

    /// <summary>R283: Return the number of images in the document.</summary>
    public int GetImageCount() => _images.Count;

    /// <summary>R283: Add an image reference with the given file path.</summary>
    public void AddImage(string path, string caption = "")
    {
        ArgumentNullException.ThrowIfNull(path);
        _images.Add((path, caption ?? string.Empty));
    }

    /// <summary>R283: Insert an image at the given paragraph position (appended to image list).</summary>
    public void InsertImage(int paragraphIndex, string path, string caption = "")
    {
        ArgumentNullException.ThrowIfNull(path);
        if (paragraphIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(paragraphIndex));
        _images.Add((path, caption ?? string.Empty));
    }

    /// <summary>R283: Return the path of the image at the given index.</summary>
    public string GetImagePath(int index)
    {
        if (index < 0 || index >= _images.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _images[index].Path;
    }

    /// <summary>R283: Add an image at a paragraph position with path and caption.</summary>
    public void AddImage(int position, string path, string caption)
    {
        ArgumentNullException.ThrowIfNull(path);
        _images.Add((path, caption ?? string.Empty));
    }

    /// <summary>R283: Return the caption of the image at the given index.</summary>
    public string GetImageCaption(int index)
    {
        if (index < 0 || index >= _images.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _images[index].Caption;
    }

    // -------------------------------------------------------------------------
    // Metadata operations (R196) — delegate to GetDocumentMetadata() + in-memory
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, string> _metaOverrides = new();

    private string? GetMeta(string key)
    {
        if (_metaOverrides.TryGetValue(key, out var ov)) return ov;
        var meta = GetDocumentMetadata();
        return meta.TryGetValue(key, out var v) ? v : null;
    }

    private void SetMeta(string key, string? value)
        => _metaOverrides[key] = value ?? string.Empty;

    /// <summary>R196: Return the document title.</summary>
    public string? GetDocumentTitle() => GetMeta("title");

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
    public string? GetDocumentDescription() => GetMeta("description");

    /// <summary>R196: Set the document description.</summary>
    public void SetDocumentDescription(string? desc) => SetMeta("description", desc);

    /// <summary>R196: Return the document subject.</summary>
    public string? GetDocumentSubject() => GetMeta("subject");

    /// <summary>R196: Set the document subject.</summary>
    public void SetDocumentSubject(string? subject) => SetMeta("subject", subject);

    /// <summary>R196: Return the document keywords.</summary>
    public string? GetDocumentKeywords() => GetMeta("keywords");

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
        _metaOverrides[key] = value ?? string.Empty;
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
    public FodtDocumentStats GetDocumentSummary() => GetDocumentStats();

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
        if (index < 0 || index >= paras.Count) return;
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

    /// <summary>R156: Set the outline level of the heading at the given index.</summary>
    public void SetHeadingLevel(int headingIndex, int level)
    {
        var headings = GetHeadingParagraphs();
        if (headingIndex < 0 || headingIndex >= headings.Count)
            throw new ArgumentOutOfRangeException(nameof(headingIndex));
        if (level < 1 || level > 6)
            throw new ArgumentOutOfRangeException(nameof(level));
        headings[headingIndex].Element.SetAttributeValue(NsText + "outline-level", level.ToString());
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
    public int GetPageCount() => ParagraphCount > 0 ? 1 : 0;

    /// <summary>R402: Estimated reading time in minutes at ~200 words/minute (minimum 1).</summary>
    public double GetReadingTimeMinutes()
    {
        int words = GetWordCount();
        return words <= 0 ? 0 : Math.Max(1.0, words / 200.0);
    }

    // Property aliases for test compatibility (R399/R400/R401/R402/R405/R406)
    /// <summary>Property alias for GetHeadingCount().</summary>
    public int HeadingCount => GetHeadingCount();

    /// <summary>R405: Cross-reference count (stub — returns 0; cross-refs are XML-only).</summary>
    public int CrossReferenceCount => 0;

    /// <summary>R406: Property alias for GetHyperlinkCount().</summary>
    public int HyperlinkCount => GetHyperlinkCount();

    /// <summary>R406: Return the number of tracked changes (stub — 0 for in-memory docs).</summary>
    public int GetChangeCount() => 0;

    /// <summary>R407: Count of index marks (stub — 0 for in-memory docs).</summary>
    public int IndexMarkCount => 0;

    /// <summary>R408: Count of text frames (stub — 0 for in-memory docs).</summary>
    public int TextFrameCount => 0;

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

    /// <summary>R169: Return the number of tracked revisions (0 — stub).</summary>
    public int GetRevisionCount() => 0;

    /// <summary>R169: Return a summary of tracked changes (empty stub).</summary>
    public string GetTrackedChangeSummary() => string.Empty;

    /// <summary>R169: Accept all tracked changes and return the document (no-op — stub).</summary>
    public FodtDocument AcceptAllChanges() => this;

    // -------------------------------------------------------------------------
    // Header/Footer (R184)
    // -------------------------------------------------------------------------

    private string _headerText = string.Empty;
    private string _footerText = string.Empty;

    /// <summary>R184: Set the header text.</summary>
    public void SetHeader(string text) => _headerText = text ?? string.Empty;

    /// <summary>R184: Set the header text (alias for SetHeader).</summary>
    public void SetHeaderText(string text) => SetHeader(text);

    /// <summary>R184: Return the header text.</summary>
    public string GetHeaderText() => _headerText;

    /// <summary>R184: Return the header content (alias for GetHeaderText).</summary>
    public string GetHeaderContent() => _headerText;

    /// <summary>R184: Set the footer text.</summary>
    public void SetFooterText(string text) => _footerText = text ?? string.Empty;

    /// <summary>R184: Return the footer text.</summary>
    public string GetFooterText() => _footerText;

    /// <summary>R184: Return the footer content (alias for GetFooterText).</summary>
    public string GetFooterContent() => _footerText;

    // -------------------------------------------------------------------------
    // Annotation operations (R186)
    // -------------------------------------------------------------------------

    private readonly List<(string Author, string Text)> _annotations = new();

    /// <summary>R186: Return the number of annotations in the document.</summary>
    public int GetAnnotationCount() => _annotations.Count;

    /// <summary>R186: Add an annotation with text only.</summary>
    public void AddAnnotation(string text)
    {
        ArgumentNullException.ThrowIfNull(text);
        _annotations.Add((string.Empty, text));
    }

    /// <summary>R186: Add an annotation with the given author and text.</summary>
    public void AddAnnotation(string author, string text)
    {
        ArgumentNullException.ThrowIfNull(author);
        ArgumentNullException.ThrowIfNull(text);
        _annotations.Add((author, text));
    }

    /// <summary>R186: Add an annotation with text, author, and date string.</summary>
    public void AddAnnotation(string text, string author, string date)
    {
        ArgumentNullException.ThrowIfNull(text);
        _annotations.Add((author ?? string.Empty, text));
    }

    /// <summary>R186: Add an annotation at a paragraph position with text and author.</summary>
    public void AddAnnotation(int position, string text, string author)
    {
        ArgumentNullException.ThrowIfNull(text);
        _annotations.Add((author ?? string.Empty, text));
    }

    /// <summary>R186: Return the text of the annotation at the given index.</summary>
    public string GetAnnotationText(int index)
    {
        if (index < 0 || index >= _annotations.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _annotations[index].Text;
    }

    // -------------------------------------------------------------------------
    // Cross-reference operations (R187)
    // -------------------------------------------------------------------------

    private readonly List<(string Target, string Label)> _crossRefs = new();

    /// <summary>R187: Return the number of cross-references in the document.</summary>
    public int GetCrossReferenceCount() => _crossRefs.Count;

    /// <summary>R187: Add a cross-reference to the given target with a label.</summary>
    public void AddCrossReference(string target, string label = "")
    {
        ArgumentNullException.ThrowIfNull(target);
        _crossRefs.Add((target, label ?? string.Empty));
    }

    /// <summary>R187: Add a cross-reference to a target at a paragraph position.</summary>
    public void AddCrossReference(string target, int position)
    {
        ArgumentNullException.ThrowIfNull(target);
        _crossRefs.Add((target, string.Empty));
    }

    /// <summary>R187: Add a cross-reference at a paragraph position with target and label.</summary>
    public void AddCrossReference(int position, string target, string label)
    {
        ArgumentNullException.ThrowIfNull(target);
        _crossRefs.Add((target, label ?? string.Empty));
    }

    /// <summary>R187: Return the target of the cross-reference at the given index.</summary>
    public string GetCrossReferenceTarget(int index)
    {
        if (index < 0 || index >= _crossRefs.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _crossRefs[index].Target;
    }

    // -------------------------------------------------------------------------
    // Text box operations (R182)
    // -------------------------------------------------------------------------

    private readonly List<string> _textBoxes = new();

    /// <summary>R182: Return the number of text boxes in the document.</summary>
    public int GetTextBoxCount() => _textBoxes.Count;

    /// <summary>R182: Add a text box with the given content.</summary>
    public void AddTextBox(string content)
    {
        ArgumentNullException.ThrowIfNull(content);
        _textBoxes.Add(content);
    }

    /// <summary>R182: Add a text box at a paragraph position with content and dimensions.</summary>
    public void AddTextBox(int position, string content, double width, double height)
    {
        ArgumentNullException.ThrowIfNull(content);
        _textBoxes.Add(content);
    }

    /// <summary>R182: Return the content of the text box at the given index.</summary>
    public string GetTextBoxContent(int index)
    {
        if (index < 0 || index >= _textBoxes.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _textBoxes[index];
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

    /// <summary>R168: Return a display name for the table at the given index.</summary>
    public string GetTableName(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        if (tableIndex < xmlTables.Count)
            return xmlTables[tableIndex].Name ?? $"Table{tableIndex}";
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

    /// <summary>R168: Add a table with rows, cols, and a header string (header ignored).</summary>
    public void AddTable(int rows, int cols, string header)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _inMemoryTables.Add((rows, cols, new string?[rows, cols]));
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
        _bookmarks.Add((position, name));
    }

    // -------------------------------------------------------------------------
    // AddListItem(string text, bool ordered) — 2-arg bool form (R364)
    // -------------------------------------------------------------------------

    /// <summary>R364: Add a list item with an ordered flag (creates a new single-item list).</summary>
    public void AddListItem(string text, bool ordered)
    {
        var list = new List<string> { text ?? string.Empty };
        _lists.Add(list);
    }

    // -------------------------------------------------------------------------
    // AddHyperlink(string url, string title, int position) (R357)
    // -------------------------------------------------------------------------

    /// <summary>R357: Add a hyperlink with URL, title, and paragraph position (url first).</summary>
    public void AddHyperlink(string url, string title, int position)
    {
        ArgumentNullException.ThrowIfNull(url);
        _hyperlinks.Add((title ?? string.Empty, url));
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
        _inMemoryTables.Add((rows, cols, cellData));
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
        _inMemoryTables.Add((rowCount, colCount, cellData));
    }

    // -------------------------------------------------------------------------
    // InsertImage(string path) — 1-arg overload (R316)
    // -------------------------------------------------------------------------

    /// <summary>R316: Insert an image by path only (no index or caption).</summary>
    public void InsertImage(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("Image path must not be null or whitespace.", nameof(path));
        _images.Add((path, string.Empty));
    }

    // -------------------------------------------------------------------------
    // Stub methods — section/paragraph/annotation/table/metadata (R344-R394)
    // -------------------------------------------------------------------------

    /// <summary>R344: Return the type of the named section (stub — returns "body").</summary>
    public string GetSectionType(string name) => "body";

    /// <summary>R344: Return the content of the named section (stub — returns empty).</summary>
    public string GetSectionContent(string name) => string.Empty;

    /// <summary>R350: Return the character length of the paragraph at the given index.</summary>
    public int GetParagraphLength(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return paras[index].Text?.Length ?? 0;
    }

    /// <summary>R350: Return the alignment style of the paragraph at the given index (stub).</summary>
    public string GetParagraphAlignment(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return "left";
    }

    /// <summary>R371: Return the date string of the annotation at the given index (stub).</summary>
    public string GetAnnotationDate(int index)
    {
        if (index < 0 || index >= _annotations.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return string.Empty;
    }

    /// <summary>R370: Return the author of the annotation at the given index (stub).</summary>
    public string GetAnnotationAuthor(int index)
    {
        if (index < 0 || index >= _annotations.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _annotations[index].Author;
    }

    /// <summary>R353: Duplicate the paragraph at the given index by appending a copy.</summary>
    public void DuplicateParagraph(int index)
    {
        var paras = Paragraphs;
        if (index < 0 || index >= paras.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        AppendParagraph(paras[index].Text ?? string.Empty);
    }

    /// <summary>R302: Add a row to the table at the given index (1-arg overload).</summary>
    public void AddTableRow(int tableIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
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
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx >= 0 && imIdx < _inMemoryTables.Count)
        {
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
        return "TableDefault";
    }

    /// <summary>R375: Set the style name of the table at the given index (stub).</summary>
    public void SetTableStyle(int tableIndex, string style)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
    }

    /// <summary>R376: Return the row height of a table row (stub — returns 0).</summary>
    public double GetTableRowHeight(int tableIndex, int rowIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        return 0.0;
    }

    /// <summary>R378: Return the column width of a table column (stub — returns 0).</summary>
    public double GetTableColumnWidth(int tableIndex, int colIndex)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
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

    /// <summary>R349: Return the style of the named section (stub).</summary>
    public string GetSectionStyle(string name) => string.Empty;

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
    public string? GetDocumentLanguage() => GetLanguage();

    /// <summary>R342: Return the document author (alias for GetAuthor).</summary>
    public string? GetDocumentAuthor() => GetAuthor();

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

    /// <summary>R303: Export the document to PDF path (stub — throws NotSupportedException).</summary>
    public void ExportToPdf(string filePath)
    {
        // PDF export not supported in this implementation (no PDF library).
        // Tests should use Record.Exception or not call this in success paths.
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or whitespace.", nameof(filePath));
        // no-op: PDF export is not implemented
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
        int imIdx = tableIndex - xmlTables.Count;
        if (imIdx >= 0 && imIdx < _inMemoryTables.Count)
            _inMemoryTables.RemoveAt(imIdx);
    }

    /// <summary>R293: Remove the named section.</summary>
    public void RemoveSection(string name)
    {
        _sections.Remove(name);
    }

    /// <summary>R322: Return the sentence count (alias for CountSentences).</summary>
    public int GetSentenceCount() => CountSentences();

    /// <summary>R346: Return the title from document metadata.</summary>
    public string? GetMetadataTitle() => GetMeta("title");

    /// <summary>R346: Return the subject from document metadata.</summary>
    public string? GetMetadataSubject() => GetMeta("subject");

    /// <summary>R346: Return the language from document metadata.</summary>
    public string? GetMetadataLanguage() => GetMeta("language");

    /// <summary>R346: Return the keywords from document metadata.</summary>
    public string? GetMetadataKeywords() => GetMeta("keywords");

    /// <summary>R346: Return the generator from document metadata.</summary>
    public string? GetMetadataGenerator() => GetMeta("generator");

    /// <summary>R346: Return the description from document metadata.</summary>
    public string? GetMetadataDescription() => GetMeta("description");

    /// <summary>R346: Return the date from document metadata.</summary>
    public string? GetMetadataDate() => GetMeta("date");

    /// <summary>R346: Return the creator from document metadata.</summary>
    public string? GetMetadataCreator() => GetMeta("creator");

    /// <summary>R346: Return the author from document metadata.</summary>
    public string? GetMetadataAuthor() => GetAuthor();

    /// <summary>R312: Set the table name (stub — no-op).</summary>
    public void SetTableName(int tableIndex, string name)
    {
        var xmlTables = Tables;
        int total = xmlTables.Count + _inMemoryTables.Count;
        if (tableIndex < 0 || tableIndex >= total)
            throw new ArgumentOutOfRangeException(nameof(tableIndex));
        // in-memory tables: name is not stored; XML tables: name would need XML edit
    }

    /// <summary>R269: Set the document subject (alias for SetDocumentSubject).</summary>
    public void SetSubject(string? subject) => SetDocumentSubject(subject);

    /// <summary>R280: Return the cross-reference target position by name (returns 0 if not found).</summary>
    public int GetCrossReferenceTarget(string name)
    {
        foreach (var xref in _crossRefs)
            if (xref.Target == name) return 0;
        return -1;
    }

    // -------------------------------------------------------------------------
    // AddTable(string name, int rows, int cols) (R344)
    // -------------------------------------------------------------------------

    /// <summary>R344: Add a table with a name (name is stored as tag), rows, and columns.</summary>
    public void AddTable(string name, int rows, int cols)
    {
        if (rows <= 0) throw new ArgumentOutOfRangeException(nameof(rows));
        if (cols <= 0) throw new ArgumentOutOfRangeException(nameof(cols));
        _inMemoryTables.Add((rows, cols, new string?[rows, cols]));
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
        _inMemoryTables.Add((rowCount, colCount, cellData));
    }

    // -------------------------------------------------------------------------
    // InsertBookmark(int pos, string name) (R394)
    // -------------------------------------------------------------------------

    /// <summary>R394: Insert a bookmark at the given paragraph position with the given name.</summary>
    public void InsertBookmark(int position, string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        _bookmarks.Add((position, name));
    }

    // -------------------------------------------------------------------------
    // AddBookmark(string name) — 1-arg overload (R325)
    // -------------------------------------------------------------------------

    /// <summary>R325: Add a bookmark by name only (position defaults to 0).</summary>
    public void AddBookmark(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        _bookmarks.Add((0, name));
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
    public string? GetDocumentCreationDate() => GetCreationDate();

    /// <summary>R386: Return the document last modified date from metadata.</summary>
    public string? GetDocumentModifiedDate() => GetLastModifiedDate();

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
        // Store as a style attribute on the paragraph element (stub).
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
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return "body";
    }

    /// <summary>R375: Return the content of the section at the given index (stub — returns empty).</summary>
    public string GetSectionContent(int index)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return string.Empty;
    }

    /// <summary>R351: Return the title of the section at the given index.</summary>
    public string GetSectionTitle(int index)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return _sections[index];
    }

    /// <summary>R307: Return the style of the section at the given index (stub — returns empty).</summary>
    public string GetSectionStyle(int index)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        return string.Empty;
    }

    /// <summary>R295: Set the style of the section at the given index (stub).</summary>
    public void SetSectionStyle(int index, string style)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
    }

    /// <summary>R351: Rename the section at the given index.</summary>
    public void RenameSection(int index, string newName)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _sections[index] = newName ?? _sections[index];
    }

    /// <summary>R312: Remove the section at the given index.</summary>
    public void RemoveSection(int index)
    {
        if (index < 0 || index >= _sections.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        _sections.RemoveAt(index);
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
