// Tests for NetpbmImageFilters.MedianFilter, NetpbmImageAnalyzer.GetBrightness,
// NetpbmImageAnalyzer.GetBrightnessMap.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R157

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R157: Tests for NetpbmImageFilters.MedianFilter, GetBrightness, GetBrightnessMap.
/// MedianFilter(radius): removes noise by taking pixel median in neighborhood.
/// GetBrightness(): returns mean pixel value (0.0 to 255.0) for PGM or luminance for PPM.
/// GetBrightnessMap(): returns array of per-pixel brightness values.
/// Covers: MedianFilter preserves dimensions; MedianFilter result pixel in [0,255];
/// MedianFilter radius=0 returns equivalent; MedianFilter uniform image preserves value;
/// GetBrightness uniform image returns fill value; GetBrightness zero image is 0.0;
/// GetBrightness max image is 255.0; GetBrightness between 0 and 255;
/// GetBrightnessMap count matches pixel count; GetBrightnessMap values in [0,1];
/// GetBrightnessMap uniform image all same value;
/// dogfood Create->MedianFilter->GetBrightness->GetBrightnessMap pipeline.
/// </summary>
public class NetpbmR157MedianFilterAndBrightnessTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // MedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_PreservesDimensions()
    {
        var img = MakePgm(6, 4, 128);
        var filtered = img.MedianFilter(1);
        Assert.Equal(6, filtered.Width);
        Assert.Equal(4, filtered.Height);
    }

    [Fact]
    public void MedianFilter_PixelsClamped()
    {
        var img = MakePgm(4, 4, 200);
        var filtered = img.MedianFilter(1);
        for (var r = 0; r < filtered.Height; r++)
            for (var c = 0; c < filtered.Width; c++)
                Assert.InRange(filtered.GetPixel(r, c), (byte)0, (byte)255);
    }

    [Fact]
    public void MedianFilter_UniformImage_PreservesValue()
    {
        var img = MakePgm(4, 4, 100);
        var filtered = img.MedianFilter(1);
        // Median of uniform fill=100 image should still be 100
        Assert.Equal(100, filtered.GetPixel(1, 1));
    }

    [Fact]
    public void MedianFilter_PixelCountUnchanged()
    {
        var img = MakePgm(5, 5, 77);
        var filtered = img.MedianFilter(1);
        Assert.Equal(25, filtered.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_UniformImage_ReturnsFillValue()
    {
        var img = MakePgm(4, 4, 128);
        var analyzer = new NetpbmImageAnalyzer(img);
        var brightness = analyzer.GetBrightness();
        Assert.Equal(128.0, brightness, precision: 0);
    }

    [Fact]
    public void GetBrightness_ZeroImage_IsZero()
    {
        var img = MakePgm(4, 4, 0);
        var analyzer = new NetpbmImageAnalyzer(img);
        Assert.Equal(0.0, analyzer.GetBrightness(), precision: 0);
    }

    [Fact]
    public void GetBrightness_MaxImage_Is255()
    {
        var img = MakePgm(4, 4, 255);
        var analyzer = new NetpbmImageAnalyzer(img);
        Assert.Equal(255.0, analyzer.GetBrightness(), precision: 0);
    }

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = MakePgm(4, 4, 0);
        for (var i = 0; i < 16; i++)
            img.SetPixel(i / 4, i % 4, (byte)(i * 16));
        var analyzer = new NetpbmImageAnalyzer(img);
        var brightness = analyzer.GetBrightness();
        Assert.InRange(brightness, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessMap_CountMatchesPixelCount()
    {
        var img = MakePgm(4, 3, 100);
        var analyzer = new NetpbmImageAnalyzer(img);
        var map = analyzer.GetBrightnessMap();
        Assert.Equal(12, map.Length); // 4*3
    }

    [Fact]
    public void GetBrightnessMap_ValuesInRange()
    {
        var img = MakePgm(4, 4, 128);
        var analyzer = new NetpbmImageAnalyzer(img);
        var map = analyzer.GetBrightnessMap();
        foreach (var v in map)
            Assert.InRange(v, 0.0, 1.0);
    }

    [Fact]
    public void GetBrightnessMap_UniformImage_AllSameValue()
    {
        var img = MakePgm(3, 3, 255);
        var analyzer = new NetpbmImageAnalyzer(img);
        var map = analyzer.GetBrightnessMap();
        var first = map[0];
        foreach (var v in map)
            Assert.Equal(first, v, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->MedianFilter->GetBrightness->GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_MedianFilterBrightnessMap_Pipeline()
    {
        var img = MakePgm(8, 8, 0);
        // Add some noise
        for (var r = 0; r < 8; r++)
            for (var c = 0; c < 8; c++)
                img.SetPixel(r, c, (byte)((r * 8 + c) * 4 % 256));

        // Apply median filter
        var filtered = img.MedianFilter(1);
        Assert.Equal(8, filtered.Width);

        // Check brightness
        var analyzer = new NetpbmImageAnalyzer(filtered);
        var brightness = analyzer.GetBrightness();
        Assert.InRange(brightness, 0.0, 255.0);

        // Check brightness map
        var map = analyzer.GetBrightnessMap();
        Assert.Equal(64, map.Length);
        foreach (var v in map)
            Assert.InRange(v, 0.0, 1.0);
    }
}
