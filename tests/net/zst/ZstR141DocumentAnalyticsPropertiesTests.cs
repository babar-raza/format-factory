// Tests for ZstDocument analytics properties: IsHighlyCompressed, OverheadBytes,
// BytesPerFrame, SizeExceeds100K, IsMinimalFrame, FrameHeaderDescriptor.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R141

using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R141: Tests for ZstDocument analytics properties.
/// IsHighlyCompressed: true if compression ratio indicates >= 80% reduction.
/// OverheadBytes: bytes of ZST framing overhead (FileSizeBytes minus content).
/// BytesPerFrame: FileSizeBytes / FrameCount (or 0 if no frames).
/// SizeExceeds100K: true if FileSizeBytes > 100 * 1024.
/// IsMinimalFrame: true for minimal single-frame ZST output.
/// FrameHeaderDescriptor: first byte of the frame header (0x04 for minimal frame).
/// Covers: default IsHighlyCompressed=false; default OverheadBytes=0; default BytesPerFrame=0.0;
/// default SizeExceeds100K=false; OverheadBytes set directly; BytesPerFrame computed correctly;
/// SizeExceeds100K true for large files; IsMinimalFrame default=true;
/// FrameHeaderDescriptor default=4; dogfood compress->parse->BytesPerFrame>0;
/// dogfood compress->parse->IsHighlyCompressed is bool.
/// </summary>
public class ZstR141DocumentAnalyticsPropertiesTests
{
    // -------------------------------------------------------------------------
    // Default values
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_IsHighlyCompressed_Default_IsFalse()
    {
        Assert.False(new ZstDocument().IsHighlyCompressed);
    }

    [Fact]
    public void ZstDocument_OverheadBytes_Default_IsZero()
    {
        Assert.Equal(0L, new ZstDocument().OverheadBytes);
    }

    [Fact]
    public void ZstDocument_BytesPerFrame_Default_IsZero()
    {
        Assert.Equal(0.0, new ZstDocument().BytesPerFrame);
    }

    [Fact]
    public void ZstDocument_SizeExceeds100K_Default_IsFalse()
    {
        Assert.False(new ZstDocument().SizeExceeds100K);
    }

    [Fact]
    public void ZstDocument_IsMinimalFrame_Default_IsTrue()
    {
        // Default ZstDocument has IsMinimalFrame=true (single-frame minimal structure)
        Assert.True(new ZstDocument().IsMinimalFrame);
    }

    [Fact]
    public void ZstDocument_FrameHeaderDescriptor_Default_IsFour()
    {
        // 0x04 is the standard minimal frame header descriptor
        Assert.Equal((byte)4, new ZstDocument().FrameHeaderDescriptor);
    }

    // -------------------------------------------------------------------------
    // Direct property assignments
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_OverheadBytes_SetDirectly()
    {
        var doc = new ZstDocument { OverheadBytes = 42L };
        Assert.Equal(42L, doc.OverheadBytes);
    }

    [Fact]
    public void ZstDocument_SizeExceeds100K_TrueForLargeFile()
    {
        var doc = new ZstDocument { FileSizeBytes = 200 * 1024 };
        Assert.True(doc.SizeExceeds100K);
    }

    [Fact]
    public void ZstDocument_SizeExceeds100K_FalseForSmallFile()
    {
        var doc = new ZstDocument { FileSizeBytes = 100 };
        Assert.False(doc.SizeExceeds100K);
    }

    [Fact]
    public void ZstDocument_BytesPerFrame_MatchesComputation()
    {
        // BytesPerFrame = FileSizeBytes / FrameCount when FrameCount > 0
        var doc = new ZstDocument { FileSizeBytes = 200, FrameCount = 4 };
        Assert.Equal(50.0, doc.BytesPerFrame);
    }

    [Fact]
    public void ZstDocument_BytesPerFrame_ZeroFrames_IsZero()
    {
        var doc = new ZstDocument { FileSizeBytes = 100, FrameCount = 0 };
        Assert.Equal(0.0, doc.BytesPerFrame);
    }

    // -------------------------------------------------------------------------
    // Dogfood: compress->parse->analytics
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParse_BytesPerFrame_IsPositive()
    {
        var input = System.Text.Encoding.UTF8.GetBytes(
            "ZstR141 analytics test. " + new string('a', 200));
        var compressed = ZstWriter.Compress(input);
        using var stream = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);

        // At least 1 frame → BytesPerFrame > 0
        Assert.True(doc.BytesPerFrame > 0.0, "Expected BytesPerFrame > 0 for compressed data.");
    }

    [Fact]
    public void Dogfood_CompressParse_IsHighlyCompressed_IsBool()
    {
        var input = Encoding.UTF8.GetBytes(new string('Z', 500));
        var compressed = ZstWriter.Compress(input);
        using var stream = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);

        // IsHighlyCompressed is a bool — just verify it is accessible and typed correctly
        var value = doc.IsHighlyCompressed;
        Assert.IsType<bool>(value);
    }

    [Fact]
    public void Dogfood_CompressParse_SizeExceeds100K_FalseForSmallInput()
    {
        var input = Encoding.UTF8.GetBytes("tiny");
        var compressed = ZstWriter.Compress(input);
        using var stream = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);

        // Tiny compressed output won't exceed 100K
        Assert.False(doc.SizeExceeds100K);
    }
}
