// Tests for NetpbmImage.Threshold dedicated coverage.
// Sprint: ff-sprint-s213-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R219

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R219: Dedicated tests for NetpbmImage.Threshold(int threshold).
/// PGM: returns new image.
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// Pixels above threshold → MaxValue; at or below → 0.
/// All output pixels are either 0 or MaxValue.
/// Original unchanged after threshold.
/// Dogfood: uniform below threshold → all 0.
/// Dogfood: uniform above threshold → all MaxValue.
/// </summary>
public class NetpbmR219ThresholdTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Threshold_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.Threshold(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Threshold_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Threshold_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Threshold(128);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void Threshold_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.Threshold(100);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PixelAboveThreshold_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 200);
        var result = img.Threshold(128);
        Assert.Equal(255, result.GetPixel(1, 1));
    }

    [Fact]
    public void Threshold_PixelBelowThreshold_BecomesZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        var result = img.Threshold(128);
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 180);
        var _ = img.Threshold(128);
        Assert.Equal(180, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformBelowThreshold_AllZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 50);
        var result = img.Threshold(128);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(0, result.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_UniformAboveThreshold_AllMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 200);
        var result = img.Threshold(128);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(255, result.GetPixel(x, y));
    }
}
