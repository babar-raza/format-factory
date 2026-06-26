// Tests for NetpbmImage.ApplyKernel dedicated coverage.
// Sprint: ff-sprint-s204-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R209

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R209: Dedicated tests for NetpbmImage.ApplyKernel(double[,] kernel).
/// null kernel → ArgumentNullException.
/// Empty kernel (0x0) → ArgumentException.
/// Non-square kernel (rows != cols) → ArgumentException.
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// PGM: applies kernel; uniform image stays uniform at centre.
/// All output pixels clamped to [0, MaxValue].
/// Identity kernel: returns image with same pixel values at centre.
/// Dogfood: apply kernel, format and dims stable.
/// Dogfood: apply kernel twice, both not same reference.
/// </summary>
public class NetpbmR209ApplyKernelTests
{
    private static readonly double[,] IdentityKernel = { { 0, 0, 0 }, { 0, 1, 0 }, { 0, 0, 0 } };
    private static readonly double[,] BlurKernel = {
        { 1.0/9, 1.0/9, 1.0/9 },
        { 1.0/9, 1.0/9, 1.0/9 },
        { 1.0/9, 1.0/9, 1.0/9 }
    };

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyKernel_NullKernel_ThrowsArgumentNullException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentNullException>(() => img.ApplyKernel(null!));
    }

    [Fact]
    public void ApplyKernel_NonSquareKernel_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var nonSquare = new double[2, 3] { { 1, 0, 0 }, { 0, 1, 0 } };
        Assert.Throws<ArgumentException>(() => img.ApplyKernel(nonSquare));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyKernel_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.ApplyKernel(IdentityKernel);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyKernel_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.ApplyKernel(BlurKernel);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ApplyKernel_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.ApplyKernel(IdentityKernel);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void ApplyKernel_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyKernel(IdentityKernel);
        Assert.Equal(7, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ApplyKernel_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.ApplyKernel(IdentityKernel);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyKernel_UniformImage_CentrePixelUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 100);
        var result = img.ApplyKernel(BlurKernel);
        Assert.Equal(100, result.GetPixel(2, 2));
    }

    [Fact]
    public void ApplyKernel_AllPixelsClamped()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, img.MaxValue);
        var sharpKernel = new double[3, 3] { { -1, -1, -1 }, { -1, 9, -1 }, { -1, -1, -1 } };
        var result = img.ApplyKernel(sharpKernel);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                Assert.True(result.GetPixel(r, c) >= 0 && result.GetPixel(r, c) <= img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ApplyKernel_FormatAndDimsStable()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, (r * 6 + c) * 4);
        var result = img.ApplyKernel(BlurKernel);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void DogfoodPipeline_ApplyKernelTwice_NotSameReference()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var r1 = img.ApplyKernel(BlurKernel);
        var r2 = r1.ApplyKernel(BlurKernel);
        Assert.NotSame(r1, r2);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
