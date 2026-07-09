// FormatFactory.Fods — FodsDocument row/cell/column editing operations (partial class).
// Domain: AddRow, InsertRow, DeleteRows, ClearSheet, AddColumn, DeleteColumn, SetColumnWidth,
//         SetCellBold/Italic/FontSize/FontName, SetCellColor/Border, SetCellStyle, SetCellRange,
//         SetColumnHeaders, SetNamedRange, SetAutoFilter (3-arg), ClearFilter, SetFormula,
//         SetCellComment, GetCellComment, SortRows, FreezeRows, and cell/row mutation helpers.
// Split from FodsDocumentAccessor.cs (TC-PQLM-021 decomposition).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // Private helpers (EnsureCell, SetCellValueAutoExpand)
    // =========================================================================

    private static void EnsureCell(FodsSheet sheet, int row, int col)
    {
        while (row >= sheet.Rows.Count)
            sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count)
            r.Element.Add(new XElement(NsTable + "table-cell"));
    }

    // =========================================================================
    // Row operations: AddRow, InsertRow, DeleteRows, ClearSheet
    // =========================================================================

    /// <summary>Append a row with the given values to the first (active) sheet. R225.</summary>
    public void AddRow(IList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        var sheet = _activeSheet != null ? (GetSheetByName(_activeSheet) ?? sheets[0]) : sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var row = new XElement(NsTable + "table-row");
        foreach (var val in values)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (!string.IsNullOrEmpty(val))
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", val));
            }
            row.Add(cell);
        }
        sheet.Element.Add(row);
    }

    /// <summary>Append a row with the given values to the named sheet. R240.</summary>
    public void AddRow(string sheetName, IReadOnlyList<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        InsertRowWithValues(sheetName, sheet.Rows.Count, values);
    }

    /// <summary>Append a row to the named sheet (string[] overload, alias for AddRow). R281.</summary>
    public void AddRowToSheet(string sheetName, string[] values)
        => AddRow(sheetName, values);

    /// <summary>Insert a new row with the given values at index in the first sheet. R227.</summary>
    public void InsertRow(int index, IList<string> values)
    {
        if (index < 0) throw new ArgumentOutOfRangeException(nameof(index));
        ArgumentNullException.ThrowIfNull(values);
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        var sheet = sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        var newRow = new XElement(NsTable + "table-row");
        foreach (var val in values)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (!string.IsNullOrEmpty(val))
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", val));
            }
            newRow.Add(cell);
        }
        var rows = sheet.Rows;
        if (index < rows.Count) rows[index].Element.AddBeforeSelf(newRow);
        else if (rows.Count > 0) rows[^1].Element.AddAfterSelf(newRow);
        else sheet.Element.Add(newRow);
    }

    /// <summary>Append a row with values to the named sheet (2-arg overload). R243.</summary>
    public void InsertRowWithValues(string sheetName, IReadOnlyList<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        InsertRowWithValues(sheetName, sheet.Rows.Count, values);
    }

    /// <summary>Delete count rows starting at startRow in the first sheet. R225.</summary>
    public void DeleteRows(int startRow, int count)
    {
        if (startRow < 0) throw new ArgumentOutOfRangeException(nameof(startRow));
        if (count < 0) throw new ArgumentOutOfRangeException(nameof(count));
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        var sheet = sheets[0];
        for (int i = 0; i < count; i++)
        {
            var rows = sheet.Rows;
            if (startRow >= rows.Count) break;
            rows[startRow].Element.Remove();
        }
    }

    /// <summary>Delete a single row at rowIndex in the named sheet. R245.</summary>
    public void DeleteRow(string sheetName, int rowIndex)
    {
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        DeleteRows(sheetName, rowIndex, 1);
    }

    /// <summary>Remove all rows from the first sheet. R225.</summary>
    public void ClearSheet()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return;
        foreach (var row in sheets[0].Rows.ToList()) row.Element.Remove();
    }

    /// <summary>Clear the value of a cell (alias for ClearCellValue). R283.</summary>
    public void ClearCell(string sheetName, int row, int col)
        => ClearCellValue(sheetName, row, col);

    /// <summary>Clear the value of the cell at (row, col) in the named sheet. R245.</summary>
    public void ClearCellValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return;
        if (row < 0 || row >= sheet.Rows.Count) return;
        var r = sheet.Rows[row];
        if (col < 0 || col >= r.Cells.Count) return;
        SetCellValue(sheetName, row, col, "");
    }

    /// <summary>Set cell value (alias for SetCellValue). R281.</summary>
    public void SetCell(string sheetName, int row, int col, string value)
        => SetCellValue(sheetName, row, col, value);

    // =========================================================================
    // Column operations
    // =========================================================================

    /// <summary>Append a column to the named sheet (header only). R217.</summary>
    public void AddColumn(string sheetName, string? header)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        bool isFirstRow = true, hasRows = false;
        foreach (var row in sheet.Rows)
        {
            hasRows = true;
            var cell = new XElement(NsTable + "table-cell");
            if (isFirstRow && header != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", header));
            }
            row.Element.Add(cell);
            isFirstRow = false;
        }
        if (!hasRows && header != null)
        {
            var headerRow = new XElement(NsTable + "table-row");
            var cell = new XElement(NsTable + "table-cell");
            cell.SetAttributeValue(NsOffice + "value-type", "string");
            cell.Add(new XElement(nsText + "p", header));
            headerRow.Add(cell);
            sheet.Element.Add(headerRow);
        }
    }

    /// <summary>Add a column with header and enumerable values to the named sheet. R236.</summary>
    public void AddColumn(string sheetName, string header, IEnumerable<string?> values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(header);
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        var valueList = values.ToList();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        while (sheet.Rows.Count == 0) sheet.Element.Add(new XElement(NsTable + "table-row"));
        sheet.Rows[0].Element.Add(new XElement(NsTable + "table-cell",
            new XElement(nsText + "p", header)));
        for (int i = 0; i < valueList.Count; i++)
        {
            int rowIdx = i + 1;
            while (sheet.Rows.Count <= rowIdx) sheet.Element.Add(new XElement(NsTable + "table-row"));
            sheet.Rows[rowIdx].Element.Add(new XElement(NsTable + "table-cell",
                new XElement(nsText + "p", valueList[i] ?? "")));
        }
    }

    /// <summary>Append a column to the named sheet using an array of values. R266.</summary>
    public void AddColumn(string sheetName, string[] values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (values == null) throw new ArgumentNullException(nameof(values));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        int rowIdx = 0;
        foreach (var row in sheet.Rows)
        {
            var cell = new XElement(NsTable + "table-cell");
            if (rowIdx < values.Length && values[rowIdx] != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", values[rowIdx]));
            }
            row.Element.Add(cell);
            rowIdx++;
        }
        while (rowIdx < values.Length)
        {
            var newRow = new XElement(NsTable + "table-row");
            var cell = new XElement(NsTable + "table-cell");
            if (values[rowIdx] != null)
            {
                cell.SetAttributeValue(NsOffice + "value-type", "string");
                cell.Add(new XElement(nsText + "p", values[rowIdx]));
            }
            newRow.Add(cell);
            sheet.Element.Add(newRow);
            rowIdx++;
        }
    }

    /// <summary>Delete a column identified by its header name. R253/R311.</summary>
    public void DeleteColumn(string sheetName, string columnName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnName);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (sheet.Rows.Count == 0)
            throw new ArgumentException($"Column '{columnName}' not found in sheet '{sheetName}'.", nameof(columnName));
        var headerVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerVals.Count; i++)
            if (headerVals[i] == columnName) { colIndex = i; break; }
        if (colIndex < 0)
            throw new ArgumentException($"Column '{columnName}' not found in sheet '{sheetName}'.", nameof(columnName));
        DeleteColumn(sheetName, colIndex);
    }


    /// <summary>Set the header row (row 0) of the named sheet to the given values. R276.</summary>
    public void SetColumnHeaders(string sheetName, string[] headers)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(headers);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        for (int c = 0; c < headers.Length; c++)
            SetCellValueAutoExpand(sheet, 0, c, headers[c] ?? "");
    }

    /// <summary>Store the width for a column (in-memory). R218.</summary>
    public void SetColumnWidth(string sheetName, int colIndex, double width)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (colIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(colIndex), "Column index must not be negative.");
        if (width < 0)
            throw new ArgumentOutOfRangeException(nameof(width), "Width must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        if (!_columnWidths.TryGetValue(sheetName, out var cols))
        {
            cols = new Dictionary<int, double>();
            _columnWidths[sheetName] = cols;
        }
        cols[colIndex] = width;
    }

    /// <summary>Set the row height for a row (in-memory). R247.</summary>
    public void SetRowHeight(string sheetName, int rowIndex, double height)
    {
        // TODO(GI-FODS-NET-010): wire row height to ODF XML
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowIndex < 0) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        _rowHeights[(sheetName, rowIndex)] = height;
    }

    // =========================================================================
    // Cell style operations (static and instance)
    // =========================================================================

    /// <summary>Set a cell's style-name attribute by explicit FodsSheet reference. R212.</summary>
    public static void SetCellStyle(FodsSheet sheet, int row, int col, string styleName)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(styleName);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row > sheet.Rows.Count)
            throw new ArgumentOutOfRangeException(nameof(row),
                $"Row {row} is out of range (sheet has {sheet.Rows.Count} rows).");
        if (row == sheet.Rows.Count) sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count) r.Element.Add(new XElement(NsTable + "table-cell"));
        r.Cells[col].Element.SetAttributeValue(NsTable + "style-name", styleName);
    }

    /// <summary>Set the bold attribute for a cell (static). R221.</summary>
    public static void SetCellBold(FodsSheet sheet, int row, int col, bool bold)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-weight", bold ? "bold" : "normal");
    }

    /// <summary>Get the bold attribute for a cell (static). R221.</summary>
    public static bool GetCellBold(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return false;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return false;
        return r.Cells[col].Element.Attribute(NsFo + "font-weight")?.Value == "bold";
    }

    /// <summary>Set the italic attribute for a cell (static). R222.</summary>
    public static void SetCellItalic(FodsSheet sheet, int row, int col, bool italic)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-style", italic ? "italic" : "normal");
    }

    /// <summary>Get the italic attribute for a cell (static). R222.</summary>
    public static bool GetCellItalic(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return false;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return false;
        return r.Cells[col].Element.Attribute(NsFo + "font-style")?.Value == "italic";
    }

    /// <summary>Set the font size for a cell (static). R223.</summary>
    public static void SetCellFontSize(FodsSheet sheet, int row, int col, int size)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (size < 0) throw new ArgumentOutOfRangeException(nameof(size));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-size", size.ToString());
    }

    /// <summary>Get the font size for a cell (static). R223.</summary>
    public static int GetCellFontSize(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return 0;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return 0;
        var raw = r.Cells[col].Element.Attribute(NsFo + "font-size")?.Value;
        return raw is not null && int.TryParse(raw, out int v) ? v : 0;
    }

    /// <summary>Set the font name for a cell (static). R224.</summary>
    public static void SetCellFontName(FodsSheet sheet, int row, int col, string fontName)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(fontName);
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "font-family", fontName);
    }

    /// <summary>Get the font name for a cell (static). R224.</summary>
    public static string? GetCellFontName(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "font-family")?.Value;
    }

    // Instance overloads for first-sheet and named-sheet access
    /// <summary>Set bold on the first-sheet cell. R229.</summary>
    public void SetCellBold(int row, int col, bool bold) { var s = Sheets; if (s.Count > 0) SetCellBold(s[0], row, col, bold); }
    /// <summary>Set italic on the first-sheet cell. R229.</summary>
    public void SetCellItalic(int row, int col, bool italic) { var s = Sheets; if (s.Count > 0) SetCellItalic(s[0], row, col, italic); }
    /// <summary>Set font size on the first-sheet cell. R229.</summary>
    public void SetCellFontSize(int row, int col, int size) { var s = Sheets; if (s.Count > 0) SetCellFontSize(s[0], row, col, size); }

    /// <summary>Set the bold attribute for a cell in the named sheet. R247.</summary>
    public void SetCellBold(string sheetName, int row, int col, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        SetCellBold(GetSheetByName(sheetName) ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName)), row, col, bold);
    }

    /// <summary>Set the italic attribute for a cell in the named sheet. R247.</summary>
    public void SetCellItalic(string sheetName, int row, int col, bool italic)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        SetCellItalic(GetSheetByName(sheetName) ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName)), row, col, italic);
    }

    // =========================================================================
    // Cell color and border operations
    // =========================================================================

    /// <summary>Set the background color for a cell (static). R225.</summary>
    public static void SetCellColor(FodsSheet sheet, int row, int col, string color)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(color);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "background-color", color);
    }

    /// <summary>Get the background color of a cell (static). R225.</summary>
    public static string? GetCellColor(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "background-color")?.Value;
    }

    /// <summary>Set the background color for the first-sheet cell. R229.</summary>
    public void SetCellColor(int row, int col, string color) { var s = Sheets; if (s.Count > 0) SetCellColor(s[0], row, col, color); }

    /// <summary>Get the background color of the first-sheet cell. R229.</summary>
    public string? GetCellColor(int row, int col) { var s = Sheets; return s.Count == 0 ? null : GetCellColor(s[0], row, col); }

    /// <summary>Set the background color for a named-sheet cell. R229.</summary>
    public void SetCellColor(string sheetName, int row, int col, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        SetCellColor(GetSheetByName(sheetName) ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName)), row, col, color);
    }

    /// <summary>Get the background color of a named-sheet cell. R229.</summary>
    public string GetCellColor(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName);
        return sheet is null ? string.Empty : (GetCellColor(sheet, row, col) ?? string.Empty);
    }

    /// <summary>Set cell background color (alias for SetCellColor, static). R225.</summary>
    public static void SetCellBackgroundColor(FodsSheet sheet, int row, int col, string color)
        => SetCellColor(sheet, row, col, color);

    /// <summary>Set cell background color (alias for SetCellColor). R229.</summary>
    public void SetCellBackgroundColor(string sheetName, int row, int col, string color)
        => SetCellColor(sheetName, row, col, color);

    /// <summary>Set cell background color (alias for SetCellColor). R272.</summary>
    public void SetCellBackground(string sheetName, int row, int col, string colorName)
        => SetCellColor(sheetName, row, col, colorName);

    /// <summary>Set the border style for a cell (static). R226.</summary>
    public static void SetCellBorder(FodsSheet sheet, int row, int col, string border)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(border);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        EnsureCell(sheet, row, col);
        sheet.Rows[row].Cells[col].Element.SetAttributeValue(NsFo + "border", border);
    }

    /// <summary>Get the border style of a cell (static). R226.</summary>
    public static string? GetCellBorder(FodsSheet sheet, int row, int col)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (row >= sheet.Rows.Count) return null;
        var r = sheet.Rows[row];
        if (col >= r.Cells.Count) return null;
        return r.Cells[col].Element.Attribute(NsFo + "border")?.Value;
    }

    /// <summary>Set the border style for a named-sheet cell. R226.</summary>
    public void SetCellBorder(string sheetName, int row, int col, string border)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        SetCellBorder(GetSheetByName(sheetName) ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName)), row, col, border);
    }

    /// <summary>Get the border style of a named-sheet cell. R226/R353.</summary>
    public string? GetCellBorder(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName)) throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return GetCellBorder(sheet, row, col) ?? string.Empty;
    }

    // =========================================================================
    // Bulk cell operations
    // =========================================================================

    /// <summary>Apply a named format to a cell (stored as fo:data-style-name). R257.</summary>
    public void SetCellFormatting(string sheetName, int row, int col, string format)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        while (row >= sheet.Rows.Count) sheet.Element.Add(new XElement(NsTable + "table-row"));
        var r = sheet.Rows[row];
        while (col >= r.Cells.Count) r.Element.Add(new XElement(NsTable + "table-cell"));
        r.Cells[col].Element.SetAttributeValue(NsFo + "data-style-name", format);
    }

    /// <summary>Bulk-set a block of cells starting at startRow/startCol from a jagged array. R273.</summary>
    public void SetCellRange(string sheetName, int startRow, int startCol, string[][] values)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(values);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        for (int r = 0; r < values.Length; r++)
        {
            var rowValues = values[r];
            if (rowValues == null) continue;
            for (int c = 0; c < rowValues.Length; c++)
                SetCellValueAutoExpand(sheet, startRow + r, startCol + c, rowValues[c] ?? "");
        }
    }

    // =========================================================================
    // Named range, formula, and filter operations
    // =========================================================================

    /// <summary>Define a named range (in-memory only). R264.</summary>
    public void SetNamedRange(string name, string sheetName, string range)
    {
        // TODO(GI-FODS-NET-011): wire to ODF table:named-expressions/table:named-range XML for persistence
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name must not be null or empty.", nameof(name));
        _namedRanges[name] = range;
    }

    /// <summary>Retrieve the range string for a named range. R264.</summary>
    public string? GetNamedRange(string name)
    {
        if (name == null) throw new ArgumentNullException(nameof(name));
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("name must not be whitespace.", nameof(name));
        if (!_namedRanges.TryGetValue(name, out var r))
            throw new KeyNotFoundException($"Named range '{name}' not found.");
        return r;
    }

    /// <summary>Set the formula for a cell (alias for SetCellFormula). R249.</summary>
    public void SetFormula(string sheetName, int row, int col, string formula)
        => SetCellFormula(sheetName, row, col, formula);

    /// <summary>No-op formula evaluator (formulas are stored but not computed). R249.</summary>
    public void EvaluateFormulas() { /* no-op: formula evaluation not supported */ }

    /// <summary>Apply an auto-filter on the named column of a sheet (3-arg, persisted). R265.</summary>
    public void SetAutoFilter(string sheetName, string colName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        _activeFilters[sheetName] = (colName, value);
        sheet.Element.SetAttributeValue(NsFfExt + "auto-filter", $"{colName}:{value}");
    }

    /// <summary>Clear the active auto-filter from a sheet. R265.</summary>
    public void ClearFilter(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _activeFilters.Remove(sheetName);
        GetSheetByName(sheetName)?.Element.Attribute(NsFfExt + "auto-filter")?.Remove();
    }

    /// <summary>Freeze the top N rows of a sheet (validated, not persisted to XML). R264.</summary>
    public void FreezeRows(string sheetName, int rowCount)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (rowCount < 0)
            throw new ArgumentOutOfRangeException(nameof(rowCount), "rowCount must not be negative.");
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        // no-op: freeze pane metadata not persisted in this implementation
    }

    // =========================================================================
    // Cell comments
    // =========================================================================

    /// <summary>Attach a text comment to a cell. R280.</summary>
    public void SetCellComment(string sheetName, int row, int col, string comment)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        if (GetSheetByName(sheetName) == null)
            throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        _cellComments[(sheetName, row, col)] = comment ?? string.Empty;
    }

    /// <summary>Return the comment attached to a cell, or empty string if none. R280.</summary>
    public string GetCellComment(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellComments.TryGetValue((sheetName, row, col), out var c) ? c : string.Empty;
    }

    // =========================================================================
    // Sort operations
    // =========================================================================

    /// <summary>Sort data rows by column header name (alias for SortRows). R255.</summary>
    public void SortSheet(string sheetName, string columnHeader, bool ascending)
        => SortRows(sheetName, columnHeader, ascending);

    /// <summary>Sort data rows (rows 1..N) in the named sheet by the column with the given header name. R238.</summary>
    public void SortRows(string sheetName, string columnHeader, bool ascending)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnHeader);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        if (sheet.Rows.Count <= 1) return;
        var headerRowVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerRowVals.Count; i++)
            if (headerRowVals[i] == columnHeader) { colIndex = i; break; }
        if (colIndex < 0) return;
        var rows = sheet.Rows;
        var headerEl = rows[0].Element;
        var dataRows = rows.Skip(1).ToList();
        var sorted = dataRows.OrderBy(r =>
        {
            var cells = r.Cells;
            if (colIndex >= cells.Count) return (object)"";
            var val = cells[colIndex].Element.Value ?? "";
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
        foreach (var el in rows.Select(r => r.Element).ToList()) el.Remove();
        tableEl.Add(headerEl);
        foreach (var r in sorted) tableEl.Add(r.Element);
    }

    // =========================================================================
    // Sheet name rename
    // =========================================================================

    /// <summary>Rename the sheet at the given zero-based index. R476.</summary>
    public void SetSheetName(int index, string name)
    {
        var names = GetSheetNames();
        if (index < 0 || index >= names.Count)
            throw new ArgumentOutOfRangeException(nameof(index));
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(name));
        RenameSheet(names[index], name);
    }
}
