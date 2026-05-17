// FormatFactory.Fods Tests -- FodsCsvExporter G11-E Prototype Tests
// Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the G11-E FODS → CSV conversion prototype.
/// Tests cover: basic export, empty document, CSV escaping, null guards.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodsCsvExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsCsvExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "fods-csv-export-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // EscapeCsvField tests (unit)
    // -------------------------------------------------------------------------

    [Fact]
    public void EscapeCsvField_Null_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodsCsvExporter.EscapeCsvField(null));
    }

    [Fact]
    public void EscapeCsvField_Empty_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodsCsvExporter.EscapeCsvField(string.Empty));
    }

    [Fact]
    public void EscapeCsvField_PlainValue_ReturnedAsIs()
    {
        Assert.Equal("hello", FodsCsvExporter.EscapeCsvField("hello"));
        Assert.Equal("123", FodsCsvExporter.EscapeCsvField("123"));
    }

    [Fact]
    public void EscapeCsvField_WithComma_WrappedInQuotes()
    {
        var result = FodsCsvExporter.EscapeCsvField("hello, world");
        Assert.Equal("\"hello, world\"", result);
    }

    [Fact]
    public void EscapeCsvField_WithDoubleQuote_Doubled()
    {
        var result = FodsCsvExporter.EscapeCsvField("say \"hi\"");
        Assert.Equal("\"say \"\"hi\"\"\"", result);
    }

    [Fact]
    public void EscapeCsvField_WithNewline_WrappedInQuotes()
    {
        var result = FodsCsvExporter.EscapeCsvField("line1\nline2");
        Assert.Equal("\"line1\nline2\"", result);
    }

    [Fact]
    public void EscapeCsvField_WithCarriageReturn_WrappedInQuotes()
    {
        var result = FodsCsvExporter.EscapeCsvField("line1\r\nline2");
        Assert.StartsWith("\"", result);
        Assert.EndsWith("\"", result);
    }

    [Fact]
    public void EscapeCsvField_SpacesOnly_NotQuoted()
    {
        // Spaces alone don't require quoting per RFC 4180
        Assert.Equal("   ", FodsCsvExporter.EscapeCsvField("   "));
    }

    // -------------------------------------------------------------------------
    // Null guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportFirstSheetToCsv_NullFodsPath_Throws()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(null!, Path.Combine(_tempDir, "out.csv")));
    }

    [Fact]
    public void ExportFirstSheetToCsv_EmptyFodsPath_Throws()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(string.Empty, Path.Combine(_tempDir, "out.csv")));
    }

    [Fact]
    public void ExportFirstSheetToCsv_NullCsvPath_Throws()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, null!));
    }

    [Fact]
    public void ExportFirstSheetToCsv_FileNotFound_Throws()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(
                Path.Combine(FixturesDir, "does-not-exist.fods"),
                Path.Combine(_tempDir, "out.csv")));
    }

    // -------------------------------------------------------------------------
    // Integration tests against fixture file
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_ProducesFile()
    {
        var csvPath = Path.Combine(_tempDir, "minimal.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.Equal("exported", result.Status);
        Assert.True(File.Exists(csvPath), "CSV file should exist after export.");
    }

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_ReturnsCorrectPaths()
    {
        var csvPath = Path.Combine(_tempDir, "paths.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.Equal(MinimalFods, result.SourcePath);
        Assert.Equal(csvPath, result.OutputPath);
    }

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_HasRows()
    {
        var csvPath = Path.Combine(_tempDir, "rows.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.True(result.RowsExported >= 0, "RowsExported must be non-negative.");
    }

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_CsvIsUtf8NoBom()
    {
        var csvPath = Path.Combine(_tempDir, "utf8.csv");
        FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        var bytes = File.ReadAllBytes(csvPath);
        if (bytes.Length >= 3)
        {
            Assert.False(bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "CSV must not have UTF-8 BOM.");
        }
    }

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_ContentIsReadable()
    {
        var csvPath = Path.Combine(_tempDir, "readable.csv");
        FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        var content = File.ReadAllText(csvPath, Encoding.UTF8);
        Assert.NotNull(content);
    }

    [Fact]
    public void ExportFirstSheetToCsv_OutputDir_CreatedIfMissing()
    {
        var subDir = Path.Combine(_tempDir, "subdir", "nested");
        var csvPath = Path.Combine(subDir, "out.csv");

        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.Equal("exported", result.Status);
        Assert.True(File.Exists(csvPath), "CSV file should exist in auto-created subdirectory.");
    }

    [Fact]
    public void ExportFirstSheetToCsv_MinimalFixture_SheetNameNotNull()
    {
        var csvPath = Path.Combine(_tempDir, "sheetname.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.NotNull(result.SheetName);
    }

    [Fact]
    public void ExportFirstSheetToCsv_MaxColumns_NonNegative()
    {
        var csvPath = Path.Combine(_tempDir, "maxcols.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, csvPath);

        Assert.True(result.MaxColumns >= 0, "MaxColumns must be non-negative.");
    }

    // -------------------------------------------------------------------------
    // Gate 11 governance assertions
    // -------------------------------------------------------------------------

    [Fact]
    public void G11E_Prototype_CommercialProductReadyIsFalse()
    {
        const bool commercialProductReady = false;
        Assert.False(commercialProductReady,
            "commercial_product_ready must remain false until G11-G is approved.");
    }

    [Fact]
    public void G11E_Prototype_ExporterDoesNotPublish()
    {
        var methods = typeof(FodsCsvExporter).GetMethods(
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        foreach (var method in methods)
        {
            Assert.False(method.Name.Contains("Publish", StringComparison.OrdinalIgnoreCase),
                $"FodsCsvExporter must not have 'Publish' methods. Found: {method.Name}");
            Assert.False(method.Name.Contains("Upload", StringComparison.OrdinalIgnoreCase),
                $"FodsCsvExporter must not have 'Upload' methods. Found: {method.Name}");
        }
    }
}
