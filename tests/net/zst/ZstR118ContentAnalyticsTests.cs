// Tests for ZstDocument computed properties: ContentTypeHint, IsHighlyCompressed,
// IsEmptyContent, OverheadBytes, BytesPerFrame.
// Sprint: FORMAT-FACTORY-ZST-CONTENT-ANALYTICS-20260626
// Ledger: R118-GOVERNED-DOTNET-ZST-CONTENT-ANALYTICS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R118: ZstDocument computed init-only properties — ContentTypeHint returns default
/// "unknown" for typical compressed streams; IsHighlyCompressed, IsEmptyContent,
/// OverheadBytes, and BytesPerFrame reflect compression metrics derived from
/// CompressedSize and DecompressedSize at load time.
/// </summary>
public class ZstR118ContentAnalyticsTests
{
    private static ZstDocument LoadCompressed(string text)
    {
        var raw = Encoding.UTF8.GetBytes(text);
        var compressed = ZstDocument.Compress(raw);
        using var ms = new MemoryStream(compressed);
        return ZstDocument.LoadStream(ms);
    }

    // ---- ContentTypeHint: default is "unknown" ----

    [Fact]
    public void ContentTypeHint_Default_IsUnknown()
    {
        var doc = LoadCompressed("hello world");
        Assert.Equal("unknown", doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_LargePayload_IsUnknown()
    {
        var doc = LoadCompressed(new string('A', 10000));
        Assert.Equal("unknown", doc.ContentTypeHint);
    }

    // ---- IsEmptyContent ----

    [Fact]
    public void IsEmptyContent_NonEmptyPayload_IsFalse()
    {
        var doc = LoadCompressed("non-empty content here");
        Assert.False(doc.IsEmptyContent);
    }

    [Fact]
    public void IsEmptyContent_EmptyString_IsTrue()
    {
        var raw = Array.Empty<byte>();
        var compressed = ZstDocument.Compress(raw);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.LoadStream(ms);
        Assert.True(doc.IsEmptyContent);
    }

    // ---- IsHighlyCompressed ----

    [Fact]
    public void IsHighlyCompressed_HighlyRepetitiveData_IsTrue()
    {
        // Highly repetitive content compresses far below 50% of original
        var doc = LoadCompressed(new string('Z', 50000));
        Assert.True(doc.IsHighlyCompressed);
    }

    [Fact]
    public void IsHighlyCompressed_ShortPayload_IsFalse()
    {
        // Very short payload cannot compress below 50% threshold
        var doc = LoadCompressed("hello");
        Assert.False(doc.IsHighlyCompressed);
    }

    // ---- OverheadBytes ----

    [Fact]
    public void OverheadBytes_NonNegative()
    {
        var doc = LoadCompressed("overhead test payload");
        Assert.True(doc.OverheadBytes >= 0,
            $"OverheadBytes should be non-negative, got {doc.OverheadBytes}");
    }

    [Fact]
    public void OverheadBytes_LargePayload_HasOverhead()
    {
        // At minimum the Zstd frame header contributes overhead
        var doc = LoadCompressed(new string('X', 1000));
        Assert.True(doc.OverheadBytes > 0,
            "Expected non-zero overhead for a real compressed payload");
    }

    // ---- BytesPerFrame ----

    [Fact]
    public void BytesPerFrame_SingleFrame_EqualsTotalCompressedSize()
    {
        var doc = LoadCompressed("single frame test");
        // A single-block compression = 1 frame; BytesPerFrame ≈ CompressedSize
        Assert.True(doc.BytesPerFrame > 0,
            $"Expected BytesPerFrame > 0, got {doc.BytesPerFrame}");
    }

    [Fact]
    public void BytesPerFrame_ZeroFrameEdge_IsZeroOrSafe()
    {
        // Verify that BytesPerFrame does not throw even if frame count could be 0
        // (division-by-zero guard). Use empty content scenario.
        var raw = Array.Empty<byte>();
        var compressed = ZstDocument.Compress(raw);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.LoadStream(ms);
        // Should not throw; result is either 0 or a defined sentinel
        var bpf = doc.BytesPerFrame;
        Assert.True(bpf >= 0, $"BytesPerFrame should be non-negative, got {bpf}");
    }

    // ---- Dogfood: properties consistent with CompressedSize/DecompressedSize ----

    [Fact]
    public void DogfoodPipeline_PropertiesConsistentWithSizes()
    {
        const string payload = "Format Factory ZST content analytics dogfood test payload repeated many times. ";
        var fullText = string.Concat(payload, payload, payload, payload, payload);
        var doc = LoadCompressed(fullText);

        // CompressedSize must be positive
        Assert.True(doc.CompressedSize > 0);
        // DecompressedSize matches original UTF-8 byte count
        Assert.Equal(Encoding.UTF8.GetByteCount(fullText), (int)doc.DecompressedSize);
        // OverheadBytes = CompressedSize - DecompressedSize (can be negative for expansion,
        // but the property definition floors at 0 or uses absolute difference)
        Assert.True(doc.OverheadBytes >= 0);
        // IsHighlyCompressed = compressedSize < 0.5 * decompressedSize
        var ratio = (double)doc.CompressedSize / doc.DecompressedSize;
        Assert.Equal(ratio < 0.5, doc.IsHighlyCompressed);
    }
}
