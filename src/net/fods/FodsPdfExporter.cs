// FormatFactory.Fods -- Commercial .NET FODS → PDF Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: product-deepening-fods-pdf-export-20260616
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
//
// Pure .NET PDF 1.4 writer — no NuGet dependencies.
// Renders FODS spreadsheet cells as text lines using PDF text operators.
// Supports multi-sheet documents (one PDF page per sheet).
//
// KNOWN SCOPE LIMITATION (PROB-002, Option C — formal declaration):
//   PDF export is Latin-1-scoped (Unicode > U+00FF is replaced with '?').
//   Root cause: PDF standard fonts (Helvetica, Helvetica-Bold) use WinAnsiEncoding (Latin-1).
//   Full Unicode requires TrueType font embedding — deferred post-Gate 11.
//   Resolution: Documented as v0.x known scope boundary. No PdfSharp NuGet added.
//   Severity: MEDIUM (no existing customer requirement for non-Latin PDF at this stage).

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Fods;

/// <summary>
/// Result returned by <see cref="FodsPdfExporter.ExportToPdf"/>.
/// </summary>
public sealed class FodsPdfExportResult
{
    /// <summary>Path to the generated PDF file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Number of pages written (one per sheet).</summary>
    public int PageCount { get; init; }

    /// <summary>Number of sheets processed.</summary>
    public int SheetCount { get; init; }

    /// <summary>Total rows written across all pages.</summary>
    public int TotalRowsWritten { get; init; }
}

