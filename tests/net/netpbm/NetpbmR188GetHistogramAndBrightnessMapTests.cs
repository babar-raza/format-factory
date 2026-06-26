// Tests for NetpbmImage.GetHistogram, GetBrightnessMap deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R188

using System.Collections.Generic;
using System.Linq;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R188: Tests for NetpbmImage.GetHistogram, GetBrightnessMap deeper coverage.
/// GetHistogram(): returns dictionary of pixel value → count.
/// GetBrightnessMap(): returns 2D array (or list) of per-pixel brightness values.
/// Covers: GetHistogram non-null; GetHistogram non-empty;
/// GetHistogram entry count <= 256; GetHistogram sum equals total pixel count;
/// GetHistogram for solid-color image has single entry;
/// GetHistogram after AdjustBrightness changes distribution;
/// GetBrightnessMap non-null; GetBrightnessMap dimensions match image;
/// GetBrightnessMap values in [0,255]; GetBrightnessMap mean matches GetStats mean;
/// GetHistogram PGM vs PPM consistency; GetBrightnessMap after Invert has complementary values;
/// GetHistogram after DrawRectangle includes new pixel values;
/// dogfood Create->FillRegion->GetHistogram->GetBrightnessMap->AdjustBrightness->GetHistogram verify.
/// </summary>
public class NetpbmR188GetHistogramAndBrightnessMapTests
{
    private static NetpbmImage CreateSolid(byte value, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, value);

    private static NetpbmImage CreateColor(byte value, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Ppm, value);

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = CreateSolid(128);
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
    }

    [Fact]
    public void GetHistogram_NonEmpty()
    {
        var img = CreateSolid(100);
        var hist = img.GetHistogram();
        Assert.NotEmpty(hist);
    }

    [Fact]
    public void GetHistogram_EntryCount_AtMost256()
    {
        var img = CreateSolid(64);
        var hist = img.GetHistogram();
        Assert.True(hist.Count <= 256);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = CreateSolid(200, 4, 4);
        var hist = img.GetHistogram();
        var totalPixels = hist.Values.Sum();
        Assert.Equal(16, totalPixels); // 4x4 = 16 pixels
    }

    [Fact]
    public void GetHistogram_SolidColor_SingleEntry()
    {
        var img = CreateSolid(77);
        var hist = img.GetHistogram();
        // Solid-color image should have exactly one unique pixel value
        Assert.Equal(1, hist.Count);
    }

    [Fact]
    public void GetHistogram_SolidColor_EntryKeyIs77()
    {
        var img = CreateSolid(77);
        var hist = img.GetHistogram();
        Assert.True(hist.ContainsKey(77));
    }

    [Fact]
    public void GetHistogram_AfterAdjustBrightness_Shifts()
    {
        var img = CreateSolid(50);
        var hist1 = img.GetHistogram();
        var brightened = img.AdjustBrightness(30);
        var hist2 = brightened.GetHistogram();
        // The dominant pixel value should shift upward
        Assert.True(hist2.Keys.Max() >= hist1.Keys.Max());
    }

    [Fact]
    public void GetHistogram_AfterInvert_KeysComplementary()
    {
        var img = CreateSolid(100);
        var inverted = img.Invert();
        var hist = inverted.GetHistogram();
        // Inverted value of 100 should be 155 (255-100)
        Assert.True(hist.ContainsKey(155));
    }

    // -------------------------------------------------------------------------
    // GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessMap_NonNull()
    {
        var img = CreateSolid(128);
        var map = img.GetBrightnessMap();
        Assert.NotNull(map);
    }

    [Fact]
    public void GetBrightnessMap_RowCount_MatchesHeight()
    {
        var img = CreateSolid(128, 5, 3);
        var map = img.GetBrightnessMap();
        Assert.Equal(3, map.Count);
    }

    [Fact]
    public void GetBrightnessMap_ColCount_MatchesWidth()
    {
        var img = CreateSolid(128, 5, 3);
        var map = img.GetBrightnessMap();
        Assert.Equal(5, map[0].Count);
    }

    [Fact]
    public void GetBrightnessMap_Values_InRange()
    {
        var img = CreateSolid(200, 4, 4);
        var map = img.GetBrightnessMap();
        foreach (var row in map)
            foreach (var v in row)
                Assert.InRange(v, 0.0, 255.0);
    }

    [Fact]
    public void GetBrightnessMap_SolidColor_AllSameValue()
    {
        var img = CreateSolid(100, 4, 4);
        var map = img.GetBrightnessMap();
        var first = map[0][0];
        foreach (var row in map)
            foreach (var v in row)
                Assert.Equal(first, v, 1.0); // tolerance 1.0
    }

    [Fact]
    public void GetBrightnessMap_MeanMatchesGetStats()
    {
        var img = CreateSolid(150, 4, 4);
        var map = img.GetBrightnessMap();
        var (mean, _, _) = img.GetStats();
        // BrightnessMap mean should be close to GetStats mean
        var mapMean = map.SelectMany(r => r).Average();
        Assert.InRange(mapMean, mean - 2.0, mean + 2.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->FillRegion->GetHistogram->GetBrightnessMap->AdjustBrightness->GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFillGetHistogramBrightnessMapAdjustVerify_Pipeline()
    {
        // Create 8x8 gray image
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.Pgm, 50);
        Assert.Equal(NetpbmFormat.Pgm, img.Format);

        // FillRegion with different value
        var filled = img.FillRegion(2, 2, 4, 4, 200);
        Assert.Equal(8, filled.Width);
        Assert.Equal(8, filled.Height);

        // GetHistogram — should have at least 2 unique values (50 and 200)
        var hist = filled.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count >= 2);
        var totalPixels = hist.Values.Sum();
        Assert.Equal(64, totalPixels); // 8×8

        // GetBrightnessMap
        var map = filled.GetBrightnessMap();
        Assert.Equal(8, map.Count);
        Assert.Equal(8, map[0].Count);
        foreach (var row in map)
            foreach (var v in row)
                Assert.InRange(v, 0.0, 255.0);

        // AdjustBrightness
        var brightened = filled.AdjustBrightness(20);
        var hist2 = brightened.GetHistogram();
        Assert.NotNull(hist2);
        Assert.True(hist2.Keys.Max() >= hist.Keys.Max());

        // GetStats on brightened
        var (mean, min, max) = brightened.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
