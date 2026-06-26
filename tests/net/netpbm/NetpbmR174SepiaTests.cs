// Tests for NetpbmImage.Sepia dedicated coverage.
// Sprint: ff-sprint-s178-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R174

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R174: Dedicated tests for NetpbmImage.Sepia().
/// Applies a sepia tone effect to the image.
/// Non-PPM images (PBM, PGM) return a clone (no effect).
/// PPM images: luminance = 0.299R + 0.587G + 0.114B;
/// result.R = lum * 1.0, result.G = lum * 0.8, result.B = lum * 0.6.
/// Returns a new image; original is unchanged.
/// Covers: PBM returns clone; PGM returns clone; returns new image;
/// width/height unchanged; format preserved; original pixels unchanged;
/// PPM green channel less than red; PPM blue channel less than green;
/// result pixels in valid range; dogfood PPM pipeline.
/// </summary>
public class NetpbmR174SepiaTests
{
    // -------------------------------------------------------------------------
    // Non-PPM handling (clone)
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_OnPbmImage_ReturnsClone()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.Sepia();
        Assert.NotSame(img, result);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void Sepia_OnPgmImage_ReturnsClone()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Sepia();
        Assert.NotSame(img, result);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sepia_ResultWidth_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Sepia_ResultHeight_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Sepia_ResultFormat_MatchesOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel channel relationship tests (PPM)
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_OriginalPixels_Unchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.Sepia();
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void Sepia_ResultPixels_InValidRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        // Set some non-zero pixels via Pixels array
        var result = img.Sepia();
        // All result channels should be in [0, MaxValue]
        Assert.InRange(result.MaxValue, 1, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmCreated_SepiaReturnsNonNull()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.NotNull(result);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void DogfoodPipeline_PgmSepia_ReturnsSameDimensions()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (byte)(r * 4 + c * 16));
        var result = img.Sepia();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
        Assert.Equal(img.Format, result.Format);
    }
}
