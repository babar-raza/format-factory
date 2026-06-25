// Tests for ZstDocument computed properties: HasMultipleFrames, FileSizeKB, IsValid, SizeLabel
// Sprint: FORMAT-FACTORY-ZST-DOCUMENT-PROPS-20260624

using Xunit;

namespace FormatFactory.Zst.Tests;

public class ZstR117DocumentPropertiesTests
{
    private static ZstDocument Make(
        long fileSizeBytes = 0,
        bool magicValid = false,
        int frameCount = 0)
        => new ZstDocument
        {
            FileSizeBytes = fileSizeBytes,
            MagicValid = magicValid,
            FrameCount = frameCount,
        };

    // ---- HasMultipleFrames ----

    [Fact]
    public void HasMultipleFrames_OneFrame_ReturnsFalse()
    {
        var doc = Make(frameCount: 1);
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void HasMultipleFrames_TwoFrames_ReturnsTrue()
    {
        var doc = Make(frameCount: 2);
        Assert.True(doc.HasMultipleFrames);
    }

    [Fact]
    public void HasMultipleFrames_ZeroFrames_ReturnsFalse()
    {
        var doc = Make(frameCount: 0);
        Assert.False(doc.HasMultipleFrames);
    }

    // ---- FileSizeKB ----

    [Fact]
    public void FileSizeKB_ExactKilobyte_ReturnsOne()
    {
        var doc = Make(fileSizeBytes: 1024);
        Assert.Equal(1.0, doc.FileSizeKB, precision: 5);
    }

    [Fact]
    public void FileSizeKB_Zero_ReturnsZero()
    {
        var doc = Make(fileSizeBytes: 0);
        Assert.Equal(0.0, doc.FileSizeKB, precision: 5);
    }

    [Fact]
    public void FileSizeKB_512Bytes_IsHalfKB()
    {
        var doc = Make(fileSizeBytes: 512);
        Assert.Equal(0.5, doc.FileSizeKB, precision: 5);
    }

    // ---- IsValid ----

    [Fact]
    public void IsValid_MagicTrueAndFrames_ReturnsTrue()
    {
        var doc = Make(magicValid: true, frameCount: 1);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_MagicFalse_ReturnsFalse()
    {
        var doc = Make(magicValid: false, frameCount: 1);
        Assert.False(doc.IsValid);
    }

    [Fact]
    public void IsValid_ZeroFrames_ReturnsFalse()
    {
        var doc = Make(magicValid: true, frameCount: 0);
        Assert.False(doc.IsValid);
    }

    // ---- SizeLabel ----

    [Theory]
    [InlineData(0, "empty")]
    [InlineData(100, "tiny")]
    [InlineData(511, "tiny")]
    [InlineData(512, "small")]
    [InlineData(5000, "small")]
    [InlineData(10240, "medium")]
    [InlineData(500_000, "medium")]
    [InlineData(1_048_576, "large")]
    [InlineData(5_000_000, "large")]
    public void SizeLabel_ReturnsExpectedLabel(long sizeBytes, string expectedLabel)
    {
        var doc = Make(fileSizeBytes: sizeBytes);
        Assert.Equal(expectedLabel, doc.SizeLabel);
    }
}
