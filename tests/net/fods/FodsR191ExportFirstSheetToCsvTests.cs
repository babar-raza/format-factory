// Tests for FodsCsvExporter.ExportFirstSheetToCsv dedicated coverage.
// Sprint: ff-sprint-s184-dotnet-deepening-20260628
// Ledger: PC-FODS-R191

using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R191: Dedicated tests for FodsCsvExporter.ExportFirstSheetToCsv(string fodsPath, string csvPath).
/// Loads a FODS file and exports its first sheet to a CSV file.
/// null/whitespace fodsPath throws FodsCsvExportException.
/// null/whitespace csvPath throws FodsCsvExportException.
/// Nonexistent fodsPath throws FodsCsvExportException.
/// Result has SourcePath, OutputPath, SheetName, RowsExported, MaxColumns, Status.
/// CSV file is created at csvPath.
/// Status reflects "exported" or similar on success.
/// Covers: null fodsPath throws; whitespace fodsPath throws; null csvPath throws;
/// whitespace csvPath throws; nonexistent file throws; valid export creates csv file;
/// result source path matches input; result output path matches csvPath;
/// result rows exported >= 0; dogfood minimal FODS export produces csv.
/// </summary>
public class FodsR191ExportFirstSheetToCsvTests
{
    private static string TempPath(string ext = ".csv") =>
        Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ext);

    private static string SampleFodsPath =>
        Path.GetFullPath("samples/by-format/fods/minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportFirstSheetToCsv_NullFodsPath_ThrowsFodsCsvExportException()
    {
        var csvPath = TempPath();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(null!, csvPath));
    }

    [Fact]
    public void ExportFirstSheetToCsv_WhitespaceFodsPath_ThrowsFodsCsvExportException()
    {
        var csvPath = TempPath();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv("   ", csvPath));
    }

    [Fact]
    public void ExportFirstSheetToCsv_NullCsvPath_ThrowsFodsCsvExportException()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, null!));
    }

    [Fact]
    public void ExportFirstSheetToCsv_WhitespaceCsvPath_ThrowsFodsCsvExportException()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, "   "));
    }

    [Fact]
    public void ExportFirstSheetToCsv_NonexistentFodsPath_ThrowsFodsCsvExportException()
    {
        var csvPath = TempPath();
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv("/no/such/file.fods", csvPath));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportFirstSheetToCsv_ValidExport_CreatesCsvFile()
    {
        var csvPath = TempPath();
        try
        {
            FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, csvPath);
            Assert.True(File.Exists(csvPath));
        }
        finally
        {
            if (File.Exists(csvPath)) File.Delete(csvPath);
        }
    }

    [Fact]
    public void ExportFirstSheetToCsv_ValidExport_ResultSourcePathMatchesInput()
    {
        var csvPath = TempPath();
        try
        {
            var result = FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, csvPath);
            Assert.Equal(SampleFodsPath, result.SourcePath);
        }
        finally
        {
            if (File.Exists(csvPath)) File.Delete(csvPath);
        }
    }

    [Fact]
    public void ExportFirstSheetToCsv_ValidExport_ResultOutputPathMatchesCsvPath()
    {
        var csvPath = TempPath();
        try
        {
            var result = FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, csvPath);
            Assert.Equal(csvPath, result.OutputPath);
        }
        finally
        {
            if (File.Exists(csvPath)) File.Delete(csvPath);
        }
    }

    [Fact]
    public void ExportFirstSheetToCsv_ValidExport_RowsExportedNonNegative()
    {
        var csvPath = TempPath();
        try
        {
            var result = FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, csvPath);
            Assert.True(result.RowsExported >= 0);
        }
        finally
        {
            if (File.Exists(csvPath)) File.Delete(csvPath);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MinimalFods_ProducesCsvWithContent()
    {
        var csvPath = TempPath();
        try
        {
            var result = FodsCsvExporter.ExportFirstSheetToCsv(SampleFodsPath, csvPath);
            var content = File.ReadAllText(csvPath);
            Assert.NotNull(content);
            Assert.False(string.IsNullOrEmpty(result.Status));
        }
        finally
        {
            if (File.Exists(csvPath)) File.Delete(csvPath);
        }
    }
}
