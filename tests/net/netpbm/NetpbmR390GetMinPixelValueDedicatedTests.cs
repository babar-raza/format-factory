// Tests for NetpbmImage.GetMinPixelValue dedicated coverage.
// Sprint: ff-sprint-s377-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R390

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R390: Dedicated tests for NetpbmImage.GetMinPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMinPixelValue.
/// Height unchanged after GetMinPixelValue.
/// Format unchanged after GetMinPixelValue.
/// MaxValue unchanged after GetMinPixelValue.
/// Uniform image returns uniform value.
/// Idempotent (called twice same result).
/// Dogfood: all-zero image returns 0.
/// Dogfood: all-max image returns MaxValue.
/// </summary>
public class NetpbmR390GetMinPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMinPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMinPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMinPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_UniformImage_ReturnsUniformValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 55);
        int min = img.GetMinPixelValue();
        Assert.Equal(55, min);
    }

    [Fact]
    public void GetMinPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 200);
        int first = img.GetMinPixelValue();
        int second = img.GetMinPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        int min = img.GetMinPixelValue();
        Assert.Equal(0, min);
    }

    [Fact]
    public void DogfoodPipeline_AllMaxImage_ReturnsMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int min = img.GetMinPixelValue();
        Assert.Equal(img.MaxValue, min);
    }
}
