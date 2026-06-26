// Tests for NetpbmImage.Threshold dedicated coverage.
// Sprint: ff-sprint-s233-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R240

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R240: Dedicated tests for NetpbmImage.Threshold(value).
/// Valid call returns non-null.
/// Returns different object (not same reference).
/// Format preserved after threshold.
/// MaxValue preserved after threshold.
/// Width preserved after threshold.
/// Height preserved after threshold.
/// Pixel at or above threshold → MaxValue.
/// Pixel below threshold → 0.
/// Original image pixels unchanged after threshold.
/// Dogfood: set pixels, threshold, verify binary output.
/// </summary>
public class NetpbmR240ThresholdTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(128);
        Assert.NotNull(result);
    }

    [Fact]
    public void Threshold_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Threshold_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(100);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Threshold_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Threshold(100);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Threshold_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(128);
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void Threshold_HeightPreserved()
    {
        var img = NetpbmImage.Create(4, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(128);
        Assert.Equal(7, result.Height);
    }

    [Fact]
    public void Threshold_PixelAtOrAboveThreshold_IsMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 200);
        var result = img.Threshold(128);
        Assert.Equal(255, result.GetPixel(1, 1));
    }

    [Fact]
    public void Threshold_PixelBelowThreshold_IsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 50);
        var result = img.Threshold(128);
        Assert.Equal(0, result.GetPixel(2, 2));
    }

    [Fact]
    public void Threshold_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        _ = img.Threshold(128);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixels_Threshold_VerifyBinaryOutput()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);   // below threshold
        img.SetPixel(1, 1, 128);  // at threshold
        img.SetPixel(2, 2, 200);  // above threshold
        var result = img.Threshold(128);
        Assert.Equal(0, result.GetPixel(0, 0));
        Assert.Equal(255, result.GetPixel(1, 1));
        Assert.Equal(255, result.GetPixel(2, 2));
    }
}
