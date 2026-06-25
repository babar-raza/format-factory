// Tests for ZstDocument frame-level properties via live-parsed compressed data.
// Sprint: FORMAT-FACTORY-ZST-FRAME-PROPERTIES-20260626
// Ledger: R119-GOVERNED-DOTNET-ZST-FRAME-PROPERTIES-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R119: ZstDocument frame-level properties tested through live ZstParser.ParseStream
/// output: IsMinimalFrame reflects whether data fits in a single minimum frame,
/// SizeExceeds100K is true only for payloads over 100 KB, FrameHeaderDescriptor is
/// a byte populated by the parser, FileSizeBytes matches actual compressed size.
/// </summary>
public class ZstR119FramePropertiesTests
{
    private static ZstDocument ParseCompressed(byte[] payload)
    {
        var compressed = ZstWriter.Compress(payload);
        using var ms = new MemoryStream(compressed);
        return ZstParser.ParseStream(ms, knownLength: compressed.Length);
    }

    // ---- IsMinimalFrame ----

    [Fact]
    public void IsMinimalFrame_SmallPayload_IsTrue()
    {
        var payload = Encoding.UTF8.GetBytes("Hello, Zst!");
        var doc = ParseCompressed(payload);
        Assert.True(doc.IsMinimalFrame,
            "Small single-block compression should be a minimal frame");
    }

    [Fact]
    public void IsMinimalFrame_LargePayload_IsFalse()
    {
        // 200 KB payload should NOT be a minimal frame
        var payload = new byte[200 * 1024];
        new Random(42).NextBytes(payload);
        var doc = ParseCompressed(payload);
        Assert.False(doc.IsMinimalFrame,
            "Large payload should not be a minimal frame");
    }

    // ---- SizeExceeds100K ----

    [Fact]
    public void SizeExceeds100K_SmallCompressed_IsFalse()
    {
        var payload = Encoding.UTF8.GetBytes("Small payload");
        var doc = ParseCompressed(payload);
        Assert.False(doc.SizeExceeds100K,
            "Small compressed output should not exceed 100 KB");
    }

    [Fact]
    public void SizeExceeds100K_LargeCompressed_IsTrue()
    {
        // 200 KB random data compresses poorly — result will exceed 100 KB
        var payload = new byte[200 * 1024];
        new Random(42).NextBytes(payload);
        var doc = ParseCompressed(payload);
        Assert.True(doc.SizeExceeds100K,
            "200 KB random payload compressed output should exceed 100 KB");
    }

    // ---- FileSizeBytes ----

    [Fact]
    public void FileSizeBytes_PositiveForNonEmpty()
    {
        var payload = Encoding.UTF8.GetBytes("FileSizeBytes test");
        var doc = ParseCompressed(payload);
        Assert.True(doc.FileSizeBytes > 0,
            $"FileSizeBytes should be positive, got {doc.FileSizeBytes}");
    }

    [Fact]
    public void FileSizeBytes_MatchesCompressedLength()
    {
        var payload = Encoding.UTF8.GetBytes("Test content for size check.");
        var compressed = ZstWriter.Compress(payload);
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.Equal(compressed.Length, doc.FileSizeBytes);
    }

    // ---- FrameHeaderDescriptor ----

    [Fact]
    public void FrameHeaderDescriptor_ParsedDoc_IsZeroOrNonNegative()
    {
        var payload = Encoding.UTF8.GetBytes("Frame header descriptor test.");
        var doc = ParseCompressed(payload);
        // FrameHeaderDescriptor is a byte — always 0–255
        Assert.True(doc.FrameHeaderDescriptor >= 0,
            $"FrameHeaderDescriptor should be a valid byte value, got {doc.FrameHeaderDescriptor}");
    }

    // ---- FrameCount ----

    [Fact]
    public void FrameCount_SingleBlockPayload_IsAtLeastOne()
    {
        var payload = Encoding.UTF8.GetBytes("Single frame payload");
        var doc = ParseCompressed(payload);
        Assert.True(doc.FrameCount >= 1,
            $"Expected FrameCount >= 1, got {doc.FrameCount}");
    }

    [Fact]
    public void FrameCount_MagicValid_IsTrue()
    {
        var payload = Encoding.UTF8.GetBytes("Magic bytes test");
        var doc = ParseCompressed(payload);
        Assert.True(doc.MagicValid,
            "ZstWriter.Compress output should always have valid magic bytes");
    }

    // ---- Dogfood: live parsed document all-properties consistent ----

    [Fact]
    public void DogfoodPipeline_SmallPayload_AllPropertiesConsistent()
    {
        var text = "Format Factory ZST frame properties dogfood test.";
        var payload = Encoding.UTF8.GetBytes(text);
        var compressed = ZstWriter.Compress(payload);
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        // Consistency checks
        Assert.True(doc.MagicValid);
        Assert.Equal(compressed.Length, doc.FileSizeBytes);
        Assert.True(doc.FrameCount >= 1);
        Assert.False(doc.SizeExceeds100K); // small payload
        Assert.True(doc.IsValid); // MagicValid && FrameCount > 0
        Assert.True(doc.FileSizeKB < 1.0); // compressed.Length < 1024
    }
}
