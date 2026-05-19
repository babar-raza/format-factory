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

    // -----------------------------------------------------------------------
    // R28 Lane H: C9 Malformed-Input Resilience — FodtDocument.Load
    // -----------------------------------------------------------------------

    /// <summary>
    /// C9-MAL-FODT-01: FodtDocument.Load handles empty XML (valid XML, no ODF structure).
    /// The file contains a minimal XML root element but no office:document.
    /// Document should load without crash; Body should be null and Paragraphs empty.
    /// </summary>
    [Fact]
    public void Document_Load_EmptyXml_NoOdfStructure_ReturnsNullBody()
    {
        var path = Path.Combine(_tempDir, "empty-xml.fodt");
        File.WriteAllText(path, "<?xml version=\"1.0\" encoding=\"UTF-8\"?><root/>");

        var doc = FodtDocument.Load(path);
        // Must NOT crash; body should be null since there is no office:body/office:text.
        Assert.Null(doc.Body);
        Assert.Empty(doc.Paragraphs);
    }

    /// <summary>
    /// C9-MAL-FODT-02: FodtDocument.Load handles valid ODF document missing office:body.
    /// The file has office:document root but no office:body child.
    /// </summary>
    [Fact]
    public void Document_Load_MissingBody_ReturnsNullBody()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<!-- office:body deliberately absent -->" +
            "</office:document>";
        var path = Path.Combine(_tempDir, "no-body.fodt");
        File.WriteAllText(path, xml);

        var doc = FodtDocument.Load(path);
        // Must not crash; body absent means null Body and empty Paragraphs.
        Assert.Null(doc.Body);
        Assert.Empty(doc.Paragraphs);
        // MimeType should still be readable from the root element.
        Assert.Equal("application/vnd.oasis.opendocument.text-flat-xml", doc.MimeType);
    }

    /// <summary>
    /// C9-MAL-FODT-03: FodtDocument.Load rejects truncated XML file with FodtDocumentException.
    /// The file is cut off mid-tag, producing invalid XML.
    /// </summary>
    [Fact]
    public void Document_Load_TruncatedFile_ThrowsFodtDocumentException()
    {
        var path = Path.Combine(_tempDir, "truncated-doc.fodt");
        File.WriteAllText(path,
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\">" +
            "<office:body><office:text><text:p");

        var ex = Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(path));
        Assert.Contains("XML parse error", ex.Message);
    }

    /// <summary>
    /// C9-MAL-FODT-04: FodtParser.Parse handles valid ODF document missing office:body gracefully.
    /// Returns success with zero paragraphs.
    /// </summary>
    [Fact]
    public void Parser_MissingBody_ReturnsSuccessWithZeroParagraphs()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            " office:version=\"1.3\">" +
            "</office:document>";
        var path = Path.Combine(_tempDir, "parser-no-body.fodt");
        File.WriteAllText(path, xml);

        var parser = new FodtParser();
        var result = parser.Parse(path);
        Assert.True(result.IsSuccess);
        Assert.Equal(0, result.ParagraphCount);
        Assert.Equal(0, result.HeadingCount);
    }

    /// <summary>
    /// C9-MAL-FODT-05: TXT exporter handles FODT with no paragraphs (exports empty file).
    /// </summary>
    [Fact]
    public void TxtExporter_NoParagraphs_ExportsEmptyFile()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:text>" +
            "</office:text></office:body>" +
            "</office:document>";
        var fodtPath = Path.Combine(_tempDir, "no-paras.fodt");
        File.WriteAllText(fodtPath, xml);
        var txtPath = Path.Combine(_tempDir, "no-paras.txt");

        var result = FodtTxtExporter.ExportTxt(fodtPath, txtPath);
        Assert.Equal("exported_empty_no_paragraphs", result.Status);
        Assert.Equal(0, result.ParagraphsExported);
    }
}
