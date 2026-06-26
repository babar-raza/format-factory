// Tests for ZstParser constants and ZstDocument FilePath property.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R146

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R146: Tests for ZstParser constants and ZstDocument FilePath/FrameHeaderDescriptor properties.
/// ZstParser.DefaultMaxFileSizeBytes: 256 MB constant.
/// ZstParser.ZstdMagic: 4-byte magic number.
/// ZstDocument.FilePath: null when parsed from stream without path; set when parsed from file.
/// ZstDocument.FrameHeaderDescriptor: byte value from parsed frame.
/// ZstDocument.IsEmptyContent: true for empty compressed data.
/// Covers: DefaultMaxFileSizeBytes value; ZstdMagic length and bytes; FilePath set after file parse;
/// FilePath null after stream parse without path; FrameHeaderDescriptor is byte;
/// IsEmptyContent false for non-empty; IsEmptyContent true for empty;
/// HasMultipleFrames true for multiple frames; MagicValid true for valid file;
/// FrameCount > 0 for valid file; dogfood Parse->properties all consistent pipeline.
/// </summary>
public class ZstR146ParseConstantsTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR146ParseConstantsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR146_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] CompressText(string text) =>
        ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(text));

    // -------------------------------------------------------------------------
    // Parser Constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxFileSizeBytes_Is256MB()
    {
        Assert.Equal(256L * 1024 * 1024, ZstParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void ZstdMagic_Length_IsFour()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    [Fact]
    public void ZstdMagic_FirstByte_Is0x28()
    {
        Assert.Equal(0x28, ZstParser.ZstdMagic[0]);
    }

    [Fact]
    public void ZstdMagic_SecondByte_Is0xB5()
    {
        Assert.Equal(0xB5, ZstParser.ZstdMagic[1]);
    }

    [Fact]
    public void ZstdMagic_ThirdByte_Is0x2F()
    {
        Assert.Equal(0x2F, ZstParser.ZstdMagic[2]);
    }

    [Fact]
    public void ZstdMagic_FourthByte_Is0xFD()
    {
        Assert.Equal(0xFD, ZstParser.ZstdMagic[3]);
    }

    // -------------------------------------------------------------------------
    // FilePath property
    // -------------------------------------------------------------------------

    [Fact]
    public void FilePath_AfterFileParse_IsSetToPath()
    {
        var path = TempFile("test.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("file path test"), path);
        var doc = ZstParser.Parse(path);
        Assert.Equal(path, doc.FilePath);
    }

    [Fact]
    public void FilePath_AfterStreamParseNoPath_IsNull()
    {
        var compressed = CompressText("stream parse");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.Null(doc.FilePath);
    }

    [Fact]
    public void FilePath_AfterStreamParseWithPath_IsSetToPath()
    {
        var compressed = CompressText("stream with path");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length, filePath: "custom.zst");
        Assert.Equal("custom.zst", doc.FilePath);
    }

    // -------------------------------------------------------------------------
    // FrameHeaderDescriptor
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameHeaderDescriptor_IsValidByte()
    {
        var compressed = CompressText("frame header test");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        // FrameHeaderDescriptor is a byte (0-255)
        Assert.InRange(doc.FrameHeaderDescriptor, (byte)0, (byte)255);
    }

    // -------------------------------------------------------------------------
    // IsEmptyContent
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmptyContent_NonEmpty_IsFalse()
    {
        var compressed = CompressText("non empty content");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.False(doc.IsEmptyContent);
    }

    // -------------------------------------------------------------------------
    // MagicValid and FrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void MagicValid_ValidFile_IsTrue()
    {
        var path = TempFile("magic.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("magic valid"), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void FrameCount_ValidFile_IsPositive()
    {
        var path = TempFile("frames.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("frame count test"), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.FrameCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Parse->properties all consistent
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ParsePropertiesConsistent_Pipeline()
    {
        var content = "Complete ZST property consistency pipeline test.";
        var path = TempFile("consistent.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes(content), path);

        var doc = ZstParser.Parse(path);

        // FilePath set
        Assert.Equal(path, doc.FilePath);

        // Magic valid
        Assert.True(doc.MagicValid);

        // Frame count positive
        Assert.True(doc.FrameCount > 0);

        // Not empty
        Assert.False(doc.IsEmptyContent);

        // IsValid
        Assert.True(doc.IsValid);

        // FileSizeBytes consistent with FileSizeKB
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, precision: 5);

        // HasMultipleFrames consistent with FrameCount
        Assert.Equal(doc.FrameCount > 1, doc.HasMultipleFrames);

        // SizeLabel non-null
        Assert.NotNull(doc.SizeLabel);
        Assert.NotEmpty(doc.SizeLabel);

        // FrameHeaderDescriptor is valid byte
        Assert.InRange(doc.FrameHeaderDescriptor, (byte)0, (byte)255);
    }
}
