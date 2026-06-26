// Tests for NetpbmImage.Threshold dedicated coverage.
// Sprint: ff-sprint-s254-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R261

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R261: Dedicated tests for NetpbmImage.Threshold(value).
/// Threshold binarizes the image IN PLACE (void return):
/// pixels >= value become MaxValue; pixels less than value become 0.
/// Dimensions, format, and MaxValue are preserved.
/// Covers: width unchanged; height unchanged; format unchanged; MaxValue unchanged;
/// pixel >= threshold becomes MaxValue; pixel less than threshold becomes 0;
/// pixel exactly at threshold becomes MaxValue; zero threshold all-become-MaxValue;
/// MaxValue threshold only-max-pixels-pass; dogfood known pixels verify binarization;
/// dogfood all-pixels-are-zero-or-MaxValue after threshold.
/// </summary>
public class NetpbmR261ThresholdDedicatedTests
{
    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Threshold(128);
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void Threshold_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Threshold(128);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Threshold_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Threshold(100);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void Threshold_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.Threshold(100);
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PixelAboveThreshold_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 200); // above threshold 128
        img.Threshold(128);
        Assert.Equal(255, img.GetPixel(1, 1));
    }

    [Fact]
    public void Threshold_PixelBelowThreshold_BecomesZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50); // below threshold 128
        img.Threshold(128);
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_PixelAtThreshold_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 0, 128); // exactly at threshold
        img.Threshold(128);
        Assert.Equal(255, img.GetPixel(1, 0));
    }

    [Fact]
    public void Threshold_ZeroThreshold_AllPixelsBecomeMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        // With threshold=0, all pixels >= 0 → all become MaxValue
        img.Threshold(0);
        for (int c = 0; c < 2; c++)
            for (int r = 0; r < 2; r++)
                Assert.Equal(255, img.GetPixel(c, r));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_VerifyBinarization()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100); // below 150
        img.SetPixel(1, 0, 200); // above 150
        img.SetPixel(2, 0, 150); // at 150 → MaxValue
        img.SetPixel(3, 0, 50);  // below 150
        img.Threshold(150);
        Assert.Equal(0, img.GetPixel(0, 0));   // below
        Assert.Equal(255, img.GetPixel(1, 0)); // above
        Assert.Equal(255, img.GetPixel(2, 0)); // at threshold
        Assert.Equal(0, img.GetPixel(3, 0));   // below
    }

    [Fact]
    public void DogfoodPipeline_AllPixelsAreZeroOrMaxValue_AfterThreshold()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(1, 1, 180);
        img.SetPixel(2, 2, 100);
        img.Threshold(128);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
            {
                int v = img.GetPixel(c, r);
                Assert.True(v == 0 || v == img.MaxValue,
                    $"Pixel at ({c},{r}) = {v}, expected 0 or {img.MaxValue}");
            }
    }
}
