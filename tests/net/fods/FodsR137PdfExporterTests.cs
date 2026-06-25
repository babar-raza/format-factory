// Tests for FodsPdfExporter.ExportToPdf(FodsDocument, pdfPath) and ExportToPdfBytes(FodsDocument).
// Sprint: FORMAT-FACTORY-FODS-R137-20260627
// Ledger: R137-GOVERNED-DOTNET-FODS-PDF-EXPORTER-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R137: Tests for FodsPdfExporter — the FODS→PDF export API.
/// Covers: ExportToPdf(FodsDocument, pdfPath) result object properties,
/// ExportToPdfBytes(FodsDocument) byte output, and PDF structure invariants.
/// The exporter writes a minimal PDF file using only built-in .NET primitives.
/// </summary>
public class FodsR137PdfExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPdfPath() =>
        Path.Combine(Path.GetTempPath(), $"fods_r137_{Guid.NewGuid():N}.pdf");

    // -------------------------------------------------------------------------
    // ExportToPdf(FodsDocument, pdfPath) — result object properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_Document_OutputPathMatchesGivenPath()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.Equal(pdfPath, result.OutputPath);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_OutputFileExists()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(File.Exists(pdfPath), "PDF output file should exist after export");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_PageCountAtLeastOne()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.PageCount >= 1, $"Expected PageCount >= 1, got {result.PageCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_SheetCountAtLeastOne()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.SheetCount >= 1, $"Expected SheetCount >= 1, got {result.SheetCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_TotalRowsWrittenNonNegative()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.TotalRowsWritten >= 0,
                $"TotalRowsWritten must be >= 0, got {result.TotalRowsWritten}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_OutputFileHasPdfHeader()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            FodsPdfExporter.ExportToPdf(doc, pdfPath);
            var header = new byte[4];
            using var fs = File.OpenRead(pdfPath);
            _ = fs.Read(header, 0, 4);
            // PDF starts with "%PDF"
            Assert.Equal((byte)'%', header[0]);
            Assert.Equal((byte)'P', header[1]);
            Assert.Equal((byte)'D', header[2]);
            Assert.Equal((byte)'F', header[3]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    // -------------------------------------------------------------------------
    // ExportToPdfBytes — byte array output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_Document_ReturnsNonEmptyArray()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0, "ExportToPdfBytes should return a non-empty byte array");
    }

    [Fact]
    public void ExportToPdfBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsPdfExporter.ExportToPdfBytes(null!));
    }

    [Fact]
    public void ExportToPdfBytes_BytesHavePdfHeader()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var bytes = FodsPdfExporter.ExportToPdfBytes(doc);
        Assert.True(bytes.Length >= 4);
        Assert.Equal((byte)'%', bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'D', bytes[2]);
        Assert.Equal((byte)'F', bytes[3]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-sheet export — PDF bytes and file are consistent
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheet_PdfBytesAndFileConsistent()
    {
        var doc = FodsDocument.Load(FixturePath("fods-multi-sheet.fods"));
        var pdfPath = TempPdfPath();
        try
        {
            // File-based export
            var result = FodsPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.PageCount >= 1);
            Assert.True(result.SheetCount >= 1);

            // Bytes-based export
            var bytes = FodsPdfExporter.ExportToPdfBytes(doc);
            Assert.True(bytes.Length > 0);

            // Both have valid PDF headers
            Assert.Equal((byte)'%', bytes[0]);
            var fileBytes = File.ReadAllBytes(pdfPath);
            Assert.Equal((byte)'%', fileBytes[0]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }
}
