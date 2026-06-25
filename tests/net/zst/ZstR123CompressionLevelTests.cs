// Tests for ZstWriter compression-level constants and multi-level round-trips.
// Sprint: FORMAT-FACTORY-ZST-COMPRESS-LEVELS-R123-20260627
// Ledger: R123-GOVERNED-DOTNET-ZST-COMPRESS-LEVELS-001

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R123: ZstWriter exposes DefaultCompressionLevel (3), MinCompressionLevel (1),
/// MaxCompressionLevel (22), and DefaultMaxDecompressedBytes (512 MB).
/// Compress(bytes, level) at level 1 and level 22 both produce valid Zstd output
/// that round-trips correctly (compress→decompress restores original payload).
/// Level-22 output starts with Zstandard magic bytes.
/// </summary>
public class ZstR123CompressionLevelTests
{
    private static byte[] Utf8(string s) => Encoding.UTF8.GetBytes(s);

    // ---- Compression-level constants ----

    [Fact]
    public void DefaultCompressionLevel_IsThree()
    {
        Assert.Equal(3, ZstWriter.DefaultCompressionLevel);
    }

    [Fact]
    public void MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_IsTwentyTwo()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_IsPositive()
    {
        // 512 MB limit — just assert it's a large positive value
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > 0);
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes >= 1024 * 1024);
    }

    // ---- Level 1 (fastest): round-trip ----

    [Fact]
    public void Compress_LevelOne_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(Utf8("hello at level one"), level: 1);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_LevelOne_RoundTripRestoresOriginal()
    {
        var original   = Utf8("Round-trip payload at min compression level.");
        var compressed = ZstWriter.Compress(original, level: 1);
        var restored   = ZstWriter.Decompress(compressed);
        Assert.Equal(original, restored);
    }

    [Fact]
    public void Compress_LevelOne_OutputStartsWithMagicBytes()
    {
        var compressed = ZstWriter.Compress(Utf8("magic check"), level: 1);
        // Zstandard magic: 0xFD 0x2F 0xB5 0x28 (little-endian)
        Assert.True(compressed.Length >= 4);
        Assert.Equal(0x28, compressed[0]);
        Assert.Equal(0xB5, compressed[1]);
        Assert.Equal(0x2F, compressed[2]);
        Assert.Equal(0xFD, compressed[3]);
    }

    // ---- Level 22 (best): round-trip ----

    [Fact]
    public void Compress_LevelTwentyTwo_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(Utf8("hello at level twenty-two"), level: 22);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_LevelTwentyTwo_RoundTripRestoresOriginal()
    {
        var original   = Utf8("Round-trip payload at max compression level.");
        var compressed = ZstWriter.Compress(original, level: 22);
        var restored   = ZstWriter.Decompress(compressed);
        Assert.Equal(original, restored);
    }

    [Fact]
    public void Compress_LevelTwentyTwo_OutputStartsWithMagicBytes()
    {
        var compressed = ZstWriter.Compress(Utf8("magic check max level"), level: 22);
        Assert.True(compressed.Length >= 4);
        Assert.Equal(0x28, compressed[0]);
        Assert.Equal(0xB5, compressed[1]);
        Assert.Equal(0x2F, compressed[2]);
        Assert.Equal(0xFD, compressed[3]);
    }

    // ---- Default level: consistent with DefaultCompressionLevel ----

    [Fact]
    public void Compress_DefaultLevel_RoundTripRestoresOriginal()
    {
        var original   = Utf8("Payload at default compression level.");
        var compressed = ZstWriter.Compress(original);
        var restored   = ZstWriter.Decompress(compressed);
        Assert.Equal(original, restored);
    }

    // ---- Dogfood: JSON payload compressed at all three representative levels ----

    [Fact]
    public void DogfoodPipeline_JsonPayload_AllLevelsRoundTrip()
    {
        var json = Utf8(
            "{\"product\":\"FormatFactory\",\"version\":\"1.0\"," +
            "\"formats\":[\"FODS\",\"ZST\",\"CSV\",\"NDJSON\"],\"year\":2026}");

        foreach (var level in new[] { 1, ZstWriter.DefaultCompressionLevel, 22 })
        {
            var compressed = ZstWriter.Compress(json, level: level);
            var restored   = ZstWriter.Decompress(compressed);
            Assert.Equal(json, restored);
        }
    }
}
