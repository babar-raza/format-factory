// Tests for FodtPdfExporter.ExportToPdf(string fodtPath, string pdfPath) and
// FodtPngExporter.ExportToPng(string fodtPath, string pngPath) path-based overloads.
// Sprint: FORMAT-FACTORY-FODT-R140-20260627
// Ledger: R140-GOVERNED-DOTNET-FODT-PATH-EXPORTERS-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R140: Tests for the path-based exporter overloads:
/// FodtPdfExporter.ExportToPdf(string fodtPath, string pdfPath) and
/// FodtPngExporter.ExportToPng(string fodtPath, string pngPath).
/// These overloads load the FODT from disk before exporting — distinct from
/// the FodtDocument-based overloads tested in R138/R139.
/// Covers: output file exists; %PDF / PNG signature headers; result properties;
/// null/whitespace guards; fixture file pipeline; dogfood roundtrip.
/// </summary>
public class FodtR140PathExportersTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPdfPath() =>
        Path.Combine(Path.GetTempPath(), $"fodt_r140_{Guid.NewGuid():N}.pdf");

    private static string TempPngPath() =>
        Path.Combine(Path.GetTempPath(), $"fodt_r140_{Guid.NewGuid():N}.png");

    // -------------------------------------------------------------------------
    // FodtPdfExporter.ExportToPdf(string, string) — path-based overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_Path_OutputFileExists()
    {
        var pdfPath = TempPdfPath();
        try
        {
            FodtPdfExporter.ExportToPdf(FixturePath("fodt-minimal-roundtrip.fodt"), pdfPath);
            Assert.True(File.Exists(pdfPath), "PDF output file should exist");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_OutputPathMatchesGivenPath()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(FixturePath("fodt-minimal-roundtrip.fodt"), pdfPath);
            Assert.Equal(pdfPath, result.OutputPath);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_OutputHasPdfHeader()
    {
        var pdfPath = TempPdfPath();
        try
        {
            FodtPdfExporter.ExportToPdf(FixturePath("fodt-minimal-roundtrip.fodt"), pdfPath);
            var header = new byte[4];
            using var fs = File.OpenRead(pdfPath);
            _ = fs.Read(header, 0, 4);
            Assert.Equal((byte)'%', header[0]);
            Assert.Equal((byte)'P', header[1]);
            Assert.Equal((byte)'D', header[2]);
            Assert.Equal((byte)'F', header[3]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_PageCountAtLeastOne()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(FixturePath("fodt-minimal-roundtrip.fodt"), pdfPath);
            Assert.True(result.PageCount >= 1, $"Expected PageCount >= 1, got {result.PageCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_NullFodtPath_ThrowsArgumentNullException()
    {
        var pdfPath = TempPdfPath();
        Assert.Throws<ArgumentNullException>(() => FodtPdfExporter.ExportToPdf(null!, pdfPath));
    }

    [Fact]
    public void ExportToPdf_Path_EmptyFodtPath_ThrowsArgumentNullException()
    {
        var pdfPath = TempPdfPath();
        Assert.Throws<ArgumentNullException>(() => FodtPdfExporter.ExportToPdf(string.Empty, pdfPath));
    }

    // -------------------------------------------------------------------------
    // FodtPngExporter.ExportToPng(string, string) — path-based overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_Path_OutputFileExists()
    {
        var pngPath = TempPngPath();
        try
        {
            FodtPngExporter.ExportToPng(FixturePath("fodt-minimal-roundtrip.fodt"), pngPath);
            Assert.True(File.Exists(pngPath), "PNG output file should exist");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_OutputHasPngSignature()
    {
        var pngPath = TempPngPath();
        try
        {
            FodtPngExporter.ExportToPng(FixturePath("fodt-minimal-roundtrip.fodt"), pngPath);
            var header = new byte[8];
            using var fs = File.OpenRead(pngPath);
            _ = fs.Read(header, 0, 8);
            Assert.Equal(137, header[0]);
            Assert.Equal(80, header[1]);   // 'P'
            Assert.Equal(78, header[2]);   // 'N'
            Assert.Equal(71, header[3]);   // 'G'
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_WidthPxPositive()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(FixturePath("fodt-minimal-roundtrip.fodt"), pngPath);
            Assert.True(result.WidthPx > 0, $"Expected WidthPx > 0, got {result.WidthPx}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_NullFodtPath_ThrowsArgumentNullException()
    {
        var pngPath = TempPngPath();
        Assert.Throws<ArgumentNullException>(() => FodtPngExporter.ExportToPng(null!, pngPath));
    }

    // -------------------------------------------------------------------------
    // Dogfood: headings fixture — path-based PDF + PNG pipeline consistent
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingsFixture_PdfAndPngBothExport()
    {
        var pdfPath = TempPdfPath();
        var pngPath = TempPngPath();
        try
        {
            var fodtPath = FixturePath("fodt-headings-and-list.fodt");

            var pdfResult = FodtPdfExporter.ExportToPdf(fodtPath, pdfPath);
            var pngResult = FodtPngExporter.ExportToPng(fodtPath, pngPath);

            // Both files exist
            Assert.True(File.Exists(pdfPath));
            Assert.True(File.Exists(pngPath));

            // PDF header
            var pdfBytes = File.ReadAllBytes(pdfPath);
            Assert.Equal((byte)'%', pdfBytes[0]);

            // PNG signature
            var pngBytes = File.ReadAllBytes(pngPath);
            Assert.Equal(137, pngBytes[0]);

            // Result properties
            Assert.True(pdfResult.PageCount >= 1);
            Assert.True(pngResult.WidthPx > 0);
        }
        finally
        {
            if (File.Exists(pdfPath)) File.Delete(pdfPath);
            if (File.Exists(pngPath)) File.Delete(pngPath);
        }
    }
}
