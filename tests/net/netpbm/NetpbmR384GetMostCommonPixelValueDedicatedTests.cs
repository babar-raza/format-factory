// Tests for NetpbmImage.GetMostCommonPixelValue dedicated coverage.
// Sprint: ff-sprint-s371-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R384

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R384: Dedicated tests for NetpbmImage.GetMostCommonPixelValue().
/// Valid image returns non-negative.
/// Uniform image returns uniform value.
/// Width unchanged after GetMostCommonPixelValue.
/// Height unchanged after GetMostCommonPixelValue.
/// Format unchanged after GetMostCommonPixelValue.
/// MaxValue unchanged after GetMostCommonPixelValue.
/// Idempotent (called twice same result).
/// Dominant value returns that value.
/// Dogfood: all-zero image returns 0.
/// Dogfood: all-max image returns max.
/// </summary>
public class NetpbmR384GetMostCommonPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMostCommonPixelValue_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int val = img.GetMostCommonPixelValue();
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetMostCommonPixelValue_UniformImage_ReturnsUniformValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 90);
        int val = img.GetMostCommonPixelValue();
        Assert.Equal(90, val);
    }

    [Fact]
    public void GetMostCommonPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetMostCommonPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMostCommonPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMostCommonPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMostCommonPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMostCommonPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMostCommonPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMostCommonPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMostCommonPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 200);
        int first = img.GetMostCommonPixelValue();
        int second = img.GetMostCommonPixelValue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMostCommonPixelValue_DominantValue_ReturnsThatValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        // Fill 12 of 16 pixels with value 150
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 150);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 20);
        img.SetPixel(0, 2, 30);
        img.SetPixel(0, 3, 40);
        int val = img.GetMostCommonPixelValue();
        Assert.Equal(150, val);
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
        int val = img.GetMostCommonPixelValue();
        Assert.Equal(0, val);
    }

    [Fact]
    public void DogfoodPipeline_AllMaxImage_ReturnsMax()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int val = img.GetMostCommonPixelValue();
        Assert.Equal(img.MaxValue, val);
    }
}
