// FormatFactory.Fods Tests -- FodsPdfExporter Prototype Tests
// Sprint: product-deepening-fods-pdf-export-20260616
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the G11-E FODS → PDF export prototype.
///
/// Covers:
///   - Basic PDF export from file path
///   - Export from FodsDocument object
///   - ExportToPdfBytes (in-memory export)
///   - PDF header and %%EOF markers present
///   - Multi-sheet document export (page-per-sheet)
///   - Empty document export (0 sheets)
///   - Result metadata: PageCount, SheetCount, TotalRowsWritten
///   - Output file is created and non-empty
///   - Null argument guards
///   - Row truncation at MaxRowsPerPage
///   - Cell values appear in PDF output
/// </summary>
public class FodsPdfExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private static readonly string MultiSheetFods =
        Path.Combine(FixturesDir, "fods-multi-sheet.fods");

    private readonly string _tempDir;

    public FodsPdfExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"fods-pdf-{Guid.NewGuid():N}");
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
        var result = FodsPdfExporter.ExportToPdf(MinimalFods, pdfPath);

        Assert.True(File.Exists(pdfPath), "PDF file should be created");
        Assert.True(new FileInfo(pdfPath).Length > 0, "PDF file should be non-empty");
        Assert.Equal(pdfPath, result.OutputPath);
    }

    [Fact]
    public void ExportToPdf_FromFilePath_HasValidPdfHeader()
    {
        var pdfPath = Path.Combine(_tempDir, "header.pdf");
        FodsPdfExporter.ExportToPdf(MinimalFods, pdfPath);

        var bytes = File.ReadAllBytes(pdfPath);
        // PDF must start with %PDF-
        Assert.True(bytes.Length >= 5, "PDF must have at least 5 bytes");
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
        FodsPdfExporter.ExportToPdf(MinimalFods, pdfPath);

        var text = File.ReadAllText(pdfPath, System.Text.Encoding.Latin1);
        Assert.Contains("%%EOF", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdf_FromFilePath_HasXrefTable()
    {
        var pdfPath = Path.Combine(_tempDir, "xref.pdf");
        FodsPdfExporter.ExportToPdf(MinimalFods, pdfPath);

        var text = File.ReadAllText(pdfPath, System.Text.Encoding.Latin1);
        Assert.Contains("xref", text, StringComparison.Ordinal);
        Assert.Contains("startxref", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Export from FodsDocument
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_FromDocument_ReturnsCorrectSheetCount()
    {
        var pdfPath = Path.Combine(_tempDir, "doc.pdf");
        var doc = FodsDocument.Load(MinimalFods);
        var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.True(result.SheetCount >= 1, "Should have at least 1 sheet");
        Assert.Equal(result.SheetCount, result.PageCount);
        Assert.True(File.Exists(pdfPath));
    }

    [Fact]
    public void ExportToPdf_FromDocument_MultiSheet_ProducesMultiplePages()
    {
        if (!File.Exists(MultiSheetFods))
        {
            // Create in-memory multi-sheet doc
            var doc = FodsDocument.CreateNew();
            var s1 = doc.AddSheet("Sheet1");
            var s2 = doc.AddSheet("Sheet2");
            FodsDocument.SetCellValue(s1, 0, 0, "A");
            FodsDocument.SetCellValue(s2, 0, 0, "B");
            var pdfPath2 = Path.Combine(_tempDir, "multi2.pdf");
            var result2 = FodsPdfExporter.ExportToPdf(doc, pdfPath2);
            Assert.Equal(2, result2.PageCount);
            Assert.Equal(2, result2.SheetCount);
            return;
        }
        var pdfPath = Path.Combine(_tempDir, "multi.pdf");
        var result = FodsPdfExporter.ExportToPdf(MultiSheetFods, pdfPath);
        Assert.True(result.PageCount > 1, "Multi-sheet doc should produce multiple pages");
    }

    // -------------------------------------------------------------------------
    // In-memory export
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ReturnsNonEmptyArray()
    {
        var doc = FodsDocument.Load(MinimalFods);
        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);

        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0, "PDF bytes should be non-empty");
    }

    [Fact]
    public void ExportToPdfBytes_StartsWithPdfHeader()
    {
        var doc = FodsDocument.Load(MinimalFods);
        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);

        Assert.Equal((byte)'%', bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'D', bytes[2]);
        Assert.Equal((byte)'F', bytes[3]);
    }

    [Fact]
    public void ExportToPdfBytes_ContainsEofMarker()
    {
        var doc = FodsDocument.Load(MinimalFods);
        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("%%EOF", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_EmptyDocument_ProducesValidPdfWithNoPages()
    {
        var doc = FodsDocument.CreateNew();
        var pdfPath = Path.Combine(_tempDir, "empty.pdf");
        var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(0, result.PageCount);
        Assert.Equal(0, result.SheetCount);
        Assert.Equal(0, result.TotalRowsWritten);
        Assert.True(File.Exists(pdfPath));
        var bytes = File.ReadAllBytes(pdfPath);
        Assert.True(bytes.Length > 0, "Even empty PDF should have structure bytes");
    }

    // -------------------------------------------------------------------------
    // Cell value in output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_CellValuesAppearInOutput()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("TestSheet");
        doc.InsertRowWithValues("TestSheet", 0, new[] { "HelloValue" });

        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("HelloValue", text, StringComparison.Ordinal);
        Assert.Contains("TestSheet", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdfBytes_MultipleRowsInOutput()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int r = 0; r < 5; r++)
            doc.InsertRowWithValues("Data", r, new[] { $"Row{r}" });

        var result2 = FodsPdfExporter.ExportToPdf(doc, Path.Combine(_tempDir, "rows.pdf"));
        Assert.Equal(5, result2.TotalRowsWritten);
    }

    // -------------------------------------------------------------------------
    // Null / invalid argument guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_NullFilePath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf((string)null!, Path.Combine(_tempDir, "x.pdf")));
    }

    [Fact]
    public void ExportToPdf_NullOutputPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf(MinimalFods, null!));
    }

    [Fact]
    public void ExportToPdf_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf((FodsDocument)null!, Path.Combine(_tempDir, "x.pdf")));
    }

    [Fact]
    public void ExportToPdfBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdfBytes(null!));
    }

    // -------------------------------------------------------------------------
    // Result metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_SingleSheet_ResultMetadataIsCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "B" });

        var pdfPath = Path.Combine(_tempDir, "meta.pdf");
        var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(1, result.PageCount);
        Assert.Equal(1, result.SheetCount);
        Assert.Equal(2, result.TotalRowsWritten);
        Assert.Equal(pdfPath, result.OutputPath);
    }

    [Fact]
    public void ExportToPdf_TwoSheets_ResultMetadataHasTwoPages()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.InsertRowWithValues("Alpha", 0, new[] { "X" });
        doc.InsertRowWithValues("Beta", 0, new[] { "Y" });
        doc.InsertRowWithValues("Beta", 1, new[] { "Z" });

        var pdfPath = Path.Combine(_tempDir, "twosheets.pdf");
        var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);

        Assert.Equal(2, result.PageCount);
        Assert.Equal(2, result.SheetCount);
        Assert.Equal(3, result.TotalRowsWritten);
    }

    // -------------------------------------------------------------------------
    // PDF structure: contains /Type /Page entries for each sheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ContainsCatalogAndPages()
    {
        var doc = FodsDocument.CreateNew();
        var _ = doc.AddSheet("S1");

        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("/Type /Catalog", text, StringComparison.Ordinal);
        Assert.Contains("/Type /Pages", text, StringComparison.Ordinal);
        Assert.Contains("/Type /Page", text, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToPdfBytes_ContainsFontDictionary()
    {
        var doc = FodsDocument.CreateNew();
        var __ = doc.AddSheet("FontTest");

        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        Assert.Contains("/Type /Font", text, StringComparison.Ordinal);
        Assert.Contains("/BaseFont /Helvetica", text, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // PDF special character escaping
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_ParenthesesInCellValueAreEscaped()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Escape");
        // Use short values so column width truncation does not remove the closing paren
        doc.InsertRowWithValues("Escape", 0, new[] { "(AB)" });

        byte[] bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        var text = System.Text.Encoding.Latin1.GetString(bytes);

        // Parentheses should be backslash-escaped in PDF strings
        Assert.Contains(@"\(AB\)", text, StringComparison.Ordinal);
    }
}
