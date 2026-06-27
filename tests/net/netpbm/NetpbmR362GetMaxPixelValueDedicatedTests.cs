// Tests for NetpbmImage.GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s349-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R362

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R362: Dedicated tests for NetpbmImage.GetMaxPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMaxPixelValue.
/// Height unchanged after GetMaxPixelValue.
/// Format unchanged after GetMaxPixelValue.
/// MaxValue unchanged after GetMaxPixelValue.
/// All-zero image returns 0.
/// All-max image returns MaxValue.
/// Idempotent (called twice same result).
/// Dogfood: mixed image returns value greater than min.
/// </summary>
public class NetpbmR362GetMaxPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        int max = img.GetMaxPixelValue();
        Assert.Equal(0, max);
    }

    [Fact]
    public void GetMaxPixelValue_AllMaxImage_ReturnsMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(255);
        int max = img.GetMaxPixelValue();
        Assert.Equal(255, max);
    }

    [Fact]
    public void GetMaxPixelValue_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        int first = img.GetMaxPixelValue();
        int second = img.GetMaxPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_ReturnsValueGreaterThanMin()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(10);
        img.SetPixel(2, 2, 200);
        int max = img.GetMaxPixelValue();
        Assert.True(max > 10);
    }
}
