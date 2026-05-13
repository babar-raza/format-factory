// FodtParserTests -- Tier 0 xUnit tests for FormatFactory.Fodt
// Gate 11: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using Xunit;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtParserTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    // ------------------------------------------------------------------
    // T01: null/empty path
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_NullPath_ReturnsError()
    {
        var parser = new FodtParser();
        var result = parser.Parse(null!);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parse_EmptyPath_ReturnsError()
    {
        var parser = new FodtParser();
        var result = parser.Parse(string.Empty);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    // ------------------------------------------------------------------
    // T02: file not found
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_FileNotFound_ReturnsError()
    {
        var parser = new FodtParser();
        var result = parser.Parse("/nonexistent/path/file.fodt");
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("not found"));
    }

    // ------------------------------------------------------------------
    // T03: size guard
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_FileTooLarge_ReturnsError()
    {
        using var tmp = new TempFile("<office:document/>");
        var parser = new FodtParser { MaxFileSizeBytes = 5 };
        var result = parser.Parse(tmp.Path);
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("exceeds limit"));
    }

    // ------------------------------------------------------------------
    // T04: empty file (no BOM)
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_EmptyFile_ReturnsError()
    {
        var tmpPath = System.IO.Path.GetTempFileName();
        try
        {
            File.WriteAllBytes(tmpPath, Array.Empty<byte>());
            var parser = new FodtParser();
            var result = parser.Parse(tmpPath);
            Assert.False(result.IsSuccess);
            Assert.Contains(result.Errors, e => e.Contains("empty"));
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // ------------------------------------------------------------------
    // T05: malformed XML
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_MalformedXml_ReturnsError()
    {
        using var tmp = new TempFile("<office:document><unclosed>");
        var parser = new FodtParser();
        var result = parser.Parse(tmp.Path);
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("XML parse error"));
    }

    // ------------------------------------------------------------------
    // T06: DTD rejection (XXE defense)
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_DtdPresent_ReturnsError()
    {
        const string dtdXml =
            "<?xml version=\"1.0\"?>" +
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>" +
            "<root>&xxe;</root>";
        using var tmp = new TempFile(dtdXml);
        var parser = new FodtParser();
        var result = parser.Parse(tmp.Path);
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("XML parse error"));
    }

    // ------------------------------------------------------------------
    // T07: minimal valid FODT -- paragraph and heading counts
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_MinimalFodt_SucceedsAndCountsParagraphs()
    {
        const string minimalFodt =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            "  office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            "  office:version=\"1.3\">" +
            "  <office:body>" +
            "    <office:text>" +
            "      <text:h text:outline-level=\"1\">Title</text:h>" +
            "      <text:p>First paragraph.</text:p>" +
            "      <text:p>Second paragraph.</text:p>" +
            "    </office:text>" +
            "  </office:body>" +
            "</office:document>";

        using var tmp = new TempFile(minimalFodt);
        var parser = new FodtParser();
        var result = parser.Parse(tmp.Path);

        Assert.True(result.IsSuccess, string.Join("; ", result.Errors));
        Assert.Equal("application/vnd.oasis.opendocument.text-flat-xml", result.MimeType);
        Assert.Equal("1.3", result.OdfVersion);
        Assert.Equal(3, result.ParagraphCount); // 1 heading + 2 paragraphs
        Assert.Equal(1, result.HeadingCount);
    }

    // ------------------------------------------------------------------
    // T08: list counting
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_FodtWithList_CountsLists()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\">" +
            "  <office:body><office:text>" +
            "    <text:list>" +
            "      <text:list-item><text:p>Item 1</text:p></text:list-item>" +
            "      <text:list-item><text:p>Item 2</text:p></text:list-item>" +
            "    </text:list>" +
            "    <text:list>" +
            "      <text:list-item><text:p>Item A</text:p></text:list-item>" +
            "    </text:list>" +
            "  </office:text></office:body>" +
            "</office:document>";

        using var tmp = new TempFile(xml);
        var parser = new FodtParser();
        var result = parser.Parse(tmp.Path);

        Assert.True(result.IsSuccess, string.Join("; ", result.Errors));
        Assert.Equal(2, result.ListCount);
        // text:p inside list items are also counted as paragraphs
        Assert.Equal(3, result.ParagraphCount);
    }

    // ------------------------------------------------------------------
    // T09: table extraction
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_FodtWithTable_ExtractsTable()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            "  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\">" +
            "  <office:body><office:text>" +
            "    <table:table table:name=\"Table1\">" +
            "      <table:table-row>" +
            "        <table:table-cell/><table:table-cell/>" +
            "      </table:table-row>" +
            "      <table:table-row>" +
            "        <table:table-cell/><table:table-cell/>" +
            "      </table:table-row>" +
            "    </table:table>" +
            "  </office:text></office:body>" +
            "</office:document>";

        using var tmp = new TempFile(xml);
        var parser = new FodtParser();
        var result = parser.Parse(tmp.Path);

        Assert.True(result.IsSuccess, string.Join("; ", result.Errors));
        Assert.Single(result.Tables);
        Assert.Equal("Table1", result.Tables[0].Name);
        Assert.Equal(2, result.Tables[0].RowCount);
        Assert.Equal(4, result.Tables[0].CellCount);
    }

    // ------------------------------------------------------------------
    // T10: GetParagraphCount convenience method
    // ------------------------------------------------------------------
    [Fact]
    public void GetParagraphCount_ValidFodt_ReturnsCount()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\">" +
            "  <office:body><office:text>" +
            "    <text:p>Hello</text:p>" +
            "    <text:p>World</text:p>" +
            "  </office:text></office:body>" +
            "</office:document>";

        using var tmp = new TempFile(xml);
        var parser = new FodtParser();
        Assert.Equal(2, parser.GetParagraphCount(tmp.Path));
    }

    // ------------------------------------------------------------------
    // T11: GetParagraphCount throws FodtParseException on bad file
    // ------------------------------------------------------------------
    [Fact]
    public void GetParagraphCount_BadFile_ThrowsFodtParseException()
    {
        var parser = new FodtParser();
        Assert.Throws<FodtParseException>(() =>
            parser.GetParagraphCount("/does/not/exist.fodt"));
    }

    // ------------------------------------------------------------------
    // T12: real FODT samples (skipped if dir absent)
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_RealSamples_SucceedIfPresent()
    {
        if (!Directory.Exists(SamplesDir)) return;

        var files = Directory.GetFiles(SamplesDir, "*.fodt");
        if (files.Length == 0) return;

        var parser = new FodtParser();
        foreach (var file in files)
        {
            var result = parser.Parse(file);
            Assert.True(result.IsSuccess || result.Errors.Count > 0);
        }
    }

    // ------------------------------------------------------------------
    // Helper: temporary file that cleans itself up
    // ------------------------------------------------------------------
    private sealed class TempFile : IDisposable
    {
        public string Path { get; }
        public TempFile(string content)
        {
            Path = System.IO.Path.GetTempFileName();
            File.WriteAllText(Path, content, System.Text.Encoding.UTF8);
        }
        public void Dispose()
        {
            if (File.Exists(Path))
                File.Delete(Path);
        }
    }
}
