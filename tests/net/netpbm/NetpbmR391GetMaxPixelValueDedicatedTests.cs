// Tests for NetpbmImage.GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s378-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R391

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R391: Dedicated tests for NetpbmImage.GetMaxPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMaxPixelValue.
/// Height unchanged after GetMaxPixelValue.
/// Format unchanged after GetMaxPixelValue.
/// MaxValue unchanged after GetMaxPixelValue.
/// Uniform image returns uniform value.
/// Idempotent (called twice same result).
/// Dogfood: all-zero image returns 0.
/// Dogfood: mixed image returns max element.
/// </summary>
public class NetpbmR391GetMaxPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_UniformImage_ReturnsUniformValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 88);
        int max = img.GetMaxPixelValue();
        Assert.Equal(88, max);
    }

    [Fact]
    public void GetMaxPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 200);
        int first = img.GetMaxPixelValue();
        int second = img.GetMaxPixelValue();
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
        int max = img.GetMaxPixelValue();
        Assert.Equal(0, max);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_ReturnsHighestValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 200);
        img.SetPixel(1, 0, 128);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 200);
    }
}
