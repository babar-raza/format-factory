// Tests for NetpbmImage.AdjustBrightness dedicated coverage.
// Sprint: ff-sprint-s250-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R257

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R257: Dedicated tests for NetpbmImage.AdjustBrightness(delta).
/// AdjustBrightness adds delta to every pixel value, clamping results to [0, MaxValue].
/// Modifies the image IN PLACE (void return).
/// Covers: width unchanged; height unchanged; format unchanged; MaxValue unchanged;
/// positive delta increases pixel values (clamped at MaxValue);
/// negative delta decreases pixel values (clamped at 0);
/// zero delta → pixels unchanged; all-pixels remain in [0, MaxValue] after adjust;
/// dogfood: set pixel, apply positive delta, verify clamped;
/// dogfood: set pixel, apply negative delta, verify clamped at 0.
/// </summary>
public class NetpbmR257AdjustBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.AdjustBrightness(10);
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void AdjustBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.AdjustBrightness(10);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void AdjustBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.AdjustBrightness(20);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void AdjustBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.AdjustBrightness(50);
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_PositiveDelta_IncreasesPixel()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        img.AdjustBrightness(50);
        Assert.Equal(150, img.GetPixel(1, 1)); // 100 + 50 = 150
    }

    [Fact]
    public void AdjustBrightness_NegativeDelta_DecreasesPixel()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        img.AdjustBrightness(-30);
        Assert.Equal(70, img.GetPixel(1, 1)); // 100 - 30 = 70
    }

    [Fact]
    public void AdjustBrightness_ZeroDelta_PixelsUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        img.AdjustBrightness(0);
        Assert.Equal(128, img.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_OverflowClampsAtMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 240);
        img.AdjustBrightness(50); // 240 + 50 = 290 → clamped to 255
        Assert.Equal(255, img.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_UnderflowClampsAtZero()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.AdjustBrightness(-50); // 10 - 50 = -40 → clamped to 0
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_AllPixelsInRangeAfterAdjust()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 255);
        img.AdjustBrightness(100);
        for (int c = 0; c < img.Width; c++)
            for (int r = 0; r < img.Height; r++)
                Assert.InRange(img.GetPixel(c, r), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PositiveDelta_VerifyClampedMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 100);
        img.SetPixel(0, 0, 90);
        img.AdjustBrightness(50); // 90 + 50 = 140 → clamped to 100
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void DogfoodPipeline_NegativeDelta_VerifyClampedAtZero()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 0, 5);
        img.AdjustBrightness(-100); // 5 - 100 = -95 → clamped to 0
        Assert.Equal(0, img.GetPixel(1, 0));
    }
}
