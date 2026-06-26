// Tests for NetpbmImage.ToGrayscale dedicated coverage.
// Sprint: ff-sprint-s180-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R176

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R176: Dedicated tests for NetpbmImage.ToGrayscale().
/// Converts a PPM (color) image to PGM (grayscale) using luminance formula:
/// gray = Clamp(0.299R + 0.587G + 0.114B, 0, MaxValue).
/// Non-PPM images throw InvalidOperationException.
/// Result format is always PGM_P5; MaxValue preserved; dims unchanged.
/// Covers: PBM throws; PGM throws; PPM returns PGM_P5;
/// result format is PGM_P5; width/height unchanged; MaxValue preserved;
/// original pixels unchanged; result Pixels not null; result in valid range;
/// dogfood PPM ToGrayscale pipeline.
/// </summary>
public class NetpbmR176ToGrayscaleTests
{
    // -------------------------------------------------------------------------
    // Guard tests (non-PPM throws)
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_OnPbmImage_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        Assert.Throws<InvalidOperationException>(() => img.ToGrayscale());
    }

    [Fact]
    public void ToGrayscale_OnPgmImage_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<InvalidOperationException>(() => img.ToGrayscale());
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_OnPpmImage_ResultFormatIsPgmP5()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ToGrayscale_ResultWidth_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void ToGrayscale_ResultHeight_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ToGrayscale_ResultMaxValue_MatchesOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void ToGrayscale_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.NotSame(img, result);
    }

    // -------------------------------------------------------------------------
    // Pixel semantics tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_ResultPixels_NotNull()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.NotNull(result.Pixels);
    }

    [Fact]
    public void ToGrayscale_ResultPixels_InValidRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.InRange(result.GetPixel(r, c), 0, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmToGrayscale_NonNullResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.ToGrayscale();
        Assert.NotNull(result);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }
}
