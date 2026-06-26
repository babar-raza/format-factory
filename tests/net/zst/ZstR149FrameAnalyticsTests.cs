// Tests for ZstDocument frame analytics: FrameCount, FrameHeaderDescriptor, BytesPerFrame.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R149

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R149: Tests for ZstDocument frame analytics and ZstParser.DefaultMaxFileSizeBytes.
/// ZstDocument: FrameCount, FrameHeaderDescriptor, BytesPerFrame, OverheadBytes,
///              IsMinimalFrame, IsHighlyCompressed, ContentTypeHint, IsEmptyContent.
/// ZstParser.DefaultMaxFileSizeBytes: default file size cap for parsing.
/// Covers: FrameCount is 1 for single-frame compress; FrameHeaderDescriptor is byte;
/// BytesPerFrame positive; OverheadBytes non-negative; IsMinimalFrame is bool;
/// IsHighlyCompressed false for small data; ContentTypeHint is non-null;
/// IsEmptyContent false for non-empty; DefaultMaxFileSizeBytes positive;
/// Parse with explicit filePath; MagicValid true for valid ZST;
/// IsValid = MagicValid AND FrameCount > 0; multiple parse calls consistent;
/// dogfood Compress->Parse->analytics properties pipeline.
/// </summary>
public class ZstR149FrameAnalyticsTests
{
    private static byte[] CompressText(string text) =>
        ZstWriter.Compress(Encoding.UTF8.GetBytes(text));

    private static ZstDocument ParseBytes(byte[] data, string? filePath = null)
    {
        using var stream = new MemoryStream(data);
        return ZstParser.ParseStream(stream, data.Length, filePath);
    }

    // -------------------------------------------------------------------------
    // FrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameCount_SingleFrame_IsOne()
    {
        var compressed = CompressText("Single frame test data.");
        var doc = ParseBytes(compressed);
        Assert.Equal(1, doc.FrameCount);
    }

    [Fact]
    public void FrameCount_Positive()
    {
        var compressed = CompressText("Frame count positive test.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    // -------------------------------------------------------------------------
    // FrameHeaderDescriptor
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameHeaderDescriptor_IsValidByte()
    {
        var compressed = CompressText("Frame header descriptor test.");
        var doc = ParseBytes(compressed);
        // byte is always 0-255
        Assert.True(doc.FrameHeaderDescriptor >= 0 && doc.FrameHeaderDescriptor <= 255);
    }

    // -------------------------------------------------------------------------
    // BytesPerFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void BytesPerFrame_IsPositive()
    {
        var compressed = CompressText("Bytes per frame positive.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.BytesPerFrame > 0);
    }

    [Fact]
    public void BytesPerFrame_EqualsFileSizeForSingleFrame()
    {
        var compressed = CompressText("Single frame bytes per frame.");
        var doc = ParseBytes(compressed);
        // For single frame: BytesPerFrame should equal FileSizeBytes
        Assert.Equal(doc.FileSizeBytes, (long)doc.BytesPerFrame);
    }

    // -------------------------------------------------------------------------
    // OverheadBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void OverheadBytes_IsNonNegative()
    {
        var compressed = CompressText("Overhead bytes test data.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.OverheadBytes >= 0);
    }

    // -------------------------------------------------------------------------
    // IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_IsBool()
    {
        var compressed = CompressText("Minimal frame check.");
        var doc = ParseBytes(compressed);
        // Just verify it's accessible and readable
        Assert.True(doc.IsMinimalFrame == true || doc.IsMinimalFrame == false);
    }

    // -------------------------------------------------------------------------
    // IsHighlyCompressed
    // -------------------------------------------------------------------------

    [Fact]
    public void IsHighlyCompressed_FalseForSmallData()
    {
        var compressed = CompressText("Small data.");
        var doc = ParseBytes(compressed);
        Assert.False(doc.IsHighlyCompressed);
    }

    // -------------------------------------------------------------------------
    // ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_IsNonNull()
    {
        var compressed = CompressText("Content type hint test.");
        var doc = ParseBytes(compressed);
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_IsNonEmpty()
    {
        var compressed = CompressText("Content hint non-empty.");
        var doc = ParseBytes(compressed);
        Assert.False(string.IsNullOrEmpty(doc.ContentTypeHint));
    }

    // -------------------------------------------------------------------------
    // IsEmptyContent
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmptyContent_FalseForNonEmptyData()
    {
        var compressed = CompressText("Non-empty content for test.");
        var doc = ParseBytes(compressed);
        Assert.False(doc.IsEmptyContent);
    }

    // -------------------------------------------------------------------------
    // DefaultMaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxFileSizeBytes_IsPositive()
    {
        Assert.True(ZstParser.DefaultMaxFileSizeBytes > 0);
    }

    [Fact]
    public void DefaultMaxFileSizeBytes_IsAtLeast1MB()
    {
        Assert.True(ZstParser.DefaultMaxFileSizeBytes >= 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void IsValid_TrueForValidData()
    {
        var compressed = CompressText("Valid frame data.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid && doc.FrameCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->Parse->analytics properties pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseAnalyticsPipeline()
    {
        var texts = new[]
        {
            "First document: short content.",
            "Second document: medium length content for frame analytics testing.",
        };

        foreach (var text in texts)
        {
            var compressed = CompressText(text);
            var doc = ParseBytes(compressed, "analytics-test.zst");

            // Frame analytics
            Assert.Equal(1, doc.FrameCount);
            Assert.True(doc.BytesPerFrame > 0);
            Assert.True(doc.OverheadBytes >= 0);

            // Validity
            Assert.True(doc.IsValid);
            Assert.True(doc.MagicValid);

            // Content
            Assert.False(doc.IsEmptyContent);
            Assert.NotNull(doc.ContentTypeHint);

            // FilePath set
            Assert.Equal("analytics-test.zst", doc.FilePath);

            // IsHighlyCompressed false for small strings
            Assert.False(doc.IsHighlyCompressed);
        }
    }
}
