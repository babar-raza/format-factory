// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s224-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R231

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R231: Dedicated tests for NetpbmImage.FlipVertical().
/// Returns new image (not same reference).
/// Format preserved.
/// MaxValue preserved.
/// Width preserved.
/// Height preserved.
/// All pixels in valid range.
/// Original image unchanged.
/// Flip-twice returns same pixel values as original.
/// Uniform image stays uniform after flip.
/// Dogfood: top pixel appears on bottom after flip.
/// </summary>
public class NetpbmR231FlipVerticalTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipVertical();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipVertical_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipVertical();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void FlipVertical_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 180);
        var result = img.FlipVertical();
        Assert.Equal(180, result.MaxValue);
    }

    [Fact]
    public void FlipVertical_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipVertical();
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void FlipVertical_HeightPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipVertical();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void FlipVertical_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(0, 0, 7);
        var result = img.FlipVertical();
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 15);
    }

    [Fact]
    public void FlipVertical_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 77);
        img.FlipVertical();
        Assert.Equal(77, img.GetPixel(0, 0));
    }

    [Fact]
    public void FlipVertical_FlipTwice_SamePixelValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 55);
        var result = img.FlipVertical().FlipVertical();
        Assert.Equal(55, result.GetPixel(0, 0));
    }

    [Fact]
    public void FlipVertical_UniformImage_StaysUniform()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 64);
        var result = img.FlipVertical();
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(64, result.GetPixel(x, y));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TopPixelAppearsOnBottom()
    {
        var img = NetpbmImage.Create(1, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 88);  // top pixel = 88
        // After vertical flip, pixel at y=0 should appear at y=height-1=3
        var result = img.FlipVertical();
        Assert.Equal(88, result.GetPixel(0, 3));
    }
}
