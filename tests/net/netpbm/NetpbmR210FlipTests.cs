// Tests for NetpbmImage.Flip dedicated coverage.
// Sprint: ff-sprint-s205-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R210

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R210: Dedicated tests for NetpbmImage.Flip(FlipDirection direction).
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// Horizontal flip: leftmost column becomes rightmost.
/// Vertical flip: top row becomes bottom row.
/// PBM: flip preserves format.
/// PGM: flip preserves format.
/// PPM: flip preserves format.
/// Flip twice (same direction) returns to original pixel values.
/// Dogfood: flip horizontal then vertical, dims stable.
/// Dogfood: flip PGM, specific pixel at expected position.
/// </summary>
public class NetpbmR210FlipTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Flip_PgmHorizontal_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Flip(FlipDirection.Horizontal);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Flip_PgmVertical_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Flip(FlipDirection.Vertical);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Flip_PbmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PBM_P1);
        var result = img.Flip(FlipDirection.Horizontal);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void Flip_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Flip(FlipDirection.Vertical);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Flip_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Flip(FlipDirection.Horizontal);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Flip_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 4, NetpbmFormat.PGM_P5);
        var result = img.Flip(FlipDirection.Horizontal);
        Assert.Equal(7, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Flip_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Flip(FlipDirection.Vertical);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Flip_Horizontal_LeftmostPixelMirrored()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);  // top-left pixel
        var result = img.Flip(FlipDirection.Horizontal);
        // After horizontal flip, the leftmost pixel goes to rightmost column (col = width-1 = 4)
        Assert.Equal(200, result.GetPixel(0, 4));
    }

    [Fact]
    public void Flip_Vertical_TopRowMirrored()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);  // top-left pixel (row=0)
        var result = img.Flip(FlipDirection.Vertical);
        // After vertical flip, top row goes to bottom row (row = height-1 = 4)
        Assert.Equal(200, result.GetPixel(4, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FlipHorizontalThenVertical_DimsStable()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var r1 = img.Flip(FlipDirection.Horizontal);
        var r2 = r1.Flip(FlipDirection.Vertical);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
        Assert.Equal(6, r2.Width);
        Assert.Equal(4, r2.Height);
    }

    [Fact]
    public void DogfoodPipeline_FlipTwiceHorizontal_PixelRestored()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 0, 150);
        var r1 = img.Flip(FlipDirection.Horizontal);
        var r2 = r1.Flip(FlipDirection.Horizontal);
        // Two horizontal flips restores to original
        Assert.Equal(150, r2.GetPixel(1, 0));
    }
}
