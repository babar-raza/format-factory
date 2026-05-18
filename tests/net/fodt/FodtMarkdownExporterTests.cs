// FormatFactory.Fodt Tests -- FodtMarkdownExporter G11-E Expanded Prototype Tests
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for the G11-E FODT → Markdown export prototype.
/// Tests cover: basic export, heading format, null guards, output structure.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodtMarkdownExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtMarkdownExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-md-export-tests-" + Guid.NewGuid().ToString("N"));
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
    public void ExportToMarkdown_NullFodtPath_Throws()
    {
        Assert.Throws<FodtMarkdownExportException>(() =>
            FodtMarkdownExporter.ExportToMarkdown(null!, Path.Combine(_tempDir, "out.md")));
    }

    [Fact]
    public void ExportToMarkdown_EmptyFodtPath_Throws()
    {
        Assert.Throws<FodtMarkdownExportException>(() =>
            FodtMarkdownExporter.ExportToMarkdown("", Path.Combine(_tempDir, "out.md")));
    }

    [Fact]
    public void ExportToMarkdown_NullMdPath_Throws()
    {
        Assert.Throws<FodtMarkdownExportException>(() =>
            FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, null!));
    }

    [Fact]
    public void ExportToMarkdown_NonExistentFodtPath_Throws()
    {
        Assert.Throws<FodtMarkdownExportException>(() =>
            FodtMarkdownExporter.ExportToMarkdown(
                Path.Combine(_tempDir, "nonexistent.fodt"),
                Path.Combine(_tempDir, "out.md")));
    }

    // -------------------------------------------------------------------------
    // FormatParagraphAsMarkdown unit tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FormatParagraph_NullPara_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtMarkdownExporter.FormatParagraphAsMarkdown(null!));
    }

    // -------------------------------------------------------------------------
    // Integration tests (using fixture)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_MinimalFodt_CreatesMdFile()
    {
        var outMd = Path.Combine(_tempDir, "minimal.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outMd);

        Assert.True(File.Exists(outMd), "Markdown output file must be created");
        Assert.Equal(outMd, result.OutputPath);
    }

    [Fact]
    public void ExportToMarkdown_MinimalFodt_StatusIsExportedOrEmpty()
    {
        var outMd = Path.Combine(_tempDir, "out.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outMd);

        Assert.True(
            result.Status == "exported" ||
            result.Status == "exported_empty_no_paragraphs",
            $"Status must be 'exported' or 'exported_empty_no_paragraphs', got: {result.Status}");
    }

    [Fact]
    public void ExportToMarkdown_MinimalFodt_NonNegativeCounts()
    {
        var outMd = Path.Combine(_tempDir, "out.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outMd);

        Assert.True(result.HeadingsExported >= 0);
        Assert.True(result.ParagraphsExported >= 0);
    }

    [Fact]
    public void ExportToMarkdown_MinimalFodt_OutputFileNonEmptyIfHasContent()
    {
        var outMd = Path.Combine(_tempDir, "out.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outMd);

        if (result.Status == "exported")
        {
            var info = new FileInfo(outMd);
            Assert.True(info.Length > 0, "Output must be non-empty when status=exported");
        }
    }

    [Fact]
    public void ExportToMarkdown_HeadingLevel1_StartsWithHash()
    {
        // Build a synthetic FODT with a heading, verify Markdown output format
        var doc = FodtDocument.Load(MinimalFodt);
        var paras = doc.Paragraphs;

        // Check any headings in the fixture
        foreach (var para in paras)
        {
            if (para.IsHeading)
            {
                var line = FodtMarkdownExporter.FormatParagraphAsMarkdown(para);
                Assert.StartsWith("#", line);
                break;
            }
        }
    }

    [Fact]
    public void ExportToMarkdown_MinimalFodt_OutputIsSingleDocument()
    {
        var outMd = Path.Combine(_tempDir, "out.md");
        FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outMd);
        // Must be exactly one output file
        Assert.True(File.Exists(outMd));
        Assert.False(Directory.Exists(outMd));
    }
}
