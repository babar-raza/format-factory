// FormatFactory.Fods Tests -- G11-F Malformed XML Guard (G11-F Hardening Slice)
// Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
// Gate 11 status: commercial_readiness_in_progress — G11-G NOT approved
// commercial_product_ready: false
//
// Documents and verifies the parser's resilience to malformed/adversarial XML inputs.
// Tests prototype-level behaviour only — no commercial readiness claim.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// G11-F hardening: malformed XML guard tests.
/// Verifies FodsParser does not crash or expose internals when given:
/// - Empty files
/// - Truncated XML
/// - Non-XML content
/// - Oversized files (size guard)
/// - Null/empty path
/// Prototype status — no commercial readiness claim.
/// </summary>
public class FodsG11fMalformedXmlGuardTests : IDisposable
{
    private readonly string _tempDir;
    private readonly FodsParser _parser = new FodsParser();

    public FodsG11fMalformedXmlGuardTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-malformed-guard-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string WriteTemp(string name, string content)
    {
        var path = Path.Combine(_tempDir, name);
        File.WriteAllText(path, content, System.Text.Encoding.UTF8);
        return path;
    }

    private string WriteTempBytes(string name, byte[] content)
    {
        var path = Path.Combine(_tempDir, name);
        File.WriteAllBytes(path, content);
        return path;
    }

    [Fact]
    public void Parser_NullPath_ReturnsErrorNotThrow()
    {
        var result = _parser.Parse(null!);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_EmptyPath_ReturnsError()
    {
        var result = _parser.Parse("");
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_NonExistentFile_ReturnsError()
    {
        var result = _parser.Parse(Path.Combine(_tempDir, "does-not-exist.fods"));
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_EmptyFile_ReturnsError()
    {
        var path = WriteTempBytes("empty.fods", Array.Empty<byte>());
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_TruncatedXml_ReturnsError()
    {
        var path = WriteTemp("truncated.fods", "<?xml version=\"1.0\"?><office:document");
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_NonXmlContent_ReturnsError()
    {
        var path = WriteTemp("notxml.fods", "This is not XML at all. PK\x03\x04 binary garbage.");
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_WrongRootElement_ReturnsErrorOrEmptyDocument()
    {
        // Valid XML but wrong root — not an ODF document
        var path = WriteTemp("wrongroot.fods",
            "<?xml version=\"1.0\"?><html><body><p>Not FODS</p></body></html>");
        var result = _parser.Parse(path);
        // Either error or empty sheets — must NOT return success with data
        if (result.IsSuccess)
            Assert.Empty(result.Sheets);
        else
            Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_FileSizeGuard_RejectsOversized()
    {
        // Parser with 1-byte max file size should reject any real file
        var tinyParser = new FodsParser { MaxFileSizeBytes = 1 };
        var path = WriteTemp("valid-but-oversized.fods", "<root/>");
        var result = tinyParser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }
}
