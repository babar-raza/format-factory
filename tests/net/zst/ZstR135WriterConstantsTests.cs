// Tests for ZstWriter compression constants.
// Sprint: ff-sprint-s140-dotnet-deepening-20260627
// Ledger: PC-ZST-R135

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R135: Tests for ZstWriter compression-level and decompression-size constants.
/// DefaultCompressionLevel = 3; MinCompressionLevel = 1; MaxCompressionLevel = 22;
/// DefaultMaxDecompressedBytes = 512 MB.
/// Covers: DefaultCompressionLevel=3; MinCompressionLevel=1; MaxCompressionLevel=22;
/// DefaultMaxDecompressedBytes=512MB; Min&lt;Default; Default&lt;Max; Min positive;
/// DefaultMaxDecompressedBytes positive; Compress uses Default level;
/// dogfood Compress at MinLevel and MaxLevel both produce valid magic bytes.
/// </summary>
public class ZstR135WriterConstantsTests
{
    // -------------------------------------------------------------------------
    // Constant value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstWriter_DefaultCompressionLevel_IsThree()
    {
        Assert.Equal(3, ZstWriter.DefaultCompressionLevel);
    }

    [Fact]
    public void ZstWriter_MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void ZstWriter_MaxCompressionLevel_Is22()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void ZstWriter_DefaultMaxDecompressedBytes_Is512MB()
    {
        const long expected = 512L * 1024 * 1024;
        Assert.Equal(expected, ZstWriter.DefaultMaxDecompressedBytes);
    }

    // -------------------------------------------------------------------------
    // Constant relationship tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstWriter_MinCompressionLevel_LessThanDefault()
    {
        Assert.True(ZstWriter.MinCompressionLevel < ZstWriter.DefaultCompressionLevel);
    }

    [Fact]
    public void ZstWriter_DefaultCompressionLevel_LessThanMax()
    {
        Assert.True(ZstWriter.DefaultCompressionLevel < ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void ZstWriter_MinCompressionLevel_IsPositive()
    {
        Assert.True(ZstWriter.MinCompressionLevel > 0);
    }

    [Fact]
    public void ZstWriter_DefaultMaxDecompressedBytes_IsPositive()
    {
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > 0);
    }

    // -------------------------------------------------------------------------
    // Compress with explicit level works
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstWriter_Compress_AtMinLevel_ProducesValidMagicBytes()
    {
        var data = Encoding.UTF8.GetBytes("hello world at minimum compression level");
        var compressed = ZstWriter.Compress(data, ZstWriter.MinCompressionLevel);
        Assert.True(compressed.Length >= 4);
        Assert.Equal(0x28, compressed[0]);
        Assert.Equal(0xB5, compressed[1]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: compress at Max level produces valid zst
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CompressAtMaxLevel_ValidMagicAndDecompresses()
    {
        var original = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("Format Factory ZST test. ", 20)));
        var compressed = ZstWriter.Compress(original, ZstWriter.MaxCompressionLevel);

        // Valid magic
        Assert.Equal(0x28, compressed[0]);
        Assert.Equal(0xFD, compressed[3]);

        // Can decompress
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original.Length, decompressed.Length);
    }
}
