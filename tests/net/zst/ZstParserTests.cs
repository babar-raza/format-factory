// FormatFactory.Zst.Tests -- ZstParser unit tests
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using FormatFactory.Zst;
using FormatFactory.Zst.Exceptions;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>Core parser tests for the .NET ZST implementation.</summary>
public class ZstParserTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/zst/valid"));

    private string Sample(string name) => Path.Combine(SamplesDir, name);

    // --- Parse() guard tests ---

    [Fact]
    public void Parse_NullPath_Throws()
    {
        Assert.Throws<ZstFileNotFoundException>(() => ZstParser.Parse(null!));
    }

    [Fact]
    public void Parse_NonExistentFile_Throws()
    {
        Assert.Throws<ZstFileNotFoundException>(() =>
            ZstParser.Parse(Path.Combine(SamplesDir, "does-not-exist.zst")));
    }

    [Fact]
    public void Parse_FileSizeExceedsGuard_Throws()
    {
        // Use any real file but pass a tiny limit (1 byte).
        Assert.Throws<ZstFileSizeException>(() =>
            ZstParser.Parse(Sample("minimal-synthetic.zst"), maxFileSizeBytes: 1));
    }

    // --- Magic validation ---

    [Fact]
    public void Parse_MinimalSynthetic_MagicValid()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void Parse_Block128K_MagicValid()
    {
        var doc = ZstParser.Parse(Sample("block-128k.zst"));
        Assert.True(doc.MagicValid);
    }

    // --- File size ---

    [Fact]
    public void Parse_MinimalSynthetic_FileSizePositive()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.FileSizeBytes > 0);
    }

    [Fact]
    public void Parse_Block128K_FileSizePositive()
    {
        var doc = ZstParser.Parse(Sample("block-128k.zst"));
        Assert.True(doc.FileSizeBytes > 0);
    }

    [Fact]
    public void Parse_Block128K_SizeExceeds100K()
    {
        var doc = ZstParser.Parse(Sample("block-128k.zst"));
        Assert.True(doc.SizeExceeds100K);
    }

    [Fact]
    public void Parse_MinimalSynthetic_SizeDoesNotExceed100K()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.False(doc.SizeExceeds100K);
    }

    // --- Frame count ---

    [Fact]
    public void Parse_MinimalSynthetic_FrameCountAtLeastOne()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void Parse_Block128K_FrameCountAtLeastOne()
    {
        var doc = ZstParser.Parse(Sample("block-128k.zst"));
        Assert.True(doc.FrameCount >= 1);
    }

    // --- IsMinimalFrame ---

    [Fact]
    public void Parse_MinimalSynthetic_IsMinimalFrame()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.IsMinimalFrame);
    }

    [Fact]
    public void Parse_Block128K_NotMinimalFrame()
    {
        var doc = ZstParser.Parse(Sample("block-128k.zst"));
        Assert.False(doc.IsMinimalFrame);
    }

    // --- OverheadBytes ---

    [Fact]
    public void Parse_MinimalSynthetic_OverheadBytesNonNegative()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.OverheadBytes >= 0);
    }

    // --- BytesPerFrame ---

    [Fact]
    public void Parse_AnyFile_BytesPerFramePositive()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.True(doc.BytesPerFrame > 0);
    }

    // --- ContentTypeHint ---

    [Fact]
    public void Parse_MinimalSynthetic_ContentTypeHintIsCompressedData()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.Equal("compressed_data", doc.ContentTypeHint);
    }

    // --- FrameHeaderDescriptor ---

    [Fact]
    public void Parse_MinimalSynthetic_FrameHeaderDescriptorIsByte()
    {
        var doc = ZstParser.Parse(Sample("minimal-synthetic.zst"));
        Assert.IsType<byte>(doc.FrameHeaderDescriptor);
    }

    // --- FilePath ---

    [Fact]
    public void Parse_MinimalSynthetic_FilePathMatchesInput()
    {
        var path = Sample("minimal-synthetic.zst");
        var doc = ZstParser.Parse(path);
        Assert.Equal(path, doc.FilePath);
    }

    // --- Multiple samples ---

    [Theory]
    [InlineData("minimal-synthetic.zst")]
    [InlineData("block-128k.zst")]
    [InlineData("random-data.zst")]
    [InlineData("text-compressed.zst")]
    public void Parse_AllSamples_MagicValid(string sampleName)
    {
        var doc = ZstParser.Parse(Sample(sampleName));
        Assert.True(doc.MagicValid, $"Expected magic valid for {sampleName}");
    }

    [Theory]
    [InlineData("minimal-synthetic.zst")]
    [InlineData("block-128k.zst")]
    [InlineData("random-data.zst")]
    [InlineData("text-compressed.zst")]
    public void Parse_AllSamples_FileSizePositive(string sampleName)
    {
        var doc = ZstParser.Parse(Sample(sampleName));
        Assert.True(doc.FileSizeBytes > 0, $"Expected positive file size for {sampleName}");
    }

    [Theory]
    [InlineData("minimal-synthetic.zst")]
    [InlineData("block-128k.zst")]
    [InlineData("random-data.zst")]
    [InlineData("text-compressed.zst")]
    public void Parse_AllSamples_FrameCountPositive(string sampleName)
    {
        var doc = ZstParser.Parse(Sample(sampleName));
        Assert.True(doc.FrameCount >= 1, $"Expected at least one frame for {sampleName}");
    }
}
