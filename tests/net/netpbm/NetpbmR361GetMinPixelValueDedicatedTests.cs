// Tests for NetpbmImage.GetMinPixelValue dedicated coverage.
// Sprint: ff-sprint-s348-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R361

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R361: Dedicated tests for NetpbmImage.GetMinPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMinPixelValue.
/// Height unchanged after GetMinPixelValue.
/// Format unchanged after GetMinPixelValue.
/// MaxValue unchanged after GetMinPixelValue.
/// All-zero image returns 0.
/// All-max image returns max.
/// Idempotent (called twice same result).
/// Dogfood: mixed image returns value less than max.
/// </summary>
public class NetpbmR361GetMinPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMinPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMinPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMinPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        int min = img.GetMinPixelValue();
        Assert.Equal(0, min);
    }

    [Fact]
    public void GetMinPixelValue_AllMaxImage_ReturnsMax()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(255);
        int min = img.GetMinPixelValue();
        Assert.Equal(255, min);
    }

    [Fact]
    public void GetMinPixelValue_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(50);
        int first = img.GetMinPixelValue();
        int second = img.GetMinPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_ReturnsValueLessThanMax()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(200);
        img.SetPixel(2, 2, 10);
        int min = img.GetMinPixelValue();
        Assert.True(min < 200);
    }
}
