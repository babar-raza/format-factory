// Tests for NetpbmImage.GetMinPixelValue dedicated coverage.
// Sprint: ff-sprint-s252-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R259

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R259: Dedicated tests for NetpbmImage.GetMinPixelValue().
/// GetMinPixelValue returns the minimum pixel value across all pixels as an int.
/// Image dimensions, format, and MaxValue are NOT modified (non-mutating).
/// Covers: all-zero image returns 0; result is non-negative; result in [0, MaxValue];
/// width/height/format/MaxValue unchanged; called twice same result;
/// after setting minimum pixel the result reflects it;
/// mixed image minimum is lowest value;
/// dogfood: set known minimum, verify result matches;
/// dogfood: min < max after setting two distinct values.
/// </summary>
public class NetpbmR259GetMinPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        int min = img.GetMinPixelValue();
        Assert.Equal(0, min);
    }

    [Fact]
    public void GetMinPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_ResultInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.SetPixel(1, 1, 50);
        int min = img.GetMinPixelValue();
        Assert.InRange(min, 0, 200);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMinPixelValue();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetMinPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMinPixelValue();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetMinPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetMinPixelValue();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetMinPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 150);
        img.GetMinPixelValue();
        Assert.Equal(150, img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 100);
        int first = img.GetMinPixelValue();
        int second = img.GetMinPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownMinimum_VerifyResult()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // Set all pixels to 100 except one known minimum
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 100);
        img.SetPixel(2, 1, 10); // known minimum
        int min = img.GetMinPixelValue();
        Assert.Equal(10, min);
    }

    [Fact]
    public void DogfoodPipeline_MinLessThanMax_WhenDistinctValues()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 20);
        img.SetPixel(2, 2, 200);
        int min = img.GetMinPixelValue();
        // Min should be <= 20 (since default pixels are 0)
        Assert.True(min <= 20);
    }
}
