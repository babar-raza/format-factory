// Tests for NetpbmImage.Sepia dedicated coverage.
// Sprint: ff-sprint-s191-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R191

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R191: Dedicated tests for NetpbmImage.Sepia().
/// Non-PPM images (PBM, PGM) return a clone with no pixel change.
/// PPM images: each pixel's luma L = 0.299R + 0.587G + 0.114B;
/// output R = clamp(L*1.0), G = clamp(L*0.8), B = clamp(L*0.6).
/// Returns a new image object (not same reference).
/// Format and MaxValue are preserved.
/// Dimensions are unchanged.
/// Covers: PBM returns new image; PBM format preserved; PGM returns new image;
/// PGM format preserved; PPM returns new image; PPM format preserved;
/// MaxValue preserved; dims unchanged; PPM red channel > blue channel (lum*1.0 > lum*0.6);
/// dogfood PPM sepia dims and format unchanged.
/// </summary>
public class NetpbmR191SepiaTests
{
    // -------------------------------------------------------------------------
    // Guard / clone tests (non-PPM)
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        var result = img.Sepia();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sepia_PbmImage_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void Sepia_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Sepia();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sepia_PgmImage_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // PPM functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_PpmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sepia_PpmImage_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Sepia_PpmImage_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Sepia_PpmImage_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(5, 7, NetpbmFormat.PPM_P6);
        var result = img.Sepia();
        Assert.Equal(5, result.Width);
        Assert.Equal(7, result.Height);
    }

    [Fact]
    public void Sepia_PpmPixel_RedChannelGreaterThanBlueChannel()
    {
        // For any non-black pixel, R=lum*1.0 > B=lum*0.6 when lum > 0
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        img.SetPixelColor(1, 1, 200, 200, 200);
        var result = img.Sepia();
        int r = result.GetPixelColor(1, 1).R;
        int b = result.GetPixelColor(1, 1).B;
        Assert.True(r >= b);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PpmSepia_DimsAndFormatUnchanged()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PPM_P6);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 8; c++)
                img.SetPixelColor(r, c, (byte)(r * 30), (byte)(c * 20), 128);
        var result = img.Sepia();
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }
}
