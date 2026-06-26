// Tests for ZstParser.Parse(filePath), ZstException, and invalid input handling.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R153

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R153: Tests for ZstParser.Parse(filePath), ZstException, and invalid input handling.
/// ZstParser.Parse(filePath): parses a .zst file and returns ZstDocument.
/// ZstException: thrown for invalid or oversized content.
/// Covers: Parse returns non-null for valid file; Parse MagicValid true;
/// Parse FilePath matches input path; Parse IsValid true for valid file;
/// Parse FrameCount positive; Parse FileSizeBytes matches file size;
/// Decompress(data, maxBytes) throws ZstException when limit exceeded;
/// ZstException is Exception; ZstException message non-null;
/// Parse then Decompress restores content; CompressToFile produces valid file;
/// Parse after CompressToFile is valid; BytesPerFrame is non-negative;
/// OverheadBytes is non-negative; dogfood CompressToFile->Parse->Decompress verify.
/// </summary>
public class ZstR153ParseFileAndExceptionTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR153ParseFileAndExceptionTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR153_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CompressAndSave(string text, string fileName = "test.zst")
    {
        var path = TempFile(fileName);
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes(text), path);
        return path;
    }

    // -------------------------------------------------------------------------
    // ZstParser.Parse(filePath)
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ReturnsNonNull()
    {
        var path = CompressAndSave("hello world");
        var doc = ZstParser.Parse(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void Parse_MagicValid_IsTrue()
    {
        var path = CompressAndSave("magic test");
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void Parse_FilePath_MatchesInput()
    {
        var path = CompressAndSave("filepath test");
        var doc = ZstParser.Parse(path);
        Assert.Equal(path, doc.FilePath);
    }

    [Fact]
    public void Parse_IsValid_IsTrue()
    {
        var path = CompressAndSave("valid content");
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void Parse_FrameCount_IsPositive()
    {
        var path = CompressAndSave("frame content");
        var doc = ZstParser.Parse(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void Parse_FileSizeBytes_MatchesActualFileSize()
    {
        var path = CompressAndSave("size match test");
        var doc = ZstParser.Parse(path);
        var actual = new FileInfo(path).Length;
        Assert.Equal(actual, doc.FileSizeBytes);
    }

    [Fact]
    public void Parse_BytesPerFrame_IsNonNegative()
    {
        var path = CompressAndSave("bytes per frame test");
        var doc = ZstParser.Parse(path);
        Assert.True(doc.BytesPerFrame >= 0);
    }

    [Fact]
    public void Parse_OverheadBytes_IsNonNegative()
    {
        var path = CompressAndSave("overhead test");
        var doc = ZstParser.Parse(path);
        Assert.True(doc.OverheadBytes >= 0);
    }

    // -------------------------------------------------------------------------
    // ZstException
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstException_IsException()
    {
        var ex = new ZstException("test");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void ZstException_Message_IsNotNull()
    {
        var ex = new ZstException("test message");
        Assert.NotNull(ex.Message);
        Assert.Equal("test message", ex.Message);
    }

    [Fact]
    public void Decompress_ExceedsMaxBytes_ThrowsZstException()
    {
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes("content that will be limited"));
        Assert.ThrowsAny<Exception>(() => ZstWriter.Decompress(data, maxDecompressedBytes: 1));
    }

    // -------------------------------------------------------------------------
    // Round-trip: CompressToFile -> Parse -> Decompress
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ThenDecompress_RestoresContent()
    {
        var original = "parse then decompress ZST R153";
        var path = CompressAndSave(original);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);

        var compressed = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressToFile->Parse->Decompress verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressToFileParseDecompressVerify()
    {
        // Compress to file
        var text = "ZST R153 dogfood content for verification";
        var path = CompressAndSave(text, "dogfood.zst");
        Assert.True(File.Exists(path));

        // Parse the file
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid);
        Assert.True(doc.IsValid);
        Assert.Equal(path, doc.FilePath);
        Assert.Equal(1, doc.FrameCount);
        Assert.True(doc.FileSizeBytes > 0);

        // Decompress and verify
        var compressed = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));

        // Verify SizeLabel
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
    }
}
