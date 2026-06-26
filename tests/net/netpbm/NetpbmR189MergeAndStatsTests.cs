// Tests for NetpbmImage.MergeHorizontal, MergeVertical, GetStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R189

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R189: Tests for NetpbmImage.MergeHorizontal, MergeVertical, GetStats deeper.
/// MergeHorizontal(other): returns new image concatenated horizontally.
/// MergeVertical(other): returns new image concatenated vertically.
/// GetStats(): returns (mean, min, max) pixel statistics.
/// Covers: MergeHorizontal width is sum; MergeHorizontal height matches;
/// MergeHorizontal format preserved; MergeHorizontal returns new instance;
/// MergeVertical height is sum; MergeVertical width matches;
/// MergeVertical format preserved; MergeVertical returns new instance;
/// GetStats mean in range [0,255]; GetStats min less than max for non-solid;
/// GetStats solid color mean equals fill value; GetStats max >= min always;
/// MergeHorizontal->GetStats stats valid; MergeVertical->MergeHorizontal chain;
/// GetStats after Invert values complement; GetStats after AdjustBrightness shifts;
/// dogfood Create->MergeHorizontal->MergeVertical->GetStats->AdjustBrightness->GetStats.
/// </summary>
public class NetpbmR189MergeAndStatsTests
{
    private static NetpbmImage Solid(byte val, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, val);

    // -------------------------------------------------------------------------
    // MergeHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_Width_IsSum()
    {
        var a = Solid(50, 4, 4);
        var b = Solid(100, 4, 4);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(8, merged.Width);
    }

    [Fact]
    public void MergeHorizontal_Height_Unchanged()
    {
        var a = Solid(50, 4, 3);
        var b = Solid(100, 6, 3);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(3, merged.Height);
    }

    [Fact]
    public void MergeHorizontal_Format_Preserved()
    {
        var a = Solid(50);
        var b = Solid(100);
        var merged = a.MergeHorizontal(b);
        Assert.Equal(NetpbmFormat.Pgm, merged.Format);
    }

    [Fact]
    public void MergeHorizontal_ReturnsNewInstance()
    {
        var a = Solid(50);
        var b = Solid(100);
        var merged = a.MergeHorizontal(b);
        Assert.NotSame(a, merged);
        Assert.NotSame(b, merged);
    }

    [Fact]
    public void MergeHorizontal_WithSelf_DoubleWidth()
    {
        var img = Solid(128, 3, 3);
        var merged = img.MergeHorizontal(img);
        Assert.Equal(6, merged.Width);
        Assert.Equal(3, merged.Height);
    }

    // -------------------------------------------------------------------------
    // MergeVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_Height_IsSum()
    {
        var a = Solid(50, 4, 3);
        var b = Solid(100, 4, 5);
        var merged = a.MergeVertical(b);
        Assert.Equal(8, merged.Height);
    }

    [Fact]
    public void MergeVertical_Width_Unchanged()
    {
        var a = Solid(50, 4, 3);
        var b = Solid(100, 4, 2);
        var merged = a.MergeVertical(b);
        Assert.Equal(4, merged.Width);
    }

    [Fact]
    public void MergeVertical_Format_Preserved()
    {
        var a = Solid(50);
        var b = Solid(100);
        var merged = a.MergeVertical(b);
        Assert.Equal(NetpbmFormat.Pgm, merged.Format);
    }

    [Fact]
    public void MergeVertical_ReturnsNewInstance()
    {
        var a = Solid(50);
        var b = Solid(100);
        var merged = a.MergeVertical(b);
        Assert.NotSame(a, merged);
        Assert.NotSame(b, merged);
    }

    [Fact]
    public void MergeVertical_WithSelf_DoubleHeight()
    {
        var img = Solid(64, 3, 3);
        var merged = img.MergeVertical(img);
        Assert.Equal(3, merged.Width);
        Assert.Equal(6, merged.Height);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_Mean_InRange()
    {
        var img = Solid(128);
        var (mean, _, _) = img.GetStats();
        Assert.InRange(mean, 0.0, 255.0);
    }

    [Fact]
    public void GetStats_SolidColor_MeanEqualsValue()
    {
        var img = Solid(100);
        var (mean, _, _) = img.GetStats();
        Assert.Equal(100.0, mean, 1.0);
    }

    [Fact]
    public void GetStats_MaxGreaterOrEqualMin()
    {
        var img = Solid(80);
        var (_, min, max) = img.GetStats();
        Assert.True(max >= min);
    }

    [Fact]
    public void GetStats_SolidColor_MinEqualsMax()
    {
        var img = Solid(77);
        var (_, min, max) = img.GetStats();
        Assert.Equal(min, max);
    }

    [Fact]
    public void GetStats_AfterAdjustBrightness_MeanShifts()
    {
        var img = Solid(50);
        var (mean1, _, _) = img.GetStats();
        var brightened = img.AdjustBrightness(50);
        var (mean2, _, _) = brightened.GetStats();
        Assert.True(mean2 >= mean1);
    }

    [Fact]
    public void GetStats_AfterInvert_MeanIsComplement()
    {
        var img = Solid(100);
        var inverted = img.Invert();
        var (mean, _, _) = inverted.GetStats();
        Assert.InRange(mean, 150.0, 160.0); // 255 - 100 = 155
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateMergeHorizMergeVertGetStatsAdjustGetStats_Pipeline()
    {
        // Create two different-shade images
        var dark = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 50);
        var light = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 200);

        // MergeHorizontal
        var hMerge = dark.MergeHorizontal(light);
        Assert.Equal(8, hMerge.Width);
        Assert.Equal(4, hMerge.Height);

        // GetStats on merged — mean between 50 and 200
        var (hMean, hMin, hMax) = hMerge.GetStats();
        Assert.True(hMin <= hMean);
        Assert.True(hMean <= hMax);
        Assert.True(hMax > hMin); // Two different shades

        // MergeVertical
        var vMerge = dark.MergeVertical(light);
        Assert.Equal(4, vMerge.Width);
        Assert.Equal(8, vMerge.Height);

        // AdjustBrightness
        var brightened = hMerge.AdjustBrightness(10);
        var (bMean, bMin, bMax) = brightened.GetStats();
        Assert.True(bMean >= hMean - 5);

        // Stats always valid
        Assert.True(bMin >= 0);
        Assert.True(bMax <= 255);
        Assert.InRange(bMean, 0.0, 255.0);
    }
}
