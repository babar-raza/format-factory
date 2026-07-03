// FormatFactory.Fods — FodsDocument export, import, filter, and merge operations (partial class).
// Domain: JSON/CSV/TSV/XML/HTML/Markdown export, FilterRows, ImportFromCsv, MergeSheet, CopyRange.
// Split from FodsDocumentAccessor.cs (TC-PQLM-021 decomposition).
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // JSON export
    // =========================================================================

    /// <summary>Export the first sheet as a JSON array of row objects. R95.</summary>
    public string ExportSheetToJson()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToJson(sheets[0]);
    }

    /// <summary>Export a named sheet as a JSON array of row objects. R95.</summary>
    public string ExportSheetToJson(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToJson(sheet);
    }

    /// <summary>Export a specific sheet as a JSON array of row objects. R95.</summary>
    public static string ExportSheetToJson(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToJson(sheet);

    /// <summary>Export the named sheet as JSON; if sheetName looks like a file path, write all sheets to that path. R245/R319.</summary>
    public string ExportToJson(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or whitespace.", nameof(sheetName));
        if (sheetName.Contains(Path.DirectorySeparatorChar) ||
            sheetName.Contains(Path.AltDirectorySeparatorChar) ||
            Path.HasExtension(sheetName))
        {
            File.WriteAllText(sheetName, ExportToJson(), System.Text.Encoding.UTF8);
            return string.Empty;
        }
        return ExportSheetToJson(sheetName);
    }

    /// <summary>Export the named sheet as JSON and write it to the given file path. R288.</summary>
    public void ExportToJson(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        File.WriteAllText(filePath, ExportSheetToJson(sheetName));
    }

    /// <summary>Export all sheets as a combined JSON object keyed by sheet name. R256.</summary>
    public string ExportToJson()
    {
        var sheets = Sheets;
        if (sheets.Count == 0) return "{}";
        var parts = new List<string>();
        foreach (var sheet in sheets)
        {
            var name = sheet.Name ?? "sheet";
            parts.Add($"\"{EscapeJson(name)}\": {ExportSheetToJson(name)}");
        }
        return "{" + string.Join(", ", parts) + "}";
    }

    private static string EscapeJson(string s)
        => s.Replace("\\", "\\\\").Replace("\"", "\\\"");

    // =========================================================================
    // Markdown export
    // =========================================================================

    /// <summary>Export the first sheet as a Markdown table. R101.</summary>
    public string ExportSheetToMarkdown()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToMarkdown(sheets[0]);
    }

    /// <summary>Export a named sheet as a Markdown table. R101.</summary>
    public string ExportSheetToMarkdown(string sheetName)
    {
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return ExportSheetToMarkdown(sheet);
    }

    /// <summary>Export a specific sheet as a Markdown table. R101.</summary>
    public static string ExportSheetToMarkdown(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToMarkdown(sheet);

    // =========================================================================
    // CSV export
    // =========================================================================

    /// <summary>Export the first sheet as CSV. R107.</summary>
    public string ExportSheetToCsv()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return ExportSheetToCsv(sheets[0]);
    }

    /// <summary>Export a named sheet as CSV. R107.</summary>
    public string ExportSheetToCsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return ExportSheetToCsv(sheet);
    }

    /// <summary>Export a specific sheet as CSV. R107.</summary>
    public static string ExportSheetToCsv(FodsSheet sheet)
        => FodsDocumentExporter.ExportSheetToCsv(sheet);

    /// <summary>Export a named sheet as CSV and write to a file. R115.</summary>
    public void ExportSheetToCsvFile(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        File.WriteAllText(filePath, ExportSheetToCsv(sheetName), System.Text.Encoding.UTF8);
    }

    /// <summary>Export the first sheet as CSV and write to a file. R115.</summary>
    public void ExportSheetToCsvFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            throw new ArgumentException("File path must not be null or empty.", nameof(filePath));
        File.WriteAllText(filePath, ExportSheetToCsv(), System.Text.Encoding.UTF8);
    }

    /// <summary>Export a named sheet as CSV to a file (alias for ExportSheetToCsvFile). R198.</summary>
    public void ExportSheetToCsv(string sheetName, string filePath)
        => ExportSheetToCsvFile(sheetName, filePath);

    /// <summary>Export the specified sheet to a CSV string (alias for ExportSheetToCsv). R289.</summary>
    public string ExportToCsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        return ExportSheetToCsv(sheetName);
    }

    /// <summary>Export a named sheet to a CSV file (alias for ExportSheetToCsvFile). R267.</summary>
    public void ExportToCsv(string sheetName, string filePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        ExportSheetToCsvFile(sheetName, filePath);
    }

    // =========================================================================
    // TSV export
    // =========================================================================

    /// <summary>Export a named sheet as TSV (tab-separated). R236.</summary>
    public string ExportSheetToTsv(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var sb = new System.Text.StringBuilder();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var row in sheet.Rows)
        {
            var cells = row.Cells;
            for (int i = 0; i < cells.Count; i++)
            {
                if (i > 0) sb.Append('\t');
                var val = cells[i].Element.Element(nsText + "p")?.Value ?? cells[i].Element.Value;
                sb.Append(val ?? "");
            }
            sb.AppendLine();
        }
        return sb.ToString();
    }

    // =========================================================================
    // XML export
    // =========================================================================

    /// <summary>Export the first sheet as XML (the raw table:table element). R194.</summary>
    public string ExportSheetToXml()
    {
        var sheets = Sheets;
        if (sheets.Count == 0)
            throw new InvalidOperationException("Document has no sheets.");
        return sheets[0].Element.ToString(SaveOptions.None);
    }

    /// <summary>Export a named sheet as XML (the raw table:table element). R194.</summary>
    public string ExportSheetToXml(string sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"Sheet '{sheetName}' not found.", nameof(sheetName));
        return sheet.Element.ToString(SaveOptions.None);
    }

    /// <summary>Return the document as an FODS XML string (alias for ToFodsXml). R251.</summary>
    public string ToXml() => ToFodsXml();

    // =========================================================================
    // HTML export
    // =========================================================================

    /// <summary>Export the document to an HTML string. R281.</summary>
    public string ExportToHtml()
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head><body>");
        foreach (var sheet in Sheets)
        {
            sb.AppendLine($"<h2>{HtmlEscape(sheet.Name ?? "")}</h2>");
            sb.AppendLine("<table border=\"1\">");
            foreach (var row in sheet.Rows)
            {
                sb.Append("<tr>");
                var nsText2 = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
                foreach (var cell in row.Cells)
                {
                    var val = cell.Element.Element(nsText2 + "p")?.Value ?? cell.Element.Value ?? "";
                    sb.Append($"<td>{HtmlEscape(val)}</td>");
                }
                sb.AppendLine("</tr>");
            }
            sb.AppendLine("</table>");
        }
        sb.AppendLine("</body></html>");
        return sb.ToString();
    }

    private static string HtmlEscape(string s)
        => s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;").Replace("\"", "&quot;");

    // =========================================================================
    // FilterRows overloads
    // =========================================================================

    /// <summary>
    /// Return a filtered view of rows where column at index equals value.
    /// The header row (index 0) is always included. R115.
    /// </summary>
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
            if (r == 0 || (col < rowVals.Count && rowVals[col] == value))
                result.Add(rowVals);
        }
        return result;
    }

    /// <summary>Return matching row indices where the column value satisfies the predicate. R199.</summary>
    public IReadOnlyList<int> FilterRows(string sheetName, int col, Func<string?, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();
        var rows = sheet.Rows;
        var result = new List<int>();
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        for (int r = 0; r < rows.Count; r++)
        {
            var cells = rows[r].Element.Elements(NsTable + "table-cell").ToList();
            string? cellValue = col < cells.Count ? cells[col].Element(nsText + "p")?.Value : null;
            if (predicate(cellValue)) result.Add(r);
        }
        return result;
    }

    /// <summary>Return row indices matching a row-index predicate. R207.</summary>
    public IReadOnlyList<int> FilterRows(string sheetName, Func<int, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();
        var result = new List<int>();
        for (int r = 0; r < sheet.Rows.Count; r++)
            if (predicate(r)) result.Add(r);
        return result;
    }

    /// <summary>Return row indices where the row-values predicate returns true. R221.</summary>
    public IReadOnlyList<int> FilterRows(string sheetName, Func<IReadOnlyList<string?>, bool> predicate)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(predicate);
        var sheet = GetSheetByName(sheetName);
        if (sheet is null) return Array.Empty<int>();
        var result = new List<int>();
        for (int r = 0; r < sheet.Rows.Count; r++)
            if (predicate(GetRowValues(sheet, r))) result.Add(r);
        return result;
    }

    /// <summary>Return a new FodsDocument containing only rows where the first-sheet column equals value. R227.</summary>
    public FodsDocument FilterRows(int col, string value)
    {
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        ArgumentNullException.ThrowIfNull(value);
        var sheets = Sheets;
        if (sheets.Count == 0) return CreateEmpty();
        var sheet = sheets[0];
        var result = CreateEmpty();
        result.AddSheet(sheet.Name ?? "Sheet1");
        var resultSheet = result.Sheets[0];
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var row in sheet.Rows)
        {
            var cells = row.Element.Elements(NsTable + "table-cell").ToList();
            if (col >= cells.Count) continue;
            var cellVal = cells[col].Element(nsText + "p")?.Value;
            if (cellVal == value)
                resultSheet.Element.Add(new XElement(row.Element));
        }
        return result;
    }

    /// <summary>Return a new document containing only rows where the column header's cell equals value. R241.</summary>
    public FodsDocument FilterRows(string sheetName, string columnName, string value)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        ArgumentNullException.ThrowIfNull(columnName);
        ArgumentNullException.ThrowIfNull(value);
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (sheet.Rows.Count == 0)
        {
            var empty = CreateEmpty();
            empty.AddSheet(sheetName);
            return empty;
        }
        var headerVals = GetRowValues(sheet, 0);
        int colIndex = -1;
        for (int i = 0; i < headerVals.Count; i++)
            if (headerVals[i] == columnName) { colIndex = i; break; }
        var result = CreateEmpty();
        result.AddSheet(sheetName);
        var resultSheet = result.GetSheetByName(sheetName)!;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        resultSheet.Element.Add(new XElement(sheet.Rows[0].Element));
        if (colIndex >= 0)
        {
            foreach (var row in sheet.Rows.Skip(1))
            {
                var cells = row.Element.Elements(NsTable + "table-cell").ToList();
                if (colIndex < cells.Count && cells[colIndex].Element(nsText + "p")?.Value == value)
                    resultSheet.Element.Add(new XElement(row.Element));
            }
        }
        return result;
    }

    // =========================================================================
    // Import
    // =========================================================================

    /// <summary>Import a CSV file into the named sheet. R248.</summary>
    public void ImportFromCsv(string sheetName, string csvFilePath)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        if (string.IsNullOrWhiteSpace(csvFilePath))
            throw new ArgumentException("CSV file path must not be null or empty.", nameof(csvFilePath));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}' exists.", nameof(sheetName));
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var line in File.ReadAllLines(csvFilePath))
        {
            var parts = line.Split(',');
            var rowEl = new XElement(NsTable + "table-row");
            foreach (var part in parts)
                rowEl.Add(new XElement(NsTable + "table-cell",
                    new XElement(nsText + "p", part.Trim('"'))));
            sheet.Element.Add(rowEl);
        }
    }

    // =========================================================================
    // Merge and copy operations
    // =========================================================================

    /// <summary>Copy a sheet from sourceDoc into this document under the given name. R250.</summary>
    public void MergeSheet(FodsDocument sourceDoc, string sheetName)
    {
        ArgumentNullException.ThrowIfNull(sourceDoc);
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
        var srcSheet = sourceDoc.GetSheetByName(sheetName);
        if (srcSheet is null) return;
        string destName = sheetName;
        int suffix = 2;
        while (GetSheetByName(destName) != null) destName = $"{sheetName}_{suffix++}";
        AddSheet(destName);
        var destSheet = GetSheetByName(destName)!;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        foreach (var srcRow in srcSheet.Rows)
        {
            var newRow = new XElement(NsTable + "table-row");
            foreach (var srcCell in srcRow.Cells)
            {
                var val = srcCell.Element.Element(nsText + "p")?.Value ?? srcCell.Element.Value;
                newRow.Add(new XElement(NsTable + "table-cell",
                    new XElement(nsText + "p", val ?? "")));
            }
            destSheet.Element.Add(newRow);
        }
    }

    /// <summary>Copy a rectangular range from srcSheet to destSheet. R250.</summary>
    public void CopyRange(string srcSheet, int srcRow, int srcCol,
                          string destSheet, int destRow, int destCol,
                          int rows, int cols)
    {
        if (string.IsNullOrWhiteSpace(srcSheet))
            throw new ArgumentException("Source sheet name must not be null or empty.", nameof(srcSheet));
        if (string.IsNullOrWhiteSpace(destSheet))
            throw new ArgumentException("Destination sheet name must not be null or empty.", nameof(destSheet));
        var src = GetSheetByName(srcSheet);
        var dest = GetSheetByName(destSheet);
        if (src is null || dest is null) return;
        var nsText = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:text:1.0");
        for (int r = 0; r < rows; r++)
        {
            int sr = srcRow + r, dr = destRow + r;
            while (dest.Rows.Count <= dr)
                dest.Element.Add(new XElement(NsTable + "table-row"));
            var destRowEl = dest.Rows[dr];
            for (int c = 0; c < cols; c++)
            {
                int sc = srcCol + c, dc = destCol + c;
                string val = "";
                if (sr < src.Rows.Count)
                {
                    var srcCells = src.Rows[sr].Cells;
                    if (sc < srcCells.Count)
                        val = srcCells[sc].Element.Element(nsText + "p")?.Value
                              ?? srcCells[sc].Element.Value ?? "";
                }
                while (destRowEl.Cells.Count <= dc)
                    destRowEl.Element.Add(new XElement(NsTable + "table-cell"));
                var destCell = destRowEl.Cells[dc].Element;
                var pEl = destCell.Element(nsText + "p");
                if (pEl is null) destCell.Add(new XElement(nsText + "p", val));
                else pEl.Value = val;
            }
        }
    }

    /// <summary>Append all rows from the source sheet to the end of the target sheet. R270.</summary>
    public void MergeSheets(string sourceSheetName, string targetSheetName)
    {
        if (string.IsNullOrWhiteSpace(sourceSheetName))
            throw new ArgumentException("Source sheet name must not be null or empty.", nameof(sourceSheetName));
        if (string.IsNullOrWhiteSpace(targetSheetName))
            throw new ArgumentException("Target sheet name must not be null or empty.", nameof(targetSheetName));
        var source = GetSheetByName(sourceSheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sourceSheetName}' exists.");
        var target = GetSheetByName(targetSheetName)
            ?? throw new InvalidOperationException($"No sheet named '{targetSheetName}' exists.");
        foreach (var row in source.Rows)
            target.Element.Add(new XElement(row.Element));
    }
}
