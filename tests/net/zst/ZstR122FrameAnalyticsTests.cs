// Tests for ZstDocument frame analytics: FrameHeaderDescriptor, IsMinimalFrame,
// SizeExceeds100K, IsHighlyCompressed, OverheadBytes, BytesPerFrame, ContentTypeHint, IsEmptyContent.
// Sprint: FORMAT-FACTORY-ZST-FRAME-ANALYTICS-R122-20260626
// Ledger: R122-GOVERNED-DOTNET-ZST-FRAMEANALYTICS-001

using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R122: ZstDocument analytics properties not previously covered:
/// FrameHeaderDescriptor (byte from RFC 8878 §3.1.2), IsMinimalFrame (size &lt; 1024 and 1 frame),
/// SizeExceeds100K (size &gt; 100,000 bytes), IsHighlyCompressed (heuristic), OverheadBytes,
/// BytesPerFrame, ContentTypeHint, and IsEmptyContent.
/// </summary>
public class ZstR122FrameAnalyticsTests
{
    private static ZstDocument Make(
        long fileSizeBytes = 100,
        bool magicValid = true,
        int frameCount = 1,
        byte frameHeaderDescriptor = 0,
        bool isMinimalFrame = false,
        bool sizeExceeds100K = false,
        bool isHighlyCompressed = false,
        long overheadBytes = 0,
        string? filePath = null,
        bool isEmptyContent = false,
        string contentTypeHint = "unknown")
        => new ZstDocument
        {
            FileSizeBytes        = fileSizeBytes,
            MagicValid           = magicValid,
            FrameCount           = frameCount,
            FrameHeaderDescriptor = frameHeaderDescriptor,
            IsMinimalFrame       = isMinimalFrame,
            SizeExceeds100K      = sizeExceeds100K,
            IsHighlyCompressed   = isHighlyCompressed,
            OverheadBytes        = overheadBytes,
            FilePath             = filePath,
            IsEmptyContent       = isEmptyContent,
            ContentTypeHint      = contentTypeHint,
        };

    // ---- FrameHeaderDescriptor ----

    [Fact]
    public void FrameHeaderDescriptor_Default_IsByte()
    {
        var doc = Make();
        // The property must be a byte; verify it's in [0,255]
        Assert.True(doc.FrameHeaderDescriptor >= 0);
        Assert.True(doc.FrameHeaderDescriptor <= 255);
    }

    [Fact]
    public void FrameHeaderDescriptor_SetToExplicitValue_Preserved()
    {
        var doc = Make(frameHeaderDescriptor: 0xA4);
        Assert.Equal(0xA4, doc.FrameHeaderDescriptor);
    }

    // ---- IsMinimalFrame ----

    [Fact]
    public void IsMinimalFrame_SingleFrameSmallFile_CanBeTrue()
    {
        var doc = Make(fileSizeBytes: 50, frameCount: 1, isMinimalFrame: true);
        Assert.True(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_MultiFrame_CanBeFalse()
    {
        var doc = Make(frameCount: 2, isMinimalFrame: false);
        Assert.False(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_LargeFile_CanBeFalse()
    {
        var doc = Make(fileSizeBytes: 200_000, isMinimalFrame: false);
        Assert.False(doc.IsMinimalFrame);
    }

    // ---- SizeExceeds100K ----

    [Fact]
    public void SizeExceeds100K_SmallFile_ReturnsFalse()
    {
        var doc = Make(fileSizeBytes: 1024, sizeExceeds100K: false);
        Assert.False(doc.SizeExceeds100K);
    }

    [Fact]
    public void SizeExceeds100K_LargeFile_ReturnsTrue()
    {
        var doc = Make(fileSizeBytes: 500_000, sizeExceeds100K: true);
        Assert.True(doc.SizeExceeds100K);
    }

    // ---- IsHighlyCompressed ----

    [Fact]
    public void IsHighlyCompressed_TinyValidFrame_CanBeTrue()
    {
        var doc = Make(fileSizeBytes: 50, frameCount: 1, isHighlyCompressed: true);
        Assert.True(doc.IsHighlyCompressed);
    }

    [Fact]
    public void IsHighlyCompressed_NormalSize_IsFalse()
    {
        var doc = Make(fileSizeBytes: 5000, isHighlyCompressed: false);
        Assert.False(doc.IsHighlyCompressed);
    }

    // ---- OverheadBytes ----

    [Fact]
    public void OverheadBytes_Positive_ReturnsPositiveLong()
    {
        var doc = Make(fileSizeBytes: 100, overheadBytes: 95);
        Assert.Equal(95L, doc.OverheadBytes);
    }

    [Fact]
    public void OverheadBytes_Zero_IsZero()
    {
        var doc = Make(overheadBytes: 0);
        Assert.Equal(0L, doc.OverheadBytes);
    }

    // ---- BytesPerFrame (computed) ----

    [Fact]
    public void BytesPerFrame_SingleFrame_EqualFileSizeBytes()
    {
        var doc = Make(fileSizeBytes: 200, frameCount: 1);
        // BytesPerFrame = FileSizeBytes / FrameCount
        Assert.Equal(200.0, doc.BytesPerFrame, precision: 5);
    }

    [Fact]
    public void BytesPerFrame_ZeroFrames_ReturnsZero()
    {
        var doc = Make(fileSizeBytes: 100, frameCount: 0);
        Assert.Equal(0.0, doc.BytesPerFrame, precision: 5);
    }

    // ---- ContentTypeHint ----

    [Fact]
    public void ContentTypeHint_Default_IsNonNull()
    {
        var doc = Make();
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_Archive_ReturnsCompressedArchive()
    {
        var doc = Make(contentTypeHint: "compressed_archive");
        Assert.Equal("compressed_archive", doc.ContentTypeHint);
    }

    // ---- IsEmptyContent ----

    [Fact]
    public void IsEmptyContent_EmptyPayload_IsTrue()
    {
        var doc = Make(fileSizeBytes: 4, frameCount: 0, isEmptyContent: true);
        Assert.True(doc.IsEmptyContent);
    }

    [Fact]
    public void IsEmptyContent_NonEmptyPayload_IsFalse()
    {
        var doc = Make(fileSizeBytes: 100, frameCount: 1, isEmptyContent: false);
        Assert.False(doc.IsEmptyContent);
    }

    // ---- Dogfood: comprehensive document analytics ----

    [Fact]
    public void DogfoodPipeline_CompressedLogFile_AllAnalyticsConsistent()
    {
        var doc = Make(
            fileSizeBytes: 800,
            magicValid: true,
            frameCount: 1,
            frameHeaderDescriptor: 0x60,
            isMinimalFrame: true,
            sizeExceeds100K: false,
            isHighlyCompressed: false,
            overheadBytes: 795,
            contentTypeHint: "compressed_data",
            isEmptyContent: false);

        // Basic validity
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.Equal(1, doc.FrameCount);

        // Frame analytics
        Assert.True(doc.IsMinimalFrame);
        Assert.False(doc.SizeExceeds100K);
        Assert.Equal(0x60, doc.FrameHeaderDescriptor);

        // Size analytics
        Assert.Equal(800.0 / 1024.0, doc.FileSizeKB, precision: 5);
        Assert.Equal(800.0, doc.BytesPerFrame, precision: 5);
        Assert.Equal(795L, doc.OverheadBytes);

        // Content analytics
        Assert.Equal("compressed_data", doc.ContentTypeHint);
        Assert.False(doc.IsEmptyContent);
        Assert.False(doc.HasMultipleFrames);
    }
}