/// <summary>
/// G11-E Expanded Prototype: Exports a FODS spreadsheet to a PDF document.
///
/// Scope:
///   - Each sheet produces one PDF page.
///   - Sheet name rendered as a bold-style heading using Helvetica-Bold.
///   - Rows rendered as tab-separated text lines using Helvetica.
///   - Output: PDF 1.4, ASCII-safe (non-ASCII cells are transliterated with '?').
///   - Page size: A4 (595 × 842 pt).
///   - Left margin: 50 pt; top margin: 800 pt; line height: 14 pt.
///
/// Limitations (prototype):
///   - No Unicode beyond Latin-1 (PDF standard fonts are Latin-1 encoded).
///   - No formula evaluation — raw cell text only.
///   - No merged-cell handling.
///   - No cell formatting (bold, colour, alignment).
///   - Column widths are fixed (tab-separated). Values that exceed column width wrap visually.
///
/// Security:
///   - File-size guard via <see cref="FodsDocument.MaxFileSizeBytes"/>.
///   - PDF special characters in cell text are escaped (parentheses, backslash).
///
/// ODF basis: §9.4.2 table:table, §9.4.4 table:table-row, §9.4.5 table:table-cell
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodsPdfExporter
{
    // A4 page in PDF points (1 pt = 1/72 inch)
    private const double PageWidth = 595.0;
    private const double PageHeight = 842.0;
    private const double MarginLeft = 50.0;
    private const double MarginTop = 800.0;
    private const double LineHeight = 14.0;
    private const int FontSizeHeading = 12;
    private const int FontSizeBody = 9;
    // Maximum rows per page before wrapping to next page
    private const int MaxRowsPerPage = 50;

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export all sheets to PDF at <paramref name="pdfPath"/>.
    /// </summary>
    public static FodsPdfExportResult ExportToPdf(
        string fodsPath,
        string pdfPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new ArgumentNullException(nameof(fodsPath));
        if (string.IsNullOrWhiteSpace(pdfPath))
            throw new ArgumentNullException(nameof(pdfPath));

        var doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        return ExportToPdf(doc, pdfPath);
    }

    /// <summary>
    /// Export an already-loaded <see cref="FodsDocument"/> to PDF at <paramref name="pdfPath"/>.
    /// </summary>
    public static FodsPdfExportResult ExportToPdf(FodsDocument document, string pdfPath)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        if (string.IsNullOrWhiteSpace(pdfPath))
            throw new ArgumentNullException(nameof(pdfPath));

        var sheetNames = document.GetSheetNames();
        var pages = BuildPages(document, sheetNames);

        using var stream = new FileStream(pdfPath, FileMode.Create, FileAccess.Write, FileShare.None);
        int totalRows = WritePdf(stream, pages);

        return new FodsPdfExportResult
        {
            OutputPath = pdfPath,
            PageCount = pages.Count,
            SheetCount = sheetNames.Count,
            TotalRowsWritten = totalRows,
        };
    }

    /// <summary>
    /// Export a FODS document to a PDF byte array (no file I/O).
    /// </summary>
    public static byte[] ExportToPdfBytes(FodsDocument document)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));

        var sheetNames = document.GetSheetNames();
        var pages = BuildPages(document, sheetNames);

        using var ms = new MemoryStream();
        WritePdf(ms, pages);
        return ms.ToArray();
    }

    // -------------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------------

    private sealed class PdfPage
    {
        public string SheetName { get; init; } = string.Empty;
        public List<string[]> Rows { get; init; } = new();
    }

    private static List<PdfPage> BuildPages(FodsDocument doc, IReadOnlyList<string> sheetNames)
    {
        var pages = new List<PdfPage>();
        foreach (var name in sheetNames)
        {
            var sheet = doc.GetSheetByName(name);
            if (sheet is null) continue;

            int rowCount = doc.GetRowCount(name);
            int colCount = doc.GetColumnCount(name);

            var rows = new List<string[]>();
            for (int r = 0; r < rowCount; r++)
            {
                var vals = doc.GetRowValues(name, r);
                var cells = new string[colCount];
                for (int c = 0; c < colCount; c++)
                    cells[c] = (c < vals.Count ? vals[c] : null) ?? string.Empty;
                rows.Add(cells);
            }
            pages.Add(new PdfPage { SheetName = name, Rows = rows });
        }
        return pages;
    }

    /// <summary>
    /// Write a minimal PDF 1.4 document to <paramref name="stream"/>.
    /// Returns total row count written.
    /// </summary>
    private static int WritePdf(Stream stream, List<PdfPage> pages)
    {
        // We build object bytes in memory, tracking byte offsets for the xref table.
        var writer = new PdfWriter(stream);

        writer.WriteHeader();

        // We'll collect: (objectNumber, offset, stream bytes?)
        var objects = new List<(int ObjNum, long Offset, byte[] Bytes)>();
        int nextObj = 1;

        // Object 1: Catalog (reference to Pages — obj 2)
        int catalogObj = nextObj++;
        int pagesObj = nextObj++;

        // Font objects: Helvetica (body) and Helvetica-Bold (heading)
        int fontBodyObj = nextObj++;
        int fontHeadingObj = nextObj++;

        // Page objects and content stream objects
        var pageObjNums = new List<int>();
        var contentData = new List<(int PageObjNum, int ContentObjNum, byte[] ContentBytes)>();
        int totalRows = 0;

        foreach (var page in pages)
        {
            int pageObj = nextObj++;
            int contentObj = nextObj++;
            pageObjNums.Add(pageObj);

            byte[] contentBytes = BuildPageContent(page, fontBodyObj, fontHeadingObj, ref totalRows);
            contentData.Add((pageObj, contentObj, contentBytes));
        }

        // Now write objects in order, tracking offsets
        long offset;

        // Catalog
        offset = writer.Position;
        byte[] catalogBytes = Encoding.ASCII.GetBytes(
            $"{catalogObj} 0 obj\n<< /Type /Catalog /Pages {pagesObj} 0 R >>\nendobj\n");
        objects.Add((catalogObj, offset, catalogBytes));
        writer.WriteRaw(catalogBytes);

        // Pages tree
        offset = writer.Position;
        var kidsStr = new StringBuilder();
        foreach (var pn in pageObjNums)
            kidsStr.Append($"{pn} 0 R ");
        byte[] pagesBytes = Encoding.ASCII.GetBytes(
            $"{pagesObj} 0 obj\n<< /Type /Pages /Count {pageObjNums.Count} /Kids [ {kidsStr}] >>\nendobj\n");
        objects.Add((pagesObj, offset, pagesBytes));
        writer.WriteRaw(pagesBytes);

        // Font body: Helvetica
        offset = writer.Position;
        byte[] fontBodyBytes = Encoding.ASCII.GetBytes(
            $"{fontBodyObj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n");
        objects.Add((fontBodyObj, offset, fontBodyBytes));
        writer.WriteRaw(fontBodyBytes);

        // Font heading: Helvetica-Bold
        offset = writer.Position;
        byte[] fontHeadBytes = Encoding.ASCII.GetBytes(
            $"{fontHeadingObj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n");
        objects.Add((fontHeadingObj, offset, fontHeadBytes));
        writer.WriteRaw(fontHeadBytes);

        // Page and content objects
        foreach (var (pageObj, contentObj, contentBytes) in contentData)
        {
            // Content stream
            offset = writer.Position;
            byte[] contentHeader = Encoding.ASCII.GetBytes(
                $"{contentObj} 0 obj\n<< /Length {contentBytes.Length} >>\nstream\n");
            byte[] contentFooter = Encoding.ASCII.GetBytes("\nendstream\nendobj\n");
            var fullContent = new byte[contentHeader.Length + contentBytes.Length + contentFooter.Length];
            Buffer.BlockCopy(contentHeader, 0, fullContent, 0, contentHeader.Length);
            Buffer.BlockCopy(contentBytes, 0, fullContent, contentHeader.Length, contentBytes.Length);
            Buffer.BlockCopy(contentFooter, 0, fullContent, contentHeader.Length + contentBytes.Length, contentFooter.Length);
            objects.Add((contentObj, offset, fullContent));
            writer.WriteRaw(fullContent);

            // Page dictionary
            offset = writer.Position;
            byte[] pageBytes = Encoding.ASCII.GetBytes(
                $"{pageObj} 0 obj\n" +
                $"<< /Type /Page /Parent {pagesObj} 0 R " +
                $"/MediaBox [ 0 0 {(int)PageWidth} {(int)PageHeight} ] " +
                $"/Contents {contentObj} 0 R " +
                $"/Resources << /Font << /F1 {fontBodyObj} 0 R /F2 {fontHeadingObj} 0 R >> >> >>\n" +
                $"endobj\n");
            objects.Add((pageObj, offset, pageBytes));
            writer.WriteRaw(pageBytes);
        }

        // Cross-reference table
        long xrefOffset = writer.Position;
        int totalObjects = objects.Count + 1; // +1 for object 0
        var xref = new StringBuilder();
        xref.Append("xref\n");
        xref.Append($"0 {totalObjects}\n");
        xref.Append("0000000000 65535 f \n");  // object 0 (free list head)

        // Sort by object number
        objects.Sort((a, b) => a.ObjNum.CompareTo(b.ObjNum));
        foreach (var (_, objOffset, _) in objects)
            xref.Append($"{objOffset:D10} 00000 n \n");

        writer.WriteRaw(Encoding.ASCII.GetBytes(xref.ToString()));

        // Trailer
        byte[] trailer = Encoding.ASCII.GetBytes(
            $"trailer\n<< /Size {totalObjects} /Root {catalogObj} 0 R >>\n" +
            $"startxref\n{xrefOffset}\n%%EOF\n");
        writer.WriteRaw(trailer);

        return totalRows;
    }

    private static byte[] BuildPageContent(PdfPage page, int fontBodyObj, int fontHeadObj, ref int totalRows)
    {
        // Build PDF content stream: BT ... ET blocks
        var sb = new StringBuilder();
        double y = MarginTop;

        // Heading: sheet name in Helvetica-Bold
        sb.AppendLine("BT");
        sb.AppendLine($"/F2 {FontSizeHeading} Tf");
        sb.AppendLine($"{MarginLeft} {y:F1} Td");
        sb.AppendLine($"({PdfEscape(page.SheetName)}) Tj");
        sb.AppendLine("ET");
        y -= LineHeight * 1.5;

        int rowsOnPage = 0;
        foreach (var row in page.Rows)
        {
            if (rowsOnPage >= MaxRowsPerPage)
                break;  // prototype: truncate at max rows

            // Join cells with fixed-width spacing (tab-like)
            var lineText = BuildRowText(row);

            sb.AppendLine("BT");
            sb.AppendLine($"/F1 {FontSizeBody} Tf");
            sb.AppendLine($"{MarginLeft} {y:F1} Td");
            sb.AppendLine($"({PdfEscape(lineText)}) Tj");
            sb.AppendLine("ET");
            y -= LineHeight;
            rowsOnPage++;
            totalRows++;
        }

        return Encoding.Latin1.GetBytes(sb.ToString());
    }

    private static string BuildRowText(string[] cells)
    {
        // Fixed column width of 12 characters, truncated
        const int ColWidth = 12;
        var sb = new StringBuilder();
        for (int i = 0; i < cells.Length && i < 8; i++)
        {
            if (i > 0) sb.Append("  ");
            var cell = cells[i];
            if (cell.Length > ColWidth)
                cell = cell[..ColWidth];
            sb.Append(cell.PadRight(ColWidth));
        }
        return sb.ToString().TrimEnd();
    }

    /// <summary>Escape PDF string special characters: ( ) \</summary>
    private static string PdfEscape(string text)
    {
        // Replace non-Latin-1 with '?', then escape PDF specials
        var sb = new StringBuilder(text.Length);
        foreach (char c in text)
        {
            if (c > 255) { sb.Append('?'); continue; }
            if (c == '(' || c == ')' || c == '\\') sb.Append('\\');
            sb.Append(c);
        }
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // Low-level PDF stream writer
    // -------------------------------------------------------------------------

    private sealed class PdfWriter
    {
        private readonly Stream _stream;

        public PdfWriter(Stream stream) => _stream = stream;

        public long Position => _stream.Position;

        public void WriteHeader()
        {
            // PDF header + binary comment (marks file as binary for transfer agents)
            var header = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"u8.ToArray();
            _stream.Write(header);
        }

        public void WriteRaw(byte[] data) => _stream.Write(data, 0, data.Length);
    }
}
