// FormatFactory.Fodt -- Commercial .NET FODT → PDF Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: product-deepening-fodt-pdf-export-20260616
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
//
// Pure .NET PDF 1.4 writer — no NuGet dependencies.
// Renders FODT document paragraphs and headings as text using PDF text operators.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Fodt;

/// <summary>
/// Result returned by <see cref="FodtPdfExporter.ExportToPdf"/>.
/// </summary>
public sealed class FodtPdfExportResult
{
    /// <summary>Path to the generated PDF file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Number of pages written.</summary>
    public int PageCount { get; init; }

    /// <summary>Total paragraphs written.</summary>
    public int TotalParagraphsWritten { get; init; }
}

/// <summary>
/// G11-E Expanded Prototype: Exports a FODT text document to a PDF document.
///
/// Scope:
///   - Paragraphs rendered as body text lines using Helvetica (9pt).
///   - Headings detected via <see cref="FodtDocument.GetHeadingTexts"/> rendered in Helvetica-Bold (12pt).
///   - Output: PDF 1.4, Latin-1 encoded (non-Latin-1 characters replaced with '?').
///   - Page size: A4 (595 × 842 pt). Left margin: 50 pt. Top: 800 pt. Line height: 14 pt.
///   - Long paragraphs are word-wrapped at ~80 characters per line.
///
/// Limitations (prototype):
///   - No Unicode beyond Latin-1.
///   - No inline formatting (bold within paragraph, italic, underline).
///   - No tables, images, or lists (list items rendered as plain text).
///   - Heading detection via text matching against GetHeadingTexts().
///   - Multi-page wrapping: new page added when content exceeds bottom margin.
///
/// Security: all paragraph text is PDF-escaped (parentheses, backslash).
///
/// ODF basis: §5.1.2 text:h, §5.1.3 text:p (ODF 1.3)
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodtPdfExporter
{
    private const double PageWidth = 595.0;
    private const double PageHeight = 842.0;
    private const double MarginLeft = 50.0;
    private const double MarginTop = 800.0;
    private const double MarginBottom = 50.0;
    private const double LineHeight = 14.0;
    private const int FontSizeHeading = 12;
    private const int FontSizeBody = 9;
    private const int WrapWidth = 80;

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodtPath"/> and export to PDF at <paramref name="pdfPath"/>.
    /// </summary>
    public static FodtPdfExportResult ExportToPdf(
        string fodtPath,
        string pdfPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodtPath))
            throw new ArgumentNullException(nameof(fodtPath));
        if (string.IsNullOrWhiteSpace(pdfPath))
            throw new ArgumentNullException(nameof(pdfPath));

        var doc = FodtDocument.Load(fodtPath, maxFileSizeBytes);
        return ExportToPdf(doc, pdfPath);
    }

    /// <summary>
    /// Export an already-loaded <see cref="FodtDocument"/> to PDF at <paramref name="pdfPath"/>.
    /// </summary>
    public static FodtPdfExportResult ExportToPdf(FodtDocument document, string pdfPath)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        if (string.IsNullOrWhiteSpace(pdfPath))
            throw new ArgumentNullException(nameof(pdfPath));

        using var stream = new FileStream(pdfPath, FileMode.Create, FileAccess.Write, FileShare.None);
        var (pageCount, paraCount) = WritePdf(stream, document);
        return new FodtPdfExportResult
        {
            OutputPath = pdfPath,
            PageCount = pageCount,
            TotalParagraphsWritten = paraCount,
        };
    }

    /// <summary>
    /// Export a FODT document to a PDF byte array (no file I/O).
    /// </summary>
    public static byte[] ExportToPdfBytes(FodtDocument document)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        using var ms = new MemoryStream();
        WritePdf(ms, document);
        return ms.ToArray();
    }

    // -------------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------------

    private sealed class RenderLine
    {
        public string Text { get; init; } = string.Empty;
        public bool IsHeading { get; init; }
    }

    private static List<RenderLine> BuildRenderLines(FodtDocument doc)
    {
        var paragraphs = doc.GetParagraphTexts();
        var headingSet = new HashSet<string>(doc.GetHeadingTexts(), StringComparer.Ordinal);
        var lines = new List<RenderLine>();

        foreach (var para in paragraphs)
        {
            if (string.IsNullOrWhiteSpace(para))
            {
                lines.Add(new RenderLine { Text = string.Empty, IsHeading = false });
                continue;
            }

            bool isHeading = headingSet.Contains(para);
            // Word-wrap long paragraphs
            var words = para.Split(' ');
            var sb = new StringBuilder();
            foreach (var word in words)
            {
                if (sb.Length + word.Length + 1 > WrapWidth && sb.Length > 0)
                {
                    lines.Add(new RenderLine { Text = sb.ToString().TrimEnd(), IsHeading = isHeading });
                    sb.Clear();
                    isHeading = false; // continuation lines are not headings
                }
                if (sb.Length > 0) sb.Append(' ');
                sb.Append(word);
            }
            if (sb.Length > 0)
                lines.Add(new RenderLine { Text = sb.ToString().TrimEnd(), IsHeading = isHeading });
        }
        return lines;
    }

    private static (int PageCount, int ParaCount) WritePdf(Stream stream, FodtDocument doc)
    {
        var renderLines = BuildRenderLines(doc);
        var writer = new PdfWriter(stream);
        writer.WriteHeader();

        var objects = new List<(int ObjNum, long Offset, byte[] Bytes)>();
        int nextObj = 1;

        int catalogObj = nextObj++;
        int pagesObj = nextObj++;
        int fontBodyObj = nextObj++;
        int fontHeadingObj = nextObj++;

        // Split lines into pages
        var pages = new List<List<RenderLine>>();
        var currentPage = new List<RenderLine>();
        int linesPerPage = (int)((MarginTop - MarginBottom) / LineHeight);
        foreach (var line in renderLines)
        {
            if (currentPage.Count >= linesPerPage)
            {
                pages.Add(currentPage);
                currentPage = new List<RenderLine>();
            }
            currentPage.Add(line);
        }
        if (currentPage.Count > 0 || pages.Count == 0)
            pages.Add(currentPage);

        var pageObjNums = new List<int>();
        var contentData = new List<(int PageObjNum, int ContentObjNum, byte[] ContentBytes)>();

        foreach (var page in pages)
        {
            int pageObj = nextObj++;
            int contentObj = nextObj++;
            pageObjNums.Add(pageObj);
            byte[] contentBytes = BuildPageContent(page);
            contentData.Add((pageObj, contentObj, contentBytes));
        }

        // Catalog
        long offset = writer.Position;
        byte[] catalogBytes = Encoding.ASCII.GetBytes(
            $"{catalogObj} 0 obj\n<< /Type /Catalog /Pages {pagesObj} 0 R >>\nendobj\n");
        objects.Add((catalogObj, offset, catalogBytes));
        writer.WriteRaw(catalogBytes);

        // Pages tree
        offset = writer.Position;
        var kidsStr = new StringBuilder();
        foreach (var pn in pageObjNums) kidsStr.Append($"{pn} 0 R ");
        byte[] pagesBytes = Encoding.ASCII.GetBytes(
            $"{pagesObj} 0 obj\n<< /Type /Pages /Count {pageObjNums.Count} /Kids [ {kidsStr}] >>\nendobj\n");
        objects.Add((pagesObj, offset, pagesBytes));
        writer.WriteRaw(pagesBytes);

        // Font body
        offset = writer.Position;
        byte[] fontBodyBytes = Encoding.ASCII.GetBytes(
            $"{fontBodyObj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n");
        objects.Add((fontBodyObj, offset, fontBodyBytes));
        writer.WriteRaw(fontBodyBytes);

        // Font heading
        offset = writer.Position;
        byte[] fontHeadBytes = Encoding.ASCII.GetBytes(
            $"{fontHeadingObj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n");
        objects.Add((fontHeadingObj, offset, fontHeadBytes));
        writer.WriteRaw(fontHeadBytes);

        // Page and content stream objects
        foreach (var (pageObj, contentObj, contentBytes) in contentData)
        {
            offset = writer.Position;
            byte[] ch = Encoding.ASCII.GetBytes(
                $"{contentObj} 0 obj\n<< /Length {contentBytes.Length} >>\nstream\n");
            byte[] cf = Encoding.ASCII.GetBytes("\nendstream\nendobj\n");
            var full = new byte[ch.Length + contentBytes.Length + cf.Length];
            Buffer.BlockCopy(ch, 0, full, 0, ch.Length);
            Buffer.BlockCopy(contentBytes, 0, full, ch.Length, contentBytes.Length);
            Buffer.BlockCopy(cf, 0, full, ch.Length + contentBytes.Length, cf.Length);
            objects.Add((contentObj, offset, full));
            writer.WriteRaw(full);

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

        // xref
        long xrefOffset = writer.Position;
        int totalObjects = objects.Count + 1;
        var xref = new StringBuilder();
        xref.Append("xref\n");
        xref.Append($"0 {totalObjects}\n");
        xref.Append("0000000000 65535 f \n");
        objects.Sort((a, b) => a.ObjNum.CompareTo(b.ObjNum));
        foreach (var (_, objOffset, _) in objects)
            xref.Append($"{objOffset:D10} 00000 n \n");
        writer.WriteRaw(Encoding.ASCII.GetBytes(xref.ToString()));

        // Trailer
        byte[] trailer = Encoding.ASCII.GetBytes(
            $"trailer\n<< /Size {totalObjects} /Root {catalogObj} 0 R >>\n" +
            $"startxref\n{xrefOffset}\n%%EOF\n");
        writer.WriteRaw(trailer);

        int paraCount = renderLines.Count(l => !string.IsNullOrEmpty(l.Text));
        return (pages.Count, paraCount);
    }

    private static byte[] BuildPageContent(List<RenderLine> lines)
    {
        var sb = new StringBuilder();
        double y = MarginTop;

        foreach (var line in lines)
        {
            string font = line.IsHeading ? "F2" : "F1";
            int size = line.IsHeading ? FontSizeHeading : FontSizeBody;
            sb.AppendLine("BT");
            sb.AppendLine($"/{font} {size} Tf");
            sb.AppendLine($"{MarginLeft} {y:F1} Td");
            sb.AppendLine($"({PdfEscape(line.Text)}) Tj");
            sb.AppendLine("ET");
            y -= line.IsHeading ? LineHeight * 1.5 : LineHeight;
        }
        return Encoding.Latin1.GetBytes(sb.ToString());
    }

    private static string PdfEscape(string text)
    {
        var sb = new StringBuilder(text.Length);
        foreach (char c in text)
        {
            if (c > 255) { sb.Append('?'); continue; }
            if (c == '(' || c == ')' || c == '\\') sb.Append('\\');
            sb.Append(c);
        }
        return sb.ToString();
    }

    private sealed class PdfWriter
    {
        private readonly Stream _stream;
        public PdfWriter(Stream stream) => _stream = stream;
        public long Position => _stream.Position;

        public void WriteHeader()
        {
            var header = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"u8.ToArray();
            _stream.Write(header);
        }

        public void WriteRaw(byte[] data) => _stream.Write(data, 0, data.Length);
    }
}
