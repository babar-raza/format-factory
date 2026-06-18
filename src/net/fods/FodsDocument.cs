// FormatFactory.Fods -- Commercial .NET FODS Document (DOM-backed)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
    // Factory: Load / CreateNew
    // -------------------------------------------------------------------------

    /// <summary>
    /// Create a new, blank FODS document with no sheets.
    /// Call <see cref="AddSheet"/> to add sheets before using the document.
    /// R114 Train A: blank document factory for programmatic construction.
    /// </summary>
    public static FodsDocument CreateNew()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            "  xmlns:style=\"urn:oasis:names:tc:opendocument:xmlns:style:1.0\"" +
            "  office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            "  office:version=\"1.3\">" +
            "  <office:body><office:spreadsheet/></office:body>" +
            "</office:document>";
        var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit };
        using var reader = XmlReader.Create(new System.IO.StringReader(xml), settings);
        var doc = XDocument.Load(reader);
        return new FodsDocument(doc);
    }

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
    /// Number of sheets in the document.
    /// R92 Train B: convenience property.
    /// </summary>
    public int SheetCount => Sheets.Count;

    /// <summary>
    /// Get a sheet by name (case-sensitive). Returns null if not found.
    /// R89 Train B: named sheet access.
    /// </summary>
    public FodsSheet? GetSheetByName(string name)
    {
        foreach (var sheet in Sheets)
        {
            if (sheet.Name == name) return sheet;
        }
        return null;
    }

    /// <summary>
    /// Get a sheet by zero-based index. Returns null if the index is out of range.
    /// R104 Wave 1: index-based sheet access (complements GetSheetByName).
    /// </summary>
    public FodsSheet? GetSheetByIndex(int index)
    {
        var sheets = Sheets;
        if (index < 0 || index >= sheets.Count) return null;
        return sheets[index];
    }

    /// <summary>
    /// Return the names of all sheets in document order.
    /// Returns an empty list if the document has no sheets.
    /// R92 Train L: sheet name enumeration.
    /// </summary>
    public IReadOnlyList<string> GetSheetNames()
    {
        var sheets = Sheets;
        var names = new List<string>(sheets.Count);
        foreach (var sheet in sheets)
            names.Add(sheet.Name);
        return names.AsReadOnly();
    }

    /// <summary>
    /// Add a new empty sheet with the given name.
    /// The sheet is appended to the end of the spreadsheet body.
    /// Throws if a sheet with the same name already exists.
    /// R100 Train B: sheet creation API.
    /// </summary>
    public FodsSheet AddSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(name));

        if (GetSheetByName(name) != null)
            throw new InvalidOperationException($"A sheet named '{name}' already exists.");

        var body = _doc.Root?.Element(NsOffice + "body");
        var spreadsheet = body?.Element(NsOffice + "spreadsheet");
        if (spreadsheet is null)
            throw new InvalidOperationException("Document has no spreadsheet body.");

        var tableElement = new XElement(NsTable + "table",
            new XAttribute(NsTable + "name", name));

        spreadsheet.Add(tableElement);
        return new FodsSheet(tableElement);
    }

    /// <summary>
    /// Remove a sheet by name from the spreadsheet body.
    /// Throws <see cref="InvalidOperationException"/> if no sheet with that name exists.
    /// R101 Train B: sheet management completion (AddSheet exists, RemoveSheet was missing).
    /// </summary>
    public void RemoveSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(name));

        var sheet = GetSheetByName(name);
        if (sheet is null)
            throw new InvalidOperationException($"No sheet named '{name}' exists.");

        sheet.Element.Remove();
    }

    /// <summary>
    /// Rename a sheet from <paramref name="oldName"/> to <paramref name="newName"/>.
    /// Throws if the old name is not found or the new name already exists.
    /// R103 Train A: sheet renaming for workbook management.
    /// </summary>
    public void RenameSheet(string oldName, string newName)
    {
        if (string.IsNullOrWhiteSpace(oldName))
            throw new ArgumentException("Old sheet name must not be null or empty.", nameof(oldName));
        if (string.IsNullOrWhiteSpace(newName))
            throw new ArgumentException("New sheet name must not be null or empty.", nameof(newName));

        var sheet = GetSheetByName(oldName);
        if (sheet is null)
            throw new InvalidOperationException($"No sheet named '{oldName}' exists.");
        if (GetSheetByName(newName) != null)
            throw new InvalidOperationException($"A sheet named '{newName}' already exists.");

        sheet.Element.SetAttributeValue(NsTable + "name", newName);
    }

    /// <summary>
    /// Copy a sheet (deep clone) and add it with the given new name.
    /// Throws if the source sheet is not found or the new name already exists.
    /// R104 Wave 1: sheet duplication for workbook templating.
    /// </summary>
    public FodsSheet CopySheet(string sourceName, string newName)
    {
        if (string.IsNullOrWhiteSpace(sourceName))
            throw new ArgumentException("Source sheet name must not be null or empty.", nameof(sourceName));
        if (string.IsNullOrWhiteSpace(newName))
            throw new ArgumentException("New sheet name must not be null or empty.", nameof(newName));

        var source = GetSheetByName(sourceName);
        if (source is null)
            throw new InvalidOperationException($"No sheet named '{sourceName}' exists.");
        if (GetSheetByName(newName) != null)
            throw new InvalidOperationException($"A sheet named '{newName}' already exists.");

        var body = _doc.Root?.Element(NsOffice + "body");
        var spreadsheet = body?.Element(NsOffice + "spreadsheet");
        if (spreadsheet is null)
            throw new InvalidOperationException("Document has no spreadsheet body.");

        var cloned = new XElement(source.Element);
        cloned.SetAttributeValue(NsTable + "name", newName);
        spreadsheet.Add(cloned);
        return new FodsSheet(cloned);
    }

    /// <summary>
    /// Delete rows from a sheet by zero-based index range [startRow, startRow+count).
    /// Throws if the sheet is not found, or the range is out of bounds.
    /// R105 Wave 2: row management for spreadsheet editing.
    /// </summary>
    public void DeleteRows(string sheetName, int startRow, int count)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (count < 0)
            throw new ArgumentOutOfRangeException(nameof(count), "Count must not be negative.");
        if (count == 0) return;

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (startRow < 0 || startRow + count > rows.Count)
            throw new ArgumentOutOfRangeException(nameof(startRow),
                $"Row range [{startRow}, {startRow + count}) is out of bounds (sheet has {rows.Count} rows).");

        // Collect elements first, then remove (to avoid invalidating indices)
        var toRemove = new List<XElement>(count);
        for (int i = startRow; i < startRow + count; i++)
            toRemove.Add(rows[i].Element);
        foreach (var el in toRemove)
            el.Remove();
    }

    /// <summary>
    /// Insert an empty row at the given zero-based index in the named sheet.
    /// The new row contains no cells. Existing rows at and after the index shift down.
    /// Throws if the sheet is not found or the index is out of range.
    /// R105 Wave 2: row insertion for spreadsheet editing.
    /// </summary>
    public void InsertRow(string sheetName, int rowIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (rowIndex < 0 || rowIndex > rows.Count)
            throw new ArgumentOutOfRangeException(nameof(rowIndex),
                $"Row index {rowIndex} is out of range (sheet has {rows.Count} rows, insert at 0..{rows.Count}).");

        var newRow = new XElement(NsTable + "table-row");
        if (rowIndex < rows.Count)
            rows[rowIndex].Element.AddBeforeSelf(newRow);
        else if (rows.Count > 0)
            rows[^1].Element.AddAfterSelf(newRow);
        else
            sheet.Element.Add(newRow);
    }

    /// <summary>
    /// Return the column headers from the first row of the first sheet.
    /// Assumes that row 0 contains header labels. Returns an empty list if the
    /// document has no sheets or the first row is empty.
    /// R93 Train K: column header extraction.
    /// </summary>
    public IReadOnlyList<string> GetColumnHeaders()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return Array.Empty<string>();
        return GetColumnHeaders(sheets[0]);
    }

    /// <summary>
    /// Return the column headers from the first row of the named sheet.
    /// Returns an empty list if the sheet is not found or its first row is empty.
    /// R93 Train K: column header extraction (named sheet overload).
    /// </summary>
    public IReadOnlyList<string> GetColumnHeaders(string sheetName)
    {
        var sheet = GetSheetByName(sheetName);
        if (sheet == null) return Array.Empty<string>();
        return GetColumnHeaders(sheet);
    }

    /// <summary>
    /// Return the column headers from the first row of <paramref name="sheet"/>.
    /// Returns an empty list if the first row is empty.
    /// R93 Train K.
    /// </summary>
    public static IReadOnlyList<string> GetColumnHeaders(FodsSheet sheet)
    {
        var tableEl = sheet.Element;
        var nsTable = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
        var nsText  = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");

        var firstRow = tableEl.Elements(nsTable + "table-row").FirstOrDefault();
        if (firstRow == null) return Array.Empty<string>();

        var headers = new List<string>();
        foreach (var cell in firstRow.Elements(nsTable + "table-cell"))
        {
            var textParagraph = cell.Element(nsText + "p");
            headers.Add(textParagraph?.Value ?? string.Empty);
        }

        // Remove trailing empty headers
        while (headers.Count > 0 && headers[^1] == string.Empty)
            headers.RemoveAt(headers.Count - 1);

        return headers.AsReadOnly();
    }

    /// <summary>
    /// Get a cell value by zero-based row and column indices from the first sheet.
    /// Returns null if indices are out of range or cell is empty/covered.
    /// R89 Train B: cell-level access.
    /// </summary>
    public string? GetCellValue(int row, int col)
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return null;
        return GetCellValue(sheets[0], row, col);
    }

    /// <summary>
    /// Get a cell value by zero-based row and column indices from a specific sheet.
    /// Returns null if indices are out of range or cell is empty/covered.
    /// R89 Train B: cell-level access.
    /// </summary>
    public static string? GetCellValue(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;
        var cell = r.Cells[col];
        return cell.IsCovered ? null : cell.Value;
    }

    /// <summary>
    /// Set a cell value by zero-based row and column indices on the first sheet.
    /// The row and column must exist within the sheet's existing DOM structure.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if indices are out of range.
    /// R91 Train G: round-trip edit support.
    /// </summary>
    public void SetCellValue(int row, int col, string value)
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new ArgumentOutOfRangeException(nameof(row), "Document has no sheets.");
        SetCellValue(sheets[0], row, col, value);
    }

    /// <summary>
    /// Set a cell value by zero-based row and column indices on a specific sheet.
    /// The row and column must exist within the sheet's existing DOM structure.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if indices are out of range.
    /// R91 Train G: round-trip edit support.
    /// </summary>
    public static void SetCellValue(FodsSheet sheet, int row, int col, string value)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(value);
        if (row < 0 || row >= sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count)
            throw new ArgumentOutOfRangeException(nameof(col),
                $"Column {col} is out of range (row has {r.Cells.Count} cells).");
        r.Cells[col].SetText(value);
    }

    /// <summary>
    /// Export a sheet as an HTML table string. Uses the first sheet if no sheet specified.
    /// Rows become &lt;tr&gt; elements, cells become &lt;td&gt; elements.
    /// Empty cells produce empty &lt;td&gt; elements. Cell text is HTML-escaped.
    /// R94 Train M: HTML export for dogfood pipeline.
    /// </summary>
    public string ExportSheetToHtml()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToHtml(sheets[0]);
    }

    /// <summary>
    /// Export a named sheet as an HTML table string.
    /// R94 Train M: HTML export for dogfood pipeline.
    /// </summary>
    public string ExportSheetToHtml(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToHtml(sheet);
    }

    /// <summary>
    /// Export a specific sheet as an HTML table string.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToHtml"/>.
    /// R94 Train M: HTML export for dogfood pipeline.
    /// </summary>
    public static string ExportSheetToHtml(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToHtml(sheet);

    /// <summary>
    /// Return the number of rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// R96 Train L: row count query for data inspection.
    /// </summary>
    public int GetRowCount()
    {
        var sheets = Sheets;
        return sheets.Count == 0 ? 0 : sheets[0].Rows.Count;
    }

    /// <summary>
    /// Return the number of rows in the named sheet.
    /// Throws if the sheet is not found.
    /// R96 Train L: row count query (named sheet overload).
    /// </summary>
    public int GetRowCount(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return sheet.Rows.Count;
    }

    /// <summary>
    /// Return the maximum number of columns (cells in any single row) in the named sheet.
    /// Returns 0 if the sheet has no rows.
    /// R108 Lane C: column count for data structure analysis.
    /// </summary>
    public int GetColumnCount(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        int maxCols = 0;
        foreach (var row in sheet.Rows)
        {
            int cellCount = row.Cells.Count;
            if (cellCount > maxCols) maxCols = cellCount;
        }
        return maxCols;
    }

    /// <summary>
    /// Return the maximum number of columns in the first sheet.
    /// Returns 0 if the document has no sheets or the first sheet has no rows.
    /// R108 Lane C: column count for data structure analysis.
    /// </summary>
    public int GetColumnCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        var name = sheets[0].Name;
        return name != null ? GetColumnCount(name) : 0;
    }

    /// <summary>
    /// Return the total number of cells across all rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// R97 Train L: cell count for data density analysis.
    /// </summary>
    public int GetCellCount()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return 0;
        int count = 0;
        foreach (var row in sheets[0].Rows)
            count += row.Cells.Count;
        return count;
    }

    /// <summary>
    /// Return all cell values from a given row in the first sheet as a list of strings.
    /// Returns null values for empty or covered cells.
    /// Throws if the row index is out of range.
    /// R102 Train A: row-level data extraction for export pipelines.
    /// </summary>
    public IReadOnlyList<string?> GetRowValues(int row)
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new ArgumentOutOfRangeException(nameof(row), "Document has no sheets.");
        return GetRowValues(sheets[0], row);
    }

    /// <summary>
    /// Return all cell values from a given row in the named sheet.
    /// R102 Train A: row-level data extraction (named sheet overload).
    /// </summary>
    public IReadOnlyList<string?> GetRowValues(string sheetName, int row)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return GetRowValues(sheet, row);
    }

    /// <summary>
    /// Return all cell values from a given row in the specified sheet.
    /// R102 Train A: row-level data extraction (static overload).
    /// </summary>
    public static IReadOnlyList<string?> GetRowValues(FodsSheet sheet, int row)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0 || row >= sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
        var cells = sheet.Rows[row].Cells;
        var values = new List<string?>(cells.Count);
        foreach (var cell in cells)
            values.Add(cell.IsCovered ? null : cell.Value);
        return values.AsReadOnly();
    }

    /// <summary>
    /// Export a sheet as a JSON array of row objects.
    /// The first row is treated as headers; subsequent rows become objects keyed by those headers.
    /// If the sheet has zero or one row, returns "[]".
    /// R95 Train L: JSON export for data interchange pipeline.
    /// </summary>
    public string ExportSheetToJson()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToJson(sheets[0]);
    }

    /// <summary>
    /// Export a named sheet as a JSON array of row objects.
    /// R95 Train L: JSON export (named sheet overload).
    /// </summary>
    public string ExportSheetToJson(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToJson(sheet);
    }

    /// <summary>
    /// Export a specific sheet as a JSON array of row objects.
    /// First row = header keys; subsequent rows = value objects.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToJson"/>.
    /// R95 Train L: JSON export (static overload).
    /// </summary>
    public static string ExportSheetToJson(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToJson(sheet);

    /// <summary>
    /// Export a sheet as a Markdown table string.
    /// The first row is treated as headers with a separator line beneath.
    /// Pipe characters in cell values are escaped as \|.
    /// Returns an empty string if the sheet has no rows.
    /// R101 Train A: Markdown export for documentation pipeline.
    /// </summary>
    public string ExportSheetToMarkdown()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToMarkdown(sheets[0]);
    }

    /// <summary>
    /// Export a named sheet as a Markdown table string.
    /// R101 Train A: Markdown export (named sheet overload).
    /// </summary>
    public string ExportSheetToMarkdown(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToMarkdown(sheet);
    }

    /// <summary>
    /// Export a specific sheet as a Markdown table string.
    /// First row = headers; separator line = dashes; subsequent rows = data.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToMarkdown"/>.
    /// R101 Train A: Markdown export (static overload).
    /// </summary>
    public static string ExportSheetToMarkdown(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToMarkdown(sheet);

    /// <summary>
    /// Remove all rows from the named sheet, leaving it empty.
    /// Throws if the sheet is not found.
    /// R106 Wave 2: sheet clearing for spreadsheet editing.
    /// </summary>
    public void ClearSheet(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (rows.Count == 0) return;

        var toRemove = new List<XElement>(rows.Count);
        foreach (var row in rows)
            toRemove.Add(row.Element);
        foreach (var el in toRemove)
            el.Remove();
    }

    /// <summary>
    /// Return all cell values from the specified column (zero-based) across all rows
    /// in the named sheet. Returns null for cells that are empty or missing.
    /// Throws if the sheet is not found or the column index is negative.
    /// R106 Wave 2: column extraction for data analysis workflows.
    /// </summary>
    public IReadOnlyList<string?> GetColumnValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0)
            throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");

        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var result = new List<string?>();
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col < cells.Count)
            {
                var textP = cells[col].Element(nsText + "p");
                result.Add(textP?.Value);
            }
            else
            {
                result.Add(null);
            }
        }
        return result;
    }

    /// <summary>
    /// Return numeric (float) cell values from the given column in the named sheet.
    /// Reads office:value-type="float" cells and returns their office:value attribute as double.
    /// Cells with no value, non-numeric type, or out-of-range column index are skipped.
    /// Spec: FACT-FODS-006 (table:table-cell), FACT-FODS-010 (office:value-type float).
    /// R100 Wave 5: numeric column extraction for data analysis.
    /// </summary>
    public IReadOnlyList<double> GetNumericColumnValues(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (col < 0)
            throw new ArgumentOutOfRangeException(nameof(col), "Column index must not be negative.");

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");

        var result = new List<double>();
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col >= cells.Count) continue;
            var cell = cells[col];
            var vtype = cell.Attribute(NsOffice + "value-type")?.Value;
            if (vtype != "float" && vtype != "currency" && vtype != "percentage") continue;
            var raw = cell.Attribute(NsOffice + "value")?.Value;
            if (raw is not null && double.TryParse(raw, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var d))
                result.Add(d);
        }
        return result;
    }

    /// <summary>
    /// Export a sheet as CSV (comma-separated values).
    /// Each row becomes a line, cells are comma-separated, values containing commas/quotes/newlines
    /// are enclosed in double quotes with internal quotes doubled (RFC 4180).
    /// R107 Wave 2: CSV export for data interchange and dogfood pipeline.
    /// </summary>
    public string ExportSheetToCsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return ExportSheetToCsv(sheet);
    }

    /// <summary>
    /// Export the first sheet as CSV.
    /// R107 Wave 2: CSV export (default sheet overload).
    /// </summary>
    public string ExportSheetToCsv()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToCsv(sheets[0]);
    }

    /// <summary>
    /// Export a specific sheet as CSV.
    /// Delegates to <see cref="FodsDocumentExporter.ExportSheetToCsv"/>.
    /// R107 Wave 2: CSV export (static overload).
    /// </summary>
    public static string ExportSheetToCsv(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToCsv(sheet);

    /// <summary>
    /// Insert a new row at the given index with the specified cell values.
    /// Creates a table-row element with table-cell elements containing text:p for each value.
    /// Null values produce empty cells. Existing rows at and after the index shift down.
    /// R107 Wave 2: populated row insertion for spreadsheet editing workflows.
    /// </summary>
    public void InsertRowWithValues(string sheetName, int rowIndex, IReadOnlyList<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (rowIndex < 0 || rowIndex > rows.Count)
            throw new ArgumentOutOfRangeException(nameof(rowIndex),
                $"Row index {rowIndex} is out of range (sheet has {rows.Count} rows, insert at 0..{rows.Count}).");

        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var newRow = new XElement(NsTable + "table-row");
        foreach (var val in values)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (val != null)
                cell.Add(new XElement(nsText + "p", val));
            newRow.Add(cell);
        }

        if (rowIndex < rows.Count)
            rows[rowIndex].Element.AddBeforeSelf(newRow);
        else if (rows.Count > 0)
            rows[^1].Element.AddAfterSelf(newRow);
        else
            sheet.Element.Add(newRow);
    }

    /// <summary>
    /// Check whether a sheet with the given name exists in the document.
    /// Returns true if found, false otherwise.
    /// R109 Lane C: sheet existence check for defensive programming.
    /// </summary>
    public bool HasSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            return false;
        return GetSheetByName(name) != null;
    }

    /// <summary>
    /// Return the ODF value-type of a cell (e.g. "string", "float", "date").
    /// Reads the office:value-type attribute from the table-cell element.
    /// Returns null if the cell has no value-type attribute or indices are out of range.
    /// R110 Wave 4: cell metadata inspection for data analysis.
    /// </summary>
    public string? GetCellDataType(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;

        return r.Cells[col].Element.Attribute(NsOffice + "value-type")?.Value;
    }

    /// <summary>
    /// Search all cells in the named sheet for the given text value.
    /// Returns a list of (Row, Col) tuples for every cell whose text content matches exactly.
    /// The comparison is ordinal (case-sensitive). Returns an empty list if no matches found.
    /// Throws if the sheet is not found.
    /// R110 Wave 4: cell search for data lookup and validation.
    /// </summary>
    public IReadOnlyList<(int Row, int Col)> FindCellsByValue(string sheetName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(value);

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");

        var results = new List<(int, int)>();
        var rows = sheet.Rows;
        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Cells;
            for (int c = 0; c < cells.Count; c++)
            {
                if (!cells[c].IsCovered && cells[c].Value == value)
                    results.Add((r, c));
            }
        }
        return results;
    }

    /// <summary>
    /// Merge a rectangular range of cells in the specified sheet.
    /// Sets table:number-columns-spanned and table:number-rows-spanned on the top-left cell,
    /// and replaces spanned cells with table:covered-table-cell elements.
    /// ODF spec: §9.4.5 table:table-cell merge attributes.
    /// R111 Wave 5: object-model depth for cell merge operations.
    /// </summary>
    public void MergeCells(string sheetName, int startRow, int startCol, int rowSpan, int colSpan)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowSpan < 1)
            throw new ArgumentOutOfRangeException(nameof(rowSpan), "Row span must be at least 1.");
        if (colSpan < 1)
            throw new ArgumentOutOfRangeException(nameof(colSpan), "Column span must be at least 1.");

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (startRow < 0 || startRow + rowSpan > rows.Count)
            throw new ArgumentOutOfRangeException(nameof(startRow),
                $"Merge range rows [{startRow}..{startRow + rowSpan - 1}] exceeds sheet row count {rows.Count}.");

        // Set span attributes on the anchor cell
        var anchorRow = rows[startRow];
        if (startCol < 0 || startCol + colSpan > anchorRow.Cells.Count)
            throw new ArgumentOutOfRangeException(nameof(startCol),
                $"Merge range cols [{startCol}..{startCol + colSpan - 1}] exceeds row cell count {anchorRow.Cells.Count}.");

        var anchorCell = anchorRow.Cells[startCol];
        anchorCell.Element.SetAttributeValue(NsTable + "number-columns-spanned", colSpan.ToString());
        anchorCell.Element.SetAttributeValue(NsTable + "number-rows-spanned", rowSpan.ToString());

        // Replace covered cells with covered-table-cell elements
        for (int r = startRow; r < startRow + rowSpan; r++)
        {
            var rowCells = rows[r].Cells;
            for (int c = startCol; c < startCol + colSpan; c++)
            {
                if (r == startRow && c == startCol) continue; // skip anchor
                if (c < rowCells.Count)
                {
                    var cellEl = rowCells[c].Element;
                    cellEl.ReplaceWith(new XElement(NsTable + "covered-table-cell"));
                }
            }
        }
    }

    /// <summary>
    /// Set a formula expression on a cell.
    /// Writes the table:formula attribute (e.g., "of:=SUM([.A1:.A10])") on the cell element.
    /// ODF spec: §9.4.6 table:formula attribute.
    /// R111 Wave 5: object-model depth for formula editing workflows.
    /// </summary>
    public void SetCellFormula(string sheetName, int row, int col, string formula)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(formula);

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var rows = sheet.Rows;
        if (row < 0 || row >= rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {rows.Count} rows).");
        var r = rows[row];
        if (col < 0 || col >= r.Cells.Count)
            throw new ArgumentOutOfRangeException(nameof(col),
                $"Column {col} is out of range (row has {r.Cells.Count} cells).");

        r.Cells[col].Element.SetAttributeValue(NsTable + "formula", formula);
    }

    /// <summary>
    /// Get the formula expression from a cell, or null if no formula is set.
    /// Reads the table:formula attribute from the cell element.
    /// R111 Wave 5: complement to SetCellFormula for formula inspection.
    /// </summary>
    public string? GetCellFormula(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "formula")?.Value;
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the first sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if the sheet is empty.
    /// R112: governed /add-dotnet-api.
    /// </summary>
    public (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange()
    {
        var sheet = Sheets.FirstOrDefault();
        if (sheet is null) return null;
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the named sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if the sheet is empty.
    /// </summary>
    public (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return GetUsedRange(sheet);
    }

    /// <summary>
    /// Return the bounding range of non-empty cells in the given sheet as
    /// (minRow, minCol, maxRow, maxCol), or null if no cells have content.
    /// </summary>
    public static (int MinRow, int MinCol, int MaxRow, int MaxCol)? GetUsedRange(FodsSheet sheet)
    {
        int minRow = int.MaxValue, minCol = int.MaxValue;
        int maxRow = int.MinValue, maxCol = int.MinValue;
        bool found = false;
        var rows = sheet.Rows;
        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Cells;
            for (int c = 0; c < cells.Count; c++)
            {
                var text = cells[c].Element.Value;
                if (!string.IsNullOrEmpty(text))
                {
                    found = true;
                    if (r < minRow) minRow = r;
                    if (r > maxRow) maxRow = r;
                    if (c < minCol) minCol = c;
                    if (c > maxCol) maxCol = c;
                }
            }
        }
        return found ? (minRow, minCol, maxRow, maxCol) : null;
    }

    /// <summary>
    /// Sort rows in the named sheet by the value in the given column.
    /// Uses ordinal string comparison by default.  Numeric strings are
    /// compared numerically when both values parse as double.
    /// R113: governed /add-dotnet-api.
    /// </summary>
    public void SortRows(string sheetName, int sortColumn, bool ascending = true)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (sortColumn < 0)
            throw new ArgumentOutOfRangeException(nameof(sortColumn), "Column index must be non-negative.");

        var rows = sheet.Rows;
        if (rows.Count <= 1) return;

        var sorted = rows.OrderBy(r =>
        {
            var cells = r.Cells;
            if (sortColumn >= cells.Count) return (object)"";
            var val = cells[sortColumn].Element.Value ?? "";
            if (double.TryParse(val, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var num))
                return (object)num;
            return val;
        }, Comparer<object>.Create((a, b) =>
        {
            if (a is double da && b is double db) return da.CompareTo(db);
            return string.Compare(a?.ToString() ?? "", b?.ToString() ?? "", StringComparison.Ordinal);
        })).ToList();

        if (!ascending) sorted.Reverse();

        var tableEl = sheet.Element;
        var rowEls = sorted.Select(r => r.Element).ToList();
        foreach (var el in rowEls) el.Remove();
        foreach (var el in rowEls) tableEl.Add(el);
    }

    /// <summary>
    /// Return aggregate statistics for a named sheet: total rows, max column count,
    /// total cell slots, and non-empty cell count.
    /// Returns zeros if the sheet is not found.
    /// R114 Train A: sheet-level aggregate stats for data analysis.
    /// </summary>
    public (int RowCount, int ColCount, int CellCount, int NonEmptyCellCount) GetSheetStats(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return (0, 0, 0, 0);

        int rowCount = sheet.Rows.Count;
        int maxCols = 0;
        int cellCount = 0;
        int nonEmpty = 0;

        foreach (var row in sheet.Rows)
        {
            int c = row.Cells.Count;
            if (c > maxCols) maxCols = c;
            cellCount += c;
            foreach (var cell in row.Cells)
                if (!cell.IsCovered && !string.IsNullOrEmpty(cell.Value))
                    nonEmpty++;
        }

        return (rowCount, maxCols, cellCount, nonEmpty);
    }

    /// <summary>
    /// Set or replace the ODF table:style-name attribute on a cell.
    /// Throws if the sheet is not found or row/col indices are out of range.
    /// R114 Train A: cell style management for formatting pipelines.
    /// </summary>
    public void SetCellStyle(string sheetName, int row, int col, string styleName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(styleName);

        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));

        if (row < 0 || row >= sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");

        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count)
            throw new ArgumentOutOfRangeException(nameof(col),
                $"Column {col} is out of range (row has {r.Cells.Count} cells).");

        r.Cells[col].Element.SetAttributeValue(NsTable + "style-name", styleName);
    }

    /// <summary>
    /// Get the ODF table:style-name attribute from a cell, or null if not set.
    /// Returns null if the sheet, row, or col index is not found.
    /// R114 Train A: cell style retrieval.
    /// </summary>
    public string? GetCellStyle(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return null;
        if (row < 0 || row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
    }

    // -------------------------------------------------------------------------
    // R115 — CSV file export + row filtering
    // -------------------------------------------------------------------------

    /// <summary>
    /// Export a named sheet as CSV and write the result to <paramref name="filePath"/>.
    /// R115 Train A: CSV file export for dogfood pipeline integration.
    /// </summary>
    /// <exception cref="ArgumentException">sheetName or filePath null/empty.</exception>
    /// <exception cref="InvalidOperationException">Sheet not found.</exception>
    public void ExportSheetToCsvFile(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var csv = ExportSheetToCsv(sheetName);
        File.WriteAllText(filePath, csv, System.Text.Encoding.UTF8);
    }

    /// <summary>
    /// Export the first sheet as CSV and write to <paramref name="filePath"/>.
    /// R115 Train A: CSV file export (default-sheet overload).
    /// </summary>
    public void ExportSheetToCsvFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        var csv = ExportSheetToCsv();
        File.WriteAllText(filePath, csv, System.Text.Encoding.UTF8);
    }

    /// <summary>
    /// Return a filtered view of rows where <paramref name="col"/> equals <paramref name="value"/>
    /// (case-sensitive exact match). The header row (index 0) is always included.
    /// R115 Train B: row filtering for data query pipeline.
    /// </summary>
    /// <returns>List of row value arrays (including header). Empty if sheet not found.</returns>
    public IReadOnlyList<IReadOnlyList<string?>> FilterRows(string sheetName, int col, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(value);

        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<IReadOnlyList<string?>>();

        var rows = sheet.Rows;
        var result = new List<IReadOnlyList<string?>>();

        for (int r = 0; r < rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            // Always include header row (row 0), include data rows that match
            if (r == 0 || (col < rowVals.Count && rowVals[col] == value))
                result.Add(rowVals);
        }
        return result;
    }

    /// <summary>
    /// Compute numeric aggregates (min, max, sum, count) for a column in a sheet.
    /// Non-numeric cells and the header row are skipped.
    /// R116: column aggregate query.
    /// </summary>
    /// <returns>A tuple (Min, Max, Sum, Count). Count is 0 if no numeric cells.</returns>
    public (double Min, double Max, double Sum, int Count) GetColumnAggregates(string sheetName, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));

        var sheet = GetSheetByName(sheetName);
        if (sheet is null)
            return (0, 0, 0, 0);

        double min = double.MaxValue;
        double max = double.MinValue;
        double sum = 0;
        int count = 0;

        // Skip row 0 (header)
        for (int r = 1; r < sheet.Rows.Count; r++)
        {
            var rowVals = GetRowValues(sheet, r);
            if (col >= rowVals.Count) continue;
            var raw = rowVals[col];
            if (raw is null) continue;
            if (double.TryParse(raw, System.Globalization.NumberStyles.Any,
                                System.Globalization.CultureInfo.InvariantCulture, out double v))
            {
                if (v < min) min = v;
                if (v > max) max = v;
                sum += v;
                count++;
            }
        }

        return count == 0 ? (0, 0, 0, 0) : (min, max, sum, count);
    }

    // -------------------------------------------------------------------------
    // Metadata
    // -------------------------------------------------------------------------

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
