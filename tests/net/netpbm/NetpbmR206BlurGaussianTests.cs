// Tests for NetpbmImage.BlurGaussian dedicated coverage.
// Sprint: ff-sprint-s202-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R206

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R206: Dedicated tests for NetpbmImage.BlurGaussian(int radius).
/// radius &lt; 0 → ArgumentOutOfRangeException.
/// radius = 0 → returns clone (no blur).
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// PBM: returns clone (binary format passthrough).
/// PGM: applies Gaussian kernel; uniform image stays uniform.
/// PPM: format and dims preserved.
/// All output pixels clamped to [0, MaxValue].
/// Dogfood: blur PGM, format and dims stable.
/// Dogfood: blur twice, result not same reference.
/// </summary>
public class NetpbmR206BlurGaussianTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurGaussian_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurGaussian(-1));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurGaussian_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurGaussian(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurGaussian_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PBM_P1);
        var result = img.BlurGaussian(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurGaussian_PpmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.BlurGaussian(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurGaussian_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurGaussian(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void BlurGaussian_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.BlurGaussian(1);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void BlurGaussian_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurGaussian(1);
        Assert.Equal(7, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void BlurGaussian_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurGaussian(1);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurGaussian_UniformPgm_CentrePixelUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 100);
        var result = img.BlurGaussian(1);
        Assert.Equal(100, result.GetPixel(2, 2));
    }

    [Fact]
    public void BlurGaussian_AllPixelsClamped()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, img.MaxValue);
        var result = img.BlurGaussian(1);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                Assert.True(result.GetPixel(r, c) <= img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_BlurFormatAndDimsStable()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, (r * 6 + c) * 4);
        var result = img.BlurGaussian(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DogfoodPipeline_BlurTwice_NotSameReference()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var r1 = img.BlurGaussian(1);
        var r2 = r1.BlurGaussian(1);
        Assert.NotSame(r1, r2);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
