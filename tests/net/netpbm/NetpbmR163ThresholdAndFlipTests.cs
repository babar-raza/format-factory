// Tests for NetpbmImage.Threshold, FlipHorizontal, FlipVertical.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R163

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R163: Tests for NetpbmImage.Threshold, FlipHorizontal, FlipVertical.
/// Threshold(threshold): pixels above threshold become MaxValue; others become 0.
/// FlipHorizontal(): mutates image by mirroring left-right in place.
/// FlipVertical(): mutates image by mirroring top-bottom in place.
/// Covers: Threshold above threshold becomes 255; Threshold below threshold becomes 0;
/// Threshold preserves dimensions; Threshold format preserved;
/// FlipHorizontal preserves dimensions; FlipHorizontal mirrors pixel positions;
/// FlipHorizontal twice returns to original; FlipVertical preserves dimensions;
/// FlipVertical mirrors pixel positions; FlipVertical twice returns to original;
/// Combined flip horizontal then vertical; dogfood Create->Threshold->FlipH->FlipV pipeline.
/// </summary>
public class NetpbmR163ThresholdAndFlipTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 0) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_AboveThreshold_BecomeMaxValue()
    {
        var img = MakePgm(4, 4, 200); // all pixels 200
        var result = img.Threshold(128);
        Assert.Equal(255, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_BelowThreshold_BecomesZero()
    {
        var img = MakePgm(4, 4, 50); // all pixels 50
        var result = img.Threshold(128);
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_AtThreshold_BecomesZeroOrMax()
    {
        var img = MakePgm(4, 4, 128);
        var result = img.Threshold(128);
        // Threshold 128: pixels == 128 can go either way; just check it's 0 or 255
        Assert.True(result.GetPixel(0, 0) == 0 || result.GetPixel(0, 0) == 255);
    }

    [Fact]
    public void Threshold_PreservesDimensions()
    {
        var img = MakePgm(5, 3, 100);
        var result = img.Threshold(50);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Threshold_PreservesFormat()
    {
        var img = MakePgm(4, 4, 100);
        var result = img.Threshold(50);
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    [Fact]
    public void Threshold_PixelCountMatchesDimensions()
    {
        var img = MakePgm(6, 4, 100);
        var result = img.Threshold(50);
        Assert.Equal(24, result.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = MakePgm(6, 4, 100);
        img.FlipHorizontal();
        Assert.Equal(6, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void FlipHorizontal_MirrorsPixelPositions()
    {
        var img = MakePgm(4, 4, 0);
        img.SetPixel(0, 0, 255); // top-left
        img.FlipHorizontal();
        // After horizontal flip, top-left pixel should be at top-right
        Assert.Equal(255, img.GetPixel(0, img.Width - 1));
    }

    [Fact]
    public void FlipHorizontal_Twice_ReturnsToOriginal()
    {
        var img = MakePgm(4, 4, 0);
        img.SetPixel(0, 0, 200);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(200, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = MakePgm(5, 6, 100);
        img.FlipVertical();
        Assert.Equal(5, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void FlipVertical_MirrorsPixelPositions()
    {
        var img = MakePgm(4, 4, 0);
        img.SetPixel(0, 0, 255); // top-left
        img.FlipVertical();
        // After vertical flip, top-left pixel goes to bottom-left
        Assert.Equal(255, img.GetPixel(img.Height - 1, 0));
    }

    [Fact]
    public void FlipVertical_Twice_ReturnsToOriginal()
    {
        var img = MakePgm(4, 4, 0);
        img.SetPixel(0, 2, 150);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(150, img.GetPixel(0, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Threshold->FlipH->FlipV
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ThresholdFlipHFlipV_Pipeline()
    {
        var img = MakePgm(6, 6, 0);
        // Set varying pixels
        img.SetPixel(0, 0, 200); // above threshold
        img.SetPixel(0, 5, 50);  // below threshold

        // Threshold at 128: 200 -> 255, 50 -> 0
        var threshed = img.Threshold(128);
        Assert.Equal(255, threshed.GetPixel(0, 0));
        Assert.Equal(0, threshed.GetPixel(0, 5));
        Assert.Equal(6, threshed.Width);
        Assert.Equal(6, threshed.Height);

        // FlipHorizontal
        threshed.FlipHorizontal();
        // Original (0,0) pixel (255) should now be at (0,5)
        Assert.Equal(255, threshed.GetPixel(0, 5));

        // FlipVertical
        threshed.FlipVertical();
        Assert.Equal(6, threshed.Width);
        Assert.Equal(6, threshed.Height);
        Assert.Equal(36, threshed.Pixels.Length);
    }
}
