// Tests for NetpbmImage.GetPixelValueDistinctCount dedicated coverage.
// Sprint: ff-sprint-s370-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R383

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R383: Dedicated tests for NetpbmImage.GetPixelValueDistinctCount().
/// Valid image returns positive value.
/// Uniform image returns 1.
/// Width unchanged after GetPixelValueDistinctCount.
/// Height unchanged after GetPixelValueDistinctCount.
/// Format unchanged after GetPixelValueDistinctCount.
/// MaxValue unchanged after GetPixelValueDistinctCount.
/// Idempotent (called twice same result).
/// Two-value image returns 2.
/// Dogfood: gradient image returns more than 1.
/// Dogfood: random-fill image returns positive.
/// </summary>
public class NetpbmR383GetPixelValueDistinctCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueDistinctCount_ValidImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetPixelValueDistinctCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetPixelValueDistinctCount_UniformImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 75);
        int count = img.GetPixelValueDistinctCount();
        Assert.Equal(1, count);
    }

    [Fact]
    public void GetPixelValueDistinctCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelValueDistinctCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelValueDistinctCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelValueDistinctCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelValueDistinctCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelValueDistinctCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelValueDistinctCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelValueDistinctCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelValueDistinctCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 100);
        int first = img.GetPixelValueDistinctCount();
        int second = img.GetPixelValueDistinctCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelValueDistinctCount_TwoValueImage_ReturnsTwo()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 200);
        int count = img.GetPixelValueDistinctCount();
        Assert.Equal(2, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsMoreThanOne()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        int count = img.GetPixelValueDistinctCount();
        Assert.True(count > 1);
    }

    [Fact]
    public void DogfoodPipeline_MixedFillImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r * 40 + c * 25) % 256);
        int count = img.GetPixelValueDistinctCount();
        Assert.True(count > 0);
    }
}
