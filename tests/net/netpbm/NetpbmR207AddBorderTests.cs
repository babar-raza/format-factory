// Tests for NetpbmImage.AddBorder dedicated coverage.
// Sprint: ff-sprint-s203-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R207

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R207: Dedicated tests for NetpbmImage.AddBorder(int thickness, int pixelValue).
/// thickness &lt; 0 → ArgumentOutOfRangeException.
/// thickness = 0 → returns clone (no border).
/// Returns a new image (not same reference).
/// Format preserved. MaxValue preserved.
/// New width = original + 2 * thickness.
/// New height = original + 2 * thickness.
/// Border pixels have the given pixelValue.
/// Centre pixels retain original values.
/// Pixel value clamped to [0, MaxValue] (or clamped by implementation).
/// Dogfood: add border, verify dims; centre pixel unchanged.
/// </summary>
public class NetpbmR207AddBorderTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_NegativeThickness_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.AddBorder(-1, 0));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.AddBorder(1, 0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AddBorder_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PBM_P1);
        var result = img.AddBorder(1, 0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AddBorder_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.AddBorder(1, 0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void AddBorder_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.AddBorder(1, 0);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void AddBorder_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.AddBorder(1, 0);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_WidthIncreasedByTwiceThickness()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.AddBorder(2, 0);
        Assert.Equal(5 + 2 * 2, result.Width);
    }

    [Fact]
    public void AddBorder_HeightIncreasedByTwiceThickness()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        var result = img.AddBorder(2, 0);
        Assert.Equal(4 + 2 * 2, result.Height);
    }

    [Fact]
    public void AddBorder_BorderPixelHasGivenValue()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 100);
        var result = img.AddBorder(1, 200);
        // Top-left corner pixel should be the border value
        Assert.Equal(200, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddBorder_CentrePixelUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 150);
        var result = img.AddBorder(1, 0);
        // Centre pixel (now at 3,3) should still be 150
        Assert.Equal(150, result.GetPixel(3, 3));
    }

    [Fact]
    public void DogfoodPipeline_AddBorderTwice_DimsCorrect()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var r1 = img.AddBorder(1, 0);
        var r2 = r1.AddBorder(1, 0);
        Assert.Equal(4 + 2 + 2, r2.Width);
        Assert.Equal(4 + 2 + 2, r2.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
