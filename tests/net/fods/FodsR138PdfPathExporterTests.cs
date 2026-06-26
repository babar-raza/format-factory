// Tests for FodsPdfExporter.ExportToPdf(string fodsPath, string pdfPath) — path-based overload.
// Sprint: FORMAT-FACTORY-FODS-R138-20260627
// Ledger: R138-GOVERNED-DOTNET-FODS-PDF-PATH-EXPORTER-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R138: Tests for the path-based FodsPdfExporter overload:
/// FodsPdfExporter.ExportToPdf(string fodsPath, string pdfPath).
/// This overload loads the FODS file from disk before exporting — distinct from
/// the FodsDocument-based overload tested in R137.
/// Covers: output file exists; %PDF header bytes; result properties
/// (OutputPath/PageCount/SheetCount/TotalRowsWritten); null/whitespace guards;
/// single-sheet and multi-sheet fixture pipelines.
/// </summary>
public class FodsR138PdfPathExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPdfPath() =>
        Path.Combine(Path.GetTempPath(), $"fods_r138_{Guid.NewGuid():N}.pdf");

    // -------------------------------------------------------------------------
    // ExportToPdf(string, string) — result object properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_Path_OutputFileExists()
    {
        var pdfPath = TempPdfPath();
        try
        {
            FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
            Assert.True(File.Exists(pdfPath), "PDF output file should exist after path-based export");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_OutputPathMatchesGivenPath()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
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
            FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
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
            var result = FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
            Assert.True(result.PageCount >= 1, $"Expected PageCount >= 1, got {result.PageCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_SheetCountAtLeastOne()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
            Assert.True(result.SheetCount >= 1, $"Expected SheetCount >= 1, got {result.SheetCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Path_TotalRowsWrittenNonNegative()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), pdfPath);
            Assert.True(result.TotalRowsWritten >= 0,
                $"TotalRowsWritten must be >= 0, got {result.TotalRowsWritten}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    // -------------------------------------------------------------------------
    // Null/whitespace guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_Path_NullFodsPath_ThrowsArgumentNullException()
    {
        var pdfPath = TempPdfPath();
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf(null!, pdfPath));
    }

    [Fact]
    public void ExportToPdf_Path_EmptyFodsPath_ThrowsArgumentNullException()
    {
        var pdfPath = TempPdfPath();
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf(string.Empty, pdfPath));
    }

    [Fact]
    public void ExportToPdf_Path_NullPdfPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPdfExporter.ExportToPdf(FixturePath("fods-minimal-roundtrip.fods"), null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-sheet path-based pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheetPath_PdfPropertiesConsistent()
    {
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodsPdfExporter.ExportToPdf(
                FixturePath("fods-multi-sheet.fods"), pdfPath);

            Assert.True(File.Exists(pdfPath));
            Assert.True(result.PageCount >= 1);
            Assert.True(result.SheetCount >= 1);
            Assert.Equal(pdfPath, result.OutputPath);

            // Output has PDF header
            var fileBytes = File.ReadAllBytes(pdfPath);
            Assert.Equal((byte)'%', fileBytes[0]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }
}
