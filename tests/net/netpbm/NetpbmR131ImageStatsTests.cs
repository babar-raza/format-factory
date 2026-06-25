// Tests for NetpbmDocument.GetStats() and GetChannelStats() analytic methods.
// Sprint: FORMAT-FACTORY-NETPBM-IMAGE-STATS-20260626
// Ledger: R131-GOVERNED-DOTNET-NETPBM-IMAGE-STATS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R131: NetpbmDocument.GetStats() — returns ImageStats with Mean, Min, Max across all
/// pixel channels. NetpbmDocument.GetChannelStats(channel) — per-channel stats for PPM.
/// All-white PGM: Mean=Max=255, Min=255. All-black PGM: Mean=Min=Max=0. Single gray pixel
/// stats match pixel value. PPM per-channel R/G/B stats are independently correct.
/// </summary>
public class NetpbmR131ImageStatsTests
{
    private static NetpbmDocument LoadPgm(string pgmText)
    {
        var bytes = Encoding.ASCII.GetBytes(pgmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string ppmText)
    {
        var bytes = Encoding.ASCII.GetBytes(ppmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- GetStats: all-white PGM ----

    [Fact]
    public void GetStats_AllWhitePgm_MeanIs255()
    {
        var doc = LoadPgm("P2\n2 2\n255\n255 255\n255 255\n");
        var stats = doc.GetStats();
        Assert.Equal(255.0, stats.Mean, precision: 1);
    }

    [Fact]
    public void GetStats_AllWhitePgm_MinAndMaxAre255()
    {
        var doc = LoadPgm("P2\n2 2\n255\n255 255\n255 255\n");
        var stats = doc.GetStats();
        Assert.Equal(255, stats.Min);
        Assert.Equal(255, stats.Max);
    }

    // ---- GetStats: all-black PGM ----

    [Fact]
    public void GetStats_AllBlackPgm_MeanIsZero()
    {
        var doc = LoadPgm("P2\n2 2\n255\n0 0\n0 0\n");
        var stats = doc.GetStats();
        Assert.Equal(0.0, stats.Mean, precision: 1);
    }

    [Fact]
    public void GetStats_AllBlackPgm_MinAndMaxAreZero()
    {
        var doc = LoadPgm("P2\n2 2\n255\n0 0\n0 0\n");
        var stats = doc.GetStats();
        Assert.Equal(0, stats.Min);
        Assert.Equal(0, stats.Max);
    }

    // ---- GetStats: single gray pixel ----

    [Fact]
    public void GetStats_SingleGrayPixel_MeanMatchesPixelValue()
    {
        // Single pixel with gray value 128
        var doc = LoadPgm("P2\n1 1\n255\n128\n");
        var stats = doc.GetStats();
        Assert.Equal(128.0, stats.Mean, precision: 1);
        Assert.Equal(128, stats.Min);
        Assert.Equal(128, stats.Max);
    }

    // ---- GetStats: mixed values ----

    [Fact]
    public void GetStats_MixedValues_MinAndMaxCorrect()
    {
        // 4 pixels: 0, 100, 200, 255
        var doc = LoadPgm("P2\n2 2\n255\n0 100\n200 255\n");
        var stats = doc.GetStats();
        Assert.Equal(0, stats.Min);
        Assert.Equal(255, stats.Max);
    }

    [Fact]
    public void GetStats_MixedValues_MeanIsAverage()
    {
        // 4 pixels: 0, 100, 200, 255 → mean = 555/4 = 138.75
        var doc = LoadPgm("P2\n2 2\n255\n0 100\n200 255\n");
        var stats = doc.GetStats();
        Assert.True(Math.Abs(stats.Mean - 138.75) < 1.0,
            $"Expected mean ≈ 138.75, got {stats.Mean}");
    }

    // ---- GetChannelStats: PPM per-channel ----

    [Fact]
    public void GetChannelStats_AllRedPpm_RedChannelMaxIs255()
    {
        // Single red pixel: R=255, G=0, B=0
        var doc = LoadPpm("P3\n1 1\n255\n255 0 0\n");
        var redStats = doc.GetChannelStats(0); // channel 0 = Red
        Assert.Equal(255, redStats.Max);
    }

    [Fact]
    public void GetChannelStats_AllRedPpm_GreenChannelMeanIsZero()
    {
        // Single red pixel: R=255, G=0, B=0
        var doc = LoadPpm("P3\n1 1\n255\n255 0 0\n");
        var greenStats = doc.GetChannelStats(1); // channel 1 = Green
        Assert.Equal(0.0, greenStats.Mean, precision: 1);
    }

    // ---- Dogfood: GetStats consistency with GetBrightness ----

    [Fact]
    public void DogfoodPipeline_GetStats_MeanConsistentWithGetBrightness()
    {
        // A PGM where GetBrightness and GetStats.Mean should relate:
        // GetBrightness is normalized [0,1]; GetStats.Mean is in raw pixel values [0,255]
        var doc = LoadPgm("P2\n3 1\n255\n51 128 204\n");
        var stats = doc.GetStats();
        var brightness = doc.Image.GetBrightness();

        // stats.Mean / 255 should ≈ GetBrightness
        var normalizedMean = stats.Mean / 255.0;
        Assert.True(Math.Abs(normalizedMean - brightness) < 0.01,
            $"Normalized mean {normalizedMean:F4} should ≈ GetBrightness {brightness:F4}");
    }
}
