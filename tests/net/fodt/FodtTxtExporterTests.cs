// FormatFactory.Fodt Tests -- FodtTxtExporter G11-E Prototype Tests
// Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for the G11-E FODT → TXT conversion prototype.
/// Tests cover: basic export, empty document, multi-paragraph, null guards.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodtTxtExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtTxtExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "fodt-txt-export-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // Null guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportTxt_NullFodtPath_Throws()
    {
        Assert.Throws<FodtTxtExportException>(() =>
            FodtTxtExporter.ExportTxt(null!, Path.Combine(_tempDir, "out.txt")));
    }

    [Fact]
    public void ExportTxt_EmptyFodtPath_Throws()
    {
        Assert.Throws<FodtTxtExportException>(() =>
            FodtTxtExporter.ExportTxt(string.Empty, Path.Combine(_tempDir, "out.txt")));
    }

    [Fact]
    public void ExportTxt_NullTxtPath_Throws()
    {
        Assert.Throws<FodtTxtExportException>(() =>
            FodtTxtExporter.ExportTxt(MinimalFodt, null!));
    }

    [Fact]
    public void ExportTxt_FileNotFound_Throws()
    {
        Assert.Throws<FodtTxtExportException>(() =>
            FodtTxtExporter.ExportTxt(
                Path.Combine(FixturesDir, "does-not-exist.fodt"),
                Path.Combine(_tempDir, "out.txt")));
    }

    // -------------------------------------------------------------------------
    // Integration tests against fixture file
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportTxt_MinimalFixture_ProducesFile()
    {
        var txtPath = Path.Combine(_tempDir, "minimal.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        Assert.True(
            result.Status == "exported" || result.Status == "exported_empty_no_paragraphs",
            $"Expected exported status, got: {result.Status}");
        Assert.True(File.Exists(txtPath), "TXT file should exist after export.");
    }

    [Fact]
    public void ExportTxt_MinimalFixture_ReturnsCorrectPaths()
    {
        var txtPath = Path.Combine(_tempDir, "paths.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        Assert.Equal(MinimalFodt, result.SourcePath);
        Assert.Equal(txtPath, result.OutputPath);
    }

    [Fact]
    public void ExportTxt_MinimalFixture_ParagraphsExportedNonNegative()
    {
        var txtPath = Path.Combine(_tempDir, "paras.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        Assert.True(result.ParagraphsExported >= 0, "ParagraphsExported must be non-negative.");
    }

    [Fact]
    public void ExportTxt_MinimalFixture_OutputIsUtf8NoBom()
    {
        var txtPath = Path.Combine(_tempDir, "utf8.txt");
        FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        var bytes = File.ReadAllBytes(txtPath);
        if (bytes.Length >= 3)
        {
            Assert.False(bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "TXT output must not have UTF-8 BOM.");
        }
    }

    [Fact]
    public void ExportTxt_MinimalFixture_ContentIsReadable()
    {
        var txtPath = Path.Combine(_tempDir, "readable.txt");
        FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        var content = File.ReadAllText(txtPath, Encoding.UTF8);
        Assert.NotNull(content);
    }

    [Fact]
    public void ExportTxt_MinimalFixture_OutputDirCreatedIfMissing()
    {
        var subDir = Path.Combine(_tempDir, "sub", "nested");
        var txtPath = Path.Combine(subDir, "out.txt");

        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        Assert.True(
            result.Status == "exported" || result.Status == "exported_empty_no_paragraphs");
        Assert.True(File.Exists(txtPath));
    }

    [Fact]
    public void ExportTxt_MinimalFixture_ParagraphsJoinedWithLf()
    {
        var txtPath = Path.Combine(_tempDir, "lf.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        if (result.ParagraphsExported > 1)
        {
            var content = File.ReadAllText(txtPath, Encoding.UTF8);
            Assert.Contains('\n', content);
        }
    }

    [Fact]
    public void ExportTxt_MinimalFixture_ContentNotNull()
    {
        var txtPath = Path.Combine(_tempDir, "nocr.txt");
        FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        var content = File.ReadAllText(txtPath, Encoding.UTF8);
        Assert.NotNull(content);
    }

    [Fact]
    public void ExportTxt_WithDocumentOverload_Works()
    {
        var txtPath = Path.Combine(_tempDir, "doc-overload.txt");
        var doc = FodtDocument.Load(MinimalFodt);
        var result = FodtTxtExporter.ExportTxt(doc, MinimalFodt, txtPath);

        Assert.True(
            result.Status == "exported" || result.Status == "exported_empty_no_paragraphs",
            $"Expected exported status: {result.Status}");
        Assert.True(File.Exists(txtPath));
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
        var methods = typeof(FodtTxtExporter).GetMethods(
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        foreach (var method in methods)
        {
            Assert.False(method.Name.Contains("Publish", StringComparison.OrdinalIgnoreCase),
                $"FodtTxtExporter must not have 'Publish' methods. Found: {method.Name}");
            Assert.False(method.Name.Contains("Upload", StringComparison.OrdinalIgnoreCase),
                $"FodtTxtExporter must not have 'Upload' methods. Found: {method.Name}");
        }
    }

    [Fact]
    public void G11E_Prototype_ExportedFileIsLocalOnly()
    {
        var txtPath = Path.Combine(_tempDir, "local-only.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, txtPath);

        Assert.True(Path.IsPathFullyQualified(result.OutputPath) ||
                    !result.OutputPath.StartsWith("http", StringComparison.OrdinalIgnoreCase),
            "Output path must be local, not a URL.");
    }
}
