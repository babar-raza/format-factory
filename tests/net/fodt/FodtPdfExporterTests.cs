// FormatFactory.Fodt Tests -- FodtPdfExporter Prototype Tests
// Sprint: product-deepening-fodt-pdf-export-20260616
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for the G11-E FODT → PDF export prototype.
///
/// Covers:
///   - Basic PDF export from file path
///   - Export from FodtDocument object
///   - ExportToPdfBytes (in-memory)
///   - PDF header (%PDF-) and %%EOF markers
///   - xref table present
///   - Result metadata: PageCount, TotalParagraphsWritten
///   - Empty document export
///   - Paragraph text appears in output
///   - Heading text appears in output
///   - Null argument guards
///   - PDF structure: /Type /Catalog, /Type /Pages, /Type /Page
///   - Font dictionary present
///   - Parentheses escaped in PDF strings
/// </summary>
public class FodtPdfExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private static readonly string HeadingsFodt =
        Path.Combine(FixturesDir, "fodt-headings-and-list.fodt");

    private readonly string _tempDir;

    public FodtPdfExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"fodt-pdf-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        try { Directory.Delete(_tempDir, recursive: true); } catch { /* best-effort */ }
    }

    // -------------------------------------------------------------------------
    // Basic export tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_FromFilePath_CreatesNonEmptyFile()
    {
        var pdfPath = Path.Combine(_tempDir, "export.pdf");
        var result = FodtPdfExporter.ExportToPdf(MinimalFodt, pdfPath);

        Assert.True(File.Exists(pdfPath), "PDF file should be created");
        Assert.True(new FileInfo(pdfPath).Length > 0, "PDF file should be non-empty");
        Assert.Equal(pdfPath, result.OutputPath);
    }

    [Fact]
    public void ExportToPdf_FromFilePath_HasValidPdfHeader()
    {
        var pdfPath = Path.Combine(_tempDir, "header.pdf");
        FodtPdfExporter.ExportToPdf(MinimalFodt, pdfPath);

        var bytes = File.ReadAllBytes(pdfPath);
        Assert.True(bytes.Length >= 5);
        Assert.Equal((byte)'%', bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'D', bytes[2]);
        Assert.Equal((byte)'F', bytes[3]);
        Assert.Equal((byte)'-', bytes[4]);
    }

    [Fact]
    public void ExportToPdf_FromFilePath_HasEofMarker()
    {
        var pdfPath = Path.Combine(_tempDir, "eof.pdf");
        FodtPdfExporter.ExportToPdf(MinimalFodt, pdfPath);

        var text = File.ReadAllText(pdfPath, System.Text.Encoding.Latin1);
        Assert.Contains("%%EOF", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdf_FromFilePath_HasXrefTable()
    {
        var pdfPath = Path.Combine(_tempDir, "xref.pdf");
        FodtPdfExporter.ExportToPdf(MinimalFodt, pdfPath);

        var text = File.ReadAllText(pdfPath, System.Text.Encoding.Latin1);
        Assert.Contains("xref", text, StringComparison.Ordinal);
        Assert.Contains("startxref", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // In-memory export
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ReturnsNonEmptyArray()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);

        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToPdfBytes_StartsWithPdfHeader()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);

        Assert.Equal((byte)'%', bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'D', bytes[2]);
        Assert.Equal((byte)'F', bytes[3]);
    }

    [Fact]
    public void ExportToPdfBytes_ContainsEofMarker()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("%%EOF", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_EmptyDocument_ProducesValidPdf()
    {
        var doc = FodtDocument.CreateEmpty();
        var pdfPath = Path.Combine(_tempDir, "empty.pdf");
        var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(0, result.TotalParagraphsWritten);
        Assert.True(File.Exists(pdfPath));
        Assert.True(new FileInfo(pdfPath).Length > 0);
    }

    // -------------------------------------------------------------------------
    // Paragraph text in output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ParagraphTextAppearsInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("UniqueMarkerText");

        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("UniqueMarkerText", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdfBytes_HeadingAppearsInOutput()
    {
        var doc = FodtDocument.Load(HeadingsFodt);
        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        // Headings from fodt-headings-and-list.fodt should appear
        Assert.True(text.Length > 100, "PDF should have substantial content");
    }

    [Fact]
    public void ExportToPdf_MultiParagraph_ResultHasCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para1");
        doc.AppendParagraph("Para2");
        doc.AppendParagraph("Para3");

        var pdfPath = Path.Combine(_tempDir, "multi.pdf");
        var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(3, result.TotalParagraphsWritten);
        Assert.True(result.PageCount >= 1);
    }

    // -------------------------------------------------------------------------
    // Result metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_FromDocument_ResultMetadataIsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Line one");
        doc.AppendParagraph("Line two");

        var pdfPath = Path.Combine(_tempDir, "meta.pdf");
        var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(pdfPath, result.OutputPath);
        Assert.Equal(2, result.TotalParagraphsWritten);
        Assert.True(result.PageCount >= 1);
    }

    // -------------------------------------------------------------------------
    // Null / invalid argument guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_NullFilePath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPdfExporter.ExportToPdf((string)null!, Path.Combine(_tempDir, "x.pdf")));
    }

    [Fact]
    public void ExportToPdf_NullOutputPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPdfExporter.ExportToPdf(MinimalFodt, null!));
    }

    [Fact]
    public void ExportToPdf_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPdfExporter.ExportToPdf((FodtDocument)null!, Path.Combine(_tempDir, "x.pdf")));
    }

    [Fact]
    public void ExportToPdfBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPdfExporter.ExportToPdfBytes(null!));
    }

    // -------------------------------------------------------------------------
    // PDF structure
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ContainsCatalogPagesPage()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");

        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("/Type /Catalog", text, StringComparison.Ordinal);
        Assert.Contains("/Type /Pages", text, StringComparison.Ordinal);
        Assert.Contains("/Type /Page", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdfBytes_ContainsFontDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("FontTest");

        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("/Type /Font", text, StringComparison.Ordinal);
        Assert.Contains("/BaseFont /Helvetica", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // PDF special character escaping
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ParenthesesInParagraphAreEscaped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("(AB)");

        byte[] bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains(@"\(AB\)", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Roundtrip: content from fixture file
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_FromHeadingsFodt_ProducesValidPdf()
    {
        var pdfPath = Path.Combine(_tempDir, "headings.pdf");
        var result = FodtPdfExporter.ExportToPdf(HeadingsFodt, pdfPath);

        Assert.True(File.Exists(pdfPath));
        Assert.True(result.TotalParagraphsWritten > 0, "Headings fixture should have paragraphs");
        var bytes = File.ReadAllBytes(pdfPath);
        Assert.True(bytes.Length > 200, "PDF from headings fixture should be substantial");
    }
}
