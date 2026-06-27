// Tests for NetpbmImage.GetMedianPixelValue dedicated coverage.
// Sprint: ff-sprint-s376-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R389

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R389: Dedicated tests for NetpbmImage.GetMedianPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMedianPixelValue.
/// Height unchanged after GetMedianPixelValue.
/// Format unchanged after GetMedianPixelValue.
/// MaxValue unchanged after GetMedianPixelValue.
/// Uniform image returns uniform value.
/// Idempotent (called twice same result).
/// Dogfood: all-zero image returns 0.
/// Dogfood: all-max image returns MaxValue.
/// </summary>
public class NetpbmR389GetMedianPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedianPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMedianPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMedianPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMedianPixelValue_UniformImage_ReturnsUniformValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 77);
        int median = img.GetMedianPixelValue();
        Assert.Equal(77, median);
    }

    [Fact]
    public void GetMedianPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 200);
        int first = img.GetMedianPixelValue();
        int second = img.GetMedianPixelValue();
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
        int median = img.GetMedianPixelValue();
        Assert.Equal(0, median);
    }

    [Fact]
    public void DogfoodPipeline_AllMaxImage_ReturnsMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int median = img.GetMedianPixelValue();
        Assert.Equal(img.MaxValue, median);
    }
}
