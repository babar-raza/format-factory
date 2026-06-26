// Tests for NetpbmImage.GetStats, GetChannelStats, GetBrightness, GetHistogram, GetBrightnessMap.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R175

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R175: Tests for NetpbmImage.GetStats, GetChannelStats, GetBrightness, GetHistogram, GetBrightnessMap.
/// GetStats(): returns (Mean, Min, Max) for all pixels.
/// GetChannelStats(): returns per-channel (Mean, Min, Max) for PPM.
/// GetBrightness(): returns average pixel brightness in [0,1].
/// GetHistogram(): returns 256-bucket pixel frequency array.
/// GetBrightnessMap(): returns per-pixel brightness in [0,1].
/// Covers: GetStats mean in range; GetStats min le max; GetStats on solid image;
/// GetChannelStats R min le R max; GetChannelStats G mean in range;
/// GetBrightness in [0,1]; GetBrightness solid white is one; GetBrightness solid black is zero;
/// GetHistogram length is 256; GetHistogram sum equals total pixels;
/// GetHistogram solid-white bucket is total; GetBrightnessMap length equals pixel count;
/// GetBrightnessMap all in range;
/// dogfood Create->Paint->GetStats->GetBrightness->GetHistogram->GetBrightnessMap.
/// </summary>
public class NetpbmR175GetStatsAndGetBrightnessTests
{
    private static NetpbmImage CreateSolid(byte fill, int w = 4, int h = 4, NetpbmFormat fmt = NetpbmFormat.Pgm)
        => NetpbmImage.Create(w, h, fmt, fill);

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_MeanInValidRange()
    {
        var img = CreateSolid(128);
        var (mean, _, _) = img.GetStats();
        Assert.InRange(mean, 0.0, 255.0);
    }

    [Fact]
    public void GetStats_MinLessThanOrEqualToMax()
    {
        var img = CreateSolid(200);
        var (_, min, max) = img.GetStats();
        Assert.True(min <= max);
    }

    [Fact]
    public void GetStats_SolidImage_MeanEqualsPixelValue()
    {
        var img = CreateSolid(100);
        var (mean, min, max) = img.GetStats();
        Assert.Equal(100.0, mean, 1);
        Assert.Equal(100, min);
        Assert.Equal(100, max);
    }

    // -------------------------------------------------------------------------
    // GetChannelStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_R_MinLessThanOrEqualToMax()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Ppm, 0);
        img.SetPixelColor(0, 0, 255, 0, 0);
        var stats = img.GetChannelStats();
        Assert.True(stats.R.Min <= stats.R.Max);
    }

    [Fact]
    public void GetChannelStats_G_MeanInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Ppm, 0);
        img.SetPixelColor(1, 1, 0, 128, 0);
        var stats = img.GetChannelStats();
        Assert.InRange(stats.G.Mean, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_InRangeZeroToOne()
    {
        var img = CreateSolid(150);
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, 1.0);
    }

    [Fact]
    public void GetBrightness_SolidWhite_IsOne()
    {
        var img = CreateSolid(255);
        var brightness = img.GetBrightness();
        Assert.Equal(1.0, brightness, 3);
    }

    [Fact]
    public void GetBrightness_SolidBlack_IsZero()
    {
        var img = CreateSolid(0);
        var brightness = img.GetBrightness();
        Assert.Equal(0.0, brightness, 3);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_LengthIs256()
    {
        var img = CreateSolid(128);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = CreateSolid(100, 5, 5);
        var hist = img.GetHistogram();
        var sum = 0;
        foreach (var count in hist) sum += count;
        Assert.Equal(25, sum); // 5x5=25 pixels
    }

    [Fact]
    public void GetHistogram_SolidWhite_BucketIsTotalPixels()
    {
        var img = CreateSolid(255, 3, 3);
        var hist = img.GetHistogram();
        Assert.Equal(9, hist[255]); // 3x3=9 pixels all at 255
    }

    // -------------------------------------------------------------------------
    // GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessMap_LengthEqualsPixelCount()
    {
        var img = CreateSolid(128, 3, 4);
        var map = img.GetBrightnessMap();
        Assert.Equal(12, map.Length); // 3x4=12 pixels
    }

    [Fact]
    public void GetBrightnessMap_AllValuesInRange()
    {
        var img = CreateSolid(200, 3, 3);
        var map = img.GetBrightnessMap();
        foreach (var v in map)
            Assert.InRange(v, 0.0, 1.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Paint->GetStats->GetBrightness->GetHistogram->GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePaintGetStatsGetBrightnessGetHistogramGetBrightnessMap_Pipeline()
    {
        // Create and paint
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 0);
        for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++)
            img.SetPixel(r, c, (byte)(r * 64));

        // GetStats
        var (mean, min, max) = img.GetStats();
        Assert.Equal(0, min);
        Assert.Equal(192, max);
        Assert.InRange(mean, 90.0, 100.0); // approx (0+0+0+0 + 64+64+64+64 + 128+128+128+128 + 192+192+192+192)/16 = 96
        Assert.Equal(96.0, mean, 0);

        // GetBrightness
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, 1.0);

        // GetHistogram
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
        var total = 0;
        foreach (var b in hist) total += b;
        Assert.Equal(16, total);

        // GetBrightnessMap
        var bmap = img.GetBrightnessMap();
        Assert.Equal(16, bmap.Length);
        foreach (var bv in bmap)
            Assert.InRange(bv, 0.0, 1.0);
    }
}
