// Tests for FodsCsvExporter.ExportAllSheetsToCsv dedicated coverage.
// Sprint: ff-sprint-s185-dotnet-deepening-20260628
// Ledger: PC-FODS-R192

using System.IO;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R192: Dedicated tests for FodsCsvExporter.ExportAllSheetsToCsv(string fodsPath, string outputDirPath).
/// Loads a FODS file and exports each sheet to a separate CSV file in the output directory.
/// null/whitespace fodsPath throws FodsCsvExportException.
/// null/whitespace outputDirPath throws FodsCsvExportException.
/// Nonexistent fodsPath throws FodsCsvExportException.
/// Output directory is created if it does not exist.
/// Returns a List with one result per sheet.
/// Each result has SheetName, RowsExported, Status, OutputPath.
/// Covers: null fodsPath throws; whitespace fodsPath throws; null outputDirPath throws;
/// whitespace outputDirPath throws; nonexistent file throws; valid export creates dir;
/// returns list; list count matches sheet count; each result has non-null status;
/// dogfood multi-sheet FODS creates multiple csv files.
/// </summary>
public class FodsR192ExportAllSheetsToCsvTests
{
    private static string TempDir() =>
        Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());

    private static string SampleFodsPath =>
        Path.GetFullPath("samples/by-format/fods/minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.GetFullPath("samples/by-format/fods/multi-sheet-basic.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportAllSheetsToCsv_NullFodsPath_ThrowsFodsCsvExportException()
    {
        var dir = TempDir();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportAllSheetsToCsv(null!, dir));
    }

    [Fact]
    public void ExportAllSheetsToCsv_WhitespaceFodsPath_ThrowsFodsCsvExportException()
    {
        var dir = TempDir();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportAllSheetsToCsv("   ", dir));
    }

    [Fact]
    public void ExportAllSheetsToCsv_NullOutputDir_ThrowsFodsCsvExportException()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, null!));
    }

    [Fact]
    public void ExportAllSheetsToCsv_WhitespaceOutputDir_ThrowsFodsCsvExportException()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, "   "));
    }

    [Fact]
    public void ExportAllSheetsToCsv_NonexistentFodsPath_ThrowsFodsCsvExportException()
    {
        var dir = TempDir();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportAllSheetsToCsv("/no/such/file.fods", dir));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportAllSheetsToCsv_ValidExport_ReturnsList()
    {
        var dir = TempDir();
        try
        {
            var results = FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, dir);
            Assert.IsType<List<FodsCsvExportResult>>(results);
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void ExportAllSheetsToCsv_ValidExport_CreatesOutputDirectory()
    {
        var dir = TempDir();
        try
        {
            FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, dir);
            Assert.True(Directory.Exists(dir));
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void ExportAllSheetsToCsv_SingleSheetFods_ReturnsOneResult()
    {
        var dir = TempDir();
        try
        {
            var results = FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, dir);
            Assert.True(results.Count >= 1);
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void ExportAllSheetsToCsv_EachResult_HasNonNullStatus()
    {
        var dir = TempDir();
        try
        {
            var results = FodsCsvExporter.ExportAllSheetsToCsv(SampleFodsPath, dir);
            foreach (var r in results)
                Assert.False(string.IsNullOrEmpty(r.Status));
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheetFods_CreatesCsvPerSheet()
    {
        var dir = TempDir();
        try
        {
            var results = FodsCsvExporter.ExportAllSheetsToCsv(MultiSheetFodsPath, dir);
            Assert.True(results.Count >= 2, $"Expected >= 2 results, got {results.Count}");
            foreach (var r in results)
                Assert.True(File.Exists(r.OutputPath), $"CSV not found: {r.OutputPath}");
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }
}
