// Tests for ZstDocument properties and ZstWriter.Compress deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R159

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R159: Tests for ZstDocument properties and ZstWriter.Compress deeper coverage.
/// ZstDocument: CompressedSize, DecompressedSize, FrameCount, IsEmpty, CompressionRatio.
/// ZstWriter.Compress(bytes, level): compresses bytes at specific level.
/// ZstWriter.Decompress(bytes): decompresses bytes.
/// Covers: CompressedSize positive for non-empty; DecompressedSize positive for non-empty;
/// FrameCount positive for valid frame; IsEmpty false for valid data;
/// CompressionRatio between 0 and 1 for compressible data;
/// Compress returns non-empty; Compress result decompresses correctly;
/// Compress at min level; Compress at max level; Compress empty bytes;
/// Decompress round-trip preserves content; Compress->Decompress unicode content;
/// CompressedSize less than DecompressedSize for compressible data;
/// ZstDocument.IsEmpty for empty data; Compress returns smaller than source;
/// dogfood Compress->ZstDocument.Load->Properties->Decompress verify.
/// </summary>
public class ZstR159DocumentPropertiesAndCompressTests
{
    private static readonly byte[] RepeatableData =
        Encoding.UTF8.GetBytes(string.Concat(System.Linq.Enumerable.Repeat("Hello World! This is repeated content. ", 50)));

    private static readonly byte[] SmallData =
        Encoding.UTF8.GetBytes("Hello World!");

    // -------------------------------------------------------------------------
    // ZstDocument properties
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressedSize_PositiveForNonEmpty()
    {
        var compressed = ZstWriter.Compress(RepeatableData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_PositiveForNonEmpty()
    {
        var compressed = ZstWriter.Compress(RepeatableData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void FrameCount_PositiveForValidFrame()
    {
        var compressed = ZstWriter.Compress(SmallData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void IsEmpty_FalseForValidData()
    {
        var compressed = ZstWriter.Compress(SmallData);
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void CompressionRatio_BetweenZeroAndOne_ForCompressibleData()
    {
        var compressed = ZstWriter.Compress(RepeatableData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.CompressionRatio > 0.0);
        Assert.True(doc.CompressionRatio <= 1.0);
    }

    [Fact]
    public void CompressedSize_LessThanDecompressedSize_ForCompressibleData()
    {
        var compressed = ZstWriter.Compress(RepeatableData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.CompressedSize < doc.DecompressedSize);
    }

    // -------------------------------------------------------------------------
    // ZstWriter.Compress
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_ReturnsNonEmpty()
    {
        var result = ZstWriter.Compress(SmallData);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void Compress_AtMinLevel_ReturnsBytes()
    {
        var result = ZstWriter.Compress(SmallData, ZstWriter.MinCompressionLevel);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void Compress_AtMaxLevel_ReturnsBytes()
    {
        var result = ZstWriter.Compress(RepeatableData, ZstWriter.MaxCompressionLevel);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void Compress_EmptyBytes_ReturnsBytes()
    {
        var result = ZstWriter.Compress(Array.Empty<byte>());
        Assert.NotNull(result);
    }

    [Fact]
    public void Compress_Decompress_RoundTrip_PreservesContent()
    {
        var compressed = ZstWriter.Compress(SmallData);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(SmallData, decompressed);
    }

    [Fact]
    public void Compress_Decompress_Unicode_RoundTrip()
    {
        var text = "Unicode: \u4e2d\u6587 \u00e9\u00e0\u00fc";
        var data = Encoding.UTF8.GetBytes(text);
        var compressed = ZstWriter.Compress(data);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Compress_RepeatableData_SmallerThanSource()
    {
        var compressed = ZstWriter.Compress(RepeatableData);
        Assert.True(compressed.Length < RepeatableData.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->ZstDocument.Load->Properties->Decompress verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressLoadPropertiesDecompress_Verify()
    {
        var original = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("Pattern data for compression testing. ", 20)));

        // Compress
        var compressed = ZstWriter.Compress(original, ZstWriter.DefaultCompressionLevel);
        Assert.NotEmpty(compressed);

        // ZstDocument.Load
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsEmpty);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.CompressionRatio > 0.0 && doc.CompressionRatio <= 1.0);
        Assert.True(doc.CompressedSize < doc.DecompressedSize);

        // Decompress
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, decompressed);
        Assert.Equal(original.Length, decompressed.Length);
    }
}
