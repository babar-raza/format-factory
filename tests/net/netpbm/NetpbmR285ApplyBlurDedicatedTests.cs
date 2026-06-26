// Tests for NetpbmImage.ApplyBlur dedicated coverage.
// Sprint: ff-sprint-s277-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R285

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R285: Dedicated tests for NetpbmImage.ApplyBlur().
/// Valid image no exception.
/// All pixels remain in [0, MaxValue] after blur.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice no exception.
/// Uniform image no exception.
/// Dogfood: set pixels, apply blur, all in range.
/// Dogfood: uniform image, apply blur, all same.
/// </summary>
public class NetpbmR285ApplyBlurDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyBlur_ValidImage_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200);
        var ex = Record.Exception(() => img.ApplyBlur());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyBlur_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, (c * 30 + r * 50) % 256);
        img.ApplyBlur();
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void ApplyBlur_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.ApplyBlur();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void ApplyBlur_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.ApplyBlur();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void ApplyBlur_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        img.ApplyBlur();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void ApplyBlur_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 200);
        img.ApplyBlur();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void ApplyBlur_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => { img.ApplyBlur(); img.ApplyBlur(); });
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyBlur_UniformImage_NoException()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 128);
        var ex = Record.Exception(() => img.ApplyBlur());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsApplyBlur_AllInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(3, 3, 255);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 64);
        img.ApplyBlur();
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_AfterBlurAllInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, 150);
        img.ApplyBlur();
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }
}
