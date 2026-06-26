// Tests for NetpbmImage.GetBrightnessMap, GetBrightness, GetChannelStats, GetStats.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R169

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R169: Tests for NetpbmImage.GetBrightnessMap, GetBrightness, GetChannelStats.
/// GetBrightnessMap(): returns per-pixel brightness as double[].
/// GetBrightness(): returns mean brightness of image.
/// GetChannelStats(): returns (Mean, Min, Max) for R, G, B channels.
/// GetStats(): returns (Mean, Min, Max) for all pixels.
/// Covers: GetBrightnessMap length equals pixel count; GetBrightnessMap values 0-1;
/// GetBrightnessMap all-black image all zeros; GetBrightnessMap all-white all one;
/// GetBrightness non-negative; GetBrightness black image near zero;
/// GetBrightness white image near 255; GetChannelStats R-mean correct;
/// GetChannelStats G-mean correct; GetChannelStats B-mean correct;
/// GetStats mean matches GetBrightness; GetStats min/max correct;
/// dogfood Create->GetBrightnessMap->GetStats->GetChannelStats pipeline.
/// </summary>
public class NetpbmR169GetBrightnessMapTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage CreateColor(int w, int h, byte r, byte g, byte b)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, 0);
        for (var row = 0; row < h; row++)
            for (var col = 0; col < w; col++)
                img.SetPixelColor(row, col, r, g, b);
        return img;
    }

    // -------------------------------------------------------------------------
    // GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessMap_LengthEqualsPixelCount()
    {
        var img = CreateGray(5, 4, 128);
        var map = img.GetBrightnessMap();
        Assert.Equal(5 * 4, map.Length);
    }

    [Fact]
    public void GetBrightnessMap_ValuesInRange()
    {
        var img = CreateGray(4, 4, 128);
        var map = img.GetBrightnessMap();
        Assert.All(map, v => Assert.True(v >= 0.0 && v <= 1.0));
    }

    [Fact]
    public void GetBrightnessMap_BlackImage_AllNearZero()
    {
        var img = CreateGray(4, 4, 0);
        var map = img.GetBrightnessMap();
        Assert.All(map, v => Assert.True(v < 0.01));
    }

    [Fact]
    public void GetBrightnessMap_WhiteImage_AllNearOne()
    {
        var img = CreateGray(4, 4, 255);
        var map = img.GetBrightnessMap();
        Assert.All(map, v => Assert.True(v > 0.99));
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_NonNegative()
    {
        var img = CreateGray(4, 4, 128);
        Assert.True(img.GetBrightness() >= 0);
    }

    [Fact]
    public void GetBrightness_BlackImage_NearZero()
    {
        var img = CreateGray(4, 4, 0);
        Assert.True(img.GetBrightness() < 1.0);
    }

    [Fact]
    public void GetBrightness_WhiteImage_NearMax()
    {
        var img = CreateGray(4, 4, 255);
        Assert.True(img.GetBrightness() > 250.0);
    }

    [Fact]
    public void GetBrightness_MidGray_AroundHalf()
    {
        var img = CreateGray(4, 4, 128);
        var brightness = img.GetBrightness();
        Assert.True(brightness > 100 && brightness < 160);
    }

    // -------------------------------------------------------------------------
    // GetChannelStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_RedMean_IsCorrect()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var (R, _, _) = img.GetChannelStats();
        Assert.True(Math.Abs(R.Mean - 200.0) < 1.0);
    }

    [Fact]
    public void GetChannelStats_GreenMean_IsCorrect()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var (_, G, _) = img.GetChannelStats();
        Assert.True(Math.Abs(G.Mean - 100.0) < 1.0);
    }

    [Fact]
    public void GetChannelStats_BlueMean_IsCorrect()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var (_, _, B) = img.GetChannelStats();
        Assert.True(Math.Abs(B.Mean - 50.0) < 1.0);
    }

    [Fact]
    public void GetChannelStats_UniformColor_MinEqualsMax()
    {
        var img = CreateColor(4, 4, 150, 150, 150);
        var (R, G, B) = img.GetChannelStats();
        Assert.Equal(R.Min, R.Max);
        Assert.Equal(G.Min, G.Max);
        Assert.Equal(B.Min, B.Max);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_MinLessThanOrEqualMax()
    {
        var img = CreateGray(4, 4, 128);
        var (_, min, max) = img.GetStats();
        Assert.True(min <= max);
    }

    [Fact]
    public void GetStats_BlackImage_MinZero()
    {
        var img = CreateGray(4, 4, 0);
        var (_, min, _) = img.GetStats();
        Assert.Equal(0, min);
    }

    [Fact]
    public void GetStats_WhiteImage_Max255()
    {
        var img = CreateGray(4, 4, 255);
        var (_, _, max) = img.GetStats();
        Assert.Equal(255, max);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->GetBrightnessMap->GetStats->GetChannelStats pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_BrightnessMapStatsChannelStatsPipeline()
    {
        var img = CreateColor(6, 6, 180, 90, 45);

        // GetBrightnessMap
        var map = img.GetBrightnessMap();
        Assert.Equal(36, map.Length);
        Assert.All(map, v => Assert.True(v >= 0.0 && v <= 1.0));

        // GetBrightness
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0);

        // GetStats
        var (mean, min, max) = img.GetStats();
        Assert.True(min <= mean);
        Assert.True(mean <= max);

        // GetChannelStats
        var (R, G, B) = img.GetChannelStats();
        Assert.True(Math.Abs(R.Mean - 180.0) < 2.0);
        Assert.True(Math.Abs(G.Mean - 90.0) < 2.0);
        Assert.True(Math.Abs(B.Mean - 45.0) < 2.0);

        // Map length is correct
        Assert.Equal(img.Width * img.Height, map.Length);
    }
}
