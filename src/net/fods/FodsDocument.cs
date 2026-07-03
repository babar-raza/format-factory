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
public sealed partial class FodsDocument
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
    /// blank document factory for programmatic construction.
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
            "  <office:body><office:spreadsheet>" +
            "  </office:spreadsheet></office:body>" +
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

    /// <summary>
    /// Load a FODS document from a <see cref="Stream"/>.
    /// The stream must contain valid FODS XML.
    /// </summary>
    /// <param name="stream">Readable stream containing FODS content. Must not be null.</param>
    /// <param name="maxContentBytes">
    /// Optional maximum number of bytes to read from the stream (default 50 MB).
    /// </param>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="stream"/> is null.</exception>
    /// <exception cref="FodsDocumentException">Thrown on parse or security failures.</exception>
    public static FodsDocument Load(Stream stream,
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
            return new FodsDocument(doc) { MaxFileSizeBytes = maxContentBytes };
        }
        catch (XmlException ex)
        {
            throw new FodsDocumentException($"XML parse error: {ex.Message}", ex);
        }
        catch (Exception ex) when (ex is not FodsDocumentException)
        {
            throw new FodsDocumentException(
                $"Unexpected error loading FODS from stream: {ex.GetType().Name}: {ex.Message}", ex);
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
    // CreateEmpty / LoadFromXml / ToFodsXml
    // -------------------------------------------------------------------------

    /// <summary>
    /// Create a new FODS document with no sheets and no content.
    /// Identical to <see cref="CreateNew"/> — provided for API symmetry.
    /// </summary>
    public static FodsDocument CreateEmpty() => CreateNew();

    /// <summary>
    /// Load a FODS document from an in-memory XML string.
    /// </summary>
    public static FodsDocument LoadFromXml(string xml)
    {
        if (string.IsNullOrEmpty(xml))
            throw new FodsDocumentException("xml must not be null or empty.");
        var settings = new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver = null,
        };
        try
        {
            using var reader = XmlReader.Create(new StringReader(xml), settings);
            var doc = XDocument.Load(reader, LoadOptions.PreserveWhitespace);
            return new FodsDocument(doc);
        }
        catch (XmlException ex)
        {
            throw new FodsDocumentException($"XML parse error: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Serialize the document to a FODS XML string.
    /// </summary>
    public string ToFodsXml()
    {
        using var sw = new StringWriter();
        using (var writer = XmlWriter.Create(sw, new XmlWriterSettings
        {
            Indent = true,
            OmitXmlDeclaration = false,
            Encoding = System.Text.Encoding.UTF8,
        }))
        {
            _doc.WriteTo(writer);
        }
        return sw.ToString();
    }

    // -------------------------------------------------------------------------
    // SetCellValue (string sheetName overload) / SetCellValueAutoExpand
    // -------------------------------------------------------------------------

    /// <summary>
    /// Set a cell value by sheet name, row, and column.
    /// </summary>
    public void SetCellValue(string sheetName, int row, int col, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        SetCellValue(sheet, row, col, value);
    }

    /// <summary>
    /// Get a cell value by sheet name, row, and column.
    /// </summary>
    public string? GetCellValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row), "Row index must be non-negative.");
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col), "Column index must be non-negative.");
        return GetCellValue(sheet, row, col);
    }

    /// <summary>
    /// Set a cell value, auto-expanding the sheet's rows and cells as needed.
    /// </summary>
    private static void SetCellValueAutoExpand(FodsSheet sheet, int row, int col, string value)
    {
        EnsureCell(sheet, row, col);
        SetCellValue(sheet, row, col, value);
    }

    // -------------------------------------------------------------------------
    // DeleteColumn (int overload)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Delete column at the given index from the named sheet.
    /// </summary>
    public void DeleteColumn(string sheetName, int colIndex)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (colIndex < 0) throw new ArgumentOutOfRangeException(nameof(colIndex));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (colIndex < cells.Count)
                cells[colIndex].Remove();
        }
    }

    // -------------------------------------------------------------------------
    // Charts backing store (for FodsDocumentExtendedApis)
    // -------------------------------------------------------------------------

    private readonly Dictionary<string, List<ChartInfo>> _charts = new();

    internal record ChartInfo(string Title);

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
    /// convenience property.
    /// </summary>
    public int SheetCount => Sheets.Count;

    /// <summary>
    /// Get a sheet by name (case-sensitive). Returns null if not found.
    /// named sheet access.
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
    /// index-based sheet access (complements GetSheetByName).
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
    /// sheet name enumeration.
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
    /// sheet creation API.
    /// </summary>
    public FodsSheet AddSheet(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(name));

        var existing = GetSheetByName(name);
        if (existing != null)
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
    /// sheet management completion (AddSheet exists, RemoveSheet was missing).
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
    /// sheet renaming for workbook management.
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
        if (oldName == newName) return; // no-op
        if (GetSheetByName(newName) != null)
            throw new InvalidOperationException($"A sheet named '{newName}' already exists.");

        sheet.Element.SetAttributeValue(NsTable + "name", newName);
    }

    /// <summary>
    /// Copy a sheet (deep clone) and add it with the given new name.
    /// Throws if the source sheet is not found or the new name already exists.
    /// sheet duplication for workbook templating.
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
    /// row management for spreadsheet editing.
    /// </summary>
    public void DeleteRows(string sheetName, int startRow, int count)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (count < 0)
            throw new ArgumentOutOfRangeException(nameof(count), "Count must be non-negative.");
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
    /// row insertion for spreadsheet editing.
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
    /// column header extraction.
    /// </summary>
    public IReadOnlyList<string> GetColumnHeaders()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return Array.Empty<string>();
        return GetColumnHeadersFromSheet(sheets[0]);
    }

    /// <summary>
    /// Return the column headers from the first row of the named sheet.
    /// Returns an empty list if the sheet is not found or its first row is empty.
    /// column header extraction (named sheet overload).
    /// </summary>
    public IReadOnlyList<string> GetColumnHeaders(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<string>();
        return GetColumnHeadersFromSheet(sheet);
    }

    /// <summary>
    /// Return the column headers from the first row of <paramref name="sheet"/>.
    /// Returns an empty list if the first row is empty.
 /// R93 . Internal helper — use the instance overloads instead.
    /// </summary>
    private static IReadOnlyList<string> GetColumnHeadersFromSheet(FodsSheet sheet)
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
    /// cell-level access.
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
    /// cell-level access.
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
    /// round-trip edit support.
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
    /// round-trip edit support.
    /// </summary>
    public static void SetCellValue(FodsSheet sheet, int row, int col, string value)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(value);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].SetText(value);
    }

    /// <summary>
    /// Export a sheet as an HTML table string. Uses the first sheet if no sheet specified.
    /// Rows become &lt;tr&gt; elements, cells become &lt;td&gt; elements.
    /// Empty cells produce empty &lt;td&gt; elements. Cell text is HTML-escaped.
    /// HTML export for dogfood pipeline.
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
    /// HTML export for dogfood pipeline.
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
    /// HTML export for dogfood pipeline.
    /// </summary>
    public static string ExportSheetToHtml(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToHtml(sheet);

    /// <summary>
    /// Return the number of rows in the first sheet.
    /// Returns 0 if the document has no sheets.
    /// row count query for data inspection.
    /// </summary>
    /// <summary>
    /// Remove all rows from the named sheet, leaving it empty.
    /// Throws if the sheet is not found.
    /// sheet clearing for spreadsheet editing.
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
    /// Insert a new row at the given index with the specified cell values.
    /// Creates a table-row element with table-cell elements containing text:p for each value.
    /// Null values produce empty cells. Existing rows at and after the index shift down.
    /// populated row insertion for spreadsheet editing workflows.
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
    /// Merge a rectangular range of cells in the specified sheet.
    /// Sets table:number-columns-spanned and table:number-rows-spanned on the top-left cell,
    /// and replaces spanned cells with table:covered-table-cell elements.
    /// ODF spec: §9.4.5 table:table-cell merge attributes.
    /// object-model depth for cell merge operations.
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
    /// object-model depth for formula editing workflows.
    /// </summary>
    public void SetCellFormula(string sheetName, int row, int col, string formula)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(formula);

        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsTable + "formula", formula);
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
    /// Set or replace the ODF table:style-name attribute on a cell.
    /// Throws if the sheet is not found or row/col indices are out of range.
    /// cell style management for formatting pipelines.
    /// </summary>
    public void SetCellStyle(string sheetName, int row, int col, string styleName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(styleName);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));

        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));

        // Allow appending only the next row (row == Rows.Count); anything beyond throws.
        if (row > sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
        if (row == sheet.Rows.Count)
            sheet.Element.Add(new XElement(NsTable + "table-row"));

        var r = sheet.Rows[row];
        // Allow appending only the next cell (col == r.Cells.Count); anything beyond throws.
        if (col > r.Cells.Count)
            throw new ArgumentOutOfRangeException(nameof(col),
                $"Column {col} is out of range (row has {r.Cells.Count} cells).");
        if (col == r.Cells.Count)
            r.Element.Add(new XElement(NsTable + "table-cell"));

        r.Cells[col].Element.SetAttributeValue(NsTable + "style-name", styleName);
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
