// FormatFactory.Fodt Tests -- G11-F Heading Detection and Malformed XML Guard
// Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
// Gate 11 status: commercial_readiness_in_progress — G11-G NOT approved
// commercial_product_ready: false
//
// Documents and verifies:
// 1. Heading detection (outline-level → # prefix)
// 2. Malformed XML guard (exceptions, not silent failures)
// Prototype status — no commercial readiness claim.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// G11-F hardening: heading detection and malformed XML guard tests.
/// Validates FodtMarkdownExporter correctly renders ATX headings and
/// that FodtDocument.Load rejects malformed/invalid inputs with exceptions.
/// Prototype status — no commercial readiness claim.
/// </summary>
public class FodtG11fHeadingAndGuardTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string HeadingsFodt =
        Path.Combine(FixturesDir, "fodt-headings-and-list.fodt");

    private readonly string _tempDir;

    public FodtG11fHeadingAndGuardTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-heading-guard-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string ExportMarkdown(string fodtPath)
    {
        var outPath = Path.Combine(_tempDir, "out.md");
        FodtMarkdownExporter.ExportToMarkdown(fodtPath, outPath);
        return File.ReadAllText(outPath);
    }

    // -----------------------------------------------------------------------
    // Heading detection tests
    // -----------------------------------------------------------------------

    [Fact]
    public void MarkdownExporter_Headings_H1ProducesHashPrefix()
    {
        var md = ExportMarkdown(HeadingsFodt);
        Assert.Contains("# Chapter One", md);
    }

    [Fact]
    public void MarkdownExporter_Headings_H2ProducesTwoHashPrefix()
    {
        var md = ExportMarkdown(HeadingsFodt);
        Assert.Contains("## Section 1.1", md);
    }

    [Fact]
    public void MarkdownExporter_Headings_H3ProducesThreeHashPrefix()
    {
        var md = ExportMarkdown(HeadingsFodt);
        Assert.Contains("### Subsection 1.1.1", md);
    }

    [Fact]
    public void MarkdownExporter_Headings_MultipleH1BothPresent()
    {
        var md = ExportMarkdown(HeadingsFodt);
        Assert.Contains("# Chapter One", md);
        Assert.Contains("# Chapter Two", md);
    }

    [Fact]
    public void MarkdownExporter_Headings_ParagraphTextPreserved()
    {
        var md = ExportMarkdown(HeadingsFodt);
        Assert.Contains("Introduction paragraph under chapter one.", md);
    }

    // -----------------------------------------------------------------------
    // Malformed XML guard tests
    // -----------------------------------------------------------------------

    [Fact]
    public void Document_Load_EmptyFile_ThrowsException()
    {
        var path = Path.Combine(_tempDir, "empty.fodt");
        File.WriteAllBytes(path, Array.Empty<byte>());
        Assert.ThrowsAny<Exception>(() => FodtDocument.Load(path));
    }

    [Fact]
    public void Document_Load_TruncatedXml_ThrowsException()
    {
        var path = Path.Combine(_tempDir, "truncated.fodt");
        File.WriteAllText(path, "<?xml version=\"1.0\"?><office:document");
        Assert.ThrowsAny<Exception>(() => FodtDocument.Load(path));
    }

    [Fact]
    public void Document_Load_FileSizeGuard_ThrowsException()
    {
        var path = Path.Combine(_tempDir, "tiny-limit.fodt");
        File.WriteAllText(path, "<root/>");
        // 1-byte guard should reject any file
        Assert.ThrowsAny<Exception>(() => FodtDocument.Load(path, maxFileSizeBytes: 1));
    }
}
