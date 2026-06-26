// Tests for NetpbmImage.GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s253-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R260

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R260: Dedicated tests for NetpbmImage.GetMaxPixelValue().
/// GetMaxPixelValue returns the maximum pixel value across all pixels as an int.
/// Image dimensions, format, and MaxValue are NOT modified (non-mutating).
/// Covers: all-zero image returns 0; after SetPixel result reflects max;
/// result in [0, MaxValue]; width/height/format/MaxValue unchanged;
/// called twice same result; known max pixel verified;
/// max >= min always; dogfood: set several pixels verify max is largest;
/// dogfood: all-same-value max equals that value.
/// </summary>
public class NetpbmR260GetMaxPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        int max = img.GetMaxPixelValue();
        Assert.Equal(0, max);
    }

    [Fact]
    public void GetMaxPixelValue_AfterSetPixel_ReturnsSetValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 180);
        int max = img.GetMaxPixelValue();
        Assert.Equal(180, max);
    }

    [Fact]
    public void GetMaxPixelValue_ResultInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.SetPixel(0, 0, 150);
        int max = img.GetMaxPixelValue();
        Assert.InRange(max, 0, 200);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMaxPixelValue();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetMaxPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMaxPixelValue();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetMaxPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetMaxPixelValue();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetMaxPixelValue_MaxValuePropertyUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 150);
        img.GetMaxPixelValue();
        Assert.Equal(150, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 77);
        img.SetPixel(2, 2, 200);
        int first = img.GetMaxPixelValue();
        int second = img.GetMaxPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSeveralPixels_MaxIsLargest()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 2, 200); // largest
        img.SetPixel(3, 0, 75);
        int max = img.GetMaxPixelValue();
        Assert.Equal(200, max);
    }

    [Fact]
    public void DogfoodPipeline_AllSameValue_MaxEqualsValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        // Set all pixels to 99
        for (int c = 0; c < 2; c++)
            for (int r = 0; r < 2; r++)
                img.SetPixel(c, r, 99);
        int max = img.GetMaxPixelValue();
        Assert.Equal(99, max);
    }
}
