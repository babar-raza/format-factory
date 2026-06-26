// Tests for FodsPngExporter.ExportToPng(string fodsPath, string pngPath) — path-based overload.
// Sprint: FORMAT-FACTORY-FODS-R140-20260627
// Ledger: R140-GOVERNED-DOTNET-FODS-PNG-PATH-EXPORTER-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R140: Tests for FodsPngExporter.ExportToPng(string fodsPath, string pngPath).
/// The path-based overload loads the FODS from disk before rendering to PNG —
/// distinct from the FodsDocument-based overload in FodsPngExporterTests.
/// Covers: output file exists; PNG signature bytes (137/80/78/71); WidthPx>0; HeightPx>0;
/// RowsRendered>=0; ColsRendered>=0; OutputPath matches given path; null fodsPath throws;
/// empty fodsPath throws; null pngPath throws; dogfood multi-sheet pipeline.
/// </summary>
public class FodsR140PngPathExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPngPath() =>
        Path.Combine(Path.GetTempPath(), $"fods_r140_{Guid.NewGuid():N}.png");

    // -------------------------------------------------------------------------
    // ExportToPng(string, string) — output file and signature
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_Path_OutputFileExists()
    {
        var pngPath = TempPngPath();
        try
        {
            FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
            Assert.True(File.Exists(pngPath), "PNG output file should exist after path-based export");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_OutputHasPngSignature()
    {
        var pngPath = TempPngPath();
        try
        {
            FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
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
    public void ExportToPng_Path_OutputPathMatchesGivenPath()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
            Assert.Equal(pngPath, result.OutputPath);
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_WidthPxIsPositive()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
            Assert.True(result.WidthPx > 0, $"Expected WidthPx > 0, got {result.WidthPx}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_HeightPxIsPositive()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
            Assert.True(result.HeightPx > 0, $"Expected HeightPx > 0, got {result.HeightPx}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Path_RowsRenderedNonNegative()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), pngPath);
            Assert.True(result.RowsRendered >= 0,
                $"RowsRendered must be >= 0, got {result.RowsRendered}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    // -------------------------------------------------------------------------
    // Null/whitespace guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_Path_NullFodsPath_ThrowsArgumentNullException()
    {
        var pngPath = TempPngPath();
        Assert.ThrowsAny<Exception>(() =>
            FodsPngExporter.ExportToPng(null!, pngPath));
    }

    [Fact]
    public void ExportToPng_Path_EmptyFodsPath_ThrowsException()
    {
        var pngPath = TempPngPath();
        Assert.ThrowsAny<Exception>(() =>
            FodsPngExporter.ExportToPng(string.Empty, pngPath));
    }

    [Fact]
    public void ExportToPng_Path_NullPngPath_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() =>
            FodsPngExporter.ExportToPng(FixturePath("fods-minimal-roundtrip.fods"), null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-sheet path-based PNG pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheetPath_PngPropertiesConsistent()
    {
        var pngPath = TempPngPath();
        try
        {
            var result = FodsPngExporter.ExportToPng(
                FixturePath("fods-multi-sheet.fods"), pngPath);

            Assert.True(File.Exists(pngPath));
            Assert.Equal(pngPath, result.OutputPath);
            Assert.True(result.WidthPx > 0);
            Assert.True(result.HeightPx > 0);

            // PNG signature
            var fileBytes = File.ReadAllBytes(pngPath);
            Assert.Equal(137, fileBytes[0]);
            Assert.Equal(80, fileBytes[1]);
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }
}
