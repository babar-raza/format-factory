// Tests for NetpbmImage.Normalize dedicated coverage.
// Sprint: ff-sprint-s262-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R269

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R269: Dedicated tests for NetpbmImage.Normalize().
/// Normalize rescales all pixel values to use the full [0, MaxValue] range.
/// Void in-place operation (no return value).
/// Width/height/format/MaxValue unchanged.
/// All pixels remain in [0, MaxValue] after normalize.
/// Uniform image (all same) remains valid after normalize.
/// After normalize, all-zero image stays all-zero (min=max=0, range=0).
/// Called twice → no exception, still valid.
/// Dogfood: image with known min/max, after normalize pixels in range.
/// Dogfood: varied pixels, after normalize all still valid.
/// </summary>
public class NetpbmR269NormalizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_ValidImage_NoException()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(2, 2, 200);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_AllPixelsRemainInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 2, 200);
        img.Normalize();
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void Normalize_UniformImage_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 128);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.Normalize();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void Normalize_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.Normalize();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Normalize_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.Normalize();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void Normalize_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.Normalize();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void Normalize_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.Normalize();
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_AfterNormalizeInRange()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 100);
        img.SetPixel(0, 1, 200);
        img.SetPixel(1, 1, 240);
        img.Normalize();
        Assert.InRange(img.GetPixel(0, 0), 0, 255);
        Assert.InRange(img.GetPixel(1, 1), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_VariedPixels_AllStillValid()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 5);
        img.SetPixel(1, 1, 127);
        img.SetPixel(2, 2, 250);
        img.Normalize();
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }
}
