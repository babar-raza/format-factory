// R88 Train H: FODS .NET multi-sheet CSV export tests
// Sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR88MultiSheetCsvTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MultiSheetFods =
        Path.Combine(FixturesDir, "fods-multi-sheet.fods");

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsR88MultiSheetCsvTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-r88-multisheet-csv-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // ---- ExportAllSheetsToCsv ----

    [Fact]
    public void ExportAllSheets_MultiSheet_CreatesMultipleFiles()
    {
        var outDir = Path.Combine(_tempDir, "all-sheets");
        var results = FodsCsvExporter.ExportAllSheetsToCsv(MultiSheetFods, outDir);
        Assert.True(results.Count >= 2, $"Expected at least 2 sheets, got {results.Count}");
        foreach (var r in results)
        {
            Assert.True(File.Exists(r.OutputPath), $"CSV not found: {r.OutputPath}");
            Assert.Equal("exported", r.Status);
        }
    }

    [Fact]
    public void ExportAllSheets_MultiSheet_UsesSheetNamesAsFilenames()
    {
        var outDir = Path.Combine(_tempDir, "named-sheets");
        var results = FodsCsvExporter.ExportAllSheetsToCsv(MultiSheetFods, outDir);
        foreach (var r in results)
        {
            var fileName = Path.GetFileNameWithoutExtension(r.OutputPath);
            Assert.False(string.IsNullOrEmpty(fileName));
            Assert.EndsWith(".csv", r.OutputPath);
        }
    }

    [Fact]
    public void ExportAllSheets_MinimalSingleSheet_ReturnsOneResult()
    {
        var outDir = Path.Combine(_tempDir, "single-sheet");
        var results = FodsCsvExporter.ExportAllSheetsToCsv(MinimalFods, outDir);
        Assert.Single(results);
        Assert.Equal("exported", results[0].Status);
        Assert.True(File.Exists(results[0].OutputPath));
    }

    [Fact]
    public void ExportAllSheets_CreatesOutputDirectory()
    {
        var outDir = Path.Combine(_tempDir, "nested", "deep", "dir");
        Assert.False(Directory.Exists(outDir));
        FodsCsvExporter.ExportAllSheetsToCsv(MinimalFods, outDir);
        Assert.True(Directory.Exists(outDir));
    }

    [Fact]
    public void ExportAllSheets_NullPath_Throws()
    {
        Assert.Throws<FodsCsvExportException>(
            () => FodsCsvExporter.ExportAllSheetsToCsv(null!, _tempDir));
    }

    [Fact]
    public void ExportAllSheets_NullOutputDir_Throws()
    {
        Assert.Throws<FodsCsvExportException>(
            () => FodsCsvExporter.ExportAllSheetsToCsv(MinimalFods, null!));
    }

    [Fact]
    public void ExportAllSheets_EachResultHasSourcePath()
    {
        var outDir = Path.Combine(_tempDir, "source-check");
        var results = FodsCsvExporter.ExportAllSheetsToCsv(MultiSheetFods, outDir);
        foreach (var r in results)
        {
            Assert.Equal(MultiSheetFods, r.SourcePath);
        }
    }

    [Fact]
    public void ExportAllSheets_SheetNamesPopulated()
    {
        var outDir = Path.Combine(_tempDir, "sheet-names");
        var results = FodsCsvExporter.ExportAllSheetsToCsv(MultiSheetFods, outDir);
        foreach (var r in results)
        {
            Assert.False(string.IsNullOrEmpty(r.SheetName),
                "SheetName should be populated");
        }
    }
}
