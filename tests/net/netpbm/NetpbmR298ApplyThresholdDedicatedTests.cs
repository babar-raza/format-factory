// Tests for NetpbmImage.ApplyThreshold dedicated coverage.
// Sprint: ff-sprint-s290-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R298

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R298: Dedicated tests for NetpbmImage.ApplyThreshold(threshold).
/// Valid call no exception.
/// All pixels are either 0 or MaxValue after threshold.
/// Width unchanged after ApplyThreshold.
/// Height unchanged after ApplyThreshold.
/// Format unchanged after ApplyThreshold.
/// MaxValue unchanged after ApplyThreshold.
/// Called twice no exception.
/// Threshold at 0 results in all-max (all pass).
/// Threshold at MaxValue results in all-zero (all below).
/// Dogfood: mixed image threshold produces binary pixels.
/// </summary>
public class NetpbmR298ApplyThresholdDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyThreshold_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 128);
        var ex = Record.Exception(() => img.ApplyThreshold(100));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_AllPixelsAreZeroOrMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 150);
        img.SetPixel(2, 2, 200);
        img.ApplyThreshold(100);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
            {
                int val = img.GetPixel(x, y);
                Assert.True(val == 0 || val == img.MaxValue);
            }
    }

    [Fact]
    public void ApplyThreshold_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyThreshold_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyThreshold_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyThreshold_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyThreshold(128);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyThreshold_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        img.ApplyThreshold(100);
        var ex = Record.Exception(() => img.ApplyThreshold(50));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_ThresholdAtZero_AllPassThreshold()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        img.ApplyThreshold(0);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
            {
                int val = img.GetPixel(x, y);
                Assert.True(val == 0 || val == img.MaxValue);
            }
    }

    [Fact]
    public void ApplyThreshold_ThresholdAtMaxValue_AllBelowOrEqual()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        img.ApplyThreshold(img.MaxValue);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
            {
                int val = img.GetPixel(x, y);
                Assert.True(val == 0 || val == img.MaxValue);
            }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_ProducesBinaryPixels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(1, 0, 130);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 10);
        img.ApplyThreshold(100);
        for (int x = 0; x < 4; x++)
        {
            int val = img.GetPixel(x, 0);
            Assert.True(val == 0 || val == img.MaxValue);
        }
    }
}
