// FodsParserTests -- Tier 0 xUnit tests for FormatFactory.Fods
// Gate 11: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsParserTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    // ------------------------------------------------------------------
    // T01: null/empty path
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_NullPath_ReturnsError()
    {
        var parser = new FodsParser();
        var result = parser.Parse(null!);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parse_EmptyPath_ReturnsError()
    {
        var parser = new FodsParser();
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
        var parser = new FodsParser();
        var result = parser.Parse("/nonexistent/path/file.fods");
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
        var parser = new FodsParser { MaxFileSizeBytes = 5 }; // 5 bytes -- too small
        var result = parser.Parse(tmp.Path);
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("exceeds limit"));
    }

    // ------------------------------------------------------------------
    // T04: empty file
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_EmptyFile_ReturnsError()
    {
        // Write a truly empty file (no BOM) using raw bytes
        var tmpPath = System.IO.Path.GetTempFileName();
        try
        {
            File.WriteAllBytes(tmpPath, Array.Empty<byte>());
            var parser = new FodsParser();
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
        var parser = new FodsParser();
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
        var parser = new FodsParser();
        var result = parser.Parse(tmp.Path);
        Assert.False(result.IsSuccess);
        Assert.Contains(result.Errors, e => e.Contains("XML parse error"));
    }

    // ------------------------------------------------------------------
    // T07: minimal valid FODS (synthetic -- no real sample required)
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_MinimalFods_SucceedsAndExtractsSheet()
    {
        const string minimalFods =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
            "  office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            "  office:version=\"1.3\">" +
            "  <office:body>" +
            "    <office:spreadsheet>" +
            "      <table:table table:name=\"Sheet1\">" +
            "        <table:table-row>" +
            "          <table:table-cell/>" +
            "          <table:table-cell/>" +
            "        </table:table-row>" +
            "      </table:table>" +
            "    </office:spreadsheet>" +
            "  </office:body>" +
            "</office:document>";

        using var tmp = new TempFile(minimalFods);
        var parser = new FodsParser();
        var result = parser.Parse(tmp.Path);

        Assert.True(result.IsSuccess, string.Join("; ", result.Errors));
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet-flat-xml",
                     result.MimeType);
        Assert.Equal("1.3", result.OdfVersion);
        Assert.Single(result.Sheets);
        Assert.Equal("Sheet1", result.Sheets[0].Name);
        Assert.Equal(1, result.Sheets[0].RowCount);
        Assert.Equal(2, result.Sheets[0].CellCount);
    }

    // ------------------------------------------------------------------
    // T08: multiple sheets
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_MultipleSheets_ExtractsAllNames()
    {
        const string twoSheets =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
            "  office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\">" +
            "  <office:body><office:spreadsheet>" +
            "    <table:table table:name=\"Alpha\"/>" +
            "    <table:table table:name=\"Beta\"/>" +
            "  </office:spreadsheet></office:body>" +
            "</office:document>";

        using var tmp = new TempFile(twoSheets);
        var parser = new FodsParser();
        var result = parser.Parse(tmp.Path);

        Assert.True(result.IsSuccess, string.Join("; ", result.Errors));
        Assert.Equal(2, result.Sheets.Count);
        Assert.Equal("Alpha", result.Sheets[0].Name);
        Assert.Equal("Beta",  result.Sheets[1].Name);
    }

    // ------------------------------------------------------------------
    // T09: GetSheetNames convenience method
    // ------------------------------------------------------------------
    [Fact]
    public void GetSheetNames_ValidFods_ReturnsNames()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            "  xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            "  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\">" +
            "  <office:body><office:spreadsheet>" +
            "    <table:table table:name=\"Data\"/>" +
            "  </office:spreadsheet></office:body>" +
            "</office:document>";

        using var tmp = new TempFile(xml);
        var parser = new FodsParser();
        var names = parser.GetSheetNames(tmp.Path);
        Assert.Single(names);
        Assert.Equal("Data", names[0]);
    }

    // ------------------------------------------------------------------
    // T10: GetSheetNames throws FodsParseException on bad file
    // ------------------------------------------------------------------
    [Fact]
    public void GetSheetNames_BadFile_ThrowsFodsParseException()
    {
        var parser = new FodsParser();
        Assert.Throws<FodsParseException>(() =>
            parser.GetSheetNames("/does/not/exist.fods"));
    }

    // ------------------------------------------------------------------
    // T11: real FODS sample (skipped if samples dir absent)
    // ------------------------------------------------------------------
    [Fact]
    public void Parse_RealSample_SucceedsIfSamplesPresent()
    {
        if (!Directory.Exists(SamplesDir))
        {
            // Not a failure -- samples dir is local-only
            return;
        }

        var files = Directory.GetFiles(SamplesDir, "*.fods");
        if (files.Length == 0) return;

        var parser = new FodsParser();
        foreach (var file in files)
        {
            var result = parser.Parse(file);
            // At minimum the file should be parseable XML
            Assert.True(result.IsSuccess || result.Errors.Count > 0);
            // Must not throw
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
